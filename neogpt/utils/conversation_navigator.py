import os

from rich.console import Console


def load_conversations():
    console = Console()
    conversations_dir = "neogpt/conversations"
    files = []

    # Check if the directory exists
    if os.path.exists(conversations_dir):
        # Get all files in the directory
        for filename in os.listdir(conversations_dir):
            # Full file path
            file_path = os.path.join(conversations_dir, filename)
            # Check if it's a file
            if os.path.isfile(file_path):
                files.append(file_path)

        if files:
            console.print("Select a conversation to load:", style="bold blue")
            for i, file in enumerate(files, start=1):
                console.print(f"{i}. {file}", style="green")
            selected = int(input("Enter the number of the conversation to load: "))
            console.print(f"You selected: {files[selected-1]}", style="bold yellow")
            return files[selected-1]
        else:
            console.print("No conversations found in the directory.", style="bold red")
            return None
    else:
        console.print(f"Directory {conversations_dir} does not exist.", style="bold red")
        return None