class BaseLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self):
        raise NotImplementedError("load method is not implemented")

    def lazy_load(self):
        return self.load()
