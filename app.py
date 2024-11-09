import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Securely connect to the PostgreSQL database
def get_connection():
    db_credentials = st.secrets["db_credentials"]
    engine = create_engine(
        f"postgresql+psycopg2://{db_credentials['DB_USER']}:{db_credentials['DB_PASSWORD']}@{db_credentials['DB_HOST']}:{db_credentials['DB_PORT']}/{db_credentials['DB_NAME']}"
    )
    return engine.connect()

# Function to fetch data based on a query
def fetch_data(query):
    with get_connection() as conn:
        return pd.read_sql(query, conn)

# Streamlit app to explore LEGO prices
def main():
    st.title("LEGO Price Explorer")
    st.write("Search and analyze LEGO prices from different stores! Currently on the list are ksp, super_pharm, ace, amigo, and red_pirate")

    # Search by LEGO ID only
    st.subheader("Search by LEGO ID")
    lego_id = st.text_input("Enter LEGO ID:", "")

    # Store filter with lowercase store options
    st.subheader("Filter by Store")
    store_options = ["All Stores", "ksp", "super_pharm", "ace", "amigo", "red_pirate"]
    selected_store = st.selectbox("Select Store:", store_options)

    # Filtering Logic
    query = "SELECT * FROM lego_store_data WHERE TRUE"
    if lego_id:
        query += f" AND lego_id = '{lego_id}'"
    if selected_store != "All Stores":
        query += f" AND store_name = '{selected_store}'"

    lego_data = fetch_data(query)

    if not lego_data.empty:
        st.dataframe(
            lego_data,
            column_config={
                "product_url": st.column_config.LinkColumn("Product Link")
            },
            use_container_width=True,
        )
    else:
        st.write("No data found for the entered criteria.")

    # Sorting and Filtering Options
    st.subheader("Sort and Filter LEGO Prices")
    sort_options = ["price ASC", "price DESC", "store_name ASC", "store_name DESC"]
    selected_sort = st.selectbox("Sort by:", sort_options)
    max_price = st.slider("Filter by maximum price:", min_value=0, max_value=10000, value=500)

    filter_query = f"SELECT * FROM lego_store_data WHERE price <= {max_price}"
    if selected_store != "All Stores":
        filter_query += f" AND store_name = '{selected_store}'"
    filter_query += f" ORDER BY {selected_sort}"
    sorted_filtered_data = fetch_data(filter_query)

    st.write("Filtered & Sorted Results:")
    st.dataframe(
        sorted_filtered_data,
        column_config={
            "product_url": st.column_config.LinkColumn("Product Link")
        },
        use_container_width=True,
    )

    # Top Most Expensive Legos
    st.subheader("Most Expensive Legos")
    top_expensive_query = "SELECT * FROM lego_store_data WHERE price IS NOT NULL ORDER BY price DESC LIMIT 10"
    top_expensive_data = fetch_data(top_expensive_query)
    st.dataframe(
        top_expensive_data,
        column_config={
            "product_url": st.column_config.LinkColumn("Product Link")
        },
        use_container_width=True,
    )

    # Most Cheap Legos
    st.subheader("Cheapest Legos")
    cheap_lego_query = "SELECT * FROM lego_store_data ORDER BY price ASC LIMIT 10"
    cheap_lego_data = fetch_data(cheap_lego_query)
    st.dataframe(
        cheap_lego_data,
        column_config={
            "product_url": st.column_config.LinkColumn("Product Link")
        },
        use_container_width=True,
    )

if __name__ == "__main__":
    main()
