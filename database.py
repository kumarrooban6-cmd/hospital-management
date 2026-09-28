import sqlite3
import os
from datetime import datetime, date, timedelta
import config

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "hospital.db")

class MySQLCursorWrapper:
    """Wrapper that adapts MySQL cursor to match SQLite cursor behavior (dictionary rows & %s translation)."""
    def __init__(self, raw_cursor):
        self._cursor = raw_cursor

    def execute(self, query, params=None):
        converted_query = query.replace("?", "%s")
        if params is not None:
            return self._cursor.execute(converted_query, params)
        return self._cursor.execute(converted_query)

    def executemany(self, query, params_list):
        converted_query = query.replace("?", "%s")
        return self._cursor.executemany(converted_query, params_list)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def description(self):
        return self._cursor.description

class MySQLConnectionWrapper:
    """Wrapper that adapts MySQL connection to return dictionary rows and handle PRAGMAs gracefully."""
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return MySQLCursorWrapper(self._conn.cursor(dictionary=True))

    def commit(self):
        return self._conn.commit()

    def close(self):
        return self._conn.close()

def get_db_connection():
    """Establish and return a database connection based on config.DB_ENGINE ('sqlite' or 'mysql')."""
    if getattr(config, "DB_ENGINE", "sqlite") == "mysql":
        try:
            import mysql.connector
            raw_conn = mysql.connector.connect(**config.MYSQL_CONFIG)
            return MySQLConnectionWrapper(raw_conn)
        except Exception as err:
            print(f"[Warning] Failed to connect to MySQL Server ({err}). Falling back to SQLite.")

    # Default: SQLite connection with Row factory
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_uid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        blood_group TEXT,
        phone TEXT NOT NULL,
        email TEXT,
        address TEXT,
        emergency_contact TEXT,
        medical_history TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Doctors Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_uid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        qualification TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        consultation_fee REAL NOT NULL DEFAULT 50.0,
        available_days TEXT NOT NULL,
        available_time TEXT NOT NULL,
        room_number TEXT NOT NULL,
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Appointments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_uid TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date TEXT NOT NULL,
        appointment_time TEXT NOT NULL,
        reason TEXT,
        diagnosis TEXT,
        status TEXT DEFAULT 'Scheduled',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    )
    """)

    # Hospital Beds / Wards Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS beds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_number TEXT UNIQUE NOT NULL,
        ward_type TEXT NOT NULL,
        charge_per_day REAL NOT NULL,
        status TEXT DEFAULT 'Available',
        description TEXT
    )
    """)

    # Bed Allocations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bed_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        admitted_at TEXT NOT NULL,
        discharged_at TEXT,
        status TEXT DEFAULT 'Admitted',
        notes TEXT,
        FOREIGN KEY (bed_id) REFERENCES beds(id) ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )
    """)

    # Medicines / Pharmacy Inventory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        dosage TEXT NOT NULL,
        stock_quantity INTEGER NOT NULL DEFAULT 0,
        unit_price REAL NOT NULL,
        expiry_date TEXT NOT NULL,
        manufacturer TEXT NOT NULL
    )
    """)

    # Prescriptions / Medicine Dispense Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER,
        medicine_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        dosage_instructions TEXT,
        total_price REAL NOT NULL,
        prescribed_date TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
        FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
    )
    """)

    # Invoices / Billing Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_uid TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        doctor_fee REAL DEFAULT 0.0,
        room_charges REAL DEFAULT 0.0,
        medicine_charges REAL DEFAULT 0.0,
        other_charges REAL DEFAULT 0.0,
        discount REAL DEFAULT 0.0,
        tax_amount REAL DEFAULT 0.0,
        total_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'Unpaid',
        payment_method TEXT DEFAULT 'Cash',
        invoice_date TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

def seed_db():
    """Populate database with realistic demo data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) as count FROM doctors")
    if cursor.fetchone()["count"] > 0:
        conn.close()
        return

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Sample Doctors
    doctors = [
        ("DOC-101", "Dr. Sarah Mitchell", "Cardiology", "MD, FACC", "+1 (555) 234-5678", "sarah.mitchell@hospital.com", 120.0, "Mon, Wed, Fri", "09:00 AM - 01:00 PM", "Room 301", "Active"),
        ("DOC-102", "Dr. Alexander Chen", "Neurology", "MBBS, DM (Neurology)", "+1 (555) 345-6789", "alex.chen@hospital.com", 140.0, "Tue, Thu, Sat", "10:00 AM - 02:00 PM", "Room 205", "Active"),
        ("DOC-103", "Dr. Emily Rodriguez", "Pediatrics", "MD (Pediatrics)", "+1 (555) 456-7890", "emily.rodriguez@hospital.com", 80.0, "Mon, Tue, Wed, Thu, Fri", "08:30 AM - 12:30 PM", "Room 108", "Active"),
        ("DOC-104", "Dr. Marcus Vance", "Orthopedics", "MS (Ortho), Fellowship Spine", "+1 (555) 567-8901", "marcus.vance@hospital.com", 110.0, "Mon, Wed, Thu", "01:00 PM - 05:00 PM", "Room 402", "Active"),
        ("DOC-105", "Dr. Priya Patel", "General Medicine", "MD (Internal Med)", "+1 (555) 678-9012", "priya.patel@hospital.com", 60.0, "Daily (Mon - Sat)", "09:00 AM - 04:00 PM", "Room 101", "Active"),
    ]
    cursor.executemany("""
        INSERT INTO doctors (doctor_uid, name, specialization, qualification, phone, email, consultation_fee, available_days, available_time, room_number, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, doctors)

    # Sample Patients
    patients = [
        ("PAT-1001", "James Anderson", 45, "Male", "O+", "+1 (555) 789-0123", "james.a@example.com", "742 Evergreen Terrace, Springfield", "Mary Anderson (+1 555-789-0124)", "Hypertension, Mild Asthma"),
        ("PAT-1002", "Sophia Martinez", 29, "Female", "A+", "+1 (555) 890-1234", "sophia.m@example.com", "108 Ocean Drive, Miami", "Carlos Martinez (+1 555-890-1235)", "No known allergies"),
        ("PAT-1003", "David Kim", 62, "Male", "B+", "+1 (555) 901-2345", "david.kim@example.com", "456 Maple Avenue, Seattle", "Grace Kim (+1 555-901-2346)", "Type 2 Diabetes, High Cholesterol"),
        ("PAT-1004", "Olivia Taylor", 8, "Female", "AB-", "+1 (555) 012-3456", "olivia.parents@example.com", "89 Oak Street, Austin", "Rachel Taylor (+1 555-012-3457)", "Penicillin Allergy"),
        ("PAT-1005", "Robert Miller", 54, "Male", "O-", "+1 (555) 123-4567", "robert.m@example.com", "23 Pine Lane, Denver", "Linda Miller (+1 555-123-4568)", "Previous knee surgery (2021)"),
    ]
    cursor.executemany("""
        INSERT INTO patients (patient_uid, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, patients)

    # Sample Beds
    beds = [
        ("ICU-01", "ICU", 350.0, "Occupied", "Intensive Care Unit - Bed 1 with ventilator support"),
        ("ICU-02", "ICU", 350.0, "Available", "Intensive Care Unit - Bed 2 with cardiac monitor"),
        ("GW-101", "General Ward", 75.0, "Occupied", "General Male Ward - Bed 101"),
        ("GW-102", "General Ward", 75.0, "Available", "General Male Ward - Bed 102"),
        ("GW-201", "General Ward", 75.0, "Available", "General Female Ward - Bed 201"),
        ("PVT-301", "Private Suite", 200.0, "Occupied", "Private Deluxe Room with attached restroom & AC"),
        ("PVT-302", "Private Suite", 200.0, "Available", "Private Deluxe Room - Room 302"),
        ("SP-401", "Semi-Private", 120.0, "Available", "Two-sharing Semi Private Ward - Bed A"),
        ("EMG-01", "Emergency", 150.0, "Available", "Emergency Triage Bay 1"),
    ]
    cursor.executemany("""
        INSERT INTO beds (bed_number, ward_type, charge_per_day, status, description)
        VALUES (?, ?, ?, ?, ?)
    """, beds)

    # Sample Bed Allocations (matching occupied beds)
    cursor.execute("""
        INSERT INTO bed_allocations (bed_id, patient_id, admitted_at, status, notes)
        VALUES 
        (1, 1, ?, 'Admitted', 'Admitted for acute cardiac monitoring and chest pain observation'),
        (3, 3, ?, 'Admitted', 'Admitted for diabetic ketoacidosis stabilization'),
        (6, 5, ?, 'Admitted', 'Post-operative recovery after orthopedic procedure')
    """, (yesterday, yesterday, today))

    # Sample Medicines
    medicines = [
        ("MED-101", "Amoxicillin 500mg", "Antibiotic", "Oral Capsule", 150, 12.50, "2027-10-15", "Pfizer"),
        ("MED-102", "Paracetamol 650mg", "Analgesic / Antipyretic", "Oral Tablet", 400, 4.00, "2028-04-20", "GSK"),
        ("MED-103", "Atorvastatin 20mg", "Cardiovascular", "Oral Tablet", 85, 18.00, "2027-08-30", "Novartis"),
        ("MED-104", "Metformin 500mg", "Antidiabetic", "Oral Tablet", 220, 8.50, "2027-12-01", "Sanofi"),
        ("MED-105", "Ibuprofen 400mg", "NSAID", "Oral Tablet", 12, 6.00, "2026-11-15", "Bayer"),  # Low stock
        ("MED-106", "Azithromycin 250mg", "Antibiotic", "Oral Tablet", 60, 22.00, "2027-06-18", "Teva"),
        ("MED-107", "Omeprazole 20mg", "Gastrointestinal", "Capsule", 180, 9.20, "2028-01-10", "AstraZeneca"),
        ("MED-108", "Cough Relief Syrup", "Respiratory", "100ml Bottle", 8, 14.50, "2026-12-31", "Johnson & Johnson") # Low stock
    ]
    cursor.executemany("""
        INSERT INTO medicines (medicine_code, name, category, dosage, stock_quantity, unit_price, expiry_date, manufacturer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, medicines)

    # Sample Appointments
    appointments = [
        ("APP-1001", 1, 1, today, "09:30 AM", "Routine Cardiac Follow-up & ECG Check", "Mild angina controlled with nitrates", "Completed"),
        ("APP-1002", 2, 3, today, "10:00 AM", "Seasonal Allergies and Cough", "Allergic rhinitis, prescribed antihistamine", "Completed"),
        ("APP-1003", 3, 5, today, "11:30 AM", "Blood Sugar Spikes & Fatigue", "Hyperglycemia review", "Scheduled"),
        ("APP-1004", 4, 3, tomorrow, "09:00 AM", "Annual Pediatric Wellness Exam", None, "Scheduled"),
        ("APP-1005", 5, 4, tomorrow, "02:00 PM", "Right Knee Joint Stiffness post therapy", None, "Scheduled"),
    ]
    cursor.executemany("""
        INSERT INTO appointments (appointment_uid, patient_id, doctor_id, appointment_date, appointment_time, reason, diagnosis, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, appointments)

    # Sample Prescriptions
    prescriptions = [
        (1, 1, 3, 30, "Take 1 tablet daily at bedtime", 540.0, yesterday),
        (2, 3, 2, 20, "Take 1 tablet every 6 hours as needed for fever", 80.0, today),
        (3, 5, 4, 60, "Take 1 tablet twice daily after meals", 510.0, yesterday),
    ]
    cursor.executemany("""
        INSERT INTO prescriptions (patient_id, doctor_id, medicine_id, quantity, dosage_instructions, total_price, prescribed_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, prescriptions)

    # Sample Invoices
    invoices = [
        ("INV-5001", 1, 120.0, 350.0, 540.0, 45.0, 50.0, 50.25, 1055.25, "Paid", "Credit Card", yesterday, "Comprehensive admission and cardiology diagnostics"),
        ("INV-5002", 2, 80.0, 0.0, 80.0, 20.0, 0.0, 9.00, 189.00, "Paid", "UPI", today, "Outpatient pediatric checkup and medicine"),
        ("INV-5003", 3, 60.0, 75.0, 510.0, 30.0, 25.0, 32.50, 682.50, "Pending", "Cash", today, "General ward admission and diabetes care package"),
    ]
    cursor.executemany("""
        INSERT INTO invoices (invoice_uid, patient_id, doctor_fee, room_charges, medicine_charges, other_charges, discount, tax_amount, total_amount, payment_status, payment_method, invoice_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, invoices)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_db()
    print("Database initialized and seeded successfully at:", DB_PATH)
