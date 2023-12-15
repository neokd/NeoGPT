import logging
from datetime import date, datetime, timedelta

import streamlit as st
from langchain.chains import RetrievalQA
import os

import json

from neogpt.config import MODEL_FILE, MODEL_NAME, SOURCE_DIR,UI_ARGS_PATH
from neogpt.load_llm import load_model
from neogpt.prompts.prompt import get_prompt
from neogpt.vectorstore.chroma import ChromaStore
from neogpt.vectorstore.faiss import FAISSStore
from neogpt.builder import builder
from neogpt.prompts.prompt import conversation_prompt
from langchain.chains import LLMChain
from neogpt.callback_handler import StreamlitStreamingHandler
st.set_page_config(page_title="NeoGPT", page_icon="🤖")

#load parsed arguements from the file
with open(UI_ARGS_PATH,'r') as file:
    UI_ARGS=json.load(file)


persona_list = [
    "default",
    "recruiter",
    "academician",
    "friend",
    "ml_engineer",
    "ceo",
    "researcher",
]
device_type_list=["cpu", "mps", "cuda"]
db_list=["Chroma", "FAISS"]
retriever_list=["local", "web", "hybrid", "stepback", "sql", "compress"]
model_type_list=["mistral", "llama", "ollama", "hf"]
mode_list=['llm_only','db']


@st.cache_resource(show_spinner=True)
def create_chain(mode,device_type,db,model_type,persona):
    with st.spinner(text="Loading the model"):
        llm = load_model(
        device_type,
        model_type,
        model_id=MODEL_NAME,
        model_basename=MODEL_FILE,
        LOGGING=logging,
        callback_manager=[StreamlitStreamingHandler()],
          )
        if mode=="llm_only":
            prompt,memory=conversation_prompt()
            conversation=LLMChain(prompt=prompt,llm=llm,verbose=False,memory=memory)
            return conversation
        else:
            match db:
                case 'Chroma':
                    DB=ChromaStore()
                case "FAISS":
                    DB=FAISSStore().load_local()
            
            
            # Prompt Builder Function
            prompt, memory = get_prompt(persona=persona)
            # Create a retrieval-based question-answering system using the LLM model and the Vector DB
            return RetrievalQA.from_chain_type(
                llm=llm,
                retriever=DB.as_retriever(),
                chain_type="stuff",
                chain_type_kwargs={"prompt": prompt, "memory": memory},
            )
            # return chain


def run_ui():
    with st.sidebar:
        st.markdown("# NeoGPT 🤖")
        st.markdown(
            "NeoGPT is an open-source, locally-run Language Model (LLM) 📚 which allows you to chat with documents, YouTube videos,etc. "
        )
        st.divider()
        st.session_state.mode=st.selectbox(label="MODE",options=mode_list,index=mode_list.index(UI_ARGS['MODE']))
        st.session_state.device_type=st.selectbox(label="DEVICE TYPE",options=device_type_list,index=device_type_list.index(UI_ARGS['DEVICE_TYPE']))
        st.session_state.db=st.selectbox(label="DB",options=db_list,index=db_list.index(UI_ARGS['DB']))
        st.session_state.model_type=st.selectbox(label="MODEL TYPE",options=model_type_list,index=model_type_list.index(UI_ARGS['MODEL_TYPE']))
        st.session_state.persona = st.selectbox(
            "Persona",
            options=persona_list,
            on_change=lambda: st.session_state.pop("messages", None),
        )
        
        st.write(f"TRIES: {UI_ARGS['TRIES']}")

        chain = create_chain(st.session_state.mode,
                             st.session_state.device_type,
                             st.session_state.db,
                             st.session_state.model_type,
                             st.session_state.persona)
        uploads = st.file_uploader("File Upload", accept_multiple_files=True, help= "Upload files to be placed in your document folder")
        # Place the uploaded files in dir
        if uploads:
            for upload in uploads:
                file_name = upload.name
                destinatiopn_path = os.path.join(SOURCE_DIR, file_name)
                with open(destinatiopn_path, "wb") as f:
                    f.write(upload.getvalue())
            # Run the build process once files are detected
            builder()
        
        st.divider()
        st.markdown("### Feedback and Contact")
        st.warning(
            "Feedback? Please open an issue on [GitHub issues page](https://github.com/neokd/NeoGPT/issues/new)"
        )
        st.divider()
        st.button(
            "Clear Chat History",
            on_click=lambda: st.session_state.pop("messages", None),
        )

    st.title("NeoGPT🤖")

    if "messages" not in st.session_state:
        project_info = st.empty()
        project_info.markdown(
            "Welcome to NeoGPT, your open-source, locally-run Language Model (LLM). You can chat with documents, YouTube videos, and more! Try it out by typing a message below.\n\n"
            "### Currently, the database is built using 2 papers:\n"
            "- [Attention Is All You Need](https://arxiv.org/pdf/1706.03762.pdf)\n"
            "- [HuggingGPT](https://arxiv.org/pdf/2303.17580.pdf)\n\n"
            "- [22 AI News EXPLAINED!!!](https://www.youtube.com/watch?v=BPknz-hCnec)\n"
            "### Example Sample Commands:\n"
            "1. Summarize the paper Attention Is All You Need\n"
            "2. What do you know about HuggingGPT?\n"
            "3. What is MemGPT?\n"
        )
        st.warning(
            "**Note:** The bot stops interacting if no prompt is given within 5mins from latest prompt, all your history will be deleted once you refresh the page. "
        )
        st.session_state.messages = []
    st.warning(
        "**NeoGPT** may generate inaccurate responses about people, places, or facts."
    )

    last_input_time = datetime.now()

    if "last_input_time" in st.session_state:
        last_input_time = st.session_state.last_input_time

    # Display chat message from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Check if one minute has passed since the last input
    if datetime.now() - last_input_time > timedelta(minutes=5):
        st.warning("You have not given any input for 5 minute. Input closed.")
        return

    prompt = st.chat_input("Hey! how can I help you?")

    # Update the last input time
    st.session_state.last_input_time = datetime.now()

    # React to user input
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        if st.session_state.mode=="llm_only":
            res = (
                    chain.invoke(prompt)['text']
        )
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(res)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": res})
        else:
            response = chain(prompt, return_only_outputs=True)["result"]
            # res = (
            #     chain.invoke({"question": prompt})
            # )
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    # run this file
    run_ui()
