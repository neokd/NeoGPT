from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

# hf = HuggingFacePipeline.from_model_id(
#     model_id="TinyLlama/TinyLlama-1.1B-Chat-v0.6",
#     task="text-generation",
#     pipeline_kwargs={"max_new_tokens": 10},
#     device=0,  # -1 for CPU
#     batch_size=2,
#     model_kwargs={
#         "cache_dir": "/Users/kuldeep/Project/NeoGPT/neogpt/models"
#     }
# )

from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, TextStreamer
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v0.6"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=8096, streamer = TextStreamer(tokenizer))
hf = HuggingFacePipeline(pipeline=pipe, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
from langchain.prompts import PromptTemplate

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate.from_template(template)

chain = prompt | hf

question = "Who is the prime minister of india"

print(chain.invoke({"question": question}))