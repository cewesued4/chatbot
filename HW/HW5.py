import streamlit as st
from pyexpat.errors import messages
import requests
# location can be a city, a zip code, an airpot code ('SYR'),
# or a landmark('Eiffel+Tower')
#note: hard codes units to degrees Fahrenheit
import chromadb
import pysqlite3
import sys
from openai import OpenAI
from bs4 import BeautifulSoup
import numpy as np
from pathlib import Path
import zipfile

zip_path = "Lab-04-Data.zip"
extract_path = "Lab-04-Data"

if not Path(extract_path).exists():

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab')
collection = chroma_client.get_or_create_collection(name='Lab4Collection')

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

#this configures the Gemini SDK globally with the Open AI API key
#the Gemini SDK stores the API key inside of the genai module
# Show title and description.
st.title("💬 RAG Course Bot")
st.write(
    "Enter in the location you want to get weather information for." 
)

def relevant_course_info(embedding):
   query_embedding = embedding
       #Get the text related to this question (this prompt)
   results = collection.query(
        query_embeddings = [query_embedding],
        n_results=3, #The number of closest documents to return
           
    )
   st.write(results)
tool = [
    {
        "type": "function",
        "function": {
            "name": "relevant_course_info",
            "description": "Get relevant course information",
            "parameters": {
                "type": "object",
                "properties": {
                    "response": {
                        "type": "object",
                        "description": "The response from the language model"
                    }
                },
                "required": ["response"]
            }
        }
    }
]
def chat_completion_request(messages, tools=None, tool_choice= "auto", model="gpt-4o-mini"):
    return client.chat.completions.create(
         model=model,
         messages=messages,
         tools=tools,
         tool_choice=tool_choice
    )

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role":"user","content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    client = st.session_state.client
    # creating an embedding for the user prompt to use for searching the vector database
    embedding_response = client.embeddings.create(
        input=prompt,
        model="text-embedding-3-small"
    )
    query_embedding = embedding_response.data[0].embedding
    stream = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{"role": "system", "content": "You are a helpful assistant. After answering, ask if the user would like information. If the user says yes, then answer by giving more information. "
        "If the user says no, go back to asking what you can help with. Give answers such that someone who is 10 years old can understand. "}]+st.session_state.messages,
        stream = True
    )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
#IGNORE
#if st.button("Get Weather"):
        #weather = get_current_weather(location)
        #st.write(f"### Weather for {weather['location']}")
        #st.write(f"**Temperature:** {weather['temperature']} F")
        #st.write(f"**Conditions:** {weather['description']}")

        #prompt = f"Based on the weather in {weather['location']}, {weather['temperature']} F, and {weather['description']}, what should I wear today?"
        #response = chat_completion_request(messages=[{"role": "user", "content": prompt}], tools=tool)

        #try:
             #response = client.chat.completions.create(
                  #model = "gpt-4o-mini",
                  #messages=[{
                       #"role": "user",
                       #"content": prompt
                  #}]
             #)
             #st.write("### Clothing Recommendation")
             #st.write(response.choices[0].message.content)
        #except Exception as e:
             #st.error("Error generating clothing recommendation.")

#if 'client' not in st.session_state:
    #api_key = st.secrets["OPENAI_API_KEY"]
    #st.session_state.client = OpenAI(api_key=api_key)

#if "messages" not in st.session_state:
#    st.session_state["messages"] = [{"role": "assistant","content":"How can I help you?"}]

#for msg in st.session_state.messages:
#    chat_msg = st.chat_message(msg["role"])
#    chat_msg.write(msg["content"])

#client = st.session_state.client
#completion = client.chat.completions.create(
#    model = "gpt-4o-mini",
#    messages=[
#        {"role": "system", "content": "You are a helpful assistant."},
#        {"role": "user","content": "message 1 content. "},
#        {"role":"assistant","content":"message 2 content."},
#        {"role": "user","content":"message 3 content"},
#        {"role": "assistant","content": "message 4 content."},
#        {"role": "user","content":"message 5 content."}
#    ],

#)






        # Stream the response to the app using `st.write_stream`.
