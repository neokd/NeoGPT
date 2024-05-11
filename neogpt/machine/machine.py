from machine.browser.browser import Browser
from machine.terminal.terminal import Terminal


class Machine:
    def __init__(self, neogpt) -> None:
        self.neogpt = neogpt
        self.role = "Machine 🤖🧠"
        self.working_dir = "./machine/workspace/"
        self.terminal = Terminal(neogpt)
        self.browser = Browser(neogpt)

    def run(self, command):
        return self.terminal.run(command)
