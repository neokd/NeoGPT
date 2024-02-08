import os
import sys
import threading
import time
from typing import Any
from uuid import UUID

import streamlit as st
import tiktoken
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult
from rich.console import Console

from neogpt.config import CURRENT_WORKING_AGENT, QUERY_COST, TOTAL_COST
from neogpt.utils.formatter import MessageFormatter
from neogpt.utils.budget_manager import final_cost

OPENAI_MODEL_COST_PER_1K_TOKENS = {
    # GPT-4 input
    "gpt-4": 0.03,
    "gpt-4-0314": 0.03,
    "gpt-4-0613": 0.03,
    "gpt-4-32k": 0.06,
    "gpt-4-32k-0314": 0.06,
    "gpt-4-32k-0613": 0.06,
    "gpt-4-vision-preview": 0.01,
    "gpt-4-1106-preview": 0.01,
    # GPT-4 output
    "gpt-4-completion": 0.06,
    "gpt-4-0314-completion": 0.06,
    "gpt-4-0613-completion": 0.06,
    "gpt-4-32k-completion": 0.12,
    "gpt-4-32k-0314-completion": 0.12,
    "gpt-4-32k-0613-completion": 0.12,
    "gpt-4-vision-preview-completion": 0.03,
    "gpt-4-1106-preview-completion": 0.03,
    # GPT-3.5 input
    "gpt-3.5-turbo": 0.0015,
    "gpt-3.5-turbo-0301": 0.0015,
    "gpt-3.5-turbo-0613": 0.0015,
    "gpt-3.5-turbo-1106": 0.001,
    "gpt-3.5-turbo-instruct": 0.0015,
    "gpt-3.5-turbo-16k": 0.003,
    "gpt-3.5-turbo-16k-0613": 0.003,
    # GPT-3.5 output
    "gpt-3.5-turbo-completion": 0.002,
    "gpt-3.5-turbo-0301-completion": 0.002,
    "gpt-3.5-turbo-0613-completion": 0.002,
    "gpt-3.5-turbo-1106-completion": 0.002,
    "gpt-3.5-turbo-instruct-completion": 0.002,
    "gpt-3.5-turbo-16k-completion": 0.004,
    "gpt-3.5-turbo-16k-0613-completion": 0.004,
    # Azure GPT-35 input
    "gpt-35-turbo": 0.0015,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0301": 0.0015,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0613": 0.0015,
    "gpt-35-turbo-instruct": 0.0015,
    "gpt-35-turbo-16k": 0.003,
    "gpt-35-turbo-16k-0613": 0.003,
    # Azure GPT-35 output
    "gpt-35-turbo-completion": 0.002,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0301-completion": 0.002,  # Azure OpenAI version of ChatGPT
    "gpt-35-turbo-0613-completion": 0.002,
    "gpt-35-turbo-instruct-completion": 0.002,
    "gpt-35-turbo-16k-completion": 0.004,
    "gpt-35-turbo-16k-0613-completion": 0.004,
    # Others
    "text-ada-001": 0.0004,
    "ada": 0.0004,
    "text-babbage-001": 0.0005,
    "babbage": 0.0005,
    "text-curie-001": 0.002,
    "curie": 0.002,
    "text-davinci-003": 0.02,
    "text-davinci-002": 0.02,
    "code-davinci-002": 0.02,
    # Fine Tuned input
    "babbage-002-finetuned": 0.0016,
    "davinci-002-finetuned": 0.012,
    "gpt-3.5-turbo-0613-finetuned": 0.012,
    "gpt-3.5-turbo-1106-finetuned": 0.012,
    # Fine Tuned output
    "babbage-002-finetuned-completion": 0.0016,
    "davinci-002-finetuned-completion": 0.012,
    "gpt-3.5-turbo-0613-finetuned-completion": 0.016,
    "gpt-3.5-turbo-1106-finetuned-completion": 0.016,
    # Azure Fine Tuned input
    "babbage-002-azure-finetuned": 0.0004,
    "davinci-002-azure-finetuned": 0.002,
    "gpt-35-turbo-0613-azure-finetuned": 0.0015,
    # Azure Fine Tuned output
    "babbage-002-azure-finetuned-completion": 0.0004,
    "davinci-002-azure-finetuned-completion": 0.002,
    "gpt-35-turbo-0613-azure-finetuned-completion": 0.002,
    # Legacy fine-tuned models
    "ada-finetuned-legacy": 0.0016,
    "babbage-finetuned-legacy": 0.0024,
    "curie-finetuned-legacy": 0.012,
    "davinci-finetuned-legacy": 0.12,
}

# Need to add more models and their cost


TOGETHERAI_MODEL_COST_PER_1M_TOKENS = {
	# Chat Models
	"mistralai/Mixtral-8x7B-Instruct-v0.1": 0.60,
   	"mistralai/Mistral-7B-Instruct-v0.2": 0.20,
	"deepseek-ai/deepseek-coder-33b-instruct":0.80,
	"Qwen/Qwen1.5-72B-Chat":0.90,
	"Qwen/Qwen1.5-14B-Chat":0.30,
	"Qwen/Qwen1.5-7B-Chat":0.20,
	"Qwen/Qwen1.5-4B-Chat":0.10,
	"Qwen/Qwen1.5-1.8B-Chat":0.10,
	"Qwen/Qwen1.5-0.5B-Chat":0.10,
	"codellama/CodeLlama-70b-Instruct-hf": 0.90,
	"meta-llama/Llama-2-70b-chat-hf": 0.90,
	"snorkelai/Snorkel-Mistral-PairRM-DPO": 0.20,
	"codellama/CodeLlama-13b-Instruct-hf": 0.22,
	"codellama/CodeLlama-34b-Instruct-hf": 0.776,
	"codellama/CodeLlama-7b-Instruct-hf": 0.20,
	"NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO": 0.60,
	"NousResearch/Nous-Hermes-2-Mixtral-8x7B-SFT": 0.60,
	"NousResearch/Nous-Hermes-2-Yi-34B": 0.80,
	"openchat/openchat-3.5-1210": 0.20,
	"togethercomputer/StripedHyena-Nous-7B": 0.20,
	"DiscoResearch/DiscoLM-mixtral-8x7b-v2": 0.60,
	"mistralai/Mistral-7B-Instruct-v0.1": 0.20,
	"zero-one-ai/Yi-34B-Chat": 0.80,
	"NousResearch/Nous-Capybara-7B-V1p9": 0.20,
	"teknium/OpenHermes-2p5-Mistral-7B": 0.20,
	"upstage/SOLAR-10.7B-Instruct-v1.0": 0.30,
	"togethercomputer/llama-2-13b-chat": 0.22,
	"togethercomputer/llama-2-7b-chat": 0.20,
	"NousResearch/Nous-Hermes-Llama2-13b": 0.30,
	"NousResearch/Nous-Hermes-llama-2-7b": 0.20,
	"Open-Orca/Mistral-7B-OpenOrca": 0.20,
	"teknium/OpenHermes-2-Mistral-7B": 0.20,
	"WizardLM/WizardLM-13B-V1.2": 0.20,
	"togethercomputer/Llama-2-7B-32K-Instruct": 0.20,
	"lmsys/vicuna-13b-v1.5": 0.30,
	"Austism/chronos-hermes-13b": 0.30,
	"garage-bAInd/Platypus2-70B-instruct": 0.90,
	"Gryphe/MythoMax-L2-13b": 0.30,
	"togethercomputer/Qwen-7B-Chat": 0.20,
	"togethercomputer/RedPajama-INCITE-7B-Chat": 0.20,
	"togethercomputer/RedPajama-INCITE-Chat-3B-v1": 0.10,
	"togethercomputer/alpaca-7b": 0.20,
	"togethercomputer/falcon-40b-instruct": 0.80,
	"togethercomputer/falcon-7b-instruct": 0.20,
	#Language Models
	"Qwen/Qwen1.5-72B": 0.90,
	"Qwen/Qwen1.5-14B": 0.30,
	"Qwen/Qwen1.5-7B": 0.20,
	"Qwen/Qwen1.5-4B": 0.10,
	"Qwen/Qwen1.5-1.8B": 0.10,
	"Qwen/Qwen1.5-0.5B": 0.10,
	"mistralai/Mixtral-8x7B-v0.1": 0.60,
	"meta-llama/Llama-2-70b-hf": 0.90,
	"togethercomputer/StripedHyena-Hessian-7B": 0.20,
	"mistralai/Mistral-7B-v0.1": 0.20,
	"microsoft/phi-2": 0.10,
	"zero-one-ai/Yi-34B": 0.80,
	"zero-one-ai/Yi-6B": 0.14,
	"Nexusflow/NexusRaven-V2-13B": 0.30,
	"togethercomputer/LLaMA-2-7B-32K": 0.20,
	"togethercomputer/llama-2-13b": 0.22,
	"togethercomputer/llama-2-7b": 0.20,
	"togethercomputer/Qwen-7B": 0.20,
	"togethercomputer/RedPajama-INCITE-7B-Instruct": 0.20,
	"togethercomputer/RedPajama-INCITE-7B-Base": 0.20,
	"togethercomputer/RedPajama-INCITE-Instruct-3B-v1": 0.10,
	"togethercomputer/RedPajama-INCITE-Base-3B-v1": 0.10,
	"togethercomputer/GPT-JT-Moderation-6B": 0.20,
	"togethercomputer/falcon-40b": 0.80,
	"togethercomputer/falcon-7b": 0.20,
	#Code Models
	"codellama/CodeLlama-70b-Python-hf": 0.90,
	"codellama/CodeLlama-70b-hf": 0.90,
	"codellama/CodeLlama-13b-Python-hf": 0.22,
	"codellama/CodeLlama-34b-Python-hf": 0.776,
	"codellama/CodeLlama-7b-Python-hf": 0.20,
	"WizardLM/WizardCoder-Python-34B-V1.0": 0.80,
	"Phind/Phind-CodeLlama-34B-v2": 0.80,
}


class StreamingStdOutCallbackHandler(BaseCallbackHandler):
    """
    The StreamingStdOutCallbackHandler class is a custom callback handler class for streaming the output to the terminal.
    """

    def __init__(self):
        super().__init__()
        self.loading_thread = None
        self.streaming = False
        self.thinking_animation_thread = None
        self.console = Console()

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        # Start a new line for a clean display
        self.message_block_instance = MessageFormatter()
        # Start a thread for the "NeoGPT 🤖 is thinking..." message
        self.thinking_animation_thread = threading.Thread(
            target=self.thinking_animation
        )
        self.thinking_animation_thread.start()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Stop the thinking animation thread when a new token is generated
        self.streaming = True
        self.message_block_instance.message += token
        self.message_block_instance.refresh()

    def thinking_animation(self):
        # Loading animation when question is asked
        sys.stdout.write("\n")
        with self.console.status(
            "NeoGPT 🤖 is thinking...",
            spinner="bouncingBar",
            spinner_style="bold cyan",
            speed=0.5,
        ) as status:
            while not self.streaming:
                time.sleep(0.1)
                status.update()
                self.console.print("\r", end="")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.streaming = False
        self.message_block_instance.end()


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
        self.console = Console()

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        # Start a new line for a clean display
        self.message_block_instance = MessageFormatter()
        # Start a thread for the "NeoGPT 🤖 is thinking..." message
        self.thinking_animation_thread = threading.Thread(
            target=self.thinking_animation
        )
        self.thinking_animation_thread.start()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Stop the thinking animation thread when a new token is generated
        self.streaming = True
        self.message_block_instance.message += token
        self.message_block_instance.refresh()

    def thinking_animation(self):
        # Loading animation when question is asked
        sys.stdout.write("\n")
        with self.console.status(
            f"{self.current_working_agent[-1]} is thinking...",
            spinner="bouncingBar",
            spinner_style="bold cyan",
            speed=0.5,
        ) as status:
            while not self.streaming:
                time.sleep(0.1)
                status.update()
                self.console.print("\r", end="")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.agent_printed = False
        self.streaming = False
        self.message_block_instance.end()
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


"""
TODO: Add dynamic cost calculation based on the model used
"""



class TokenCallbackHandler(BaseCallbackHandler):
    """
    The TokenCallbackHandler class is a custom callback handler class for token and shows the cost of the query, total cost and total tokens generated.
    The cost are based on OpenAI's pricing model.
    """

    def __init__(self):
        self._tokens = []
        self.console = Console()
        # self.model_name = os.environ.get("MODEL_NAME")
        # Testing use the below line
        self.model_name = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
        # This is only for input tokens (OpenAI) and not for output tokens
        print(self.model_name)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.input_tokens = 0

        self.console.print(
            """
        "Token Callback Handler is under development. May not work as expected."
        """
        )

    def calculate_openai_cost(self, num_of_tokens, completion: bool = False):
        """
        Calculate the cost of the query based on the number of tokens generated.
        """
        if completion:
            cost_per_1k_tokens = OPENAI_MODEL_COST_PER_1K_TOKENS.get(
                f"{self.model_name}-completion"
            )
        else:
            cost_per_1k_tokens = OPENAI_MODEL_COST_PER_1K_TOKENS.get(self.model_name)

        cost = round(((num_of_tokens / 1000) * cost_per_1k_tokens) * 83, 5)
        return cost
    
    def calculate_togetherai_cost(self, num_of_tokens):
        """
        Calculate the cost of the query based on the number of tokens generated.
        """
        
        cost_per_1m_tokens = TOGETHERAI_MODEL_COST_PER_1M_TOKENS.get(self.model_name)
        cost = round(((num_of_tokens / 1_000_000) * cost_per_1m_tokens) * 83, 5)
        return cost

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        global QUERY_COST
        if "gpt-" in self.model_name:
            self.input_tokens = len(self.tokenizer.encode(prompts[0]))
            QUERY_COST += self.calculate_openai_cost(
                self.input_tokens, completion=False
            )
        else:
            pass

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


        if "gpt-" in self.model_name:
            QUERY_COST = self.calculate_openai_cost(len(self._tokens), completion=True)
        else:
            QUERY_COST = self.calculate_togetherai_cost(len(self._tokens))

        TOTAL_COST += QUERY_COST
        # # QUERY_COST = round(
        # #     (((len(self._tokens) + self.input_tokens) / 1000) * 0.002) * 83.33, 5
        # # )  # INR Cost per token, rounded to 5 decimal places
        # # TOTAL_COST = round(
        # #     TOTAL_COST + QUERY_COST, 5
        # # )  # Accumulate the cost, rounded to 5 decimal places
        # # total_tokens = len(self._tokens)
        # # self.console.print(f"\nTotal tokens generated: {total_tokens}")
        self.console.print(f"\nTotal tokens generated: {len(self._tokens) + self.input_tokens}")
        if "gpt-" in self.model_name:
            self.console.print(f"Prompt Tokens: {self.input_tokens}")
        self.console.print(f"Completion Tokens: {len(self._tokens)}")
        self.console.print(f"Query cost: {QUERY_COST:.5f} INR")
        self.console.print(f"Total cost: {TOTAL_COST:.5f} INR")
