import requests
# location can be a city, a zip code, an airpot code ('SYR'),
# or a landmark('Eiffel+Tower')
#note: hard codes units to degrees Fahrenheit
import streamlit as st
from openai import OpenAI
import pypdf 
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai #had to look this import up

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
genai.configure(api_key = st.secrets["google_api_key"]) #was not sure how to integrate a second key. had to look this up as well
#this configures the Gemini SDK globally with the Open AI API key
#the Gemini SDK stores the API key inside of the genai module
# Show title and description.
st.title("💬 Weather Bot")
st.write(
    "This is a simple chatbot that uses OpenAI and Gemini models to summarize any document. " 
        "Simply upload or search a file and select the summary type, as well as language, of your choice from the drop down menu to begin."
)

def get_current_weather(location):
    url = f"https://wttr.in/{location}?format=j1"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f'wttr.in error: status(response.status_code)')
    try:
        data = response.json()
    except ValueError:
        #unknown locations come back as plain text, not JSON
        raise Exception(f'Could not ind a location named {location}')
    #j1 has three top-level sections:
    # current condition -- one entry, conditions right now
    # weather -- three entries, one per day, each with min/max, astronomy, and hourly forecasts
    #nearest_area -- the location wttr.in actually matched

    current = data['current_condition'][0]
    #two examples; not that some values are nested one level deeper
    return{'location':location,
           'temperation': float(current['temp_F']),
           'description': current['weatherDesc'][0]['value']}

location = st.text_input("Enter a city, zip code, airport code, or landmark:")

if st.button("Get Weather"):
    try:
        weather = get_current_weather=(location)
        st.write(f"### Weather for {weather['location']}")
        st.write(f"**Temperature:** {weather['temperature']} F")
        st.write(f"**Conditions:** {weather['description']}")
    except Exception as e:
        st.error(str(e))

        
        # Stream the response to the app using `st.write_stream`.
