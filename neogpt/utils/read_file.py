import base64
import re
from io import BytesIO

import pandas as pd
import tiktoken
from langchain_community.document_loaders import (
    AsyncHtmlLoader,
    PDFMinerLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_community.document_transformers import Html2TextTransformer
from PIL import Image
from rich.console import Console
from neogpt.settings import config


# Create a console instance
console = Console()

# Define a shorthand for console.print using a lambda function
def cprint(*args, **kwargs):
    return console.print(*args, **kwargs)


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
    """
    Function to read files and URLs and replace them with their content.

    Parameters:
    user_input (str): The input prompt from the user.
    chain (Chain): The current chat session.

    Returns:
    str: The input prompt with files and URLs replaced by their content.

    """
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # web_regex = re.compile(r"(http|https)://[^\s]+(?<!\.(?:png|jpg|jpeg|gif|bmp|svg))")
    # web_paths = [match.group(0) for match in web_regex.finditer(user_input)]
    # if len(web_paths) > 0:
    #     html2text = Html2TextTransformer()
    #     for web in web_paths:
    #         content = AsyncHtmlLoader(web).load()
    #         # print(content)
    #         content = html2text.transform_documents(content)
    #         user_input = user_input.replace(web, content[0].page_content).strip()
    #         if len(tokenizer.encode(user_input)) > config.MAX_TOKEN_LENGTH:
    #             user_input = user_input[: config.MAX_TOKEN_LENGTH]
    #         # print(user_input)
    #     return user_input
    # Regular expression to match file paths

    file_regex = re.compile(
        r"(?:[a-zA-Z]:)?(?:[\\/][^:<>\"/|?*\n\r\s]+(?:\s[^:<>\"/|?*\n\r]+)*)+(?:\.(?i:txt|pdf|png|jpg|svg|jpeg|py|csv|doc|docx|ppt|pptx|xls|xlsx)\b)"
    )

    file_paths = [match.group(0) for match in file_regex.finditer(user_input)]
    
    if len(file_paths) > 0:
        for file in file_paths:
            extension = file.split(".")[-1]

            if extension.lower() in ["txt", "log", "md"]:
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
                user_input = user_input.replace(file, "```python" + content + "```")

            elif extension.lower() == "csv":
                content = ""
                df = pd.read_csv(file)
                content += (
                    "\n" + df.to_string() + "\n\n the file name is " + file + "\n\n"
                )
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

            elif extension.lower() in ["dox", "docx", "doc"]:
                content = UnstructuredWordDocumentLoader(file).load()[0].page_content
                user_input = user_input.replace(file, content)

            elif extension.lower() in ["xls", "xlsx"]:
                content = UnstructuredExcelLoader(file).load()[0].page_content
                user_input = user_input.replace(file, content)

            elif extension.lower() in ["ppt", "pptx"]:
                content = UnstructuredPowerPointLoader(file).load()[0].page_content
                user_input = user_input.replace(file, content)

    if len(tokenizer.encode(user_input)) > config.MAX_TOKEN_LENGTH:
        user_input = user_input[: config.MAX_TOKEN_LENGTH]
        # Not the best way to handle this, but it's a quick fix for now
        cprint(f"\n[bold red]The input prompt is too long. It has been truncated to {config.MAX_TOKEN_LENGTH} tokens.[/bold red]")

    return user_input
