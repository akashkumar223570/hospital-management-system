from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Bill, BillItem, Payment, Patient, generate_bill_number, AuditLog, InsuranceClaim
from datetime import datetime

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/')
@login_required
def list_bills():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    query = Bill.query.filter_by(is_cancelled=False)
    if status:
        query = query.filter_by(payment_status=status)
    bills = query.order_by(Bill.bill_date.desc()).paginate(page=page, per_page=20)
    return render_template('billing/list.html', bills=bills, status=status)


@billing_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()
    
    if request.method == 'POST':
        try:
            bill = Bill(
                bill_number=generate_bill_number(),
                patient_id=int(request.form.get('patient_id')),
                bill_type=request.form.get('bill_type', 'OPD'),
                discount_percent=float(request.form.get('discount_percent') or 0),
                notes=request.form.get('notes', '').strip() or None,
                created_by=current_user.id
            )
            db.session.add(bill)
            db.session.flush()
            
            # Add items from form (simple multiple items)
            descriptions = request.form.getlist('item_desc[]')
            quantities = request.form.getlist('item_qty[]')
            prices = request.form.getlist('item_price[]')
            types = request.form.getlist('item_type[]')
            
            for desc, qty, price, itype in zip(descriptions, quantities, prices, types):
                if desc.strip():
                    item = BillItem(
                        bill_id=bill.id,
                        item_type=itype or 'Other',
                        description=desc.strip(),
                        quantity=int(qty or 1),
                        unit_price=float(price or 0),
                        amount=int(qty or 1) * float(price or 0)
                    )
                    db.session.add(item)
            
            bill.recalculate()
            log = AuditLog(user_id=current_user.id, action='CREATE_BILL', entity='Bill',
                           entity_id=bill.id, details=f'Created bill {bill.bill_number}',
                           ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            flash(f'Bill {bill.bill_number} created successfully.', 'success')
            return redirect(url_for('billing.view', id=bill.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bill: {str(e)}', 'danger')
    
    return render_template('billing/create.html', patients=patients)


@billing_bp.route('/<int:id>')
@login_required
def view(id):
    bill = Bill.query.get_or_404(id)
    return render_template('billing/view.html', bill=bill)


@billing_bp.route('/<int:id>/payment', methods=['POST'])
@login_required
def add_payment(id):
    bill = Bill.query.get_or_404(id)
    try:
        amount = float(request.form.get('amount'))
        method = request.form.get('payment_method', 'Cash')
        txn = request.form.get('transaction_id', '').strip() or None
        
        payment = Payment(
            bill_id=bill.id,
            amount=amount,
            payment_method=method,
            transaction_id=txn,
            received_by=current_user.id
        )
        db.session.add(payment)
        bill.paid_amount += amount
        bill.recalculate()
        db.session.commit()
        flash(f'Payment of ₹{amount:.2f} recorded successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error recording payment: {str(e)}', 'danger')
    return redirect(url_for('billing.view', id=id))


@billing_bp.route('/claims')
@login_required
def claims():
    claims = InsuranceClaim.query.order_by(InsuranceClaim.submitted_date.desc()).all()
    return render_template('billing/claims.html', claims=claims)
