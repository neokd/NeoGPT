"""
This class is in development and will fully be replacing manager.py in the future. And remove langchain as a dependency.
"""

import json
import os
from datetime import datetime

from interface import terminal_chat
from llm.llm import LLM
from loaders.dirloader import DirectoryLoader
from machine.machine import Machine
from playground import playground
from prompts.prompt import PROMPT
from respond import respond
from rich.rule import Rule
from server import server
from settings import Settings
from utils.cprint import cprint
from vectorstore.neostore import NeoStore


class NeoGPT:
    def __init__(
        self,
        messages=None,
        offline=False,
        verbose=False,
        debug=False,
        max_output=2046,
        is_ui=False,
        llm=None,
        machine=None,
        default_system_message=PROMPT["DEFAULT"],
        vector_db=None,
        conversation_history=False,
        conversation_file=None,
        conversation_history_path=None,
        custom_prompt="",
        persona=None,
        data_dir=None,
        show_source_document=False,
    ) -> None:
        """
        The NeoGPT class is the main class for the NeoGPT Project. It is used to interact with the model and build the vector database.
        """
        self.messages = [] if messages is None else messages
        self.offline = offline
        self.verbose = verbose
        self.debug = debug
        self.max_output = max_output
        self.is_ui = is_ui
        self.llm = LLM(self) if llm is None else llm
        self.default_system_message = default_system_message
        self.vector_db = NeoStore() if vector_db is None else vector_db
        self.conversation_history = conversation_history
        self.conversation_file = conversation_file
        self.conversation_history_path = conversation_history_path
        self.custom_prompt = custom_prompt
        self.persona = persona
        self.machine = Machine(self) if machine is None else machine
        self.data_dir = Settings.DATA_DIR if data_dir is None else data_dir
        self.show_source_document = show_source_document

    def chat(self, prompt=None, display=True, stream=False):
        """
        This function is used to interact with the model. It takes a prompt as input and returns the response from the model.
        """
        if len(self.messages) == 0:
            self.messages.append(
                {
                    "role": "system",
                    "type": "message",
                    "content": self.default_system_message,
                }
            )

        if stream:
            return self._stream_response(prompt, display)

        # if streaming is disabled, return the response
        for _ in self._stream_response(prompt, display):
            pass

        return self.messages[-1]["content"]

    def _stream_response(self, message=None, display=False):
        """
        This function is used to stream the response from the model.
        """
        if display:
            yield from terminal_chat(self, message)
            return

        if message or message == "":
            if message == "":
                message = " Ask user to provide input."

            if isinstance(message, str) and not self.llm.support_vision:
                self.messages.append(
                    {"role": "user", "type": "message", "content": message}
                )
            elif isinstance(message, dict):
                if "role" not in message:
                    message["role"] = "user"
                self.messages.append(message)
            elif isinstance(message, list):
                self.messages = message

            yield from self._engine()

            if self.conversation_history:
                if not self.conversation_file:
                    self.conversation_file = (
                        datetime.now().strftime("%B_%d_%Y_%H-%M-%S")
                        + self.messages[0]["content"][:20]
                        + ".json"
                    )

                if not os.path.exists("conversations"):
                    os.makedirs("conversations")

                with open(f"conversations/{self.conversation_file}", "w") as f:
                    json.dump(self.messages, f, indent=4)

        else:
            print("Please provide a message to continue.")
        return

    def server(self, *args, **kwargs):
        """
        This function is used to start a FastAPI server.
        """
        server(self, *args, **kwargs)

    def playground(self, *args, **kwargs):
        """
        This function is used to start the playground.
        """
        playground(self, *args, **kwargs)

    def build(self, data_dir: str = Settings.DATA_DIR):
        """
        This function is used to build the vector database.
        """
        if isinstance(self.vector_db, NeoStore):
            docs = DirectoryLoader(path=data_dir).load_in_chunks()
            self.vector_db.build_store(docs=docs, persist=True)
            cprint("Vector Database built successfully.")
            return self.vector_db

    def _engine(self):
        # Load embeddings if not already loaded
        if (
            isinstance(self.vector_db, NeoStore)
            and self.vector_db._NeoStore__vectorstore is None
        ):
            embeddings_path = os.path.join(Settings.VECTOR_STORE_DIR, "neostore.npz")
            self.vector_db = self.vector_db.load_embeddings(embeddings_path)
            # print(f"Embeddings loaded: {self.vector_db}")

        if isinstance(self.vector_db, NeoStore):
            query = self.messages[-1]["content"]
            relevant_docs = self.vector_db.search(query)  # Adjust k as needed

            if relevant_docs:
                if self.show_source_document:
                    for content, metadata in relevant_docs:
                        cprint(f"Content: {content}, Metadata: {metadata}")
                        cprint(Rule())
                augmented_prompt = f"""
                Question: {query}
                Context: {"\n\n".join([content for content, metadata in relevant_docs])}
                Answer:"
                """

                # print(f"Augmented Prompt: {augmented_prompt}")  # Debug print
                self.messages[-1] = {
                    "role": "user",
                    "type": "message",
                    "content": augmented_prompt,
                }

            else:
                print(f"No relevant documents found for query: {query}")  # Debug print
                self.messages.append(
                    {
                        "role": "assistant",
                        "type": "message",
                        "content": "Sorry, I couldn't find any relevant information.",
                    }
                )

        yield from respond(self)
