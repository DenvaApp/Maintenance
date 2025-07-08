import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please enter your 4-digit code to access the app.'
login_manager.login_message_category = 'info'

# Configure the database
database_url = os.environ.get("DATABASE_URL", "sqlite:///maintenance.db")

# Fix PostgreSQL URL format for SQLAlchemy 2.0+
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Log database connection info (without showing sensitive data)
if database_url.startswith("postgresql"):
    app.logger.info("Using PostgreSQL database")
else:
    app.logger.info("Using SQLite database")
    
# Ensure database operations are properly tracked
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure file uploads
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize the app with the extension
db.init_app(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
        
        # Create default users if they don't exist
        from models import User
        if User.query.count() == 0:
            default_users = [
                User(display_name="Isaak", login_code="1234"),
                User(display_name="Susie", login_code="4567"),
                User(display_name="John", login_code="7890"),
            ]
            for user in default_users:
                db.session.add(user)
            db.session.commit()
            app.logger.info("Default users created successfully")
        else:
            app.logger.info(f"Database already has {User.query.count()} users")
            
    except Exception as e:
        app.logger.error(f"Database initialization failed: {str(e)}")
        db.session.rollback()

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Import routes
import routes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
