import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from langchain.chat_loaders.utils import map_ai_messages, merge_chat_runs
from langchain.schema import AIMessage
from langchain.schema.document import Document

from neogpt.config import SOCIAL_CHAT_EXTENSION

if TYPE_CHECKING:
    from langchain.chat_loaders.base import ChatSession


def process_chat(loader, file_path, type) -> Document:
    raw_msgs = loader.lazy_load()
    merged_msgs = merge_chat_runs(raw_msgs)
    messages: list[ChatSession] = list(
        map_ai_messages(merged_msgs, sender="Dr. Feather")
    )
    combined_messages = [
        f"AI: {message.content}"
        if isinstance(message, AIMessage)
        else f"Human: {message.content}"
        for message in messages[0]["messages"]
    ]
    return Document(
        page_content="\n".join(combined_messages),
        metadata={"source": file_path, "type": f"chat-{type}"},
    )


def load_single_chat(file_path: str) -> Document:
    """
    fn: load_single_chat
    Description: The function loads a single chat based on the determined chat type
    Args:
        file_path (str): File path
    return:
        Document: Document
    """
    file_name = os.path.basename(file_path).split(".")[0]
    for pattern, loader_class in SOCIAL_CHAT_EXTENSION.items():
        if re.match(pattern, file_name):
            if "whatsapp" in pattern:
                loader = loader_class(path=file_path)
                return process_chat(loader, file_path, "whatsapp")
            else:
                print("Chat type not supported: " + file_name)


def load_chat_batch(filepaths):
    """
    fn: load_chat_batch
    Description: The function loads a batch of chats based on the determined chat type
    Args:
        filepaths (list): List of file paths
    return:
        tuple: Tuple containing list of data from the chats and file paths
    """
    logging.info("Loading chat batch")
    # Create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # Load files
        futures = [exe.submit(load_single_chat, name) for name in filepaths]
        # Collect data
        data_list = [future.result() for future in futures]
        # Return data and file paths
        return (data_list, filepaths)
