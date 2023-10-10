import logging
import torch
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.llms import LlamaCpp
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.schema.agent import AgentFinish
from langchain.schema.output import LLMResult
from huggingface_hub import hf_hub_download
from langchain.utilities import GoogleSearchAPIWrapper
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.callbacks.base import BaseCallbackHandler
from vectorstore.chroma import ChromaStore
from vectorstore.faiss import FAISSStore
from langchain.vectorstores import Chroma
import argparse
from dotenv import load_dotenv
import os
from prompts.prompt import get_prompt
load_dotenv()
from config import (
    CHROMA_PERSIST_DIRECTORY,
    FAISS_PERSIST_DIRECTORY,
    MODEL_DIRECTORY,
    SOURCE_DIR,
    EMBEDDING_MODEL,
    DEVICE_TYPE,
    CHROMA_SETTINGS,
    MODEL_NAME,
    MODEL_FILE,
    N_GPU_LAYERS,
    MAX_TOKEN_LENGTH,
)
from typing import Any

# Define a custom callback handler class for token collection
class TokenCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self._tokens = []

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._tokens.append(token)

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        # Calculate the cost based on OpenAI's pricing
        cost_per_token = ((len(self._tokens) / 1000) * 0.002) * 83.33  # INR Cost per token
        total_tokens = len(self._tokens)
        print(f"\n\nTotal tokens generated: {total_tokens}")
        print(f"Total cost: {cost_per_token} INR")

# Function to load the LLM 
def load_model(device_type:str = DEVICE_TYPE, model_id:str = MODEL_NAME, model_basename:str = MODEL_FILE, LOGGING=logging):
    """
        input: device_type, model_id, model_basename, LOGGING
        output: Hugging Face model
        description:  The function loads the pre-trained model from Hugging Face and returns the loaded model.
    """
    # Checking for the availability of a CUDA-enabled GPU
    if device_type == 'cuda' and not torch.cuda.is_available():
        raise ValueError("CUDA is not available. Please use 'mps' or 'cpu' as the device_type.")
    
    try:
         # Load the Hugging Face model and tokenizer
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        # Move the model to the specified device (cuda or cpu)
        model.to(device_type)

        LOGGING.info(f"Loaded Hugging Face model: {model_name} successfully")
        return model, tokenizer
    except Exception as e:
        LOGGING.info(f"Error {e}")

# Function to set up the retrieval-based question-answering system
def db_retriver(device_type:str = DEVICE_TYPE,vectorstore:str = "Chroma", LOGGING=logging):
    """
        input: device_type,vectorstore, LOGGING
        output: None
        description: The function is used to set up the retrieval-based question-answering system. It loads the LLM model, the Chroma DB, and the prompt and memory objects. It then creates a retrieval-based question-answering system using the LLM model and the Chroma DB.
    """
    # Load the embedding model 
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE_TYPE},
        cache_folder=MODEL_DIRECTORY,
    )
    match vectorstore:
        case "Chroma":
            # Load the Chroma DB with the embedding model
            db = ChromaStore()
            LOGGING.info(f"Loaded Chroma DB Successfully")
        case "FAISS":
            # Load the FAISS DB with the embedding model
            db = FAISSStore().load_local()
            LOGGING.info(f"Loaded FAISS DB Successfully")
    # Create a retriever object 
    retriever = db.as_retriever()
    # Load the LLM model
    llm = load_model(device_type, model_id=MODEL_NAME, model_basename=MODEL_FILE, LOGGING=logging)
    # Prompt Builder Function 
    prompt , memory = get_prompt()
    # Create a retrieval-based question-answering system using the LLM model and the Vector DB
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt, "memory": memory},
    )
    # Run the retrieval-based question-answering system
    chain("Write linux command to copy file from one directory to another directory",return_only_outputs=True)

### TODO: Add the Web Search Retriever (In Progress)
def web_retriver(device_type:str = DEVICE_TYPE,vectorstore:str = "Chroma", LOGGING=logging):
    """
        input: device_type,vectorstore,LOGGING
        output: None
        description: The function is used to set up the retrieval-based question-answering system. It loads the LLM Model and searches on web for the answer backed up by the vectorstore.
        WARNING: The function is still in progress and is not yet complete.
    """
    # Load the embedding model 
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE_TYPE},
        cache_folder=MODEL_DIRECTORY,
    )
    # Import the env
    try:
        os.environ["GOOGLE_CSE_ID"] = os.environ.get("GOOGLE_CSE_ID")
        os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
        # Using Google Search API Wrapper
        print(os.environ.get("GOOGLE_CSE_ID"))
        
    except Exception as e:
        LOGGING.info(f"Error {e}")
    search = GoogleSearchAPIWrapper()
    # Load the Vector DB
    match vectorstore:
        case "Chroma":
            # Load the Chroma DB with the embedding model
            db = ChromaStore()
            LOGGING.info(f"Loaded Chroma DB Successfully")
        case "FAISS":
            # Load the FAISS DB with the embedding model
            db = FAISSStore().load_local()
            LOGGING.info(f"Loaded FAISS DB Successfully")
    
    llm = load_model(device_type, model_id=MODEL_NAME, model_basename=MODEL_FILE, LOGGING=logging)
          
    web_research_retriever = WebResearchRetriever.from_llm(
        vectorstore=db,
        llm=llm,
        search=search,
    )
    user_input = "What is Task Decomposition in LLM Powered Autonomous Agents?"
    qa_chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm ,retriever=web_research_retriever )
    result = qa_chain({"question": user_input})
    print(result)

if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO,
    )
    # Parse the arguments
    parser = argparse.ArgumentParser(description="NeoGPT CLI Interface")
    parser.add_argument(
        "--device-type",
        choices=["cpu", "mps", "cuda"],
        default=DEVICE_TYPE,
        help="Specify the device type (cpu, mps, cuda)",
    )
    parser.add_argument(
        "--db",
        choices=["Chroma", "FAISS"],
        default="Chroma",
        help="Specify the vectorstore (Chroma, FAISS)",
    )
    args = parser.parse_args()
    # db_retriver(device_type=args.device_type,vectorstore="Chroma", LOGGING=logging)
    web_retriver(device_type=args.device_type,vectorstore="FAISS", LOGGING=logging)
    
