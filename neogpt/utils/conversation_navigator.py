import os


def load_conversations():
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
    else:
        print(f"Directory {conversations_dir} does not exist.")

    return files
