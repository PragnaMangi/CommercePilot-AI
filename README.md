# 🚀 CommercePilot AI

### Agentic Commerce Copilot for Intelligent Shopping

> **Tell it your shopping goal. CommercePilot understands, compares, recommends, manages your cart, and helps you complete checkout.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Frontend](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJavaScript-orange.svg)](#)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](#)
[![AI](https://img.shields.io/badge/AI-Gemini-blue.svg)](#)
[![Payments](https://img.shields.io/badge/Payments-Razorpay-3395FF.svg)](#)

---

## 📌 Overview

**CommercePilot AI** is an **Agentic Commerce Copilot** designed to make online shopping more intelligent, conversational, and goal-oriented.

Instead of forcing users to manually search, compare products, check availability, manage their cart, and proceed through checkout, CommercePilot allows users to express their shopping goal naturally.

For example:

> **"Find me the best laptop under ₹60,000."**

or:

> **"Build me the best gaming setup under ₹80,000."**

The AI agent interprets the user's intent, interacts with commerce APIs, considers budget and inventory, recommends products, manages the cart, and connects the shopping journey to **Razorpay Checkout**.

---

# 🎯 Problem

Traditional e-commerce requires users to perform many steps manually:

1. Search for products
2. Open multiple product pages
3. Compare specifications and prices
4. Check inventory
5. Find alternatives
6. Add products to the cart
7. Calculate the total
8. Proceed to checkout
9. Complete payment

This creates unnecessary friction, especially when users have a **goal rather than a specific product in mind**.

CommercePilot AI aims to turn this process into an intelligent, conversational experience.

---

# 💡 Solution

CommercePilot AI introduces an **agentic layer on top of the commerce system**.

The user communicates with the system using natural language, while the AI agent determines what shopping actions need to be performed.

### Example

Instead of:

> Search → Filter → Compare → Add to Cart → Checkout

The user can simply say:

> **"Find the best laptop under ₹60,000 and add the best option to my cart."**

CommercePilot can then assist with the required commerce operations.

---

# 🤖 Key Features

### 🎙️ Voice Shopping

Users can interact with the shopping assistant using voice input.

### 🤖 Gemini AI Shopping Agent

Gemini provides the intelligence layer for understanding user intent and generating shopping decisions.

### 🧠 Conversation Context

The assistant maintains context within the shopping conversation.

### 💰 Budget-Aware Recommendations

Recommendations can consider the user's specified spending limit.

### ⚖️ Automatic Product Comparison

Products can be compared using information such as:

* Price
* Rating
* Availability
* Product information

### 📦 Inventory-Aware Shopping

The system considers product stock before recommending products.

### 🔄 Smart Alternatives

When a product is unavailable or doesn't fit the user's requirements, the system can suggest alternatives.

### 🛒 Autonomous Cart Management

Products can be added to and managed through the commerce cart.

### 🎯 Goal-Based Shopping

Users can describe an outcome instead of manually searching for individual products.

Example:

> **"Build me the best gaming setup under ₹80,000."**

### 💳 Razorpay Checkout

CommercePilot integrates Razorpay for the payment stage of the shopping journey.

### 📊 Commerce Intelligence

The application provides information such as:

* Cart value
* Number of items
* Order information
* Payment status

---

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       User           │
                    │  Text / Voice Input  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   CommercePilot AI   │
                    │    Frontend UI       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Products             │
                    │ Cart                 │
                    │ Orders               │
                    │ Payments             │
                    └───────┬───────┬──────┘
                            │       │
                 ┌──────────┘       └───────────┐
                 ▼                              ▼
        ┌─────────────────┐             ┌─────────────────┐
        │   Gemini AI     │             │    Database     │
        │ Intelligence    │             │ Products/Orders │
        └─────────────────┘             └─────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │     Razorpay     │
                   │     Checkout     │
                   └──────────────────┘
```

---

# 🔄 Shopping Flow

```text
User Shopping Goal
        ↓
AI Intent Understanding
        ↓
Product Search
        ↓
Budget + Inventory Analysis
        ↓
Recommendations
        ↓
Product Comparison
        ↓
Smart Alternatives
        ↓
Cart Management
        ↓
Order Creation
        ↓
Razorpay Checkout
        ↓
Payment Verification
        ↓
Order Confirmation
```

---

# 🛠️ Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* Responsive UI
* Web Speech API for voice interaction
* Razorpay Checkout

## Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* SQLite

## AI

* Google Gemini
* Agent-based commerce logic
* Natural-language intent understanding

## Payments

* Razorpay Checkout
* Razorpay Orders API
* Server-side payment verification
* Razorpay Test Mode for demonstration

---

# 📁 Project Structure

```text
CommercePilot-AI/
│
├── backend/
│   ├── main.py
│   ├── agent.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   ├── payment.py
│   ├── models.py
│   ├── database.py
│   └── ...
│
├── frontend/
│   └── index.html
│
├── LICENSE
├── README.md
└── requirements.txt
```

---

# ⚙️ Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/PragnaMangi/CommercePilot-AI.git
```

```bash
cd CommercePilot-AI
```

---

## 2. Install backend dependencies

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file in the backend/project directory.

Example:

```env
GOOGLE_API_KEY=your_gemini_api_key

RAZORPAY_KEY_ID=your_razorpay_test_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret

RAZORPAY_TEST_MODE=true
RAZORPAY_TEST_AMOUNT=500
```

### ⚠️ Security

**Never commit your `.env` file or API keys to GitHub.**

Add:

```text
.env
venv/
__pycache__/
*.db
```

to `.gitignore`.

---

# ▶️ Run the Backend

From the backend directory:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🌐 Run the Frontend

Open another terminal:

```bash
cd frontend
```

Run:

```bash
python -m http.server 5500
```

Open:

```text
http://127.0.0.1:5500
```

---

# 💳 Razorpay Test Mode

CommercePilot AI supports Razorpay Test Mode for safely demonstrating the checkout workflow.

In demonstration mode, the application can display the **actual commerce/product value** while using a smaller configured test payment amount for the Razorpay test transaction.

This allows the complete:

```text
Cart → Order → Razorpay → Payment → Verification
```

workflow to be demonstrated without processing the full product value as a real payment.

---

# 🧪 Example Demo

### User:

> Find laptops under ₹60,000

### CommercePilot:

* Searches available products
* Considers price
* Checks inventory
* Displays suitable products

Then the user can ask:

> Compare the best laptops

or:

> Give me cheaper alternatives

Then:

> Add the best one to my cart

Finally:

> Proceed to checkout

The system creates the order and launches Razorpay Checkout.

---

# 🏆 Why CommercePilot AI?

CommercePilot AI is designed to move beyond the traditional **search-and-buy** model.

Instead of simply providing product information, the system introduces an **agentic commerce workflow** where AI can assist with decisions and interact with commerce operations.

### Traditional E-Commerce

```text
Search → Compare → Cart → Checkout
```

### CommercePilot AI

```text
Goal
 ↓
Understand
 ↓
Reason
 ↓
Search
 ↓
Compare
 ↓
Optimize
 ↓
Manage Cart
 ↓
Checkout
```

---

# 🔮 Future Enhancements

Planned enhancements include:

* Multi-agent shopping workflows
* Personalized long-term shopping memory
* Price-drop monitoring
* Automatic deal discovery
* Delivery-time optimization
* Advanced spending analytics
* Multi-store product comparison
* Personalized shopping profiles
* Agent-driven reorder suggestions
* More advanced autonomous purchasing workflows

---

# 👩‍💻 Project

**CommercePilot AI**

Built as an **Agentic Commerce Copilot** combining:

**AI + E-Commerce + Agentic Workflows + Razorpay Payments**

---

# 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

## Version Information

**Version:** 1.0

**Last Updated:** August 2026

**Repository:** [CommercePilot-AI](https://github.com/PragnaMangi/CommercePilot-AI)

---

## Author

**Pragna Mangi**

---

### Built with ❤️ using Python, FastAPI, Gemini AI and Razorpay.
