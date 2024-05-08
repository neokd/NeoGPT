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
    file_regex = re.compile(
        r"(?:[a-zA-Z]:)?(?:[\\/][^:<>\"/|?*\n\r\s]+(?:\s[^:<>\"/|?*\n\r]+)*)+(?:\.(?i:txt|pdf|png|jpg|svg|jpeg|py|csv|doc|docx|ppt|pptx|xls|xlsx)\b)"
    )
    file_paths = [match.group(0) for match in file_regex.finditer(user_input)]
    file_paths = [path for path in file_paths if os.path.exists(path)]
    return file_paths[0] if file_paths else None
