from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, AuditLog, Department
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.role, User.full_name).all()
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    return render_template('admin/index.html', users=users, logs=logs)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        try:
            user = User(
                username=request.form.get('username', '').strip(),
                email=request.form.get('email', '').strip(),
                full_name=request.form.get('full_name', '').strip(),
                role=request.form.get('role', 'receptionist'),
                phone=request.form.get('phone', '').strip() or None
            )
            user.set_password(request.form.get('password', 'password123'))
            db.session.add(user)
            db.session.commit()
            flash(f'User {user.username} created successfully.', 'success')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('admin/create_user.html')


@admin_bp.route('/users/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Cannot deactivate yourself.', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(f'User {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('admin.index'))
