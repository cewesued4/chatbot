import streamlit as st
from openai import OpenAI
import pypdf 
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai #had to look this import up
import numpy as np

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
genai.configure(api_key = st.secrets["google_api_key"]) #was not sure how to integrate a second key. had to look this up as well
#this configures the Gemini SDK globally with the Open AI API key
#the Gemini SDK stores the API key inside of the genai module
# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI."
)

openAI_model = st.sidebar.selectbox(
    "Which Model?",
    ("turbo","regular")
)

if openAI_model == "turbo":
    model_to_use = "gpt-3.5-turbo"
else:
    model_to_use = "gpt-3.5"

#creating an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant","content":"How can I help you?"}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role":"user","content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    client = st.session_state.client
    stream = client.chat.completions.create(
        model = model_to_use,
        messages = st.session_state.messages,
        stream = True
    )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
#with st.chat_message("assistant"):
    #st.write("Hello human. Say something.")

#prompt = st.chat_input("Say something.")
#if prompt:
    #st.write(f"User has sent the following prompt: {prompt}")





# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("OPENAI_API_KEY not found in secrets.toml")
    st.stop()

 # Let the user upload a file via `st.file_uploader`.

    #Kept getting a AttributeError: 'UploadedFile' object has no attribute 'file'
    #So we are adding the attribute after uploading for the sake of the new function read_pdf. Copilot
    #was used to resolve this error.

    # Ask the user for a question via `st.text_area`.

    #This is the read_pdf function to be used late:
    #here, we are first creating the pdf reader, using a pdfreader object
    #once given access to metadata and pages, we create an empty list where 
    #we will store the text extracted from each page
    #then, we loop through every page and extract text from a page
    #and, checking if text exists, we prevent appending or empty string (if a page is empty, we skip)
    #furthermore, we store the page text and continue to combine everything into one string, returned, and assigned
    #to uploaded_file variable

# Here we get to the sidebar, which pops up as soon as you click on the second tab
completion = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user","content": "message 1 content. "},
        {"role":"assistant","content":"message 2 content"},
        {"role": "user","content":"message 3 content"},
        {"role": "assistant","content": "message 4 content."},
        {"role": "user","content":"message 5 content."}
    ],

)
   
    # Generate an answer using the OpenAI API.
  
#st.write_stream(stream)
   







        
        # Stream the response to the app using `st.write_stream`.
