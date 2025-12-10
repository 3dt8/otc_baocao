# engine.py → CHỈ THÊM 2 DÒNG ĐỂ TẢI SHEET HCL + TẠO CỘT QUANTITY
import pandas as pd
import streamlit as st
from utils import to_text_clean, pad_customer_10

def load_data(file):
    try:
        df = pd.read_excel(file, sheet_name="DATA", dtype=str)

        # --- FIX QUAN TRỌNG: convert ngày ---
        df["Billing Date"] = pd.to_datetime(df["Billing Date"], errors="coerce")

        # --- Chuẩn hóa mã ---
        df["Customer"] = df["Customer"].apply(pad_customer_10)
        df["Material"] = df["Material"].apply(to_text_clean)
        df["Mã TDV"] = df["Mã TDV"].apply(to_text_clean)

        # --- Doanh số ---
        df["DoanhSo"] = pd.to_numeric(df.iloc[:, 8], errors="coerce").fillna(0)

        # --- THÊM DÒNG MỚI: SỐ LƯỢNG LÀ CỘT F (index 5) ---
        df["Quantity"] = pd.to_numeric(df.iloc[:, 5], errors="coerce").fillna(0)

        # --- Nhóm KM ---
        df["Product Hierarchy"] = df["Product Hierarchy"].apply(to_text_clean)
        df["Nhóm_KM"] = df["Product Hierarchy"].str[2:4]

        return df

    except Exception as e:
        st.error(f"Lỗi load DATA: {e}")
        return pd.DataFrame()

# Các hàm khác giữ nguyên 100%
def load_hopdong(file):
    try:
        df_hd = pd.read_excel(file, sheet_name="hopdong")
        df_hd["Customer"] = df_hd["Customer"].apply(pad_customer_10)
        df_hd["GiaTri_HD"] = pd.to_numeric(df_hd.iloc[:, 7], errors="coerce").fillna(0)
        df_hd["GT_Da_Xuat"] = pd.to_numeric(df_hd.iloc[:, 8], errors="coerce").fillna(0)
        return df_hd[["Customer", "GiaTri_HD", "GT_Da_Xuat"]]
    except Exception as e:
        st.error(f"Lỗi hopdong: {e}")
        return pd.DataFrame()

def load_nhomhang(file):
    try:
        df_nh = pd.read_excel(file, sheet_name="nhomhang", dtype=str)
        df_nh["Mã sản phẩm"] = df_nh["Mã sản phẩm"].apply(to_text_clean)
        df_nh["Nhóm_khoan"] = df_nh["OTC Product Group"]
        return df_nh[["Mã sản phẩm", "Nhóm_khoan"]]
    except Exception as e:
        st.error(f"Lỗi nhomhang: {e}")
        return pd.DataFrame()

def load_khoan(file):
    try:
        df_k = pd.read_excel(file, sheet_name="khoan", dtype=str)
        df_k["Mã TDV"] = df_k["Mã TDV"].apply(to_text_clean)
        df_k["CT_Nam"] = pd.to_numeric(df_k.iloc[:, 6], errors="coerce").fillna(0)
        for col in df_k.columns[7:]:
            df_k[col] = pd.to_numeric(df_k[col], errors="coerce").fillna(0)
        return df_k
    except Exception as e:
        st.error(f"Lỗi khoan: {e}")
        return pd.DataFrame()

# engine.py → CHỈ SỬA PHẦN LOAD HCL (các phần khác giữ nguyên)
# engine.py → CHỈ THAY PHẦN load_all_data (các hàm khác giữ nguyên)
def load_all_data(file):
    df = load_data(file)
    df_hd = load_hopdong(file)
    df_nh = load_nhomhang(file)
    df_khoan = load_khoan(file)

    # LOAD SHEET HCL – SIÊU AN TOÀN
    try:
        hcl_raw = pd.read_excel(file, sheet_name="hcl", header=None)
        if hcl_raw.shape[1] < 4:
            st.warning("Sheet 'hcl' cần ít nhất 4 cột: Mã SP | SL Min | Tên SP | Đơn giá")
            df_hcl = pd.DataFrame()
        else:
            df_hcl = pd.DataFrame({
                "Material": hcl_raw.iloc[:, 0].astype(str).str.strip(),
                "SL_Min": pd.to_numeric(hcl_raw.iloc[:, 1], errors='coerce').fillna(0),
                "Ten_SP": hcl_raw.iloc[:, 2].astype(str).fillna(""),
                "Don_Gia": pd.to_numeric(hcl_raw.iloc[:, 3], errors='coerce').fillna(0)
            })
            df_hcl = df_hcl[df_hcl["Material"].str.len() > 0].reset_index(drop=True)
    except:
        df_hcl = pd.DataFrame()

    if df.empty:
        return None, None, None, None, df_hcl

    df = df.merge(df_hd, on="Customer", how="left")
    df = df.merge(df_nh, left_on="Material", right_on="Mã sản phẩm", how="left")
    df["Nhóm_khoan"] = df["Nhóm_khoan"].fillna("")

    return df, df_hd, df_nh, df_khoan, df_hcl