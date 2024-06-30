import os


class Settings:
    """This class contains the default settings for the NeoGPT."""

    # Default Directories to use.
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    MODEL_DIR = os.path.join(ROOT_DIR, "models")
    CONVERSATION_DIR = os.path.join(ROOT_DIR, "conversations")
    WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")

    VECTOR_STORE_DIR = os.path.join(ROOT_DIR, "vectorstore/store/")

    # MODEL SETTINGS
    MODEL_NAME = os.getenv("MODEL_NAME", "TheBloke/Mistral-7B-Instruct-v0.1-GGUF")
    MODEL_FILE = os.getenv("MODEL_FILE", "mistral-7b-instruct-v0.1.Q4_K_M.gguf")

    DEFAULT_MODEL_DIR = os.path.join(MODEL_DIR, MODEL_FILE)
