import streamlit as st
import google.generativeai as genai
import time
from decouple import config
import speech_recognition as sr
from gtts import gTTS
import os
import requests
from bs4 import BeautifulSoup

# Configure the API key for Gemini 1.5 Flash
GOOGLE_API_KEY = config('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Function to simulate streaming response
def stream_data(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.02)

# Function to generate response using Gemini 1.5 Flash
def generate_response(prompt, context):
    model = genai.GenerativeModel('gemini-1.5-flash')
    full_prompt = context + "\nUser: " + prompt
    response = model.generate_content(full_prompt)
    return response.text

# Function to convert text to speech and play it
def text_to_speech(text):
    text = text.replace("*", "")
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    return "response.mp3"

# Function to recognize speech from microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Sorry, the service is unavailable."

# Simple web scraper function
def scrape_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        return " ".join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"Failed to scrape the URL {url}: {str(e)}"

# Function to retrieve data and integrate it into context
def retrieve_and_integrate_data(urls):
    retrieved_content = ""
    for url in urls:
        scraped_data = scrape_url(url)
        retrieved_content += scraped_data + "\n"
    return retrieved_content

# Configure the Streamlit page
st.set_page_config(page_title="Voice-Enabled RAG Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 AI Chatbot with RAG")

# Initialize or retrieve chat history from session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create a string to hold chat context
context = ""
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    context += f"{role.capitalize()}: {content}\n"

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Allow users to input URLs for RAG
urls=['https://www.allenoverseas.com/blog/career-options-after-10th-which-stream-to-choose/','https://www.mindgroom.com/career-counselling-after-10th/west-bengal/']

# Retrieve content from the provided URLs and integrate into context
if urls:
    retrieved_content = retrieve_and_integrate_data(urls)
    context += f"Retrieved Content: {retrieved_content}\n"

# Choice between written and voice prompts
input_method = st.radio("Choose your input method:", ("Text Input", "Voice Input"))

if input_method == "Text Input":
    if prompt := st.chat_input("What is your question?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        response_text = generate_response(prompt, context)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response_chunk in stream_data(response_text):
                full_response += response_chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Update context with the latest messages
        context += f"User: {prompt}\nAssistant: {full_response}\n"

elif input_method == "Voice Input":
    if st.button("Speak"):
        user_input = recognize_speech()
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # Generate and display assistant response
            response_text = generate_response(user_input, context)
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response_chunk in stream_data(response_text):
                    full_response += response_chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Convert response to speech
            audio_file = text_to_speech(full_response)
            audio_bytes = open(audio_file, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")

            # Update context with the latest messages
            context += f"User: {user_input}\nAssistant: {full_response}\n"
