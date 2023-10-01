import os 
import torch
from chromadb.config import Settings
from pathlib import Path

BASE_DIR = Path(__file__).parent  # Get the parent directory of this script
SOURCE_DIR = BASE_DIR / "documents"  # Define the source document directory
MODEL_DIRECTORY = BASE_DIR / "models"  # Define the directory to store HuggingFace models
PERSIST_DIRECTORY = BASE_DIR / "db"  # Define the directory for Vector Embeddings storage


# MODELS 
MODEL_NAME = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
MODEL_FILE = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L12-v2"

# MODEL CONFIG
MAX_TOKEN_LENGTH = 4094 # 8192 is the max for Mistral-7B
N_GPU_LAYERS = 40

# PYTORCH DEVICE COMPATIBILITY
if torch.cuda.is_available():
    DEVICE_TYPE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE_TYPE = "mps"
else:
    DEVICE_TYPE = "cpu"

# DATABASE SETTINGS
CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)
