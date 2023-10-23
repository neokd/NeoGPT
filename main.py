import logging
import torch
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.llms import LlamaCpp, HuggingFacePipeline
from langchain.callbacks.manager import CallbackManager
from langchain.schema.output import LLMResult
from huggingface_hub import hf_hub_download
from langchain.utilities import GoogleSearchAPIWrapper
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, pipeline, AutoModelForCausalLM, TextGenerationPipeline
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.callbacks.base import BaseCallbackHandler
from vectorstore.chroma import ChromaStore
from vectorstore.faiss import FAISSStore
# from vectorstore.pinecone import PineconeVectorStore
from builder import builder
from dotenv import load_dotenv
import os, time, sys, select, argparse
from prompts.prompt import get_prompt
from colorama import init, Fore
load_dotenv()
init()
from config import (
    MODEL_DIRECTORY,
    DEVICE_TYPE,
    MODEL_NAME,
    MODEL_FILE,
    N_GPU_LAYERS,
    MAX_TOKEN_LENGTH,
    QUERY_COST,
    TOTAL_COST
)
from typing import Any, Dict, List, Optional

class StreamingStdOutCallbackHandler(BaseCallbackHandler):

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        # Start a new line for a clean display
        sys.stdout.write("\n")
        sys.stdout.write(Fore.BLUE + "NeoGPT 🤖 is thinking...")

        # Add a loading animation to show activity
        loading_chars = "/-\\"
        for char in loading_chars:
            sys.stdout.write('\b' + char)  # Move the cursor back to overwrite the token
            sys.stdout.flush()
            time.sleep(0.1)
        
        sys.stdout.write(Fore.BLUE + "\nNeoGPT 🤖:")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Display the generated token in a friendly way
        sys.stdout.write(Fore.WHITE + token)
        sys.stdout.flush()

        
       
               
# Define a custom callback handler class for token collection
class TokenCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self._tokens = []

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._tokens.append(token)

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        global TOTAL_COST, QUERY_COST  # Use the global variables
        # Cost are based on OpenAI's pricing model
        QUERY_COST = round(((len(self._tokens) / 1000) * 0.002) * 83.33, 5)  # INR Cost per token, rounded to 5 decimal places
        TOTAL_COST = round(TOTAL_COST + QUERY_COST, 5)  # Accumulate the cost, rounded to 5 decimal places
        total_tokens = len(self._tokens)
        print(Fore.WHITE + f"\n\nTotal tokens generated: {total_tokens}")
        print(Fore.WHITE + f"Query cost: {QUERY_COST} INR")
        print(Fore.WHITE + f"Total cost: {TOTAL_COST} INR")

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

    elif model_basename is not None and ".safetensors" in model_basename.lower() :
        try:
            if ".safetensors" in model_basename.lower():
                model_basename = model_basename.replace(".safetensors","")
            # Load GPTQ model from huggingface
            model = AutoGPTQForCausalLM.from_quantized(
                model_id,
                model_basename=model_basename,
                use_safetensors=True,
                trust_remote_code=True,
                device_map="auto",
                # device= "cuda" if torch.cuda.is_available() else "cpu",
                use_triton=False,
                cache_dir=MODEL_DIRECTORY,
                quantize_config=None,
            )
            # print(model)
            tokenizer = AutoTokenizer.from_pretrained(model_id,use_fast=True)
            LOGGING.info(f"Loaded GPTQ model: {model_id} successfully")
            # generation_config = GenerationConfig.from_pretrained(model_id)
            pipe = TextGenerationPipeline(
                task="text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.95,
                repetition_penalty=1.15
            )
            llm = HuggingFacePipeline(pipeline=pipe)
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")

    else:
        try:
            LOGGING.warning(f"🚨 You are using an large model. Please use a quantized model for better performance")
            kwargs = {
                # "temperature": 0, 
                "max_length": MAX_TOKEN_LENGTH, 
                "cache_dir":  MODEL_DIRECTORY,
                "trust_remote_code":True 
            }
            llm = HuggingFacePipeline.from_model_id(
                model_id = MODEL_NAME,
                task="text-generation",
                # device=0,
                model_kwargs=kwargs,
            )
            LOGGING.info(f"Loaded {model_id} successfully")
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")

# Function to set up the retrieval-based question-answering system
def db_retriver(device_type:str = DEVICE_TYPE,vectordb:str = "Chroma", retriever:str = "local",persona:str="default" ,LOGGING=logging):
    """
        input: device_type,vectorstore, LOGGING
        output: None
        description: The function is used to set up the retrieval-based question-answering system. It loads the LLM model, the Chroma DB, and the prompt and memory objects. It then creates a retrieval-based question-answering system using the LLM model and the Chroma DB.
    """
    match vectordb:
        case "Chroma":
            # Load the Chroma DB with the embedding model
            db = ChromaStore()
            LOGGING.info(f"Loaded Chroma DB Successfully")
        case "FAISS":
            # Load the FAISS DB with the embedding model
            db = FAISSStore().load_local()
            LOGGING.info(f"Loaded FAISS DB Successfully")
        # case "Pinecone":
            # Initialize Pinecone client
            # Load the Pinecone DB with the embedding model
            # pinecone_api_key = "your_api_key"
            # pinecone_environment = "your_environment_name"
            # db= Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)
            # LOGGING.info(f"Initialized Pinecone DB Successfully")

    # Load the LLM model
    llm = load_model(device_type, model_id=MODEL_NAME, model_basename=MODEL_FILE, LOGGING=logging)

    # Prompt Builder Function 
    prompt , memory = get_prompt(persona=persona)
    match retriever:
        case "local":
            LOGGING.info("Loaded Local Retriever Successfully 🚀")
            # Create a retriever object 
            local_retriever = db.as_retriever()
            chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=local_retriever,
                chain_type="stuff",
                chain_type_kwargs={
                    "prompt": prompt, 
                    "memory": memory
                    },
                )
        
        case "web":
            LOGGING.info("Loaded Web Retriever Successfully 🔍")
            try:
                os.environ["GOOGLE_CSE_ID"] = os.environ.get("GOOGLE_CSE_ID")
                os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
            except Exception as e:
                LOGGING.info(f"Error {e}")

            web_retriever = WebResearchRetriever.from_llm(
                vectorstore=db,
                llm=llm,
                search=GoogleSearchAPIWrapper(),
            )
            # Create a retriever chain
            chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=web_retriever,
                chain_type="stuff",
                chain_type_kwargs={
                    "prompt": prompt, 
                    "memory": memory
                    },
            )

        case "hybrid":
            LOGGING.info("Loaded Hybrid Retriever Successfully ⚡️")
            local_retriver = db.as_retriever()
            # local_retriever.get_relevant_documents("What is the capital of India?",k=10)
            bm_retriever = BM25Retriever.from_texts(db.get())
            # bm_retriever.update_do
            # print(bm_retriever)
            ensemble_retriever = EnsembleRetriever(retrievers=[bm_retriever, local_retriver],weights=[0.5, 0.5])

            chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=ensemble_retriever,
                chain_type="stuff",
                chain_type_kwargs={
                    "prompt": prompt, 
                    "memory": memory
                    },
                # return_source_documents=True,
            )

    # Main loop
    print(Fore.LIGHTYELLOW_EX + "Running... type '/exit' to quit")
    print(Fore.LIGHTYELLOW_EX + "Warning: The stats are based on OpenAI's pricing model and doesn't cost you anything. The stats are for demonstration purposes only.")

    if persona != "default":

        print(Fore.LIGHTYELLOW_EX + "Note: You are using a persona. The persona is used to customize the chatbot i.e. how the chatbot should behave. It depends on the document you ingest into the DB. You can change the persona by using the --persona flag. The default persona is 'default'.")
        print("Persona:", Fore.LIGHTYELLOW_EX + persona.upper())

    while True:
        query = input(Fore.LIGHTCYAN_EX +"\nEnter your query 🙋‍♂️: ")
        if(query == "/exit"):
            LOGGING.info("Byee 👋.")
            break
        chain(query)
        

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
    parser.add_argument(
        "--retriever",
        choices=["local", "web","hybrid"],
        default="local",
        help="Specify the retriever (local, web, hybrid)",
    )
    parser.add_argument(
        "--persona",
        choices=["default", "recruiter", "academician", "friend", "ml_engineer", "interviewer", "ceo", "researcher"],
        default="default",
        help="Specify the persona (default, recruiter, etc). It allows you to customize the persona i.e. how the chatbot should behave.",
    )
    parser.add_argument(
        "--build",
        default=False,
        action="store_true",
        help="Run the builder",
    )

    args = parser.parse_args()
    if args.build:
        builder(vectorstore=args.db)

    db_retriver(device_type=args.device_type,vectordb=args.db,retriever=args.retriever,persona=args.persona, LOGGING=logging)
    
