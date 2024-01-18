import os
import errno

def writing_assistant (filepath, content):
    '''
    Write content to a given filename

    Params:
    filepath: path and filename to write to
    content: text content
    '''
    path = os.path.dirname(filepath)
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

    with open(filepath, 'w', encoding='UTF8') as f:
        f.write(content)

# test
# writing_assistant('../test/test.py','print(\'Hello world\')')