# NeoGPT 🚀

> [!NOTE]
> Looking for the documentation? Check out the [docs](https://neokd.github.io/NeoGPT/).

Say goodbye to boring interactions with documents and YouTube videos. NeoGPT is your trusted companion to chat with local documents and lengthy YouTube videos effortlessly. Perfect for professionals, developers, researchers, and enthusiasts.

![NeoGPT Gif](https://github.com/neokd/NeoGPT/assets/71772185/82d5c63d-81b5-4b45-95d4-53641016bfdc)


<br/>

Note: NeoGPT is continuously evolving. Your feedback shapes its future.

Join our [Discord](https://discord.gg/qNqjsGuCTG) community to stay up to date with the latest developments.

# Table of Contents
- [Getting Started](#getting-started)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

1. **Installation:** Clone this repository and install the necessary dependencies.

   ```
   git clone https://github.com/neokd/NeoGPT.git
   cd NeoGPT
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

    Currently the database is built using 2 papers and 1 youtube video:
    - [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf)
    - [HuggingGPT](https://arxiv.org/pdf/2303.17580.pdf)
    - [22 AI News EXPLAINED!!!](https://www.youtube.com/watch?v=BPknz-hCnec)


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

Sure, here are the top 4 features from the provided content:

- **Hybrid RAG (Keyword based and Semantic Search) 🕵️‍♂️📂:**
   NeoGPT supports a Hybrid Retriever that combines both keyword-based and semantic search functionalities. This allows users to perform more nuanced and context-aware searches, enhancing the accuracy and relevance of retrieved information.

- **Docker Support 🐳:**
   NeoGPT is designed to be Docker-compatible, providing users with the flexibility and convenience of containerization. This ensures easy deployment and compatibility across various environments, streamlining the setup process for users.

- **User Interface 💻 (Streamlit):**
   The inclusion of a user-friendly command-line interface (CLI) along with a Streamlit-based User Interface (UI) enhances the accessibility of NeoGPT. This dual-interface approach caters to users with different technical backgrounds, making interactions more seamless.

- **Agent-based Chatbot 🤖:**
   NeoGPT introduces an agent-based chatbot system, allowing users to interact with specialized agents tailored for different purposes. This feature enhances the versatility of NeoGPT, enabling it to cater to a wide range of user needs and use cases.



## Contributing
We welcome contributions to NeoGPT! If you have ideas for new features or improvements, please open an issue or submit a pull request. For more information, see our [contributing guide](CONTRIBUTING.md).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Let's innovate together! 🤖✨
