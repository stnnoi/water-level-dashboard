import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# -----------------------
# ตั้งค่าเชื่อมต่อ Google Sheets
# -----------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)

# เปิด Google Sheet
worksheet = gc.open("streamlit-water-level").sheet1
data = worksheet.get_all_records()

# แปลงเป็น DataFrame และจัดการ datetime
df = pd.DataFrame(data)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce', dayfirst=True)
df = df.sort_values(by='datetime')

# ------------------------------
# เริ่มสร้างหน้าเว็บ Streamlit
# ------------------------------
st.set_page_config(page_title="AWD Dashboard", layout="wide")
st.title("📈 AWD Dashboard")

# ------------------------------
# เพิ่ม slider สำหรับเลือกช่วงเวลา
# ------------------------------
st.subheader("เลือกช่วงเวลาที่ต้องการแสดงบนกราฟ")

# กำหนดค่าวันเริ่มต้นและสิ้นสุด
min_datetime = df['datetime'].min()
max_datetime = df['datetime'].max()

# แปลง datetime เป็น timestamp เพื่อให้ใช้กับ slider
min_timestamp = min_datetime.timestamp()
max_timestamp = max_datetime.timestamp()

# slider สำหรับเลือกช่วงเวลา
selected_range = st.slider(
    "ช่วงเวลา",
    min_value=min_timestamp,
    max_value=max_timestamp,
    value=(min_timestamp, max_timestamp),
    format="DD/MM/YYYY HH:mm"
)

# แปลงค่าจาก slider กลับเป็น datetime
start_datetime = pd.to_datetime(selected_range[0], unit='s')
end_datetime = pd.to_datetime(selected_range[1], unit='s')

# กรองข้อมูลตามช่วงเวลา
filtered_df = df[(df['datetime'] >= start_datetime) & (df['datetime'] <= end_datetime)]

# ------------------------------
# วาดกราฟ Plotly ด้วยข้อมูลที่กรองแล้ว
# ------------------------------
st.subheader("กราฟระดับน้ำ (เซนติเมตร)")
filtered_df['label'] = filtered_df['water level'].astype(str) + " cm"

fig = px.line(
    filtered_df,
    x='datetime',
    y='water level',
    title='Water Level Over Time',
    markers=True,
    text='label'
)
fig.update_traces(textposition='top center')
fig.update_layout(xaxis_title="วันเวลา", yaxis_title="ระดับน้ำ (เซนติเมตร)")

st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# แสดงตาราง 4 แถว และเลื่อนหน้า
# ------------------------------
st.subheader("ข้อมูลระดับน้ำล่าสุด (4 แถวต่อหน้า)")

# แปลง datetime เป็นแค่วันที่เพื่อแสดง
df['date'] = df['datetime'].dt.date
df_display = df[['date', 'water level']].copy()
df_display = df_display.reset_index(drop=True)

# สร้างตัวแปร page สำหรับเลื่อน
rows_per_page = 4
max_page = (len(df_display) - 1) // rows_per_page

if 'page' not in st.session_state:
    st.session_state.page = 0

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ ก่อนหน้า"):
        if st.session_state.page > 0:
            st.session_state.page -= 1

with col3:
    if st.button("ถัดไป ➡️"):
        if st.session_state.page < max_page:
            st.session_state.page += 1

# คำนวณ index ของข้อมูลที่จะแสดง
start_idx = st.session_state.page * rows_per_page
end_idx = start_idx + rows_per_page
st.dataframe(df_display.iloc[start_idx:end_idx], use_container_width=True, height=180)

# แสดงหน้าปัจจุบัน
st.caption(f"หน้า {st.session_state.page + 1} จาก {max_page + 1}")
