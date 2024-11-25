import openai
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
import re

# API keys
# GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
OPENAI_KEY = st.secrets["OPENAI_API_KEY"]

# Configuring Generative AI (Gemini)
# genai.configure(api_key=GEMINI_KEY)
# model = genai.GenerativeModel('gemini-1.5-flash')

# Helper function to read data
def read_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# Extract Python code from markdown
def extract_code_content(text):
    match = re.search(r"```python(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None

# Streamlit configuration
st.set_page_config(
    page_title="InsightFlow",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Streamlit page title
st.title("🤖 InsightFlow")
st.subheader("Powered by OpenAI's ChatGPT✨")

debug_mode = st.sidebar.checkbox("Debug Mode")

# Initialize chat history and dataframe in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "df" not in st.session_state:
    st.session_state.df = None

# File upload widget
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file:
    st.session_state.df = read_data(uploaded_file)
    st.write("DataFrame Preview:")
    st.dataframe(st.session_state.df, use_container_width=True)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "content" in message:
            try:
                exec(message["content"])
            except Exception as e:
                st.error(f"Error in execution: {e}")
        else:
            st.markdown(message["content"])

# Input prompt for user
if not uploaded_file:
    user_prompt = st.chat_input("Upload a CSV/Excel file above...", disabled=True)
else:
    user_prompt = st.chat_input("Enter your prompt")

if user_prompt:
    # Add user's message to chat history
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role": "user", "content": user_prompt})

    # Generate response from OpenAI API
    openai.api_key = OPENAI_KEY
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
You are an AI assistant that generates concise Streamlit Python code. 
Adhere to the following rules:
- Use only imported libraries (pandas, numpy, streamlit, plotly).
- The DataFrame is initialized as `st.session_state.df`.
- Use `st.session_state.df.columns` to refer to the columns.
- Use Plotly for charts and graphs.
- Return the code snippet as Python code. 
- If the prompt is not specific or relevant, respond with: st.error("Prompt is not specific/irrelevant").
"""},
            {"role": "user", "content": f"The DataFrame's first 5 rows:\n {', '.join(st.session_state.df.head())}."},
            {"role": "user", "content": f"The DataFrame's info:\n {st.session_state.df.info()}."},
            {"role": "user", "content": user_prompt},
        ],
    )

    openai_response = response.choices[0].message.content
    python_code = extract_code_content(openai_response)

    # Display LLM response
    if debug_mode and python_code:
        with st.chat_message("⚙️"):
            st.markdown(f"```python\n{python_code}\n```")

    if python_code:
        try:
            with st.chat_message("assistant"):
                exec(python_code)
            st.session_state.chat_history.append({"role": "assistant", "content": python_code})
        except Exception as e:
            st.error(f"Error executing generated code: {e}")
    else:
        st.error("No valid Python code found in the response.")
