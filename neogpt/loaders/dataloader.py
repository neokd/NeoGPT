import os
import time
from typing import NamedTuple, List
from file import LOADER_MAP


class Document(NamedTuple):
    """
    Represents a document chunk with its content and associated metadata.
    """

    content: str
    metadata: dict


class CharacterTextSplitter:
    """
    A utility class to split text into chunks based on specified parameters.
    """

    def __init__(self, chunk_size: int = 1000, overlap_ratio: float = 0.2):
        """
        Initialize the CharacterTextSplitter.

        Args:
            chunk_size (int): The size of each chunk.
            overlap_ratio (float): The overlap ratio between consecutive chunks.
        """
        self.chunk_size = chunk_size
        self.overlap_size = int(chunk_size * overlap_ratio)
        self.separators = ["\n\n", "\n", " ", ""]

    def split_text_into_chunks(self, text: str) -> List[str]:
        """
        Split the given text into chunks using predefined separators or by lines.

        Args:
            text (str): The text to be split into chunks.

        Returns:
            List[str]: A list of chunks extracted from the text.
        """
        chunks = []
        text_length = len(text)

        for i in range(0, text_length, self.chunk_size - self.overlap_size):
            end = min(i + self.chunk_size, text_length)
            buffer = text[i:end].strip()
            chunks.append(buffer)

        return chunks


class DataLoader:
    """
    A data loader class to load data from a file and process it in chunks.
    """

    def __init__(self, file_path: str):
        """
        Initialize the DataLoader with the file path.

        Args:
            file_path (str): The path to the file to load.
        """
        self.file_path = file_path
        self.loader = self._get_loader()

    def _get_loader(self):
        """
        Get the appropriate loader for the file based on its extension.

        Returns:
            loader: An instance of the appropriate loader for the file.
        """
        file_ext = os.path.splitext(self.file_path)[1]
        loader_class = LOADER_MAP.get(file_ext)
        if not loader_class:
            raise ValueError(f"No loader found for file extension {file_ext}")
        return loader_class(self.file_path)

    def load_data(self) -> str:
        """
        Load the entire content of the file as a string.

        Returns:
        str: The content of the file as a string.
        """
        # return "".join(self.loader.lazy_load())
        return self.loader.load()

    def lazy_load_data(self) -> str:
        raise NotImplementedError("Lazy loading is not supported for this loader.")

    def load_in_chunks(
        self, chunk_size: int = 1000, overlap_ratio: float = 0.2
    ) -> List[Document]:
        """
        Load data from the file in chunks with optional overlap.

        Args:
            chunk_size (int): The size of each chunk.
            overlap_ratio (float): The overlap ratio between consecutive chunks.

        Returns:
            List[Document]: A list of Document namedtuple containing content chunks and metadata.
        """
        splitter = CharacterTextSplitter(chunk_size, overlap_ratio)
        data = self.load_data()

        chunks = splitter.split_text_into_chunks(data)
        documents = [
            Document(content=chunk, metadata={"file_path": self.file_path})
            for chunk in chunks
        ]

        return documents


if __name__ == "__main__":
    file_path = "/Users/kuldeep/Downloads/chinook.db"  # Replace with your file path
    start = time.time()

    data_loader = DataLoader(file_path)
    print("Loading data in chunks with overlap:")
    documents = data_loader.load_in_chunks(
        chunk_size=1000, overlap_ratio=0.02
    )  # Adjust as needed

    for doc in documents:
        print(doc)

    print(f"Time taken: {time.time() - start:.2f} seconds")
