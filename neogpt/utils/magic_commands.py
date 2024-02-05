# Import necessary modules
import datetime, pyperclip

from langchain.schema import HumanMessage
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from rich.console import Console

from neogpt.utils.user_info import get_username
from neogpt.utils.notify import notify
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
    user_input = user_input.strip().lower() # Convert the input to lowercase and remove leading/trailing spaces
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

    # If the user inputs '/save', save the chat history to a file
    elif user_input == "/save":
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.txt"
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
                cprint("🚫 Oops! The last message is from the user, not NeoGPT. Try again after NeoGPT's response. 😅")
                return 
        else:
            cprint("🚫 No chat history available. Start a conversation with NeoGPT first. 😊")
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
                cprint(f"🔁 Resending the last human input to the model: {last_message.content}")
                return last_message.content
            else:
                cprint("🚫 Oops! The last message is from NeoGPT, not the user. Try again after the user's response. 😅")
                return
        else:
            cprint("🚫 No chat history available. Start a conversation first.")
            return
        
    # If the user inputs '/help', print the list of available commands
    elif user_input == "/help":
        cprint("\n[bold magenta]📖 Available commands: [/bold magenta]")
        cprint("🔄 /reset - Reset the chat session")
        cprint("🚪 /exit - Exit the chat session")
        cprint("📜 /history - Print the chat history")
        cprint("💾 /save - Save the chat history to a file")
        cprint("📋 /copy - Copy the last response from NeoGPT to the clipboard")
        cprint("⏪ /undo - Remove the last response from the chat history")
        cprint("🔁 /redo - Resend the last human input to the model")
        return True

    # If the command is not recognized, print an error message
    else:
        cprint("Invalid command. Please try again.")
        return # Return False if the command is not recognized


# Uncomment the following lines to test the magic commands
# if __name__ == "__main__":
#     magic_commands("/exit")