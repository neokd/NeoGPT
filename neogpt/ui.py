import streamlit as st

from neogpt.manager import db_retriever


@st.cache_resource
def retrieval_chain():
    return db_retriever()


def main():
    st.title("NeoGPT Studio")
    # st.write("Welcome to NeoGPT! This is a web-based interface for interacting with the NeoGPT chatbot.")
    # st.write("To get started, simply type your message in the input box below and press 'Enter' to send it to NeoGPT.")

    st.warning("NeoGPT's UI is under construction. Please check back later.")


if __name__ == "__main__":
    main()
