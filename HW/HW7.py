import streamlit as st
import pandas as pd
import chromadb
from openai import OpenAI
import os


client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)

df = pd.read_csv("news.csv")
#for idx, row in df.iterrows(): #used copilot here to see how to create an embedding for a list of non-document files/csv file with multiple documents inside 

    #article_text = f"""
    #Company: {row['company_name']}
    #Date: {row['Date']}

    #Article:
    #{row['Document']}

    #Source:
    #{row['URL']}
    #"""
    #embedding = client.embeddings.create(
        #model="text-embedding-3-small",
        #input=article_text
    #).data[0].embedding

    #collection.add(
        #ids=[str(idx)],
        #embeddings=[embedding],
        #documents=[article_text],
        #metadatas=[{
        #    "company": row["company_name"],
        #    "date": str(row["Date"]),
        #    "url": row["URL"]
        #    
        #}]
    #)

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
    system_prompt = system_prompt = """
You are a news reporting assistant for a global law firm.You can only use the retrieved articles provided.
If the user asks:
'Find the most interesting news'
Return a ranked list of the top news stories, a short summary of each story, and
a reason why each story is interesting.

Interesting news includes lawsuits, legal disputes, bankruptcy, government investigations, SEC actions, mergers, acquisitions, CEO changes, major financial announcements, and fraud.
Rank articles from most important to least important.

If the user asks:
'Find news about X'
Return a summary about the the specific topic and company as well as a list of relevant articles about that company or topic.
"""
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


