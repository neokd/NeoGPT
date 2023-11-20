import logging

from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.utilities import DuckDuckGoSearchAPIWrapper

from neogpt.prompts.prompt import few_shot_prompt, stepback_prompt

search = DuckDuckGoSearchAPIWrapper(max_results=4)


def retriever(query):
    return search.run(query)


def stepback(llm, db):
    general_prompt = few_shot_prompt()
    question_gen = general_prompt | llm | StrOutputParser()
    # question = "was chatgpt around while trump was president?"
    # print(retriever(question_gen.invoke({"question": question})))
    prompt, memory = stepback_prompt()
    retriever = db.as_retriever()
    chain = (
        {
            "normal_context": RunnableLambda(lambda x: x["question"]) | retriever,
            "step_back_context": question_gen | retriever,
            "question": lambda x: x["question"],
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    logging.info("Stepback Prompting Retriever Loaded Successfully")

    return chain
    # return x
