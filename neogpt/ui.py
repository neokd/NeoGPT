import logging
from neogpt.load_llm import load_model
import streamlit as st
from langchain.chains import RetrievalQA
from neogpt.vectorstore.chroma import ChromaStore
from neogpt.prompts.prompt import get_prompt
from neogpt.config import (
    DEVICE_TYPE, 
    MODEL_NAME,
    MODEL_FILE
)

st.set_page_config(
    page_title="NeoGPT",
    page_icon="🤖",
)


@st.cache_resource(show_spinner=True)
def create_chain():
    with st.spinner(text="Loading the model"):
        
        db = ChromaStore()
        logging.info(f"Loaded Chroma DB Successfully.")
        # st.chat_message(f"Loaded Chroma DB Successfully.")
        retriever = db.as_retriever()
        # Load the LLM model
        llm = load_model(DEVICE_TYPE, model_id=MODEL_NAME, model_basename=MODEL_FILE,ui=True, LOGGING=logging)
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
    
    with st.sidebar:
        st.markdown("# NeoGPT 🤖")
        st.markdown("NeoGPT is an open-source, locally-run Language Model (LLM) 📚 which allows you to chat with documents, YouTube videos,etc. ")
        st.divider()
        st.markdown("## Default Configurations:")
        st.markdown(f"Model: **{MODEL_NAME}**")
        st.markdown(f"Device: **{DEVICE_TYPE}**")
        st.markdown(f"Retriever: **Local Retrieval**")
        st.markdown(f"Database: **Chroma DB**")
        st.divider()
        st.markdown("### Feedback and Contact")
        st.warning(f"Feedback? Please open an issue on [GitHub issues page](https://github.com/neokd/NeoGPT/issues/new)")
        st.divider()
        st.button("Clear Chat History", on_click=lambda: st.session_state.pop("messages", None))
        
        
    st.title("NeoGPT🤖")
    
    # initialize chat history
    if "messages" not in st.session_state:
        project_info = st.empty()
        project_info.markdown(
            "Welcome to NeoGPT, your open-source, locally-run Language Model (LLM). You can chat with documents, YouTube videos, and more! Try it out by typing a message below.\n\n"
            "### Currently, the database is built using 2 papers:\n"
            "- [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf)\n"
            "- [HuggingGPT](https://arxiv.org/pdf/2303.17580.pdf)\n\n"
            "### YouTube Video from 1littlecoder:\n"
            "- [22 AI News EXPLAINED!!!](https://www.youtube.com/watch?v=BPknz-hCnec)"
             "### Example Sample Commands:\n"
            "1. Summarize the paper Attention Is All You Need\n"
            "2. What do you know about HuggingGPT?\n"
            "3. What is MemGPT?\n"  
        )
        st.session_state.messages = []
    st.warning("**NeoGPT** may generate inaccurate responses about people, places, or facts.")
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
        # # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        

if __name__ == "__main__":
    # run this file
    run_ui()