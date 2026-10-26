from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Medicine, MedicineBatch, StockMovement, Prescription, PrescriptionItem, Supplier
from datetime import datetime, date

pharmacy_bp = Blueprint('pharmacy', __name__)

@pharmacy_bp.route('/')
@login_required
def list_medicines():
    search = request.args.get('search', '').strip()
    query = Medicine.query.filter_by(is_active=True)
    if search:
        query = query.filter(db.or_(
            Medicine.name.ilike(f'%{search}%'),
            Medicine.generic_name.ilike(f'%{search}%')
        ))
    medicines = query.order_by(Medicine.name).all()
    low_stock = [m for m in medicines if m.is_low_stock]
    return render_template('pharmacy/list.html', medicines=medicines, low_stock=low_stock, search=search)


@pharmacy_bp.route('/prescriptions')
@login_required
def prescriptions():
    status = request.args.get('status', 'Active')
    rxs = Prescription.query.filter_by(status=status).order_by(Prescription.prescription_date.desc()).all()
    return render_template('pharmacy/prescriptions.html', prescriptions=rxs, status=status)


@pharmacy_bp.route('/dispense/<int:id>', methods=['GET', 'POST'])
@login_required
def dispense(id):
    rx = Prescription.query.get_or_404(id)
    if request.method == 'POST':
        try:
            for item in rx.items:
                med = Medicine.query.filter(Medicine.name.ilike(f'%{item.medicine_name}%')).first()
                if med and med.current_stock >= item.quantity:
                    med.current_stock -= item.quantity
                    movement = StockMovement(
                        medicine_id=med.id,
                        movement_type='OUT',
                        quantity=item.quantity,
                        reference=f'RX-{rx.id}',
                        performed_by=current_user.id,
                        notes=f'Dispensed for prescription {rx.id}'
                    )
                    db.session.add(movement)
            
            rx.is_dispensed = True
            rx.status = 'Dispensed'
            rx.dispensed_at = datetime.utcnow()
            rx.dispensed_by = current_user.id
            db.session.commit()
            flash('Prescription dispensed successfully. Stock updated.', 'success')
            return redirect(url_for('pharmacy.prescriptions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('pharmacy/dispense.html', prescription=rx)


@pharmacy_bp.route('/stock-in', methods=['GET', 'POST'])
@login_required
def stock_in():
    medicines = Medicine.query.filter_by(is_active=True).order_by(Medicine.name).all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        try:
            med_id = int(request.form.get('medicine_id'))
            qty = int(request.form.get('quantity'))
            batch_no = request.form.get('batch_number', '').strip()
            expiry = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
            
            med = Medicine.query.get(med_id)
            med.current_stock += qty
            
            batch = MedicineBatch(
                medicine_id=med_id,
                batch_number=batch_no,
                expiry_date=expiry,
                quantity=qty,
                purchase_price=float(request.form.get('purchase_price') or 0),
                supplier_id=int(request.form.get('supplier_id')) if request.form.get('supplier_id') else None
            )
            db.session.add(batch)
            
            movement = StockMovement(
                medicine_id=med_id,
                movement_type='IN',
                quantity=qty,
                reference=batch_no,
                performed_by=current_user.id
            )
            db.session.add(movement)
            db.session.commit()
            flash(f'Stock added: {qty} units of {med.name}', 'success')
            return redirect(url_for('pharmacy.list_medicines'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('pharmacy/stock_in.html', medicines=medicines, suppliers=suppliers)
