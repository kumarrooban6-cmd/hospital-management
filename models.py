import uuid
from datetime import datetime, date
from database import get_db_connection

def generate_uid(prefix=""):
    """Generate clean human-readable identifier."""
    unique_suffix = str(uuid.uuid4().hex[:4]).upper()
    return f"{prefix}-{unique_suffix}"

# ==============================================================================
# DASHBOARD METRICS
# ==============================================================================
def get_dashboard_stats():
    """Fetch aggregated metrics for the executive dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("SELECT COUNT(*) AS total_patients FROM patients")
    total_patients = cursor.fetchone()["total_patients"]

    cursor.execute("SELECT COUNT(*) AS total_doctors FROM doctors WHERE status = 'Active'")
    total_doctors = cursor.fetchone()["total_doctors"]

    cursor.execute("SELECT COUNT(*) AS today_appointments FROM appointments WHERE appointment_date = ?", (today,))
    today_appointments = cursor.fetchone()["today_appointments"]

    cursor.execute("SELECT COUNT(*) AS available_beds FROM beds WHERE status = 'Available'")
    available_beds = cursor.fetchone()["available_beds"]

    cursor.execute("SELECT COUNT(*) AS total_beds FROM beds")
    total_beds = cursor.fetchone()["total_beds"]

    cursor.execute("SELECT COUNT(*) AS low_stock FROM medicines WHERE stock_quantity <= 15")
    low_stock = cursor.fetchone()["low_stock"]

    cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS total_revenue FROM invoices WHERE payment_status = 'Paid'")
    total_revenue = cursor.fetchone()["total_revenue"]

    cursor.execute("""
        SELECT a.*, p.name AS patient_name, d.name AS doctor_name, d.specialization
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.appointment_date = ?
        ORDER BY a.appointment_time ASC
        LIMIT 6
    """, (today,))
    upcoming_appointments = cursor.fetchall()

    cursor.execute("""
        SELECT i.*, p.name AS patient_name
        FROM invoices i
        JOIN patients p ON i.patient_id = p.id
        ORDER BY i.id DESC
        LIMIT 5
    """, ())
    recent_invoices = cursor.fetchall()

    conn.close()
    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "today_appointments": today_appointments,
        "available_beds": available_beds,
        "total_beds": total_beds,
        "low_stock": low_stock,
        "total_revenue": total_revenue,
        "upcoming_appointments": upcoming_appointments,
        "recent_invoices": recent_invoices
    }

# ==============================================================================
# PATIENT MANAGEMENT
# ==============================================================================
def get_all_patients(search_query=None):
    """Retrieve all patients with optional name/phone/UID search."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        param = f"%{search_query}%"
        cursor.execute("""
            SELECT * FROM patients 
            WHERE name LIKE ? OR phone LIKE ? OR patient_uid LIKE ? OR blood_group LIKE ?
            ORDER BY id DESC
        """, (param, param, param, param))
    else:
        cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = cursor.fetchall()
    conn.close()
    return patients

def get_patient_by_id(patient_id):
    """Get patient by primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    return patient

def get_patient_complete_record(patient_id):
    """Fetch complete patient history: appointments, admissions, prescriptions, and invoices."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient = cursor.fetchone()
    if not patient:
        conn.close()
        return None

    # Appointments
    cursor.execute("""
        SELECT a.*, d.name as doctor_name, d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.patient_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """, (patient_id,))
    appointments = cursor.fetchall()

    # Bed admissions
    cursor.execute("""
        SELECT ba.*, b.bed_number, b.ward_type, b.charge_per_day
        FROM bed_allocations ba
        JOIN beds b ON ba.bed_id = b.id
        WHERE ba.patient_id = ?
        ORDER BY ba.id DESC
    """, (patient_id,))
    admissions = cursor.fetchall()

    # Prescriptions
    cursor.execute("""
        SELECT p.*, m.name as medicine_name, m.dosage, d.name as doctor_name
        FROM prescriptions p
        JOIN medicines m ON p.medicine_id = m.id
        LEFT JOIN doctors d ON p.doctor_id = d.id
        WHERE p.patient_id = ?
        ORDER BY p.id DESC
    """, (patient_id,))
    prescriptions = cursor.fetchall()

    # Invoices
    cursor.execute("""
        SELECT * FROM invoices WHERE patient_id = ? ORDER BY id DESC
    """, (patient_id,))
    invoices = cursor.fetchall()

    conn.close()
    return {
        "patient": patient,
        "appointments": appointments,
        "admissions": admissions,
        "prescriptions": prescriptions,
        "invoices": invoices
    }

def create_patient(data):
    """Register a new patient."""
    conn = get_db_connection()
    cursor = conn.cursor()
    uid = generate_uid("PAT")
    cursor.execute("""
        INSERT INTO patients (patient_uid, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        data.get("name"),
        int(data.get("age", 0)),
        data.get("gender"),
        data.get("blood_group"),
        data.get("phone"),
        data.get("email"),
        data.get("address"),
        data.get("emergency_contact"),
        data.get("medical_history")
    ))
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return patient_id

def update_patient(patient_id, data):
    """Update patient demographic and medical profile."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE patients 
        SET name = ?, age = ?, gender = ?, blood_group = ?, phone = ?, email = ?, address = ?, emergency_contact = ?, medical_history = ?
        WHERE id = ?
    """, (
        data.get("name"),
        int(data.get("age", 0)),
        data.get("gender"),
        data.get("blood_group"),
        data.get("phone"),
        data.get("email"),
        data.get("address"),
        data.get("emergency_contact"),
        data.get("medical_history"),
        patient_id
    ))
    conn.commit()
    conn.close()

def delete_patient(patient_id):
    """Delete a patient record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()

# ==============================================================================
# DOCTOR MANAGEMENT
# ==============================================================================
def get_all_doctors(search_query=None):
    """Retrieve all doctors with optional filter."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        param = f"%{search_query}%"
        cursor.execute("""
            SELECT * FROM doctors 
            WHERE name LIKE ? OR specialization LIKE ? OR room_number LIKE ?
            ORDER BY id ASC
        """, (param, param, param))
    else:
        cursor.execute("SELECT * FROM doctors ORDER BY id ASC")
    doctors = cursor.fetchall()
    conn.close()
    return doctors

def get_doctor_by_id(doctor_id):
    """Fetch doctor by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cursor.fetchone()
    conn.close()
    return doctor

def create_doctor(data):
    """Add a new doctor to the roster."""
    conn = get_db_connection()
    cursor = conn.cursor()
    uid = generate_uid("DOC")
    cursor.execute("""
        INSERT INTO doctors (doctor_uid, name, specialization, qualification, phone, email, consultation_fee, available_days, available_time, room_number, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        data.get("name"),
        data.get("specialization"),
        data.get("qualification"),
        data.get("phone"),
        data.get("email"),
        float(data.get("consultation_fee", 50.0)),
        data.get("available_days"),
        data.get("available_time"),
        data.get("room_number"),
        data.get("status", "Active")
    ))
    conn.commit()
    doctor_id = cursor.lastrowid
    conn.close()
    return doctor_id

def update_doctor(doctor_id, data):
    """Update doctor information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE doctors
        SET name = ?, specialization = ?, qualification = ?, phone = ?, email = ?, consultation_fee = ?, available_days = ?, available_time = ?, room_number = ?, status = ?
        WHERE id = ?
    """, (
        data.get("name"),
        data.get("specialization"),
        data.get("qualification"),
        data.get("phone"),
        data.get("email"),
        float(data.get("consultation_fee", 50.0)),
        data.get("available_days"),
        data.get("available_time"),
        data.get("room_number"),
        data.get("status"),
        doctor_id
    ))
    conn.commit()
    conn.close()

def delete_doctor(doctor_id):
    """Delete a doctor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
    conn.commit()
    conn.close()

# ==============================================================================
# APPOINTMENT MANAGEMENT
# ==============================================================================
def get_all_appointments(date_filter=None, status_filter=None):
    """Retrieve appointments with optional date or status filter."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT a.*, p.name AS patient_name, p.phone AS patient_phone, p.blood_group,
               d.name AS doctor_name, d.specialization, d.room_number, d.consultation_fee
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE 1=1
    """
    params = []
    if date_filter:
        query += " AND a.appointment_date = ?"
        params.append(date_filter)
    if status_filter and status_filter != "All":
        query += " AND a.status = ?"
        params.append(status_filter)

    query += " ORDER BY a.appointment_date DESC, a.appointment_time ASC"
    cursor.execute(query, params)
    appointments = cursor.fetchall()
    conn.close()
    return appointments

def get_appointment_by_id(appointment_id):
    """Fetch appointment details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.name AS patient_name, d.name AS doctor_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.id = ?
    """, (appointment_id,))
    appointment = cursor.fetchone()
    conn.close()
    return appointment

def create_appointment(data):
    """Schedule a new appointment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    uid = generate_uid("APP")
    cursor.execute("""
        INSERT INTO appointments (appointment_uid, patient_id, doctor_id, appointment_date, appointment_time, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Scheduled')
    """, (
        uid,
        int(data.get("patient_id")),
        int(data.get("doctor_id")),
        data.get("appointment_date"),
        data.get("appointment_time"),
        data.get("reason")
    ))
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return app_id

def update_appointment_status(appointment_id, status, diagnosis=None):
    """Update status and clinical notes of an appointment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if diagnosis:
        cursor.execute("UPDATE appointments SET status = ?, diagnosis = ? WHERE id = ?", (status, diagnosis, appointment_id))
    else:
        cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()

def delete_appointment(appointment_id):
    """Cancel and delete an appointment."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()

# ==============================================================================
# BED & INPATIENT (IPD) MANAGEMENT
# ==============================================================================
def get_all_beds():
    """Get all beds with their current occupancy and patient info."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, ba.id AS allocation_id, ba.admitted_at, p.name AS patient_name, p.patient_uid
        FROM beds b
        LEFT JOIN bed_allocations ba ON b.id = ba.bed_id AND ba.status = 'Admitted'
        LEFT JOIN patients p ON ba.patient_id = p.id
        ORDER BY b.ward_type, b.bed_number
    """)
    beds = cursor.fetchall()
    conn.close()
    return beds

def get_available_beds():
    """Get list of unallocated beds."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM beds WHERE status = 'Available' ORDER BY bed_number")
    beds = cursor.fetchall()
    conn.close()
    return beds

def allocate_bed(bed_id, patient_id, notes=""):
    """Admit patient to bed and mark bed as Occupied."""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute("""
        INSERT INTO bed_allocations (bed_id, patient_id, admitted_at, status, notes)
        VALUES (?, ?, ?, 'Admitted', ?)
    """, (bed_id, patient_id, today, notes))

    cursor.execute("UPDATE beds SET status = 'Occupied' WHERE id = ?", (bed_id,))
    conn.commit()
    conn.close()

def discharge_bed(allocation_id):
    """Discharge patient from bed and free up bed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute("SELECT bed_id FROM bed_allocations WHERE id = ?", (allocation_id,))
    alloc = cursor.fetchone()
    if alloc:
        bed_id = alloc["bed_id"]
        cursor.execute("UPDATE bed_allocations SET status = 'Discharged', discharged_at = ? WHERE id = ?", (today, allocation_id))
        cursor.execute("UPDATE beds SET status = 'Available' WHERE id = ?", (bed_id,))
        conn.commit()
    conn.close()

# ==============================================================================
# PHARMACY & MEDICINE INVENTORY
# ==============================================================================
def get_all_medicines(search_query=None):
    """Retrieve medicines catalog."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if search_query:
        param = f"%{search_query}%"
        cursor.execute("""
            SELECT * FROM medicines 
            WHERE name LIKE ? OR category LIKE ? OR medicine_code LIKE ?
            ORDER BY name ASC
        """, (param, param, param))
    else:
        cursor.execute("SELECT * FROM medicines ORDER BY name ASC")
    medicines = cursor.fetchall()
    conn.close()
    return medicines

def get_medicine_by_id(medicine_id):
    """Get single medicine by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
    med = cursor.fetchone()
    conn.close()
    return med

def create_medicine(data):
    """Add new medicine to inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()
    uid = generate_uid("MED")
    cursor.execute("""
        INSERT INTO medicines (medicine_code, name, category, dosage, stock_quantity, unit_price, expiry_date, manufacturer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        data.get("name"),
        data.get("category"),
        data.get("dosage"),
        int(data.get("stock_quantity", 0)),
        float(data.get("unit_price", 0.0)),
        data.get("expiry_date"),
        data.get("manufacturer")
    ))
    conn.commit()
    med_id = cursor.lastrowid
    conn.close()
    return med_id

def update_medicine(medicine_id, data):
    """Update medicine details and stock."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE medicines 
        SET name = ?, category = ?, dosage = ?, stock_quantity = ?, unit_price = ?, expiry_date = ?, manufacturer = ?
        WHERE id = ?
    """, (
        data.get("name"),
        data.get("category"),
        data.get("dosage"),
        int(data.get("stock_quantity", 0)),
        float(data.get("unit_price", 0.0)),
        data.get("expiry_date"),
        data.get("manufacturer"),
        medicine_id
    ))
    conn.commit()
    conn.close()

def delete_medicine(medicine_id):
    """Remove medicine from catalog."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    conn.commit()
    conn.close()

def dispense_medicine(patient_id, medicine_id, doctor_id, quantity, dosage_instructions):
    """Dispense medicine to patient and decrement stock inventory."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT stock_quantity, unit_price FROM medicines WHERE id = ?", (medicine_id,))
    med = cursor.fetchone()
    if not med or med["stock_quantity"] < quantity:
        conn.close()
        return False, "Insufficient stock available"

    total_price = quantity * med["unit_price"]
    today = date.today().isoformat()

    cursor.execute("""
        INSERT INTO prescriptions (patient_id, doctor_id, medicine_id, quantity, dosage_instructions, total_price, prescribed_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, doctor_id if doctor_id else None, medicine_id, quantity, dosage_instructions, total_price, today))

    cursor.execute("""
        UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?
    """, (quantity, medicine_id))

    conn.commit()
    conn.close()
    return True, "Medicine dispensed successfully"

def get_prescriptions_list():
    """Fetch full list of dispensed prescriptions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, pt.name AS patient_name, pt.phone AS patient_phone,
               m.name AS medicine_name, m.dosage, m.unit_price,
               d.name AS doctor_name
        FROM prescriptions p
        JOIN patients pt ON p.patient_id = pt.id
        JOIN medicines m ON p.medicine_id = m.id
        LEFT JOIN doctors d ON p.doctor_id = d.id
        ORDER BY p.id DESC
    """)
    prescriptions = cursor.fetchall()
    conn.close()
    return prescriptions

# ==============================================================================
# BILLING & INVOICING
# ==============================================================================
def get_all_invoices():
    """Retrieve all invoices with patient details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name AS patient_name, p.patient_uid, p.phone AS patient_phone
        FROM invoices i
        JOIN patients p ON i.patient_id = p.id
        ORDER BY i.id DESC
    """)
    invoices = cursor.fetchall()
    conn.close()
    return invoices

def get_invoice_by_id(invoice_id):
    """Get single invoice with full patient details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, p.name AS patient_name, p.patient_uid, p.age, p.gender, p.blood_group,
               p.phone AS patient_phone, p.email AS patient_email, p.address AS patient_address
        FROM invoices i
        JOIN patients p ON i.patient_id = p.id
        WHERE i.id = ?
    """, (invoice_id,))
    invoice = cursor.fetchone()
    conn.close()
    return invoice

def create_invoice(data):
    """Generate and calculate a comprehensive medical bill."""
    conn = get_db_connection()
    cursor = conn.cursor()
    uid = generate_uid("INV")

    doctor_fee = float(data.get("doctor_fee", 0.0) or 0.0)
    room_charges = float(data.get("room_charges", 0.0) or 0.0)
    medicine_charges = float(data.get("medicine_charges", 0.0) or 0.0)
    other_charges = float(data.get("other_charges", 0.0) or 0.0)
    discount = float(data.get("discount", 0.0) or 0.0)
    tax_percent = float(data.get("tax_percent", 5.0) or 0.0)

    subtotal = doctor_fee + room_charges + medicine_charges + other_charges - discount
    if subtotal < 0:
        subtotal = 0.0
    tax_amount = round(subtotal * (tax_percent / 100.0), 2)
    total_amount = round(subtotal + tax_amount, 2)

    today = date.today().isoformat()

    cursor.execute("""
        INSERT INTO invoices (invoice_uid, patient_id, doctor_fee, room_charges, medicine_charges, other_charges, discount, tax_amount, total_amount, payment_status, payment_method, invoice_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        uid,
        int(data.get("patient_id")),
        doctor_fee,
        room_charges,
        medicine_charges,
        other_charges,
        discount,
        tax_amount,
        total_amount,
        data.get("payment_status", "Unpaid"),
        data.get("payment_method", "Cash"),
        today,
        data.get("notes", "")
    ))
    conn.commit()
    inv_id = cursor.lastrowid
    conn.close()
    return inv_id

def update_invoice_payment(invoice_id, status, method):
    """Update payment status and method."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE invoices SET payment_status = ?, payment_method = ? WHERE id = ?
    """, (status, method, invoice_id))
    conn.commit()
    conn.close()

def delete_invoice(invoice_id):
    """Delete invoice record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    conn.commit()
    conn.close()
