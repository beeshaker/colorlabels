import streamlit as st
from conn import MySQLDatabase

st.title("Client Profiles")

db = MySQLDatabase()

# Fetch all clients
clients = db.fetch_all_clients()['client_name']

# Select a client
selected_client = st.selectbox("Select a Client", clients)

if selected_client:
    # Fetch sales trend
    client_sales = db.fetch_client_sales(selected_client)

    # Display client sales trend
    if not client_sales.empty:
        st.subheader(f"Sales Trend for {selected_client}")
        st.line_chart(client_sales.set_index('month_year')['total_sales'])
    else:
        st.write("No sales data available for this client.")

    # Display total sales
    total_sales = db.fetch_client_total_sales(selected_client)
    st.metric("Total Sales", f"Ksh{total_sales:,.2f}")
