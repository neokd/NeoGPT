from neogpt.config import (
    DEVICE_TYPE,
    MODEL_NAME,
    MODEL_FILE,
)

import logging
from langchain.chains import RetrievalQA
from neogpt.vectorstore.chroma import ChromaStore
from neogpt.vectorstore.faiss import FAISSStore
from neogpt.load_llm import load_model
from neogpt.prompts.prompt import get_prompt
import os
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from colorama import Fore


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
    LOGGING.info("Note: The stats are based on OpenAI's pricing model. The cost is calculated based on the number of tokens generated. You don't have to pay anything to use the chatbot. The cost is only for reference.")

    
    print(Fore.LIGHTYELLOW_EX + "\nNeoGPT 🤖 is ready to chat. Type '/exit' to exit.")
    if persona != "default":
        print("NeoGPT 🤖 is in "+ Fore.LIGHTMAGENTA_EX + persona + Fore.LIGHTYELLOW_EX + " mode.")

    while True:
        query = input(Fore.LIGHTCYAN_EX +"\nEnter your query 🙋‍♂️: ")
        if(query == "/exit"):
            LOGGING.info("Byee 👋.")
            break
        chain(query)
   