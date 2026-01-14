import streamlit as st
from engine import load_all_data
from filters_otc import apply_filters
from report_simple import render_report

st.set_page_config(page_title="OTC Báo cáo Doanh số", layout="wide")
st.title("OTC – BÁO CÁO DOANH SỐ THEO BỘ LỌC")

uploaded = st.file_uploader("Chọn file Excel OTC", type=["xlsx"])

if not uploaded:
    st.info("Tải file lên để bắt đầu.")
    st.stop()

with st.spinner("Đang load dữ liệu..."):
    df, _, _, _, df_hcl = load_all_data(uploaded)  # nhận thêm df_hcl

if df is None or df.empty:
    st.error("Không load được dữ liệu!")
    st.stop()

st.success("Load thành công!")

df_filtered = apply_filters(df)
if df_filtered.empty:
    st.warning("Không có dữ liệu sau lọc.")
    st.stop()


render_report(df_filtered, df_hcl)  # truyền df_hcl


