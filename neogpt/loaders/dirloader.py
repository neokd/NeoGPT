import os
import time
from typing import List, NamedTuple

from loaders.file import LOADER_MAP
from utils.cprint import cprint


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

    def split_text_into_chunks(self, text: str) -> list[str]:
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


class DirectoryLoader:
    """
    A data loader class to load data from files and process it in chunks.
    """

    def __init__(self, path: str):
        """
        Initialize the DataLoader with the file or directory path.

        Args:
            path (str): The path to the file or directory to load.
        """
        self.path = path
        self.is_directory = os.path.isdir(path)  # Check if path is a directory

    def _get_loader(self, file_path: str):
        """
        Get the appropriate loader for the file based on its extension.

        Args:
            file_path (str): The path to the file.

        Returns:
            loader: An instance of the appropriate loader for the file.
        """
        file_ext = os.path.splitext(file_path)[1]
        loader_class = LOADER_MAP.get(file_ext)
        if not loader_class:
            print(f"No loader found for file extension {file_ext}")
        return loader_class(file_path)

    def _load_file(self, file_path: str) -> str:
        """
        Load the entire content of a single file as a string.

        Args:
            file_path (str): The path to the file.

        Returns:
        str: The content of the file as a string.
        """
        try:
            loader = self._get_loader(file_path)
            return loader.load()
        except Exception as e:
            print(
                "File type not supported",
                os.extsep.join(os.path.basename(file_path).split(os.extsep)[1:]),
                e,
            )
            return ""

    def load_data(
        self, chunk_size: int = 1000, overlap_ratio: float = 0.2
    ) -> list[Document]:
        """
        Load data from the specified file or directory.

        Args:
            chunk_size (int): Optional. The size of each chunk.
            overlap_ratio (float): Optional. The overlap ratio between consecutive chunks.

        Returns:
            List[Document]: A list of Document namedtuple containing content chunks and metadata.
        """
        processed_file = 0
        if self.is_directory:
            start = time.time()
            # print(os.path.abspath(self.path))
            documents = []
            for root, _, files in os.walk(os.path.abspath(self.path)):
                for file in files:
                    file_path = os.path.join(root, file)
                    documents.extend(
                        self._process_file(file_path, chunk_size, overlap_ratio)
                    )
                    processed_file += 1
            print(
                f"Loaded {processed_file} files from : {self.path} in {time.time() - start:.2f} seconds"
            )
            return documents
        else:
            print(f"Loaded 1 document from file: {self.path}")
            return self._process_file(self.path, chunk_size, overlap_ratio)

    def _process_file(
        self, file_path: str, chunk_size: int = 1000, overlap_ratio: float = 0.2
    ) -> list[Document]:
        """
        Process a single file, loading data and splitting it into chunks.

        Args:
            file_path (str): The path to the file.
            chunk_size (int): Optional. The size of each chunk.
            overlap_ratio (float): Optional. The overlap ratio between consecutive chunks.

        Returns:
            List[Document]: A list of Document namedtuple containing content chunks and metadata.
        """
        splitter = CharacterTextSplitter(chunk_size, overlap_ratio)
        data = self._load_file(file_path)

        chunks = splitter.split_text_into_chunks(data)
        documents = [
            Document(content=chunk, metadata={"file_path": file_path})
            for chunk in chunks
        ]

        return documents

    def load_in_chunks(
        self, chunk_size: int = 1000, overlap_ratio: float = 0.2
    ) -> list[Document]:
        """
        Load data from the file or directory in chunks with optional overlap.

        Args:
            chunk_size (int): Optional. The size of each chunk.
            overlap_ratio (float): Optional. The overlap ratio between consecutive chunks.

        Returns:
            List[Document]: A list of Document namedtuple containing content chunks and metadata.
        """
        return self.load_data(chunk_size, overlap_ratio)

