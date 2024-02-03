import logging
import os
import re
import warnings
from datetime import datetime

from langchain_core._api.deprecation import LangChainDeprecationWarning
from rich.console import Console
from rich.prompt import Prompt

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
    MODEL_TYPE,
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
from neogpt.utils import get_username, magic_commands, read_file, writing_assistant
from neogpt.vectorstore import ChromaStore, FAISSStore

# Create a console instance
console = Console()


# Define a shorthand for console.print using a lambda function
def cprint(*args, **kwargs):
    return console.print(*args, **kwargs)


def db_retriever(
    device_type: str = DEVICE_TYPE,
    model_type: str = MODEL_TYPE,
    vectordb: str = "Chroma",
    retriever: str = "local",
    persona: str = "default",
    show_stats: bool = False,
    LOGGING=logging,
):
    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

    match vectordb:
        case "Chroma":
            db = ChromaStore()
            LOGGING.info("Loaded Chroma DB Successfully")
        case "FAISS":
            db = FAISSStore() if retriever == "hybrid" else FAISSStore().load_local()
            LOGGING.info("Loaded FAISS DB Successfully")

    model_name = (
        os.getenv("MODEL_NAME") if os.getenv("MODEL_NAME") is not None else MODEL_NAME
    )

    llm = load_model(
        device_type=device_type,
        model_type=model_type,
        model_id=model_name,
        model_basename=MODEL_FILE,
        show_stats=show_stats,
        LOGGING=logging,
    )

    if persona != "default":
        cprint(
            "NeoGPT 🤖 is in [bold magenta]" + persona + "[/bold magenta] mode.",
        )

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

    return chain


# RAG Chat
def retrieval_chat(chain, show_source, retriever, LOGGING):
    # Run the chat loop
    cprint(
        "\n[bright_yellow]NeoGPT 🤖 is ready to chat. Type /exit to quit.[/bright_yellow]"
    )
    while True:
        query = Prompt.ask(f"[bold cyan]\n{get_username()} 🙎‍♂️ [/bold cyan]")
        # print(chain.combine_documents_chain.memory.chat_memory)

        # Matching for magic commands
        if query.startswith("/"):
            result = magic_commands(query, chain)
            if result is False:
                break
            else:
                continue

        regex = re.compile(r"([^']+)")
        if regex.search(query):
            query = read_file(query)

        res = (
            chain.invoke({"question": query})
            if retriever == "stepback"
            else chain.invoke(query)
        )

        if show_source:
            answer, docs = res["result"], res["source_documents"]
            separator_line = "-" * int(
                (console.width - len("SOURCE DOCUMENTS") - 5) / 2
            )
            cprint(f"{separator_line} SOURCE DOCUMENTS {separator_line}")
            for document in docs:
                cprint(document)
            cprint(f"{separator_line} SOURCE DOCUMENTS {separator_line}")


# Agent related chat
def hire(task: str = "", tries: int = 5, LOGGING=logging):
    global TOTAL_COST
    llm = load_model(
        device_type=DEVICE_TYPE,
        model_type=MODEL_TYPE,
        model_id=MODEL_NAME,
        model_basename=MODEL_FILE,
        callback_manager=[AgentCallbackHandler()],
        show_stats=False,
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


# TODO: Add shell mode
def shell_():
    cprint(
        "\n[bright_yellow]NeoGPT 🤖 is ready to chat. Type /exit to quit.[/bright_yellow]"
    )


def manager(
    device_type: str = DEVICE_TYPE,
    model_type: str = MODEL_TYPE,
    vectordb: str = "Chroma",
    retriever: str = "local",
    persona: str = "default",
    show_source: bool = False,
    write: str | None = None,
    shell: bool = False,
    show_stats: bool = False,
    LOGGING=logging,
):
    """
    The manager function is the main function that runs NeoGPT.
    """
    chain = db_retriever(
        device_type, model_type, vectordb, retriever, persona, show_stats, LOGGING
    )

    if shell:
        shell_()
    else:
        retrieval_chat(chain, show_source, retriever, LOGGING)
