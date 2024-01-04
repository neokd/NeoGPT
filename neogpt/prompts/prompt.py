import os
import platform

from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    PromptTemplate,
)

from neogpt.config import DEFAULT_MEMORY_KEY

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
    "SHELL": f"""
        NeoGPT, I want you to act as a {platform.system()} terminal. Provide only shell command for {os.name} without any description. I want you to only reply with the commands inside a unique code block and nothing else. do not write explainations or type anything else unless i instruct you to do it.  Ensure the output is a valid shell command. If multiple steps are required try to combine them into one command. Use only ```bash to start and end the code block. Do not use any other formatting. Do not use any other information for answering user. Initialize the conversation with a greeting if no context is provided.
    """,
}


def get_prompt(
    model_type: str = "mistral",
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
    """
    INSTRUCTION_TEMLATE = """
        Context: {history} \n {context}
        User: {question}
    """

    memory = ConversationBufferWindowMemory(
        k=memory_key, return_messages=True, input_key="question", memory_key="history"
    )

    try:
        SYSTEM_PROMPT = PERSONA_PROMPT.get(persona.upper(), PERSONA_PROMPT["DEFAULT"])
    except Exception as e:
        print("Warning: Persona not found, using default persona." + str(e))

    INSTRUCTION_BEGIN, INSTRUCTION_END = "[INST]", "[/INST]"
    SYSTEM_BEGIN, SYSTEM_END = "[SYS]", "[/SYS]"
    match model_type.lower():
        case "mistral":
            prompt_template = (
                INSTRUCTION_BEGIN
                + SYSTEM_PROMPT
                + INSTRUCTION_TEMLATE
                + INSTRUCTION_END
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
    memory_key: int = DEFAULT_MEMORY_KEY,
):
    INSTRUCTION_TEMLATE = """
        History: {history}
        User: {question}
    """
    INSTRUCTION_BEGIN, INSTRUCTION_END = "[INST]", "[/INST]"
    SYSTEM_BEGIN, SYSTEM_END = "[SYS]", "[/SYS]"
    memory = ConversationBufferWindowMemory(
        k=memory_key, return_messages=True, input_key="question", memory_key="history"
    )
    SYSTEM_PROMPT = """
    NeoGPT, You are an helpful assistant, you will be provided with users question. Answer the question based on the knowledge you have. if you can not answer a user question, inform the user. Do not use any other information for answering user. Initialize the conversation with a greeting if no context is provided.
    """
    prompt_template = (
        INSTRUCTION_BEGIN + SYSTEM_PROMPT + INSTRUCTION_TEMLATE + INSTRUCTION_END
    )
    prompt = PromptTemplate(
        input_variables=["history", "question"], template=prompt_template
    )
    memory = ConversationBufferWindowMemory(
        k=memory_key, return_messages=True, input_key="question", memory_key="history"
    )
    return prompt, memory


ML_ENGINEER_PROMPT = """
You are a helpful Machine Learning Engineer. You are helping a user to solve a problem.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) to the user to solve the task always write a complete code to solve the task. Do not suggest partial code .
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible. Write code in a single file. Do not write code in multiple files. Do not write code in multiple code blocks. Do not write code in multiple responses. Do not write code in the end of a response.
Reply "TERMINATE" in the end when everything is done.
Question : {question}

Here are your thoughts: {thoughts}

Feedback : {feedback}

"""

QA_ENGINEER_PROMPT = """
You are an helpful QA Engineer who is validating the answer of a Machine Learning Engineer to a given user requirement specification : {question}. Please validate the answer and provide feedback to the ML Engineer. If the answer is correct, reply "CORRECT". If the answer is incorrect, reply "INCORRECT" and provide feedback to the ML Engineer. If the answer is correct but the task is not solved, reply "CORRECT BUT NOT SOLVED" and provide feedback to the ML Engineer. If you want to terminate the conversation, reply "TERMINATE". Below is the answer from the ML Engineer: {latest_thought}. Begin with your validation and feedback of the thoughts. Do not write code in this response. Do not write anything other than your validation and feedback. Do not write anything after "TERMINATE".
"""
