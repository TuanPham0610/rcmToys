import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import random

# Hàm tạo dữ liệu ngẫu nhiên cho từng sản phẩm
def generate_random_data_for_product(product_name):
    return {
        "Số sao": round(random.uniform(1, 5), 1),
        "Số đánh giá": random.randint(1000, 20000),
        "Giá tiêu chuẩn": random.randint(100_000, 10_000_000),
        "Giá cao nhất": random.randint(100_000, 15_000_000),
        "Nhà sản xuất": random.choice(["Công ty A", "Công ty B", "Công ty C", "Công ty D"]),
        "Phiên bản": f"{random.randint(1, 15)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
    }

# Cấu hình ứng dụng
st.set_page_config(page_title="Hệ thống gợi ý sản phẩm", layout="wide")

st.markdown(
    """
    <style>
    .main { background-color: #f8faff; font-family: 'Arial', sans-serif; }
    .stButton>button { margin-top: 10px; background-color: #007bff; color: white; border-radius: 5px; padding: 5px 10px; border: none; }
    .stButton>button:hover { background-color: #0056b3; }
    .product-card { padding: 15px; background: white; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 10px; }
    .product-header { font-weight: bold; font-size: 18px; margin-bottom: 5px; }
    .product-info { font-size: 14px; margin-bottom: 5px; color: #555; }
    .pagination { margin-top: 20px; text-align: center; }
    .pagination button { background-color: #007bff; color: white; border-radius: 5px; padding: 5px 15px; border: none; margin: 0 5px; }
    .pagination button:hover { background-color: #0056b3; }
    .product-similar { margin: 20px 0; }
    .back-button { margin-top: 15px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Tiêu đề ứng dụng
st.title("🎯 Hệ thống gợi ý sản phẩm tương tự")
st.markdown("#### Xem chi tiết sản phẩm và gợi ý tương tự")

try:
    # Đường dẫn file
    file_path = r"E:\TTNT\Project\sampled_item_features.xlsx"
    df = pd.read_excel(file_path)

    # Đổi tên cột
    df.rename(columns={"unique_product_names": "Tên sản phẩm"}, inplace=True)

    # Kiểm tra và lưu dữ liệu ngẫu nhiên trong Session State
    if "product_data" not in st.session_state:
        st.session_state["product_data"] = {
            product: generate_random_data_for_product(product)
            for product in df["Tên sản phẩm"]
        }

    # Chuẩn hóa dữ liệu
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(df.select_dtypes(include=["float64", "int64"]))
    similarity_matrix = cosine_similarity(scaled_features)

    similarity_df = pd.DataFrame(
        similarity_matrix,
        index=df["Tên sản phẩm"],
        columns=df["Tên sản phẩm"]
    )

    # Số sản phẩm mỗi trang
    products_per_page = 10
    total_pages = (len(df) - 1) // products_per_page + 1

    if "selected_product" not in st.session_state:
        st.session_state["selected_product"] = None
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = 1

    if st.session_state["selected_product"] is None:
        st.subheader("📋 Danh sách sản phẩm:")

        # Phân trang
        start_idx = (st.session_state["current_page"] - 1) * products_per_page
        end_idx = start_idx + products_per_page
        current_products = df.iloc[start_idx:end_idx]

        # Hiển thị sản phẩm trên trang hiện tại
        for _, row in current_products.iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div class="product-card">
                        <div class="product-header">{row['Tên sản phẩm']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Xem sản phẩm", key=row["Tên sản phẩm"]):
                    st.session_state["selected_product"] = row["Tên sản phẩm"]

        # Điều hướng phân trang
        st.markdown("<div class='pagination'>", unsafe_allow_html=True)
        if st.button("⬅️ Trang trước") and st.session_state["current_page"] > 1:
            st.session_state["current_page"] -= 1
        st.write(f"Trang {st.session_state['current_page']} / {total_pages}")
        if st.button("➡️ Trang sau") and st.session_state["current_page"] < total_pages:
            st.session_state["current_page"] += 1
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        selected_product = st.session_state["selected_product"]
        st.subheader(f"📌 Chi tiết sản phẩm: **{selected_product}**")

        # Lấy thông tin cố định từ Session State
        product_info = st.session_state["product_data"][selected_product]
        st.markdown(
            f"""
            <div class="product-card">
                <p class="product-info"><b>Số sao:</b> {product_info['Số sao']}</p>
                <p class="product-info"><b>Số đánh giá:</b> {product_info['Số đánh giá']}</p>
                <p class="product-info"><b>Giá tiêu chuẩn:</b> {product_info['Giá tiêu chuẩn']:,} VNĐ</p>
                <p class="product-info"><b>Giá cao nhất:</b> {product_info['Giá cao nhất']:,} VNĐ</p>
                <p class="product-info"><b>Nhà sản xuất:</b> {product_info['Nhà sản xuất']}</p>
                <p class="product-info"><b>Phiên bản:</b> {product_info['Phiên bản']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Hiển thị sản phẩm gợi ý
        st.subheader("📌 Gợi ý sản phẩm tương tự:")
        similar_products = similarity_df.loc[selected_product].sort_values(ascending=False).iloc[1:6]
        for product_name, similarity_score in similar_products.items():
            st.markdown(
                f"""
                <div class="product-similar">
                    <p>{product_name} (Độ tương đồng: {similarity_score:.4f})</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Xem sản phẩm", key=product_name):
                st.session_state["selected_product"] = product_name

        if st.button("🔙 Quay lại danh sách sản phẩm", key="back"):
            st.session_state["selected_product"] = None

except Exception as e:
    st.error(f"⚠️ Lỗi: {str(e)}")
