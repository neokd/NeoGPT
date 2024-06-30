import os
import subprocess
import tempfile

from machine.terminal.base import CodeRunner


class PythonRunner(CodeRunner):
    def __init__(self, neogpt) -> None:
        super().__init__(neogpt)

    def execute(self, language, code):
        os.makedirs(self.neogpt.machine.working_dir, exist_ok=True)
        import_machine_code = "import time\nfrom neogpt import neogpt\nmachine = neogpt.machine\nprint(machine)\n"
        code = import_machine_code + code
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            dir=self.neogpt.machine.working_dir,
        ) as f:
            f.write(code)
            f.close()
            file_path = f.name

        result, err = self._subprocess_exec("python", file_path)
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
        # os.remove(file_path)
        return result.stdout, result.stderr
