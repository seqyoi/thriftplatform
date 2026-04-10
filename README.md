# AI-Powered Thrift E-Commerce Platform

A full-stack thrift marketplace that enables users to buy and sell second-hand clothing, enhanced with features such as ratings and reviews, filtering, recommendations, and chatbot assistance.



## Problem

Traditional thrift platforms rely heavily on manual input for product listing and categorization. This often leads to:

* Incorrect or inconsistent product categories
* Poor search and filtering experience
* Lack of personalization for users

---

## 💡 Solution

This platform provides an intelligent thrift marketplace with integrated AI features to improve usability and user experience:


* **Smart Search & Filtering**
  Dynamically displays relevant products based on user queries

* **Chatbot Assistance**
  Helps users navigate the platform and get quick responses

* **Recommendation System**
  Suggests relevant items based on user activity

---

##  Features

* User authentication (login/signup/logout)
* Product listing with image upload
* Category-based browsing
* Search functionality
* User reviews and ratings
* Recommendation system
* Chatbot integration

---

## 🛠️ Tech Stack

### Backend

* Django
* Python

### Frontend

* HTML, CSS, JavaScript

### Database

* SQLite (can be extended to PostgreSQL)

## ⚙️ Installation & Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name
   ```

2. Navigate to project directory:

   ```bash
   cd your-repo-name
   ```

3. Create virtual environment:

   ```bash
   python -m venv venv
   ```

4. Activate environment:

   ```bash
   venv\Scripts\activate   # Windows
   source venv/bin/activate # Mac/Linux
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Run migrations:

   ```bash
   python manage.py migrate
   ```

7. Start server:

   ```bash
   python manage.py runserver
   ```

---

## 🔄 How It Works

1. User signs up or logs in providing their credentials
2. after authentication, they can browse the platform interactively
3. User can buy listed products as well as list their products on sale in the platform
4. Users can search, browse, and interact
5. Users can rate and review each product

---


## 🚀 Future Improvements

* Improve model accuracy with larger dataset
* Add payment integration
* Enhance recommendation system

---

## 👤 Authors 
-Cilus Duwadi, Juniper Poudyal, Sujina Shrestha
Undergraduate Computer Engineering Student 

---

## 📌 Note

This project is developed as part of an undergraduate project to explore the integration of machine learning with full-stack web development.
