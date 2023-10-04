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
from langchain.prompts import PromptTemplate
from huggingface_hub import hf_hub_download
from langchain.callbacks.base import BaseCallbackHandler
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
from typing import Any, Dict, Optional
import sys

class TokenCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self._tokens = []

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._tokens.append(token)


    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        cost_per_token = ((len(self._tokens) / 1000 ) * 0.002) * 83.33 # INR Cost per token
        total_tokens = len(self._tokens)
        print(f"\n\nTotal tokens generated: {total_tokens}")
        print(f"Total cost: {cost_per_token} INR")


def load_model(device_type:str = DEVICE_TYPE, model_id:str = MODEL_NAME, model_basename:str = MODEL_FILE, LOGGING=logging):
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler(),TokenCallbackHandler()])
    try:
        model_path = hf_hub_download(
            repo_id=model_id,
            filename=model_basename,
            resume_download=True,
            cache_dir=MODEL_DIRECTORY,
        )
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
            kwargs["n_gpu_layers"] = 1
        if device_type.lower() == "cuda":
            kwargs["n_gpu_layers"] = N_GPU_LAYERS  # set this based on your GPU
        llm =  LlamaCpp(**kwargs)
        LOGGING.info(f"Loaded {model_id} locally")
        return llm  # Returns a LlamaCpp object
    except Exception as e:
        LOGGING.info(f"Error {e}")

def db_retriver(device_type:str = DEVICE_TYPE, LOGGING=logging):
    embeddings = HuggingFaceInstructEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": DEVICE_TYPE},
        cache_folder=MODEL_DIRECTORY,
    )
    db = Chroma(
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings,
    )
    retriever = db.as_retriever()
    LOGGING.info(f"Loaded Chroma DB Successfully")
    llm = load_model(device_type, model_id=MODEL_NAME, model_basename=MODEL_FILE, LOGGING=logging)
    template = """
    [INST]
        Context: {summaries}
        User: {question}
    [/INST]
    """ 
    prompt = PromptTemplate(input_variables=["summaries", "question"], template=template)
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm=llm,
        retriever=retriever,
        # chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
    )

    chain({'question'  : "Write a random number generator guessing game in python",},return_only_outputs=True)


if __name__ == '__main__':
    
    db_retriver()

    