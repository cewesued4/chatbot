import streamlit as st
from openai import OpenAI
import pypdf 
from pypdf import PdfReader

# Show title and description.
st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    st.error("A valid OpenAI API key is required.")
    st.stop()

try:

    client = OpenAI(api_key=openai_api_key)
# Simple test request
    client.models.list()
except Exception as e:
    st.error("Invalid OpenAI API key.")
    st.stop()

else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .pdf)", type=("txt", "pdf")
    )
    #Kept getting a AttributeError: 'UploadedFile' object has no attribute 'file'
    #So we are adding the attribute after uploading for the sake of the new function read_pdf. Copilot
    #was used to resolve this error.
    if uploaded_file:
        uploaded_file.file = uploaded_file
    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )
    #This is the read_pdf function to be used late:
    #here, we are first creating the pdf reader, using a pdfreader object
    #once given access to metadata and pages, we create an empty list where 
    #we will store the text extracted from each page
    #then, we loop through every page and extract text from a page
    #and, checking if text exists, we prevent appending or empty string (if a page is empty, we skip)
    #furthermore, we store the page text and continue to combine everything into one string, returned, and assigned
    #to uploaded_file variable
    def read_pdf(uploaded_file):
        reader = PdfReader(uploaded_file)
        pages_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

        return "\n".join(pages_text)  
    if uploaded_file and question:
        file_extension = uploaded_file.file.name.split('.')[-1]
        if file_extension == 'txt':
        # Process the uploaded file and question.
            document = uploaded_file.read().decode()
        elif file_extension == 'pdf':
            document = read_pdf(uploaded_file)
        else:
            st.error("Unsupported file type.")

        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4.1-nano", #tested 4.1,4.1-nano,3.5-turbo,and5
            messages=messages,
            stream=True,
        )
        
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)