# --- Under Development ---
"""
    The Purpose of this file is to provide a wrapper around the ChromaDB
    to provide a simple interface for storing and retrieving documents
    from the database.
"""


import chromadb
from typing import Optional, List
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema.document import Document
class ChromaStore:
    CHROMA_SETTINGS = chromadb.Settings(
        anonymized_telemetry=False,
        is_persistent=True,
    )
    CHROMA_PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "db")

    def __init__(self) -> None:
        self.chroma_client = chromadb.PersistentClient(path=self.CHROMA_PERSIST_DIRECTORY,settings=self.CHROMA_SETTINGS)

    def batch_add(self,documents:List[Document]) -> List[Document]:
        max_batch_size = self.chroma_client.max_batch_size
        for i in range(0, len(documents), max_batch_size):
            yield documents[i:i + max_batch_size]




if __name__ == '__main__':
    ChromaStore()