import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="SBD Stock Dashboard", layout="wide")

# 1. Connect to Google Sheets using Secrets
try:
    creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    
    SHEET_ID = "1Putj_rdvaHjokbSdT8ArjQbMDVnTDeHDNysj5avTOW4"
    sheet = client.open_by_key(SHEET_ID)
    stock_ws = sheet.get_worksheet(0)
    log_ws = sheet.worksheet("Logs")
except Exception as e:
    st.error("Connection Error. Please check your Google Credentials in Secrets.")
    st.stop()

# 2. Logic to display data
st.title("📦 Shree Balaji Decor: Stock Agent")
data = stock_ws.get_all_records()
df = pd.DataFrame(data)[['Item', 'Quantity']] # Only showing your 2 variables

# 3. Search & Filters
search = st.text_input("🔍 Search Item Code")
if search:
    df = df[df['Item'].astype(str).str.contains(search, case=False)]

# 4. Ranking (Most Sold)
logs = pd.DataFrame(log_ws.get_all_records())
if not logs.empty:
    st.subheader("🔥 Top Selling Items")
    sales_rank = logs.groupby('Item').size().reset_index(name='Sales Count').sort_values('Sales Count', ascending=False)
    st.table(sales_rank)

st.subheader("Inventory Status")
st.dataframe(df, use_container_width=True)
