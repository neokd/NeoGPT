# __Builder 👷__

### Building Database 🛠️

[Builder](https://github.com/neokd/NeoGPT/blob/main/builder.py) is a script to build the vector database for NeoGPT. Currently it support 2 vector databases:

-   Chroma
-   FAISS

### Test data

For testing purposes, we have included 2 papers and 1 youtube video in the `neogpt/documents` folder. 

The database is built using 2 papers and 1 youtube video: 

- [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf)
- [HuggingGPT](https://arxiv.org/pdf/2303.17580.pdf)
- [22 AI News EXPLAINED!!!](https://www.youtube.com/watch?v=BPknz-hCnec)


### Supported file formats

The NeoGPT database builder supports a range of document formats, each associated with a specific loader that processes and includes the content from these documents in the database. The following document formats are supported:

- **.pdf (PDF):** PDFMinerLoader
- **.txt (Text):** TextLoader
- **.csv (CSV):** CSVLoader
- **.html (HTML):** UnstructuredHTMLLoader
- **.tsv (TSV):** UnstructuredTSVLoader
- **.eml (Email):** UnstructuredEmailLoader
- **.epub (eBook):** UnstructuredEPubLoader
- **.xls (Excel):** UnstructuredExcelLoader
- **.xlsx (Excel):** UnstructuredExcelLoader
- **.pptx (PowerPoint):** UnstructuredPowerPointLoader
- **.ppt (PowerPoint):** UnstructuredPowerPointLoader
- **.docx (Word Document):** UnstructuredWordDocumentLoader
- **.doc (Word Document):** UnstructuredWordDocumentLoader
- **.md (Markdown):** UnstructuredMarkdownLoader
- **.json (JSON):** JSONLoader
- **.py (Python):** TextLoader

Also it supports youtube videos.

### Adding Your Own Data

To add your own data to the NeoGPT database, follow these steps:

1. Prepare your local documents or content in one of the supported formats mentioned above. (Multiple formats can be used at the same time.)

2. Place your data in the `neogpt/documents` folder within your NeoGPT project directory.

3. Run the builder script by executing the following command in your terminal or command prompt:

```bash title="Terminal"
   python builder.py
```

!!! info "Note"
      It will take some time to build the database depending on the number of documents and the size of the documents.

To add youtube videos, refer below [section](#adding-youtube-videos) for more details.

A folder named `neogpt/db` will be created in your NeoGPT project directory. This folder will contain the database files.

### Specifying the Database Type (CLI)

By default, the builder script will build a database using the Chroma database type. To build a database using the FAISS database type, run the builder script with the `--db` flag:

To build a database using the Chroma database type (default):
```bash title="Terminal"
   python builder.py --db Chroma
```

To build a database using the FAISS database type:
```bash title="Terminal"
   python builder.py --db FAISS
```

### Adding YouTube Videos

To add YouTube videos to the NeoGPT database, follow these steps:

1. Create a file `builder.url` in the `neogpt/documents` folder within the project directory.
2. Add the YouTube video URLs to the `builder.url` file, one URL per line.
    Example:
    ```plaintext title="builder.url"
        https://www.youtube.com/watch?v=VideoID1
        https://www.youtube.com/watch?v=VideoID2
        https://www.youtube.com/watch?v=VideoID3
    ```
3. Run the builder script by executing the following command in your terminal or command prompt:
    
```bash title="Terminal"
python builder.py
```

Enjoy chatting with NeoGPT using the content from the added YouTube videos .

