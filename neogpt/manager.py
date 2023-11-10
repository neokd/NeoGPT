import logging
from datetime import datetime

from colorama import Fore

from neogpt.config import DEVICE_TYPE, MODEL_FILE, MODEL_NAME
from neogpt.load_llm import load_model
from neogpt.retrievers import (
    context_compress,
    hybrid_retriever,
    local_retriever,
    sql_retriever,
    stepback,
    web_research,
)
from neogpt.vectorstore import ChromaStore, FAISSStore


def db_retriver(
    device_type: str = DEVICE_TYPE,
    vectordb: str = "Chroma",
    retriever: str = "local",
    persona: str = "default",
    show_source: bool = False,
    LOGGING=logging,
):
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
            LOGGING.info("Loaded Chroma DB Successfully")
        case "FAISS":
            # Load the FAISS DB with the embedding model
            db = FAISSStore() if retriever == "hybrid" else FAISSStore().load_local()
            LOGGING.info("Loaded FAISS DB Successfully")
        # case "Pinecone":
        # Initialize Pinecone client
        # Load the Pinecone DB with the embedding model
        # pinecone_api_key = "your_api_key"
        # pinecone_environment = "your_environment_name"
        # db= Pinecone(api_key=pinecone_api_key, environment=pinecone_environment)
        # LOGGING.info(f"Initialized Pinecone DB Successfully")

    # Load the LLM model
    llm = load_model(
        device_type, model_id=MODEL_NAME, model_basename=MODEL_FILE, LOGGING=logging
    )

    # Prompt Builder Function
    match retriever:
        case "local":
            chain = local_retriever(db, llm, persona)
        case "web":
            chain = web_research(db, llm, persona)
        case "hybrid":
            chain = hybrid_retriever(db, llm, persona)
        case "stepback":
            chain = stepback(llm, db)
        case "compress":
            chain = context_compress(llm, db, persona)
        case "sql":
            chain = sql_retriever(llm, persona)

    # Main loop
    LOGGING.info(
        "Note: The stats are based on OpenAI's pricing model. The cost is calculated based on the number of tokens generated. You don't have to pay anything to use the chatbot. The cost is only for reference."
    )

    print(Fore.LIGHTYELLOW_EX + "\nNeoGPT 🤖 is ready to chat. Type '/exit' to exit.")
    if persona != "default":
        print(
            "NeoGPT 🤖 is in "
            + Fore.LIGHTMAGENTA_EX
            + persona
            + Fore.LIGHTYELLOW_EX
            + " mode."
        )

    #  Main Loop with timer
    last_input_time = datetime.now()
    while True:
        time_difference = (datetime.now() - last_input_time).total_seconds()
        # Check if 2 minute have passed since the last input
        if time_difference > 120:
            print("\n \nNo input received for 1 minute! Exiting the program.")
            break

        query = input(Fore.LIGHTCYAN_EX + "\nEnter your query 🙋‍♂️: ")

        if query == "/exit":
            LOGGING.info("Byee 👋.")
            break

        res = (
            chain.invoke({"question": query})
            if retriever == "stepback"
            else chain.invoke(query)
        )
        # res = chain.invoke({"question": query})

        if show_source:
            answer, docs = res["result"], res["source_documents"]
            print("Question: " + Fore.LIGHTGREEN_EX + query)
            print("Answer: " + Fore.LIGHTGREEN_EX + answer)
            print(
                "----------------------------------SOURCE DOCUMENTS---------------------------"
            )
            for document in docs:
                # print("\n> " + document.metadata["source"] + ":")
                print(document)
            print(
                "----------------------------------SOURCE DOCUMENTS---------------------------"
            )

        last_input_time = datetime.now()  # update the last_input_time to now
