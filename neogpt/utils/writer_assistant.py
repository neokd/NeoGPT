import errno
import os


def writing_assistant(filepath, content, code=False):
    """
    Write content to a given filename

    Params:
    filepath: path and filename to write to
    content: text content
    code: if True, ensure the file has a .py extension
    """
    path = os.path.dirname(filepath)
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

    if code and not filepath.endswith(".py"): # ensure the file has a .py extension
        filepath += ".py"

    with open(filepath, "w", encoding="UTF8") as f: # write content to file
        f.write(content)


# test
# writing_assistant('../test/test.py','print(\'Hello world\')')
