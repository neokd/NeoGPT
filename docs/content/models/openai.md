# __NeoGPT + OpenAI__

OpenAI offers a spectrum of models with different levels of power suitable for different tasks. The list of models is available [here](https://platform.openai.com/docs/models/overview).

!!! warning "Requires OpenAI API Key"
    You need to set the environment variable `OPENAI_API_KEY` to use models from OpenAI. You can get the API key from [here](https://platform.openai.com/api-keys).

## How to use

Follow the steps below to use OpenAI with NeoGPT.

- Get the API key from [here](https://platform.openai.com/api-keys).
- Set the environment variable `OPENAI_API_KEY` to the API key.
- Run the following command to use OpenAI with NeoGPT.

```python
python main.py --model_type openai
```

!!! info "Note"
    Currently, NeoGPT is tested only with `gpt-3.5-turbo` model.

