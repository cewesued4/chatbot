from pyexpat.errors import messages

import openai
import requests
# location can be a city, a zip code, an airpot code ('SYR'),
# or a landmark('Eiffel+Tower')
#note: hard codes units to degrees Fahrenheit
import streamlit as st
from openai import OpenAI
from bs4 import BeautifulSoup
import langchain
from langchain.agents import create_agent



#import google.generativeai as genai #had to look this import up

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
#genai.configure(api_key = st.secrets["google_api_key"]) #was not sure how to integrate a second key. had to look this up as well
#this configures the Gemini SDK globally with the Open AI API key
#the Gemini SDK stores the API key inside of the genai module
# Show title and description.
st.title("💬 Weather Bot")
st.write(
    "Enter in the location you want to get weather information for." 
)


def get_current_weather(location: str = "Syracuse, NY") -> dict:
    """Get the weather for a given location. Then return the following:
    Location: str
    Temperature: float
    Description of the weather conditions and what to wear: str"""
    url = f"https://wttr.in/{location}?format=j1"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f'wttr.in error: status{response.status_code}')
    try:
        data = response.json()
    except ValueError:
        #unknown locations come back as plain text, not JSON
        raise Exception(f'Could not find a location named {location}')
    #j1 has three top-level sections:
    # current condition -- one entry, conditions right now
    # weather -- three entries, one per day, each with min/max, astronomy, and hourly forecasts
    #nearest_area -- the location wttr.in actually matched

    current = data['current_condition'][0]
    #two examples; not that some values are nested one level deeper
    return{'location':location,
           'temperature': float(current['temp_F']),
           'description': current['weatherDesc'][0]['value']}

location = st.text_input("Enter a city and state")

agent = create_agent(
     model="gpt-4o-mini",
     tools = [get_current_weather],
     system_prompt="You are a helpful assistant that provides the weather."

)
def chat_completion_request(messages, tools=None, tool_choice= "auto", model="gpt-4o-mini"):
    return client.chat.completions.create(
         model=model,
         messages=messages,
         tools=tools,
         tool_choice=tool_choice
    )
    
if st.button("Get Weather"):
        weather = get_current_weather(location)
        st.write(f"### Weather for {weather['location']}")
        st.write(f"**Temperature:** {weather['temperature']} F")
        st.write(f"**Conditions:** {weather['description']}")
        result = agent.invoke(
             {"messages":[{"role":"user","content":f"What should I wear in {location}?"}]}
        )
        st.write("### Clothing Recommendation")
        with st.chat_message("assistant"):
             st.write(result.choices[0].messages.content)
         

     




        # Stream the response to the app using `st.write_stream`.
