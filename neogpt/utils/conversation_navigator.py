import os


def load_conversations():
    directory = "neogpt/conversations"
    files = []

    try:
        for filename in os.listdir(directory):
            if filename.endswith(".txt"): 
                files.append(os.path.join(directory, filename))
    except FileNotFoundError:
        print(f"Directory {directory} not found.")
    except PermissionError:
        print(f"Permission denied for directory {directory}.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return files

load_conversations()