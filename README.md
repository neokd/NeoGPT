<div align="center">
  <!-- <img src="https://github.com/neokd/NeoGPT/assets/71772185/82d5c63d-81b5-4b45-95d4-53641016bfdc" alt="NeoGPT Gif" width="500"/> -->
  
<h1 style="font-size: 3em;">NeoGPT 🚀</h1>

  [![GitHub license](https://img.shields.io/github/license/neokd/NeoGPT?style=flat-round&color=blue&logo=github)](https://github.com/neokd/NeoGPT/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/neokd/NeoGPT?style=flat-round&color=green&logo=github)](https://github.com/neokd/NeoGPT/issues)
[![GitHub stars](https://img.shields.io/github/stars/neokd/NeoGPT?style=flat-round&color=yellow&logo=github)](https://github.com/neokd/NeoGPT/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/neokd/NeoGPT?style=flat-round&color=orange&logo=github)](https://github.com/neokd/NeoGPT/network)
[![Google Collab](https://img.shields.io/badge/Colab-F9AB00?style=flat-round&logo=googlecolab&labelColor=525252)](https://colab.research.google.com/drive/1ngzHdvoHfbSXZaeW5dBA__W4oHGLTQhV?usp=sharing)


</div>

> Currently We are in the development phase and are in progress of removing langchain as a dependency from the existing codebase. We are also working on adding more features to the CLI .

<div align="center">

<span>
        <a href="https://docs.neogpt.dev/introduction">Documentation</a>
        <span> | </span>
        <a href="https://discord.gg/qNqjsGuCTG">Discord</a>
</span>
<div>
<br/>
<img src="https://github.com/neokd/NeoGPT/blob/f04841e9afbac5bf426aca3619cd86a464da4932/docs/assets/intro.png?raw=true" alt="Intro Image"/>
</div>
</div>
<br/>

```bash
pip install neogpt
```
> Not working? Read our setup guide [here](https://docs.neogpt.dev/installation)

```bash
$ neogpt
```

# Introduction
NeoGPT is an AI assistant that transforms your local workspace into a powerhouse of productivity from your CLI. With features like code interpretation, multi-RAG support, vision models, and LLM integration, NeoGPT redefines how you work and create. Join the revolution and experience a new era of efficiency with NeoGPT.



NeoGPT is continuously evolving, and your feedback shapes its future. Join our [Discord community](https://discord.gg/qNqjsGuCTG) to stay up to date with the latest developments.


# Table of Contents
- [Getting Started](#getting-started)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

1. **Installation:** Clone this repository and install the necessary dependencies.


    ```
      git clone https://github.com/neokd/NeoGPT.git
      cd NeoGPT/neogpt
      pip install -r requirements.txt
    ```

2. **Building Database** Currently NeoGPT supports local files and Youtube videos. To build the database add your local files to the documents directory and URL in the `builder.url` file. Then run the builder script.

    ```python
       python main.py --build
    ```
    This will create a database file in the `neogpt/db` folder. You can also specify the database to use by using `--db` flag.
    Supported databases are:
    - `Chroma` (default)
    - `FAISS`

    Currently the database is built using 2 papers as reference:
    - [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf)
    - [HuggingGPT](https://arxiv.org/pdf/2303.17580.pdf)


3. **Run NeoGPT:** Run the CLI to start using NeoGPT. Requires `Python v3.10`. You can use the `--help` flag to view the available commands and options.
    ```bash
    python main.py
    ```
    You can also use `--ui` flag to run the Streamlit UI.
    ```bash
    python main.py --ui
    ```

4. **Project Documentation:**
    To view the project documentation, run the following command in your terminal or command prompt (Development ⚠️)
    ```bash
    cd docs
    npm i mintlify
    mintlify dev
    ```
    

## Features

- **Code Interpreter:**
    Execute code seamlessly in your local environment with our Code Interpreter. Enjoy the convenience of real-time code execution, all within your personal workspace.

- **Multi RAG Support:**
    NeoGPT supports multiple RAG techniques, enabling you to choose the most suitable model for your needs. It includes local RAG, ensemble RAG, web RAG, and more. 🧠📚

- **Vision:**
   Explore a new dimension as NeoGPT supports vision models like bakllava and llava, enabling you to chat with images using Ollama. 🖼️👁️🧠

- **LLM 🤖:**
   NeoGPT supports multiple LLM models, allowing users to interact with a variety of language models. We support LlamaCpp, Ollama, LM Studio, OpenAI, and Togerther Ai. 🤖🧠📚


## Quick Start

```bash
pip install https://github.com/neokd/NeoGPT/releases/download/v0.1.0/neogpt-0.1.0-py3-none-any.whl
```

## Terminal

After installing the package, you can run the CLI by typing the following command in your terminal.

```bash
$ neogpt
```

## Python

```python
from neogpt import db_retriever

chain = db_retriever()

chain.invoke("What operating system are we on?")
```

## Commands


### Code Interpreter
To use the Interpreter, type the following command in your terminal.

```bash
$ neogpt --interpreter
```

### Build Vector Database
To build the vector database, type the following command in your terminal.

```bash
$ neogpt --build
```

### Run Streamlit UI
To run the Streamlit UI, type the following command in your terminal.

```bash
$ neogpt --ui
```

### Change Your LLM

#### Offline LLM

To change your LLM, type the following command in your terminal.

```bash
$ neogpt --model ollama/bakllava
```
#### Online LLM

To change your LLM, type the following command in your terminal.

> Warning: Add your API key to the `.env` file before running the command.

```bash
$ neogpt --model together/mistralai/Mistral-7B-Instruct-v0.2
```

## Magic Commands


- 🔄 `/reset` - Reset the chat session
- 🚪 `/exit` - Exit the chat session
- 📜 `/history` - Print the chat history
- 💾 `/save` - Save the chat history to a `neogpt/conversations`
- 📋 `/copy` - Copy the last response from NeoGPT to the clipboard
- ⏪ `/undo` - Remove the last response from the chat history
- 🔁 `/redo` - Resend the last human input to the model
- 📂 `/load [path]` - Load the saved chat history from the specified file
- 🔖 `/tokens [prompt]` - Calculate the number of tokens for a given prompt
- 📄 `/export` - Export the current settings to the settings/settings.yaml file
- 📜 `/conversations` - List available previously saved conversations.
- 📚 `/source` - Prints the source directory
- 🔍 `/search [keyword]` - Search the chat history for the keyword
- 📋 `/copycode` or `/cc` - Copy the last code block to the clipboard


## Contributing
We welcome contributions to NeoGPT! If you have ideas for new features or improvements, please open an issue or submit a pull request. For more information, see our [contributing guide](CONTRIBUTING.md).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Let's innovate together! 🤖✨


 



























































 
   
