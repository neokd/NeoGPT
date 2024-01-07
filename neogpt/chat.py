import logging
import os
import re
from datetime import datetime

from colorama import Fore
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from neogpt.agents import ML_Engineer, QA_Engineer
from neogpt.callback_handler import (
    AgentCallbackHandler,
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
from neogpt.prompts.prompt import conversation_prompt


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

        res = conversation.invoke({"question": query})
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
