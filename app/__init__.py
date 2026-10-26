from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.main import main_bp
    from app.blueprints.patients import patients_bp
    from app.blueprints.appointments import appointments_bp
    from app.blueprints.doctors import doctors_bp
    from app.blueprints.billing import billing_bp
    from app.blueprints.records import records_bp
    from app.blueprints.adt import adt_bp
    from app.blueprints.pharmacy import pharmacy_bp
    from app.blueprints.lab import lab_bp
    from app.blueprints.staff import staff_bp
    from app.blueprints.inventory import inventory_bp
    from app.blueprints.reports import reports_bp
    from app.blueprints.portal import portal_bp
    from app.blueprints.emergency import emergency_bp
    from app.blueprints.nursing import nursing_bp
    from app.blueprints.radiology import radiology_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(doctors_bp, url_prefix='/doctors')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(records_bp, url_prefix='/records')
    app.register_blueprint(adt_bp, url_prefix='/adt')
    app.register_blueprint(pharmacy_bp, url_prefix='/pharmacy')
    app.register_blueprint(lab_bp, url_prefix='/lab')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(portal_bp, url_prefix='/portal')
    app.register_blueprint(emergency_bp, url_prefix='/emergency')
    app.register_blueprint(nursing_bp, url_prefix='/nursing')
    app.register_blueprint(radiology_bp, url_prefix='/radiology')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        from app.utils.seed import seed_data
        seed_data()

    return app
