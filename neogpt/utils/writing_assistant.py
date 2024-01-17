import os
import errno

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')


def writing_assistant (filepath, content):
    '''
    Write content to a given filename

    Params:
    filepath: path and filename to write to
    content: text content
    '''
    with safe_open_w(filepath) as f:
        f.write(content)

# test
#writing_assistant('../test/test.py','test')