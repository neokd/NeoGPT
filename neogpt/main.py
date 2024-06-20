from core import NeoGPT


def cli_args(neogpt):
    arguments = [{}]

    pass


if __name__ == "__main__":
    neogpt = NeoGPT()

    # neogpt.llm.api_key = "x"
    neogpt.llm.api_url = "http://localhost:11434/v1"
    neogpt.llm.model = "phi3"
    # neogpt.llm.support_vision = (
    # True  # When ollama brings Vision with OpenAI Compatability
    # )
    # print(neogpt)
    print(neogpt.chat())
