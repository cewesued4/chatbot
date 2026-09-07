import streamlit as st
from openai import OpenAI
import pypdf 
from pypdf import PdfReader

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
genai.configure(api_key =st.secrets[""])

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses a OpenAI model to summarize any document. " 
        "Simply upload a file and select the summary type of your choice from the drop down menu to begin."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("OPENAI_API_KEY not found in secrets.toml")
    st.stop()

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

# Here we get to the sidebar, which pops up as soon as you click on the second tab
st.sidebar.header("Summary Options")

summary_type = st.selectbox(
    "Choose summary format:",
    (
        "100 Words",
        "2 Paragraphs",
        "5 Bullet Points"
    )
)
advanced_model = st.checkbox("Use advanced model (gpt-5)")
if uploaded_file:
    file_extension = uploaded_file.file.name.split('.')[-1]
    if file_extension == 'txt':
        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
    elif file_extension == 'pdf':
        document = read_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
    #And starting here, we are pre-prompting the model for each selection chosen by the user
    if summary_type == "100 Words":
        prompt = (
        "Summarize the following document in approximately 100 words."
    )

    elif summary_type == "2 Paragraphs":
        prompt = (
            "Summarize the following document in exactly 2 connected paragraphs."
        )

    else:  
        prompt = (
        "Summarize the following document in exactly 5 concise bullet points."
        )
    messages = [
    {
        "role": "user",
        "content": f"""
        {prompt}

        DOCUMENT:
        {document}
        """
    }
    ]
        # Generate an answer using the OpenAI API.
    stream = client.chat.completions.create(
        model="gpt-4.1-nano" if advanced_model else "gpt-5", 
        messages=messages,
        stream=True,
    )
    st.write_stream(stream)






        
        # Stream the response to the app using `st.write_stream`.
