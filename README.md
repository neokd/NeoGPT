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
- [Project Roadmap](#project-roadmap)
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
    ```python
        python main.py
    ```
    You can also use `--ui` flag to run the Streamlit UI.
    ```python
        python main.py --ui
    ```

4. **Project Documentation:**
    To view the project documentation, run the following command in your terminal or command prompt (Development ⚠️)
    ```python
        cd docs
        pip install -r requirements.txt
        mkdocs serve
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

## Project Roadmap

- ☐ **OpenAI LLM Integration:** Enable users to interact with systems that cannot run local models by integrating OpenAI LLM. 🌐

- ☐ **Integration with togetherAI:** Integrate togetherAI services for enhanced user experience and functionality. 🤝

- ☐ **HuggingFace Model Loading Improvement:** Optimize loading of full models from HuggingFace for better performance. 🚀

- ☐ **Image Loading and Storage:** Allow users to load images (base64) to the NeoGPT builder and store them. 🖼️

- ☐ **SQL Database Direct Support:** Integrate direct support for SQL databases in the NeoGPT builder for efficient data management.
 💽

- ☐ **HuggingFace Datasets Support:** Add functionality to load datasets directly from HuggingFace into the NeoGPT builder. 📊

- ☐ **URL Loading Support:** Support loading data from various URLs like HackerNews, Notion DB, etc. 🌐

- ☐ **Social Chats Integration:** Enable loading of data from various social chat platforms (Telegram, Slack, Discord). 💬

- ☐ **Streamlit UI Enhancement:** Improve Streamlit UI with direct integration with `manager.py` for a seamless user experience. 🎨

- ☐ **Agent Variety Expansion:** Introduce more agents with various purposes to cater to diverse NeoGPT user needs. 🤖

- ☐ **Agent Visualization in UI:** Implement visual representation of active agents in the NeoGPT UI with prompts for user clarity. 
👀

- ☐ **Agent Tools and Skills:** Equip NeoGPT agents with tools and skills (Google search, Python REPL) to enhance capabilities. 🛠️

- ☐ **Chat Session Retention:** Store NeoGPT chat sessions in a database to allow users access to past conversations. 🗂️

- ☐ **Voice Support:** Implement voice support using Speech Recognition and Text-to-Speech for NeoGPT user interactions. 🗣️

- ☐ **Documentation Improvement:** Enhance documentation for better understanding, including examples , diagrams, and more. 📖

- ☐ **Writing Assistant Enhancement:** Improve the NeoGPT writing assistant to allow users to write to various file types. ✍️

- ☐ **Text-to-Handwriting in Writing Assistant:** Add the capability for the NeoGPT writing assistant to convert text to handwriting. ✒️

- ☐ **Prompt Improvement:** Implement better prompts for improved results, including Hyper Prompting for task-based prompt input. 🚀

- ☐ **Builder in UI - Retrieved Chunks:** Allow live uploading of files and rebuild the database in the background and allow users to view chunks or documents that were used to generate an answer. 👷

- ☐ **Only LLM Mode:** Add Only LLM mode in CLI and UI allowing users to ignore vector db and chat only with the LLM. 🦾

- ☐ **Autonomous Agent:** Implementing a group of agents that can collaborate to solve a problem. 🤖


## Contributing
We welcome contributions to NeoGPT! If you have ideas for new features or improvements, please open an issue or submit a pull request. For more information, see our [contributing guide](CONTRIBUTING.md).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. Let's innovate together! 🤖✨
