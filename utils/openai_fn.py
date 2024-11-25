import openai
import re
import streamlit as st

# Extract Python code from markdown
def extract_code_content(text):
    match = re.search(r"```python(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None
    
def get_openai_response(user_prompt, df):
    # Generate response from OpenAI API
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    
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
- Make the graphs vivid.
- If the prompt is not specific or relevant, provide your answer inside: `st.markdown()`.
"""},
            {"role": "user", "content": f"The DataFrame's first 5 rows:\n {', '.join(df.head())}."},
            {"role": "user", "content": f"The DataFrame's info:\n {df.info()}."},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    openai_response = response.choices[0].message.content
    
    return extract_code_content(openai_response)
