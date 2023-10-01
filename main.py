import logging
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA, RetrievalQAWithSourcesChain
from langchain.llms import LlamaCpp
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from huggingface_hub import hf_hub_download

from config import (
    PERSIST_DIRECTORY,
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

def load_model(device_type:str = DEVICE_TYPE, model_id:str = MODEL_NAME, model_basename:str = MODEL_FILE, LOGGING=logging):
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
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
        persist_directory=PERSIST_DIRECTORY,
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

    chain({'question'  : "What is the linux command to list files in direcotyu",},return_only_outputs=True)


if __name__ == '__main__':
    db_retriver()

    