import logging
import os
from concurrent.futures import ThreadPoolExecutor

from langchain.schema import Document

from neogpt.config import CODE_EXTENSION


def load_single_code(file_path: str) -> Document:
    """
    fn: load_single_code
    Description: The function loads a single code file
    Args:
        file_path (str): File path
    return:
        Code: Code
    """
    import chardet

    # Loads a single code file from a file path
    file_extension = os.path.splitext(file_path)[1]
    if file_extension in CODE_EXTENSION:
        with open(file_path, "rb") as f:
            # Detect encoding
            result = chardet.detect(f.read())
            encoding = result["encoding"]

        with open(file_path, encoding=encoding) as f:
            code = f.read()

        return Document(
            page_content=code, metadata={"source": file_path, "encoding": encoding}
        )


def load_code_batch(filepaths):
    """
    fn: load_code_batch
    Description: The function loads a batch of code files
    Args:
        filepaths (list): List of file paths
    return:
        list: List of data from the code files
    """
    logging.info("Loading code batch")
    # create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # load code files
        futures = [exe.submit(load_single_code, name) for name in filepaths]
        # collect data
        data_list = [future.result() for future in futures]
        # return data and file paths
        return (data_list, filepaths)
