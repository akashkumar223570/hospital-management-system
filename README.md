# City Care Hospital Management System (HMS)

A professional, modular **Flask-based Hospital Management System** covering the complete roadmap:

- Patient Management (UHID, demographics, history, allergies)
- Appointment Management (booking, queue, status, walk-ins)
- Doctor & Department Management
- Billing & Payments (multi-item bills, payments, insurance claims stub)
- Medical Records & Prescriptions
- ADT (Admission, Discharge, Transfer) with bed management
- Pharmacy (inventory, batches, dispensing, stock movements)
- Laboratory Information System (orders, sample tracking, results)
- Staff / HR basics
- Role-Based Access Control & Audit Logs
- Inventory (equipment & consumables)
- Emergency & Triage
- Nursing notes & clinical workflow
- Radiology orders & reports
- Reports & Analytics dashboard
- Patient Portal (UHID lookup)
- Security foundations (hashed passwords, sessions, audit trail)

## Quick Start

```bash
# 1. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

## Demo Credentials

| Role         | Username     | Password    |
|--------------|--------------|-------------|
| Admin        | `admin`      | `admin123`  |
| Doctor       | `dr.smith`   | `doctor123` |
| Doctor       | `dr.patel`   | `doctor123` |
| Receptionist | `reception`  | `recep123`  |
| Pharmacist   | `pharmacist` | `pharma123` |
| Lab Tech     | `labtech`    | `lab123`    |
| Nurse        | `nurse.rita` | `nurse123`  |

## Project Structure

```
hms_flask/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # All database models
│   ├── blueprints/          # Modular feature blueprints
│   │   ├── auth.py
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── billing.py
│   │   ├── adt.py
│   │   ├── pharmacy.py
│   │   ├── lab.py
│   │   ├── emergency.py
│   │   ├── nursing.py
│   │   ├── radiology.py
│   │   └── ...
│   ├── templates/           # Jinja2 + Bootstrap 5 UI
│   ├── static/              # CSS, JS
│   └── utils/seed.py        # Sample data seeder
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Features by Module

### 1. Patient Management
- Unique Hospital ID (UHID) generation
- Full demographics, emergency contact, insurance
- Medical history, allergies, chronic conditions
- Visit history, linked appointments, records, bills

### 2. Appointments
- Doctor/department based booking
- Queue numbers, walk-ins, status workflow
- Today’s queue view for OPD

### 3. ADT
- Ward & bed master with real-time availability
- Admission → Transfer → Discharge with summary
- Length of stay calculation

### 4. Pharmacy
- Medicine master with reorder levels
- Batch tracking & expiry
- Stock-in / stock-out movements
- Prescription dispensing with auto stock deduction

### 5. Laboratory
- Test catalog with TAT & pricing
- Order creation (multi-test)
- Sample collection → Result entry → Abnormal flagging

### 6. Billing
- Multi-item bills (consultation, lab, pharmacy, room…)
- Discounts, payment recording (Cash/Card/UPI)
- Outstanding balance tracking

### 7. Clinical
- Medical records with vitals & diagnosis
- Prescription writing linked to records
- Emergency triage (Critical → Non-Urgent)
- Nursing notes with timeline

### 8. Admin & Security
- Role-based users (admin, doctor, nurse, receptionist, pharmacist, lab_tech…)
- Audit log of important actions
- Secure password hashing (Werkzeug)

## Technology Stack

- **Backend**: Flask 3, SQLAlchemy 2, Flask-Login, Flask-Migrate
- **Database**: SQLite (default) — easily switchable to PostgreSQL/MySQL
- **Frontend**: Bootstrap 5, Bootstrap Icons, custom CSS
- **Auth**: Session-based with role checks

## Production Notes

1. Change `SECRET_KEY` in `config.py` or set environment variable.
2. Use a production WSGI server: `gunicorn -w 4 run:app`
3. Switch database URI to PostgreSQL for multi-user production.
4. Configure proper backup of the `instance/` folder.
5. Advanced modules (full PACS/DICOM, FHIR, ABDM, AI prediction) are structured for extension.

## License

Educational / demonstration use. Adapt freely for final-year projects or internal hospital systems.
