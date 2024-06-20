# Adapted from OpenAI's Vision example
import base64

import requests
from openai import OpenAI

# Point to the local server
client = OpenAI(base_url="http://localhost:11434/api/generate", api_key="lm-studio")

# Ask the user for a path on the filesystem:
path = input("Enter a local filepath to an image: ")

# Read the image and encode it to base64:
base64_image = ""
try:
    image = open(path.replace("'", ""), "rb").read()
    base64_image = base64.b64encode(image).decode("utf-8")
except:
    print("Couldn't read the image. Make sure the path is correct and the file exists.")
    exit()

completion = client.chat.completions.create(
    model="xtuner/llava-phi-3-mini-gguf/llava-phi-3-mini-int4.gguf",
    messages=[
        {
            "role": "system",
            "content": "This is a chat between a user and an assistant. The assistant is helping the user to describe an image.",
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ],
    max_tokens=1000,
    stream=True,
)

for chunk in completion:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
