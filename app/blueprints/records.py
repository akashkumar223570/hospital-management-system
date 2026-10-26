from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import MedicalRecord, Prescription, PrescriptionItem, Patient, Doctor, Medicine, Appointment
from datetime import datetime, date

records_bp = Blueprint('records', __name__)

@records_bp.route('/')
@login_required
def list_records():
    page = request.args.get('page', 1, type=int)
    records = MedicalRecord.query.order_by(MedicalRecord.visit_date.desc()).paginate(page=page, per_page=20)
    return render_template('records/list.html', records=records)


@records_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    patients = Patient.query.filter_by(is_active=True).all()
    doctors = Doctor.query.all()
    
    if request.method == 'POST':
        try:
            record = MedicalRecord(
                patient_id=int(request.form.get('patient_id')),
                doctor_id=int(request.form.get('doctor_id')),
                appointment_id=int(request.form.get('appointment_id')) if request.form.get('appointment_id') else None,
                chief_complaint=request.form.get('chief_complaint', '').strip() or None,
                symptoms=request.form.get('symptoms', '').strip() or None,
                examination_findings=request.form.get('examination_findings', '').strip() or None,
                diagnosis=request.form.get('diagnosis', '').strip() or None,
                diagnosis_code=request.form.get('diagnosis_code', '').strip() or None,
                treatment_plan=request.form.get('treatment_plan', '').strip() or None,
                follow_up_notes=request.form.get('follow_up_notes', '').strip() or None,
                blood_pressure=request.form.get('blood_pressure', '').strip() or None,
                pulse=int(request.form.get('pulse')) if request.form.get('pulse') else None,
                temperature=float(request.form.get('temperature')) if request.form.get('temperature') else None,
                weight=float(request.form.get('weight')) if request.form.get('weight') else None,
                height=float(request.form.get('height')) if request.form.get('height') else None,
                spo2=int(request.form.get('spo2')) if request.form.get('spo2') else None,
            )
            if request.form.get('follow_up_date'):
                record.follow_up_date = datetime.strptime(request.form.get('follow_up_date'), '%Y-%m-%d').date()
            
            db.session.add(record)
            db.session.flush()
            
            # Optional prescription
            med_names = request.form.getlist('med_name[]')
            dosages = request.form.getlist('med_dosage[]')
            freqs = request.form.getlist('med_freq[]')
            durs = request.form.getlist('med_duration[]')
            qtys = request.form.getlist('med_qty[]')
            
            if any(n.strip() for n in med_names):
                rx = Prescription(
                    patient_id=record.patient_id,
                    doctor_id=record.doctor_id,
                    medical_record_id=record.id
                )
                db.session.add(rx)
                db.session.flush()
                for name, dos, freq, dur, qty in zip(med_names, dosages, freqs, durs, qtys):
                    if name.strip():
                        item = PrescriptionItem(
                            prescription_id=rx.id,
                            medicine_name=name.strip(),
                            dosage=dos or None,
                            frequency=freq or None,
                            duration=dur or None,
                            quantity=int(qty or 1)
                        )
                        db.session.add(item)
            
            db.session.commit()
            flash('Medical record created successfully.', 'success')
            return redirect(url_for('records.view', id=record.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('records/create.html', patients=patients, doctors=doctors)


@records_bp.route('/<int:id>')
@login_required
def view(id):
    record = MedicalRecord.query.get_or_404(id)
    return render_template('records/view.html', record=record)
