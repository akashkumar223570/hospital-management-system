from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Appointment, Patient, Doctor, Department, AuditLog
from datetime import datetime, date

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/')
@login_required
def list_appointments():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    if date_filter:
        try:
            d = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(appointment_date=d)
        except:
            pass
    else:
        # Default to today and future
        query = query.filter(Appointment.appointment_date >= date.today())
    
    appointments = query.order_by(Appointment.appointment_date, Appointment.appointment_time).paginate(page=page, per_page=20)
    return render_template('appointments/list.html', appointments=appointments, status=status, date_filter=date_filter)


@appointments_bp.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()
    doctors = Doctor.query.filter_by(is_available=True).all()
    departments = Department.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            appt = Appointment(
                patient_id=int(request.form.get('patient_id')),
                doctor_id=int(request.form.get('doctor_id')),
                department_id=int(request.form.get('department_id')) if request.form.get('department_id') else None,
                appointment_date=datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').date(),
                appointment_time=request.form.get('appointment_time'),
                appointment_type=request.form.get('appointment_type', 'OPD'),
                reason=request.form.get('reason', '').strip() or None,
                is_walk_in=bool(request.form.get('is_walk_in')),
                status='Scheduled',
                created_by=current_user.id
            )
            # Simple queue number for the day
            day_count = Appointment.query.filter_by(
                appointment_date=appt.appointment_date,
                doctor_id=appt.doctor_id
            ).count()
            appt.queue_number = day_count + 1
            
            db.session.add(appt)
            log = AuditLog(user_id=current_user.id, action='BOOK_APPOINTMENT', entity='Appointment',
                           details=f'Booked appointment for patient ID {appt.patient_id}',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash('Appointment booked successfully.', 'success')
            return redirect(url_for('appointments.list_appointments'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error booking appointment: {str(e)}', 'danger')
    
    return render_template('appointments/book.html', patients=patients, doctors=doctors, departments=departments)


@appointments_bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    appt = Appointment.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['Scheduled', 'Confirmed', 'In Progress', 'Completed', 'Cancelled', 'No-Show']:
        appt.status = new_status
        db.session.commit()
        flash(f'Appointment status updated to {new_status}.', 'success')
    return redirect(request.referrer or url_for('appointments.list_appointments'))


@appointments_bp.route('/today')
@login_required
def today():
    today = date.today()
    appointments = Appointment.query.filter_by(appointment_date=today).order_by(
        Appointment.appointment_time).all()
    return render_template('appointments/today.html', appointments=appointments, today=today)
