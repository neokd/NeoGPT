"""
    The Purpose of this file is to provide a wrapper around the FAISS from langchain
"""
from vectorstore.base import VectorStore
from langchain.schema.document import Document
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from config import (
    FAISS_PERSIST_DIRECTORY,
    EMBEDDING_MODEL,
    DEVICE_TYPE,
    MODEL_DIRECTORY,
)

class FAISSStore(VectorStore):
    def __init__(self) -> None:
        self.embeddings = HuggingFaceInstructEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": DEVICE_TYPE},
            cache_folder=MODEL_DIRECTORY,
        )
        self.faiss = FAISS(
            embedding_function=None,
            index=0,
            index_to_docstore_id={},
            docstore={},
        )
        self.docstore = None

    def from_documents(self, documents: list[Document]) -> Document:
        self.docstore = self.faiss.from_documents(
            documents=documents,
            embedding=self.embeddings,
        )
        self.docstore.save_local(FAISS_PERSIST_DIRECTORY) 
        # self.faiss.save_local(FAISS_PERSIST_DIRECTORY)

    def load_local(self):
        self.docstore = self.faiss.load_local(
            folder_path=FAISS_PERSIST_DIRECTORY,
            embeddings=self.embeddings,
        )
        return self.docstore

    def as_retriever(self):
        return self.docstore.as_retriever()