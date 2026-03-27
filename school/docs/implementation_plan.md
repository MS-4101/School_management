# Implementation Plan & Documentation - School Management Platform

## 1. Overview
The platform unifies the **Library, Lab, Inventory, and School Bus Tracking** systems into a cohesive Django application (`school`). This eliminates data silos, introduces a unified multi-tenant Role-Based Access Control (RBAC) model, and standardizes the user interface across all modules.

## 2. Core Architecture
- **Framework**: Django 4.2+
- **Database**: MySQL (`school_db`) shared across all modules.
- **Multi-Tenancy**: School-based scoping for the Bus Tracking module via `SchoolTenantMiddleware`.
- **RBAC**: Unified `CustomUser` model inheriting from `AbstractUser`. Includes dynamic permissions (`Role`, `Permission`) for internal modules and static role properties (`is_school_admin`, `is_parent`) for specialized interfaces.

## 3. Integrated Modules
1. **Accounts & RBAC (`apps.accounts`)**: Handles all authentication (sessions & JWT if needed), user management, role assignments, and School entity mappings.
2. **Dashboard (`apps.dashboard`)**: Central unified landing page and routing to role-specific dashboards (Admin, School Admin, Parent).
3. **Library Management (`apps.library_mgmt`)**: Manages book categories, physical copies, patron issuing, fines, and damage logs.
4. **Lab Management (`apps.lab_mgmt`)**: Manages equipment catalogs, specific units, condition tracking, and booking schedules.
5. **Inventory (`apps.inventory`)**: Central purchasing module processing Purchase Orders, Suppliers, and Goods Received Notes (GRNs). Triggers signals to auto-create `BookCopy` or `LabUnit` objects upon receipt.
6. **Buses (`apps.buses`)**: Multi-tenant bus fleet tracking, student route mapping, and daily trip generation with real-time pickup updates.
7. **Notifications (`apps.notifications`)**: WhatsApp communication node bridging bus trip events to Twilio messaging services.

## 4. UI Theme Standardization
- The responsive, modernized **BusTrack Pro** theme is universally applied.
- Classes such as `.form-control`, `.btn-primary`, and color variables (`--gold-dark`, `--success`, `--blue`) replace older template designs.
- Unified UI component library for consistent navbar, dropdowns, dashboards, and modal dialogs.

## 5. Deployment Consideration
- Ensure `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` are valid in the production `.env`.
- Run database migrations (`python manage.py makemigrations` and `python manage.py migrate`).
- Setup an active WhatsApp Sender via Twilio.
- Start standard Django Web Server or Gunicorn for production routing.
