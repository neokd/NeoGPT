import logging
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial  # Import partial

from bs4 import BeautifulSoup as Soup
from langchain.schema.document import Document

from neogpt.config import URL_EXTENSION


def process_url(url_path: str, recursive: bool) -> Document:
    """
    fn: process_url
    Description: The function processes the url
    Args:
        file_path (str): File path
        additional_arg (str): Additional argument to be passed
    return:
        Document: Document
    """
    file_extension = os.path.splitext(url_path)[1]
    if file_extension != ".url":
        return  # Skip if not a .url file

    with open(url_path) as build:
        urls = build.readlines()
        for url in urls:
            if "youtube.com" in url:
                loader_class = URL_EXTENSION.get(".youtube", None)
                loader = loader_class.from_youtube_url(url, add_video_info=True)
            else:
                if recursive is True:
                    loader_class = URL_EXTENSION.get("recursive", None)
                    loader = loader_class(
                        url, extractor=lambda x: Soup(x, "html.parser").text
                    )
                else:
                    loader_class = URL_EXTENSION.get("normal", None)
                    loader = loader_class(url)

    result = loader.load()[0]
    return result


def load_url_batch(urlpaths, recursive):
    """
    fn: load_url_batch
    Description: The function loads the url batch
    Args:
        urlpaths (list): List of url paths
        additional_arg (str): Additional argument to be passed
    return:
        list: List of data from the urls
    """
    logging.info("Loading Url batch")
    with ThreadPoolExecutor(len(urlpaths)) as exe:
        # Use partial to pass additional_arg to process_url
        partial_process_url = partial(process_url, recursive=recursive)
        futures = [exe.submit(partial_process_url, name) for name in urlpaths]
        data_list = [future.result() for future in futures]
    return (data_list, urlpaths)
