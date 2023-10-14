import os 
import torch
from chromadb.config import Settings
from langchain.document_loaders import (
    PDFMinerLoader, 
    TextLoader,
    UnstructuredHTMLLoader,
    UnstructuredTSVLoader,
    CSVLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader,
    JSONLoader,
    YoutubeLoader
)

# Source Directory for Documents to Ingest
SOURCE_DIR = os.path.join(os.path.dirname(__file__), "documents")
# To store models from HuggingFace
MODEL_DIRECTORY = os.path.join(os.path.dirname(__file__), "models")
# PARENT DB DIRECTORY
PARENT_DB_DIRECTORY = os.path.join(os.path.dirname(__file__), "db")
# CHROMA DB DIRECTORY
CHROMA_PERSIST_DIRECTORY = os.path.join(PARENT_DB_DIRECTORY, "chroma")
# FAISS DB DIRECTORY
FAISS_PERSIST_DIRECTORY = os.path.join(PARENT_DB_DIRECTORY, "faiss")
# PINECONE DB DIRECTORY
PINECONE_PERSIST_DIRECTORY = os.path.join(PARENT_DB_DIRECTORY,"pinecone")

# GGUF MODELS (Recommended , Default and Fast)
# MODEL_NAME = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
# MODEL_FILE = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
# HUGGING FACE MODEL (Not recommended for low RAM systems)
MODEL_NAME = "microsoft/phi-1_5"
MODEL_FILE = None
# DEFAULT EMBEDDING MODEL
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"
# EMBEDDING MODEL CONFIG
INGEST_THREADS = 8 or os.cpu_count()

# MODEL CONFIG
MAX_TOKEN_LENGTH = 2048 # 8192 is the max for Mistral-7B
N_GPU_LAYERS = 40

# PYTORCH DEVICE COMPATIBILITY
if torch.cuda.is_available():
    DEVICE_TYPE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE_TYPE = "mps"
else:
    DEVICE_TYPE = "cpu"

#  CHROMA DB SETTINGS
CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)

# PINECONE SETTINGS
EMBEDDING_DIMENSION = ""
INDEX_NAME = ""

# List of file supported for ingest 
DOCUMENT_EXTENSION = {
    '.pdf': PDFMinerLoader,
    '.txt': TextLoader,
    '.csv' :CSVLoader,
    '.html' :UnstructuredHTMLLoader, 
    '.tsv' :UnstructuredTSVLoader,
    '.eml' :UnstructuredEmailLoader,
    '.epub' :UnstructuredEPubLoader,
    '.xls' :UnstructuredExcelLoader,
    '.xlsx' :UnstructuredExcelLoader,
    '.pptx' :UnstructuredPowerPointLoader,
    '.ppt' :UnstructuredPowerPointLoader,
    '.docx' :UnstructuredWordDocumentLoader,
    '.doc' :UnstructuredWordDocumentLoader,
    '.md' :UnstructuredMarkdownLoader,
    '.json' :JSONLoader,
    '.youtube' :YoutubeLoader,
}
