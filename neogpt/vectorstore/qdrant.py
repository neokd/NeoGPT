# --- Under Development ---
"""
    The Purpose of this file is to provide a wrapper around the QdrantDB
    to provide a simple interface for storing and retrieving documents
    from the database.
"""

from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.schema.document import Document
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient

from neogpt.config import (
    QDRANT_PERSIST_DIRECTORY,
    DEVICE_TYPE,
    EMBEDDING_MODEL,
    MODEL_DIRECTORY,
)
from neogpt.vectorstore.base import VectorStore


class QdrantStore(VectorStore):
    """
    The QdrantStore class provides a wrapper around the QdrantDB
    to provide a simple interface for storing and retrieving documents
    from the database.
    """

    def __init__(self) -> None:
        self.embeddings = HuggingFaceInstructEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE_TYPE},
            cache_folder=MODEL_DIRECTORY,
        )

    def from_documents(self, documents: list[Document]) -> Document:
        qdrant=Qdrant.from_documents(documents,self.embeddings,path=QDRANT_PERSIST_DIRECTORY,collection_name="documents")
        return documents

    def as_retriever(self):
        return self.chroma.as_retriever()

    def _embeddings(self):
        return self.embeddings
