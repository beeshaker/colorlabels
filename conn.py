import mysql.connector
from mysql.connector import Error
import pandas as pd


class MySQLDatabase:
    def __init__(self):
        """Initialize database connection settings."""
        
        """
        self.host = "localhost"
        self.user = "root"
        self.password = "pass"
        self.database = "colorlabels"
        self.conn = None
        self.cursor = None
        
        """
        
        
        self.host = "database-1.c9wq6somacoq.ap-south-1.rds.amazonaws.com"
        self.user = "beeshaker"
        self.password = "eNJD7QvFIT1"
        self.database = "colorlabels"
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish a connection to the database."""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.conn.is_connected():
                self.cursor = self.conn.cursor(buffered=True)
                print("Connection to MySQL database successful")
        except Error as e:
            print(f"Error: {e}")
            self.conn = None

    def close(self):
        """Close the connection to the database."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print("Connection closed")

    def load_sales_data(self):
        """Load all sales data from the database."""
        self.connect()
        if not self.conn:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
        query = "SELECT salesperson_name, client_name, month_year, total_amount FROM sales;"
        return pd.read_sql(query, self.conn)

    def fetch_all_clients(self):
        """Fetch all distinct clients from the database."""
        self.connect()
        if not self.conn:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
        query = "SELECT DISTINCT client_name FROM sales ORDER BY client_name;"
        return pd.read_sql(query, self.conn)

    def fetch_all_salespersons(self):
        """Fetch all distinct salespersons from the database."""
        self.connect()
        if not self.conn:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
        query = "SELECT DISTINCT salesperson_name FROM sales ORDER BY salesperson_name;"
        return pd.read_sql(query, self.conn)

    def fetch_client_sales(self, client_name):
        """Fetch sales data for a specific client, grouped by month."""
        self.connect()
        if not self.conn:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
        query = f"""
            SELECT month_year, SUM(total_amount) AS total_sales
            FROM sales
            WHERE client_name = '{client_name}'
            GROUP BY month_year
            ORDER BY STR_TO_DATE(month_year, '%y-%b');
        """
        return pd.read_sql(query, self.conn)

    def fetch_salesperson_sales(self, salesperson_name):
        """Fetch sales data for a specific salesperson, grouped by month."""
        self.connect()
        if not self.conn:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
        query = f"""
            SELECT month_year, SUM(total_amount) AS total_sales
            FROM sales
            WHERE salesperson_name = '{salesperson_name}'
            GROUP BY month_year
            ORDER BY STR_TO_DATE(month_year, '%y-%b');
        """
        return pd.read_sql(query, self.conn)

    def fetch_client_total_sales(self, client_name):
        """Fetch the total sales for a specific client."""
        self.connect()
        if not self.conn:
            return 0  # Return 0 if connection fails
        query = f"""
            SELECT SUM(total_amount) AS total_sales
            FROM sales
            WHERE client_name = '{client_name}';
        """
        result = pd.read_sql(query, self.conn)
        return result['total_sales'][0] if not result.empty else 0

    def fetch_salesperson_total_sales(self, salesperson_name):
        """Fetch the total sales for a specific salesperson."""
        self.connect()
        if not self.conn:
            return 0  # Return 0 if connection fails
        query = f"""
            SELECT SUM(total_amount) AS total_sales
            FROM sales
            WHERE salesperson_name = '{salesperson_name}';
        """
        result = pd.read_sql(query, self.conn)
        return result['total_sales'][0] if not result.empty else 0

    def fetch_sales_in_year(self, year):
        """Fetch all sales for a specific year."""
        self.connect()
        if not self.conn:
            return pd.DataFrame()  # Return an empty DataFrame if connection fails
        query = f"""
            SELECT salesperson_name, client_name, month_year, total_amount
            FROM sales
            WHERE YEAR(STR_TO_DATE(month_year, '%y-%b')) = {year};
        """
        return pd.read_sql(query, self.conn)
    
    #purchases
    def load_purchase_data(self):
        self.connect()
        if not self.conn:
            return pd.DataFrame() 
        
        query = "SELECT * FROM purchase_report;"
        data = pd.read_sql(query, self.conn)

        return data
