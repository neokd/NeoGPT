"""
This module contains the LLM class which is the main class for the LLM model. We'll be following openai message format for interaction with the model.
"""

from openai import OpenAI


class LLM:
    def __init__(self, neogpt) -> None:
        self.neogpt = neogpt
        # Model Name
        self.model = ""
        # Model Type
        self.support_vision = False

        # Settings for the model
        self.temperature = 0
        self.max_tokens = None
        self.context_window = None
        self.api_key = None
        self.api_url = None

        # Set Budget for Paid API
        self.max_budget = None

        # Set the persona
        self.persona = None

        # Avoid Repatition of loading LlamaCpp Model
        self.llama_cpp_model = None

    def inference(self, messages):
        """
        This function is used to interact with the model. It takes a prompt as input and returns the response from the model.
        Format:
        messages = [
         {
                "role": "system",
                "content": "I'm fine, thank you.",
            },
            {
                "role": "user",
                "content": "Hello, how are you?",
            }
        ]
        """
        assert (
            messages[0]["role"] == "system"
        ), "The first message should be from the system."
        for message in messages[1:]:
            assert (
                message["role"] != "system"
            ), "The subsequent messages should be from the user."

        if self.support_vision:
            image_message = [
                message for message in messages if message["type"] == "image"
            ]
            print(image_message)
            # TODO: Add support for image processing here
        # else:
        #     # Handle text messages
        #     message = messages[1:]
        # TODO: Add support running LlamaCpp here and add mechanism to trim tokens if the message is too long
        # self.model = "llama3"
        model_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        # self.api_url = "http://localhost:11434/v1"
        # self.api_key = "x"

        if self.api_key:
            model_params["api_key"] = self.api_key
        elif not self.api_key:
            model_params["api_key"] = "x"
        if self.api_url:
            model_params["api_url"] = self.api_url
        if self.temperature:
            model_params["temperature"] = self.temperature
        if self.max_tokens:
            model_params["max_tokens"] = self.max_tokens
        if self.context_window:
            model_params["context_window"] = self.context_window

        # TODO: Add support for max_budget
        # if self.max_budget:
        #     # In older way we were using a variable and then passing it to the model_params dictionary
        #     model_params["max_budget"] = self.max_budget
        # print("Running OpenAI-like LLM")
        if self.model.startswith("llamacpp"):
            yield from run_llama_cpp_llm(self, model_params)
        else:
            yield from run_openai_like_llm(self, model_params)


def run_openai_like_llm(llm, params):
    """
    This function is used to run the model in OpenAI-like format.
    """
    # print(llm)
    client = OpenAI(base_url=params.get("api_url"))
    # print(params)
    completion = client.chat.completions.create(
        model=params["model"].removeprefix("llamacpp"),
        messages=params["messages"],
        temperature=params.get("temperature"),
        stream=params.get("stream"),
    )
    yield from completion


def run_llama_cpp_llm(llm_instance, params):
    """
    This function is used to run the model in LlamaCpp format.
    """
    from llama_cpp import Llama

    # Check if the model is loaded, if not, load it
    if llm_instance.llama_cpp_model is None:
        print("Model loaded with LlamaCpp.")
        llm_instance.llama_cpp_model = Llama(
            model_path=params["model"].removeprefix("llamacpp/"), verbose=False
        )

    # Use the loaded model for inference
    completion = llm_instance.llama_cpp_model.create_chat_completion_openai_v1(
        messages=params["messages"],
        stream=params.get("stream"),
    )
    yield from completion


# if __name__  == "__main__":
#     llm = LLM(None)
#     messages = [
#         {
#             "role": "system",
#             "content": "I'm fine, thank you.",
#         },
#         {
#             "role": "user",
#             "content": "Hello, how are you?",
#         }
#     ]
#     print()
#     for chunk in llm.inference(messages):
#         if chunk.choices[0].delta.content:
#             print(chunk.choices[0].delta.content, end="", flush=True)
#     print("Done")
