import streamlit as st
from itertools import cycle
from confluent_kafka import Producer
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
sys.path.append("F:\\Data Engineering\\kafka_fraud_detection")

# Load environment variables
load_dotenv()

# Kafka configuration
conf = {
    'bootstrap.servers': os.getenv("bootstrap_server"), 
    'security.protocol': 'SASL_SSL',    
    'sasl.mechanisms': 'PLAIN',     
    'sasl.username': os.getenv("api_key"),     
    'sasl.password': os.getenv("api_secret"), 
}

# Create a producer instance
producer = Producer(conf)

# Topic to produce messages to
topic = os.getenv("topic")

# Page configuration
st.set_page_config(
    page_title="My E-Commerce Store",
    page_icon="🎁",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .product-card img {
        max-width: 100%;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Product data with valid names
products = [
    # Books
    {"id": i, "name": name, "price": price, "image": f"https://via.placeholder.com/150?text={name.replace(' ', '+')}", "description": desc, "category": "Books"}
    for i, (name, price, desc) in enumerate([
        ("Atomic Habits", 15.99, "Transform your habits and change your life."),
        ("The Power of Now", 13.99, "A guide to spiritual enlightenment."),
        ("The 5 AM Club", 14.99, "Own your morning, elevate your life."),
        ("Think and Grow Rich", 12.99, "Classic book on success mindset."),
        ("The Subtle Art of Not Giving a F*ck", 16.99, "A counterintuitive approach to living a good life."),
        ("You Are a Badass", 14.49, "How to stop doubting and start living."),
        ("Daring Greatly", 17.49, "The power of vulnerability."),
        ("Grit", 18.99, "Passion and perseverance for long-term goals."),
        ("Mindset", 19.99, "The new psychology of success."),
        ("Can't Hurt Me", 20.99, "Master your mind and defy the odds.")
    ], 1)
] + [
    # Electronics
    {"id": i, "name": name, "price": price, "image": f"https://via.placeholder.com/150?text={name.replace(' ', '+')}", "description": desc, "category": "Electronics"}
    for i, (name, price, desc) in enumerate([
        ("iPhone 15", 999.99, "Latest Apple iPhone with A17 chip."),
        ("Samsung Galaxy S24", 899.99, "Flagship smartphone from Samsung."),
        ("MacBook Pro", 1299.99, "Apple's latest powerful laptop."),
        ("Sony WH-1000XM5", 349.99, "Noise-canceling wireless headphones."),
        ("iPad Air", 599.99, "Powerful tablet from Apple."),
        ("Dell XPS 15", 1399.99, "High-performance laptop from Dell."),
        ("Bose QuietComfort 45", 329.99, "Premium noise-canceling headphones."),
        ("GoPro Hero 11", 499.99, "Action camera for adventurers."),
        ("Nintendo Switch", 299.99, "Hybrid gaming console."),
        ("Kindle Paperwhite", 129.99, "E-reader with glare-free display.")
    ], 11)
] + [
    # Fashion
    {"id": i, "name": name, "price": price, "image": f"https://via.placeholder.com/150?text={name.replace(' ', '+')}", "description": desc, "category": "Fashion"}
    for i, (name, price, desc) in enumerate([
        ("Nike Air Max", 149.99, "Comfortable and stylish sneakers."),
        ("Adidas Ultraboost", 179.99, "Premium running shoes."),
        ("Levi's 501 Jeans", 69.99, "Classic straight fit jeans."),
        ("Ray-Ban Aviators", 129.99, "Iconic sunglasses for a cool look."),
        ("Casio G-Shock Watch", 99.99, "Durable and stylish wristwatch."),
        ("North Face Jacket", 199.99, "Warm and waterproof winter jacket."),
        ("Michael Kors Handbag", 249.99, "Elegant designer handbag."),
        ("Polo Ralph Lauren Shirt", 89.99, "Casual and sophisticated shirt."),
        ("Timberland Boots", 159.99, "Classic outdoor boots."),
        ("Fossil Leather Wallet", 49.99, "Premium leather wallet.")
    ], 21)
] + [
    # Digital Subscriptions
    {"id": i, "name": name, "price": price, "image": f"https://via.placeholder.com/150?text={name.replace(' ', '+')}", "description": desc, "category": "Digital Subscriptions"}
    for i, (name, price, desc) in enumerate([
        ("Netflix Premium", 15.99, "Unlimited movies and TV shows."),
        ("Spotify Family", 14.99, "Ad-free music streaming for the family."),
        ("Amazon Prime", 12.99, "Fast delivery and streaming benefits."),
        ("Disney+", 7.99, "Stream Disney, Pixar, Marvel, and Star Wars."),
        ("Adobe Creative Cloud", 52.99, "Suite of creative apps."),
        ("Microsoft 365", 69.99, "Office apps and cloud storage."),
        ("YouTube Premium", 11.99, "Ad-free videos and music."),
        ("Audible", 14.95, "Unlimited audiobooks and podcasts."),
        ("NYTimes Digital", 9.99, "Unlimited news articles online."),
        ("PlayStation Plus", 9.99, "Online gaming and free monthly games.")
    ], 31)
]

# Initialize session state for cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

def delivery_callback(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def log_activity(event_type, product):
    event = {
        "event_type": event_type,
        "product_id": product["id"],
        "product_name": product["name"],
        "category": product["category"],
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        producer.produce(topic, key=str(product["id"]), value=json.dumps(event), callback=delivery_callback)
    except Exception as e:
        print(f"Error producing message: {e}")

    producer.flush(timeout=10)  # Add a timeout to avoid indefinite blocking
    print("All messages sent to Kafka")

def remove_from_cart(product_id):
    if product_id in st.session_state.cart:
        del st.session_state.cart[product_id]
        st.success("Item removed from cart!")

def update_quantity(product_id, quantity_change):
    if product_id in st.session_state.cart:
        st.session_state.cart[product_id]["quantity"] += quantity_change
        if st.session_state.cart[product_id]["quantity"] <= 0:
            remove_from_cart(product_id)

def add_to_cart(product):
    if product["id"] in st.session_state.cart:
        st.session_state.cart[product["id"]]["quantity"] += 1
    else:
        st.session_state.cart[product["id"]] = {"product": product, "quantity": 1}
    
    log_activity("add_to_cart", product)  # Log activity
    st.success(f"{product['name']} added to cart!")

# Display products by category
# Display products by category
categories = set([p["category"] for p in products])
for category in categories:
    st.header(category)
    category_products = [p for p in products if p["category"] == category]
    cols = cycle(st.columns(5))
    for product in category_products:
        with next(cols):
            with st.container():
                st.image(product["image"], use_container_width=True)  # Updated parameter
                st.subheader(product["name"])
                st.write(product["description"])
                st.write(f"**Price:** ${product['price']}")
                if st.button(f"Add to Cart 🛒", key=f"add_{product['id']}"):
                    add_to_cart(product)

# Shopping cart sidebar
st.sidebar.title("🛒 Shopping Cart")
if st.session_state.cart:
    total = 0
    for product_id, item in st.session_state.cart.items():
        product = item["product"]
        quantity = item["quantity"]
        total += product["price"] * quantity

        # Display cart item with +, -, quantity, and delete buttons
        st.sidebar.markdown(f"<div class='cart-item'>", unsafe_allow_html=True)
        st.sidebar.write(f"**{product['name']}** (${product['price']} each)")
        col1, col2, col3, col4 = st.sidebar.columns([1, 2, 1, 1])
        with col1:
            if st.button(f"➖", key=f"decrease_{product_id}"):
                update_quantity(product_id, -1)
        with col2:
            st.markdown(f"<div class='quantity-display'>{quantity}</div>", unsafe_allow_html=True)
        with col3:
            if st.button(f"➕", key=f"increase_{product_id}"):
                update_quantity(product_id, 1)
        with col4:
            if st.button(f"🗑️", key=f"delete_{product_id}"):
                remove_from_cart(product_id)
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

def log_checkout():
    event = {
        "event_type": "checkout",
        "timestamp": datetime.utcnow().isoformat(),
        "cart_items": [
            {
                "product_id": item["product"]["id"],
                "product_name": item["product"]["name"],
                "quantity": item["quantity"],
                "price": item["product"]["price"]
            }
            for item in st.session_state.cart.values()
        ],
        "total_price": sum(item["product"]["price"] * item["quantity"] for item in st.session_state.cart.values())
    }

    try:
        producer.produce(topic, key="checkout", value=json.dumps(event), callback=delivery_callback)
    except Exception as e:
        print(f"Error producing message: {e}")

    producer.flush(timeout=10)  # Add a timeout to avoid indefinite blocking
    print("All messages sent to Kafka")

    # Clear cart only after successful Kafka message production
    st.session_state.cart = {}
    st.sidebar.success("Thank you for your purchase! Your order has been placed.")

# Shopping cart sidebar
st.sidebar.title("🛒 Shopping Cart")
if st.session_state.cart:
    total = 0
    for product_id, item in st.session_state.cart.items():
        product = item["product"]
        quantity = item["quantity"]
        total += product["price"] * quantity
        st.sidebar.write(f"**{product['name']}** (${product['price']} each) x {quantity}")

    st.sidebar.write(f"**Total:** ${total:.2f}")

    # Checkout button
    if st.sidebar.button("Checkout"):
        log_checkout()  # Log checkout activity
    else:
        st.sidebar.write("Your cart is empty.")
else:
    st.sidebar.write("Your cart is empty.")

# Footer
st.markdown("---")
st.markdown("© 2023 My E-Commerce Store. All rights reserved.")