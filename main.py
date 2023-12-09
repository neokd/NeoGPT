import argparse
import logging
import sys
import json

from streamlit.web import cli as stcli

from neogpt.config import UI_ARGS_PATH
from neogpt.builder import builder
from neogpt.config import DEVICE_TYPE, NEOGPT_LOG_FILE
from neogpt.manager import db_retriver, hire
from neogpt.chat import chat_mode


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
        "--model_type",
        choices=["mistral", "llama", "ollama", "hf"],
        default="llama",
    )
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
        "--show_source",
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
        version="You are using NeoGPT🤖 v0.1.0-alpha.",
    )
    parser.add_argument("--task", type=str,
                        help="Task to be performed by the Agent")
    parser.add_argument(
        "--tries",
        type=int,
        default=5,
        help="Number of retries if the Agent fails to perform the task",
    )
    parser.add_argument("--mode", default="llm_only",
                        choices=['llm_only', 'db'], help="Specify the mode of query")

    args = parser.parse_args()

    ui_args = {
        "DB": args.db,
        "RETRIEVER": args.retriever,
        "PERSONA": args.persona,
        "MODEL_TYPE": args.model_type,
        "WRITE": args.write,
        "BUILD": args.build,
        "SHOW_SOURCE": args.show_source,
        "MODE": args.mode
        }
    
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

    if args.ui:
        logging.info("Starting the UI server for NeoGPT 🤖")
        logging.info(
            "Note: The UI server only supports local retriever and Chroma DB")
        # write the args in ui_args.json file to read from
        with open(UI_ARGS_PATH,"w") as file:
            json.dump(ui_args,file)
        sys.argv = ["streamlit", "run", "neogpt/ui.py"]
        sys.exit(stcli.main())

    elif args.task is not None:
        print()
        hire(
            task=args.task,
            tries=args.tries,
            LOGGING=logging,
        )
    elif args.mode == "llm_only":
        chat_mode(
            device_type=args.device_type,
            model_type=args.model_type,
            persona=args.persona,
            show_source=args.show_source,
            write=args.write,
            LOGGING=logging
        )
    else:
        db_retriver(
            device_type=args.device_type,
            model_type=args.model_type,
            vectordb=args.db,
            retriever=args.retriever,
            persona=args.persona,
            show_source=args.show_source,
            write=args.write,
            LOGGING=logging,
        )


if __name__ == "__main__":
    # Parse the arguments
    main()
