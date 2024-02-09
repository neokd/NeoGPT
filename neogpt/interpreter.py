from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
import subprocess
from rich.prompt import Prompt
import re


def shell():
    

    
    result = subprocess.run("""ls -l""", shell=True, capture_output=True, text=True)
    print(result.stdout)
    return


def interpreter(message, chain):
    """
    This function interprets the user input and executes the corresponding command.
    TODO: have local context awareness and execute command and fix code if error is found.
    """
    # # Check for ``` in the message
    code_pattern = re.compile(r'```([^\n]*)\n(.*?)```', re.DOTALL)
    matches = code_pattern.findall(message)

    if len(matches) == 0:
        return message

    language, code = matches[0]
    
    """
    Identify the language write it to a temporary file and execute it using the shell. 
    """


    return code






    # combined_blocks = {}
    
    # for language, code in matches:
    #     language = language.strip()
    #     code = code.strip()
        
    #     if language not in combined_blocks:
    #         combined_blocks[language] = code
    #     else:
    #         combined_blocks[language] += '\n' + code



