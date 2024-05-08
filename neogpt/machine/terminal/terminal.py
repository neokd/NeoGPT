import re

from machine.terminal.languages.python import PythonRunner
from machine.terminal.languages.shell import ShellRunner
from rich.markdown import Markdown
from utils.cprint import cprint


class Terminal:
    def __init__(self, neogpt) -> None:
        self.neogpt = neogpt
        self.role = "Terminal 🤖🧠"
        self.executors = {
            "python": PythonRunner(neogpt),
            "bash": ShellRunner(neogpt),
            "sh": ShellRunner(neogpt),
            "powershell": ShellRunner(neogpt),
        }

    def _preprocess_code(self, command):
        code_pattern = re.compile(r"```([^\n]*)\n(.*?)```", re.DOTALL)
        matches = code_pattern.findall(command)
        if len(matches) == 0:
            return None, command

        language, code = matches[0]
        combined_blocks = {}
        for language, code in matches:
            language = language.strip()
            code = code.strip()

            if language not in combined_blocks:
                combined_blocks[language] = code
            else:
                combined_blocks[language] += "\n" + code
        return language, "".join(combined_blocks.values())

    def run(self, command):
        if self.neogpt.verbose:
            print(f"\nNeoGPT is using the {self.role} to execute the command.\n")
        language, code = self._preprocess_code(command)
        if language:
            retry = 3  # Max retries allowed for the code execution
            while retry > 0:
                result, err = self.executors[language].execute(language, code)

                if err:
                    # Check for basic errors and retry or else
                    # Add fix for common ModuleNotFoundError in python and retry
                    retry -= 1
                    cprint("An error occurred while executing the code. Retrying...")
                else:
                    cprint(Markdown(f"\n\nOutput:\n```bash\n{result}\n```"))
                    # Add result to the previous message
                    self.neogpt.messages[-1]["content"] += (
                        f"Output \n```bash\n{result}```"
                    )

                    break
            return result
        else:
            return ""
