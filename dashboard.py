import streamlit as st
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="E-Commerce Customer Behavior Analysis",
    layout="wide"
)

# MongoDB Connection
@st.cache_resource
def init_connection():
    uri = os.getenv("MONGODB_URL")  # Fetch MongoDB URI from environment variables
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client

# Fetch data from MongoDB
def get_data():
    client = init_connection()
    db = client[os.getenv('DB')]  # Fetch database name from environment variables
    
    # Fetch data from collections
    activity_data = list(db.user_activities.find({}, {'_id': 0}))
    order_data = list(db.orders.find({}, {'_id': 0}))
    
    # Convert to DataFrames
    activity_df = pd.DataFrame(activity_data)
    order_df = pd.DataFrame(order_data)
    
    # Convert timestamp to datetime
    if 'timestamp' in activity_df:
        activity_df['timestamp'] = pd.to_datetime(activity_df['timestamp'])
    if 'timestamp' in order_df:
        order_df['timestamp'] = pd.to_datetime(order_df['timestamp'])
    
    return activity_df, order_df

# Load data
activity_df, order_df = get_data()

# Layout
st.title("📊 E-Commerce Customer Behavior Analysis Dashboard")

# First row - Key Metrics
st.subheader("Key Metrics")
col_metrics = st.columns(4)

with col_metrics[0]:
    total_orders = len(order_df)
    st.metric("Total Orders", total_orders)

with col_metrics[1]:
    total_activities = len(activity_df)
    st.metric("Total Activities", total_activities)

with col_metrics[2]:
    unique_products = activity_df['product_name'].nunique()
    st.metric("Unique Products", unique_products)

with col_metrics[3]:
    total_revenue = order_df['total_price'].sum()
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

# Second row - Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Order Timeline")
    if not order_df.empty:
        # Group by date and count orders
        daily_orders = order_df.groupby(order_df['timestamp'].dt.date).size().reset_index()
        daily_orders.columns = ['date', 'count']
        
        # Convert the 'date' column to string format
        daily_orders['date'] = daily_orders['date'].astype(str)
        
        # Create the line chart
        timeline = px.line(
            daily_orders,
            x='date',
            y='count',
            title='Daily Order Count'
        )
        timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Orders",
            xaxis={'type': 'category'}  # Ensure x-axis is treated as categorical
        )
        st.plotly_chart(timeline, use_container_width=True)
    else:
        st.write("No order data available.")

with col2:
    st.subheader("Product Distribution")
    if not activity_df.empty:
        product_dist = activity_df['product_name'].value_counts()
        product_pie = px.pie(
            values=product_dist.values,
            names=product_dist.index,
            title='Top Products Added to Cart'
        )
        st.plotly_chart(product_pie, use_container_width=True)
    else:
        st.write("No activity data available.")

# Third row - Charts
col3, col4 = st.columns(2)

with col3:
    st.subheader("Category Distribution")
    if not activity_df.empty:
        category_dist = activity_df['category'].value_counts()
        category_bar = px.bar(
            x=category_dist.index,
            y=category_dist.values,
            title='Activities by Category'
        )
        category_bar.update_layout(
            xaxis_title="Category",
            yaxis_title="Count"
        )
        st.plotly_chart(category_bar, use_container_width=True)
    else:
        st.write("No activity data available.")

with col4:
    st.subheader("Top Selling Products")
    if not order_df.empty:
        # Flatten cart_items to get product-level details
        order_items = order_df.explode('cart_items')
        order_items = pd.concat([order_items.drop(['cart_items'], axis=1), order_items['cart_items'].apply(pd.Series)], axis=1)
        
        top_products = order_items.groupby('product_name')['quantity'].sum().sort_values(ascending=False).head(10)
        top_products_df = pd.DataFrame(top_products).reset_index()
        top_products_df.columns = ['product_name', 'total_quantity']
        
        top_products_chart = px.bar(
            top_products_df,
            x='product_name',
            y='total_quantity',
            title='Top 10 Selling Products'
        )
        top_products_chart.update_layout(
            xaxis_title="Product",
            yaxis_title="Total Quantity Sold"
        )
        st.plotly_chart(top_products_chart, use_container_width=True)
    else:
        st.write("No order data available.")

# Recent Activity Table
st.subheader("Recent Activities")
if not activity_df.empty:
    recent_activities = activity_df.sort_values('timestamp', ascending=False).head(10)
    st.dataframe(
        recent_activities[['timestamp', 'product_name', 'category', 'price']],
        use_container_width=True
    )
else:
    st.write("No recent activities available.")

# Recent Orders Table
st.subheader("Recent Orders")
if not order_df.empty:
    recent_orders = order_df.sort_values('timestamp', ascending=False).head(10)
    
    # Flatten cart_items for display
    recent_orders_flattened = recent_orders.explode('cart_items')
    recent_orders_flattened = pd.concat([recent_orders_flattened.drop(['cart_items'], axis=1), recent_orders_flattened['cart_items'].apply(pd.Series)], axis=1)
    
    # Display flattened data
    st.dataframe(
        recent_orders_flattened[['timestamp', 'product_name', 'quantity', 'price']],
        use_container_width=True
    )
else:
    st.write("No recent orders available.")

# Sidebar filters
st.sidebar.title("Filters")
# Date range filter
if not activity_df.empty:
    min_date = activity_df['timestamp'].min().date()
    max_date = activity_df['timestamp'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
else:
    st.sidebar.write("No activity data available for filtering.")