import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# --- SETUP ---
st.set_page_config(page_title="SBD Intelligence Dashboard", layout="wide")

def get_client():
    # Read the secret from Streamlit
    creds_dict = dict(st.secrets["GOOGLE_CREDENTIALS"])
    
    # MAGIC FIX: This line fixes the 'PEM' error automatically by 
    # converting literal '\n' text into real new lines.
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)
