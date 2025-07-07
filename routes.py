import os
import uuid
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import Category, Equipment, WorkLog, User, Notification
from forms import CategoryForm, EquipmentForm, WorkLogForm, LoginForm, UserForm, NotificationForm
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import HRFlowable
from io import BytesIO

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with 4-digit code"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login_code=form.login_code.data).first()
        if user and user.is_active:
            login_user(user, remember=True)
            flash(f'Welcome back, {user.display_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid login code. Please try again.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    user_name = current_user.display_name
    logout_user()
    flash(f'Goodbye, {user_name}!', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Homepage dashboard"""
    total_equipment = Equipment.query.count()
    
    # Get equipment with high maintenance (more than 3 logs in last 2 months)
    high_maintenance_equipment = []
    for equipment in Equipment.query.all():
        if equipment.is_high_maintenance():
            high_maintenance_equipment.append(equipment)
    
    # Get recent work logs
    recent_logs = WorkLog.query.order_by(WorkLog.created_at.desc()).limit(5).all()
    
    # Get categories for filter
    categories = Category.query.all()
    
    # Get unread notifications for current user
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        read=False, 
        dismissed=False
    ).order_by(Notification.priority.desc(), Notification.created_at.desc()).all()
    
    # Get system-wide notifications (user_id is None)
    system_notifications = Notification.query.filter_by(
        user_id=None, 
        read=False, 
        dismissed=False
    ).order_by(Notification.priority.desc(), Notification.created_at.desc()).all()
    
    all_unread = unread_notifications + system_notifications
    
    return render_template('index.html', 
                         total_equipment=total_equipment,
                         high_maintenance_equipment=high_maintenance_equipment,
                         recent_logs=recent_logs,
                         categories=categories,
                         unread_notifications=all_unread)

@app.route('/equipment')
@login_required
def equipment_list():
    """List all equipment with search and filter"""
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    
    query = Equipment.query
    
    if search:
        query = query.filter(Equipment.name.contains(search))
    
    if category_id:
        query = query.filter(Equipment.category_id == category_id)
    
    equipment = query.all()
    categories = Category.query.all()
    
    return render_template('equipment.html', 
                         equipment=equipment, 
                         categories=categories,
                         search=search,
                         selected_category=category_id)

@app.route('/add_equipment', methods=['GET', 'POST'])
@login_required
def add_equipment():
    """Add new equipment"""
    form = EquipmentForm()
    
    # Populate category choices with hierarchical names
    categories = Category.query.all()
    choices = []
    for c in categories:
        display_name = c.full_name if hasattr(c, 'full_name') else c.name
        choices.append((c.id, display_name))
    form.category_id.choices = choices
    
    if form.validate_on_submit():
        # Handle file upload
        photo_filename = None
        if form.photo.data:
            file = form.photo.data
            if file and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                photo_filename = unique_filename
        
        equipment = Equipment(
            name=form.name.data,
            category_id=form.category_id.data,
            photo_filename=photo_filename
        )
        
        db.session.add(equipment)
        db.session.commit()
        
        flash('Equipment added successfully!', 'success')
        return redirect(url_for('equipment_list'))
    
    return render_template('add_equipment.html', form=form)

@app.route('/edit_equipment/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def edit_equipment(equipment_id):
    """Edit existing equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    form = EquipmentForm(obj=equipment)
    
    # Populate category choices with hierarchical names
    categories = Category.query.all()
    choices = []
    for c in categories:
        display_name = c.full_name if hasattr(c, 'full_name') else c.name
        choices.append((c.id, display_name))
    form.category_id.choices = choices
    
    if form.validate_on_submit():
        # Handle file upload
        if form.photo.data:
            file = form.photo.data
            if file and allowed_file(file.filename):
                # Delete old photo if it exists
                if equipment.photo_filename:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], equipment.photo_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Save new photo
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                equipment.photo_filename = unique_filename
        
        # Update equipment details
        equipment.name = form.name.data
        equipment.category_id = form.category_id.data
        
        db.session.commit()
        flash('Equipment updated successfully!', 'success')
        return redirect(url_for('equipment_list'))
    
    return render_template('edit_equipment.html', form=form, equipment=equipment)

@app.route('/equipment/<int:equipment_id>')
@login_required
def equipment_detail(equipment_id):
    """Show equipment detail and work history"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # Get work logs for this equipment, ordered by date (most recent first)
    work_logs = WorkLog.query.filter_by(equipment_id=equipment_id)\
                           .order_by(WorkLog.date.desc(), WorkLog.created_at.desc())\
                           .all()
    
    # Get notifications for this equipment
    notifications = Notification.query.filter_by(equipment_id=equipment_id)\
                                    .order_by(Notification.created_at.desc())\
                                    .all()
    
    # Calculate some statistics
    total_logs = len(work_logs)
    recent_logs = [log for log in work_logs if (datetime.utcnow().date() - log.date).days <= 30]
    work_types = {}
    for log in work_logs:
        work_types[log.work_type] = work_types.get(log.work_type, 0) + 1
    
    # Get last maintenance date
    last_maintenance = work_logs[0].date if work_logs else None
    
    return render_template('equipment_detail.html', 
                         equipment=equipment, 
                         work_logs=work_logs,
                         notifications=notifications,
                         total_logs=total_logs,
                         recent_logs=len(recent_logs),
                         work_types=work_types,
                         last_maintenance=last_maintenance)

@app.route('/delete_equipment/<int:equipment_id>')
@login_required
def delete_equipment(equipment_id):
    """Delete equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # Delete associated photo if it exists
    if equipment.photo_filename:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], equipment.photo_filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    # Delete the equipment (work logs will be deleted due to cascade)
    db.session.delete(equipment)
    db.session.commit()
    
    flash(f'Equipment "{equipment.name}" deleted successfully!', 'success')
    return redirect(url_for('equipment_list'))

@app.route('/export_logs')
@login_required
def export_logs():
    """Show export options"""
    current_year = datetime.now().year
    current_month = datetime.now().month
    return render_template('export_logs.html', current_year=current_year, current_month=current_month)

@app.route('/export_pdf')
@login_required
def export_pdf():
    """Export work logs to PDF"""
    export_type = request.args.get('type', 'monthly')
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # Create PDF buffer
    buffer = BytesIO()
    
    # Generate filename based on export type
    if export_type == 'yearly':
        filename = f"maintenance_logs_{year}.pdf"
        title = f"Maintenance Logs - {year}"
        # Get all logs for the year
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
    else:  # monthly
        month_name = datetime(year, month, 1).strftime('%B')
        filename = f"maintenance_logs_{year}_{month:02d}.pdf"
        title = f"Maintenance Logs - {month_name} {year}"
        # Get logs for the specific month
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
    
    # Initialize month_name for both cases
    month_name = datetime(year, month, 1).strftime('%B') if export_type != 'yearly' else 'All Year'
    
    # Query work logs for the date range
    logs = WorkLog.query.filter(
        WorkLog.date >= start_date,
        WorkLog.date < end_date
    ).order_by(WorkLog.date.desc(), WorkLog.created_at.desc()).all()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Build PDF content
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#ea580c'),  # Orange color
        alignment=1  # Center alignment
    )
    story.append(Paragraph(title, title_style))
    
    # Summary section
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=15
    )
    
    total_logs = len(logs)
    equipment_count = len(set(log.equipment_id for log in logs))
    
    if export_type == 'yearly':
        summary_text = f"Total work logs: {total_logs} | Equipment serviced: {equipment_count} | Year: {year}"
        period_label = f"Year {year}"
    else:
        summary_text = f"Total work logs: {total_logs} | Equipment serviced: {equipment_count} | Month: {month_name} {year}"
        period_label = f"{month_name} {year}"
    
    story.append(Paragraph(summary_text, summary_style))
    story.append(Spacer(1, 12))
    
    if logs:
        # Group logs by equipment for better organization
        equipment_logs = {}
        for log in logs:
            equipment_name = log.equipment_ref.name
            category_name = log.equipment_ref.category_ref.name
            if equipment_name not in equipment_logs:
                equipment_logs[equipment_name] = {
                    'category': category_name,
                    'logs': []
                }
            equipment_logs[equipment_name]['logs'].append(log)
        
        # Create content for each equipment
        for equipment_name, data in equipment_logs.items():
            # Equipment header
            equipment_style = ParagraphStyle(
                'EquipmentHeader',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                textColor=colors.HexColor('#64748b')
            )
            
            equipment_header = f"{equipment_name} ({data['category']})"
            story.append(Paragraph(equipment_header, equipment_style))
            
            # Create table for this equipment's logs
            table_data = [['Date', 'Work Type', 'Notes']]
            
            for log in data['logs']:
                notes = log.notes if log.notes else 'No notes'
                # Truncate long notes for better table formatting
                if len(notes) > 60:
                    notes = notes[:57] + "..."
                
                table_data.append([
                    log.date.strftime('%Y-%m-%d'),
                    log.work_type,
                    notes
                ])
            
            # Create and style the table
            table = Table(table_data, colWidths=[1.2*inch, 1.3*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
    else:
        # No logs found message
        no_logs_style = ParagraphStyle(
            'NoLogs',
            parent=styles['Normal'],
            fontSize=12,
            alignment=1,
            textColor=colors.HexColor('#64748b')
        )
        story.append(Paragraph("No maintenance logs found for this period.", no_logs_style))
    
    # Footer with generation info
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 10))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        alignment=1
    )
    
    generation_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    footer_text = f"Generated on {generation_time} by Equipment Maintenance Logger"
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Prepare response
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@app.route('/categories')
@login_required
def categories():
    """Manage categories"""
    # Get all categories and organize them hierarchically
    root_categories = Category.query.filter_by(parent_id=None).all()
    all_categories = Category.query.all()
    form = CategoryForm()
    
    # Populate parent category choices for the form - allow both root and subcategories as parents
    choices = [(0, 'None (Root Category)')]
    for c in all_categories:
        # Show full hierarchical name for clarity
        if hasattr(c, 'full_name'):
            display_name = c.full_name
        else:
            display_name = c.name
        choices.append((c.id, display_name))
    form.parent_id.choices = choices
    
    return render_template('categories.html', 
                         categories=all_categories, 
                         root_categories=root_categories,
                         form=form)

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    """Add new category"""
    form = CategoryForm()
    
    # Populate parent category choices
    all_cats = Category.query.all()
    choices = [(0, 'None (Root Category)')]
    for c in all_cats:
        display_name = c.full_name if hasattr(c, 'full_name') else c.name
        choices.append((c.id, display_name))
    form.parent_id.choices = choices
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data != 0 else None
        
        # Check if category already exists at the same level
        if parent_id:
            existing = Category.query.filter_by(name=form.name.data, parent_id=parent_id).first()
        else:
            existing = Category.query.filter_by(name=form.name.data, parent_id=None).first()
            
        if existing:
            flash('Category already exists at this level!', 'error')
        else:
            category = Category(name=form.name.data, parent_id=parent_id)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
    else:
        flash('Please provide a valid category name.', 'error')
    
    return redirect(url_for('categories'))

@app.route('/delete_category/<int:category_id>')
@login_required
def delete_category(category_id):
    """Delete category"""
    category = Category.query.get_or_404(category_id)
    
    # Check if category has equipment
    if category.equipment:
        flash('Cannot delete category with equipment. Please reassign or delete equipment first.', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('categories'))

@app.route('/log_work')
@login_required
def select_equipment():
    """Select equipment for work logging"""
    search = request.args.get('search', '')
    
    query = Equipment.query
    if search:
        query = query.filter(Equipment.name.contains(search))
    
    equipment = query.all()
    
    return render_template('select_equipment.html', equipment=equipment, search=search)

@app.route('/log_work/<int:equipment_id>', methods=['GET', 'POST'])
@login_required
def log_work(equipment_id):
    """Log work for specific equipment"""
    equipment = Equipment.query.get_or_404(equipment_id)
    form = WorkLogForm()
    form.equipment_id.data = equipment_id
    
    if form.validate_on_submit():
        work_log = WorkLog(
            equipment_id=equipment_id,
            user_id=current_user.id,
            date=form.date.data,
            work_type=form.work_type.data,
            notes=form.notes.data
        )
        
        db.session.add(work_log)
        db.session.commit()
        
        flash(f'Work logged for {equipment.name}!', 'success')
        return redirect(url_for('index'))
    
    # Get recent logs for this equipment
    recent_logs = WorkLog.query.filter_by(equipment_id=equipment_id)\
                              .order_by(WorkLog.date.desc()).limit(5).all()
    
    return render_template('log_work.html', 
                         form=form, 
                         equipment=equipment,
                         recent_logs=recent_logs)

@app.route('/admin/users')
@login_required
def manage_users():
    """Admin page to manage users"""
    users = User.query.all()
    form = UserForm()
    return render_template('manage_users.html', users=users, form=form)

@app.route('/admin/users/add', methods=['POST'])
@login_required
def add_user():
    """Add new user"""
    form = UserForm()
    
    if form.validate_on_submit():
        # Check if login code already exists
        existing_user = User.query.filter_by(login_code=form.login_code.data).first()
        if existing_user:
            flash('Login code already exists. Please choose a different code.', 'error')
        else:
            user = User(
                display_name=form.display_name.data,
                login_code=form.login_code.data
            )
            db.session.add(user)
            db.session.commit()
            flash(f'User "{user.display_name}" created successfully with code {user.login_code}!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'error')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    """Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Check if user has work logs
    if user.work_logs:
        flash(f'Cannot delete user "{user.display_name}" who has logged work. Work logs would be orphaned.', 'error')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.display_name}" deleted successfully!', 'success')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/users/toggle/<int:user_id>')
@login_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.active = not user.active
    db.session.commit()
    
    status = "activated" if user.active else "deactivated"
    flash(f'User "{user.display_name}" {status} successfully!', 'success')
    
    return redirect(url_for('manage_users'))

@app.route('/notifications')
@login_required
def my_notifications():
    """User's personal notification page"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.read.asc(), Notification.priority.desc(), Notification.created_at.desc()
    ).all()
    
    # Also get system-wide notifications
    system_notifications = Notification.query.filter_by(user_id=None).order_by(
        Notification.read.asc(), Notification.priority.desc(), Notification.created_at.desc()
    ).all()
    
    all_notifications = notifications + system_notifications
    
    return render_template('notifications.html', notifications=all_notifications)

@app.route('/notifications/create', methods=['GET', 'POST'])
@login_required
def create_notification():
    """Create new notification"""
    form = NotificationForm()
    
    # Populate equipment choices
    form.equipment_id.choices = [(0, 'None (System-wide)')] + [
        (e.id, f"{e.name} ({e.category_ref.name})") for e in Equipment.query.all()
    ]
    
    # Populate user choices
    form.user_id.choices = [(0, 'All Users (System-wide)')] + [
        (u.id, u.display_name) for u in User.query.filter_by(active=True).all()
    ]
    
    if form.validate_on_submit():
        notification = Notification(
            title=form.title.data,
            message=form.message.data,
            notification_type=form.notification_type.data,
            priority=form.priority.data,
            equipment_id=form.equipment_id.data if form.equipment_id.data != 0 else None,
            user_id=form.user_id.data if form.user_id.data != 0 else None,
            due_date=form.due_date.data,
            repeat_days=form.repeat_days.data
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Notification "{notification.title}" created successfully!', 'success')
        return redirect(url_for('manage_notifications'))
    
    return render_template('create_notification.html', form=form)

@app.route('/notifications/manage')
@login_required
def manage_notifications():
    """Manage all notifications"""
    all_notifications = Notification.query.order_by(
        Notification.read.asc(), Notification.priority.desc(), Notification.created_at.desc()
    ).all()
    
    return render_template('manage_notifications.html', notifications=all_notifications)

@app.route('/notifications/mark-read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id and notification.user_id != current_user.id:
        flash('You can only mark your own notifications as read.', 'error')
        return redirect(url_for('my_notifications'))
    
    notification.read = True
    db.session.commit()
    
    return redirect(request.referrer or url_for('my_notifications'))

@app.route('/notifications/dismiss/<int:notification_id>')
@login_required
def dismiss_notification(notification_id):
    """Dismiss notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id and notification.user_id != current_user.id:
        flash('You can only dismiss your own notifications.', 'error')
        return redirect(url_for('my_notifications'))
    
    notification.dismissed = True
    db.session.commit()
    
    return redirect(request.referrer or url_for('my_notifications'))

@app.route('/notifications/delete/<int:notification_id>')
@login_required
def delete_notification(notification_id):
    """Delete notification"""
    notification = Notification.query.get_or_404(notification_id)
    
    db.session.delete(notification)
    db.session.commit()
    
    flash(f'Notification "{notification.title}" deleted successfully!', 'success')
    return redirect(url_for('manage_notifications'))

@app.route('/api/equipment/search')
@login_required
def api_equipment_search():
    """API endpoint for equipment search"""
    search = request.args.get('q', '')
    equipment = Equipment.query.filter(Equipment.name.contains(search)).all()
    
    return jsonify([{
        'id': e.id,
        'name': e.name,
        'category': e.category_ref.name
    } for e in equipment])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
