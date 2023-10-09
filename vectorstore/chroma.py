# --- Under Development ---
"""
    The Purpose of this file is to provide a wrapper around the ChromaDB
    to provide a simple interface for storing and retrieving documents
    from the database.
"""
from vectorstore.base import VectorStore
from langchain.schema.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceInstructEmbeddings
from config import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_SETTINGS,
    EMBEDDING_MODEL,
    DEVICE_TYPE,
    MODEL_DIRECTORY,
)
class ChromaStore(VectorStore):
    def __init__(self) -> None:
        self.chroma = Chroma()
        self.embeddings = HuggingFaceInstructEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE_TYPE},
            cache_folder=MODEL_DIRECTORY,
        )
    
    def from_documents(self, documents: list[Document]) -> Document:
        self.chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            client_settings=CHROMA_SETTINGS,
        )
        return documents
    
    def as_retriever(self):
        return self.chroma.as_retriever()


    
