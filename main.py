import logging
from builder import builder
import argparse
from neogpt.retriever import db_retriver
from neogpt.config import (
    DEVICE_TYPE,
)
    


if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO,
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
        choices=["local","web","hybrid"],
        default="local",
        help="Specify the retriever (local, web, hybrid)",
    )
    parser.add_argument(
        "--persona",
        choices=["default", "recruiter", "academician", "friend", "ml_engineer", "ceo", "researcher"],
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
    args = parser.parse_args()
    if args.build:
        builder(vectorstore=args.db)

    db_retriver(device_type=args.device_type,vectordb=args.db,retriever=args.retriever,persona=args.persona, LOGGING=logging)
    

