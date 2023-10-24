# The file is currently in development and is not ready for use.
# Run python main.py to interact in the terminal

from vectorstore.chroma import ChromaStore
import logging
import streamlit as st
from prompts.prompt import get_prompt
from langchain.chains import RetrievalQA
import main

st.title('NeoGPT Bot')

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource(show_spinner=True)
def create_chain():
    with st.spinner(text="Loading the model"):
        db = ChromaStore()
        logging.info(f"Loaded Chroma DB Successfully")
        retriever = db.as_retriever()
        # Load the LLM model
        llm = main.load_model('cpu', model_id='TheBloke/Mistral-7B-Instruct-v0.1-GGUF', model_basename='mistral-7b-instruct-v0.1.Q4_K_M.gguf', LOGGING=logging)
        # Prompt Builder Function 
        prompt , memory = get_prompt()
        # Create a retrieval-based question-answering system using the LLM model and the Vector DB
        return RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )

chain = create_chain()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = chain(prompt, return_only_outputs=True)
        st.write(response['result'])

    st.session_state.messages.append({"role": "assistant", "content": response['result']})

