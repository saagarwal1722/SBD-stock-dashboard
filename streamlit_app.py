import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Dashboard Setup
st.set_page_config(page_title="SBD Intelligence", layout="wide")

def get_client():
    # This reads the 'Secret Box' you fill in Streamlit
    creds_info = st.secrets["GOOGLE_CREDENTIALS"]
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
    
    # 1. Categories Sidebar
    categories = ["0.72 MM", "0.8 MM", "0.92 MM", "1 MM", "Door Skin 7x3.25", "Door Skin 8x4", "Acrylic Sheet"]
    selected_cat = st.sidebar.selectbox("📂 Select Category", categories)
    
    # 2. Demand Slider Sidebar
    demand_filter = st.sidebar.slider("Show items sold exactly 'X' times:", 0, 20, 1)
    
    # Fetch Data
    ws = sheet.worksheet(selected_cat)
    df = pd.DataFrame(ws.get_all_records())
    df['Processed'] = df['Quantity'].apply(get_sales_info)
    df['Current Stock'] = df['Processed'].apply(lambda x: x[0])
    df['Times Sold'] = df['Processed'].apply(lambda x: x[1])

    # 3. Search Bar
    search_query = st.text_input("🔍 Type Design Code for History (e.g., PT 100)")
    if search_query:
        st.subheader(f"📜 History for {search_query}")
        try:
            h_data = pd.DataFrame(sheet.worksheet("Edit History").get_all_records())
            item_h = h_data[h_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            st.table(item_h)
        except: st.error("Edit History tab not found.")

    # 4. Display List
    st.subheader(f"📦 Inventory ({selected_cat})")
    final_df = df[df['Times Sold'] == demand_filter]
    st.dataframe(final_df[['Item', 'Current Stock', 'Times Sold']], use_container_width=True)

except Exception as e:
    st.error(f"Waiting for your Secret Key... Error: {e}")
