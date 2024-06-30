import json
import os
from datetime import datetime

from utils.cprint import cprint


def handle_exit_chat(neogpt):
    cprint("\nExiting chat...")
    exit()


def handle_history(neogpt):
    """
    A function to display the conversation history.
    """

    user_messages_exist = any(message["role"] == "user" for message in neogpt.messages)
    print(neogpt.messages)
    if not user_messages_exist:
        cprint("\nChat with NeoGPT to see the conversation history.")
        return

    cprint("\n Showing conversation history...\n")
    for message in neogpt.messages[1:]:
        cprint(f"{message['role']} > {message['content']}")


def handle_save_conversation(neogpt):
    """
    A function to save the conversation history to a JSON file.

    Args:
        neogpt (NeoGPT): The NeoGPT instance.
    """
    # Check if there are any user messages in the conversation history
    user_messages_exist = any(message["role"] == "user" for message in neogpt.messages)

    if not user_messages_exist:
        cprint("\nChat with NeoGPT to save the conversation.")
        return

    conversation_file = (
        datetime.now().strftime("%B_%d_%Y_%H-%M-%S")
        + neogpt.messages[0]["content"][:20]
        + ".json"
    )

    neogpt_dir = "neogpt"
    if os.path.exists(neogpt_dir):
        conversations_dir = os.path.join(neogpt_dir, "conversations")
        if not os.path.exists(conversations_dir):
            os.makedirs(conversations_dir)
        file_path = os.path.join(conversations_dir, conversation_file)
    else:
        conversations_dir = "conversations"
        if not os.path.exists(conversations_dir):
            os.makedirs(conversations_dir)
        file_path = os.path.join(conversations_dir, conversation_file)

    with open(file_path, "w") as f:
        json.dump(neogpt.messages[1:], f, indent=4)  # Exclude the system message

    cprint(f"\nConversation saved to {file_path}")


def reset_chat(neogpt):
    """
    A function to reset the chat conversation.

    Args:
        neogpt (NeoGPT): The NeoGPT instance.
    """
    neogpt.messages = []
    neogpt.messages.append(
        {
            "role": "system",
            "type": "message",
            "content": neogpt.default_system_message,
        }
    )
    cprint("\nChat session reset.")


def magic_commands(user_input, neogpt):
    """
    A function to handle magic commands in the chat.

    Args:
        user_input (str): The user input.
        neogpt (NeoGPT): The NeoGPT instance.

    Returns:
        action (function): The function to execute based on the magic command.
    """
    help_message = """
    \n
    Available Magic Commands:
    /reset - Reset the chat conversation.
    /bye - Exit the chat.
    /history - View the conversation history.
    /save - Save the conversation to a JSON file.
    /help, /? - Display this help message.
    """.strip()

    short_hand_aliases = {
        "/r": "/reset",
        "/q": "/exit",
        "/h": "/history",
        "/s": "/save",
        "/?": "/help",
    }

    if user_input in short_hand_aliases:
        user_input = short_hand_aliases[user_input]

    magic_command = {
        "/exit": handle_exit_chat,
        "/bye": handle_exit_chat,
        "/quit": handle_exit_chat,
        "/history": handle_history,
        "/save": handle_save_conversation,
        "/reset": reset_chat,
        "/help": lambda neogpt: cprint(help_message),
    }
    try:
        action = magic_command.get(user_input, neogpt)
    except TypeError:
        cprint("\nInvalid magic command. Type /help for a list of available commands.")
        return False
    return action(neogpt)
