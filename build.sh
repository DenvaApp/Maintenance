#!/bin/bash
# Build script for Render deployment

echo "Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies..."
pip install -e . || {
    echo "pyproject.toml installation failed, installing packages individually..."
    pip install email-validator>=2.1.0 \
                flask-wtf>=1.2.0 \
                flask>=3.0.0 \
                flask-sqlalchemy>=3.1.0 \
                gunicorn>=21.0.0 \
                psycopg2-binary>=2.9.0 \
                wtforms>=3.1.0 \
                werkzeug>=3.0.0 \
                sqlalchemy>=2.0.0 \
                reportlab>=4.0.0 \
                flask-login>=0.6.0
}

echo "Build completed successfully!"