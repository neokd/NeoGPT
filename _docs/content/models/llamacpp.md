# __NeoGPT + LLamaCpp__



NeoGPT uses [LLamaCpp](https://github.com/abetlen/llama-cpp-python) to load the LLM models. [LLamaCpp](https://github.com/abetlen/llama-cpp-python) is a python binding for [llama.cpp](https://github.com/ggerganov/llama.cpp). It supports GGUF format to load the LLM models. This enhances the speed and effectiveness of NeoGPT in handling large language models, contributing to a more efficient natural language processing experience.


##  How to Use

```bash title="Terminal"
python main.py --model_type llama
```

By default, NeoGPT uses the `Mistral-7B instruct` model. In order to use other models, follow the instructions below.

### Using Other Models

Run the following command in your terminal or command prompt:

=== "Terminal"
    ```bash title="Terminal"
    export MODEL_NAME="example_model" && export  MODEL_FILE="example_model.gguf"
    ```
=== "Example"
    ```bash title="Terminal"
    export MODEL_NAME="TheBloke/Llama-2-7B-Chat-GGUF" && export  MODEL_FILE="llama-2-7b-chat.Q4_0.gguf"
    ```
    



Make sure to replace `example_model` with the name of the model you want to use and `example_model.gguf` with the name of the model file.





## Tested Models (Q4)

| Model Name           | Model Size | Tested | 
|----------------------|------------|------------|
| Mistral-7B instruct  | 4.1GB      | ✅       |
| Llama 2 &B  | 3.83      | ✅       |


