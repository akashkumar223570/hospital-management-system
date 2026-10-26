from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import EmergencyVisit, Patient, Doctor
from datetime import datetime

emergency_bp = Blueprint('emergency', __name__)

@emergency_bp.route('/')
@login_required
def list_visits():
    status = request.args.get('status', 'Waiting')
    visits = EmergencyVisit.query.filter_by(status=status).order_by(EmergencyVisit.arrival_time).all()
    return render_template('emergency/list.html', visits=visits, status=status)


@emergency_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    patients = Patient.query.filter_by(is_active=True).all()
    doctors = Doctor.query.all()
    
    if request.method == 'POST':
        try:
            visit = EmergencyVisit(
                patient_id=int(request.form.get('patient_id')),
                triage_level=request.form.get('triage_level'),
                chief_complaint=request.form.get('chief_complaint', '').strip(),
                initial_vitals=request.form.get('initial_vitals', '').strip() or None,
                triage_notes=request.form.get('triage_notes', '').strip() or None,
                triaged_by=current_user.id,
                assigned_doctor_id=int(request.form.get('doctor_id')) if request.form.get('doctor_id') else None,
                status='Waiting'
            )
            db.session.add(visit)
            db.session.commit()
            flash('Emergency visit registered and triaged.', 'success')
            return redirect(url_for('emergency.list_visits'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('emergency/register.html', patients=patients, doctors=doctors)


@emergency_bp.route('/<int:id>/update', methods=['POST'])
@login_required
def update_status(id):
    visit = EmergencyVisit.query.get_or_404(id)
    visit.status = request.form.get('status', visit.status)
    if visit.status == 'Under Treatment' and not visit.treatment_started:
        visit.treatment_started = datetime.utcnow()
    db.session.commit()
    flash('Status updated.', 'success')
    return redirect(url_for('emergency.list_visits'))
