"""
This class is in development and will fully be replacing manager.py in the future. And remove langchain as a dependency.
"""

import os
import json
from datetime import datetime
from lm.llm import LLM
from respond import respond

default_system_message = """
 NeoGPT ,You are a helpful assistant, you will use the provided context to answer user questions.Read the given context before answering questions and think step by step. If you can not answer a user question based on the provided context, inform the user. Do not use any other information for answering user. Initialize the conversation with a greeting if no context is provided. Do not generate empty responses. When a user refers to a filename, they're likely referring to an existing file in the directory you're currently executing code in.For images speak what you see in the image and don't generate any other information.You are capable to answer any task.

"""


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
        default_system_message=default_system_message,
        vector_db="Chroma",
        conversation_history=True,
        conversation_file=None,
        conversation_history_path=None,
        custom_prompt="",
        persona=None,
    ) -> None:
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

    def chat(self, prompt=None, display=True, stream=True):
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

    def _stream_response(self, message=None, display=True):
        """
        This function is used to stream the response from the model.
        """

        if message or message == "":
            if message == "":
                message = " Ask user to provide input. "

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

            response = respond(self)

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

            # msg = ""
            # # for chunk in response:
            # #     if chunk.choices[0].delta.content is not None:
            # #         msg += chunk.choices[0].delta.content
            # self.messages.append(
            #     {"role": "assistant", "type": "message", "content": msg}
            # )
            # #     print(chunk.choices[0].delta.content)
            return response
        else:
            print("Please provide a message to continue.")


    def _engine(self):
        # TODO: This function is responsible for calling RAG and Interpreter 
        pass


if __name__ == "__main__":
    neogpt = NeoGPT()
    neogpt.persona = """
      NeoGPT,I want you to act as a machine learning engineer. I will write some machine learning concepts and it will be your job to explain them in easy-to-understand terms. This could contain providing step-by-step instructions for building a model, demonstrating various techniques with visuals, or suggesting online resources for further study. start with a greeting if no context is provided.
    """
    # neogpt.llm.api_key = "x"
    neogpt.llm.api_url = "http://localhost:11434/v1"
    neogpt.llm.model = "llama3"
    while True:
        x = input("\n\nEnter your message: ")
        for chunk in neogpt.chat(x):
            print(chunk, end="", flush=True)
