from abc import ABC
from langchain.schema.document import Document
class VectorStore(ABC):
    def __init__(self) -> None:
        pass

    def from_documents(self, documents: list[Document]) -> Document:
        pass

    
