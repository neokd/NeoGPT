from abc import ABC

from langchain.schema.document import Document


class VectorStore(ABC):
    """
    Base class for VectorStore
    """

    def __init__(self) -> None:
        pass

    def from_documents(self, documents: list[Document]) -> Document:
        pass
