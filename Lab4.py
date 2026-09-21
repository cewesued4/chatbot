import streamlit as st
from openai import OpenAI
import pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3
import chromadb
import pypdf 
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
#import google.generativeai as genai #had to look this import up
import numpy as np
import sys

from pathlib import Path
import zipfile

zip_path = "Lab-04-Data.zip"
extract_path = "Lab-04-Data"

if not Path(extract_path).exists():

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)
#A fix for working with ChromaDB on Streamlit Community Cloud
#_import_('pysqlite')
#sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab')
collection = chroma_client.get_or_create_collection(name='Lab4Collection')

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

#Extract text from HTML
#This function extracts text from each html document
#to pass to add_to_collection
#def extract_text_from_html(html_path):
 #   try:
 #       with open(html_path, "r", encoding="utf-8") as f:
 #           html = f.read()

#        soup = BeautifulSoup(html, "html.parser")
  #      #removing script/style tags
    #    for tag in soup(["script", "style"]):
    #        tag.decompose()
    #    text = soup.get_text(separator="\n")
    #    return text

    #except Exception as e:
    #    st.error(f"Error reading {html_path}: {e}")
    #    return ""
        #text = ""
        #for page in reader.pages:
           # page_text = page.extract_text()
            #if page_text:
                #text += page_text + "\n"

        #return text
    #except Exception as e:
        #st.error(f"Error reading {pdf_path}: {e}")
       # return ""
        
#A function that will add documents to collection
#a collection = ChromaDB collection, already established
#text = extracted text from PDF files
#Embeddings inserted into the collection from OpenAI
#def add_to_collection(collection, text, file_name):
    #client = st.session_state.openai_client
    #response = client.embeddings.create(
        #input=text,
        #model='text-embedding-3-small'
    #)
    #Get the embedding
    #embedding = response.data[0].embedding

    #Add embedding and document to ChromaDB
    #collection.add(
        #documents=[text],
        #ids=[file_name],
        #embeddings=[embedding],
        #metadatas = [
            #{
                #"source":file_name,
                #"document_type":"pdf"
            #}
        #]
    #)



#Populate collection with pdfs
#this function uses extract_text_from pdf
#and add_to_collection to put syllabi in ChromaDB collection
#def load_pdfs_to_collection(folder_path, collection):
    #folder = Path(folder_path)
    #st.write("Contents of folder:*", list(folder.iterdir()))
    #st.write("Folder exists:", folder.exists())

    #st.write("Folder contents:")
    #st.write(list(folder.iterdir()))
    #pdf_files = list(folder.rglob("*.pdf"))

    #st.write("PDF files*found:")
    #st.write(pdf_files)
    #count = 0
    #for pdf_file in pdf_files:
        #st.write("Processing:", pdf_file)
        #text = extract_text_from_pdf(pdf_file)
        #st.write("Characters extracted:", len(text))
        #if text.strip():
            #st.write("Adding:", pdf_file.name)
            #add_to_collection(
                #collection,
                #text,
                #pdf_file.name
            #)
            #count += 1
    #st.write("Loaded count:", count)
    #return count

#loaded = load_pdfs_to_collection('./Lab-04-Data/', collection)
#st.write("Loaded:", loaded)
#st.write("Collection count after loading:", collection.count())
#Check if collection is empty and load PDFs
#if collection.count() ==0:
    #loaded = load_pdfs_to_collection('./Lab-04-Data/',collection)
#client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
#genai.configure(api_key = st.secrets["google_api_key"]) #was not sure how to integrate a second key. had to look this up as well
#this configures the Gemini SDK globally with the Open AI API key
#the Gemini SDK stores the API key inside of the genai module
# Show title and description.
st.title("Lab 4: Chatbot using RAG")
st.write("Collection count:", collection.count())
#Querying a collection - only used for testing
st.write(
    "This is a simple chatbot that uses OpenAI."
)

topic = st.sidebar.text_input('Topic', placeholder = 'Type your topic (e.g., GenAI)...')

if topic:
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=topic,
        model='text-embedding-3-small')

    #Get the embedding
    query_embedding = response.data[0].embedding
    #Get the text related to this question (this prompt)
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results=3, #The number of closest documents to return
        
    )
    st.write(results)

    #Display the results
    st.subheader(f'Results for: {topic}')

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]

        st.write(f'**{i+1}. {doc_id}**')
else:
    st.info('Enter a topic in the sidebar to search the collection')
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

client = st.session_state.client
completion = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user","content": "message 1 content. "},
        {"role":"assistant","content":"message 2 content."},
        {"role": "user","content":"message 3 content"},
        {"role": "assistant","content": "message 4 content."},
        {"role": "user","content":"message 5 content."}
    ],

)
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role":"user","content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    client = st.session_state.client
    stream = client.chat.completions.create(
        model = model_to_use,
        messages = [{"role": "system", "content": "You are a helpful assistant. After answering, ask if the user would like information. If the user says yes, then answer by giving more information. "
        "If the user says no, go back to asking what you can help with. Give answers such that someone who is 10 years old can understand. "}]+st.session_state.messages,
        stream = True
    )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
    
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
