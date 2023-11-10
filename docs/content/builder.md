# __Builder 👷__

### Building Database 🛠️

[Builder](https://github.com/neokd/NeoGPT/blob/main/neogpt/builder.py) is a script to build the vector database for NeoGPT. Currently it support 2 vector databases:

-   Chroma

-   FAISS

### Specifying the Database Type (CLI)

By default, the builder script will build a database using the Chroma database type. To build a database using the FAISS database type, run the builder script with the `--db` flag:

To build a database using the Chroma database type (default):
```bash title="Terminal"
   python neogpt/builder.py --db Chroma
```

To build a database using the FAISS database type:
```bash title="Terminal"
   python neogpt/builder.py --db FAISS
```

### Supported file formats

The NeoGPT database builder supports a range of document formats, each associated with a specific loader that processes and includes the content from these documents in the database. The following document formats are supported:

#### General Document Formats:

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

#### Chat Documents:

   - **.txt (Whatsapp):** WhatsAppLoader

#### Code Documents:

   - **.py (Python):** Language.PYTHON

   - **.cpp (C++):** Language.CPP

   - **.go (Go):** Language.GO

   - **.java (Java):** Language.JAVA

   - **.kt (Kotlin):** Language.KOTLIN

   - **.js (JavaScript):** Language.JS

   - **.ts (TypeScript):** Language.TS

   - **.php (PHP):** Language.PHP

   - **.proto (Protocol Buffer):** Language.PROTO

   - **.rst (reStructuredText):** Language.RST

   - **.ruby (Ruby):** Language.RUBY

   - **.rs (Rust):** Language.RUST

   - **.scala (Scala):** Language.SCALA

   - **.swift (Swift):** Language.SWIFT

   - **.markdown (Markdown):** Language.MARKDOWN

   - **.latex (LaTeX):** Language.LATEX

   - **.html (HTML):** Language.HTML

   - **.sol (Solidity):** Language.SOL

   - **.cs (C#):** Language.CSHARP

   - **.cobol (COBOL):** Language.COBOL

!!! info "Note"
      For programming languages, we have been implemented to read the file content and store it as a document in the database. This ensures that the content of code files is processed appropriately, allowing NeoGPT to understand and respond to code-related queries.

### Test data

For testing purposes, we have included 2 papers and 1 youtube video in the `neogpt/documents` folder. 

The database is built using 2 papers and 1 youtube video: 

- [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf)

- [HuggingGPT](https://arxiv.org/pdf/2303.17580.pdf)

- [22 AI News EXPLAINED!!!](https://www.youtube.com/watch?v=BPknz-hCnec)


### Folder Structure

```plaintext title="Folder Structure"
neogpt
   ├── builder.py
   │   ├── db
   │   │   ├── chroma/
   │   │   └── faiss/
   │   ├── logs
   │   │   ├── builder.log
   │   ├── modules
   │   │   ├── __init__.py
   │   │   ├── load_chats.py
   │   │   ├── load_code.py
   │   │   ├── load_docs.py
   │   │   └── load_web.py

```

### Adding Your Own Data

To add your own data to the NeoGPT database, follow these steps:

1. Prepare your local documents or content in one of the supported formats mentioned above. (Multiple formats can be used at the same time.)

2. Place your data in the `neogpt/documents` folder within your NeoGPT project directory.

3. Run the builder script by executing the following command in your terminal or command prompt:

```bash title="Terminal"
   python neogpt/builder.py
```

!!! info "Note"
      It will take some time to build the database depending on the number of documents and the size of the documents.

To add youtube videos, refer below [section](#adding-urls-to-the-database)

A folder named `neogpt/db` will be created in your NeoGPT project directory. This folder will contain the database files.


### Adding URL's to the Database

To include URL's in the NeoGPT database, follow these steps:

1. Create a file `builder.url` in the `neogpt/documents` folder within the project directory.

2. Add the URLs to the `builder.url` file, one URL per line.
    Example:
    ```plaintext title="builder.url"
      https://www.youtube.com/watch?v=VideoID1
      https://www.youtube.com/watch?v=VideoID2
      https://neokd.github.io/NeoGPT/
    ```
   You can include URLs from various sources, not limited to YouTube videos.

3. Run the builder script by executing the following command in your terminal or command prompt:
    
```bash title="Terminal"
python neogpt/builder.py
```

If you want to extract the child pages of a URL (for non-YouTube URLs), you can use the `--recursive` flag. The builder script uses `WebBaseLoader` by default, which extracts only the root or specified domain of the URL. To extract child pages, run the builder script with the `--recursive` flag:

```bash title="Terminal"
python neogpt/builder.py --recursive
```

### Adding Chat Data to the Database

#### WhatsApp

To add WhatsApp chat data to the NeoGPT database, follow these steps:

1. Export the chat from WhatsApp.

2. Move the exported chat file to the `neogpt/documents` folder within the project directory.

3. Run the builder script by executing the following command in your terminal or command prompt:

```bash title="Terminal"
python neogpt/builder.py
```


!!! tip "Tip"
      
      You can add all the supported file formats to the `neogpt/documents` folder and run the builder script. The builder script will automatically detect the file format and process the content accordingly.