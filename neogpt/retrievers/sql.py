"""
   SQL retriever
   Refer : https://python.langchain.com/docs/expression_language/cookbook/sql_db
"""

import logging
import os

from colorama import Fore
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

from neogpt.config import SOURCE_DIR


def sql_retriever(llm, persona):
    """
    SQL retriever
    """
    logging.info(
        f"{Fore.YELLOW}Warning: The SQL retriever takes a long time to load. Please be patient 🤖 {Fore.RESET}"
    )

    # Find any .db file in source dir
    db_files = [file for file in os.listdir(SOURCE_DIR) if file.endswith(".db")]
    if len(db_files) > 1:
        raise ValueError(f"More than one .db file found in {SOURCE_DIR}")

    db_file = SOURCE_DIR + "/" + db_files[0]
    # Load the SQL DB
    db = SQLDatabase.from_uri(f"sqlite:///{db_file}")
    # prompt,memory = get_prompt(persona = persona)
    chain = SQLDatabaseChain.from_llm(llm, db)
    logging.info("Loaded the SQL retriever successfully 🤖")
    return chain
