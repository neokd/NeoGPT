"""
This class is in development and will fully be replacing manager.py in the future. And remove langchain as a dependency.
"""

import json
import os
import re
from datetime import datetime

from interface import terminal_chat
from llm.llm import LLM
from machine.machine import Machine
from playground import playground
from prompts.prompt import PROMPT
from respond import respond
from server import server
from utils import cprint


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
        vector_db="Chroma",
        conversation_history=False,
        conversation_file=None,
        conversation_history_path=None,
        custom_prompt="",
        persona=None,
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
        self.vector_db = "Chroma" if vector_db is None else vector_db
        self.conversation_history = conversation_history
        self.conversation_file = conversation_file
        self.conversation_history_path = conversation_history_path
        self.custom_prompt = custom_prompt
        self.persona = persona
        self.machine = Machine(self) if machine is None else machine

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

            if isinstance(message, str):
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

    def build(self):
        """
        This function is used to build the vector database.
        """
        pass

    def _engine(self):
        # TODO: This function is responsible for calling RAG and Smart Interpreter
        for chunk in respond(self):
            yield chunk
