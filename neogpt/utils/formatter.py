import re

from rich.box import MINIMAL
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.style import Style


class MessageFormatter:
    """
    A class representing a message block formatter.

    Attributes:
        live (Live): The Live instance for rendering on the terminal.
        type (str): The type of the block.
        message (str): The message content.

    Methods:
        __init__: Initializes the MessageFormatter with a Live instance and default message.
        refresh: Refreshes the display with the formatted message.
        update_from_message: Updates content from a message.
        end: Stops the Live rendering, finalizing the display.
    """

    def __init__(self):
        """
        Initializes the MessageFormatter with a Live instance and default message.
        """
        self.live = Live(
            auto_refresh=False, console=Console(), vertical_overflow="visible"
        )
        self.live.start()
        ai_message = "<br/>" + Style(bold=True, color="bright_yellow").render(
            "NeoGPT: "
        )
        self.type = "message"
        self.message = ai_message

    def refresh(self, cursor=True):
        """
        Refreshes the display with the formatted message.

        Args:
            cursor (bool): Whether to include a cursor in the display.
        """
        content = self.message

        if cursor:
            content += "●"

        markdown = Markdown(content.strip(), code_theme="monokai")
        self.live.update(markdown)
        self.live.refresh()

    def update_from_message(self, message):
        """
        Updates content from a message.

        Args:
            message (str): The message to update the content.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def end(self):
        """
        Stops the Live rendering, finalizing the display.
        """
        self.refresh(cursor=False)
        self.live.stop()
