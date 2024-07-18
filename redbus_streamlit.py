import streamlit as st
import mysql.connector
import pandas as pd

# Database connection
def create_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="chris",
        database="redbus"
    )
    return connection

def fetch_data():
    connection = create_connection()
    query = "SELECT * FROM bus_routes"
    data = pd.read_sql(query, connection)
    connection.close()
    return data

# Streamlit app
def main():
    st.title("Redbus Data Filtering and Visualization")
    
    # Fetch data
    data = fetch_data()

    if data.empty:
        st.write("No data available.")
    else:
        # Display raw data
        st.write("### Raw Data")
        st.dataframe(data)
        
        # Filter options
        st.sidebar.header("Filter Options")
        unique_routes = data['route_name'].unique()
        selected_routes = st.sidebar.multiselect("Select Route", unique_routes, unique_routes)
        
        unique_bus_types = data['bustype'].unique()
        selected_bus_types = st.sidebar.multiselect("Select Bus Type", unique_bus_types, unique_bus_types)
        
        min_price = int(data['price'].min())
        max_price = int(data['price'].max())
        price_range = st.sidebar.slider("Price Range (INR)", min_price, max_price, (min_price, max_price))
        
        min_rating = float(data['star_rating'].min())
        max_rating = float(data['star_rating'].max())
        rating_range = st.sidebar.slider("Rating Range", min_rating, max_rating, (min_rating, max_rating))
        
        # Filter data
        filtered_data = data[
            (data['route_name'].isin(selected_routes)) &
            (data['bustype'].isin(selected_bus_types)) &
            (data['price'].between(price_range[0], price_range[1])) &
            (data['star_rating'].between(rating_range[0], rating_range[1]))
        ]
        
        # Display filtered data
        st.write("### Filtered Data")
        st.dataframe(filtered_data)
        
        # Visualization
        st.write("### Visualization")
        st.bar_chart(filtered_data.groupby('route_name')['price'].mean())
        st.bar_chart(filtered_data.groupby('bustype')['star_rating'].mean())

if __name__ == "__main__":
    main()