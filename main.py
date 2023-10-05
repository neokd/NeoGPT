import logging
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.llms import LlamaCpp
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.schema.agent import AgentFinish
from langchain.schema.output import LLMResult
from langchain.vectorstores import Chroma
from huggingface_hub import hf_hub_download
from langchain.callbacks.base import BaseCallbackHandler

import argparse
import click
import psutil

from prompts.prompt import get_prompt

from config import (
    CHROMA_PERSIST_DIRECTORY,
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
        output: llm (LlamaCpp)
        description: The function loads the LLM model locally or downloads it from huggingface, and returns the LLM object.
    """
    # Create a callback manager to handle callbacks during model loading
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler(),TokenCallbackHandler()])
    try:
        # Download the model checkpoint from the Hugging Face Hub
        model_path = hf_hub_download(
            repo_id=model_id,
            filename=model_basename,
            resume_download=True,
            cache_dir=MODEL_DIRECTORY,
        )
        # Model Parameters
        kwargs = {
            "model_path": model_path,
            "max_tokens": MAX_TOKEN_LENGTH,
            "n_ctx": MAX_TOKEN_LENGTH,
            "n_batch": 512,  
            "callback_manager": callback_manager,
            "verbose":False,
            "f16_kv":True,
            "streaming":True,
        }
        if device_type.lower() == "mps":
            kwargs["n_gpu_layers"] = 1 # only for MPS devices
        if device_type.lower() == "cuda":
            kwargs["n_gpu_layers"] = N_GPU_LAYERS  # set this based on your GPU
        # Create a LlamaCpp object (language model)
        llm =  LlamaCpp(**kwargs)
        LOGGING.info(f"Loaded {model_id} locally")
        return llm  # Returns a LlamaCpp object (language model)
    except Exception as e:
        LOGGING.info(f"Error {e}")

# Function to set up the retrieval-based question-answering system
def db_retriver(device_type:str = DEVICE_TYPE, LOGGING=logging):
    """
        input: device_type, LOGGING
        output: None
        description: The function is used to set up the retrieval-based question-answering system. It loads the LLM model, the Chroma DB, and the prompt and memory objects. It then creates a retrieval-based question-answering system using the LLM model and the Chroma DB.
    """
    # Load the embedding model used with Chroma DB.
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE_TYPE},
        cache_folder=MODEL_DIRECTORY,
    )
    # Load the Chroma DB with the embedding model
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
    # Create a retriever object from the Chroma DB
    retriever = db.as_retriever()
    LOGGING.info(f"Loaded Chroma DB Successfully")
    # Load the LLM model
    llm = load_model(device_type, model_id=MODEL_NAME, model_basename=MODEL_FILE, LOGGING=logging)
    # Prompt Builder Function 
    prompt , memory = get_prompt()
    # Create a retrieval-based question-answering system using the LLM model and the Chroma DB
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt, "memory": memory},
    )
    # Run the retrieval-based question-answering system
    chain("Hello world",return_only_outputs=True)

def get_cpu_info():
    cpu_info = {}
    cpu_info['CPU'] = psutil.cpu_info()[0].model
    cpu_info['Cores'] = psutil.cpu_count(logical=False)
    cpu_info['Threads'] = psutil.cpu_count(logical=True)
    cpu_info['Usage'] = psutil.cpu_percent(interval=1)

    return cpu_info

def get_gpu_info():
    try:
        import gpustat
        gpu_info = gpustat.GPUStatCollection.new_query().jsonify()
    except ImportError:
        gpu_info = "gpustat library not installed. Install it for better GPU information."

    return gpu_info


def argparse_get_device_info():
    parser = argparse.ArgumentParser(description="Get CPU and GPU Information")

    parser.add_argument(
        "--device-type",
        choices=["cpu", "mps", "cuda"],
        default="cpu",
        help="Specify the device type (cpu, mps, cuda)",
    )
    parser.add_argument(
        "--specific-model",
        type=str,
        default="default",
        help="Specify the specific model or identifier",
    )

    args = parser.parse_args()

    if args.device_type == "cpu":
        info = get_cpu_info()
    elif args.device_type == "cuda" or args.device_type == "mps":
        info = get_gpu_info()
    else:
        info = "Invalid device type specified."

    print(f"Device Type (argparse): {args.device_type}")
    print(f"Specific Model (argparse): {args.specific_model}")
    print(info)


@click.command()
@click.option("--device-type", type=click.Choice(["cpu", "mps", "cuda"]), default="cpu", help="Specify the device type (cpu, mps, cuda)")
@click.option("--specific-model", type=str, default="default", help="Specify the specific model or identifier")
def click_get_device_info(device_type, specific_model):
    if device_type == "cpu":
        info = get_cpu_info()
    elif device_type == "cuda" or device_type == "mps":
        info = get_gpu_info()
    else:
        info = "Invalid device type specified."

    click.echo(f"Device Type (click): {device_type}")
    click.echo(f"Specific Model (click): {specific_model}")
    click.echo(info)

if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO,
    )
    db_retriver()
    click_get_device_info()
    
