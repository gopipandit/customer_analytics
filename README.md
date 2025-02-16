# customer_analytics# 🛒 E-Commerce Data Engineering Project

## 📌 Overview
This project is a complete **end-to-end data engineering solution** that captures user interactions on an e-commerce platform, processes them in real time, and visualizes key business insights. The system leverages **Streamlit, Kafka, MongoDB, and Power BI** to provide a seamless experience for users while maintaining robust data tracking and analysis.

## 🏗️ Architecture
1. **Frontend (Streamlit)**  
   - A simple yet interactive e-commerce website where users can browse products, add/remove items from the cart, and place orders.
   
2. **Event Logging (Kafka Producer)**  
   - Every user interaction (adding/removing items, checkout) is sent to Kafka topics using a Kafka producer.

3. **Data Processing & Storage (Kafka Consumer + MongoDB)**  
   - A Kafka consumer listens for events, processes them, and stores order data in the `orders` collection and other user activities in the `user_activities` collection in MongoDB.

4. **Analytics & Visualization (Power BI)**  
   - MongoDB data is connected to **Power BI dashboards** to track key business metrics, including:
     - Total orders placed
     - Items added to cart (category-wise trends)
     - Daily revenue and sales trends
     - Most sold items and popular categories

## 🚀 Technologies Used
- **Streamlit** – Interactive frontend for user experience.
- **Apache Kafka** – Real-time event streaming for user interactions.
- **MongoDB** – NoSQL database for storing structured event data.
- **Power BI** – Business intelligence tool for insights and reporting.
- **Python** – Backend logic, event processing, and data ingestion.

## 📊 Power BI Dashboard Highlights
- 📈 **Daily Sales Trends** – Track revenue over time.
- 🛍️ **Most Sold Items** – Identify the most popular products.
- 🔥 **Category-wise Trends** – Understand which product categories are performing well.
- 🛒 **User Engagement** – Monitor how users interact with different products.

## 🎯 Key Takeaways
- Demonstrates **real-time data processing** using Kafka.
- Utilizes **MongoDB** for structured event storage.
- Connects data to **Power BI** for actionable business insights.
- Fully functional **end-to-end data engineering pipeline**.

This project showcases a **real-world data engineering use case**—from **data generation, processing, and storage to analytics and visualization**! 🚀

---

💡 **Future Enhancements**
- Implementing **user authentication** for personalized experiences.
- Expanding to **multiple data sources** for deeper insights.
- Integrating **machine learning models** for product recommendations.

📌 *Feel free to contribute, fork, or enhance this project!*
