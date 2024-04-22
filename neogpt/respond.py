from neogpt.utils.formatter import MessageFormatter

budget = 0


def respond(neogpt):
    """
    This function is to interact with the model and get the response.
    TODO: Implement Budget Manager for paid API. (OpenAI , Together AI)
    """
    try:
        msg = ""
        for chunk in neogpt.llm.inference(neogpt.messages):
            if chunk.choices[0].delta.content is not None:
                msg += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content
        neogpt.messages.append({"role": "assistant", "type": "message", "content": msg})
    except Exception as e:
        print(e)
        yield "An error occurred."


"""
ChatCompletionChunk(id='chatcmpl-124', choices=[Choice(delta=ChoiceDelta(content=' with', function_call=None, role='assistant', tool_calls=None), finish_reason=None, index=0, logprobs=None)], created=1713691062, model='llama3', object='chat.completion.chunk', system_fingerprint='fp_ollama')


ChatCompletionChunk(id='chatcmpl-a4fa36a7-b9d2-4464-a02d-9aee0e114625', choices=[Choice(delta=ChoiceDelta(content=None, function_call=None, role=None, tool_calls=None), finish_reason='stop', index=0, logprobs=None)], created=1713691230, model='/Users/kuldeep/Projects/NeoGPT/neogpt/models/models--TheBloke--Mistral-7B-Instruct-v0.1-GGUF/snapshots/731a9fc8f06f5f5e2db8a0cf9d256197eb6e05d1/mistral-7b-instruct-v0.1.Q4_K_M.gguf', object='chat.completion.chunk', system_fingerprint=None)

"""
