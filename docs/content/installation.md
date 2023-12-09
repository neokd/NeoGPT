---
title: Installation
---

# __Installation__ 🧑‍💻👩‍💻

This guide will walk you through the process of setting up NeoGPT on your system. NeoGPT is designed to be user-friendly and is compatible with a variety of operating systems.



## __Pre-requisites__
Before you begin, make sure you have the following prerequisites installed on your system:

- Python 3.10 or higher

- Git

- Editor of your choice (VSCode, PyCharm, etc.)

## Installation Steps

You can install NeoGPT by following whichever of the following methods is most convenient for you:

1. [Bash Script](#with-bash-script)

2. [Docker](#with-docker)

3. [Poetry](#with-poetry)

4. [pip](#with-pip)

5. [conda](#with-conda)

### With bash script

It is recommended to use the bash script to install NeoGPT. The bash script will automatically install all the required packages and set up the virtual environment for you. Followed by that it will build the database and run the CLI.

!!! tip "Recommended"

1. Clone the repository using the following command
```bash title="Terminal"
git clone https://github.com/neokd/NeoGPT.git
```

2. Navigate to the root directory of the repository
```bash title="Terminal"
cd NeoGPT
```

3. Run the following command in your terminal or command prompt:
```bash title="Terminal"
bash ./install.sh
```

!!! warning "Note"
    The script will not create any virtual environment. It will use the default python environment. If you want to use a virtual environment, you can create one and activate it before running the script.

### With docker


!!! info "Docker"
    You need to have docker installed on your system to use this method. You can install docker by following the instructions [here](https://docs.docker.com/get-docker/).

1. Clone the repository using the following command
```bash title="Terminal"
git clone https://github.com/neokd/NeoGPT.git
```

2. Navigate to the root directory of the repository
```bash title="Terminal"
cd NeoGPT
```

3. Run the following command in your terminal or command prompt:
```bash title="Terminal"
docker compose up --build
```

4. Run the following command in your terminal or command prompt:
```bash title="Terminal"
docker compose up
```

5. You can now access the UI at http://localhost:8501


### With poetry 

!!! info "Poetry"
    You need to have poetry installed on your system to use this method. You can install poetry by running the following command in your terminal or command prompt:
    ```bash title="Terminal"
    pip install poetry
    ```

1. Clone the repository using the following command
```bash title="Terminal"
git clone https://github.com/neokd/NeoGPT.git
```

2. Navigate to the root directory of the repository
```bash title="Terminal"
cd NeoGPT
```

3. Run the following command in your terminal or command prompt:
```bash title="Terminal"
poetry install
```

4. Run the following command in your terminal or command prompt:
```bash title="Terminal"
    poetry run python main.py
```


### With pip

1. Clone the repository using the following command
```bash title="Terminal"
git clone https://github.com/neokd/NeoGPT.git
```

2. Navigate to the root directory of the repository
```bash title="Terminal"
cd NeoGPT
```

3. Set up a virtual environment and activate it

    For Windows:
    ```powershell title="Terminal"
        python -m venv neogpt-env
        neogpt-env\Scripts\activate
    ```
    For Linux/MacOS:

    ```bash title="Terminal"
        python3 -m venv neogpt-env
        source neogpt-env/bin/activate
    ```

4. Install the required packages
```bash title="Terminal"
pip install -r requirements.txt
```

### With conda

1. Clone the repository using the following command
```bash title="Terminal"
git clone https://github.com/neokd/NeoGPT.git
```

2. Navigate to the root directory of the repository
```bash title="Terminal"
cd NeoGPT
```

3. Set up a virtual environment and activate it
```bash title="Terminal"
conda create -n neogpt-env python=3.10
conda activate neogpt-env
```

4. Install the required packages
```bash title="Terminal"
pip install -r requirements.txt
```


## LLamaCpp

NeoGPT used llama-cpp-python to load the LLM models.

If you want to use BLAS or Metal with llama-cpp you can set appropriate flags:

for BLAS:

```bash title="Terminal"
CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install llama-cpp-python==0.2.11
```

for Metal (macOS only):

```bash title="Terminal"
CMAKE_ARGS="-DLLAMA_METAL=on"  FORCE_CMAKE=1 pip install llama-cpp-python==0.2.11 --no-cache-dir
```
