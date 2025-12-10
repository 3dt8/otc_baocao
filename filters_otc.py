# filters_otc.py — VER 2.2 (UI Sidebar tối ưu + đồng bộ) - No change (cache removed)
import streamlit as st
import pandas as pd

def parse_multi_input(text):
    if not text.strip():
        return []

    clean_text = text.replace(",", "\n").replace(";", "\n")
    parts = clean_text.split("\n")
    return [p.strip() for p in parts if p.strip()]

def apply_filters(df):
    st.sidebar.header("🔎 BỘ LỌC DỮ LIỆU OTC — Ver 2.2")

    # 1️⃣ LỌC THEO NGÀY
    st.sidebar.subheader("📅 1. Khoảng ngày (Billing Date)")

    date_from = st.sidebar.date_input(
        "Từ ngày",
        df["Billing Date"].min()
    )
    date_to = st.sidebar.date_input(
        "Đến ngày",
        df["Billing Date"].max()
    )

    df_filtered = df[
        (df["Billing Date"] >= pd.to_datetime(date_from)) &
        (df["Billing Date"] <= pd.to_datetime(date_to))
    ]

    # 2️⃣ LỌC KHÁCH HÀNG
    st.sidebar.subheader("🏪 2. Khách hàng")

    pasted_kh = st.sidebar.text_area(
        "Dán MÃ KH (nhiều mã – xuống dòng hoặc , ;)",
        placeholder="0010026313\n0010029877"
    )

    pasted_list = parse_multi_input(pasted_kh)

    if pasted_list:
        df_filtered = df_filtered[df_filtered["Customer"].isin(pasted_list)]
    else:
        list_kh = sorted(df["Name"].dropna().unique())
        selected_kh = st.sidebar.multiselect(
            "Hoặc chọn theo tên:",
            list_kh
        )
        if selected_kh:
            df_filtered = df_filtered[df_filtered["Name"].isin(selected_kh)]

    # 3️⃣ LỌC SẢN PHẨM
    st.sidebar.subheader("📦 3. Sản phẩm")

    pasted_sp = st.sidebar.text_area(
        "Dán MÃ SP (nhiều mã – xuống dòng hoặc , ;)",
        placeholder="010248\n050626\n020104"
    )

    pasted_sp_list = parse_multi_input(pasted_sp)

    if pasted_sp_list:
        df_filtered = df_filtered[df_filtered["Material"].isin(pasted_sp_list)]
    else:
        list_sp = sorted(df["Item Description"].dropna().unique())
        selected_sp = st.sidebar.multiselect(
            "Hoặc chọn theo tên sản phẩm",
            list_sp
        )
        if selected_sp:
            df_filtered = df_filtered[df_filtered["Item Description"].isin(selected_sp)]

    # 4️⃣ PROGRAM
    st.sidebar.subheader("🏷 4. Program")

    list_pg = sorted(df["Program"].dropna().unique())
    selected_pg = st.sidebar.multiselect("Chọn Program", list_pg)

    if selected_pg:
        df_filtered = df_filtered[df_filtered["Program"].isin(selected_pg)]

    # 5️⃣ NHÓM KM (Product Hierarchy level 2)
    st.sidebar.subheader("🧪 5. Nhóm KM (Level 2)")

    list_km = sorted(df["Nhóm_KM"].dropna().unique())
    selected_km = st.sidebar.multiselect("Chọn nhóm KM", list_km)

    if selected_km:
        df_filtered = df_filtered[df_filtered["Nhóm_KM"].isin(selected_km)]

    # 6️⃣ NHÓM KHOÁN (sheet nhomhang)
    st.sidebar.subheader("🟦 6. Nhóm Khoán")

    list_nk = sorted(df["Nhóm_khoan"].fillna("").unique())
    selected_nk = st.sidebar.multiselect("Chọn nhóm khoán", list_nk)

    if selected_nk:
        df_filtered = df_filtered[df_filtered["Nhóm_khoan"].isin(selected_nk)]

    # 7️⃣ GIÁ TRỊ HỢP ĐỒNG
    st.sidebar.subheader("📜 7. Giá trị hợp đồng")

    list_hd_raw = sorted(df["GiaTri_HD"].fillna(0).unique())

    # Tạo cột hiển thị đẹp
    list_hd_fmt = [f"{int(v):,}" for v in list_hd_raw]

    # Map: format hiển thị → giá trị thật
    hd_map = dict(zip(list_hd_fmt, list_hd_raw))

    selected_hd_fmt = st.sidebar.multiselect("Chọn giá trị hợp đồng", list_hd_fmt)

    # Khi lọc → dùng giá trị thật
    if selected_hd_fmt:
        selected_real = [hd_map[v] for v in selected_hd_fmt]
        df_filtered = df_filtered[df_filtered["GiaTri_HD"].isin(selected_real)]

    # HOÀN TẤT
    st.sidebar.write("---")
    st.sidebar.metric("🔢 Tổng số dòng sau lọc", f"{len(df_filtered):,}")

    return df_filtered