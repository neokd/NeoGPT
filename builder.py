import logging
import os
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor, as_completed
import re
from langchain.docstore.document import Document
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Optional, Iterator, List, Dict
from chromadb.config import Settings
import argparse
from neogpt.vectorstore.chroma import ChromaStore
from neogpt.vectorstore.faiss import FAISSStore
from neogpt.config import (
    SOURCE_DIR,
    INGEST_THREADS,
    DEVICE_TYPE,
    DOCUMENT_EXTENSION,
    URL_EXTENSION,
    RESERVED_FILE_NAMES
)

LOG_FILE = "builder.log"

def load_single_document(file_path: str) -> Document:
    """
        fn: load_single_document
        Description: The function loads the single document
        Args:
            file_path (str): File path
        return:
            Document: Document
    """
    # Loads a single document from a file path
    file_extension = os.path.splitext(file_path)[1]
    loader_class = DOCUMENT_EXTENSION.get(file_extension)
    if loader_class:
        loader = loader_class(file_path)
    else:
        raise ValueError("Document type is undefined")
    return loader.load()[0]


def load_document_batch(filepaths):
    """
        fn: load_document_batch
        Description: The function loads the document batch
        Args:
            filepaths (list): List of file paths
        return:
            list: List of data from the files
    """
    logging.info("Loading document batch")
    # create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # load files
        futures = [exe.submit(load_single_document, name) for name in filepaths]
        # collect data
        
        data_list = [future.result() for future in futures]
        # return data and file paths
        return (data_list, filepaths)


def process_url(url_path: str) -> Document:
    """
        fn: process_url
        Description: The function processes the url
        Args:
            file_path (str): File path
        return:
            Document: Document
    """
    file_extension = os.path.splitext(url_path)[1]
    if file_extension != ".url":
        return  # Skip if not a .url file

    with open(url_path) as build:
        urls = build.readlines()
        for url in urls:
            if "youtube.com" in url:
                loader_class = URL_EXTENSION.get('.youtube', None)  # 
                loader = loader_class.from_youtube_url(
                    url,
                    add_video_info=True
                )
    return loader.load()[0]
        
def load_url_batch(urlpaths):
    """
        fn: load_url_batch
        Description: The function loads the url batch
        Args:
            urlpaths (list): List of url paths
        return:
            list: List of data from the urls
    """
    logging.info("Loading Url batch")
    with ThreadPoolExecutor(len(urlpaths)) as exe:
        futures = [exe.submit(process_url, name) for name in urlpaths]
        data_list = [future.result() for future in futures]
    return (data_list, urlpaths)


def build_documents(source_directory : str) -> list[Document]:
    """
        fn: build_documents
        Description: The function builds the documents from the source directory
        Args:
            source_directory (str): Source directory
        return:
            list[Document]: List of documents
    """
    doc_path = []
    url_path = []
    for root,_,files in os.walk(source_directory):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1]
            source_file_path = os.path.join(root, file_name)
            if file_extension in DOCUMENT_EXTENSION.keys() and file_name not in RESERVED_FILE_NAMES:
                doc_path.append(source_file_path)
            elif file_name in RESERVED_FILE_NAMES:
                url_path.append(source_file_path)

    n_workers = min(INGEST_THREADS, max(len(doc_path), 1), max(len(url_path), 1))

    chunk_size = round((len(doc_path) + len(url_path)) / n_workers)

    docs = []
    with ProcessPoolExecutor(n_workers) as executor:
        futures = []
        # split the load operations into chunks
        if len(doc_path) > 0:
            for i in range(0, len(doc_path), chunk_size):
                # select a chunk of filenames
                filepaths = doc_path[i : (i + chunk_size)]
                # submit the task
                future = executor.submit(load_document_batch, filepaths)
                futures.append(future)

        if len(url_path) > 0:  

            for i in range(0, len(url_path), chunk_size):
                urlpaths = url_path[i : (i + chunk_size)]
                future = executor.submit(load_url_batch, urlpaths)
                futures.append(future)

        for future in as_completed(futures):
            contents, _ = future.result()
            docs.extend(contents)

    return docs
            

def builder(vectorstore: str = "Chroma"):
    """
        fn: builder
        Description: The function builds the vectorstore (Chroma, FAISS)
        Args:
            vectorstore (str, optional): Vectorstore (Chroma, FAISS). Defaults to "Chroma".
        return:
            None
    """
    logging.info(f"Loading Documents from {SOURCE_DIR}")
    documents = build_documents(SOURCE_DIR)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)

    texts = text_splitter.split_documents(documents)

    logging.info(f"Loaded {len(documents)} documents from {SOURCE_DIR}")
    logging.info(f"Split into {len(texts)} chunks of text")
    logging.info(f"Using {DEVICE_TYPE} device for embedding model")

    match vectorstore:
        case "Chroma":
            logging.info(f"Using Chroma for vectorstore")
            db = ChromaStore().from_documents(
                documents=texts,
            )
            logging.info(f"Loaded Documents to Chroma DB Successfully")
        case "FAISS":
            logging.info(f"Using FAISS for vectorstore")
            db = FAISSStore().from_documents(
                documents=texts,
            )
            logging.info(f"Loaded Documents to FAISS DB Successfully")
    
    logging.info(f"Builder👷🏻‍♀️ has built your VectorDB successfully!")
   
# def query():
#     embeddings = HuggingFaceInstructEmbeddings(
#         model_name=EMBEDDING_MODEL_NAME,
#         model_kwargs={"device": 'mps'},
#         cache_folder=os.path.join(os.path.dirname(__file__), "models"),
#     )
#     db = Chroma(
#         embedding_function=embeddings,
#         persist_directory=PERSIST_DIRECTORY,
#     )
#     while True:
#         query = input()
#         results= db.similarity_search(query)
#         print(results)

if __name__ == "__main__":
    logging.basicConfig(
        filename=LOG_FILE,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO,
    )
    parser = argparse.ArgumentParser(description="NeoGPT CLI Interface")
    parser.add_argument(
        "--db",
        choices=["Chroma", "FAISS"],
        default="Chroma",
        help="Specify the vectorstore (Chroma, FAISS)",
    )
    args = parser.parse_args()
    builder(vectorstore=args.db)


