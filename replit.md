# Maintenance Log - Equipment Maintenance Tracking System

## Overview

This is a Flask-based web application for tracking equipment maintenance logs. It provides a mobile-friendly interface for logging work performed on equipment, managing equipment categories, and generating maintenance reports. The system uses simple 4-digit authentication codes for user access.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL (with SQLite fallback for development)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login with custom 4-digit code system
- **PDF Generation**: ReportLab for maintenance reports
- **File Uploads**: Werkzeug for handling equipment photos

### Frontend Architecture
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Feather Icons for consistent iconography
- **Styling**: Custom CSS with CSS variables for theming
- **JavaScript**: Vanilla JS for interactive features (search, image preview, form validation)

### Database Schema
The application uses a relational database with the following key models:
- **User**: Stores user information with 4-digit login codes
- **Category**: Hierarchical categories for equipment organization
- **Equipment**: Equipment items with photos and category relationships
- **WorkLog**: Maintenance work records linked to equipment and users
- **Notification**: In-app notification system for maintenance reminders

## Key Components

### Authentication System
- Simple 4-digit code authentication (no traditional passwords)
- Session-based login with Flask-Login
- User management with active/inactive status
- Default user "Isaak" with code "1234"

### Equipment Management
- Hierarchical category system (parent-child relationships)
- Equipment with photo uploads (16MB max file size)
- Equipment search and filtering by category
- Equipment detail pages with work history

### Work Logging
- Work type classification (Preventative, Repair, Inspection, etc.)
- Date-based work logging
- User attribution for accountability
- Notes and description fields

### Notification System
- In-app notifications for maintenance reminders
- Priority levels (urgent, high, normal, low)
- Due date tracking with overdue detection
- Notification types (maintenance, warning, info, overdue)
- Read/unread status tracking

### Reporting
- PDF export functionality for maintenance reports
- Monthly and date range reporting
- Professional report formatting with ReportLab

## Data Flow

1. **User Authentication**: Users enter 4-digit codes → Flask-Login creates session
2. **Equipment Management**: Users create categories → add equipment with photos → organize hierarchically
3. **Work Logging**: Users select equipment → log work performed → system records with user attribution
4. **Notifications**: System creates maintenance reminders → users receive alerts → notifications can be marked read/dismissed
5. **Reporting**: Users request reports → system queries database → generates PDF with ReportLab

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: User session management
- Flask-WTF: Form handling and validation
- ReportLab: PDF generation
- Werkzeug: File upload handling
- WTForms: Form validation

### Frontend Dependencies
- Bootstrap 5: CSS framework (CDN)
- Feather Icons: Icon library (CDN)
- Google Fonts (Inter): Typography (CDN)

### Database
- PostgreSQL: Production database
- SQLite: Development/fallback database

## Deployment Strategy

### Render.com Deployment
The application is configured for easy deployment on Render using:
- **render.yaml**: Infrastructure as code configuration
- **Automatic deployment**: Connects to GitHub repository
- **Database**: Automatically provisions PostgreSQL instance
- **Environment variables**: Configured via Render dashboard

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for session management

### File Structure
- `main.py`: Application entry point
- `app.py`: Flask application factory and configuration
- `routes.py`: All route handlers and view functions
- `models.py`: Database models and relationships
- `forms.py`: WTForms form definitions
- `templates/`: Jinja2 HTML templates
- `static/`: CSS, JavaScript, and uploaded images

### Production Considerations
- File uploads stored in local filesystem (`static/uploads/`)
- Session management with secure secret key
- Database connection pooling enabled
- ProxyFix middleware for deployment behind reverse proxy

## Changelog
- July 07, 2025. Initial setup  
- July 07, 2025. Fixed critical data persistence issue with database commits and error handling
- July 07, 2025. Added comprehensive greenhouse equipment icon system with 11 custom SVG icons
- July 07, 2025. Updated forms to include only specific greenhouse equipment options
- July 08, 2025. Enhanced database initialization with init_db.py script
- July 08, 2025. Added comprehensive logging and error handling for database operations
- July 08, 2025. Fixed PostgreSQL URL format compatibility for Render deployment

## User Preferences

Preferred communication style: Simple, everyday language.