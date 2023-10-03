import os
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List
from langchain.document_loaders import DOCUMENT_MAP
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Chroma
from config import (
    SOURCE_DIR,
    CHROMA_PERSIST_DIRECTORY,
    EMBEDDING_MODEL,
    CHROMA_SETTINGS,
    DEVICE_TYPE,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO,
)

def load_single_document(file_path: str) -> Document:
    # Loads a single document from a file path
    file_extension = os.path.splitext(file_path)[1]
    loader_class = DOCUMENT_MAP.get(file_extension)
    if loader_class:
        loader = loader_class(file_path)
        return loader.load()[0]
    else:
        raise ValueError("Document type is undefined")

def load_documents(source_directory: str) -> List[Document]:
    doc_paths = []

    for root, _, files in os.walk(source_directory):
        for file_name in files:
            file_extension = os.path.splitext(file_name)[1]
            source_file_path = os.path.join(root, file_name)
            if file_extension in DOCUMENT_MAP:
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
            future = executor.submit(load_single_document, filepaths[0])
            futures.append(future)

        # Process all results
        for future in as_completed(futures):
            # Open the file and load the data
            contents = future.result()
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
    builder()
