from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import RadiologyOrder, RadiologyTest, Patient, Doctor, generate_radiology_order_number
from datetime import datetime

radiology_bp = Blueprint('radiology', __name__)

@radiology_bp.route('/')
@login_required
def list_orders():
    orders = RadiologyOrder.query.order_by(RadiologyOrder.ordered_date.desc()).all()
    return render_template('radiology/list.html', orders=orders)


@radiology_bp.route('/tests')
@login_required
def tests():
    tests = RadiologyTest.query.filter_by(is_active=True).all()
    return render_template('radiology/tests.html', tests=tests)


@radiology_bp.route('/order', methods=['GET', 'POST'])
@login_required
def create_order():
    patients = Patient.query.filter_by(is_active=True).all()
    doctors = Doctor.query.all()
    tests = RadiologyTest.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            order = RadiologyOrder(
                order_number=generate_radiology_order_number(),
                patient_id=int(request.form.get('patient_id')),
                doctor_id=int(request.form.get('doctor_id')) if request.form.get('doctor_id') else None,
                test_id=int(request.form.get('test_id')),
                clinical_indication=request.form.get('clinical_indication', '').strip() or None,
                status='Ordered'
            )
            db.session.add(order)
            db.session.commit()
            flash(f'Radiology order {order.order_number} created.', 'success')
            return redirect(url_for('radiology.list_orders'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('radiology/order.html', patients=patients, doctors=doctors, tests=tests)


@radiology_bp.route('/<int:id>/report', methods=['GET', 'POST'])
@login_required
def report(id):
    order = RadiologyOrder.query.get_or_404(id)
    if request.method == 'POST':
        order.report = request.form.get('report', '').strip()
        order.status = 'Reported'
        order.reported_by = current_user.id
        order.reported_at = datetime.utcnow()
        db.session.commit()
        flash('Report saved.', 'success')
        return redirect(url_for('radiology.list_orders'))
    return render_template('radiology/report.html', order=order)
