import logging
from .load_llm import load_model
import streamlit as st
from langchain.chains import RetrievalQA
from .vectorstore.chroma import ChromaStore
from .prompts.prompt import get_prompt

@st.cache_resource(show_spinner=True)
def create_chain():
    with st.spinner(text="Loading the model"):
        db = ChromaStore()
        logging.info(f"Loaded Chroma DB Successfully.")
        st.chat_message(f"Loaded Chroma DB Successfully.")
        retriever = db.as_retriever()
        # Load the LLM model
        llm = load_model('cpu', model_id='TheBloke/Mistral-7B-Instruct-v0.1-GGUF', model_basename='mistral-7b-instruct-v0.1.Q4_K_M.gguf', LOGGING=logging)
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

def run_ui():
    st.title("NeoGPT Bot 🤖")

    # initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    #Display chat message from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input('Hey! how can I help you?')
    # React to user input
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = chain(prompt, return_only_outputs=True)["result"]

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    # run this file
    run_ui()