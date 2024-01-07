import logging
import os

from langchain.chains import RetrievalQA
from langchain.retrievers.web_research import WebResearchRetriever
from langchain_community.utilities import GoogleSearchAPIWrapper

from neogpt.prompts.prompt import get_prompt


def web_research(db, llm, persona="default"):
    """
    Fn: web_research
    Description: The function sets up the web retrieval-based question-answering system.
    Args:
        db (object): The database object
        llm (object): The LLM model object
    return:
        chain (object): The chain object
    Note: Web Research Retriever works only with Google Search API and Faiss DB.
    """
    try:
        os.environ["GOOGLE_CSE_ID"] = os.environ.get("GOOGLE_CSE_ID")
        os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
    except Exception as e:
        logging.info(
            "Could not load the environment variables for Google Search API" + e
        )

    try:
        prompt, memory = get_prompt(persona=persona)

        retriever = WebResearchRetriever.from_llm(
            vectorstore=db, llm=llm, search=GoogleSearchAPIWrapper()
        )

        chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt, "memory": memory},
            return_source_documents=True,
        )
        logging.info("Loaded Web Retriever Successfully 🔍")
    except Exception as e:
        logging.info(f"Error {e}")

    return chain
