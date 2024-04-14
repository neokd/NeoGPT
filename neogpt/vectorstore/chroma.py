# --- Under Development ---
"""
The Purpose of this file is to provide a wrapper around the ChromaDB
to provide a simple interface for storing and retrieving documents
from the database.
"""

import warnings

from langchain.schema.document import Document
from langchain_community.embeddings import (
    HuggingFaceEmbeddings,
)
from langchain_community.vectorstores.chroma import Chroma

from neogpt.settings.config import (
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
        warnings.filterwarnings(
            "ignore", message="<All keys matched successfully>", lineno=357
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE_TYPE, "trust_remote_code": True},
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
