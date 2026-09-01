import streamlit as st
from openai import OpenAI

Home = st.Page("streamlit_app.py", title="Home", default=True)
Lab1 = st.Page('Lab1.py', title = "Lab1")
Lab2 = st.Page('Lab2.py', title = "Lab2")
pg = st.navigation([Lab1, Lab2])
st.set_page_config(page_title = 'Navigation Page')
pg.run()
