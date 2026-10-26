from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Doctor, Department, User, Appointment

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/')
@login_required
def list_doctors():
    doctors = Doctor.query.all()
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('doctors/list.html', doctors=doctors, departments=departments)


@doctors_bp.route('/departments')
@login_required
def departments():
    depts = Department.query.filter_by(is_active=True).all()
    return render_template('doctors/departments.html', departments=depts)


@doctors_bp.route('/<int:id>')
@login_required
def view(id):
    doctor = Doctor.query.get_or_404(id)
    upcoming = Appointment.query.filter(
        Appointment.doctor_id == id,
        Appointment.status.in_(['Scheduled', 'Confirmed'])
    ).order_by(Appointment.appointment_date).limit(10).all()
    return render_template('doctors/view.html', doctor=doctor, upcoming=upcoming)
