import streamlit as st
import pandas as pd
import chromadb
from openai import OpenAI
import os


client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

df = pd.read_csv("news.csv")

chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_NewsDB')
collection = chroma_client.get_or_create_collection(name='news_articles')

st.write("Collection count:", collection.count())

#this configures the Gemini SDK globally with the Open AI API key
#the Gemini SDK stores the API key inside of the genai module
# Show title and description.
st.title("💬 Chatbot for News Articles")
st.write(
    "This is a simple chatbot using embeddings from Lab 5 for news articles."
)


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
def chat_completion_request(messages, tools=None, tool_choice= "auto", model="gpt-4o-mini", system_prompt="You are a helpful assistant."):
    return client.chat.completions.create(
         model=model,
         messages=[{"role": "system", "content": system_prompt}] + messages,
         tools=tools,
         tool_choice=tool_choice
    )
if 'client' not in st.session_state:
    api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant","content":"How can I help you?"}]
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
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    retrieved_docs = results["documents"][0]

    context = "\n\n".join(retrieved_docs)
    stream = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{"role": "system", "content": system_prompt},
        {
            "role": "system",
            "content": f"""
Retrieved Articles:
{context}
"""
        },
        {
            "role": "user",
            "content": prompt
        }
    ] + st.session_state.messages,
        stream = True
    )
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})


