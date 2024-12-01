import streamlit as st
import plotly.express as px
from conn import MySQLDatabase
import pandas as pd

st.title("Purchase Item Profiles")

# Initialize Database Connection
db = MySQLDatabase()

# Load Data
purchase_data = db.load_purchase_data()

# Convert Columns to Appropriate Data Types
try:
    purchase_data['PO Date'] = pd.to_datetime(purchase_data['PO Date'], format='%d/%m/%Y', errors='coerce')
    purchase_data['Amount'] = pd.to_numeric(purchase_data['Amount'].str.replace(',', '', regex=True), errors='coerce')
    purchase_data['Rate'] = pd.to_numeric(purchase_data['Rate'].str.replace(',', '', regex=True), errors='coerce')
    purchase_data['Qty'] = pd.to_numeric(purchase_data['Qty'].str.replace(',', '', regex=True), errors='coerce')
    purchase_data['Pending Qty'] = pd.to_numeric(purchase_data['Pending Qty'].str.replace(',', '', regex=True), errors='coerce')
except Exception as e:
    st.error(f"Error during data type conversion: {e}")

# Fill NaN values to avoid issues during calculations
purchase_data.fillna({'Amount': 0, 'Rate': 0, 'Qty': 0, 'Pending Qty': 0}, inplace=True)

# Select Item
items = purchase_data['Item Name'].dropna().unique()
selected_item = st.selectbox("Select an Item", items)

# Filter data for the selected item
item_data = purchase_data[purchase_data['Item Name'] == selected_item]

# Key Metrics
st.header(f"Key Metrics for {selected_item}")
total_qty = item_data['Qty'].sum()
total_pending_qty = item_data['Pending Qty'].sum()
total_amount = item_data['Amount'].sum()
average_rate = item_data['Rate'].mean()

# Handle potential NaN values
total_qty = 0 if pd.isna(total_qty) else total_qty
total_pending_qty = 0 if pd.isna(total_pending_qty) else total_pending_qty
total_amount = 0.0 if pd.isna(total_amount) else total_amount
average_rate = 0.0 if pd.isna(average_rate) else average_rate

# Display Metrics
st.markdown(f"<h3 style='font-size:24px;'>Total Purchase Amount: <span style='color:green;'>Ksh{total_amount:,.2f}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:24px;'>Total Pending Quantity: <span style='color:green;'>{int(total_pending_qty)}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:24px;'>Average Rate: <span style='color:green;'>Ksh{average_rate:,.2f}</span></h3>", unsafe_allow_html=True)

# Item Trends
st.header(f"Trends for {selected_item}")
if not item_data.empty:
    try:
        item_trend = item_data.groupby('PO Date')['Amount'].sum().reset_index()
        fig = px.line(item_trend, x='PO Date', y='Amount', title=f"Amount Over Time for {selected_item}")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating trends: {e}")
else:
    st.write("No data available for the selected item.")

# Display Item Data
st.header("Item Purchase Data")
try:
    st.dataframe(item_data)
except Exception as e:
    st.error(f"Error displaying item data: {e}")
