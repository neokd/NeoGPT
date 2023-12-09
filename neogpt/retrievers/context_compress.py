import warnings

from langchain.chains import RetrievalQA
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema.output_parser import StrOutputParser

from neogpt.prompts.prompt import get_prompt


def context_compress(llm, db, persona: str = "default"):
    retriever = db.as_retriever()
    prompt, memory = get_prompt(persona=persona)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    compressor = LLMChainExtractor.from_llm(
        llm, llm_chain_kwargs={"output_parser": StrOutputParser()}
    )
    compress_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=compress_retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt, "memory": memory},
        return_source_documents=True,
    )
    return chain
