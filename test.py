from langchain.llms import HuggingFacePipeline
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

llm = HuggingFacePipeline.from_model_id(
    model_id="microsoft/phi-1_5",
    task="text-generation",
    # batch_size=2,  # adjust as needed based on GPU map and model size.
    model_kwargs={"temperature": 0, "max_length": 8192, "cache_dir": "./models/","trust_remote_code":True }
)
from langchain.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | llm

question = "What is electroencephalography?"

print(chain.invoke({"question": question}))