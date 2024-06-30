from enum import Enum
from typing import List, NamedTuple

import numpy as np
from rich.progress import Progress
from sentence_transformers import SentenceTransformer
from settings import Settings


class Document(NamedTuple):
    """
    Represents a document chunk with its content and associated metadata.
    """

    content: str
    metadata: dict


class NeoMetric(Enum):
    """An enumeration of similarity metrics supported by NeoStore."""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


class NeoStore:
    """A custom vector store implementation for NeoGPT using numpy."""

    def __init__(
        self,
        embedding_model: SentenceTransformer = None,
        similarity_metric=NeoMetric.COSINE,
    ) -> None:
        self.similarity_metric = similarity_metric
        self.__vectorstore = None
        self._similarity_function = None
        self.embeddings_model = embedding_model

        if self.embeddings_model is None:
            self.embeddings_model = SentenceTransformer(
                model_name_or_path="all-MiniLM-L6-v2",
                trust_remote_code=True,
            )

        self._get_similarity_metric()

    def _get_similarity_metric(self):
        if self.similarity_metric == NeoMetric.COSINE:
            self._similarity_function = self._cosine_similarity
        elif self.similarity_metric == NeoMetric.EUCLIDEAN:
            self._similarity_function = self._euclidean_similarity
        else:
            raise ValueError("Invalid similarity metric specified.")

    def _cosine_similarity(self, query: np.ndarray):
        assert query.ndim == 1
        assert query.shape[0] == self.__vectorstore.shape[1]

        n1 = np.linalg.norm(self.__vectorstore, axis=1)
        n2 = np.linalg.norm(query)

        return np.dot(self.__vectorstore, query) / (n1 * n2)

    def _euclidean_similarity(self, query: np.ndarray):
        assert query.ndim == 1
        assert (
            query.shape[0] == self.__vectorstore.shape[1]
        ), f"Mismatch shapes.\n\nQuery shape: {query.shape[0]} Store shape: {self.__vectorstore.shape[1]}"
        distance = np.sqrt(((self.__vectorstore - query) ** 2).sum(axis=1))
        return distance

    def _get_top_k(self, query: np.ndarray, k: int):
        reverse_arr = self.similarity_metric == NeoMetric.COSINE

        arr = self._similarity_function(query)

        sorted_indices = np.argsort(arr)
        top_k_indices = (
            sorted_indices[:k] if not reverse_arr else sorted_indices[::-1][:k]
        )

        top_k_scores = arr[top_k_indices]

        top_k_docs = []

        for j, idx in enumerate(top_k_indices):
            if idx < len(self.docs):
                # Get the existing document
                doc = self.docs[idx]

                # Add score to the existing metadata
                doc_metadata = (
                    doc.metadata.copy()
                )  # Make a copy to avoid modifying the original
                doc_metadata["score"] = top_k_scores[j]

                # Append the updated Document instance to top_k_docs
                top_k_docs.append(Document(content=doc.content, metadata=doc_metadata))
            else:
                # Handle the case where idx is out of range of self.docs
                print(f"Warning: Index {idx} is out of range of self.docs")

        # Ensure we return exactly k documents if possible
        if len(top_k_docs) < k:
            print(f"Warning: Only {len(top_k_docs)} documents found, less than k={k}")

        assert len(top_k_docs) == min(k, len(self.docs))
        assert top_k_scores.ndim == 1

        return top_k_docs

    def build_store(
        self,
        docs: list[Document],
        batch_size: int = 32,
        persist: bool = False,
        embeddings_path: str = Settings.VECTOR_STORE_DIR,
    ) -> np.ndarray:
        """
        Convert a list of documents into embeddings in batches with a rich progress bar.

        Args:
            docs (List[Document]): List of documents as NamedTuple instances (Document).
            batch_size (int): Batch size for processing documents.
            persist (bool): Whether to persist embeddings to disk.
            embeddings_path (str): Path to save the embeddings.

        Returns:
            np.ndarray: Array of embeddings.
        """
        embeddings = []
        self.docs = docs

        num_docs = len(docs)
        num_batches = (num_docs + batch_size - 1) // batch_size

        with Progress(
            expand=True,
        ) as progress:
            task = progress.add_task("Building Vector Store...", total=num_docs)

            for i in range(num_batches):
                start = i * batch_size
                end = min(start + batch_size, num_docs)
                batch_docs = docs[start:end]
                batch_embeddings = self.embeddings_model.encode(
                    [doc.content for doc in batch_docs]
                )
                embeddings.extend(batch_embeddings)

                progress.update(task, advance=len(batch_docs))

        self.__vectorstore = np.array(embeddings)

        if persist:
            self.save_embeddings(embeddings_path)

        return self.__vectorstore

    def save_embeddings(self, path: str):
        """
        Save the vector store embeddings and associated documents to an .npz file.

        Args:
            path (str): Path to save the embeddings and documents.
        """
        if not path.endswith(".npz"):
            path += "neostore.npz"
        if self.__vectorstore is not None:
            docs = [(doc.content, doc.metadata) for doc in self.docs]

            np.savez(
                path,
                embeddings=self.__vectorstore,
                docs=docs,
            )
        else:
            raise ValueError("Vector store is empty. Build the store first.")

    @classmethod
    def load_embeddings(
        cls,
        path: str,
        embedder: SentenceTransformer = None,
        similarity_metric=NeoMetric.COSINE,
    ):
        """
        Load the vector store embeddings and associated documents from an .npz file.

        Args:
            path (str): Path to load the embeddings and documents.
            embedder (SentenceTransformer, optional): SentenceTransformer model for embeddings.
            similarity_metric (NeoMetric, optional): Similarity metric to use.

        Returns:
            NeoStore: Loaded NeoStore instance with embeddings and documents.
        """

        data = np.load(path, allow_pickle=True)

        if isinstance(data, np.lib.npyio.NpzFile):
            embeddings = data["embeddings"]
            docs = [
                Document(
                    content=content,
                    metadata={"file_path": metadata.get("file_path", "")},
                )
                for content, metadata in data["docs"]
            ]
        else:
            embeddings = data
            docs = []

        store = cls(embedder, similarity_metric)
        store.__vectorstore = embeddings
        store.docs = docs  # Set the loaded documents to the store

        return store

    def search(self, query: str, k: int = 5) -> list[Document]:
        """
        Search for top-k documents similar to a given query.

        Args:
            query (str): Query string.
            k (int): Number of top-k documents to retrieve.

        Returns:
            List[Document]: List of top-k documents with content and metadata.
        """
        assert self.embeddings_model is not None
        assert k >= 1, f"K should be greater than 0. Got: {k}"
        query_embedding = self.embeddings_model.encode([query])
        return self._get_top_k(query_embedding[0], k)
