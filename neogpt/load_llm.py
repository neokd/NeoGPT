from neogpt.config import (
    MODEL_DIRECTORY,
    DEVICE_TYPE,
    MODEL_NAME,
    MODEL_FILE,
    N_GPU_LAYERS,
    MAX_TOKEN_LENGTH,
)
from neogpt.callback_handler import StreamingStdOutCallbackHandler,TokenCallbackHandler,StreamlitStreamingHandler
from langchain.callbacks.manager import CallbackManager
from huggingface_hub import hf_hub_download
from langchain.llms import LlamaCpp, HuggingFacePipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig, pipeline, AutoModelForCausalLM, TextGenerationPipeline
import logging

# Function to load the LLM 
def load_model(device_type:str = DEVICE_TYPE, model_id:str = MODEL_NAME, model_basename:str = MODEL_FILE,ui:bool = False, LOGGING=logging):
    """
        Fn: load_model
        Description: The function loads the LLM model (LLamaCpp, GPTQ, HuggingFacePipeline)
        Args:
            device_type (str, optional): Device type (cpu, mps, cuda). Defaults to DEVICE_TYPE.
            model_id (str, optional): Model ID. Defaults to MODEL_NAME.
            model_basename (str, optional): Model basename. Defaults to MODEL_FILE.
            LOGGING (logging, optional): Logging. Defaults to logging.
        return: 
            llm (LlamaCpp): Returns a LlamaCpp object (language model)
            llm (GPTQ): Returns a GPTQ object (language model)
            llm (HuggingFacePipeline): Returns a HuggingFace Pipeline object (language model)
    """
    if model_basename is not None and ".gguf" in model_basename.lower() :
        if ui:
            callback_manager = CallbackManager([StreamlitStreamingHandler()])
        else:
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
