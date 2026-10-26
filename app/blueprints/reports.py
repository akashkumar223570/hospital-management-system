from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models import Patient, Appointment, Admission, Bill, Medicine, LabOrder, Bed, Department
from datetime import date, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Daily stats
    daily_regs = Patient.query.filter(func.date(Patient.registration_date) == today).count()
    opd_today = Appointment.query.filter(
        Appointment.appointment_date == today,
        Appointment.appointment_type == 'OPD'
    ).count()
    ipd_count = Admission.query.filter_by(status='Admitted').count()
    
    total_beds = Bed.query.count()
    occupied = Bed.query.filter_by(status='Occupied').count()
    occupancy = round(occupied / total_beds * 100, 1) if total_beds else 0
    
    # Revenue
    today_revenue = db.session.query(func.coalesce(func.sum(Bill.paid_amount), 0)).filter(
        func.date(Bill.bill_date) == today
    ).scalar() or 0
    
    outstanding = db.session.query(func.coalesce(func.sum(Bill.balance_amount), 0)).filter(
        Bill.payment_status.in_(['Pending', 'Partial']),
        Bill.is_cancelled == False
    ).scalar() or 0
    
    # Lab TAT (simple count of pending)
    pending_labs = LabOrder.query.filter(LabOrder.status.in_(['Ordered', 'Sample Collected', 'In Progress'])).count()
    
    # Low stock
    low_meds = Medicine.query.filter(Medicine.current_stock <= Medicine.reorder_level).count()
    
    stats = {
        'daily_regs': daily_regs,
        'opd_today': opd_today,
        'ipd_count': ipd_count,
        'occupancy': occupancy,
        'total_beds': total_beds,
        'occupied': occupied,
        'today_revenue': today_revenue,
        'outstanding': outstanding,
        'pending_labs': pending_labs,
        'low_meds': low_meds,
    }
    
    return render_template('reports/index.html', stats=stats, today=today)
