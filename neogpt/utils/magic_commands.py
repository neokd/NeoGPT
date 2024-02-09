# Import necessary modules
import datetime
import os

import pyperclip
from langchain.schema import AIMessage, HumanMessage
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from rich.console import Console

from neogpt.utils.notify import notify
from neogpt.utils.user_info import get_username

from tiktoken import Tokenizer, TokenCount
from tiktoken.models import GPT2

# Create a Tokenizer and TokenCount object
tokenizer = Tokenizer()

# Create a console object for pretty printing
console = Console()


# Function to print to the console
def cprint(*args, **kwargs):
    """Prints to the console with rich formatting."""
    return console.print(*args, **kwargs)


# This file contains the magic commands that can be used during chat sessions.
def magic_commands(user_input, chain):
    """
    Function to handle magic commands during chat sessions.

    Parameters:
    user_input (str): The command input by the user.
    chain (Chain): The current chat session.

    Returns:
    bool: True if the command is recognized and executed, False otherwise.
    """
    # If the user inputs '/reset', reset the chat session
    if user_input == "/reset":
        cprint("Resetting the chat session...")
        # Print the current memory before resetting
        # print(chain.combine_documents_chain.memory)
        # Reset the chat memory
        chain.combine_documents_chain.memory.chat_memory = ChatMessageHistory(
            messages=[]
        )
        # Print the chat memory after resetting
        # print(chain.combine_documents_chain.memory.chat_memory)
        return True

    # If the user inputs '/exit', exit the chat session
    elif user_input == "/exit":
        cprint("\nNeoGPT 🤖 is shutting down. Bye 👋")
        return False

    # If the user inputs '/history', print the chat history
    elif user_input == "/history":
        cprint("\n[bold magenta]Chat history: 📖[/bold magenta]")
        if len(chain.combine_documents_chain.memory.chat_memory.messages) == 0:
            cprint(
                "No chat history available. Start chatting with NeoGPT to see the history."
            )
            return True

        for message in chain.combine_documents_chain.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                cprint(
                    f"   [bright_yellow]{get_username()} [/bright_yellow]{message.content}"
                )
            else:
                cprint(f"   [bright_blue]NeoGPT: [/bright_blue]{message.content}")

        return True
  
    # If the user input is '/export', export the config to the settings.yaml file
    elif user_input == "/export":
        cprint("Exporting the current chat memory to the settings/settings.yaml file...")
        from neogpt.config import export_config

        export_config()
        return True

    # If the command is not recognized, print an error message
    else:
        cprint("Invalid command. Please try again.")
        return  # Return False if the command is not recognized


# Uncomment the following lines to test the magic commands
# if __name__ == "__main__":
#     magic_commands("/exit")
