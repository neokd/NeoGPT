import os

import torch
from chromadb.config import Settings
from colorama import init
from dotenv import load_dotenv
from langchain.chat_loaders.whatsapp import WhatsAppChatLoader
from langchain.document_loaders import (
    CSVLoader,
    JSONLoader,
    PDFMinerLoader,
    RecursiveUrlLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredExcelLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    UnstructuredTSVLoader,
    UnstructuredWordDocumentLoader,
    WebBaseLoader,
    YoutubeLoader,
)
from langchain.text_splitter import Language

# Load Environment Variables
load_dotenv()
# Initialize Colorama
init()

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
PINECONE_PERSIST_DIRECTORY = os.path.join(PARENT_DB_DIRECTORY, "pinecone")

# DEFAULT MEMORY KEY FOR CONVERSATION MEMORY (DEFAULT IS 2)
DEFAULT_MEMORY_KEY = 2

# GGUF MODELS (Recommended , Default and Fast)
MODEL_NAME = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
MODEL_FILE = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"

# MISTRAL MODEL LITE
# MODEL_NAME = "TheBloke/MistralLite-7B-GGUF"
# MODEL_FILE = "mistrallite.Q4_K_M.gguf"

# GPTQ MODELS (Quantized Models)
# MODEL_NAME = "TheBloke/Tinyllama-2-1b-miniguanaco-GPTQ"
# MODEL_FILE = "model.safetensors"

# HUGGING FACE MODEL (Not recommended for low RAM systems)
# MODEL_NAME = "microsoft/phi-1_5"
# MODEL_FILE = None

# DEFAULT EMBEDDING MODEL
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"
# EMBEDDING MODEL CONFIG
INGEST_THREADS = 8 or os.cpu_count()

# MODEL CONFIG
MAX_TOKEN_LENGTH = 8192  # 8192 is the max for Mistral-7B
N_GPU_LAYERS = 40

# PYTORCH DEVICE COMPATIBILITY
if torch.cuda.is_available():
    DEVICE_TYPE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE_TYPE = "mps"
else:
    DEVICE_TYPE = "cpu"

# CHROMA DB SETTINGS
CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)

# PINECONE SETTINGS
EMBEDDING_DIMENSION = ""
INDEX_NAME = ""

# Reserved File Names
RESERVED_FILE_NAMES = [
    "builder.url",
]

# List of file supported for ingest
DOCUMENT_EXTENSION = {
    ".pdf": PDFMinerLoader,
    ".txt": TextLoader,
    ".csv": CSVLoader,
    ".html": UnstructuredHTMLLoader,
    ".tsv": UnstructuredTSVLoader,
    ".eml": UnstructuredEmailLoader,
    ".epub": UnstructuredEPubLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".pptx": UnstructuredPowerPointLoader,
    ".ppt": UnstructuredPowerPointLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".doc": UnstructuredWordDocumentLoader,
    ".md": UnstructuredMarkdownLoader,
    ".json": JSONLoader,
    # ".py": TextLoader,
}

# List of URL patterns supported for ingest
URL_EXTENSION = {
    ".youtube": YoutubeLoader,
    "recursive": RecursiveUrlLoader,
    "normal": WebBaseLoader,
}

# List of all Social Chat and their loaders
SOCIAL_CHAT_EXTENSION = {
    r"^(chat_|_chat|whatsapp_|whatsapp_chat|whatsapp_chat_|whatsapp_)" : WhatsAppChatLoader,
}


# List of all file extensions for programming languages and their parsers
CODE_EXTENSION = {
    '.cpp': Language.CPP,
    '.go': Language.GO,
    '.java': Language.JAVA,
    '.kt': Language.KOTLIN,
    '.js': Language.JS,
    '.ts': Language.TS,
    '.php': Language.PHP,
    '.proto': Language.PROTO,
    '.py': Language.PYTHON,
    '.rst': Language.RST,
    '.ruby': Language.RUBY,
    '.rs': Language.RUST,
    '.scala': Language.SCALA,
    '.swift': Language.SWIFT,
    '.markdown': Language.MARKDOWN,
    '.latex': Language.LATEX,
    '.html': Language.HTML,
    '.sol': Language.SOL,
    '.cs': Language.CSHARP,
    '.cobol': Language.COBOL,
}


# Initial Query Cost and Total Cost
QUERY_COST = 0
TOTAL_COST = 0

# LOG CONFIG
LOG_FOLDER = os.path.join(os.path.dirname(__file__), "logs")
# BUILDER LOG
BUILDER_LOG_FILE = os.path.join(LOG_FOLDER, "builder.log")
# NEOGPT LOG
NEOGPT_LOG_FILE =  os.path.join(LOG_FOLDER, "neogpt.log")
