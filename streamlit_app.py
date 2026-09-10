import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Navigation Page")

Home = st.Page("Home.py", title="Home")
Lab1 = st.Page('Lab1.py', title = "Lab1")
Lab2 = st.Page('Lab2.py', title = "Lab2")
Lab3 = st.Page('Lab3.py', title = "Lab3", default=True)
pg = st.navigation([Home, Lab1, Lab2, Lab3])

pg.run()
