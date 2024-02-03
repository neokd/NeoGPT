import re
import base64
from PIL import Image
from io import BytesIO
from langchain.schema import HumanMessage
from langchain_community.document_loaders import PDFMinerLoader

def read_file(user_input):

    regex = re.compile(r'(?:[a-zA-Z]:)?(?:\./|/|\\)[\S\\ ]+?\.(?i:txt|pdf|png|svg|jpeg)\b')
    file_paths = [match.group(0) for match in regex.finditer(user_input)]

    for file in file_paths:
        extension = file.split(".")[-1]

        if extension.lower() in ["txt","log"]:
            with open(file, "r") as f:
                content = f.read()
                user_input = user_input.replace(file, content)

        elif extension.lower() == "pdf":
            content = PDFMinerLoader(file).load()[0].page_content
            user_input = user_input.replace(file, content)
        
        elif extension.lower() in ["jpg", "jpeg", "png"]:
            with open(file, "rb") as f:
                content = f.read()
                encoded = base64.b64encode(content).decode("utf-8")
                user_input = user_input.replace(file,encoded)

    return user_input
