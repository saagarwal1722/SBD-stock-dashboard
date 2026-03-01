import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

# --- SETUP ---
st.set_page_config(page_title="SBD Intelligence Dashboard", layout="wide")

def get_client():
    creds_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    return gspread.authorize(creds)

# --- LOGIC: Parsing Sales Frequency ---
def get_sales_info(raw_value):
    val_str = str(raw_value).strip()
    if '-' in val_str:
        parts = [p for p in val_str.split('-') if p.strip()]
        try:
            numbers = [float(p) for p in parts]
            current_qty = numbers[0] - sum(numbers[1:])
            return current_qty, len(numbers) - 1
        except:
            return val_str, 0
    return raw_value, 0

# --- UI ---
st.title("🚀 Shree Balaji Decor: Business Intelligence")

try:
    client = get_client()
    sheet = client.open_by_key("1Putj_rdvaHjokbSdT8ArjQbMDVnTDeHDNysj5avTOW4")
    
    # 1. CATEGORY DROPDOWN (Requirement #2)
    categories = [
        "0.72 MM", "0.8 MM", "0.92 MM", "1 MM", 
        "Door Skin 7x3.25", "Door Skin 8x4", "Acrylic Sheet"
    ]
    selected_cat = st.sidebar.selectbox("📂 Select Category / Thickness", categories)
    
    # Fetch data based on category (maps to your sheet tabs)
    try:
        ws = sheet.worksheet(selected_cat)
        data = ws.get_all_records()
        df = pd.DataFrame(data)
    except:
        st.warning(f"Tab '{selected_cat}' not found. Please ensure tab names match exactly.")
        st.stop()

    # Process Sales Count
    df['Processed'] = df['Quantity'].apply(get_sales_info)
    df['Current Stock'] = df['Processed'].apply(lambda x: x[0])
    df['Times Sold'] = df['Processed'].apply(lambda x: x[1])

    # 2. DEMAND HEATMAP MENUS (Requirement #3)
    st.sidebar.divider()
    st.sidebar.subheader("📊 Demand Menus")
    demand_filter = st.sidebar.slider("View items sold exactly 'X' times:", 0, 20, 20)
    
    # 3. SEARCH & DEEP HISTORY (Requirement #1)
    search_query = st.text_input("🔍 Deep Search: Type Design Code for Full History (e.g., PT 100)")

    if search_query:
        # Show deep history from "Edit History" tab
        st.subheader(f"📜 Transaction History for {search_query}")
        try:
            history_ws = sheet.worksheet("Edit History")
            h_data = pd.DataFrame(history_ws.get_all_records())
            # Filter history for the specific design
            item_history = h_data[h_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
            if not item_history.empty:
                st.table(item_history)
            else:
                st.info("No records found in Edit History for this design.")
        except:
            st.error("Could not find 'Edit History' tab in Google Sheets.")

    # 4. MAIN DISPLAY (Filtered by Demand Menu)
    st.subheader(f"📦 Inventory: {selected_cat} (Items sold {demand_filter} times)")
    filtered_df = df[df['Times Sold'] == demand_filter]
    
    if not filtered_df.empty:
        st.dataframe(filtered_df[['Item', 'Current Stock', 'Times Sold']], use_container_width=True)
    else:
        st.write(f"No items found with exactly {demand_filter} sales in this category.")

except Exception as e:
    st.error(f"Setup incomplete: {e}")
