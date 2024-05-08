import base64
import readline

from rich.markdown import Markdown
from rich.prompt import Prompt
from utils.cprint import cprint
from utils.formatter import MessageFormatter
from utils.magic_command import magic_commands
from utils.read_file import read_file


def terminal_chat(neogpt, message):
    while True:
        message = Prompt.ask("\nYou > ")

        try:
            readline.add_history(message)
        except:
            pass

        if isinstance(message, str):
            if message.startswith("/"):
                magic_commands(message, neogpt)
                continue

            if neogpt.llm.support_vision:
                image_path = read_file(message)
                if image_path:
                    cprint("Image detected. Processing image...")
                    # Handle image processing
                    message.replace(image_path, "")
                    image = open(image_path.replace("'", ""), "rb").read()
                    base64_image = base64.b64encode(image).decode("utf-8")
                    print(message)

                    neogpt.messages.append(
                        {
                            "role": "user",
                            "type": "message",
                            "content": message,
                            "images": [base64_image],
                        }
                    )

        formatted_text = MessageFormatter()
        for chunk in neogpt.chat(message, display=False, stream=True):
            if chunk.choices[0].finish_reason is None:
                formatted_text.message += chunk.choices[0].delta.content
                formatted_text.refresh()

            if (
                chunk.choices[0].finish_reason == "stop"
                or chunk.choices[0].delta.content == ""
            ):
                formatted_text.end()
                formatted_text.message = formatted_text.message.replace(
                    "<br/>\x1b[1;93mNeoGPT: \x1b[0m", ""
                )
                break

            yield chunk.choices[0].delta.content
