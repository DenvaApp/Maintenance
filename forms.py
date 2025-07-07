from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, HiddenField, IntegerField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional, Regexp, NumberRange
from datetime import date

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=100)])
    parent_id = SelectField('Parent Category (Optional)', coerce=int, validators=[Optional()])

class EquipmentForm(FlaskForm):
    name = StringField('Equipment Name', validators=[DataRequired(), Length(min=1, max=200)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    photo = FileField('Equipment Photo', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    icon = SelectField('Equipment Icon (Alternative to Photo)', choices=[
        ('', 'No Icon'),
        ('pepper-shoots', '🌶️ Pepper Shoots'),
        ('pepper-bin', '🗃️ Pepper Bin'),
        ('tow-buggy', '🚚 Tow Buggy'),
        ('spray-robot', '🤖 Spray Robot'),
        ('spray-wagon', '🚛 Spray Wagon'),
        ('motor', '⚙️ Motor'),
        ('forklift', '🚜 Forklift'),
        ('scissor-lift', '🚜 Scissor Lift'),
        ('greenhouse-fan', '💨 Greenhouse Fan'),
        ('heating-system', '🔥 Heating System'),
        ('irrigation-system', '💧 Irrigation System')
    ], validators=[Optional()])

class WorkLogForm(FlaskForm):
    equipment_id = HiddenField('Equipment ID', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    work_type = SelectField('Work Type', choices=[
        ('Preventative', 'Preventative'),
        ('Repair', 'Repair'),
        ('Inspection', 'Inspection'),
        ('Cleaning', 'Cleaning'),
        ('Calibration', 'Calibration'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])

class LoginForm(FlaskForm):
    login_code = StringField('4-Digit Login Code', validators=[
        DataRequired(message='Please enter your 4-digit code'),
        Length(min=4, max=4, message='Code must be exactly 4 digits'),
        Regexp(r'^\d{4}$', message='Code must contain only numbers')
    ])

class UserForm(FlaskForm):
    display_name = StringField('Display Name', validators=[
        DataRequired(message='Please enter a display name'),
        Length(min=1, max=50, message='Name must be between 1 and 50 characters')
    ])
    login_code = StringField('4-Digit Login Code', validators=[
        DataRequired(message='Please enter a 4-digit code'),
        Length(min=4, max=4, message='Code must be exactly 4 digits'),
        Regexp(r'^\d{4}$', message='Code must contain only numbers')
    ])


class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=500)])
    notification_type = SelectField('Type', choices=[
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('maintenance', 'Maintenance Required'),
        ('overdue', 'Overdue')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], validators=[DataRequired()])
    equipment_id = SelectField('Equipment (Optional)', coerce=int, validators=[Optional()])
    user_id = SelectField('User (Optional)', coerce=int, validators=[Optional()])
    due_date = DateTimeLocalField('Due Date (Optional)', validators=[Optional()])
    repeat_days = IntegerField('Repeat Every (Days)', validators=[Optional(), NumberRange(min=1, max=365)])
