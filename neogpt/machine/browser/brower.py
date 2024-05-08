
from duckduckgo_search import DDGS


class Browser:
    def __init__(self, neogpt) -> None:
        self.role = "Browser 🌐🔍"
        self.browser = DDGS()
        self.neogpt = neogpt

    def search(self, query):
        result = self.browser.text(query, max_results=5)
        print(result)
        # Close the session after the search
        # self.browser._close_session()
        return result
