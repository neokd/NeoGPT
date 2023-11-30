import sys
import threading
import time
from typing import Any
from uuid import UUID

import streamlit as st
from colorama import Fore
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult

from neogpt.config import CURRENT_WORKING_AGENT, PROJECT_COST, QUERY_COST, TOTAL_COST


class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.loading_thread = None
        self.streaming = False
        self.thinking_animation_thread = None
        self.neo_gpt_printed = False

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        # Start a new line for a clean display
        sys.stdout.write("\n")

        # Start a thread for the "NeoGPT 🤖 is thinking..." message
        self.thinking_animation_thread = threading.Thread(
            target=self.thinking_animation
        )
        self.thinking_animation_thread.start()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Stop the thinking animation thread when a new token is generated
        self.streaming = True

        if self.thinking_animation_thread and self.thinking_animation_thread.is_alive():
            self.thinking_animation_thread.join()  # Wait for the thread to finish

        if not self.neo_gpt_printed:
            sys.stdout.write(Fore.BLUE + "\nNeoGPT 🤖:")
            self.neo_gpt_printed = True

        # Display the generated token in a friendly way
        sys.stdout.write(Fore.WHITE + token)
        sys.stdout.flush()

    def thinking_animation(self):
        thinking_message = "NeoGPT 🤖 is thinking..."
        loading_chars = "/-\\"
        animation_idx = 0

        sys.stdout.write(Fore.BLUE + thinking_message)

        while not self.streaming:
            sys.stdout.write(loading_chars[animation_idx])
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")  # Move the cursor back to overwrite the animation
            animation_idx = (animation_idx + 1) % len(loading_chars)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.neo_gpt_printed = False
        self.streaming = False


# Define a custom callback handler class for token collection
class TokenCallbackHandler(BaseCallbackHandler):
    """
    The TokenCallbackHandler class is a custom callback handler class for token and shows the cost of the query, total cost and total tokens generated.
    The cost are based on OpenAI's pricing model.
    """

    def __init__(self):
        super().__init__()
        self._tokens = []

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._tokens.append(token)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        global TOTAL_COST, QUERY_COST  # Use the global variables
        # Cost are based on OpenAI's pricing model
        QUERY_COST = round(
            ((len(self._tokens) / 1000) * 0.002) * 83.33, 5
        )  # INR Cost per token, rounded to 5 decimal places
        TOTAL_COST = round(
            TOTAL_COST + QUERY_COST, 5
        )  # Accumulate the cost, rounded to 5 decimal places
        total_tokens = len(self._tokens)
        print(Fore.WHITE + f"\n\nTotal tokens generated: {total_tokens}")
        print(Fore.WHITE + f"Query cost: {QUERY_COST} INR")
        print(Fore.WHITE + f"Total cost: {TOTAL_COST} INR")


class StreamlitStreamingHandler(StreamingStdOutCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self.output = st.empty()
        self._token = ""

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        del self.output
        self._token = ""
        self.output = st.empty()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self._token += token
        self.output.info(self._token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # Remove info message
        st.empty()


class AgentCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self._tokens = []
        self.loading_thread = None
        self.streaming = False
        self.thinking_animation_thread = None
        self.agent_printed = False
        self.current_working_agent = CURRENT_WORKING_AGENT

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        # Start a new line for a clean display
        # sys.stdout.write("\n")

        # Start a thread for the "NeoGPT 🤖 is thinking..." message
        self.thinking_animation_thread = threading.Thread(
            target=self.thinking_animation
        )
        self.thinking_animation_thread.start()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self._tokens.append(token)
        # Stop the thinking animation thread when a new token is generated
        self.streaming = True

        if self.thinking_animation_thread and self.thinking_animation_thread.is_alive():
            self.thinking_animation_thread.join()  # Wait for the thread to finish

        if not self.agent_printed:
            sys.stdout.write(Fore.BLUE + f"\n{self.current_working_agent[-1]}:")
            self.agent_printed = True

        # Display the generated token in a friendly way
        sys.stdout.write(Fore.WHITE + token)
        sys.stdout.flush()

    def thinking_animation(self):
        thinking_message = f"\n{self.current_working_agent[-1]} is thinking..."
        loading_chars = "/-\\"
        animation_idx = 0

        sys.stdout.write(Fore.BLUE + thinking_message)

        while not self.streaming:
            sys.stdout.write(loading_chars[animation_idx])
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")  # Move the cursor back to overwrite the animation
            animation_idx = (animation_idx + 1) % len(loading_chars)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.agent_printed = False
        self.streaming = False
        global TOTAL_COST, QUERY_COST  # Use the global variables
        # Cost are based on OpenAI's pricing model
        QUERY_COST = round(
            ((len(self._tokens) / 1000) * 0.002) * 83.33, 5
        )  # INR Cost per token, rounded to 5 decimal places
        TOTAL_COST += round(
            QUERY_COST, 5
        )  # Accumulate the cost, rounded to 5 decimal places
        final_cost()
        # print(Fore.WHITE + f"Total cost: {TOTAL_COST} INR")


def final_cost():
    global PROJECT_COST
    PROJECT_COST += TOTAL_COST
    return PROJECT_COST
