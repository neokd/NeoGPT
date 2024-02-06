import base64
import re
from io import BytesIO

import pandas as pd
from langchain_community.document_loaders import PDFMinerLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from PIL import Image


def read_file(user_input):
    regex = re.compile(
        r"(?:[a-zA-Z]:)?(?:\./|/|\\)[\S\\ ]+?\.(?i:txt|pdf|png|jpg|svg|jpeg|py|csv)\b"
    )
    file_paths = [match.group(0) for match in regex.finditer(user_input)]

    for file in file_paths:
        extension = file.split(".")[-1]

        if extension.lower() in ["txt", "log"]:
            with open(file) as f:
                content = f.read()
                user_input = user_input.replace(file, content)

        if extension.lower() == "py":
            loader = GenericLoader.from_filesystem(
                file,
                glob="*",
                suffixes=[".py"],
                parser=LanguageParser(),
            )
            content = loader.load()[0].page_content
            # print(content)
            user_input = user_input.replace(file, content)

        elif extension.lower() == "csv":
            content = ""
            df = pd.read_csv(file)
            content += "\n" + df.to_string() + "\n\n the file name is " + file + "\n\n"
            user_input = user_input.replace(file, content)

        elif extension.lower() == "pdf":
            content = PDFMinerLoader(file).load()[0].page_content
            user_input = user_input.replace(file, content)

        elif extension.lower() in ["jpg", "jpeg", "png"]:
            with open(file, "rb") as f:
                content = f.read()
                encoded = base64.b64encode(content).decode("utf-8")
                user_input = user_input.replace(file, encoded)

    return user_input
