import streamlit as st
from conn import MySQLDatabase
import plotly.express as px
import pandas as pd


# Streamlit App
st.title("Sales Dashboard")
db = MySQLDatabase()

# Load data
sales_data = db.load_sales_data()

# Filter Options
salespersons = sales_data['salesperson_name'].unique()
clients = sales_data['client_name'].unique()
months = sales_data['month_year'].unique()

# Sidebar filters
selected_salesperson = st.sidebar.selectbox("Select Salesperson", ["All"] + list(salespersons))
selected_client = st.sidebar.selectbox("Select Client", ["All"] + list(clients))
selected_month = st.sidebar.selectbox("Select Month", ["All"] + list(months))

# Filter data
filtered_data = sales_data.copy()
if selected_salesperson != "All":
    filtered_data = filtered_data[filtered_data['salesperson_name'] == selected_salesperson]
if selected_client != "All":
    filtered_data = filtered_data[filtered_data['client_name'] == selected_client]
if selected_month != "All":
    filtered_data = filtered_data[filtered_data['month_year'] == selected_month]

# KPIs
st.header("Key Performance Indicators")
total_sales = filtered_data['total_amount'].sum()
top_salesperson = filtered_data.groupby('salesperson_name')['total_amount'].sum().idxmax()
top_client = filtered_data.groupby('client_name')['total_amount'].sum().idxmax()


st.markdown(f"<h3 style='font-size:24px;'>Total Sales: <span style='color:green;'>Ksh{total_sales:,.2f}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:24px;'>Top Salesperson: <span style='color:green;'>{top_salesperson}</span></h3>", unsafe_allow_html=True)
st.markdown(f"<h3 style='font-size:24px;'>Top Client: <span style='color:green;'>{top_client}</span></h3>", unsafe_allow_html=True)


# Monthly Sales Trends
st.header("Monthly Sales Trends")
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


# Top Salespersons
st.header("Top Salespersons")
if not filtered_data.empty:
    top_salespersons = filtered_data.groupby('salesperson_name')['total_amount'].sum().reset_index()
    top_salespersons = top_salespersons.sort_values('total_amount', ascending=False)
    fig = px.bar(top_salespersons, x='salesperson_name', y='total_amount', title="Top Salespersons")
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")

# Top Clients
st.header("Top Clients")
if not filtered_data.empty:
    top_clients = filtered_data.groupby('client_name')['total_amount'].sum().reset_index()
    top_clients = top_clients.sort_values('total_amount', ascending=False)
    fig = px.bar(top_clients, x='client_name', y='total_amount', title="Top Clients")
    st.plotly_chart(fig)
else:
    st.write("No data available for the selected filters.")

# Display Filtered Data
st.header("Filtered Sales Data")
st.dataframe(filtered_data)