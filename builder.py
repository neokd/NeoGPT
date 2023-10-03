import logging
import threading
from langchain.document_loaders import DirectoryLoader, PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Chroma
from config import (
    PERSIST_DIRECTORY,
    MODEL_DIRECTORY,
    SOURCE_DIR,
    EMBEDDING_MODEL,
    DEVICE_TYPE,
    CHROMA_SETTINGS,
)

def load_docs(directory: str = SOURCE_DIR):
    loader = DirectoryLoader(directory, glob="**/*.pdf", use_multithreading=True, loader_cls=PDFMinerLoader)
    docs = loader.load()
    logging.info(f"Loaded {len(docs)} documents from {directory}")
    return docs

def split_docs(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    logging.info(f"Split {len(docs)} documents into chunks")
    return docs

def process_and_store_documents(docs):
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE_TYPE},
        cache_folder=MODEL_DIRECTORY,
    )
    db = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=PERSIST_DIRECTORY,
        client_settings=CHROMA_SETTINGS,
    )
    logging.info(f"Loaded Documents to Chroma DB Successfully")

def builder():
    logging.info("Building the database")
    documents = load_docs()
    docs = split_docs(documents)

    # Create a list to hold threads. Here, 4 is taken as the default number of threads
    # that will be simultaneously run to convert files into vectors.

    threads = []
    num_threads = 4

    # Split the list of documents into equal parts for each thread
    part_size = len(docs) // num_threads
    doc_parts = [docs[i:i + part_size] for i in range(0, len(docs), part_size)]

    # Create and start threads
    for part in doc_parts:
        thread = threading.Thread(target=process_and_store_documents, args=(part,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    builder()
