import os
import re


def read_file(user_input: str) -> str:
    """
    Reads a file and returns its content as a string.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        str: The content of the file as a string.
    """
    pattern = re.compile(
        r"([A-Za-z]:\\[^:\n]*?\.(png|jpg|jpeg|PNG|JPG|JPEG))|(/[^:\n]*?\.(png|jpg|jpeg|PNG|JPG|JPEG))"
    )
    matches = [match.group() for match in re.finditer(pattern, user_input) if match.group()]
    matches += [match.replace("\\", "") for match in matches if match]
    existing_paths = [match for match in matches if os.path.exists(match)]
    # print(existing_paths)
    return max(existing_paths, key=len) if existing_paths else None
