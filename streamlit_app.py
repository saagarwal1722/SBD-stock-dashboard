import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# --- SETUP ---
st.set_page_config(page_title="SBD Intelligence Dashboard", layout="wide")

def get_client():
    # 1. Read the secret from Streamlit
    creds_info = st.secrets["GOOGLE_CREDENTIALS"]
    
    # 2. THE MAGIC FIX: This line converts the text into a real key format
    # It replaces the text '\n' with actual new lines that the computer needs.
    if isinstance(creds_info["private_key"], str):
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

def get_sales_info(raw_value):
    val_str = str(raw_value).strip()
    if '-' in val_str:
        parts = [p for p in val_str.split('-') if p.strip()]
        try:
            numbers = [float(p) for p in parts]
            current_qty = numbers[0] - sum(numbers[1:])
            return current_qty, len(numbers) - 1
        except: return val_str, 0
    return raw_value, 0

st.title("🚀 Shree Balaji Decor: Live Dashboard")

try:
    client = get_client()
    sheet = client.open_by_key("1Putj_rdvaHjokbSdT8ArjQbMDVnTDeHDNysj5avTOW4")
    
    # Categories based on your request
    categories = ["0.72 MM", "0.8 MM", "0.92 MM", "1 MM", "Door Skin 7x3.25", "Door Skin 8x4", "Acrylic Sheet"]
    selected_cat = st.sidebar.selectbox("📂 Select Category", categories)
    demand_filter = st.sidebar.slider("Show items sold exactly 'X' times:", 0, 20, 1)
    
    ws = sheet.worksheet(selected_cat)
    df = pd.DataFrame(ws.get_all_records())
    df['Processed'] = df['Quantity'].apply(get_sales_info)
    df['Current Stock'] = df['Processed'].apply(lambda x: x[0])
    df['Times Sold'] = df['Processed'].apply(lambda x: x[1])

    # Search Logic (Using your 'Logs' tab for history)
    search_query = st.text_input("🔍 Type Design Code for History (e.g., PT 100)")
    if search_query:
        st.subheader(f"📜 History for {search_query}")
        try:
            h_data = pd.DataFrame(sheet.worksheet("Logs").get_all_records())
            item_h = h_data[h_data['Item'].astype(str).str.contains(search_query, case=False)]
            st.table(item_h)
        except: st.info("Add a 'Logs' tab to see history.")

    st.subheader(f"📦 Inventory ({selected_cat})")
    final_df = df[df['Times Sold'] == demand_filter]
    st.dataframe(final_df[['Item', 'Current Stock', 'Times Sold']], use_container_width=True)

except Exception as e:
    st.error(f"Waiting for your Secret Key... Error: {e}")
