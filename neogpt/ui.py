import random

import streamlit as st

from neogpt.manager import db_retriever
from neogpt.settings import config
from neogpt.settings.config import CONVERSTAION_MEMORY_DIRECTORY
from neogpt.utils import get_username

st.set_page_config(page_title="NeoGPT Studio", page_icon="🤖")

retriever_options = [
    "Local",
    "Hybrid",
    "Web",
    "Stepback",
    "Context Compress",
]

persona_options = [
    "Default",
    "ML Engineer",
    "Researcher",
    "Recruiter",
    "Friend",
    "Academician",
    "CEO",
]

db_options = [
    "Chroma",
    "FAISS",
]

RANDOM_PROMPTS = [
    "Write python code to find the factorial of a number",
    "Explain the difference between time complexity and space complexity in algorithms.",
    "What are some common security vulnerabilities in web applications, and how can they be mitigated?",
    "Compare and contrast arrays and linked lists. When would you choose one over the other?",
    "Given an array of integers, return indices of the two numbers such that they add up to a specific target.",
    "Write a function to check if two strings are anagrams of each other?",
    "What is encapsulation in OOP, and how does it improve software design?",
    "Describe the difference between supervised and unsupervised learning. Provide examples of each",
]


@st.cache_resource()
def retrieval_chain(selected_retriever, selected_persona, selected_db):
    with st.spinner("Loading NeoGPT..."):
        chain = db_retriever(
            ui=True,
            retriever=selected_retriever,
            persona=selected_persona,
            vectordb=selected_db,
            show_stats=False,
        )
    return chain


# def show_chat_history():
#     # Access the chain attribute from st.session_state and print it
#     chain = st.session_state.chain
#     # print(chain)
#     for files in os.listdir(CONVERSTAION_MEMORY_DIRECTORY):
#         print(files)
#     return


def main():
    with st.sidebar:
        st.title("NeoGPT Studio")

        # Initialize st.session_state.chain if not already initialized

        # User can choose from the list of retriever options
        selected_retriever = st.selectbox(
            "Retriever", retriever_options, index=retriever_options.index("Local")
        ).lower()

        # User can choose from the list of persona options
        selected_persona = st.selectbox(
            "Persona", persona_options, index=persona_options.index("Default")
        ).lower()

        # User can choose from the list of db options
        selected_db = st.selectbox(
            "Vector DB", db_options, index=db_options.index("Chroma")
        )

        show_source_document = st.toggle("Show Source Document", False)

        # Retrieve the previous selections from session state
        prev_retriever = st.session_state.get("prev_retriever", "local")
        prev_persona = st.session_state.get("prev_persona", "default")
        prev_db = st.session_state.get("prev_db", "Chroma")
        chain_result = st.session_state.get("chain", None)
        # Check if there's a change in the select boxes
        st.divider()
        st.subheader("Upload Your Own Data")
        st.file_uploader("Upload a file")

    if (
        selected_retriever != prev_retriever
        or selected_persona != prev_persona
        or selected_db != prev_db
    ):
        st.session_state.prev_retriever = selected_retriever
        st.session_state.prev_persona = selected_persona
        st.session_state.prev_db = selected_db
        st.session_state.chain = retrieval_chain(
            selected_retriever, selected_persona, selected_db
        )

    # Chats in the current session
    if "messages" not in st.session_state:
        st.session_state.messages = []

    prompt = ""

    if len(st.session_state.messages) == 0 and not prompt:
        q1, q2, q3, q4 = random.sample(RANDOM_PROMPTS, 4)
        st.header("NeoGPT Studio")
        # print(q1, q2, q3, q4)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(q1, key="write_button", use_container_width=True):
                prompt = str(q1)

            if st.button(q2, key="write_button_2", use_container_width=True):
                prompt = str(q2)

        with col2:
            if st.button(q3, key="write_button_3", use_container_width=True):
                prompt = str(q3)

            if st.button(q4, key="write_button_4", use_container_width=True):
                prompt = str(q4)

    # st.write("To get started, type your message in the input box below and press 'Enter' to send it to NeoGPT.")
    # print(st.session_state.messages)
    for message in st.session_state.messages:
        if (
            message["role"] == "assistant"
            and show_source_document
            and isinstance(message["content"], list)
        ):
            col1, col2 = st.columns([1, 1])
            source_documents = message["content"]
            for i in range(0, len(source_documents), 2):
                with col1:
                    st.info(
                        source_documents[i].page_content[:150]
                        + "\n"
                        + source_documents[i].metadata.get("source")
                    )
                with col2:
                    if i + 1 < len(source_documents):
                        st.info(
                            source_documents[i + 1].page_content[:150]
                            + "\n"
                            + source_documents[i + 1].metadata.get("source")
                        )

        elif (
            message["role"] == "assistant"
            and not show_source_document
            and isinstance(message["content"], list)
        ):
            continue
        else:
            st.chat_message(message["role"]).write(message["content"])

    if "chain" not in st.session_state:
        st.session_state.chain = retrieval_chain("local", "default", "Chroma")

    if prompt := st.chat_input("Chat with NeoGPT...") or prompt:
        # print(chain_result)
        st.chat_message(get_username()).write(prompt)
        st.session_state.messages.append({"role": get_username(), "content": prompt})
        # Access the chain attribute from st.session_state
        # print(st.session_state.chain)
        # Send the prompt to the chain

        with st.chat_message("assistant"):
            response = chain_result.invoke(prompt)
            st.session_state.messages.append(
                {"role": "assistant", "content": response["result"]}
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": response["source_documents"]}
            )

            if show_source_document:
                col1, col2 = st.columns([1, 1])
                source_documents = response["source_documents"]
                for i in range(0, len(source_documents), 2):
                    with col1:
                        st.info(
                            source_documents[i].page_content[:150]
                            + "\n"
                            + source_documents[i].metadata.get("source")
                        )
                    with col2:
                        if i + 1 < len(source_documents):
                            st.info(
                                source_documents[i + 1].page_content[:150]
                                + "\n"
                                + source_documents[i + 1].metadata.get("source")
                            )

            # st.write(response)
        # st.chat_message("NeoGPT").write(response)

    # Rest of your application logic goes here


if __name__ == "__main__":
    main()
