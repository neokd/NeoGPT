import logging
import os

from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from langchain.callbacks.manager import CallbackManager
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline, LlamaCpp, Ollama

from neogpt.callback_handler import (
    StreamingStdOutCallbackHandler,
    StreamlitStreamingHandler,
    StreamOpenAICallbackHandler,
    TokenCallbackHandler,
)
from neogpt.config import (
    DEVICE_TYPE,
    MAX_TOKEN_LENGTH,
    MODEL_DIRECTORY,
    MODEL_FILE,
    MODEL_NAME,
    MODEL_TYPE,
    N_GPU_LAYERS,
)

load_dotenv()
try:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
except Exception as e:
    logging.info(e)


# Function to load the LLM
def load_model(
    device_type: str = DEVICE_TYPE,
    model_type: str = MODEL_TYPE,
    model_id: str = MODEL_NAME,
    model_basename: str = MODEL_FILE,
    callback_manager: list = None,
    LOGGING=logging,
):
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
        llm (Ollama): Returns a Ollama object (language model)
        llm (HuggingFacePipeline): Returns a HuggingFace Pipeline object (language model)
    """

    callbacks = [StreamingStdOutCallbackHandler(), TokenCallbackHandler()]
    callback_manager = (
        CallbackManager(callback_manager)
        if callback_manager is not None
        else CallbackManager(callbacks)
    )

    if (model_type == "mistral" or model_type == "llama") and (
        model_basename is not None and ".gguf" in model_basename.lower()
    ):
        try:
            LOGGING.info("Using LlamaCpp to load the model")
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
                "verbose": False,
                "f16_kv": True,
                "streaming": True,
            }
            if device_type.lower() == "mps":
                kwargs["n_gpu_layers"] = 1  # only for MPS devices
            if device_type.lower() == "cuda":
                kwargs["n_gpu_layers"] = N_GPU_LAYERS  # set this based on your GPU
            # Create a LlamaCpp object (language model)
            llm = LlamaCpp(**kwargs)
            LOGGING.info(f"Loaded {model_id} locally")
            return llm  # Returns a LlamaCpp object (language model)
        except Exception as e:
            LOGGING.info(f"Error {e}")

    elif model_type == "ollama":
        try:
            LOGGING.info("Using Ollama to load the model")
            llm = Ollama(
                base_url="http://localhost:11434",
                model=model_id,
                callback_manager=callback_manager,
            )
            LOGGING.info(f"Loaded {model_id} locally. ")
            return llm  # Returns a Ollama object (language model)
        except Exception as e:
            LOGGING.warning(
                "Unable to load Ollama model. Read https://neokd.github.io/NeoGPT/models/ollama/ to set the enviornment variable and load again "
            )

    elif model_type == "hf":
        try:
            LOGGING.warning(
                "🚨 You are using an large model. Please use a quantized model for better performance"
            )
            kwargs = {
                # "temperature": 0,
                "max_length": MAX_TOKEN_LENGTH,
                "cache_dir": MODEL_DIRECTORY,
                "trust_remote_code": True,
            }
            llm = HuggingFacePipeline.from_model_id(
                model_id=MODEL_NAME,
                task="text-generation",
                device=N_GPU_LAYERS if device_type.lower() == "cuda" else -1,
                model_kwargs=kwargs,
                callback_manager=callback_manager,
            )
            LOGGING.info(f"Loaded {model_id} successfully")
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")
    elif model_type == "openai":
        try:
            LOGGING.warning("🚨 You are using openai")
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                callback_manager=CallbackManager(
                    [StreamOpenAICallbackHandler(), TokenCallbackHandler()]
                ),
                streaming=True,
            )
            LOGGING.info("Loaded openai successfully")
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")
    else:
        LOGGING.warning("🚨 Please use a valid model type")
