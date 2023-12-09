

# __Run NeoGPT__ ⚡️


## CLI Usage
Run the CLI to start using NeoGPT. The below command will run NeoGPT with default options.

```bash title="Terminal"
python main.py
```

!!! info "Note"
    On first run, NeoGPT will download the model from HuggingFace and build the database. This may take few minutes.

Once everything is set up, you will be greeted with the following message:

![NeoGPT CLI](asset/cli.png)



There are various options available to run the CLI. You can use the `--help` flag to view the available commands and options.

```bash title="Terminal"
python main.py --help
```

### CLI Options

1. `--ui`: You can use `--ui` flag to run the Streamlit UI.
```bash title="Terminal"
python main.py --ui
```

2. `--db`: You can also use `--db` flag to specify the database to use. Currently the supported databases are:
    - `Chroma` (default)

    - `FAISS`
```bash title="Terminal"
python main.py --db FAISS
```

3. `--persona`: You can also use `--persona` flag to specify the persona to use. Currently the supported personas are:

    - `DEFAULT`: An helpful assistant that will help you with your queries. (default)

    - `RECRUITER`: An experienced recruiter who finds the best candidates.

    - `ACADEMICIAN`: Engages in in-depth research and presents findings.

    - `FRIEND`: Provides comfort and encouragement as a friend.

    - `ML_ENGINEER`: Explains complex ML concepts in an easy-to-understand manner.

    - `CEO`: Acts as the CEO, making strategic decisions.

    - `RESEARCHER`: Analyzes, synthesizes, and provides insights.
```bash title="Terminal"
python main.py --persona default
```

To know more about personas, refer [here](https://neokd.github.io/NeoGPT/persona/persona/).


4. `--retriever`: You can specify the retriever you want to use in the CLI. Currently the supported retrievers are:
    - Local Retriever (default)

    - Web Research Retriever (Requires Google API Key refer [here](https://neokd.github.io/NeoGPT/advance/search/))

    - Hybrid Retriever (Ensemble Retriever)

    - SQL Retriever (Experimental)

    - Context Compressor Retriever

    - Stepback Prompting Retriever (RAG + DuckDuckGo Search + Stepback Prompting)
```bash title="Terminal"
python main.py --retriever local
```

    You can read more about retrievers in the retriever [section](https://neokd.github.io/NeoGPT/retrievers/local/).


5. `--build`: You can use `--build` flag to build the database. This will build the database using the files in `neogpt/documents` folder.
    Basically it will run the `builder.py` script. You can read more about the builder [here](https://neokd.github.io/NeoGPT/builder/).
```bash title="Terminal"
python main.py --build
```

6. `--show_source`: You can use `--show_source` flag to show the source of the retrieved document. This will show the documents that are retrieved from the database and fed into the LLM
```bash title="Terminal"
python main.py --show_source
```

7. `--model_type` : You can use `--model_type` flag to specify how you want to load the model. Currently the supported LLM's are:

    - `LLamaCpp` (default)
    - `Ollama`
    - `HuggingFace`
```bash title="Terminal"
python main.py --model_type mistral
```

8. `--verbose`: You can use `--verbose` flag to enable verbose mode. This will print the logs to the terminal.
```bash title="Terminal"
python main.py --verbose
```

9. `--debug`: You can use `--debug` flag to enable debug mode. This will print the debug logs to the terminal.
```bash title="Terminal"
python main.py --debug
```

10. `--log`: You can use `--log` flag to log the output to a file. This will log the output to `logs/neogpt.log` file.
```bash title="Terminal"
python main.py --log
```

11. `--recursive`: You can use `--recursive` flag to extract the child pages of a URL (for non-YouTube URLs). The builder script uses `WebBaseLoader` by default, which extracts only the root or specified domain of the URL. To extract child pages, run the builder script with the `--recursive` flag:
```bash title="Terminal"
python main.py --recursive
```
    !!! warning "Note"
        Use `--recursive` with the `--build` flag to extract child pages of a URL.

12. `--write` : You can use `--write` flag to write the output to a file. This will write the output to specified file. 
```bash title="Terminal"
python main.py --write output.txt
```

13. `--version`: You can use `--version` flag to view the version of NeoGPT.
```bash title="Terminal"
python main.py --version
```

## Streamlit UI

You can also use the Streamlit UI to interact with NeoGPT. To run the Streamlit UI, execute the following command in your terminal or command prompt:

```bash title="Terminal"
python main.py --ui
```

This will start the Streamlit UI in your browser, if it doesn't open automatically, you can open it manually by going to `http://localhost:8501` in your browser.

![Streamlit UI NeoGPT](./asset/ui.png)


!!! warning "Note"
    The Streamlit UI is still in development. It only supports the `Local Retriever` for now.
