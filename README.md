# Brick Management System

A comprehensive web application for managing brick orders, manufacturers, orders, and users. This system helps the construction company to efficiently manage their brick supply chain.

## Features

- **User Authentication & Authorization**
  - Secure login and registration
  - Role-based access control (Admin and Regular Users)
  - User management for administrators

- **Brick Management**
  - Add, edit, and view brick details
  - Track brick specifications (color, material, dimensions, etc.)
  - Associate bricks with manufacturers

- **Manufacturer Management**
  - Maintain a database of brick manufacturers
  - Store contact information and address details
  - View all bricks supplied by each manufacturer

- **Order Management**
  - Create and track brick orders
  - Monitor order status (ordered, received, canceled)
  - View order history and expected delivery dates

- **Responsive UI**
  - User-friendly interface
  - Consistent design across all pages

## Technologies Used

- **Backend**
  - Python 3.x
  - Flask 3.0.3 (Web Framework)
  - SQLAlchemy 3.1.0 (ORM)
  - SQLite (Database)
  - Werkzeug 3.0.2 (WSGI Utility Library)

- **Frontend**
  - HTML5
  - CSS3
  - JavaScript
  - Flask Templates (Jinja2)

- **Testing**
  - Pytest 8.4.0

- **Architecture**
  - Model-View-Controller (MVC) pattern
  - Mediator pattern for business logic

## Setup Instructions

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Installation

1. Clone the repository
   ```
   git clone <repository-url>
   cd brick-management-system
   ```

2. Create and activate a virtual environment (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. Install dependencies
   ```powershell
   pip install -r requirements.txt
   ```

4. Initialize the database
   ```powershell
   python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"
   ```

5. Create initial admin user (if not already set up)
   ```powershell
   python -c "from app import app; from models import db, User; from werkzeug.security import generate_password_hash; app.app_context().push(); admin = User(userName='admin', password=generate_password_hash('p4$$w0rd'), isAdmin=True); db.session.add(admin); db.session.commit()"
   ```

## Running the Application

1. Start the Flask development server
   ```powershell
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Default Admin Credentials

- **Username:** admin
- **Password:** p4$$w0rd

## Deployment

The application can be deployed on platforms like Heroku, AWS, or any PaaS that supports Python applications.

Link to deployed app: [Brick Management System](https://muhammadsaeed.pythonanywhere.com/)
