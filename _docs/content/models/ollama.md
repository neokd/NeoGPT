# __NeoGPT + Ollama__


[Ollama](https://ollama.ai/) allows you to run LLM'S locally. It basically bundles model weights, configuration, and data into a single package, defined by a Modelfile.They have a wide range of models available for download. You can download the models from [here](https://ollama.ai/library). 


!!! warning "Note"
    It only supports MacOS and Linux for now. Windows support is coming soon. 

##  How to Use

Follow the steps below to use Ollama with NeoGPT.

- First, you need to download [Ollama](https://ollama.ai/download). 

- Fetch the model you want to use from [here](https://ollama.ai/library). Using `ollama pull <model family>`

- This will download the most basic version of the model typically (e.g., smallest # parameters and q4_0)

- If the app is running.All of your local models are automatically served on `localhost:11434`

- Set the environment variable `MODEL_NAME` to the name of the model you want to use.

=== "Command" 
    ```bash title="Terminal"
    export MODEL_NAME="example_model"
    ```

=== "Example" 
    ```bash title="Terminal"
    python main.py --model_type ollama
    ```

Make sure to replace `example_model` with the name of the model you want to use. It will be the model you choose from [Ollama](https://ollama.ai/library) Library.


## Tested Models (Q4)

| Model Name           | Model Size | Tested | 
|----------------------|------------|------------|
| Mistral-7B instruct  | 4.1GB      | ✅       |
| Llama 2 &B  | 3.83      | ✅       |

