import streamlit as st
from conn import MySQLDatabase


db = MySQLDatabase()
st.title("Salesperson Profiles")

# Fetch all salespersons
salespersons = db.fetch_all_salespersons()['salesperson_name']

# Select a salesperson
selected_salesperson = st.selectbox("Select a Salesperson", salespersons)

if selected_salesperson:
    # Fetch sales trend
    salesperson_sales = db.fetch_salesperson_sales(selected_salesperson)

    # Display salesperson sales trend
    if not salesperson_sales.empty:
        st.subheader(f"Sales Trend for {selected_salesperson}")
        st.line_chart(salesperson_sales.set_index('month_year')['total_sales'])
    else:
        st.write("No sales data available for this salesperson.")

    # Display total sales
    total_sales = db.fetch_salesperson_total_sales(selected_salesperson)
    st.metric("Total Sales", f"Ksh{total_sales:,.2f}")
