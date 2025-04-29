import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- ตั้งค่าเริ่มต้นหน้าเว็บ ---
st.set_page_config(page_title="Water Level Dashboard", page_icon="💧", layout="wide")

st.title("💧 Water Level Monitoring Dashboard")

# --- เชื่อมต่อ Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)

# --- อ่านข้อมูลจาก Google Sheet ---
worksheet = gc.open("streamlit-water-level").sheet1
data = pd.DataFrame(worksheet.get_all_records())

# --- แปลง datetime เป็น timestamp ---
data['datetime'] = pd.to_datetime(data['datetime'])

# --- Sidebar เลือกช่วงวันที่ ---
st.sidebar.header("🔎 Filter Options")
min_date = data['datetime'].min()
max_date = data['datetime'].max()
date_range = st.sidebar.date_input("Select date range", [min_date, max_date])

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (data['datetime'] >= pd.to_datetime(start_date)) & (data['datetime'] <= pd.to_datetime(end_date))
    filtered_data = data.loc[mask]
else:
    filtered_data = data

# --- วาดกราฟระดับน้ำ ---
fig = px.line(
    filtered_data, 
    x='datetime', 
    y='water_level', 
    title='Water Level Over Time',
    labels={'datetime': 'Datetime', 'water_level': 'Water Level (cm)'},
    markers=True
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Water Level (cm)",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# --- แสดงตารางข้อมูลดิบ (optional) ---
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_data)
