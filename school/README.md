# School Management Platform - Integrated Suite

This project is a unified, multi-tenant Django application merging the **Library Management System** and the **School Bus Tracker**.

## 🚀 Quick Setup Guide

Follow these steps to get the platform running on your local machine.

### 1. Prerequisites
- Python 3.9+
- MySQL Server
- Twilio Account (for WhatsApp notifications)

### 2. Environment Configuration
Create a `.env` file in the root directory (`school/`) based on `.env.example`.
```env
# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database
DB_NAME=school_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Twilio (For Bus Tracking Notifications)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### 3. Installation
```powershell
# Install dependencies
pip install -r requirements.txt
```

### 4. Database Initialization
Ensure your MySQL server is running, then execute:
```powershell
# 1. Initialize the database schema
python manage.py makemigrations
python manage.py migrate

# 2. Create your administrator account
# (Default admin created: admin / admin123)
python manage.py createsuperuser
```

### 5. Running the Application
```powershell
python manage.py runserver
```
Visit `http://localhost:8000/` to see the integrated landing page.

---

## 🏗 Architecture & Modules
- **Accounts & RBAC**: Unified user model with dynamic roles and permissions.
- **Library & Lab**: Management of physical volumes, equipment, bookings, and fines.
- **Inventory**: End-to-end procurement (PO/GRN) that feeds into Library/Lab catalogs.
- **Bus Tracker**: Real-time fleet tracking, student route mapping, and automated WhatsApp alerts.

### Documentation Files
Detailed diagrams and plans are available in the `docs/` folder:
- **DFD**: `docs/dfd.md` (Data Flow Diagram)
- **ERD**: `docs/erd.md` (Entity Relationship Diagram)
- **Implementation**: `docs/implementation_plan.md`

---
**Note**: This project follows a "Security First" approach with Multi-Tenant scoping for sensitive transport data.
