import base64
import re
from io import BytesIO

import pandas as pd
from langchain_community.document_loaders import PDFMinerLoader
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.document_loaders import UnstructuredWordDocumentLoader, UnstructuredExcelLoader, UnstructuredPowerPointLoader
from PIL import Image


def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Re-sized BSase64 string
    """
    # Convert image to 'RGB' mode to avoid 'RGBA' mode issues
    pil_image = pil_image.convert("RGB")

    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def read_file(user_input, chain):
    regex = re.compile(
        r"(?:[a-zA-Z]:)?(?:\.?/|\\)?(?:[^:<>\"/|?*\n\r]+)?\.(?i:txt|pdf|png|jpg|svg|jpeg|py|csv|doc|docx|ppt|pptx|xls|xlsx)\b"
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
            plt_img = Image.open(file)
            encoded = convert_to_base64(plt_img)
            # print(chain.combine_documents_chain.llm_chain.llm.client)
            chain.combine_documents_chain.llm_chain.llm = (
                chain.combine_documents_chain.llm_chain.llm.bind(images=[encoded])
            )

        elif extension.lower() in ["dox","docx"]:
            content = UnstructuredWordDocumentLoader(file).load()[0].page_content
            user_input = user_input.replace(file, content)

        elif extension.lower() in ["xls","xlsx"]:
            content = UnstructuredExcelLoader(file).load()[0].page_content
            user_input = user_input.replace(file, content)

        elif extension.lower() in ["ppt","pptx"]:
            content = UnstructuredPowerPointLoader(file).load()[0].page_content
            user_input = user_input.replace(file, content)

    return user_input
