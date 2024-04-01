import ast
import os
import platform
import re
import subprocess
import tempfile

from bs4 import BeautifulSoup
from langchain.schema import AIMessage
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Confirm
from rich.rule import Rule

from neogpt.settings import WORKSPACE_DIRECTORY
from neogpt.utils import read_file

console = Console()

LANGUAGE_EXTENSIONS = {
    "python": "py",
    "javascript": "js",
    "txt": "txt",
    "bash": "sh",
    "html": "html",
}


# Define a shorthand for console.print using a lambda function
def cprint(*args, **kwargs):
    return console.print(*args, **kwargs)


def is_bash_code(code):
    # Check if the code contains common Bash keywords or patterns
    bash_pattern = re.compile(
        r"\b(?:if|else|fi|while|do|done|for|in|function|echo|export|alias|source|mkdir|cd|ls|pwd|cat|grep|sed|awk|curl|wget|tar|zip|unzip|git|ssh|scp|rsync|chmod|chown|chgrp|sudo|su|apt|yum|dnf|brew|npm|pip|python|node|java|gcc|g++|make|cmake|mvn|gradle|ant|docker)\b"
    )
    return bool(bash_pattern.search(code))


def is_python_code(code):
    # Check if the code is a valid Python code
    if ast.parse(code):
        return True
    return False


def is_javascript_code(code):
    # Check if the code is a valid JavaScript code
    # TODO: Improvement for React, Vue, Angular, etc. code and add browser type js also
    js_pattern = re.compile(
        r"\b(?:function|var|let|const|console|return|import|export|class|extends|super|this|new|async|await|=>)\b"
    )
    return bool(js_pattern.search(code))


def is_html_code(code):
    # Check if the code is a valid HTML code
    # Check for HTML Tree Structure
    soup = BeautifulSoup(code, "html.parser")
    required_tags = ["html", "head", "body"]
    if all(soup.find(tag) for tag in required_tags):
        head = soup.head
        body = soup.body

        if head.findChildren() and body.findChildren():
            # Check if there are any direct children outside the "html" tag
            if len(soup.find_all(recursive=False)) > 1:
                return False
            return True
    return False


def language_parser(language, code):
    """
    This code matches ```language and check if the model has generated the correct language or not. For example, if the model has generated python code, it should be in the following format:
    ```python
    print("Hello World")
    ```
    but if the model has generated python code but the format is incorrect, it will be fixed to the correct format.
    ```css``` ->            ```python
    print("Hello World") ->  print("Hello World")
    ```                     ```
    """
    # cprint(f"Language: {language}")
    if language not in LANGUAGE_EXTENSIONS:
        if is_bash_code(code):
            return "bash", code
        elif is_python_code(code):
            if ">>>" in code:
                code = code.replace(">>>", "")
                print(code)
            return "python", code
        elif is_html_code(code):
            return "html", code
        elif is_javascript_code(code):
            return "javascript", code
    return language, code


def shell(language, code, force_run):
    """
    This function executes the code in the shell and returns the output and error if any.
    Basically, it checks the language and executes the code accordingly.
    """
    # cprint(f"Executing {language} code: \n{code}")
    lang, parsed_code = language_parser(language, code)
    # print(lang, parsed_code)
    if not force_run:
        confirm = Confirm.ask(f"\nDo you want to execute the {lang} code?")
        if not confirm:
            return "Skipping execution...", None

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=f".{LANGUAGE_EXTENSIONS[lang]}",
        delete=False,
        dir=WORKSPACE_DIRECTORY,
    ) as f:
        f.write(parsed_code)
        f.close()
        file_path = f.name

    if lang == "python":
        try:
            result = subprocess.run(
                f"python {file_path}",
                shell=True,
                capture_output=True,
                text=True,
                bufsize=1,
                cwd=os.getcwd(),
            )
            os.remove(file_path)
            return result.stdout, result.stderr
        except KeyboardInterrupt:
            os.remove(file_path)
            return "Execution interrupted", None

    elif lang == "bash":
        # Check the platform and use the correct terminal to execute the command
        terminal = "cmd.exe" if platform.system() == "Windows" else "bash"

        if any(command in code for command in ["cd"]):
            os.chdir(os.path.expanduser(parsed_code.split("cd")[-1].strip()))
            return f"Changed directory to {os.getcwd()}", None

        result = subprocess.run(
            f"{terminal} {file_path}",
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )
        os.remove(file_path)
        return result.stdout, result.stderr

    elif language == "html":
        # Open the file in the default browser
        try:
            os.startfile(file_path)
            # os.remove(file_path)
        except AttributeError:
            if platform.system() == "Darwin":
                os.system(f"open {file_path}")
            else:
                os.system(f"xdg-open {file_path}")
        return "Opening the HTML file in the default browser...", None

    elif language == "javascript":
        try:
            # check if node is installed
            result = subprocess.run(
                "node -v",
                shell=True,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                try:
                    result = subprocess.run(
                        f"node {file_path}",
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=os.getcwd(),
                    )
                    os.remove(file_path)
                    return result.stdout, result.stderr
                except KeyboardInterrupt:
                    os.remove(file_path)
                    return "Execution interrupted", None
            else:
                os.remove(file_path)
                return "Node is not installed", None

        except Exception as e:
            os.remove(file_path)
            return "Node is not installed", None

    else:
        os.remove(file_path)
        return f"Language {language} not supported.", None


def interpreter(message, chain, force_run):
    """
    This function interprets the user input and executes the corresponding command.
    TODO: have local context awareness and execute command and fix code if error is found.
    """
    # # Check for ``` in the message
    code_pattern = re.compile(r"```([^\n]*)\n(.*?)```", re.DOTALL)
    matches = code_pattern.findall(message)
    if len(matches) == 0:
        return message
    language, code = matches[0]
    combined_blocks = {}

    for language, code in matches:
        language = language.strip()
        code = code.strip()

        if language not in combined_blocks:
            combined_blocks[language] = code
        else:
            combined_blocks[language] += "\n" + code
    retry = True

    for language in combined_blocks:
        # This loop will execute the code in the order of the languages found in the message
        # cprint(Rule(f"Executing {language} code", style="blue"))
        output, error = shell(language, combined_blocks.get(language), force_run)

        if error and error is not None:
            cprint(Rule("\nNEOGPT'S INTERPRETER OUTPUT", style="red"))
            cprint(Markdown("\n" + f"```bash\n{error}\n```"))
            chain.combine_documents_chain.memory.chat_memory.messages.append(
                AIMessage(content=f"```bash\n{error}\n```")
            )
            cprint(Rule(style="red"))

            if "ModuleNotFoundError" in error:
                module = error.split("No module named ")[-1].strip()
                confirm = Confirm.ask(f"Do you want to install {module}?")
                if confirm:
                    result = subprocess.run(
                        f"pip install {module}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        cprint(f"Module {module} installed successfully.")
                        shell(language, combined_blocks.get(language), force_run)
                    else:
                        cprint(f"Error installing module {module}.")
                else:
                    cprint(f"Skipping installation of module {module}.")
            elif "Error: Cannot find module" in error:
                # Get the module name from the error message
                module = (
                    error.split("Error: Cannot find module ")[-1].strip().split("\n")[0]
                )
                # get that line only

                confirm = Confirm.ask(f"Do you want to install {module}?")
                if confirm:
                    result = subprocess.run(
                        f"npm install {module}",
                        shell=True,
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        cprint(f"Module {module} installed successfully.")
                        shell(language, combined_blocks.get(language))
                    else:
                        cprint(f"Error installing module {module}.")
                else:
                    cprint(f"Skipping installation of module {module}.")
            else:
                confirm = Confirm.ask("Do you want to fix the code?")
                if confirm:
                    result = chain.invoke(
                        f"Help me to solve the issue and write updated code. Also explain what the issue was and what you did to fix it. \n Error {error} \n Code {combined_blocks.get(language)}. Make sure to write code in correct language."
                    )
                else:
                    cprint(Markdown("\n" + "```bash\nSkipping execution...\n```"))

        else:
            cprint(
                Rule(
                    f"\n[bold]NeoGPT EXECUTED {language.upper()} CODE[/bold]",
                    style="green",
                )
            )
            cprint(Markdown("\n" + f"```bash\n{output}\n```"))
            chain.combine_documents_chain.memory.chat_memory.messages.append(
                AIMessage(content=f"\n{output}\n")
            )
            cprint(Rule(style="green"))
