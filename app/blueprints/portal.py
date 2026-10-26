from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Patient, Appointment, MedicalRecord, Bill, Prescription

portal_bp = Blueprint('portal', __name__)

@portal_bp.route('/')
@login_required
def index():
    # Simple patient portal - in real system would be patient-authenticated
    # For demo, show search by UHID
    return render_template('portal/index.html')


@portal_bp.route('/search', methods=['POST'])
@login_required
def search():
    uhid = request.form.get('uhid', '').strip()
    patient = Patient.query.filter_by(uhid=uhid).first()
    if not patient:
        flash('Patient not found.', 'warning')
        return redirect(url_for('portal.index'))
    
    appointments = patient.appointments.order_by(Appointment.appointment_date.desc()).limit(5).all()
    records = patient.medical_records.order_by(MedicalRecord.visit_date.desc()).limit(5).all()
    bills = patient.bills.order_by(Bill.bill_date.desc()).limit(5).all()
    
    return render_template('portal/patient.html', patient=patient,
                           appointments=appointments, records=records, bills=bills)
