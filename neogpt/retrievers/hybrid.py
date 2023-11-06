from langchain.chains import RetrievalQA
from langchain.retrievers import BM25Retriever, EnsembleRetriever

from neogpt.prompts.prompt import get_prompt


def hybrid_retriever(db, llm, persona="default"):
    """
    Fn: hybrid_retriever
    Description: The function sets up the hybrid retrieval-based question-answering system.
    Args:
        db (object): The database object
        llm (object): The LLM model object
    return:
        chain (object): The chain object
    """
    prompt, memory = get_prompt(persona=persona)
    # Create a retriever object
    bm_retriever = BM25Retriever.from_texts(db.get())
    local_retriver = db.as_retriever()
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm_retriever, local_retriver], weights=[0.5, 0.5]
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=ensemble_retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt, "memory": memory},
        return_source_documents=True,
    )
    return chain
