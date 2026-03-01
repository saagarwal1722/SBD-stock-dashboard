import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# --- DASHBOARD SETUP ---
st.set_page_config(page_title="Intelligence Dashboard", layout="wide")

def get_client():
    # 1. Access the secrets from Streamlit
    creds_info = st.secrets["GOOGLE_CREDENTIALS"]
    
    # 2. THE KEY FIX: This converts the text '\n' into actual line breaks.
    # This prevents the "Unable to load PEM file" error.
    if isinstance(creds_info, st.runtime.secrets.AttrDict):
        creds_dict = dict(creds_info)
    else:
        creds_dict = creds_info

    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
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

st.title("🚀 Inventory Intelligence Dashboard")

try:
    client = get_client()
    # Your Google Sheet ID
    sheet = client.open_by_key("1Putj_rdvaHjokbSdT8ArjQbMDVnTDeHDNysj5avTOW4")
    
    # Categories Sidebar
    categories = ["0.72 MM", "0.8 MM", "0.92 MM", "1 MM", "Door Skin 7x3.25", "Door Skin 8x4", "Acrylic Sheet"]
    selected_cat = st.sidebar.selectbox("📂 Select Category", categories)
    
    # Demand Filter (Group by Sales Count)
    demand_filter = st.sidebar.slider("Show items sold exactly 'X' times:", 0, 20, 0)
    
    # Load and process data
    ws = sheet.worksheet(selected_cat)
    df = pd.DataFrame(ws.get_all_records())
    
    df['Processed'] = df['Quantity'].apply(get_sales_info)
    df['Current Stock'] = df['Processed'].apply(lambda x: x[0])
    df['Times Sold'] = df['Processed'].apply(lambda x: x[1])

    # Deep History Search
    search_query = st.text_input("🔍 Search Design for History (e.g., PT 100)")
    if search_query:
        st.subheader(f"📜 History for {search_query}")
        try:
            h_ws = sheet.worksheet("Edit History")
            h_data = pd.DataFrame(h_ws.get_all_records())
            item_h = h_data[h_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.table(item_h)
        except: st.info("Ensure an 'Edit History' tab exists in your Google Sheet.")

    # Main Inventory View
    st.subheader(f"📦 Inventory ({selected_cat})")
    final_df = df[df['Times Sold'] == demand_filter]
    st.dataframe(final_df[['Item', 'Current Stock', 'Times Sold']], use_container_width=True)

except Exception as e:
    st.error(f"Waiting for valid configuration. Error details: {e}")
