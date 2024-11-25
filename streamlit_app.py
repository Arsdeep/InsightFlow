import openai
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils import openai_fn, helper_fn


# Streamlit configuration
st.set_page_config(
    page_title="InsightFlow",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Streamlit page title
st.title("🤖 InsightFlow")
st.subheader("Powered by OpenAI's ChatGPT✨")

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "df" not in st.session_state:
    st.session_state.df = None

# Sidebar for file management and additional controls
with st.sidebar:
    st.header("📁 File Management")
    
    # File upload widget in sidebar
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
    
    # Add a clear history button in the sidebar
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    # Debug mode toggle
    debug_mode = st.checkbox("Debug Mode")


# File processing
if uploaded_file:
    # Process new uploaded file
    st.session_state.df = helper_fn.data_to_df(uploaded_file)
    if st.session_state.df is not None:
        st.write("DataFrame Preview:")
        st.dataframe(st.session_state.df, use_container_width=True)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "content" in message:
            try:
                if debug_mode:
                    st.code(message["content"], language="python")
                exec(message["content"])
            except Exception as e:
                st.error(f"Error in execution: {e}")
        else:
            st.markdown(message["content"])

# Input prompt for user
if st.session_state.df is None:
    user_prompt = st.chat_input("Upload a CSV/Excel file above...", disabled=True)
else:
    user_prompt = st.chat_input("Enter your prompt")

if user_prompt:
    # Add user's message to chat history
    st.chat_message("user").markdown(user_prompt)

    try:
        python_code = openai_fn.get_openai_response(user_prompt, st.session_state.df)

        # Display LLM response
        if debug_mode and python_code:
            with st.chat_message("⚙️"):
                st.code(python_code, language="python")

        if python_code:
            try:
                with st.chat_message("assistant"):
                    exec(python_code)
                st.session_state.chat_history.append({"role": "user", "content": user_prompt})
                st.session_state.chat_history.append({"role": "assistant", "content": python_code})
            except Exception as e:
                st.error(f"Error Occured Executing Code: {e}")
        else:
            st.error("An Error Occured.")
    except Exception as e:
        st.error(f"Error generating OpenAI response: {e}")