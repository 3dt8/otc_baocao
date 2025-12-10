# report_simple.py → BẢN HOÀN CHỈNH CUỐI CÙNG (CÓ CỘT TỔNG CỘNG CHO 3 BẢNG)
import streamlit as st
import pandas as pd
from utils import fmt
import io

def df_to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def add_total_row_stt(df, label_col="Name"):
    """Thêm STT + dòng Tổng cộng – SIÊU AN TOÀN"""
    df = df.copy().reset_index(drop=True)

    if "STT" not in df.columns:
        df.insert(0, "STT", range(1, len(df) + 1))

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    total_values = df[numeric_cols].sum()

    total_dict = {"STT": "", "Customer": "", label_col: "TỔNG CỘNG"}
    total_dict.update(dict(zip(numeric_cols, total_values)))
    for col in df.columns:
        if col not in total_dict:
            total_dict[col] = ""

    total_row = pd.DataFrame([total_dict])[df.columns]
    result = pd.concat([df, total_row], ignore_index=True)
    return result

# ===================================================================
def render_report(df, df_hcl=None):   # ← THÊM df_hcl=None
    st.header("BÁO CÁO DOANH SỐ OTC")

    # ==================== 1. Doanh số theo từng tháng + TỔNG CỘNG ====================
    st.subheader("1. Doanh số theo từng tháng")
    df_thang = df.copy()
    df_thang["Tháng"] = df_thang["Billing Date"].dt.month

    pivot_thang = (
        df_thang.groupby(["Customer", "Name", "Tháng"])["DoanhSo"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    pivot_thang.columns = ["Customer", "Name"] + [f"T{int(col)}" for col in pivot_thang.columns[2:]]

    # THÊM CỘT TỔNG CỘNG CHO TỪNG KHÁCH HÀNG
    month_cols = [c for c in pivot_thang.columns if c.startswith("T")]
    pivot_thang["Tổng cộng"] = pivot_thang[month_cols].sum(axis=1)

    df1 = add_total_row_stt(pivot_thang, "Name")
    df_show1 = df1.copy()
    for col in df_show1.columns[3:]:
        df_show1[col] = df_show1[col].apply(fmt)

    st.dataframe(df_show1, use_container_width=True, hide_index=True)
    st.download_button(
        label="Xuất Excel – Doanh số theo tháng",
        data=df_to_excel_bytes(df1),
        file_name="DoanhSo_TheoThang.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ==================== 2. Doanh số theo Nhóm KM + TỔNG CỘNG ====================
    st.subheader("2. Doanh số theo Nhóm KM (Level 2)")
    pivot_km = df.pivot_table(
        index=["Customer", "Name"],
        columns="Nhóm_KM",
        values="DoanhSo",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    groups = ['01', '02', '03', '04', '05']
    available = [g for g in groups if g in pivot_km.columns]

    if available:
        df_km = pivot_km[["Customer", "Name"] + available].copy()
        df_km.rename(columns={g: f"Doanh số Nhóm KM {g}" for g in available}, inplace=True)

        # THÊM CỘT TỔNG CỘNG
        km_cols = [c for c in df_km.columns if "Doanh số Nhóm KM" in c]
        df_km["Tổng cộng"] = df_km[km_cols].sum(axis=1)

        df2 = add_total_row_stt(df_km, "Name")
        df_show2 = df2.copy()
        for col in df_show2.columns[3:]:
            df_show2[col] = df_show2[col].apply(fmt)

        st.dataframe(df_show2, use_container_width=True, hide_index=True)
        st.download_button(
            label="Xuất Excel – Nhóm KM",
            data=df_to_excel_bytes(df2),
            file_name="DoanhSo_NhomKM.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Không có dữ liệu Nhóm KM 01-05")

    # ==================== 3. Tiến độ hợp đồng theo Quý (giữ nguyên) ====================
    st.subheader("3. Tiến độ hợp đồng theo Quý")
    df_q = df.copy()
    df_q["Quý"] = ((df_q["Billing Date"].dt.month - 1) // 3) + 1

    pivot_q = df_q.pivot_table(
        index=["Customer", "Name", "GiaTri_HD"],
        columns="Quý",
        values="DoanhSo",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    for q in [1,2,3,4]:
        if q not in pivot_q.columns:
            pivot_q[q] = 0

    pivot_q["Tổng"] = pivot_q[[1,2,3,4]].sum(axis=1)
    for q in [1,2,3,4]:
        pivot_q[f"Tỷ lệ Q{q}"] = pivot_q.apply(
            lambda r: round(r[q] / (r["GiaTri_HD"]/4), 3) if r["GiaTri_HD"] > 0 else 0, axis=1
        )
    pivot_q["_Tỷ lệ Tổng"] = pivot_q.apply(
        lambda r: round(r["Tổng"] / r["GiaTri_HD"], 3) if r["GiaTri_HD"] > 0 else 0, axis=1
    )

    df3 = add_total_row_stt(pivot_q, "Name")
    df_show3 = df3.copy()
    for col in ["GiaTri_HD", 1, 2, 3, 4, "Tổng"]:
        if col in df_show3.columns:
            df_show3[col] = df_show3[col].apply(fmt)

    st.dataframe(df_show3, use_container_width=True, hide_index=True)
    st.download_button(
        label="Xuất Excel – Tiến độ Hợp đồng",
        data=df_to_excel_bytes(df3),
        file_name="TienDo_HopDong.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ==================== 4. Doanh số theo Program + TỔNG CỘNG ====================
    st.subheader("4. Doanh số theo Program")
    pivot_prog = df.pivot_table(
        index=["Customer", "Name"],
        columns="Program",
        values="DoanhSo",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    # THÊM CỘT TỔNG CỘNG
    prog_cols = [c for c in pivot_prog.columns if c not in ["Customer", "Name"]]
    pivot_prog["Tổng cộng"] = pivot_prog[prog_cols].sum(axis=1)

    df4 = add_total_row_stt(pivot_prog, "Name")
    df_show4 = df4.copy()
    for col in df_show4.columns[3:]:
        df_show4[col] = df_show4[col].apply(fmt)

    st.dataframe(df_show4, use_container_width=True, hide_index=True)
    st.download_button(
        label="Xuất Excel – Doanh số Program",
        data=df_to_excel_bytes(df4),
        file_name="DoanhSo_Program.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
 # ==================== THÊM MỚI: BẢNG HCL – SKU ====================
    st.markdown("---")
    st.subheader("BẢNG HÀNG CHỦ LỰC (HCL) – TÍNH SKU")

    # Nếu không có sheet hcl → bỏ qua
    if df_hcl is None:
        try:
            df_hcl = pd.read_excel(uploaded, sheet_name="hcl", header=None)
            # Đọc 4 cột đầu: Mã SP | SL Min | Tên SP | Đơn giá
            df_hcl = pd.DataFrame({
                "Material": df_hcl.iloc[:,0].astype(str).str.strip(),
                "SL_Min": pd.to_numeric(df_hcl.iloc[:,1], errors='coerce').fillna(0),
                "Ten_SP": df_hcl.iloc[:,2].astype(str).fillna(""),
                "Don_Gia": pd.to_numeric(df_hcl.iloc[:,3], errors='coerce').fillna(0)
            })
            df_hcl = df_hcl[df_hcl["Material"].str.len() > 0]
        except:
            st.info("Không có sheet 'hcl' → Bỏ qua phần tính SKU")
            return

    if df_hcl.empty:
        st.info("Sheet 'hcl' trống → Không có danh mục Hàng Chủ Lực")
        return

    # Lấy danh sách mã SP trong HCL
    hcl_materials = df_hcl["Material"].tolist()

    # Lọc dữ liệu bán hàng thuộc HCL
    df_hcl_sales = df[df["Material"].isin(hcl_materials)].copy()

    if df_hcl_sales.empty:
        st.info("Không có khách hàng nào mua sản phẩm Hàng Chủ Lực")
        return

    # Gộp số lượng theo KH + Mã SP
    sales_group = df_hcl_sales.groupby(["Customer", "Name", "Material"], as_index=False)["Quantity"].sum()
    sales_group = sales_group.merge(df_hcl[["Material", "SL_Min", "Ten_SP"]], on="Material", how="left")

    # Đánh dấu đạt/không đạt
    sales_group["Dat"] = (sales_group["Quantity"] >= sales_group["SL_Min"]).astype(int)

    # Tính SKU cho từng khách hàng
    sku_per_cust = sales_group.groupby(["Customer", "Name"])["Dat"].sum().reset_index()
    sku_per_cust.rename(columns={"Dat": "SKU"}, inplace=True)

    # Gộp lại để hiển thị
    result = sales_group.merge(sku_per_cust, on=["Customer", "Name"], how="left")

    # Sắp xếp: mỗi khách hàng gom lại, SKU chỉ hiện ở dòng đầu
    result = result.sort_values(["Customer", "Material"])
    final_rows = []
    seen_customers = set()

    for _, row in result.iterrows():
        cust = row["Customer"]
        if cust not in seen_customers:
            seen_customers.add(cust)
            sku_value = row["SKU"]
        else:
            sku_value = ""

        final_rows.append({
            "Mã KH": cust,
            "Tên KH": row["Name"],
            "Mã SP": row["Material"],
            "Tên SP": row["Ten_SP"],
            "Số Lượng": int(row["Quantity"]),
            "SL Min": int(row["SL_Min"]),
            "SKU": sku_value,
            "Đạt": "Có" if row["Dat"] == 1 else "Không"
        })

    df_final = pd.DataFrame(final_rows)

    # Hiển thị đẹp
    df_show = df_final.copy()
    df_show["Số Lượng"] = df_show["Số Lượng"].apply(lambda x: f"{x:,}".replace(",", "."))
    df_show["SL Min"] = df_show["SL Min"].apply(lambda x: f"{x:,}".replace(",", "."))

    # Tô đỏ nếu không đạt
    def highlight_row(row):
        if row["Đạt"] == "Không":
            return ["", "", "", "", "background-color:#ffcccc", "", "", ""]
        return [""] * 8

    st.dataframe(
        df_show.style.apply(highlight_row, axis=1),
        use_container_width=True,
        hide_index=True
    )

    st.success(f"**Đã tính xong SKU cho {len(sku_per_cust)} khách hàng**")
    st.download_button(
        "Xuất Excel – Bảng HCL SKU",
        data=df_to_excel_bytes(df_final),
        file_name="Bang_HCL_SKU.xlsx"
    )