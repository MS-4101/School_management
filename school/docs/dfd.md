# Data Flow Diagram - School Management Platform

This document illustrates the data flow within the integrated School Management Platform.

```mermaid
graph TD
    %% External Entities
    subgraph Users
        Admin["School Admin\n(Superuser)"]
        Librarian["Librarian"]
        LabAdmin["Lab Administrator"]
        Driver["Bus Driver/Staff"]
        Parent["Parent"]
    end
    
    %% Core System
    subgraph Core System [School Management Platform]
        Auth["Authentication & RBAC App"]
        Access["Access Control Module"]
        Dashboard["Unified Dashboard Module"]
        Library["Library Management App"]
        Lab["Lab Management App"]
        Inventory["Inventory Management App"]
        BusTracker["Bus Tracker App"]
        Notifications["Notifications Service"]
    end
    
    %% Databases
    DB[("School Database\n(MySQL)")]
    
    %% External Service
    Twilio["Twilio API\n(WhatsApp)"]
    
    %% Data Flows
    %% Admin Flows
    Admin -->|Login| Auth
    Admin -->|View Global Stats| Dashboard
    Admin -->|Manage Routes/Buses| BusTracker
    Admin -->|Manage Users & Roles| Access
    Access -->|Configure Permissions| Auth
    Access -->|Create Tenants| DB
    
    %% Librarian Flows
    Librarian -->|Login| Auth
    Librarian -->|Issue/Return Books| Library
    Librarian -->|Track Fines| Library
    
    %% Lab Admin Flows
    LabAdmin -->|Login| Auth
    LabAdmin -->|Book Equipment| Lab
    LabAdmin -->|Log Damages| Lab
    
    %% Driver Flows
    Driver -->|Login (Session)| Auth
    Driver -->|Start Trip & Mark Drops| BusTracker
    
    %% Parent flows
    Parent -->|Login| Auth
    Parent -->|View Child Status| Dashboard
    
    %% Authentication
    Auth <-->|Verify Credentials| DB

    %% App to DB Data storage
    Library <-->|Read/Write Catalog| DB
    Lab <-->|Read/Write Equipment| DB
    Inventory <-->|Read/Write Stock| DB
    BusTracker <-->|Read/Write Trips| DB
    
    %% Inventory module flowing to Library/Lab
    Inventory -->|Fulfills PO & GRN| Library
    Inventory -->|Fulfills PO & GRN| Lab
    
    %% Notification flows
    BusTracker -->|Trip events trigger| Notifications
    Notifications -->|Submit Messages| Twilio
    Twilio -->|WhatsApp Delivery| Parent
    Notifications -->|Log Status| DB
    
    %% Dashboard Aggregation
    DB -->|Aggregated Data| Dashboard
```
