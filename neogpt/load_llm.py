import logging
import os

from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from langchain.callbacks.manager import CallbackManager
from langchain_community.llms import LlamaCpp, Ollama
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, TextStreamer
from neogpt.callback_handler import (
    StreamingStdOutCallbackHandler,
    StreamlitStreamingHandler,
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
from rich.console import Console

load_dotenv()
try:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
except Exception as e:
    logging.info(e)

console = Console()

# Define a shorthand for console.print using a lambda function
def cprint(*args, **kwargs):
    return console.print(*args, **kwargs)

# Function to load the LLM
def load_model(
    device_type: str = DEVICE_TYPE,
    model_type: str = MODEL_TYPE,
    model_id: str = MODEL_NAME,
    model_basename: str = MODEL_FILE,
    callback_manager: list | None = None,
    show_stats: bool = False,
    LOGGING=logging,
):
    """
    Fn: load_model
    Description: The function loads the LLM model (LLamaCpp, GPTQ, HuggingFacePipeline)
    Args:
        device_type (str, optional): Device type (cpu, mps, cuda). Defaults to DEVICE_TYPE.
        model_type (str, optional): Model type (mistral, llama, ollama, hf, openai). Defaults to MODEL_TYPE.
        model_id (str, optional): Model ID. Defaults to MODEL_NAME.
        model_basename (str, optional): Model basename. Defaults to MODEL_FILE.
        callback_manager (list, optional): Callback manager. Defaults to None.
        LOGGING (logging, optional): Logging. Defaults to logging.
    return:
        llm (LlamaCpp): Returns a LlamaCpp object (language model)
        llm (Ollama): Returns a Ollama object (language model)
        llm (HuggingFacePipeline): Returns a HuggingFace Pipeline object (language model)
        llm (ChatOpenAI): Returns a OpenAI object (language model)
        llm (ChatOpenAI): Returns a model from LMStudio
    """
    callbacks = [StreamingStdOutCallbackHandler()]
    if show_stats:
        callbacks.append(TokenCallbackHandler())

    callback_manager = (
        CallbackManager(callback_manager)
        if callback_manager is not None
        else CallbackManager(callbacks)
    )

    if (model_type == "llamacpp") and (
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
                kwargs["n_gpu_layers"] = -1  # only for MPS devices
            if device_type.lower() == "cuda":
                kwargs["n_gpu_layers"] = N_GPU_LAYERS  # set this based on your GPU
            # Create a LlamaCpp object (language model)
            llm = LlamaCpp(**kwargs)
            cprint(
                f"\nUsing [bold magenta]LlamaCpp[/bold magenta] to load [bold magenta]{model_id}[/bold magenta]."
            )
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
            cprint(
                f"\nUsing [bold magenta]Ollama[/bold magenta] to load [bold magenta]{model_id}[/bold magenta]."
            )
            return llm  # Returns a Ollama object (language model)
        except Exception as e:
            LOGGING.warning(
                "Unable to load Ollama model. Read https://neokd.github.io/NeoGPT/models/ollama/ to set the enviornment variable and load again "
            )

    elif model_type == "hf":
        try:
            LOGGING.warning(
                "🚨 You are using an huggingface's transformers library to load the model. This is not recommended. Use quantized model for better performance"
            )
            kwargs = {
                # "temperature": 0,
                "max_length": MAX_TOKEN_LENGTH,
                "trust_remote_code": True,
            }
            tokenizer = AutoTokenizer.from_pretrained(
                model_id, cache_dir=MODEL_DIRECTORY
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                cache_dir=MODEL_DIRECTORY,
                trust_remote_code=True, 
            )
            streamer = TextStreamer(tokenizer, skip_prompt=True)

            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=device_type,
                streamer=streamer,
                **kwargs,
            )
            llm = HuggingFacePipeline(pipeline=pipe)
            cprint(
                f"\nUsing [bold magenta]HuggingFace[/bold magenta] to load [bold magenta]{model_id}[/bold magenta]."
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
                model=model_id,
                api_key=OPENAI_API_KEY,
                callback_manager=CallbackManager(
                    [StreamingStdOutCallbackHandler(), TokenCallbackHandler()]
                ),
                streaming=True,
            )
            cprint(
                f"\nUsing [bold magenta]OpenAi[/bold magenta] to load [bold magenta]{model_id}[/bold magenta]."
            )
            LOGGING.info("Loaded openai successfully")
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")

    elif model_type == "lmstudio":
        try:
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            llm = ChatOpenAI(
                model="local",
                base_url="http://localhost:1234/v1",
                streaming=True,
                callback_manager=callback_manager,
            )
            cprint(
                f"\nUsing [bold magenta]LM Studio[/bold magenta] to load [bold magenta]{model_id}[/bold magenta]."
            )
            LOGGING.info("Loaded {model_id} using LM studio successfully")
            return llm
        except Exception as e:
            LOGGING.info(f"Error {e}")

    else:
        LOGGING.warning("🚨 Please use a valid model type")
