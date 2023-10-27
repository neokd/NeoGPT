import os
import time
from datetime import datetime
import logging
from colorama import Fore
from neogpt.load_llm import load_model
from neogpt.prompts.prompt import get_prompt
from neogpt.vectorstore.faiss import FAISSStore
from neogpt.vectorstore.chroma import ChromaStore
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.retrievers.web_research import WebResearchRetriever
from langchain.chains import RetrievalQA, HypotheticalDocumentEmbedder, LLMChain
from neogpt.config import (
    DEVICE_TYPE,
    MODEL_NAME,
    MODEL_FILE,
)

def db_retriver(device_type:str = DEVICE_TYPE,vectordb:str = "Chroma", retriever:str = "local",persona:str="default" ,show_source:bool="False",LOGGING=logging):
    """
        Fn: db_retriver
        Description: The function sets up the retrieval-based question-answering system.
        Args:
            device_type (str, optional): Device type (cpu, mps, cuda). Defaults to DEVICE_TYPE.
            vectordb (str, optional): Vectorstore (Chroma, FAISS). Defaults to "Chroma".
            retriever (str, optional): Retriever (local, web, hybrid). Defaults to "local".
            persona (str, optional): Persona (default, recruiter). Defaults to "default".
            LOGGING (logging, optional): Logging. Defaults to logging.
        return: 
            None
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
                return_source_documents=True,
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
                return_source_documents=True,
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
                return_source_documents=True,
            )

    # Main loop
    LOGGING.info("Note: The stats are based on OpenAI's pricing model. The cost is calculated based on the number of tokens generated. You don't have to pay anything to use the chatbot. The cost is only for reference.")

    
    print(Fore.LIGHTYELLOW_EX + "\nNeoGPT 🤖 is ready to chat. Type '/exit' to exit.")
    if persona != "default":
        print("NeoGPT 🤖 is in "+ Fore.LIGHTMAGENTA_EX + persona + Fore.LIGHTYELLOW_EX + " mode.")


    #  Main Loop with timer
    last_input_time = datetime.now()
    while True:
        time_difference = (datetime.now() - last_input_time).total_seconds()
        # Check if 3 minutes have passed since the last input
        if time_difference > 180:
            print("\n \nNo input received for 3 minutes. Exiting the program.")
            break

        query = input(Fore.LIGHTCYAN_EX +"\nEnter your query 🙋‍♂️: ")
        last_input_time = datetime.now()  # update the last_input_time to now

        if(query == "/exit"):
            LOGGING.info("Byee 👋.")
            break
        res = chain(query)
        answer, docs = res["result"], res["source_documents"]
        
        print("\n\n> Question:")
        print(query)
        print("\n> Answer:")
        print(answer)

        if show_source:
            print("----------------------------------SOURCE DOCUMENTS---------------------------")
            for document in docs:
                print("\n> " + document.metadata["source"] + ":")
                print(document.page_content)
            print("----------------------------------SOURCE DOCUMENTS---------------------------")