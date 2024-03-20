import logging
import os
import re
import sys
import warnings
from datetime import datetime

from langchain_core._api.deprecation import LangChainDeprecationWarning
from rich.console import Console
from rich.prompt import Prompt

from neogpt.agents import ML_Engineer, QA_Engineer
from neogpt.callback_handler import (
    AgentCallbackHandler,
    budget_manager,
    final_cost,
)
from neogpt.interpreter import interpreter
from neogpt.load_llm import load_model
from neogpt.retrievers import (
    context_compress,
    hybrid_retriever,
    local_retriever,
    sql_retriever,
    stepback,
    web_research,
)
from neogpt.settings.config import (
    DEVICE_TYPE,
    MODEL_FILE,
    MODEL_NAME,
    MODEL_TYPE,
    QUERY_COST,
    TOTAL_COST,
    WORKSPACE_DIRECTORY,
)
from neogpt.utils import (
    conversation_navigator,
    get_username,
    magic_commands,
    read_file,
    writing_assistant,
)
from neogpt.vectorstore import ChromaStore, FAISSStore

try:
    import readline
except ImportError:
    pass
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
    ui: bool = False,
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
        ui=ui,
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
def retrieval_chat(
    chain, show_source, max_budget, retriever, interpreter_mode, force_run, LOGGING
):
    global TOTAL_COST, QUERY_COST
    # Run the chat loop
    cprint(
        "\n[bright_yellow]NeoGPT 🤖 is ready to chat. Type /exit to quit.[/bright_yellow]"
    )
    # chain.invoke("Hello, introduce yourself to someone opening this program for the first time. Be concise.")
    while True:
        query = Prompt.ask(f"[bold cyan]\n{get_username()} 🙎‍♂️ [/bold cyan]")
        # print(chain.combine_documents_chain.memory.chat_memory)
        try:
            readline.add_history(query)
        except:
            pass
        # Matching for magic commands
        if query.startswith("/"):
            result = magic_commands(query, chain)
            if result is False:
                break
            elif isinstance(result, str):
                query = result
            else:
                continue

        regex = re.compile(r"([^']+)")
        if regex.search(query):
            query = read_file(query, chain)

        res = (
            chain.invoke({"question": query})
            if retriever == "stepback"
            else chain.invoke(query)
        )

        if interpreter_mode:
            interpreter(message=res["result"], chain=chain, force_run=force_run)

        # cprint(budget)
        if max_budget is not None and not budget_manager(max_budget):
            cprint(
                f"[bold bright_yellow]\nBudget Exceeded. The total cost for the conversation is {round(final_cost(),4)} INR and the maximum budget is {max_budget} INR. Exiting the conversation. [/bold bright_yellow]"
            )
            cprint("Bye! 👋")
            break

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
    interpreter_mode: bool = False,
    force_run: bool = False,
    load_conversation: bool = False,
    prompt: str | None = None,
    show_stats: bool = False,
    max_budget: int = 0,
    LOGGING=logging,
):
    """
    The manager function is the main function that runs NeoGPT.
    """
    # device_type, model_type, vectordb, retriever, persona, show_stats, LOGGING
    chain = db_retriever(
        device_type=device_type,
        model_type=model_type,
        vectordb=vectordb,
        retriever=retriever,
        persona=persona,
        ui=False,
        show_stats=show_stats,
        LOGGING=LOGGING,
    )

    if prompt:
        cprint(f"[bold cyan]\n{get_username()} 🙎‍♂️ [/bold cyan]", prompt)
        return chain.invoke(prompt)

    if load_conversation:
        history = conversation_navigator(chain)

    retrieval_chat(
        chain, show_source, max_budget, retriever, interpreter_mode, force_run, LOGGING
    )
