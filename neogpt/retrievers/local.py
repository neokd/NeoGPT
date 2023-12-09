import logging

from langchain.chains import RetrievalQA

from neogpt.prompts.prompt import get_prompt


def local_retriever(db, llm, persona="default"):
    """
    Fn: local_retriever
    Description: The function sets up the local retrieval-based question-answering system.
    Args:
        db (object): The database object
        llm (object): The LLM model object
    return:
        chain (object): The chain object
    """
    try:
        prompt, memory = get_prompt(persona=persona)
        # Create a retriever object
        local_retriever = db.as_retriever()
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=local_retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt, "memory": memory},
            return_source_documents=True,
        )
        logging.info("Loaded Local Retriever Successfully 🔍")
    except Exception as e:
        logging.info(f"Error {e}")

    return chain
