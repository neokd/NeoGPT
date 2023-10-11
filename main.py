import logging
import torch
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.llms import LlamaCpp, HuggingFacePipeline
from langchain.callbacks.manager import CallbackManager
from langchain.schema.agent import AgentFinish
from langchain.schema.output import LLMResult
from huggingface_hub import hf_hub_download
from langchain.utilities import GoogleSearchAPIWrapper
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, pipeline, AutoModelForCausalLM
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.callbacks.base import BaseCallbackHandler
from vectorstore.chroma import ChromaStore
from vectorstore.faiss import FAISSStore
from langchain.vectorstores import Chroma
from pinecone import Pinecone,PineconeClient
import argparse
from dotenv import load_dotenv
import os
from prompts.prompt import get_prompt
load_dotenv()
from config import (
    MODEL_DIRECTORY,
    DEVICE_TYPE,
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
    if model_basename is not None and ".gguf" in model_basename.lower() :

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

    else:
        try:
            # Load the Hugging Face model and tokenizer
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map="auto",
                # torch_dtype=torch.float16,
                # low_cpu_mem_usage=True,
                # load_in_4bit=True,
                # bnb_4bit_quant_type="nf4",
                # bnb_4bit_compute_dtype=torch.float16,
                cache_dir=MODEL_DIRECTORY,
                trust_remote_code=True
            )
            # print(model)
            tokenizer = AutoTokenizer.from_pretrained(model_id,device_map="auto",trust_remote_code=True)
            # Move the model to the specified device (cuda or cpu)
            # model.to(device_type)
            # model.tie_weights()
            # torch.set_default_device(device_type)
            LOGGING.info(f"Loaded Hugging Face model: {model_id} successfully")
            generation_config = GenerationConfig.from_pretrained(model_id)
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=MAX_TOKEN_LENGTH,
                # temperature=0.2,
                # top_p=0.95,
                # do_sample=True,
                # repetition_penalty=1.15,
                generation_config=generation_config,
            )
            llm = HuggingFacePipeline(pipeline=pipe)
            llm("Hello World")
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")

# Function to set up the retrieval-based question-answering system
def db_retriver(device_type:str = DEVICE_TYPE,vectorstore:str = "Chroma", LOGGING=logging):
    """
        input: device_type,vectorstore, LOGGING
        output: None
        description: The function is used to set up the retrieval-based question-answering system. It loads the LLM model, the Chroma DB, and the prompt and memory objects. It then creates a retrieval-based question-answering system using the LLM model and the Chroma DB.
    """
    match vectorstore:
        case "Chroma":
            # Load the Chroma DB with the embedding model
            db = ChromaStore()
            LOGGING.info(f"Loaded Chroma DB Successfully")
        case "FAISS":
            # Load the FAISS DB with the embedding model
            db = FAISSStore().load_local()
            LOGGING.info(f"Loaded FAISS DB Successfully")
        case "Pinecone":
            # Initialize Pinecone client
            # Load the Pinecone DB with the embedding model
            pinecone_api_key = "your_api_key"
            pinecone_environment = "your_environment_name"
            db= Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)
            LOGGING.info(f"Initialized Pinecone DB Successfully")
            
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
        case "Pinecone":
            # Initialize Pinecone client
            # Load the Pinecone DB with the embedding model
            pinecone_api_key = "your_api_key"
            pinecone_environment = "your_environment_name"
            db= Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)
            LOGGING.info(f"Initialized Pinecone DB Successfully")
            
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
    db_retriver(device_type=args.device_type,vectorstore="Chroma", LOGGING=logging)
    # web_retriver(device_type=args.device_type,vectorstore="FAISS", LOGGING=logging)
    
