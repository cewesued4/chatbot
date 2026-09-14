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
    "This is a simple chatbot that uses OpenAI Gemini to answer questions about inputted URLs."
)

def read_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  #Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Error reading (url): {e}")
        return None


llm_choice = st.sidebar.selectbox(
    "Choose LLM:",
    (
        "OpenAI",
        "Gemini"
    )
)

if llm_choice == "OpenAI":
    model_to_use = "gpt-5-nano"
elif llm_choice == "Gemini":
    model_to_use = "gemini-3.8-flash"


    
st.sidebar.header("URL imputs")
url1 = st.sidebar.text_input("URL 1")
url2 = st.sidebar.text_input("URL 2")

url_content = ""
if url1:
    content1 = read_url_content(url1)
    if content1:
        url_content += f"\n\nContent from URL 1:\n{content1}"

if url2:
    content2 = read_url_content(url2)
    if content2:
        url_content += f"\n\nContent from URL 2:\n{content2}"

#creating an OpenAI client
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant","content":"How can I help you?"}]

for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

#completion = client.chat.completions.create(
    #model = model_to_use,
    #messages=[
        #{"role": "system", "content": "You are a helpful assistant. Use the inputted webpage content provided when it is relevant.\n\n"
        # f"{url_content}"},
        #{"role": "user","content": "message 1 content. "},
        #{"role":"assistant","content":"message 2 content."},
        #{"role": "user","content":"message 3 content"},
        #{"role": "assistant","content": "message 4 content."},
        #{"role": "user","content":"message 5 content."},
        #{"role": "assistant","content": "message 6 content."}
    #],

#)

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.write(prompt)
    messages=[
            {"role": "system", "content": "You are a helpful assistant. After answering, ask if the user would like information. If the user says yes, then answer by giving more information. "
        "If the user says no, go back to asking what you can help with. Give answers such that someone who is 10 years old can understand. Use the inputted webpage content provided when it is relevant.\n\n"
             f"{url_content}"},
            {"role": "user","content": "message 1 content. "},
            {"role":"assistant","content":"message 2 content."},
            {"role": "user","content":"message 3 content"},
            {"role": "assistant","content": "message 4 content."},
            {"role": "user","content":"message 5 content."},
            {"role": "assistant","content": "message 6 content."}
        ]
    if model_to_use == "OpenAI":
        all_messages = (
            messages + st.session_state.messages
        )
        stream = client.chat.completions.create(
            model="gpt-5-nano",
            messages=st.session_state.messages,
            stream=True
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
    else:
        gemini_model = genai.GenerativeModel(
            "gemini-3.8-flash"
        )
        prompt = ""

        for msg in messages:
            prompt += (
                f"{msg['role']}:"
                f"{msg['content']}\n"
            )
        for msg in st.session_state.messages:
            prompt += (
                f"{msg['role']}:"
                f"{msg['content']}\n"
            )
        response = gemini_model.generate_content(prompt)
        response = response.text
        with st.chat_message("assistant"):
            st.write(response)
        
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    #client = st.session_state.client
    #stream = client.chat.completions.create(
    #    model = model_to_use,
    #    messages = [{"role": "system", "content": "You are a helpful assistant. After answering, ask if the user would like information. If the user says yes, then answer by giving more information. "
    #    "If the user says no, go back to asking what you can help with. Give answers such that someone who is 10 years old can understand. "}]+st.session_state.messages,
    #    stream = True
    #)
    #with st.chat_message("assistant"):
    #    response = st.write_stream(stream)
    #st.session_state.messages.append(
    #    {"role": "assistant", "content": response})
    
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



# Here we get to the sidebar, which pops up as soon as you click on the second tab

   
    # Generate an answer using the OpenAI API.
  
#st.write_stream(stream)
   







        
        # Stream the response to the app using `st.write_stream`.
