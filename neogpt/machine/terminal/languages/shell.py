import os
import platform
import re
import subprocess
import tempfile

from machine.terminal.base import CodeRunner


class ShellRunner(CodeRunner):
    def __init__(self, neogpt) -> None:
        super().__init__(neogpt)
        self.extension = ".bat" if platform.system() == "Windows" else ".sh"
        self.command = "cmd.exe" if platform.system() == "Windows" else "bash"

    def execute(self, language, code):
        os.makedirs(self.neogpt.machine.working_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=self.extension,
            delete=False,
            dir=self.neogpt.machine.working_dir,
        ) as f:
            f.write(code)
            f.close()
            file_path = f.name

        result, err = self._subprocess_exec(self.command, file_path)
        return result, err

    def _subprocess_exec(self, language, file_path):
        result = subprocess.run(
            [language, file_path],
            shell=False,
            capture_output=True,
            text=True,
            bufsize=1,
            cwd=os.getcwd(),
        )
        os.remove(file_path)
        return result.stdout, result.stderr
