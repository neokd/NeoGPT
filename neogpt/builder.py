import argparse
import logging
import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial  # Import partial

from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

from neogpt.config import (
    BUILDER_LOG_FILE,
    DEVICE_TYPE,
    DOCUMENT_EXTENSION,
    INGEST_THREADS,
    RESERVED_FILE_NAMES,
    SOCIAL_CHAT_EXTENSION,
    SOURCE_DIR,
)
from neogpt.modules import (
    load_chat_batch,
    load_code_batch,
    load_document_batch,
    load_url_batch,
)
from neogpt.vectorstore import ChromaStore, FAISSStore


def build_documents(SOURCE_DIR: str = SOURCE_DIR, recursive: bool = False):
    document_paths = []
    chat_paths = []
    url_paths = []
    code_paths = []

    for root, _dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            extension = os.path.splitext(file)[1]
            if extension in DOCUMENT_EXTENSION and file not in RESERVED_FILE_NAMES:
                if any(re.match(pattern, file) for pattern in SOCIAL_CHAT_EXTENSION):
                    chat_paths.append(os.path.join(root, file))
                else:
                    document_paths.append(os.path.join(root, file))
            elif file in RESERVED_FILE_NAMES:
                url_paths.append(os.path.join(root, file))
            elif extension == ".py":
                code_paths.append(os.path.join(root, file))
            else:
                print("Builder: File type not supported: " + file)

    workers = min(
        INGEST_THREADS,
        max(len(document_paths), 1),
        max(len(url_paths), 1),
        max(len(chat_paths), 1),
        max(len(code_paths), 1),
    )

    chunk_size = round(
        (len(document_paths) + len(url_paths) + len(chat_paths) + len(code_paths))
        / workers
    )

    docs = []
    total_documents = (
        len(document_paths) + len(url_paths) + len(chat_paths) + len(code_paths)
    )
    with ProcessPoolExecutor(workers) as executor, tqdm(
        total=total_documents,
        desc=f"Builder is loading {total_documents} docs.",
        unit="files",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}, {rate_fmt}{postfix}]",
    ) as pbar:
        futures = []

        # partial function to pass recursive argument to load_url_batch
        load_url_batch_partial = partial(load_url_batch, recursive=False)

        if len(document_paths) > 0:
            for i in range(0, len(document_paths), chunk_size):
                filepaths = document_paths[i : (i + chunk_size)]
                future = executor.submit(load_document_batch, filepaths)
                futures.append(future)

        if len(url_paths) > 0:
            for i in range(0, len(url_paths), chunk_size):
                urlpaths = url_paths[i : (i + chunk_size)]
                future = executor.submit(load_url_batch_partial, urlpaths)
                futures.append(future)

        if len(chat_paths) > 0:
            for i in range(0, len(chat_paths), chunk_size):
                filepaths = chat_paths[i : (i + chunk_size)]
                future = executor.submit(load_chat_batch, filepaths)
                futures.append(future)

        if len(code_paths) > 0:
            for i in range(0, len(code_paths), chunk_size):
                filepaths = code_paths[i : (i + chunk_size)]
                future = executor.submit(load_code_batch, filepaths)
                futures.append(future)

        for future in as_completed(futures):
            contents, _ = future.result()
            docs.extend(contents)
            pbar.update(len(contents))
    return docs


def builder(
    vectorstore: str = "Chroma",
    recursive: bool = False,
    debug: bool = False,
    verbose: bool = False,
):
    """
    fn: builder
    Description: The function builds the vectorstore (Chroma, FAISS)
    Args:
        vectorstore (str, optional): Vectorstore (Chroma, FAISS). Defaults to "Chroma".
    return:
        None
    """

    logging.info(f"Loading Documents from {SOURCE_DIR}")
    documents = build_documents(SOURCE_DIR, recursive)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    texts = text_splitter.split_documents(documents)

    logging.info(f"Loaded {len(documents)} documents from {SOURCE_DIR}")
    logging.info(f"Split into {len(texts)} chunks of text")
    logging.info(f"Using {DEVICE_TYPE} device for embedding model")

    match vectorstore:
        case "Chroma":
            logging.info("Using Chroma for vectorstore")
            db = ChromaStore().from_documents(documents=texts)
            logging.info("Loaded Documents to Chroma DB Successfully")
        case "FAISS":
            logging.info("Using FAISS for vectorstore")
            db = FAISSStore().from_documents(documents=texts)
            logging.info("Loaded Documents to FAISS DB Successfully")
    if db:
        logging.info("Builder👷🏻‍♀️ has built your VectorDB successfully!")
    else:
        logging.info("Builder👷🏻‍♀️ has failed to build your VectorDB")


# def query():
#     embeddings = HuggingFaceInstructEmbeddings(
#         model_name=EMBEDDING_MODEL_NAME,
#         model_kwargs={"device": 'mps'},
#         cache_folder=os.path.join(os.path.dirname(__file__), "models"),
#     )
#     db = Chroma(
#         embedding_function=embeddings,
#         persist_directory=PERSIST_DIRECTORY,
#     )
#     while True:
#         query = input()
#         results= db.similarity_search(query)
#         print(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NeoGPT CLI Interface")
    parser.add_argument(
        "--db",
        choices=["Chroma", "FAISS"],
        default="Chroma",
        help="Specify the vectorstore (Chroma, FAISS)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debugging")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode")
    parser.add_argument(
        "--log", action="store_true", help="Logs Builder output to builder.log"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively loads urls from builder.url file",
    )

    log_level = logging.INFO
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
            level=logging.DEBUG,
        )
    elif args.verbose:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
            level=logging.INFO,
        )
    elif args.log:
        if not os.path.exists(BUILDER_LOG_FILE):
            with open(BUILDER_LOG_FILE, "w"):
                pass

        logging.basicConfig(
            filename=BUILDER_LOG_FILE,
            format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s",
            level=log_level,
        )

    args = parser.parse_args()
    builder(
        vectorstore=args.db,
        recursive=args.recursive,
        debug=args.debug,
        verbose=args.verbose,
    )
