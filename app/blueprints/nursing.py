from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import NursingNote, Admission, Patient
from datetime import datetime

nursing_bp = Blueprint('nursing', __name__)

@nursing_bp.route('/')
@login_required
def index():
    admissions = Admission.query.filter_by(status='Admitted').all()
    return render_template('nursing/index.html', admissions=admissions)


@nursing_bp.route('/notes/<int:admission_id>', methods=['GET', 'POST'])
@login_required
def notes(admission_id):
    admission = Admission.query.get_or_404(admission_id)
    if request.method == 'POST':
        try:
            note = NursingNote(
                admission_id=admission.id,
                patient_id=admission.patient_id,
                nurse_id=current_user.id,
                note_type=request.form.get('note_type', 'Progress'),
                content=request.form.get('content', '').strip(),
                vitals=request.form.get('vitals', '').strip() or None
            )
            db.session.add(note)
            db.session.commit()
            flash('Nursing note added.', 'success')
            return redirect(url_for('nursing.notes', admission_id=admission_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    notes_list = NursingNote.query.filter_by(admission_id=admission_id).order_by(NursingNote.note_time.desc()).all()
    return render_template('nursing/notes.html', admission=admission, notes=notes_list)
