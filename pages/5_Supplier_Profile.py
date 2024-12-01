import streamlit as st
import plotly.express as px
from conn import MySQLDatabase
import pandas as pd

st.title("Supplier Profiles and Comparative Analysis")

# Initialize Database Connection
db = MySQLDatabase()
purchase_data = db.load_purchase_data()

# Data Cleaning: Convert Columns to Appropriate Data Types
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

# Select Supplier
suppliers = purchase_data['Supplier Name'].dropna().unique()
selected_supplier = st.selectbox("Select a Supplier", suppliers)

# Filter data for the selected supplier
supplier_data = purchase_data[purchase_data['Supplier Name'] == selected_supplier]

# Key Metrics
st.header(f"Key Metrics for {selected_supplier}")
total_qty = supplier_data['Qty'].sum()
total_pending_qty = supplier_data['Pending Qty'].sum()
total_amount = supplier_data['Amount'].sum()
average_rate = supplier_data['Rate'].mean()

# Handle potential NaN values
total_qty = 0 if pd.isna(total_qty) else total_qty
total_pending_qty = 0 if pd.isna(total_pending_qty) else total_pending_qty
total_amount = 0.0 if pd.isna(total_amount) else total_amount
average_rate = 0.0 if pd.isna(average_rate) else average_rate

# Display Metrics
st.markdown(f"<h3 style='font-size:24px;'>Total Purchase Amount: <span style='color:green;'>Ksh{total_amount:,.2f}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:24px;'>Total Pending Quantity: <span style='color:blue;'>{int(total_pending_qty)}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:24px;'>Average Rate: <span style='color:red;'>Ksh{average_rate:,.2f}</span></h3>", unsafe_allow_html=True)

# Supplier Trends: Amount Over Time
st.header(f"Amount Trends for {selected_supplier}")
if not supplier_data.empty:
    try:
        supplier_trend = supplier_data.groupby('PO Date')['Amount'].sum().reset_index()
        fig = px.line(supplier_trend, x='PO Date', y='Amount', title=f"Amount Over Time for {selected_supplier}")
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating amount trends: {e}")
else:
    st.write("No data available for the selected supplier.")

# Comparative Supplier-Wise Charts
st.header("Supplier-Wise Comparative Analysis")
comparison_metric = st.selectbox(
    "Select Comparison Metric",
    ["Total Amount", "Total Quantity", "Average Rate"]
)

if not purchase_data.empty:
    try:
        # Aggregate data by supplier
        supplier_comparison = purchase_data.groupby('Supplier Name').agg(
            total_amount=('Amount', 'sum'),
            total_qty=('Qty', 'sum'),
            avg_rate=('Rate', 'mean')
        ).reset_index()

        # Select metric for comparison
        if comparison_metric == "Total Amount":
            fig = px.bar(
                supplier_comparison,
                x='Supplier Name',
                y='total_amount',
                title="Total Amount by Supplier",
                labels={'total_amount': 'Total Amount (Ksh)'}
            )
        elif comparison_metric == "Total Quantity":
            fig = px.bar(
                supplier_comparison,
                x='Supplier Name',
                y='total_qty',
                title="Total Quantity by Supplier",
                labels={'total_qty': 'Total Quantity'}
            )
        elif comparison_metric == "Average Rate":
            fig = px.bar(
                supplier_comparison,
                x='Supplier Name',
                y='avg_rate',
                title="Average Rate by Supplier",
                labels={'avg_rate': 'Average Rate (Ksh)'}
            )

        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating comparative charts: {e}")
else:
    st.write("No data available for comparative analysis.")

# Display Supplier Data
st.header("Supplier Purchase Data")
try:
    st.dataframe(supplier_data)
except Exception as e:
    st.error(f"Error displaying supplier data: {e}")
