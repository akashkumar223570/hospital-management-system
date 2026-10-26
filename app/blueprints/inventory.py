from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import InventoryItem

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required
def list_items():
    items = InventoryItem.query.filter_by(is_active=True).order_by(InventoryItem.category, InventoryItem.name).all()
    low_stock = [i for i in items if i.is_low_stock]
    return render_template('inventory/list.html', items=items, low_stock=low_stock)
