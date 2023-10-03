from chromadb.utils import embedding_functions
from typing import Optional, List
class ChromaStore:
    def __init__(self,model) -> None:
        try:
            import chromadb
            import chromadb.config
        except ImportError:
            raise ImportError(
                "Could not import chromadb python package. "
                "Please install it with `pip install chromadb`."
            )

 
if __name__ == '__main__':
    ChromaStore