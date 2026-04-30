import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# ========================
# CONFIG PAGE
# ========================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# ========================
# LOAD DATA
# ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "main_data.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df = load_data()

# ========================
# TITLE
# ========================
st.title("📊 Dashboard Analisis E-Commerce")
st.markdown("Analisis tren penjualan, kategori produk, dan segmentasi pelanggan")

# ========================
# SIDEBAR FILTER
# ========================
st.sidebar.header("Filter Data")

tahun = st.sidebar.selectbox(
    "Pilih Tahun",
    sorted(df['order_purchase_timestamp'].dt.year.unique())
)

df_filtered = df[df['order_purchase_timestamp'].dt.year == tahun]

# ========================
# KPI
# ========================
total_order = df_filtered['order_id'].nunique()
total_revenue = df_filtered['payment_value'].sum()

col1, col2 = st.columns(2)

col1.metric("Total Order", f"{total_order:,}")
col2.metric("Total Revenue", f"{total_revenue:,.0f}")

# ========================
# 📈 PERTANYAAN 1
# ========================
st.subheader("📈 Tren Jumlah Order dan Total Payment")

trend = df_filtered.groupby(
    df_filtered['order_purchase_timestamp'].dt.to_period('M')
).agg({
    'order_id': 'nunique',
    'payment_value': 'sum'
}).reset_index()

trend['order_purchase_timestamp'] = trend['order_purchase_timestamp'].astype(str)

fig, ax1 = plt.subplots(figsize=(14,6))

# jumlah order
ax1.plot(trend['order_purchase_timestamp'], trend['order_id'], marker='o')
ax1.set_ylabel("Jumlah Order")

# total payment
ax2 = ax1.twinx()
ax2.plot(trend['order_purchase_timestamp'], trend['payment_value'], linestyle='--')
ax2.set_ylabel("Total Payment")

plt.xticks(rotation=45)
plt.title(f"Tren Order & Payment Tahun {tahun}")
plt.grid()

st.pyplot(fig)

# ========================
# 🏆 PERTANYAAN 2
# ========================
st.subheader("🏆 Top 5 Kategori Produk (Revenue Tertinggi)")

top_product = df_filtered.groupby('product_category_name')['payment_value'] \
    .sum().sort_values(ascending=False).head(5)

st.bar_chart(top_product)

# ========================
# 👥 RFM ANALYSIS
# ========================
st.subheader("👥 Segmentasi Pelanggan (RFM Analysis)")

latest_date = df_filtered['order_purchase_timestamp'].max()

rfm = df_filtered.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,
    'order_id': 'nunique',
    'payment_value': 'sum'
}).reset_index()

rfm.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

# scoring
rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=5 - pd.Series(range(5)))
rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=False) + 1
rfm['M_score'] = pd.qcut(rfm['Monetary'], 5, labels=False) + 1

rfm['RFM_score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)

# segmentasi
def segment(row):
    if row['RFM_score'] >= '444':
        return 'Best Customers'
    elif row['RFM_score'] >= '333':
        return 'Loyal Customers'
    elif row['RFM_score'] >= '222':
        return 'Potential'
    else:
        return 'At Risk'

rfm['Segment'] = rfm.apply(segment, axis=1)

segment_count = rfm['Segment'].value_counts()

st.bar_chart(segment_count)

# ========================
# 📊 INSIGHT DINAMIS
# ========================
st.subheader("INSIGHT DINAMIS")

# peak month
peak = trend.loc[trend['order_id'].idxmax()]

# top category
top_category = top_product.idxmax()
top_value = top_product.max()


st.markdown(f"""### 📈 Performa Tahun {tahun}
- Puncak order terjadi pada **{peak['order_purchase_timestamp']}**
- Jumlah order tertinggi mencapai **{int(peak['order_id'])} transaksi**

### 🏆 Produk Unggulan
- Kategori terbaik adalah **{top_category}**
- Total revenue mencapai sekitar **{top_value:,.0f}**

### 👥 Pelanggan
- Segmentasi RFM menunjukkan distribusi pelanggan berdasarkan nilai transaksi
- Fokus bisnis dapat diarahkan ke **Best Customers** dan **Loyal Customers**

### Kesimpulan
- Terdapat pola penjualan musiman
- Produk unggulan berkontribusi besar terhadap revenue
- Segmentasi pelanggan dapat digunakan untuk strategi marketing
""")

# ========================
# FOOTER
# ========================
st.markdown("---")
st.caption("Feni Dwi Lestari | Data Analysis Project")