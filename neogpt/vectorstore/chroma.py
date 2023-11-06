# --- Under Development ---
"""
    The Purpose of this file is to provide a wrapper around the ChromaDB
    to provide a simple interface for storing and retrieving documents
    from the database.
"""
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.schema.document import Document
from langchain.vectorstores import Chroma

from neogpt.config import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_SETTINGS,
    DEVICE_TYPE,
    EMBEDDING_MODEL,
    MODEL_DIRECTORY,
)
from neogpt.vectorstore.base import VectorStore


class ChromaStore(VectorStore):
    """
    The ChromaStore class provides a wrapper around the ChromaDB
    to provide a simple interface for storing and retrieving documents
    from the database.
    """

    def __init__(self) -> None:
        self.embeddings = HuggingFaceInstructEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE_TYPE},
            cache_folder=MODEL_DIRECTORY,
        )
        self.chroma = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            client_settings=CHROMA_SETTINGS,
            embedding_function=self.embeddings,
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

    def get(self):
        return self.chroma.get()

    def _embeddings(self):
        return self.embeddings
