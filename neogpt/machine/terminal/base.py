from abc import ABC, abstractmethod


class CodeRunner(ABC):
    def __init__(self, neogpt) -> None:
        self.neogpt = neogpt

    @abstractmethod
    def execute(self, language, code):
        pass

    def _preprocess_code(self, command):
        # Implement preprocess_code method here
        pass
