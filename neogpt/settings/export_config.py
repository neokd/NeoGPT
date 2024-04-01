import os
from datetime import datetime

import toml
import yaml

from neogpt.settings import config


# Extract version info from TOML
def read_pyproject_toml(file_path):
    with open(file_path) as toml_file:
        toml_data = toml.load(toml_file)

    poetry_section = toml_data.get("tool", {}).get("poetry", {})

    # Extracting information
    version = poetry_section.get("version", "")
    authors = poetry_section.get("authors", [])
    license_info = poetry_section.get("license", "")

    return {
        "version": version,
        "authors": authors,
        "license": license_info,
    }


# Export Configuration
def export_config(config_filename="settings.yaml"):
    toml_path = "./pyproject.toml"
    toml_info = read_pyproject_toml(toml_path)
    data = {
        "neogpt": {
            "VERSION": toml_info["version"],
            "ENV": "development",
            "PERSONA": "default",
            "UI": False,
            "EXPORT_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "LICENSE": toml_info["license"],
        },
        "model": {
            "MODEL_NAME": config.MODEL_NAME,
            "MODEL_TYPE": config.MODEL_TYPE,
            "MODEL_FILE": config.MODEL_FILE,
            "EMBEDDING_MODEL": config.EMBEDDING_MODEL,
            "INGEST_THREADS": config.INGEST_THREADS,
            "N_GPU_LAYERS": config.N_GPU_LAYERS,
            "MAX_TOKEN_LENGTH": config.MAX_TOKEN_LENGTH,
            "TEMPERATURE": config.TEMPERATURE,
            "CONTEXT_WINDOW": config.CONTEXT_WINDOW,
        },
        "database": {
            "PARENT_DB_DIRECTORY": os.path.basename(config.PARENT_DB_DIRECTORY),
        },
        "directories": {
            "SOURCE_DIR": os.path.basename(config.SOURCE_DIR),
            "WORKSPACE_DIRECTORY": os.path.basename(config.WORKSPACE_DIRECTORY),
            "MODEL_DIRECTORY": os.path.basename(config.MODEL_DIRECTORY),
        },
        "memory": {
            "DEFAULT_MEMORY_KEY": config.DEFAULT_MEMORY_KEY,
        },
        "logs": {
            "LOG_FOLDER": os.path.basename(config.LOG_FOLDER),
        },
        "pytorch device config": {
            "DEVICE_TYPE": config.DEVICE_TYPE,
        },
    }

    SETTINGS_DIR = os.path.join(config.ROOT_DIR, "settings")
    if not os.path.exists(SETTINGS_DIR):
        os.makedirs(SETTINGS_DIR)

    filepath = os.path.join(SETTINGS_DIR, config_filename)
    if os.path.exists(filepath):
        overwrite = input(
            f"\nFile {filepath} already exists. Do you want to overwrite it? (yes/no): "
        )
        if overwrite.lower() == "yes":
            try:
                with open(filepath, "w") as file:
                    yaml.dump(data, file, sort_keys=False)
                    print(f"\nConfiguration exported to {filepath}")

            except Exception as e:
                print(f"An error occurred during export: {e}")
        else:
            filepath = os.path.join(SETTINGS_DIR, input("Enter a new file name: "))
            if os.path.exists(filepath) or os.path.exists(str(filepath + ".yaml")):
                print(f"\nFile {filepath} already exists.")
                filepath = filepath.removesuffix(".yaml")
                filepath = (
                    f'{filepath}-{datetime.now().strftime("%d-%m-%Y-%H-%M-%S")}.yaml'
                )
            if not filepath.endswith(".yaml"):
                filepath += ".yaml"

            try:
                with open(filepath, "w") as file:
                    yaml.dump(data, file, sort_keys=False)
                    print(f"\nConfiguration exported to {filepath}")

            except Exception as e:
                print(f"An error occurred during export: {e}")
