import logging
import re

from langchain.chains import LLMChain
from rich.console import Console
from rich.prompt import Prompt

from neogpt.load_llm import load_model
from neogpt.prompts.prompt import conversation_prompt
from neogpt.utils import get_username, magic_commands, read_file

try:
    import readline
except:
    pass
from neogpt.settings.config import (
    DEVICE_TYPE,
    MODEL_FILE,
    MODEL_NAME,
    MODEL_TYPE,
    QUERY_COST,
    TOTAL_COST,
    WORKSPACE_DIRECTORY,
)

# Create a global console instance
console = Console()


# Define a shorthand for console.print using a lambda function
def cprint(*args, **kwargs):
    return console.print(*args, **kwargs)


def chat_mode(
    device_type: str = DEVICE_TYPE,
    model_type: str = MODEL_TYPE,
    persona: str = "default",
    show_source: bool = False,
    write: str | None = None,
    LOGGING=logging,
):
    # Load the LLM model
    llm = load_model(
        device_type,
        model_type,
        model_id=MODEL_NAME,
        model_basename=MODEL_FILE,
        LOGGING=logging,
    )

    prompt, memory = conversation_prompt()
    conversation = LLMChain(prompt=prompt, llm=llm, verbose=False, memory=memory)

    # Main loop
    LOGGING.info(
        "Note: The stats are based on OpenAI's pricing model. The cost is calculated based on the number of tokens generated. You don't have to pay anything to use the chatbot. The cost is only for reference."
    )

    cprint("\nNeoGPT 🤖 is ready to chat. Type '/exit' to exit.")

    if persona != "default":
        cprint(f"NeoGPT 🤖 is in {persona} mode.")

    while True:
        query = Prompt.ask(f"[bold cyan]\n{get_username()} 🙎‍♂️ [/bold cyan]")
        try:
            readline.add_history(query)
        except:
            pass

        if query.startswith("/"):
            result = magic_commands(query, conversation)
            if result is False:
                break
            elif isinstance(result, str):
                query = result
            else:
                continue

        regex = re.compile(r"([^']+)")
        if regex.search(query):
            query = read_file(query, conversation)

        res = conversation.invoke({"question": query})

        if show_source:
            answer, docs = res["result"], res["source_documents"]
            cprint("Question: [green]" + query + "[/green]")
            cprint("Answer: [green]" + answer + "[/green]")
            cprint(
                "----------------------------------SOURCE DOCUMENTS---------------------------"
            )
            for document in docs:
                cprint(document)
            cprint(
                "----------------------------------SOURCE DOCUMENTS---------------------------"
            )
