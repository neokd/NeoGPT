import re

from rich.box import MINIMAL
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style


class Formatter:
    """
    A base class representing a visual "block" on the terminal.

    Attributes:
        live (Live): The Live instance for rendering on the terminal.

    Methods:
        __init__: Initializes the Formatter with a Live instance.
        update_from_message: Abstract method to be implemented by subclasses for updating content from a message.
        end: Stops the Live rendering, finalizing the display.
        refresh: Abstract method to be implemented by subclasses for refreshing the display.

    """

    def __init__(self):
        """
        Initializes the Formatter with a Live instance.
        """
        self.live = Live(
            auto_refresh=False, console=Console(), vertical_overflow="visible"
        )
        self.live.start()

    def update_from_message(self, message):
        """
        Abstract method to be implemented by subclasses for updating content from a message.

        Args:
            message (str): The message to update the content.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")

    def end(self):
        """
        Stops the Live rendering, finalizing the display.
        """
        self.refresh(cursor=False)
        self.live.stop()

    def refresh(self, cursor=True):
        """
        Abstract method to be implemented by subclasses for refreshing the display.

        Args:
            cursor (bool): Whether to include a cursor in the display.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")


class MessageFormatter(Formatter):
    """
    A subclass of Formatter representing a message block.

    Attributes:
        type (str): The type of the block.
        message (str): The message content.

    Methods:
        __init__: Initializes the MessageFormatter with a Live instance and default message.
        refresh: Refreshes the display with the formatted message.

    """

    def __init__(self):
        """
        Initializes the MessageFormatter with a Live instance and default message.
        """
        super().__init__()
        ai_message = Style(bold=True, color="bright_yellow").render("NeoGPT 🤖:")
        self.type = "message"
        self.message = ai_message + " "

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
        # panel = Panel(markdown, box=MINIMAL)
        self.live.update(markdown)
        self.live.refresh()
