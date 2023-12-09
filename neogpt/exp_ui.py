from neogpt.config import UI_ARGS_PATH
import json
import streamlit as st


with open(UI_ARGS_PATH,'r') as file:
    config_data=json.load(file)


st.write(config_data)