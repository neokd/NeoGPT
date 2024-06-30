"""
This module contains the LLM class which is the main class for the LLM model. We'll be following OpenAI message format for interaction with the model.
"""

import os
from base64 import b64encode
from pathlib import Path

from openai import OpenAI
from prompts.factory import prompt_factory
from settings import Settings
from utils.cprint import cprint


class LLM:
    def __init__(self, neogpt) -> None:
        self.neogpt = neogpt
        # Model Name
        self.model = "" or Settings.MODEL_NAME
        # Model Type
        self.support_vision = False

        # Settings for the model
        self.temperature = 0
        self.max_tokens = 8192
        self.context_window = 8192
        self.api_key = None
        self.api_url = None

        # Set Budget for Paid API
        self.max_budget = None

        # Set the persona
        self.persona = None

        # Avoid repetition of loading LlamaCpp Model
        self.llama_cpp_model = None

    def format_message(self, message, image_path=None):
        """
        This method formats a message according to OpenAI's expected input.
        If image_path is provided, it reads and encodes the image.
        """
        if image_path:
            try:
                with open(image_path, "rb") as img_file:
                    image_data = b64encode(img_file.read()).decode("utf-8")
                return {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            },
                        },
                    ],
                }
            except FileNotFoundError:
                print(f"Image file not found: {image_path}")
            except Exception as e:
                print(f"Error processing image: {e}")
        else:
            return {
                "role": "user",
                "content": message,
            }

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

        if self.support_vision and messages[-1].get("type") == "image":
            last_message = messages[-1]
            content = last_message["content"]
            image_path = last_message["image"]
            file_extension = image_path.split(".")[-1]
            content = content.replace(image_path, "")

            try:
                with open(image_path, "rb") as image_file:
                    image_data = b64encode(image_file.read()).decode("utf-8")
            except FileNotFoundError:
                print(f"Image file not found: {image_path}")
                return  # Exit the function if the image file is not found

            formatted_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": content},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{file_extension};base64,{image_data}"
                        },
                    },
                ],
            }
            messages[-1] = formatted_message

        try:
            if self.context_window and self.max_tokens:
                print("---Yet to implement---")
                print(self.context_window - self.max_tokens)
        except Exception as e:
            print(f"Error: {e}")

        model_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_window": self.context_window,
        }

        model_params["messages"] = prompt_factory(self.model, messages)

        if self.neogpt.offline:
            # Make the api key to null or a dummy key if the user is running the model offline
            pass
        # print(model_params["messages"])
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

        if self.model.startswith("llamacpp"):
            yield from run_llama_cpp_llm(self, model_params)
        else:
            yield from run_openai_like_llm(self, model_params)


def run_openai_like_llm(llm, params):
    """
    This function is used to run the model in OpenAI-like format.
    """
    client = OpenAI(base_url=params.get("api_url"), api_key=params.get("api_key"))
    completion = client.chat.completions.create(
        model=params["model"],
        messages=params["messages"],
        temperature=params.get("temperature"),
        stream=params.get("stream"),
    )
    yield from completion



def run_llama_cpp_llm(llm_instance, params):
    """
    This function is used to run the model in LlamaCpp format.
    """
    try:
        from huggingface_hub import hf_hub_download
        from llama_cpp import Llama
    except ImportError:
        cprint(
            "LlamaCpp is not installed. Please install it using `pip install llama-cpp-python`.",
        )

    model = params["model"].removeprefix("llamacpp/")
    model_file = Settings.MODEL_FILE
    model_path = os.path.join(Settings.DEFAULT_MODEL_DIR, model_file)

    if not os.path.isdir(model_path) and llm_instance.neogpt.verbose:
        cprint(
            f"Model file not found. Downloading {model_file} from Hugging Face Hub..."
        )
    model_path = hf_hub_download(
        repo_id=model,
        filename=model_file,
        resume_download=True,
        cache_dir=Settings.DEFAULT_MODEL_DIR,
    )
    # cprint(params)
    if llm_instance.llama_cpp_model is None:
        if llm_instance.neogpt.verbose:
            cprint("Loading LlamaCpp model...")
        llm_instance.llama_cpp_model = Llama(
            model_path=model_path,
            verbose=False,
            n_ctx=params.get("context_window"),
            n_gpu_layers=1,
            max_tokens=params.get("max_tokens"),
            temperature=params.get("temperature"),
            f16_kv=True,
        )
    # To limit the context window size  "Requested tokens (5418) exceed context window of 4096"
    last_message = [params["messages"][-1]]
    completion = llm_instance.llama_cpp_model.create_chat_completion_openai_v1(
        messages=last_message,
        stream=params.get("stream"),
    )
    yield from completion


# def convert_to_openai_format(messages):
#     """
#     This function is used to convert the messages to OpenAI format.
#     """
#     openai_messages = []
#     for message in messages:
#         if message["role"] != "system" and message["role"] != "user":
#             openai_messages.append(
#                 {
#                     "role": "assistant",
#                     "content": message["content"],
#                 }
#             )
#         else:
#             if message["role"] == "user" and isinstance(message.get("content"), list):
#                 openai_messages.append(
#                     {
#                         "role": message["role"],
#                         "content": message["content"],
#                     }
#                 )
#             else:
#                 openai_messages.append(
#                     {
#                         "role": "user",
#                         "content": message["content"],
#                     }
#                 )
#     return openai_messages
