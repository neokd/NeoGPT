# Import necessary modules
import datetime
import os

import pyperclip
import tiktoken
from langchain.schema import AIMessage, HumanMessage
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from rich.console import Console

from neogpt.utils import conversation_navigator
from neogpt.utils.notify import notify
from neogpt.utils.user_info import get_username

from neogpt.settings.config import SOURCE_DIR
# Create a Tokenizer and TokenCount object
tokenizer = tiktoken.get_encoding("cl100k_base")

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
    tokenizer = tiktoken.get_encoding("cl100k_base")
    # cprint(chain)
    # If the user inputs '/reset', reset the chat session
    if user_input == "/source":
        cprint(f"Source directory: {SOURCE_DIR}")
        return True
    
    elif user_input == "/reset":
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
        # print(chain.combine_documents_chain.memory.chat_memory.messages)
        for message in chain.combine_documents_chain.memory.chat_memory.messages:
            if isinstance(message, HumanMessage):
                cprint(
                    f"[bright_yellow]{get_username()} [/bright_yellow]{message.content}"
                )
            else:
                cprint(f"[bright_blue]NeoGPT: [/bright_blue]{message.content}")

        return True

    # If the user inputs '/save', save the chat history to a file
    elif user_input == "/save":
        # Create the directory if it doesn't exist
        directory = "neogpt/conversations"
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{directory}/chat_history_{timestamp}.txt"  # Save the file in the 'conversations' directory
        with open(filename, "w") as f:
            for message in chain.combine_documents_chain.memory.chat_memory.messages:
                if isinstance(message, HumanMessage):
                    f.write(f"{get_username()} {message.content}\n")
                else:
                    f.write(f"NeoGPT: {message.content}\n")
        cprint(f"Chat history saved as {filename}")
        return True

    # If the user inputs '/copy', copy the last response from NeoGPT to the clipboard
    elif user_input == "/copy":
        if len(chain.combine_documents_chain.memory.chat_memory.messages) > 0:
            last_message = chain.combine_documents_chain.memory.chat_memory.messages[-1]
            if not isinstance(last_message, HumanMessage):
                pyperclip.copy(last_message.content)
                notify("NeoGPT", "Copied to clipboard!")
                return True
            else:
                cprint(
                    "🚫 Oops! The last message is from the user, not  Try again after NeoGPT's response. 😅"
                )
                return
        else:
            cprint(
                "🚫 No chat history available. Start a conversation with NeoGPT first. 😊"
            )
            return

    # If the user inputs '/undo', remove the last response from the chat history
    elif user_input == "/undo":
        if len(chain.combine_documents_chain.memory.chat_memory.messages) > 0:
            chain.combine_documents_chain.memory.chat_memory.messages.pop()
            cprint("🔄 Last response from the chat history has been removed.")
            return True
        else:
            cprint("🚫 No chat history available. Start a conversation first.")
            return

    # If the user inputs '/redo', resend the last human input to the model
    elif user_input == "/redo":
        if len(chain.combine_documents_chain.memory.chat_memory.messages) > 0:
            last_message = chain.combine_documents_chain.memory.chat_memory.messages[-2]
            if isinstance(last_message, HumanMessage):
                cprint(
                    f"🔁 Resending the last human input to the model: {last_message.content}"
                )
                return last_message.content
            else:
                cprint(
                    "🚫 Oops! The last message is from NeoGPT, not the user. Try again after the user's response. 😅"
                )
                return
        else:
            cprint("🚫 No chat history available. Start a conversation first.")
            return

    # If the user inputs '/load [path]', load the saved chat history from the specified file
    elif user_input.startswith("/load"):
        # Extract the file path from the command]
        if len(user_input.split(" ")) < 2:
            conversation_navigator(chain)
            return True

        file_path = user_input.split(" ")[1].strip().replace("'", "").replace('"', "")

        try:
            with open(file_path) as f:
                # Read the contents of the file
                contents = f.readlines()
                # Create a list to store the loaded chat history
                loaded_chat_history = []
                for line in contents:
                    # Split the line into username and message content
                    if line.startswith("NeoGPT:"):
                        loaded_chat_history.append(
                            AIMessage(content=line.replace("NeoGPT:", "").strip())
                        )
                    else:
                        loaded_chat_history.append(
                            HumanMessage(
                                content=line.replace(get_username(), "").strip()
                            )
                        )

                # Update the chat memory with the loaded chat history
                chain.combine_documents_chain.memory.chat_memory.messages += (
                    loaded_chat_history
                )
                cprint("Chat history loaded successfully. 🎉")
                return True
        except FileNotFoundError:
            cprint("🚫 File not found. Please provide a valid file path. 😞")
            return True
        except Exception as e:
            cprint(f"🚫 Error loading chat history: {e!s} 😢")
            return True

    # If the user inputs '/tokens [prompt]', calculate the number of tokens for the given prompt
    elif user_input.startswith("/tokens"):
        # Extract the prompt from the command
        prompt = user_input.split(" ", 1)[1].strip().replace("'", "").replace('"', "")
        # Calculate the number of tokens in the prompt
        tokens = list(tokenizer.encode(prompt))
        num_tokens = len(tokens)
        # Print the number of tokens to the console
        cprint(f"The prompt contains {num_tokens} tokens.")
        return True

    # If the user inputs '/export', export the current chat memory to the settings/settings.yaml file
    elif user_input == "/export":
        cprint(
            "Exporting the current chat memory to the settings/settings.yaml file..."
        )
        from neogpt.settings.export_config import export_config

        export_config()
        return True

    elif user_input == "/conversations":
        cprint("📜 Available conversations:")
        conversation_navigator(chain)
        return True

    # If the user inputs '/help', print the list of available commands
    elif user_input == "/help" or user_input == "/":
        cprint("\n[bold magenta]📖 Available commands: [/bold magenta]")
        cprint("🔄 /reset - Reset the chat session")
        cprint("🚪 /exit - Exit the chat session")
        cprint("📜 /history - Print the chat history")
        cprint("💾 /save - Save the chat history to a `neogpt/conversations`")
        cprint("📋 /copy - Copy the last response from NeoGPT to the clipboard")
        cprint("⏪ /undo - Remove the last response from the chat history")
        cprint("🔁 /redo - Resend the last human input to the model")
        cprint("📂 /load [path] - Load the saved chat history from the specified file")
        cprint(
            "🔖 /tokens [prompt] - Calculate the number of tokens for a given prompt"
        )
        cprint(
            "📄 /export - Export the current chat memory to the settings/settings.yaml file"
        )
        cprint("📜 /conversations - List available previously saved conversations.")
        cprint("📚 /source - Prints the source directory")

        return True

    # If the command is not recognized, print an error message
    else:
        cprint("Invalid magic command. Please try again.")
        return  # Return False if the command is not recognized


# Uncomment the following lines to test the magic commands
# if __name__ == "__main__":
#     magic_commands("/exit")
