import os, time, sys, select, argparse
from uuid import UUID
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema.output import LLMResult
from langchain.callbacks.base import BaseCallbackHandler
from colorama import init, Fore
from typing import Any, Dict, List, Optional
import streamlit as st
from neogpt.config import (
    TOTAL_COST,
    QUERY_COST
)

class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    """
    The StreamingStdOutCallbackHandler class is a callback handler from langchain that displays the generated tokens and adds a loading animation to show activity.
    """
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        # Start a new line for a clean display
        sys.stdout.write("\n")
        sys.stdout.write(Fore.BLUE + "NeoGPT 🤖 is thinking...")

        # Add a loading animation to show activity
        loading_chars = "/-\\"
        for char in loading_chars:
            sys.stdout.write('\b' + char)  # Move the cursor back to overwrite the token
            sys.stdout.flush()
            time.sleep(0.1)
        
        sys.stdout.write(Fore.BLUE + "\nNeoGPT 🤖:")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Display the generated token in a friendly way
        sys.stdout.write(Fore.WHITE + token)
        sys.stdout.flush()


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

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> Any:
        global TOTAL_COST, QUERY_COST  # Use the global variables
        # Cost are based on OpenAI's pricing model
        QUERY_COST = round(((len(self._tokens) / 1000) * 0.002) * 83.33, 5)  # INR Cost per token, rounded to 5 decimal places
        TOTAL_COST = round(TOTAL_COST + QUERY_COST, 5)  # Accumulate the cost, rounded to 5 decimal places
        total_tokens = len(self._tokens)
        print(Fore.WHITE + f"\n\nTotal tokens generated: {total_tokens}")
        print(Fore.WHITE + f"Query cost: {QUERY_COST} INR")
        print(Fore.WHITE + f"Total cost: {TOTAL_COST} INR")

class StreamlitStreamingHandler(StreamingStdOutCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self.output = st.empty()
        self._token = ''
    
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        del self.output
        self._token = ''
        self.output = st.empty()
        

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self._token += token
        self.output.info(self._token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # Remove info message
        st.empty()