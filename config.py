import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hms-super-secret-key-change-in-production-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'hms.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ITEMS_PER_PAGE = 20
    HOSPITAL_NAME = "City Care Multi-Specialty Hospital"
    HOSPITAL_ADDRESS = "123 Healthcare Avenue, Medical District"
    HOSPITAL_PHONE = "+91-1800-123-4567"
    HOSPITAL_EMAIL = "info@citycarehospital.com"
