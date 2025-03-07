import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Langkah 1: Membuat Helper Function
# Ini berfungsi untuk menyiapkan DataFrame yang akan digunakan dalam membuat visualisasi data.

# 1. Fungsi helper `create_bycity_df()` digunakan untuk menyiapkan bycity_df
def create_bycity_df(df):
  bycity_df = df.groupby(by='customer_city')['customer_id'].nunique().reset_index()
  bycity_df.rename(columns={
    'customer_id': 'customer_count'
  }, inplace=True)
  return bycity_df

# 2. Fungsi helper `create_bystate_df()` digunakan untuk menyiapkan bystate_df
def create_bystate_df(df):
  bystate_df = df.groupby(by='customer_state')['customer_id'].nunique().reset_index()
  bystate_df.rename(columns={
    'customer_id': 'customer_count'
  }, inplace=True)
  return bystate_df

# 3. Fungsi helper `create_product_performance_df()` digunakan untuk menyiapkan product_performance_df
def create_product_performance_df(df):
  product_performance_df = df.groupby(by='product_category_name_english')['product_id'].nunique().reset_index()
  product_performance_df.rename(columns={
    'product_category_name_english': 'product_name',
    'product_id': 'total_item'
  }, inplace=True)
  return product_performance_df

# 4. Fungsi helper `create_product_revenue_df()` digunakan untuk menyiapkan product_revenue_df
def create_product_revenue_df(df):
  product_revenue_df = df.groupby(by='product_category_name_english')['price'].sum().reset_index()
  product_revenue_df.rename(columns={
    'product_category_name_english': 'product_name',
    'price': 'total_revenue'
  }, inplace=True)
  return product_revenue_df

# 5. Fungsi helper `create_rfm_df` digunakan untuk menyiapkan rfm_df
def create_rfm_df(df):
  rfm_df = df.groupby(by='customer_id', as_index=False).agg({
    'order_purchase_timestamp': 'max',
    'order_id': 'nunique',
    'price': 'sum'
  })
  rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']

  rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
  recent_date = df['order_purchase_timestamp'].dt.date.max()
  rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
  rfm_df.drop('max_order_timestamp', axis=1, inplace=True)

  return rfm_df

# Langkah 2: Melakukan Load Data

all_df = pd.read_csv('main_data.csv')

datetime_columns = ['order_purchase_timestamp']
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column], format='mixed')

# Langkah 3: Membuat Komponen Filter

min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
  # Mengambil start_date & end_date dari date_input
  start_date, end_date = st.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
  )

main_df = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) &
                (all_df['order_purchase_timestamp'] <= str(end_date))]

bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
product_performance_df = create_product_performance_df(main_df)
product_revenue_df = create_product_revenue_df(main_df).sort_values(by='total_revenue', ascending=False)
rfm_df = create_rfm_df(main_df)

# Langkah 4: Melengkapi Dashboard dengan Visualisasi Data

st.header('Proyek Akhir Dicoding: Dashboard Analysis (E-Commerce Dataset) :sparkles:')

# Menampilkan demografi pelanggan
st.subheader('Demografi Pelanggan')

fig, ax = plt.subplots(figsize=(25,15))
colors = ['#FF5733', '#3498db', '#3498db', '#3498db', '#3498db']

sns.barplot(
  y='customer_count',
  x='customer_city',
  data=bycity_df.sort_values(by='customer_count', ascending=False).head(5),
  palette=colors,
  ax=ax    
)

ax.set_title('5 Kota dengan Jumlah Pelanggan Terbanyak', loc='center', fontsize=50)
ax.set_ylabel('Pelanggan (Orang)', fontsize=35)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)
  
fig, ax = plt.subplots(figsize=(25,15))

sns.barplot(
  y='customer_count',
  x='customer_state',
  data=bystate_df.sort_values(by='customer_count', ascending=False).head(5),
  palette=colors,
  ax=ax    
)

ax.set_title('5 Negara Bagian dengan Jumlah Pelanggan Terbanyak', loc='center', fontsize=50)
ax.set_ylabel('Pelanggan (Orang)', fontsize=35)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

# Menampilkan performa penjualan item produk di pasar
st.subheader('Performa Penjualan Produk di Pasar')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35,15))

sns.barplot(x='total_item', y='product_name', data=product_performance_df.sort_values(by='total_item', ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel('Total Penjualan', fontsize=35)
ax[0].set_title('Produk yang Paling Laku di Pasar', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x='total_item', y='product_name', data=product_performance_df.sort_values(by='total_item', ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel('Total Penjualan', fontsize=35)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_title('Produk yang Tidak Terlalu Laku di Pasar', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Menampilkan produk yang menyumbang pendapatan terbesar
st.subheader('4 Produk Teratas Penyumbang Pendapatan Terbesar')

fig, ax = plt.subplots(figsize=(20,15))

products = product_revenue_df['product_name'].head(4)
total_revenue = product_revenue_df['total_revenue'].head(4)
colors = ('#8B4513', '#FFF8DC', '#93C572', '#E67F0D')
explode = (0.05, 0, 0, 0)

wedges, texts, autotexts = ax.pie(
  x=total_revenue,
  explode=explode,
  labels=products,
  colors=colors,
  autopct=lambda p: f'${p * sum(total_revenue) / 100:,.0f}',
  textprops={'fontsize': 20}
)

for text in texts:
  text.set_fontsize(22)

for autotext in autotexts:
  autotext.set_fontsize(22)

st.pyplot(fig)

# Menampilkan rata-rata nilai parameter RFM (Recency, Frequency, & Monetary)
st.subheader('Pelanggan Terbaik Menurut Parameter RFM (customer_id)')

row1, row2, row3 = st.columns(3)

with row1:
  avg_recency = round(rfm_df['recency'].mean(), 1)
  st.metric('Average Recency (days)', value=avg_recency)

with row2:
  avg_frequency = round(rfm_df['frequency'].mean(), 2)
  st.metric('Average Frequency', value=avg_frequency)

with row3:
  avg_monetary = format_currency(rfm_df['monetary'].mean(), 'BRL', locale='pt_BR')
  st.metric('Average Monetary', value=avg_monetary)

fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(8,15))
colors = ['#3498db', '#3498db', '#3498db', '#3498db', '#3498db']

sns.barplot(x='recency', y='customer_id', data=rfm_df.sort_values(by='recency', ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel('customer_id', fontsize=20)
ax[0].set_xlabel(None)
ax[0].set_title('By Recency(days)', loc='center', fontsize=23)
ax[0].tick_params(axis='x', labelsize=12)
ax[0].tick_params(axis='y', labelsize=12)

sns.barplot(x='frequency', y='customer_id', data=rfm_df.sort_values(by='frequency', ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel('customer_id', fontsize=20)
ax[1].set_xlabel(None)
ax[1].set_title('By Frequency', loc='center', fontsize=23)
ax[1].tick_params(axis='x', labelsize=12)
ax[1].tick_params(axis='y', labelsize=12)

sns.barplot(x='monetary', y='customer_id', data=rfm_df.sort_values(by='monetary', ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel('customer_id', fontsize=20)
ax[2].set_xlabel(None)
ax[2].set_title('By Monetary', loc='center', fontsize=23)
ax[2].tick_params(axis='x', labelsize=12)
ax[2].tick_params(axis='y', labelsize=12)

st.pyplot(fig)

st.caption('Copyright (c) Adin Rama Ariyanto Putra 2025')
