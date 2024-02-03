import os

from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
)

from neogpt.config import DEFAULT_MEMORY_KEY, MODEL_NAME

# The prompts are taken from https://github.com/f/awesome-chatgpt-prompts. Thanks to the author for the amazing work.


# Persona Prompts for Chatbot
#    - Default (Default Persona of an Assistant)
#    - Recruiter (Persona of a Recruiter recruiting for a job)
#    - Academician (Persona of an Academician who is expert in a field)
#    - Friend (Persona of a Friend who is supportive)
#    - ML Engineer (Persona of a Machine Learning Engineer)
#    - CEO (Persona of a Chief Executive Officer of a company)
#    - Researcher (Persona of a Researcher who is expert in research and analysis)

PERSONA_PROMPT = {
    "DEFAULT": """
        NeoGPT ,You are a helpful assistant, you will use the provided context to answer user questions.Read the given context before answering questions and think step by step. If you can not answer a user  question based on the provided context, inform the user. Do not use any other information for answering user. Initialize the conversation with a greeting if no context is provided. Do not generate empty responses.
    """,
    "RECRUITER": """
        NeoGPT,I want you to act as a recruiter. I will provide some information about job openings, and it will be your job to come up with strategies for sourcing qualified applicants. This could include reaching out to potential candidates through social media, networking events or even attending career fairs in order to find the best people for each role. Remember that you are representing our company, so make sure to be professional and courteous at all times.
    """,
    "ACADEMICIAN": """
        NeoGPT,I want you to act as an academician. You will be responsible for researching a topic of your choice and presenting the findings in a paper or article form. Your task is to identify reliable sources, organize the material in a well-structured way and document it accurately with citations.
    """,
    "FRIEND": """
        NeoGPT,As a trusted friend, your role is to provide unwavering support during life's challenges. You'll listen to what's happening in my life and offer helpful and comforting words. No explanations are needed; your focus is on providing positive and meaningful support to help me stay focused and positive.
    """,
    "ML_ENGINEER": """
        NeoGPT,I want you to act as a machine learning engineer. I will write some machine learning concepts and it will be your job to explain them in easy-to-understand terms. This could contain providing step-by-step instructions for building a model, demonstrating various techniques with visuals, or suggesting online resources for further study. start with a greeting if no context is provided.
    """,
    "CEO": """
        NeoGPT,I want you to act as a Chief Executive Officer for a hypothetical company. You will be responsible for making strategic decisions, managing the company's financial performance, and representing the company to external stakeholders. You will be given a series of scenarios and challenges to respond to, and you should use your best judgment and leadership skills to come up with solutions. Remember to remain professional and make decisions that are in the best interest of the company and its employees.
    """,
    "RESEARCHER": """
        NeoGPT,I want you to act as a researcher. You are provided with research documents and data related to a specific topic. Your task is to analyze, synthesize, and provide insights based on the available information. Feel free to ask questions and explore the data to draw meaningful conclusions. Let's dive into the world of research!
    """,
}


def get_prompt(
    persona: str = "default",
    memory_key: int = DEFAULT_MEMORY_KEY,
):
    """
    Fn: get_prompt
    Description: The function returns the prompt and memory for the chatbot.
    Args:
        model_type (str, optional): Model type (mistral, gptq). Defaults to "mistral".
        persona (str, optional): Persona (default, recruiter). Defaults to "default".
        memory_key (int, optional): Memory key. Defaults to DEFAULT_MEMORY_KEY.
    return:
        prompt (PromptTemplate): Returns a PromptTemplate object
        memory (ConversationBufferWindowMemory): Returns a ConversationBufferWindowMemory object
    #"""

    model_name = os.getenv("MODEL_NAME") if os.getenv("MODEL_NAME") else MODEL_NAME

    memory = ConversationBufferWindowMemory(
        k=memory_key, return_messages=True, input_key="question", memory_key="history"
    )

    try:
        SYSTEM_PROMPT = PERSONA_PROMPT.get(persona.upper(), PERSONA_PROMPT["DEFAULT"])
    except Exception as e:
        print("Warning: Persona not found, using default persona." + str(e))

    if (
        "dolphin" in model_name.lower() or "hermes" in model_name.lower()
    ):  # ChatML format
        BEGIN_INSTRUCTION, END_INSTRUCTION = "<|im_start|>", "<|im_end|>"
        SYSTEM_PROMPT = BEGIN_INSTRUCTION + SYSTEM_PROMPT + END_INSTRUCTION

        prompt_template = (
            SYSTEM_PROMPT
            + BEGIN_INSTRUCTION
            + """ Context: {history} \n {context} \n User: {question}"""
            + END_INSTRUCTION
            + BEGIN_INSTRUCTION
            + """ Assistant:"""
        )

    elif "codellama" in model_name.lower():
        BEGIN_INSTRUCTION, END_INSTRUCTION = "[INST]", "[/INST]"
        prompt_template = (
            BEGIN_INSTRUCTION
            + SYSTEM_PROMPT
            + """ Context: {history} \n {context} \n User: {question}"""
            + END_INSTRUCTION
        )

    elif "tinyllama" in model_name.lower():
        SYSTEM = "<|system|>"
        ASSISTANT = "<|assistant|>"
        USER = "<|user|>"

        prompt_template = (
            SYSTEM
            + SYSTEM_PROMPT
            + """</s>"""
            + USER
            + """Context {context} {history} </s> {question} </s>"""
            + ASSISTANT
        )

    elif "deepseek" in model_name.lower():
        INSTRUCTION = "### Instruction: "
        RESPONSE = " ### Response: "

        prompt_template = (
            SYSTEM_PROMPT
            + INSTRUCTION
            + """{history} \n {context} \n {question}"""
            + RESPONSE
        )

    elif "mistral" in model_name.lower() or "mixtral" in model_name.lower():
        BEGIN_INSTRUCTION, END_INSTRUCTION = "[INST]", "[/INST]"

        prompt_template = (
            BEGIN_INSTRUCTION
            + SYSTEM_PROMPT
            + """ Context: {history} \n {context}  \n User: {question}"""
            + END_INSTRUCTION
        )

    elif "llama" in model_name.lower():
        BEGIN_INSTRUCTION, END_INSTRUCTION = "[INST]", "[/INST]"
        BEGIN_SYSTEM, END_SYSTEM = "<<SYS>>\n", "\n<</SYS>>\n\n"
        SYSTEM_PROMPT = BEGIN_SYSTEM + SYSTEM_PROMPT + END_SYSTEM

        prompt_template = (
            BEGIN_INSTRUCTION
            + SYSTEM_PROMPT
            + """ Context: {history} \n {context} \n User: {question}"""
            + END_INSTRUCTION
        )

    elif "phi" in model_name.lower():
        INSTRUCTION = "Instruct:"
        OUTPUT = " Output:"

        prompt_template = (
            INSTRUCTION
            + SYSTEM_PROMPT
            + """{history} \n {context} \n {question}"""
            + OUTPUT
        )

    elif "zephyr" in model_name.lower():
        SYSTEM = "<|system|>"
        USER = "<|user|>"
        ASSISTANT = "<|assistant|>"

        prompt_template = (
            SYSTEM
            + SYSTEM_PROMPT
            + """</s>"""
            + USER
            + """ {history} \n {context} \n {question}"""
            + ASSISTANT
        )
    # Multi - Modal
    elif "llava" in model_name.lower():
        USER = "USER:"
        IMAGE = "<image>"
        ASSISTANT = "ASSISTANT:"

        prompt_template = (
            SYSTEM_PROMPT
            + USER
            + IMAGE
            + """\n {history} \n {context} \n {question} \n"""
            + ASSISTANT
        )

    elif "obsidian" in model_name.lower():
        BEGIN_INSTRUCTION, END_INSTRUCTION = "<|im_start|>", "<|im_end|>"
        IMAGE = "<image>"

        prompt_template = (
            SYSTEM_PROMPT
            + BEGIN_INSTRUCTION
            + """ Context: {history} \n {context} \n user {question}"""
            + IMAGE
            + "###"
            + BEGIN_INSTRUCTION
            + """ Assistant:"""
        )
    else:
        prompt_template = (
            SYSTEM_PROMPT + """ Context: {history} \n {context} \n User: {question}"""
        )

    prompt = PromptTemplate(
        input_variables=["history", "context", "question"], template=prompt_template
    )

    return prompt, memory


def few_shot_prompt():
    examples = [
        {
            "input": "Tell me about the history of artificial intelligence.",
            "output": "Explain the historical development of artificial intelligence.",
        },
        {
            "input": "What skills are essential for a data scientist?",
            "output": "List the key skills required for a data scientist role.",
        },
        {
            "input": "Discuss the implications of quantum mechanics in modern physics.",
            "output": "Examine the significance of quantum mechanics in contemporary physics.",
        },
        {
            "input": "Where's a great place to hang out this weekend?",
            "output": "Do you know of any cool spots for the weekend?",
        },
        {
            "input": "Explain the gradient descent algorithm for training neural networks.",
            "output": "Describe the gradient descent algorithm used in neural network training.",
        },
        {
            "input": "What are our revenue projections for the next quarter?",
            "output": "Provide the revenue forecasts for the upcoming quarter.",
        },
        {
            "input": "Can you elucidate the recent developments in quantum computing?",
            "output": "Elaborate on the latest advancements in quantum computing research.",
        },
    ]

    example_prompt = ChatPromptTemplate.from_messages(
        [("human", "{input}"), ("ai", "{output}")]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt, examples=examples
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """I want you to act as a text based web browser browsing an imaginary internet. You should only reply with the contents of the page, nothing else. I will enter a url and you will return the contents of this webpage on the imaginary internet. Don't write explanations.""",
            ),
            few_shot_prompt,
            ("user", "{question}"),
        ]
    )
    return prompt


def stepback_prompt(
    model_type: str = "mistral",
    persona: str = "default",
    memory_key: int = DEFAULT_MEMORY_KEY,
):
    INSTRUCTION_TEMLATE = """
    You are an expert of world knowledge. I am going to ask you a question. Your response should be comprehensive and not contradicted with the following context if they are relevant. Otherwise, ignore them if they are not relevant.

    {normal_context}
    {step_back_context}

    Original Question: {question}
    Answer:
    """
    memory = ConversationBufferWindowMemory(
        k=memory_key, return_messages=True, input_key="question", memory_key="history"
    )

    INSTRUCTION_BEGIN, INSTRUCTION_END = "[INST]", "[/INST]"
    SYSTEM_BEGIN, SYSTEM_END = "[SYS]", "[/SYS]"

    prompt = PromptTemplate(
        input_variables=["normal_context", "step_back_context", "question"],
        template=INSTRUCTION_TEMLATE,
    )

    return prompt, memory


def conversation_prompt(
    persona: str = "default",
    memory_key: int = DEFAULT_MEMORY_KEY,
):
    prompt, memory = get_prompt(persona=persona, memory_key=memory_key)
    prompt.input_variables.pop(0)
    prompt = PromptTemplate.from_template(prompt.template.replace("{context}", ""))
    return prompt, memory
