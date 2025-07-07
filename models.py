from app import db
from datetime import datetime, timedelta
from sqlalchemy import func
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(50), nullable=False)
    login_code = db.Column(db.String(4), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationship to work logs
    work_logs = db.relationship('WorkLog', backref='user_ref', lazy=True)
    notifications = db.relationship('Notification', backref='user_ref', lazy=True)
    
    def __repr__(self):
        return f'<User {self.display_name}>'
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_active(self):
        return self.active

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for subcategories
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    # Equipment relationship
    equipment = db.relationship('Equipment', backref='category_ref', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    @property
    def full_name(self):
        """Get the full hierarchical name (e.g., 'Greenhouse > Pepper Bins')"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name
    
    def get_all_equipment(self):
        """Get all equipment in this category and all subcategories"""
        equipment_list = []
        # Add equipment directly in this category using query
        direct_equipment = Equipment.query.filter_by(category_id=self.id).all()
        equipment_list.extend(direct_equipment)
        
        # Get subcategories and their equipment
        subcategories = Category.query.filter_by(parent_id=self.id).all()
        for subcategory in subcategories:
            equipment_list.extend(subcategory.get_all_equipment())
        return equipment_list
    
    def get_root_category(self):
        """Get the top-level parent category"""
        if self.parent:
            return self.parent.get_root_category()
        return self
    
    def get_level(self):
        """Get the nesting level (0 for root, 1 for first level, etc.)"""
        if self.parent:
            return self.parent.get_level() + 1
        return 0

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    photo_filename = db.Column(db.String(255))
    icon = db.Column(db.String(50))  # Store icon name (e.g., 'tool', 'truck', 'cpu')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    work_logs = db.relationship('WorkLog', backref='equipment_ref', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='equipment_ref', lazy=True)
    
    def __repr__(self):
        return f'<Equipment {self.name}>'
    
    def is_high_maintenance(self):
        """Check if equipment has more than 3 logs in the last 2 months"""
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        log_count = WorkLog.query.filter(
            WorkLog.equipment_id == self.id,
            WorkLog.date >= two_months_ago
        ).count()
        return log_count > 3
    
    def recent_log_count(self):
        """Get count of logs in the last 2 months"""
        two_months_ago = datetime.utcnow() - timedelta(days=60)
        return WorkLog.query.filter(
            WorkLog.equipment_id == self.id,
            WorkLog.date >= two_months_ago
        ).count()

class WorkLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    work_type = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WorkLog {self.work_type} on {self.date}>'


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # None for system-wide
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # info, warning, maintenance, overdue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    repeat_days = db.Column(db.Integer, nullable=True)  # for recurring reminders
    read = db.Column(db.Boolean, default=False)
    dismissed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent

    def __repr__(self):
        return f'<Notification {self.title}>'
    
    def is_overdue(self):
        """Check if notification is overdue"""
        if self.due_date:
            return datetime.utcnow() > self.due_date
        return False
    
    def days_until_due(self):
        """Get number of days until due date"""
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return delta.days
        return None
