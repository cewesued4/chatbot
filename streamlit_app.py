import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Navigation Page")

Home = st.Page("Home.py", title="Home", default=True)
Lab1 = st.Page('Lab1.py', title = "TAB 1")
Lab2 = st.Page('Lab2.py', title = "CHATBOT HERE")
pg = st.navigation([Home, Lab1, Lab2])

pg.run()
