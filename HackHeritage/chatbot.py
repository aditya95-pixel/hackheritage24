import streamlit as st
import google.generativeai as genai
import time
from decouple import config
import re

# Configure the API key for Gemini 1.5 Flash
GOOGLE_API_KEY = config('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Function to simulate streaming response
def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)

# Function to generate response using Gemini 1.5
def generate(query):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(query)
    return response.text

# Initialize or retrieve chat history from session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to format response and handle code blocks
def format_response(response):
    # Pattern to detect code blocks with any language
    pattern = re.compile(r'```(\w+)?\n([\s\S]*?)```')
    
    def replace_code_block(match):
        language = match.group(1) or 'text'  # Default to 'text' if no language specified
        code = match.group(2).strip()
        return (
            f'<div style="background-color: #f7f7f7; padding: 10px; border-radius: 5px; overflow: auto; border: 1px solid #ddd;">'
            f'<pre style="font-family: monospace; white-space: pre-wrap;">{code}</pre></div>'
        )
    
    # Replace code blocks using the regex pattern
    formatted_response = pattern.sub(replace_code_block, response)
    
    # Replace any remaining code fences without language (if any)
    formatted_response = formatted_response.replace('```', '')

    return formatted_response

# Streamlit app layout and styling
st.set_page_config(page_title="Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 AI Chatbot")

# User input field
user_input = st.text_input("You:", placeholder="Ask me anything...")

# Process the user's input
if user_input:
    with st.spinner("Bot is typing..."):
        response = generate(user_input)
        
        # Store the query and response in the chat history
        st.session_state.chat_history.append({"user": user_input, "bot": format_response(response)})

# Display chat history in a ChatGPT-like format
for chat in st.session_state.chat_history:
    st.markdown(f"<div style='background-color: #e1f5fe; padding: 10px; border-radius: 10px; margin: 10px 0;'>"
                f"<strong>You:</strong><br>{chat['user']}</div>", unsafe_allow_html=True)
    
    response_placeholder = st.empty()
    streamed_text = ""
    for word in stream_data(chat['bot']):
        streamed_text += word
        response_placeholder.markdown(
            f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 10px; margin: 10px 0;'>"
            f"<strong>Bot:</strong><br>{streamed_text}</div>", unsafe_allow_html=True)
    
    st.markdown("---")

# Footer
st.markdown("""
    ---
    *Made with 💻 by Us*
""")
