import typer
from core import NeoGPT
from utils.conversation_navigator import conversation_navigator

app = typer.Typer()


@app.command()
def main(
    local: bool = typer.Option(
        True,
        "--local",
        "-l",
        help="Run the model locally instead of using an online API.",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Print verbose output for debugging purposes."
    ),
    build: bool = typer.Option(
        False, "--build", "-b", help="Build the vector database required for RAG."
    ),
    api_key: str = typer.Option(
        "", "--api-key", "-ak", help="API key required for accessing online models."
    ),
    api_url: str = typer.Option(
        "", "--api-url", "-au", help="URL endpoint for accessing online models."
    ),
    model: str = typer.Option(
        "lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF",
        "--model",
        "-m",
        help="Model name to use for the LLM.",
    ),
    server: bool = typer.Option(
        False, "--server", "-s", help="Start the NeoGPT API server."
    ),
    playground: bool = typer.Option(
        False, "--playground", "-p", help="Start the NeoGPT Playground."
    ),
    conversations: bool = typer.Option(
        False, "--conversations", "-c", help="Display past conversation history."
    ),
    temperature: float = typer.Option(
        0.7, "--temperature", "-t", help="Temperature parameter for the LLM."
    ),
    max_tokens: int = typer.Option(
        4096, "--max-tokens", "-mt", help="Maximum tokens for the LLM."
    ),
    context_window: int = typer.Option(
        4096, "--context-window", "-cw", help="Context window for the LLM."
    ),
    show_source_document: bool = typer.Option(
        False,
        "--show-source-docs",
        "-ssd",
        help="Show the source document for the response.",
    ),
):
    neogpt = NeoGPT()

    if verbose:
        neogpt.verbose = True

    if build:
        neogpt.build()

    if api_key:
        neogpt.llm.api_key = api_key

    if api_url:
        neogpt.llm.api_url = api_url

    if model:
        neogpt.llm.model = model

    if context_window:
        neogpt.llm.context_window = context_window

    if max_tokens:
        neogpt.llm.max_tokens = max_tokens

    if temperature:
        neogpt.llm.temperature = temperature

    if server:
        # Code to start the NeoGPT API server
        typer.echo("\n\nStarting the NeoGPT API server...")
        typer.echo(
            "\n/v1/chat endpoint is available at http://127.0.0.1:8000/v1/chat (POST)"
        )
        neogpt.server()
        return

    if playground:
        # Code to start the NeoGPT Playground
        typer.echo("Starting the NeoGPT Playground...")
        neogpt.playground()
        return

    if conversations:
        # Display past conversation history
        conversation_navigator()

    neogpt.chat()


if __name__ == "__main__":
    app()
