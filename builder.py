import logging
import os
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Optional, Iterator, List, Dict
from langchain.docstore.document import Document
from langchain.document_loaders import PDFMinerLoader, TextLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
import sqlite3
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from config import (
    SOURCE_DIR,
    CHROMA_PERSIST_DIRECTORY,
    EMBEDDING_MODEL,
    CHROMA_SETTINGS,
    DEVICE_TYPE,
)



DOCUMENT_MAP = {
    '.pdf': PDFMinerLoader,
    '.txt': TextLoader,

}

def load_single_document(file_path: str) -> Document:
    # Loads a single document from a file path
    file_extension = os.path.splitext(file_path)[1]
    loader_class = DOCUMENT_MAP.get(file_extension)
    if loader_class:
        loader = loader_class(file_path)
    else:
        raise ValueError("Document type is undefined")
    return loader.load()[0]

def load_document_batch(filepaths):
    logging.info("Loading document batch")
    # Create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # Load files
        futures = [exe.submit(load_single_document, name) for name in filepaths]
        # Collect data
        data_list = [future.result() for future in futures]
        # Return data and file paths
        return (data_list, filepaths)

def load_documents(source_directory: str) -> List[Document]:
    doc_paths = []

    for root, _, files in os.walk(source_directory):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1]
            source_file_path = os.path.join(root, file_name)
            if file_extension in DOCUMENT_MAP.keys():
                doc_paths.append(source_file_path)

    n_workers = min(os.cpu_count(), len(doc_paths))
    chunk_size = len(doc_paths) // n_workers

    docs = []

    with ProcessPoolExecutor(n_workers) as executor:
        futures = []
        # Split the load operations into chunks
        for i in range(0, len(doc_paths), chunk_size):
            # Select a chunk of filenames
            filepaths = doc_paths[i: (i + chunk_size)]
            # Submit the task
            future = executor.submit(load_document_batch, filepaths)
            futures.append(future)
        # Process all results
        for future in as_completed(futures):
            # Open the file and load the data
            contents, _ = future.result()
            docs.extend(contents)

    return docs

def builder():
    logging.info(f"Loading Documents from {SOURCE_DIR}")
    documents = load_documents(SOURCE_DIR)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    texts = text_splitter.split_documents(documents)

    logging.info(f"Loaded {len(documents)} documents from {SOURCE_DIR}")
    logging.info(f"Split into {len(texts)} chunks of text")
    logging.info(f"Using {DEVICE_TYPE} device for embedding model")

    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE_TYPE},
        cache_folder=os.path.join(os.path.dirname(__file__), "models"),
    )

    db = Chroma.from_documents(
        texts,
        embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        client_settings=CHROMA_SETTINGS,
    )
    
    logging.info(f"Loaded Documents to Chroma DB Successfully")

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO,
    )
    builder()
