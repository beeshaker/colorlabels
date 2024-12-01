import streamlit as st
import plotly.express as px
import pandas as pd
from conn import MySQLDatabase

st.title("Enhanced Supplier Comparisons")

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

# Sidebar: Supplier Comparison Configuration
suppliers = purchase_data['Supplier Name'].dropna().unique()
selected_suppliers = st.sidebar.multiselect("Select Suppliers to Compare", suppliers, default=suppliers[:3])

comparison_metric = st.sidebar.selectbox(
    "Select Comparison Metric",
    ["Total Amount", "Total Quantity", "Average Rate", "Fulfillment Rate"]
)

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=[purchase_data['PO Date'].min(), purchase_data['PO Date'].max()]
)

# Filter data by selected suppliers and date range
filtered_data = purchase_data[
    (purchase_data['Supplier Name'].isin(selected_suppliers)) &
    (purchase_data['PO Date'] >= pd.to_datetime(start_date)) &
    (purchase_data['PO Date'] <= pd.to_datetime(end_date))
]

# Aggregated Metrics by Supplier
supplier_comparison = filtered_data.groupby('Supplier Name').agg(
    total_amount=('Amount', 'sum'),
    total_qty=('Qty', 'sum'),
    avg_rate=('Rate', 'mean'),
    total_pending_qty=('Pending Qty', 'sum')
).reset_index()

# Calculate additional metrics
supplier_comparison['fulfillment_rate'] = (
    (supplier_comparison['total_qty'] - supplier_comparison['total_pending_qty']) /
    supplier_comparison['total_qty'] * 100
).fillna(0)

# Generate Comparative Chart
st.header("Supplier-Wise Comparative Analysis")
if not supplier_comparison.empty:
    try:
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
        elif comparison_metric == "Fulfillment Rate":
            fig = px.bar(
                supplier_comparison,
                x='Supplier Name',
                y='fulfillment_rate',
                title="Fulfillment Rate by Supplier (%)",
                labels={'fulfillment_rate': 'Fulfillment Rate (%)'}
            )

        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating comparative chart: {e}")
else:
    st.write("No data available for comparative analysis.")

# Trends Visualization
st.header("Supplier Trends Over Time")
if not filtered_data.empty:
    try:
        supplier_trends = filtered_data.groupby(['Supplier Name', 'PO Date']).agg(
            total_amount=('Amount', 'sum')
        ).reset_index()

        fig = px.line(
            supplier_trends,
            x='PO Date',
            y='total_amount',
            color='Supplier Name',
            title="Supplier Trends Over Time",
            labels={'total_amount': 'Total Amount (Ksh)', 'PO Date': 'Date'}
        )
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Error generating trends: {e}")
else:
    st.write("No data available for trend analysis.")

# Monthly Sales Trends
st.header("Monthly Sales Trends")
sales_data = db.load_sales_data()
filtered_data = sales_data.copy()

if not filtered_data.empty:
    sales_trend = filtered_data.groupby('month_year')['total_amount'].sum().reset_index()

    # Correct parsing of `month_year` in the format `YY-MMM` (e.g., 23-Apr)
    sales_trend['month_year'] = pd.to_datetime(sales_trend['month_year'], format='%y-%b')
    
    # Sort by parsed dates
    sales_trend = sales_trend.sort_values('month_year')
    fig = px.line(sales_trend, x='month_year', y='total_amount', title="Sales Over Time")
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")