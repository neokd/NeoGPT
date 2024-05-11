from rich.markdown import Markdown
from rich.rule import Rule

budget = 0


def respond(neogpt):
    """
    This function is to interact with the model and get the response.
    TODO: Implement Budget Manager for paid API. (OpenAI , Together AI) (Additional)
    """
    try:
        msg = ""
        for chunk in neogpt.llm.inference(neogpt.messages):
            if chunk.choices[0].delta.content is not None:
                msg += chunk.choices[0].delta.content
                yield chunk
    except Exception as e:
        print(e)
        yield "An error occurred."

    finally:
        neogpt.messages.append(
            {
                "role": "assistant",
                "type": "message",
                "content": msg,
            }
        )
        #  PASS MESSAGE TO RUN CODE IF ANY v
        neogpt.machine.run(msg)
        # PASS MESSAGE TO RUN CODE IF ANY ^
