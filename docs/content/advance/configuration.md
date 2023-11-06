

# __NeoGPT Configuration__

This document outlines various configuration settings for NeoGPT. You can customize these settings to suit your needs.

!!! warning "Note"
    The default configurations are good enough for most use cases. You can skip this document if you don't want to customize the configurations. We don't recommend changing the configurations unless you know what you are doing.   
    
!!! info "Note"
    The configuration file is located at `neogpt/config.py`. You can edit the file to change the configurations.

## Directories

- **Source Directory:** The directory where documents are stored.  
  Default: `neogpt/documents`

- **Model Directory:** The directory for storing models from HuggingFace.  
  Default: `neogpt/models`

- **Parent Database Directory:** The main database directory.  
  Default: `neogpt/db`

- **Chroma Database Directory:** Directory for the Chroma database.  
  Default: `neogpt/db/chroma`

- **FAISS Database Directory:** Directory for the FAISS database.  
  Default: `neogpt/db/faiss`


## Memory and Model

- **Default Memory Key:** The default memory key to remember chat history. 
  Default: `2`

- **Model Name:** The name of the GGUF model.  
  Default: `TheBloke/Mistral-7B-Instruct-v0.1-GGUF`

- **Model File:** The model file to use.  
  Default: `mistral-7b-instruct-v0.1.Q4_K_M.gguf`

- **Embedding Model:** The default embedding model.  
  Default: `sentence-transformers/all-MiniLM-L12-v2`

## Threads and Device

- **Ingest Threads:** The number of threads for document ingestion.  
  Default: `8`

- **Max Token Length:** The maximum token length for the model.  
  Default: `8192`

- **Number of GPU Layers:** Number of layers for GPU compatibility.  
  Default: `40`
  MPS: `1`

- **Device Type:** The device type (cpu, mps, cuda).  
  Default: `cuda`

## Chroma Database Settings

- **Chroma Settings:** Anonymized telemetry and persistence settings.  
    - Anonymized Telemetry: `False`  
    - Is Persistent: `True`

## Reserved File Names

- List of reserved file names.  
  Default: `["builder.url"]`

## Supported Document Extensions

- Supported document formats and their corresponding loaders.  
  Default:
  - `.pdf`: PDFMinerLoader
  - `.txt`: TextLoader
  - `.csv`: CSVLoader
  - ... (other formats)

Read more about the supported document formats [here](../builder.md#supported-file-formats).


## URL Extensions

- Supported URL patterns for ingestion.  
  Default:
  - `.youtube`: YoutubeLoader


## Query and Cost

- **Initial Query Cost:** Initial query cost.  
  Default: `0`

- **Total Cost:** Total cost.  
  Default: `0`

## Logging

- **Log Folder:** The folder for log files.  
  Default: `logs`

- **Log File:** The log file name.  
  Default: `logs/builder.log`


!!! info "Release Note"
    You cannot change config directly from the CLI or UI. We will add support for that in the future releases.