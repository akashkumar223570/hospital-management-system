from datetime import datetime, date, timedelta
from app import db
from app.models import (
    User, Department, Doctor, Patient, Ward, Bed, Medicine, LabTest,
    RadiologyTest, Supplier, InventoryItem, Staff
)

def seed_data():
    """Seed initial data if database is empty."""
    if User.query.first():
        return  # Already seeded

    # ========== USERS ==========
    admin = User(username='admin', email='admin@citycare.com', full_name='System Administrator',
                 role='admin', phone='9999999999')
    admin.set_password('admin123')
    db.session.add(admin)

    # Doctors
    doc1_user = User(username='dr.smith', email='dr.smith@citycare.com', full_name='Dr. John Smith',
                     role='doctor', phone='9876543210')
    doc1_user.set_password('doctor123')
    db.session.add(doc1_user)

    doc2_user = User(username='dr.patel', email='dr.patel@citycare.com', full_name='Dr. Priya Patel',
                     role='doctor', phone='9876543211')
    doc2_user.set_password('doctor123')
    db.session.add(doc2_user)

    doc3_user = User(username='dr.khan', email='dr.khan@citycare.com', full_name='Dr. Ahmed Khan',
                     role='doctor', phone='9876543212')
    doc3_user.set_password('doctor123')
    db.session.add(doc3_user)

    # Nurses
    nurse1 = User(username='nurse.rita', email='nurse.rita@citycare.com', full_name='Rita Sharma',
                  role='nurse', phone='9876543220')
    nurse1.set_password('nurse123')
    db.session.add(nurse1)

    # Receptionist
    recep = User(username='reception', email='reception@citycare.com', full_name='Anita Verma',
                 role='receptionist', phone='9876543230')
    recep.set_password('recep123')
    db.session.add(recep)

    # Pharmacist
    pharma = User(username='pharmacist', email='pharmacy@citycare.com', full_name='Ramesh Gupta',
                  role='pharmacist', phone='9876543240')
    pharma.set_password('pharma123')
    db.session.add(pharma)

    # Lab Tech
    labtech = User(username='labtech', email='lab@citycare.com', full_name='Suresh Kumar',
                   role='lab_tech', phone='9876543250')
    labtech.set_password('lab123')
    db.session.add(labtech)

    db.session.flush()

    # ========== DEPARTMENTS ==========
    depts = [
        Department(name='Cardiology', description='Heart and cardiovascular care'),
        Department(name='Neurology', description='Brain and nervous system'),
        Department(name='Orthopedics', description='Bones, joints and musculoskeletal'),
        Department(name='General Medicine', description='Internal medicine and general care'),
        Department(name='Pediatrics', description='Child healthcare'),
        Department(name='Emergency', description='Emergency and trauma care'),
        Department(name='Radiology', description='Imaging and diagnostics'),
        Department(name='Laboratory', description='Pathology and lab services'),
        Department(name='Pharmacy', description='Medication management'),
    ]
    for d in depts:
        db.session.add(d)
    db.session.flush()

    # ========== DOCTORS ==========
    doc1 = Doctor(user_id=doc1_user.id, department_id=1, specialization='Interventional Cardiology',
                  qualification='MBBS, MD, DM Cardiology', experience_years=15,
                  consultation_fee=800, license_number='MCI-12345',
                  availability='Mon-Sat 9:00-14:00', bio='Senior cardiologist with 15 years experience.')
    doc2 = Doctor(user_id=doc2_user.id, department_id=2, specialization='Neurology',
                  qualification='MBBS, MD, DM Neurology', experience_years=12,
                  consultation_fee=900, license_number='MCI-12346',
                  availability='Mon-Fri 10:00-16:00', bio='Specialist in stroke and epilepsy.')
    doc3 = Doctor(user_id=doc3_user.id, department_id=4, specialization='Internal Medicine',
                  qualification='MBBS, MD Medicine', experience_years=10,
                  consultation_fee=600, license_number='MCI-12347',
                  availability='Mon-Sat 9:00-17:00', bio='Experienced general physician.')
    db.session.add_all([doc1, doc2, doc3])
    db.session.flush()

    # Update department heads
    depts[0].head_doctor_id = doc1.id
    depts[1].head_doctor_id = doc2.id

    # ========== WARDS & BEDS ==========
    wards_data = [
        ('General Ward A', 4, 'General', 20, 1200),
        ('General Ward B', 4, 'General', 15, 1200),
        ('ICU', 6, 'ICU', 8, 5000),
        ('Private Room', 4, 'Private', 10, 3500),
        ('Semi-Private', 4, 'Semi-Private', 12, 2200),
        ('Pediatric Ward', 5, 'General', 10, 1500),
        ('Emergency Bay', 6, 'Emergency', 6, 2000),
    ]
    for name, dept_id, wtype, beds, charge in wards_data:
        ward = Ward(name=name, department_id=dept_id, ward_type=wtype, total_beds=beds)
        db.session.add(ward)
        db.session.flush()
        for i in range(1, beds + 1):
            bed = Bed(bed_number=f'{name[:3].upper()}-{i:02d}', ward_id=ward.id,
                      status='Available', bed_type='ICU' if wtype == 'ICU' else 'Standard',
                      daily_charge=charge)
            db.session.add(bed)

    # ========== MEDICINES ==========
    medicines = [
        ('Paracetamol 500mg', 'Paracetamol', 'Analgesic', 'Cipla', 'Tablet', '500mg', 500, 50, 2.0, 5.0),
        ('Amoxicillin 500mg', 'Amoxicillin', 'Antibiotic', 'Sun Pharma', 'Capsule', '500mg', 300, 40, 8.0, 15.0),
        ('Metformin 500mg', 'Metformin', 'Antidiabetic', 'USV', 'Tablet', '500mg', 400, 50, 3.0, 8.0),
        ('Amlodipine 5mg', 'Amlodipine', 'Antihypertensive', 'Pfizer', 'Tablet', '5mg', 350, 40, 4.0, 10.0),
        ('Omeprazole 20mg', 'Omeprazole', 'Antacid', 'Dr Reddy', 'Capsule', '20mg', 280, 30, 5.0, 12.0),
        ('Cetirizine 10mg', 'Cetirizine', 'Antihistamine', 'GSK', 'Tablet', '10mg', 200, 30, 1.5, 4.0),
        ('Azithromycin 500mg', 'Azithromycin', 'Antibiotic', 'Cipla', 'Tablet', '500mg', 150, 20, 15.0, 35.0),
        ('Ibuprofen 400mg', 'Ibuprofen', 'NSAID', 'Abbott', 'Tablet', '400mg', 250, 40, 2.5, 6.0),
        ('ORS Powder', 'Oral Rehydration', 'Electrolyte', 'WHO', 'Sachet', '21.8g', 100, 20, 5.0, 12.0),
        ('Insulin Glargine', 'Insulin', 'Antidiabetic', 'Sanofi', 'Injection', '100IU/ml', 50, 10, 450.0, 650.0),
    ]
    for name, gen, cat, mfr, unit, strength, stock, reorder, cost, sell in medicines:
        m = Medicine(name=name, generic_name=gen, category=cat, manufacturer=mfr,
                     unit=unit, strength=strength, current_stock=stock, reorder_level=reorder,
                     unit_price=cost, selling_price=sell)
        db.session.add(m)

    # ========== LAB TESTS ==========
    lab_tests = [
        ('Complete Blood Count', 'CBC', 'Hematology', 'Blood', 350, 'As per age/gender', '', 4),
        ('Blood Glucose Fasting', 'FBS', 'Biochemistry', 'Blood', 120, '70-100 mg/dL', 'mg/dL', 2),
        ('Lipid Profile', 'LIPID', 'Biochemistry', 'Blood', 600, 'See individual', '', 6),
        ('Liver Function Test', 'LFT', 'Biochemistry', 'Blood', 550, 'See individual', '', 6),
        ('Kidney Function Test', 'KFT', 'Biochemistry', 'Blood', 500, 'See individual', '', 6),
        ('Thyroid Profile (T3,T4,TSH)', 'TFT', 'Endocrinology', 'Blood', 700, 'See individual', '', 24),
        ('Urine Routine', 'URINE', 'Clinical Pathology', 'Urine', 150, 'Normal', '', 2),
        ('HbA1c', 'HBA1C', 'Biochemistry', 'Blood', 450, '4.0-5.6%', '%', 24),
        ('COVID-19 RT-PCR', 'COVID', 'Molecular', 'Nasopharyngeal', 800, 'Negative', '', 12),
        ('Blood Group & Rh', 'BG', 'Hematology', 'Blood', 150, 'A/B/AB/O ±', '', 2),
    ]
    for name, code, cat, sample, price, nr, unit, tat in lab_tests:
        t = LabTest(name=name, code=code, category=cat, sample_type=sample,
                    price=price, normal_range=nr, unit=unit, turnaround_hours=tat)
        db.session.add(t)

    # ========== RADIOLOGY TESTS ==========
    rad_tests = [
        ('Chest X-Ray PA', 'X-Ray', 'Chest', 400, 15),
        ('X-Ray Knee AP/Lat', 'X-Ray', 'Knee', 500, 20),
        ('CT Brain Plain', 'CT', 'Brain', 3500, 30),
        ('CT Chest', 'CT', 'Chest', 4500, 40),
        ('MRI Brain', 'MRI', 'Brain', 8000, 45),
        ('MRI Knee', 'MRI', 'Knee', 7500, 40),
        ('Ultrasound Abdomen', 'Ultrasound', 'Abdomen', 1200, 25),
        ('Ultrasound Pelvis', 'Ultrasound', 'Pelvis', 1000, 20),
        ('2D Echo', 'Ultrasound', 'Heart', 2500, 30),
        ('Mammography Bilateral', 'Mammography', 'Breast', 2000, 30),
    ]
    for name, mod, part, price, dur in rad_tests:
        r = RadiologyTest(name=name, modality=mod, body_part=part, price=price, duration_minutes=dur)
        db.session.add(r)

    # ========== SUPPLIERS ==========
    suppliers = [
        Supplier(name='MedPlus Distributors', contact_person='Rajesh', phone='9876500001',
                 email='orders@medplus.com', address='Industrial Area, Phase 1'),
        Supplier(name='Apollo Pharmacy Supply', contact_person='Sneha', phone='9876500002',
                 email='supply@apollo.com', address='Warehouse Zone B'),
    ]
    db.session.add_all(suppliers)

    # ========== INVENTORY ==========
    inv_items = [
        ('Surgical Gloves (Box)', 'Consumable', 'INV-001', 'Box', 100, 20, 250, 'Store'),
        ('Face Masks (Box of 50)', 'Consumable', 'INV-002', 'Box', 80, 15, 150, 'Store'),
        ('IV Cannula 20G', 'Consumable', 'INV-003', 'Piece', 200, 50, 15, 'Store'),
        ('Syringe 5ml', 'Consumable', 'INV-004', 'Piece', 500, 100, 5, 'Store'),
        ('ECG Machine', 'Equipment', 'INV-005', 'Unit', 3, 1, 85000, 'Cardiology'),
        ('Defibrillator', 'Equipment', 'INV-006', 'Unit', 2, 1, 250000, 'Emergency'),
        ('Patient Monitor', 'Equipment', 'INV-007', 'Unit', 10, 2, 45000, 'ICU'),
        ('Surgical Gown', 'Consumable', 'INV-008', 'Piece', 150, 30, 80, 'OT'),
    ]
    for name, cat, code, unit, stock, reorder, cost, loc in inv_items:
        i = InventoryItem(name=name, category=cat, item_code=code, unit=unit,
                          current_stock=stock, reorder_level=reorder, unit_cost=cost, location=loc)
        db.session.add(i)

    # ========== SAMPLE PATIENTS ==========
    patients = [
        Patient(uhid='HMS-20241001-0001', first_name='Rahul', last_name='Sharma',
                date_of_birth=date(1985, 5, 15), gender='Male', blood_group='B+',
                phone='9812345678', email='rahul.s@email.com', address='45 MG Road',
                city='Mumbai', state='Maharashtra', pincode='400001',
                emergency_contact_name='Sunita Sharma', emergency_contact_phone='9812345679',
                emergency_contact_relation='Wife', allergies='Penicillin',
                medical_history='Hypertension since 2020'),
        Patient(uhid='HMS-20241001-0002', first_name='Priya', last_name='Mehta',
                date_of_birth=date(1992, 8, 22), gender='Female', blood_group='O+',
                phone='9823456789', email='priya.m@email.com', address='12 Park Street',
                city='Delhi', state='Delhi', pincode='110001',
                emergency_contact_name='Amit Mehta', emergency_contact_phone='9823456790',
                emergency_contact_relation='Husband'),
        Patient(uhid='HMS-20241002-0001', first_name='Aarav', last_name='Singh',
                date_of_birth=date(2015, 3, 10), gender='Male', blood_group='A+',
                phone='9834567890', address='78 Civil Lines',
                city='Lucknow', state='Uttar Pradesh', pincode='226001',
                emergency_contact_name='Neha Singh', emergency_contact_phone='9834567891',
                emergency_contact_relation='Mother'),
    ]
    db.session.add_all(patients)

    # Staff profiles
    staff_nurse = Staff(user_id=nurse1.id, employee_id='EMP-N001', department_id=4,
                        designation='Staff Nurse', joining_date=date(2020, 1, 15),
                        shift='Morning', salary=35000)
    staff_recep = Staff(user_id=recep.id, employee_id='EMP-R001', department_id=4,
                        designation='Receptionist', joining_date=date(2021, 6, 1),
                        shift='Morning', salary=25000)
    db.session.add_all([staff_nurse, staff_recep])

    db.session.commit()
    print("✓ Database seeded successfully with sample data.")
