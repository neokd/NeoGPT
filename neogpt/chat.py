import logging
import os
import re
from datetime import datetime

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from rich.console import Console

from neogpt.agents import ML_Engineer, QA_Engineer
from neogpt.callback_handler import AgentCallbackHandler, final_cost
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
from neogpt.prompts.prompt import conversation_prompt

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

    if persona == "shell":
        cprint(
            "\nYou are using NeoGPT 🤖 as a shell. It may generate commands that can be harmful to your system. Use it at your own risk. ⚠️"
        )
        execute = input("Do you want to execute the commands? (Y/N): ").upper()
        if execute == "Y":
            cprint("NeoGPT 🤖 will execute the commands in your default shell.")
        else:
            cprint("You can copy the commands and execute them manually.")

    # Main Loop with timer
    last_input_time = datetime.now()
    while True:
        time_difference = (datetime.now() - last_input_time).total_seconds()
        # Check if 1.5 minute have passed since the last input
        if time_difference > 90:
            cprint("\n \nNo input received for 1.5 minute! Exiting the program.")
            break

        query = input("\nEnter your query 🙋‍♂️: ")

        if query == "/exit":
            cprint(f"Total chat session cost: {final_cost()} INR")
            LOGGING.info("Byee 👋.")
            break

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

            cprint(
                "\n[lightyellow]Your work is written to {WORKSPACE_DIRECTORY}/{write}[/reset]"
            )

            break

        if persona == "shell" and execute == "Y":
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            command = re.sub(r"```bash|```", "", res["result"])
            os.system(command)

        last_input_time = datetime.now()  # update the last_input_time to now
