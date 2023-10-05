from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Default System level prompt
SYSTEM_PROMPT = """
        You are a helpful assistant, you will use the provided context to answer user questions.
        Read the given context before answering questions and think step by step. If you can not answer a user  question based on the provided context, inform the user. Do not use any other information for answering user.
"""
# Default memory window size
DEFAULT_MEMORY_KEY = 2

def get_prompt(model_type:str = "mistral"):
    """
        input: model_type
        output: prompt, memory
        desciption: The function streamlines prompt generation for language models, mapping model_type to the appropriate format. It utilizes conversation memory, instruction tags, and model-specific templates, returning a tailored prompt and memory object. This utility enhances context-aware interactions with language models.
    """
    INSTRUCTION_TEMLATE = """
        Context: {history} \n {context}
        User: {question}
    """
    
    memory = ConversationBufferWindowMemory(k=DEFAULT_MEMORY_KEY,return_messages=True,input_key="question", memory_key="history")

    INSTRUCTION_BEGIN, INSTRUCTION_END = "[INST]", "[/INST]"
    SYSTEM_BEGIN, SYSTEM_END = "[SYS]", "[/SYS]"

    match model_type.lower():
        case "mistral":
            prompt_template = INSTRUCTION_BEGIN + SYSTEM_PROMPT + INSTRUCTION_TEMLATE + INSTRUCTION_END

    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
    
    return prompt, memory
        


            



