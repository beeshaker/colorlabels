import streamlit as st
import pandas as pd
from conn import MySQLDatabase
import plotly.express as px

# Streamlit App
st.title("Purchase Analysis Dashboard")

# Initialize Database Connection
db = MySQLDatabase()

# Load Data
purchase_data = db.load_purchase_data()

# Data Cleaning: Convert Columns to Appropriate Data Types
# Handle missing values, remove commas, and ensure numeric columns
try:
    purchase_data['PO Date'] = pd.to_datetime(purchase_data['PO Date'], format='%d/%m/%Y', errors='coerce')
    purchase_data['Amount'] = pd.to_numeric(purchase_data['Amount'].str.replace(',', '', regex=True), errors='coerce')
    purchase_data['Pending Qty'] = pd.to_numeric(purchase_data['Pending Qty'].str.replace(',', '', regex=True), errors='coerce')
    purchase_data['Qty'] = pd.to_numeric(purchase_data['Qty'].str.replace(',', '', regex=True), errors='coerce')
    purchase_data['Rate'] = pd.to_numeric(purchase_data['Rate'].str.replace(',', '', regex=True), errors='coerce')
except Exception as e:
    st.error(f"Error during data type conversion: {e}")

# Fill NaN values to avoid issues during calculations
purchase_data.fillna({'Amount': 0, 'Pending Qty': 0, 'Qty': 0, 'Rate': 0}, inplace=True)

# Filters
suppliers = purchase_data['Supplier Name'].dropna().unique()
items = purchase_data['Item Name'].dropna().unique()

selected_supplier = st.sidebar.selectbox("Select Supplier", ["All"] + list(suppliers))
selected_item = st.sidebar.selectbox("Select Item", ["All"] + list(items))

# Apply Filters
filtered_data = purchase_data.copy()
if selected_supplier != "All":
    filtered_data = filtered_data[filtered_data['Supplier Name'] == selected_supplier]
if selected_item != "All":
    filtered_data = filtered_data[filtered_data['Item Name'] == selected_item]

# KPIs
st.header("Key Performance Indicators")
try:
    total_amount = filtered_data['Amount'].sum()
    total_pending_qty = filtered_data['Pending Qty'].sum()
    average_rate = filtered_data['Rate'].mean()
    
  
    st.markdown(f"<h3 style='font-size:24px;'>Total Purchase Amount: <span style='color:green;'>Ksh{total_amount:,.2f}</span></h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:24px;'>Total Pending Quantity: <span style='color:green;'>{int(total_pending_qty)}</span></h3>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='font-size:24px;'>Average Rate: <span style='color:green;'>Ksh{average_rate:,.2f}</span></h3>", unsafe_allow_html=True)



except Exception as e:
    st.error(f"Error calculating KPIs: {e}")

# Purchase Trend
st.header("Purchase Trends Over Time")
if not filtered_data.empty:
    try:
        trend_data = filtered_data.groupby('PO Date')['Amount'].sum().reset_index()
        fig = px.line(trend_data, x='PO Date', y='Amount', title="Purchase Amount Over Time")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating purchase trends: {e}")
else:
    st.write("No data available for the selected filters.")

# Top Suppliers by Amount
st.header("Top Suppliers by Purchase Amount")
if not filtered_data.empty:
    try:
        top_suppliers = filtered_data.groupby('Supplier Name')['Amount'].sum().reset_index()
        top_suppliers = top_suppliers.sort_values('Amount', ascending=False)
        fig = px.bar(top_suppliers, x='Supplier Name', y='Amount', title="Top Suppliers by Purchase Amount")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating supplier data: {e}")
else:
    st.write("No data available for the selected filters.")

# Display Filtered Data
st.header("Filtered Purchase Data")
try:
    st.dataframe(filtered_data)
except Exception as e:
    st.error(f"Error displaying filtered data: {e}")
