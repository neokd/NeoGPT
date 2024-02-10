import logging
import os
from concurrent.futures import ThreadPoolExecutor

from langchain.schema.document import Document

from neogpt.settings.config import DOCUMENT_EXTENSION


def load_single_document(file_path: str) -> Document:
    """
    fn: load_single_document
    Description: The function loads the single document
    Args:
        file_path (str): File path
    return:
        Document: Document
    """
    # Loads a single document from a file path
    file_extension = os.path.splitext(file_path)[1]
    loader_class = DOCUMENT_EXTENSION.get(file_extension)
    if loader_class:
        loader = loader_class(file_path)
    else:
        raise ValueError("Document type is undefined")
    return loader.load()[0]


def load_document_batch(filepaths):
    """
    fn: load_document_batch
    Description: The function loads the document batch
    Args:
        filepaths (list): List of file paths
    return:
        list: List of data from the files
    """
    logging.info("Loading document batch")
    # create a thread pool
    with ThreadPoolExecutor(len(filepaths)) as exe:
        # load files
        futures = [exe.submit(load_single_document, name) for name in filepaths]
        # collect data
        data_list = [future.result() for future in futures]
        # return data and file paths
        return (data_list, filepaths)
