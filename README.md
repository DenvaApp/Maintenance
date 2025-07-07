# Maintenance Log

A modern, mobile-friendly equipment maintenance logging web application built with Flask. Features clean design with large buttons, hierarchical categories, equipment management with photo uploads, work logging system, PDF export capabilities, and multi-user authentication with simple 4-digit login codes.

## Features

- **Multi-User Authentication**: Simple 4-digit login codes (no passwords needed)
- **Equipment Management**: Add, edit, and organize equipment with photos
- **Hierarchical Categories**: Organize equipment in nested categories
- **Work Logging**: Track maintenance work with user accountability
- **PDF Export**: Generate professional maintenance reports
- **Mobile-Friendly**: Responsive design optimized for mobile devices
- **User Management**: Add/remove users, control access permissions

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, Feather Icons
- **PDF Generation**: ReportLab
- **Authentication**: Flask-Login

## Quick Start

### Local Development

1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Set environment variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost/maintenance_log
   SESSION_SECRET=your-secret-key-here
   ```
4. Run the application: `python main.py`
5. Access at `http://localhost:5000`

### Deploy on Render

#### Option 1: Using render.yaml (Recommended)

1. Fork this repository
2. Connect your GitHub repo to Render
3. Render will automatically detect the `render.yaml` configuration
4. The app will deploy with a PostgreSQL database automatically

#### Option 2: Manual Setup

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - **Build Command**: `pip install -e .`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app`
   - **Environment**: Python 3.11
4. Create a PostgreSQL database
5. Add environment variables:
   - `DATABASE_URL`: (auto-populated from database)
   - `SESSION_SECRET`: (generate a random secret key)

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for session management (required)

## Default Users

The app comes with three default users for testing:

- **Isaak**: Login code `1234`
- **Susie**: Login code `4567`
- **John**: Login code `7890`

## Usage

1. **Login**: Enter your 4-digit code on the login page
2. **Add Equipment**: Navigate to "Equipment" → "Add New Equipment"
3. **Create Categories**: Use "Categories" to organize your equipment
4. **Log Work**: Click "Log Work" and select equipment to record maintenance
5. **Export Reports**: Use "Export" to generate PDF reports
6. **Manage Users**: Admin can add/remove users via "Users" section

## File Structure

```
├── app.py              # Flask app configuration
├── main.py             # Application entry point
├── models.py           # Database models
├── routes.py           # Route handlers
├── forms.py            # WTForms definitions
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── render.yaml         # Render deployment config
├── Dockerfile          # Docker configuration
└── pyproject.toml      # Python dependencies
```

## Contributing

This is a personal project, but suggestions and improvements are welcome.

## License

Private project - all rights reserved.