from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import LabOrder, LabOrderItem, LabTest, Patient, Doctor, generate_lab_order_number
from datetime import datetime

lab_bp = Blueprint('lab', __name__)

@lab_bp.route('/')
@login_required
def list_orders():
    status = request.args.get('status', '')
    query = LabOrder.query
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(LabOrder.order_date.desc()).all()
    return render_template('lab/list.html', orders=orders, status=status)


@lab_bp.route('/tests')
@login_required
def tests():
    tests = LabTest.query.filter_by(is_active=True).order_by(LabTest.category, LabTest.name).all()
    return render_template('lab/tests.html', tests=tests)


@lab_bp.route('/order', methods=['GET', 'POST'])
@login_required
def create_order():
    patients = Patient.query.filter_by(is_active=True).all()
    doctors = Doctor.query.all()
    tests = LabTest.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            order = LabOrder(
                order_number=generate_lab_order_number(),
                patient_id=int(request.form.get('patient_id')),
                doctor_id=int(request.form.get('doctor_id')) if request.form.get('doctor_id') else None,
                ordered_by=current_user.id,
                priority=request.form.get('priority', 'Routine'),
                clinical_notes=request.form.get('clinical_notes', '').strip() or None
            )
            db.session.add(order)
            db.session.flush()
            
            test_ids = request.form.getlist('test_ids[]')
            for tid in test_ids:
                item = LabOrderItem(lab_order_id=order.id, lab_test_id=int(tid))
                db.session.add(item)
            
            db.session.commit()
            flash(f'Lab order {order.order_number} created successfully.', 'success')
            return redirect(url_for('lab.list_orders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('lab/order.html', patients=patients, doctors=doctors, tests=tests)


@lab_bp.route('/<int:id>')
@login_required
def view_order(id):
    order = LabOrder.query.get_or_404(id)
    return render_template('lab/view.html', order=order)


@lab_bp.route('/<int:id>/collect', methods=['POST'])
@login_required
def collect_sample(id):
    order = LabOrder.query.get_or_404(id)
    order.status = 'Sample Collected'
    order.sample_collected_at = datetime.utcnow()
    order.sample_collected_by = current_user.id
    db.session.commit()
    flash('Sample collection recorded.', 'success')
    return redirect(url_for('lab.view_order', id=id))


@lab_bp.route('/<int:id>/result', methods=['GET', 'POST'])
@login_required
def enter_result(id):
    order = LabOrder.query.get_or_404(id)
    if request.method == 'POST':
        try:
            for item in order.items:
                val = request.form.get(f'result_{item.id}')
                if val is not None:
                    item.result_value = val
                    item.reference_range = item.lab_test.normal_range
                    item.result_unit = item.lab_test.unit
                    item.is_abnormal = bool(request.form.get(f'abnormal_{item.id}'))
                    item.status = 'Completed'
                    item.tested_at = datetime.utcnow()
                    item.tested_by = current_user.id
            
            order.status = 'Completed'
            order.completed_at = datetime.utcnow()
            db.session.commit()
            flash('Results entered successfully.', 'success')
            return redirect(url_for('lab.view_order', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('lab/result.html', order=order)
