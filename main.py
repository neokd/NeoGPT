import argparse
import logging
import os
import sys

from streamlit.web import cli as stcli

from builder import builder
from neogpt.config import CHROMA_PERSIST_DIRECTORY, DEVICE_TYPE, FAISS_PERSIST_DIRECTORY
from neogpt.manager import db_retriver

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
        level=logging.INFO,
    )
    # Parse the arguments
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
        ],
        default="default",
        help="Specify the persona (default, recruiter). It allows you to customize the persona i.e. how the chatbot should behave.",
    )
    parser.add_argument(
        "--build",
        default=False,
        action="store_true",
        help="Run the builder",
    )
    parser.add_argument(
        "--show_source",
        default=False,
        action="store_true",
        help="The source documents are displayed if the show_sources flag is set to True.",
    )
    parser.add_argument(
        "--ui",
        default=False,
        action="store_true",
        help="Start a UI server for NeoGPT",
    )
    parser.add_argument('--version', action='version', version='You are using NeoGPT🤖 v0.1.0-alpha.')
    args = parser.parse_args()

    if args.build:
        builder(vectorstore=args.db)

    if not os.path.exists(FAISS_PERSIST_DIRECTORY):
        builder(vectorstore="FAISS")

    if not os.path.exists(CHROMA_PERSIST_DIRECTORY):
        builder(vectorstore="Chroma")

    if args.ui:
        logging.info("Starting the UI server for NeoGPT 🤖")
        logging.info("Note: The UI server only supports local retriever and Chroma DB")
        sys.argv = ["streamlit", "run", "neogpt/ui.py"]
        sys.exit(stcli.main())
    else:
        db_retriver(
            device_type=args.device_type,
            vectordb=args.db,
            retriever=args.retriever,
            persona=args.persona,
            LOGGING=logging,
        )
