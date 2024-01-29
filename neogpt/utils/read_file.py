import re
import base64
from PIL import Image
from io import BytesIO
import PyMuPDF
from langchain.schema import HumanMessage



def read_file(user_input):
    # regex to find if input has a file path between single quotes
    regex = re.compile(r"'([^']+)'")
    file_paths = [match.group(1) for match in regex.finditer(user_input)]

    for file_path in file_paths:
        extension = file_path.split(".")[-1]

        if extension.lower() in ["txt"]:
            with open(file_path, "r") as f:
                content = f.read()
                user_input = user_input.replace(file_path, content)
                
        elif extension.lower() in ["pdf"]:
            with open(file_path, "rb") as f:
                pdf_doc = fitz.open(f)
                pdf_content = ""
                for page_num in range(pdf_doc.page_count):
                    page = pdf_doc[page_num]
                    pdf_content += page.get_text("text")
                    user_input = user_input.replace(file_path, pdf_content)

        # elif extension.lower() in ["jpg", "jpeg", "png"]:
        #     with open(file_path, "rb") as f:
        #         content = f.read()
        #         encoded = base64.b64encode(content).decode("utf-8")
        #         user_input = user_input.replace(file_path,encoded)

    return user_input
