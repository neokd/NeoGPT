"""
    The Purpose of this file is to provide a wrapper around the FAISS from langchain
"""

from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.schema.document import Document
from langchain.vectorstores import FAISS

from neogpt.config import (
    DEVICE_TYPE,
    EMBEDDING_MODEL,
    FAISS_PERSIST_DIRECTORY,
    MODEL_DIRECTORY,
)
from neogpt.vectorstore.base import VectorStore


class FAISSStore(VectorStore):
    """
    The FAISSStore class provides a wrapper around the FAISS
    to provide a simple interface for storing and retrieving documents
    from the database.
    """

    def __init__(self) -> None:
        self.embeddings = HuggingFaceInstructEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE_TYPE},
            cache_folder=MODEL_DIRECTORY,
        )
        self.faiss = FAISS(
            embedding_function=None, index=0, index_to_docstore_id={}, docstore={}
        )
        self.docstore = None

    def from_documents(self, documents: list[Document]) -> Document:
        self.docstore = self.faiss.from_documents(
            documents=documents, embedding=self.embeddings
        )
        self.docstore.save_local(FAISS_PERSIST_DIRECTORY)
        # self.faiss.save_local(FAISS_PERSIST_DIRECTORY)

    def load_local(self):
        self.docstore = self.faiss.load_local(
            folder_path=FAISS_PERSIST_DIRECTORY, embeddings=self.embeddings
        )
        return self.docstore

    def as_retriever(self):
        return self.docstore.as_retriever()

    def get(self):
        self.docstore = self.faiss.load_local(
            folder_path=FAISS_PERSIST_DIRECTORY, embeddings=self.embeddings
        )
        if self.docstore is not None:
            return str(self.docstore)
        else:
            return "No document store loaded."

    def _embeddings(self):
        return self.embeddings
