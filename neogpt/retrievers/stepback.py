"""
    
"""
from langchain.schema.output_parser import StrOutputParser
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from neogpt.prompts.prompt import few_shot_prompt, stepback_prompt
from langchain.chains import RetrievalQA
import logging

search = DuckDuckGoSearchAPIWrapper(max_results=4)

def duckduckgo_search(query):
    return search.run(query)


def stepback(llm,db):
    general_prompt = few_shot_prompt()
    x = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever()
    )
    




    logging.info("Stepback Prompting Retriever Loaded Successfully")
    
    



    

