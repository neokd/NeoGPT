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
from dotenv import load_dotenv
import os

from neogpt.config import (
    QDRANT_PERSIST_DIRECTORY,
    DEVICE_TYPE,
    EMBEDDING_MODEL,
    MODEL_DIRECTORY,
)
from neogpt.vectorstore.base import VectorStore


load_dotenv()

QDRANT_URL=os.environ.get("QDRANT_URL")
QDRANT_API_KEY=os.environ.get("QDRANT_API_KEY")

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
        self.qdrant=QdrantClient(url=QDRANT_URL,api_key=QDRANT_API_KEY)

    def from_documents(self, documents: list[Document]):
        try:
        # self.qdrant.create_collection(collection_name="documents",vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE))
            qd=Qdrant.from_documents(documents,self.embeddings,url=QDRANT_URL,api_key=QDRANT_API_KEY,collection_name="documents")
            return documents
        except Exception as e:
            raise Exception("database not build please run 'python main.py --build --mode db --db qdrant'")

    def as_retriever(self):
        try:
            client=QdrantClient(url=QDRANT_URL,api_key=QDRANT_API_KEY)
            qdrant=Qdrant(client=client,collection_name="documents",embeddings=self.embeddings)
            retriever=qdrant.as_retriever()
            return retriever
        except Exception as e:
            raise Exception("Having difficulty to connect to qdrant cloud")

    def get(self):
        return self.qdrant

    def _embeddings(self):
        return self.embeddings
