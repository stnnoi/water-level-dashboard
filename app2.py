import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# ตั้งค่าเชื่อมต่อ Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)

# เปิด Google Sheet (แก้ตรงนี้เป็นชื่อไฟล์ของคุณ)
#worksheet = gc.open("Water Level Monitoring").sheet1
worksheet = gc.open("streamlit-water-level").sheet1

# ดึงข้อมูลทั้งหมดจาก Sheet
data = worksheet.get_all_records()

# แปลงข้อมูลเป็น DataFrame
df = pd.DataFrame(data)
df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')  # แปลงให้เป็น datetime

# แปลงคอลัมน์ datetime ให้เป็นชนิด datetime จริง
df['datetime'] = pd.to_datetime(df['datetime'])

# เรียงข้อมูลตามเวลา
df = df.sort_values(by='datetime')

# ------------------------------
# เริ่มต้นสร้างหน้าเว็บ Streamlit
# ------------------------------

# ตั้งชื่อหน้า Dashboard
st.set_page_config(page_title="Water Level Dashboard", layout="wide")

st.title("📈 Water Level Monitoring Dashboard")

# แสดงข้อมูลเป็นตาราง
st.subheader("ข้อมูลระดับน้ำ (ล่าสุด)")
st.dataframe(df.tail(20), use_container_width=True)

# เลือกช่วงวันที่
st.subheader("เลือกช่วงวันที่ที่ต้องการดูกราฟ")

start_date = st.date_input("เริ่มต้น", value=df['datetime'].min().date())
end_date = st.date_input("สิ้นสุด", value=df['datetime'].max().date())

# กรองข้อมูลตามวันที่ที่เลือก
mask = (df['datetime'].dt.date >= start_date) & (df['datetime'].dt.date <= end_date)
filtered_df = df.loc[mask]
print(filtered_df.columns)  # พิมพ์รายชื่อคอลัมน์ทั้งหมดใน filtered_df

filtered_df = df[['datetime', 'water level']]  # ตรวจสอบว่าเราเลือกคอลัมน์ที่ต้องการ
print(filtered_df.head())  # ดูข้อมูล 5 แถวแรกเพื่อให้มั่นใจว่า DataFrame ถูกต้อง

filtered_df = df[df['datetime'] >= '2025-04-01']  # ตัวอย่างกรองข้อมูลจากวันที่
print(filtered_df.head())  # ตรวจสอบผลลัพธ์ของการกรอง

# วาดกราฟ Water Level
st.subheader("กราฟระดับน้ำ (เซนติเมตร)")
fig = px.line(filtered_df, x='datetime', y='water level', title='Water Level Over Time', markers=True)
fig.update_layout(xaxis_title="วันเวลา", yaxis_title="ระดับน้ำ (เซนติเมตร)")

st.plotly_chart(fig, use_container_width=True)
