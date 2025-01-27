import micropip
await micropip.install('requests')
import requests
import pandas as pd
import streamlit as st
st.set_page_config(page_title = "Emoji Shortcodes", page_icon="🕹️", layout = "wide", initial_sidebar_state = "expanded")
st.markdown(
    '''
    Direct Copy from [here](https://github.com/streamlit/emoji-shortcodes/blob/master/streamlit_app.py) by [Thiago Teixeira](https://github.com/tvst) 
    ''')
@st.cache_data(ttl=60*60*12)
def fetch_emojis():
    resp = requests.get(
        'https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json')
    json = resp.json()
    codes, emojis = zip(*json.items())
    return pd.DataFrame({
        'Emojis': emojis,
        'Shortcodes': [f':{code}:' for code in codes],
    })

'''
# Streamlit emoji shortcodes

Below are all the emoji shortcodes supported by Streamlit.

Shortcodes are a way to enter emojis using pure ASCII. So you can type this `:smile:` to show this
:smile:.

(Keep in mind you can also enter emojis directly as Unicode in your Python strings too — you don't
*have to* use a shortcode)
'''

emojis = fetch_emojis()

st.table(emojis)