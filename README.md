
# Grocery Delivery System

A full-stack web application designed to facilitate the buying and selling of groceries. Users can create stores (subject to admin approval), manage carts, and perform other standard functionalities found in grocery delivery platforms.

## 🛠️ Tech Stack

- **Backend**: Flask (API development)
- **Frontend**: Django (API consumption and UI rendering)
- **Database**: SQLite
- **Styling**: Bootstrap

## 🚀 Features

- User registration and authentication
- Store creation with admin approval
- Product browsing and searching
- Shopping cart management
- Order placement and tracking

## 📦 Installation & Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Abhay-Kohli27/G31_Grocery_Delivery_System_Flask_Django.git
   cd G31_Grocery_Delivery_System_Flask_Django
   ```

2. **Set up a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**:

   ```bash
   python manage.py migrate
   ```

5. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

6. **Access the application**:

   Open your browser and navigate to `http://localhost:8000/`

## 📁 Project Structure

```
Django_Flask_Final_Repo/
├── grocery_delivery_system_django_final/
│   ├── manage.py
│   ├── ...
├── grocery_delivery_system_flask_final/
│   ├── app.py
│   ├── ...
├── requirements.txt
└── README.md
```

## 👥 User Roles

- **Admin**: Approves store creation requests and manages the platform.
- **User**: Browses products, manages cart, and places orders.

## 🎓 Academic Project

This project was developed as part of an academic web development course to demonstrate proficiency in full-stack development using Flask and Django.
