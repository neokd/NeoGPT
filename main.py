import argparse
import json
import logging
import os
import sys
import warnings

from langchain_core._api.deprecation import LangChainDeprecationWarning
from streamlit.web import cli as stcli

from neogpt import config
from neogpt.builder import builder
from neogpt.chat import chat_mode
from neogpt.config import (
    DEVICE_TYPE,
    NEOGPT_LOG_FILE,
    export_config,
    import_config,
)
from neogpt.manager import hire, manager


def main():
    parser = argparse.ArgumentParser(description="NeoGPT CLI Interface")
    parser.add_argument(
        "--device-type",
        choices=["cpu", "mps", "cuda"],
        default=DEVICE_TYPE,
        help="Specify the device type (cpu, mps, cuda)",
    )
    parser.add_argument(
        "--db",
        choices=["Chroma", "FAISS"],
        default="Chroma",
        help="Specify the vectorstore (Chroma, FAISS)",
    )
    parser.add_argument(
        "--retriever",
        choices=["local", "web", "hybrid", "stepback", "sql", "compress"],
        default="local",
        help="Specify the retriever (local, web, hybrid, stepback, sql, compress). It allows you to customize the retriever i.e. how the chatbot should retrieve the documents.",
    )
    parser.add_argument(
        "--persona",
        choices=[
            "default",
            "recruiter",
            "academician",
            "friend",
            "ml_engineer",
            "ceo",
            "researcher",
            "shell",
        ],
        default="default",
        help="Specify the persona (default, recruiter). It allows you to customize the persona i.e. how the chatbot should behave.",
    )
    parser.add_argument(
        "--model-type",
        choices=["llamacpp", "ollama", "hf", "openai", "lmstudio"],
        default="llamacpp",
    )
    # TODO: Implement Writer Assistant
    parser.add_argument(
        "--write",
        default=None,
        help="Specify the file path for writing retrieval results. If not provided, 'notes.md' will be used as the default file name.",
        nargs="?",
        const="notes.md",
    )
    parser.add_argument(
        "--build", default=False, action="store_true", help="Run the builder"
    )
    parser.add_argument(
        "--show-source",
        default=False,
        action="store_true",
        help="The source documents are displayed if the show_sources flag is set to True.",
    )
    parser.add_argument(
        "--ui", default=False, action="store_true", help="Start a UI server for NeoGPT"
    )
    parser.add_argument(
        "--debug", default=False, action="store_true", help="Enable debugging"
    )
    parser.add_argument(
        "--verbose", default=False, action="store_true", help="Enable verbose mode"
    )
    parser.add_argument(
        "--shell",
        action="store_true",
        help="Gives shell access to NeoGPT and allows to run commands",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Shows token and cost statistics for the queries",
    )
    parser.add_argument(
        "--log",
        default=False,
        action="store_true",
        help="Logs Builder output to builder.log",
    )
    parser.add_argument(
        "--recursive",
        default=False,
        action="store_true",
        help="Recursively loads urls from builder.url file",
    )
    parser.add_argument(
        "--version",
        default=False,
        action="version",
        version="You are using NeoGPT🤖 v0.1.0-beta.",
    )
    parser.add_argument("--task", type=str, help="Task to be performed by the Agent")
    parser.add_argument(
        "--tries",
        type=int,
        default=5,
        help="Number of retries if the Agent fails to perform the task",
    )

    # Adding the --temperature argument
    parser.add_argument(
        "--temperature",
        type=float,
        default=config.TEMPERATURE,
        help=f"The temperature influences the randomness of the generated text. Default is {config.TEMPERATURE}",
        # The temperature parameter controls the randomness of predictions by scaling the logits before applying softmax.
        # A higher value makes the output more random, while a lower value makes it more deterministic.
    )

    # Adding the --max-tokens argument
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=config.MAX_TOKEN_LENGTH,
        help=f"Adjust max tokens to control response length. Default is {config.MAX_TOKEN_LENGTH}",
        # The max tokens parameter sets the maximum length of the generated text.
        # If the text exceeds this length, it will be cut off.
    )

    # Adding the --context-window argument
    parser.add_argument(
        "--context-window",
        type=int,
        default=config.CONTEXT_WINDOW,
        help=f"Context windows determine the number of tokens considered for context. Default is {config.CONTEXT_WINDOW}",
        # The context windows parameter sets the number of previous tokens to consider as context for the next token prediction.
        # A larger context window allows the model to consider more of the previous text when making predictions.
    )

    # Adding the --import switch with a YAML filename parameter
    parser.add_argument(
        "--import-config",
        nargs="?",
        const="settings.yaml",
        help="Import configuration settings from a YAML file (default: settings.yaml)",
    )

    # Adding the --export switch with an optional YAML filename parameter
    parser.add_argument(
        "--export-config",
        nargs="?",
        const="settings.yaml",
        help="Export configuration settings to a YAML file in ./neogpt/settings directory (default: settings.yaml)",
    )

    parser.add_argument(
        "--mode",
        default="db",
        choices=["llm", "db"],
        help="Specify the mode of query",
    )

    parser.add_argument(
        "--model",
        default="llamacpp",
        help="Specify the model dynamically and overwrite the config settings",
    )
    
    # Add budget and reduce the cost. If cost exceeds then stop the project
    parser.add_argument(
        "--max-budget",
        default=None,
        help="Specify the maximum budget for NeoGPT to spend. Useful when running an API",
    )
    parser.add_argument(
        "-y",
        help="Shell mode. Allows to run commands",
    )

    # TODO: Add proper voice mode when streaming text
    parser.add_argument(
        "--voice",
        default=False,
        action="store_true",
        help="Enable voice mode",
    )
    
    args = parser.parse_args()

    # This doesn't work as expected need to change it 
    if args.import_config:
        config_filename = args.import_config
        overwrite = import_config(config_filename)
    else:
        overwrite = {
            "PERSONA": args.persona,
            "UI": args.ui,
            "MODEL_TYPE": args.model_type,
        }
        # sys.exit()
    # Doesn't work as expected this is a crappy way to do it quickly need to change it
    if args.export_config:
        config_filename = args.export_config
        export_config(config_filename)
        sys.exit()  # Exit the script after exporting configuration


    if args.max_tokens:
        config.MAX_TOKEN_LENGTH = args.max_tokens

    if args.temperature:
        config.TEMPERATURE = args.temperature

    if args.context_window:
        config.CONTEXT_WINDOW = args.context_window

    if args.debug:
        log_level = logging.DEBUG
    elif args.verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    if args.log:
        log_level = logging.INFO
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
            level=log_level,
            filename=NEOGPT_LOG_FILE,
        )

    else:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
            level=log_level,
        )

    if args.model:
        model = args.model.split("/", 1)
        overwrite["MODEL_TYPE"] = model[0]

        if len(model) >= 2:
            os.environ["MODEL_NAME"] = model[1]

    # if not os.path.exists(FAISS_PERSIST_DIRECTORY):
    #     builder(vectorstore="FAISS")

    # if not os.path.exists(CHROMA_PERSIST_DIRECTORY):
    #     builder(vectorstore="Chroma")
    if args.build:
        builder(
            vectorstore=args.db,
            recursive=args.recursive,
            debug=args.debug,
            verbose=args.verbose,
        )

    if args.ui or (overwrite and overwrite["UI"]):
        logging.info("Starting the UI server for NeoGPT 🤖")
        logging.info("Note: The UI server only supports local retriever and Chroma DB")
        sys.argv = ["streamlit", "run", "neogpt/ui.py"]
        sys.exit(stcli.main())

    elif args.task is not None:
        hire(
            task=args.task,
            tries=args.tries,
            LOGGING=logging,
        )

    elif args.mode == "llm":
        chat_mode(
            device_type=args.device_type,
            model_type=args.model_type
            if overwrite["MODEL_TYPE"] is None
            else overwrite["MODEL_TYPE"],
            persona=args.persona
            if overwrite["PERSONA"] is None
            else overwrite["PERSONA"],
            show_source=args.show_source,
            write=args.write,
            LOGGING=logging,
        )
    else:
        manager(
            device_type=args.device_type,
            model_type=args.model_type
            if overwrite["MODEL_TYPE"] is None
            else overwrite["MODEL_TYPE"],
            vectordb=args.db,
            retriever=args.retriever,
            persona=args.persona
            if overwrite["PERSONA"] is None
            else overwrite["PERSONA"],
            show_source=args.show_source,
            write=args.write,
            shell=args.shell,
            show_stats=args.stats,
            LOGGING=logging,
        )
    # Supress Langchain Deprecation Warnings

    warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)


if __name__ == "__main__":
    # Parse the arguments
    main()
