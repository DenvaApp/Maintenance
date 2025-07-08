#!/usr/bin/env python3
"""
Database initialization script for Render deployment
This ensures the database is properly set up and populated with initial data
"""
import os
import sys
from app import app, db
from models import User, Category

def init_database():
    """Initialize database with tables and default data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Check if users exist, if not create default ones
            if User.query.count() == 0:
                default_users = [
                    User(display_name="Isaak", login_code="1234"),
                    User(display_name="Susie", login_code="4567"),
                    User(display_name="John", login_code="7890"),
                ]
                for user in default_users:
                    db.session.add(user)
                
                db.session.commit()
                print("✓ Default users created successfully")
            else:
                print("✓ Users already exist in database")
            
            # Check if categories exist, if not create default ones
            if Category.query.count() == 0:
                default_categories = [
                    Category(name="Greenhouse Equipment"),
                    Category(name="Processing Equipment"),
                    Category(name="Transport Equipment"),
                    Category(name="Maintenance Tools"),
                    Category(name="Safety Equipment"),
                ]
                for category in default_categories:
                    db.session.add(category)
                
                db.session.commit()
                print("✓ Default categories created successfully")
            else:
                print("✓ Categories already exist in database")
            
            # Test database connection
            user_count = User.query.count()
            category_count = Category.query.count()
            print(f"✓ Database connection verified: {user_count} users, {category_count} categories")
            
        except Exception as e:
            print(f"✗ Database initialization failed: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    init_database()