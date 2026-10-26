from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Patient, generate_uhid, AuditLog, Appointment, MedicalRecord, Admission, Bill
from datetime import datetime, date

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/')
@login_required
def list_patients():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    query = Patient.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(
            db.or_(
                Patient.uhid.ilike(f'%{search}%'),
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.phone.ilike(f'%{search}%')
            )
        )
    
    patients = query.order_by(Patient.registration_date.desc()).paginate(page=page, per_page=20)
    return render_template('patients/list.html', patients=patients, search=search)


@patients_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        try:
            uhid = generate_uhid()
            patient = Patient(
                uhid=uhid,
                first_name=request.form.get('first_name', '').strip(),
                last_name=request.form.get('last_name', '').strip(),
                date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date(),
                gender=request.form.get('gender'),
                blood_group=request.form.get('blood_group') or None,
                phone=request.form.get('phone', '').strip(),
                email=request.form.get('email', '').strip() or None,
                address=request.form.get('address', '').strip() or None,
                city=request.form.get('city', '').strip() or None,
                state=request.form.get('state', '').strip() or None,
                pincode=request.form.get('pincode', '').strip() or None,
                emergency_contact_name=request.form.get('emergency_contact_name', '').strip() or None,
                emergency_contact_phone=request.form.get('emergency_contact_phone', '').strip() or None,
                emergency_contact_relation=request.form.get('emergency_contact_relation', '').strip() or None,
                medical_history=request.form.get('medical_history', '').strip() or None,
                allergies=request.form.get('allergies', '').strip() or None,
                chronic_conditions=request.form.get('chronic_conditions', '').strip() or None,
                aadhaar=request.form.get('aadhaar', '').strip() or None,
                insurance_provider=request.form.get('insurance_provider', '').strip() or None,
                insurance_policy_number=request.form.get('insurance_policy_number', '').strip() or None,
            )
            db.session.add(patient)
            log = AuditLog(user_id=current_user.id, action='CREATE_PATIENT', entity='Patient',
                           entity_id=None, details=f'Registered patient {uhid}', ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash(f'Patient registered successfully. UHID: {uhid}', 'success')
            return redirect(url_for('patients.view', id=patient.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering patient: {str(e)}', 'danger')
    
    return render_template('patients/register.html')


@patients_bp.route('/<int:id>')
@login_required
def view(id):
    patient = Patient.query.get_or_404(id)
    appointments = patient.appointments.order_by(Appointment.appointment_date.desc()).limit(10).all()
    records = patient.medical_records.order_by(MedicalRecord.visit_date.desc()).limit(10).all()
    admissions = patient.admissions.order_by(Admission.admission_date.desc()).limit(5).all()
    bills = patient.bills.order_by(Bill.bill_date.desc()).limit(5).all()
    return render_template('patients/view.html', patient=patient, appointments=appointments,
                           records=records, admissions=admissions, bills=bills)


@patients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        try:
            patient.first_name = request.form.get('first_name', '').strip()
            patient.last_name = request.form.get('last_name', '').strip()
            patient.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            patient.gender = request.form.get('gender')
            patient.blood_group = request.form.get('blood_group') or None
            patient.phone = request.form.get('phone', '').strip()
            patient.email = request.form.get('email', '').strip() or None
            patient.address = request.form.get('address', '').strip() or None
            patient.city = request.form.get('city', '').strip() or None
            patient.state = request.form.get('state', '').strip() or None
            patient.pincode = request.form.get('pincode', '').strip() or None
            patient.emergency_contact_name = request.form.get('emergency_contact_name', '').strip() or None
            patient.emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip() or None
            patient.emergency_contact_relation = request.form.get('emergency_contact_relation', '').strip() or None
            patient.medical_history = request.form.get('medical_history', '').strip() or None
            patient.allergies = request.form.get('allergies', '').strip() or None
            patient.chronic_conditions = request.form.get('chronic_conditions', '').strip() or None
            patient.insurance_provider = request.form.get('insurance_provider', '').strip() or None
            patient.insurance_policy_number = request.form.get('insurance_policy_number', '').strip() or None
            
            log = AuditLog(user_id=current_user.id, action='UPDATE_PATIENT', entity='Patient',
                           entity_id=patient.id, details=f'Updated patient {patient.uhid}',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash('Patient details updated successfully.', 'success')
            return redirect(url_for('patients.view', id=patient.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'danger')
    
    return render_template('patients/edit.html', patient=patient)
