import logging
import os
import re
from datetime import datetime

from colorama import Fore

from neogpt.agents import ML_Engineer, QA_Engineer
from neogpt.callback_handler import (
    AgentCallbackHandler,
    StreamingStdOutCallbackHandler,
    TokenCallbackHandler,
    final_cost,
)
from neogpt.config import (
    DEVICE_TYPE,
    MODEL_FILE,
    MODEL_NAME,
    QUERY_COST,
    TOTAL_COST,
    WORKSPACE_DIRECTORY,
)
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
    model_type: str = "mistral",
    vectordb: str = "Chroma",
    retriever: str = "local",
    persona: str = "default",
    show_source: bool = False,
    write: str | None = None,
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
            # logging.warn("Chroma DB is temporarily disabled. Please use FAISS DB.")
            # exit()
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
        device_type,
        model_type,
        model_id=MODEL_NAME,
        model_basename=MODEL_FILE,
        LOGGING=logging,
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
    # print(Fore.LIGHTYELLOW_EX + "Read the docs at "+ Fore.WHITE + "https://neokd.github.io/NeoGPT/")
    if persona != "default":
        print(
            "NeoGPT 🤖 is in "
            + Fore.LIGHTMAGENTA_EX
            + persona
            + Fore.LIGHTYELLOW_EX
            + " mode."
        )

    if persona == "shell":
        print(
            Fore.LIGHTYELLOW_EX
            + "\nYou are using NeoGPT 🤖 as a shell. It may generate commands that can be harmful to your system. Use it at your own risk. ⚠️"
            + Fore.RESET
        )
        execute = input(
            Fore.LIGHTCYAN_EX + "Do you want to execute the commands? (Y/N): "
        ).upper()
        if execute == "Y":
            print(
                Fore.LIGHTYELLOW_EX
                + "NeoGPT 🤖 will execute the commands in your default shell."
                + Fore.RESET
            )
        else:
            print(
                Fore.LIGHTYELLOW_EX
                + "You can copy the commands and execute them manually."
                + Fore.RESET
            )

    #  Main Loop with timer
    last_input_time = datetime.now()
    while True:
        time_difference = (datetime.now() - last_input_time).total_seconds()
        # Check if 1.5 minute have passed since the last input
        if time_difference > 90:
            print("\n \nNo input received for 1.5 minute! Exiting the program.")
            break

        query = input(Fore.LIGHTCYAN_EX + "\nEnter your query 🙋‍♂️: ")

        if query == "/exit":
            print(f"Total chat session cost: {final_cost()} INR")
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
        # Writing the results to a file if write is specified. It can be used to write assignments, reports etc.
        if write is not None:
            if not os.path.exists(WORKSPACE_DIRECTORY):
                os.makedirs(WORKSPACE_DIRECTORY)

            base_filename = write
            file_counter = 1

            while os.path.exists(os.path.join(WORKSPACE_DIRECTORY, write)):
                # If the file already exists, append a counter to the filename
                write, extension = os.path.splitext(base_filename)
                write = f"{write}_{file_counter}{extension}"
                file_counter += 1

            answer = res["result"]

            with open(os.path.join(WORKSPACE_DIRECTORY, write), "w") as result:
                result.writelines(answer)

            print(
                "\n"
                + Fore.LIGHTYELLOW_EX
                + f"Your work is written to {WORKSPACE_DIRECTORY}/{write}"
                + Fore.RESET
            )

            break

        if persona == "shell" and execute == "Y":
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            command = re.sub(r"```bash|```", "", res["result"])
            os.system(command)

        last_input_time = datetime.now()  # update the last_input_time to now


def hire(task: str = "", tries: int = 5, LOGGING=logging):
    global TOTAL_COST
    llm = load_model(
        device_type=DEVICE_TYPE,
        model_type="mistral",
        model_id=MODEL_NAME,
        model_basename=MODEL_FILE,
        callback_manager=[AgentCallbackHandler()],
        LOGGING=LOGGING,
    )
    start = datetime.now()
    ml_agent = ML_Engineer(llm)
    qa_agent = QA_Engineer(llm)

    for i in range(tries):
        # print(TOTAL_COST)
        ml_results = ml_agent.think(task)
        if qa_agent.analyse(ml_results):
            print("\nQA Engineer approved the code. Program terminated.")
            break

        print(f"\nRemaining attempts: {tries - i}. Trying again...\n")

    else:
        print("\nOut of attempts. Program terminated.")

    end = datetime.now()
    print(f"Time taken: {round(((end - start).total_seconds() / 60),4)} minutes")
    print(f"The total cost of the project is {round(final_cost(),4)} INR")
