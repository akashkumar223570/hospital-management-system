from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Admission, Ward, Bed, Patient, Doctor, Transfer, AuditLog
from datetime import datetime, date

adt_bp = Blueprint('adt', __name__)

@adt_bp.route('/')
@login_required
def list_admissions():
    status = request.args.get('status', 'Admitted')
    admissions = Admission.query.filter_by(status=status).order_by(Admission.admission_date.desc()).all()
    return render_template('adt/list.html', admissions=admissions, status=status)


@adt_bp.route('/beds')
@login_required
def beds():
    wards = Ward.query.filter_by(is_active=True).all()
    return render_template('adt/beds.html', wards=wards)


@adt_bp.route('/admit', methods=['GET', 'POST'])
@login_required
def admit():
    patients = Patient.query.filter_by(is_active=True).all()
    doctors = Doctor.query.all()
    available_beds = Bed.query.filter_by(status='Available').all()
    
    if request.method == 'POST':
        try:
            bed_id = int(request.form.get('bed_id'))
            bed = Bed.query.get(bed_id)
            if bed.status != 'Available':
                flash('Selected bed is no longer available.', 'danger')
                return redirect(url_for('adt.admit'))
            
            admission = Admission(
                patient_id=int(request.form.get('patient_id')),
                bed_id=bed_id,
                admitting_doctor_id=int(request.form.get('doctor_id')),
                admission_type=request.form.get('admission_type', 'Elective'),
                reason=request.form.get('reason', '').strip() or None,
                diagnosis_on_admission=request.form.get('diagnosis', '').strip() or None,
                created_by=current_user.id
            )
            if request.form.get('expected_discharge'):
                admission.expected_discharge = datetime.strptime(request.form.get('expected_discharge'), '%Y-%m-%d').date()
            
            bed.status = 'Occupied'
            db.session.add(admission)
            log = AuditLog(user_id=current_user.id, action='ADMIT_PATIENT', entity='Admission',
                           details=f'Admitted patient to bed {bed.bed_number}',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash('Patient admitted successfully.', 'success')
            return redirect(url_for('adt.list_admissions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('adt/admit.html', patients=patients, doctors=doctors, available_beds=available_beds)


@adt_bp.route('/<int:id>/discharge', methods=['GET', 'POST'])
@login_required
def discharge(id):
    admission = Admission.query.get_or_404(id)
    if request.method == 'POST':
        try:
            admission.status = 'Discharged'
            admission.actual_discharge = datetime.utcnow()
            admission.discharge_summary = request.form.get('discharge_summary', '').strip() or None
            admission.discharge_instructions = request.form.get('discharge_instructions', '').strip() or None
            if admission.admission_date:
                delta = admission.actual_discharge.date() - admission.admission_date.date()
                admission.length_of_stay = max(delta.days, 1)
            
            if admission.bed:
                admission.bed.status = 'Available'
            
            db.session.commit()
            flash('Patient discharged successfully.', 'success')
            return redirect(url_for('adt.list_admissions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('adt/discharge.html', admission=admission)


@adt_bp.route('/<int:id>/transfer', methods=['GET', 'POST'])
@login_required
def transfer(id):
    admission = Admission.query.get_or_404(id)
    available_beds = Bed.query.filter_by(status='Available').all()
    
    if request.method == 'POST':
        try:
            new_bed_id = int(request.form.get('to_bed_id'))
            new_bed = Bed.query.get(new_bed_id)
            if new_bed.status != 'Available':
                flash('Target bed not available.', 'danger')
                return redirect(url_for('adt.transfer', id=id))
            
            old_bed = admission.bed
            t = Transfer(
                admission_id=admission.id,
                from_bed_id=old_bed.id if old_bed else None,
                to_bed_id=new_bed_id,
                reason=request.form.get('reason', '').strip() or None,
                transferred_by=current_user.id
            )
            if old_bed:
                old_bed.status = 'Available'
            new_bed.status = 'Occupied'
            admission.bed_id = new_bed_id
            db.session.add(t)
            db.session.commit()
            flash('Patient transferred successfully.', 'success')
            return redirect(url_for('adt.list_admissions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('adt/transfer.html', admission=admission, available_beds=available_beds)
