from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Staff, User, Department, Attendance
from datetime import date

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/')
@login_required
def list_staff():
    staff_list = Staff.query.filter_by(is_active=True).all()
    return render_template('staff/list.html', staff_list=staff_list)


@staff_bp.route('/attendance')
@login_required
def attendance():
    today = date.today()
    records = Attendance.query.filter_by(date=today).all()
    return render_template('staff/attendance.html', records=records, today=today)
