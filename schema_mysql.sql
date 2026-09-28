-- ==============================================================================
-- MediCare Hospital Management System (HMS)
-- MySQL Workbench Complete Database Script
-- ==============================================================================

-- 1. Create and Select Database
CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- 2. Drop existing tables in reverse order of dependencies (if re-running)
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS bed_allocations;
DROP TABLE IF EXISTS beds;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS patients;

-- ==============================================================================
-- 3. Table Definitions
-- ==============================================================================

-- Patients Table
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_uid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(20) NOT NULL,
    blood_group VARCHAR(10),
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    address VARCHAR(255),
    emergency_contact VARCHAR(100),
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Doctors Table
CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_uid VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(100) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    consultation_fee DECIMAL(10,2) NOT NULL DEFAULT 50.00,
    available_days VARCHAR(100) NOT NULL,
    available_time VARCHAR(100) NOT NULL,
    room_number VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Appointments Table
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_uid VARCHAR(50) UNIQUE NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date VARCHAR(20) NOT NULL,
    appointment_time VARCHAR(20) NOT NULL,
    reason TEXT,
    diagnosis TEXT,
    status VARCHAR(50) DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Beds Table
CREATE TABLE beds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bed_number VARCHAR(50) UNIQUE NOT NULL,
    ward_type VARCHAR(100) NOT NULL,
    charge_per_day DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Available',
    description VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Bed Allocations Table
CREATE TABLE bed_allocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bed_id INT NOT NULL,
    patient_id INT NOT NULL,
    admitted_at VARCHAR(20) NOT NULL,
    discharged_at VARCHAR(20),
    status VARCHAR(50) DEFAULT 'Admitted',
    notes TEXT,
    FOREIGN KEY (bed_id) REFERENCES beds(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Medicines Inventory Table
CREATE TABLE medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL,
    expiry_date VARCHAR(20) NOT NULL,
    manufacturer VARCHAR(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Prescriptions Table
CREATE TABLE prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT,
    medicine_id INT NOT NULL,
    quantity INT NOT NULL,
    dosage_instructions TEXT,
    total_price DECIMAL(10,2) NOT NULL,
    prescribed_date VARCHAR(20) NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Invoices Table
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_uid VARCHAR(50) UNIQUE NOT NULL,
    patient_id INT NOT NULL,
    doctor_fee DECIMAL(10,2) DEFAULT 0.00,
    room_charges DECIMAL(10,2) DEFAULT 0.00,
    medicine_charges DECIMAL(10,2) DEFAULT 0.00,
    other_charges DECIMAL(10,2) DEFAULT 0.00,
    discount DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(50) DEFAULT 'Unpaid',
    payment_method VARCHAR(50) DEFAULT 'Cash',
    invoice_date VARCHAR(20) NOT NULL,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================================================================
-- 4. Initial Sample Data Insertion
-- ==============================================================================

-- Insert Doctors
INSERT INTO doctors (doctor_uid, name, specialization, qualification, phone, email, consultation_fee, available_days, available_time, room_number, status)
VALUES 
('DOC-101', 'Dr. Sarah Mitchell', 'Cardiology', 'MD, FACC', '+1 (555) 234-5678', 'sarah.mitchell@hospital.com', 120.00, 'Mon, Wed, Fri', '09:00 AM - 01:00 PM', 'Room 301', 'Active'),
('DOC-102', 'Dr. Alexander Chen', 'Neurology', 'MBBS, DM (Neurology)', '+1 (555) 345-6789', 'alex.chen@hospital.com', 140.00, 'Tue, Thu, Sat', '10:00 AM - 02:00 PM', 'Room 205', 'Active'),
('DOC-103', 'Dr. Emily Rodriguez', 'Pediatrics', 'MD (Pediatrics)', '+1 (555) 456-7890', 'emily.rodriguez@hospital.com', 80.00, 'Mon, Tue, Wed, Thu, Fri', '08:30 AM - 12:30 PM', 'Room 108', 'Active'),
('DOC-104', 'Dr. Marcus Vance', 'Orthopedics', 'MS (Ortho), Fellowship Spine', '+1 (555) 567-8901', 'marcus.vance@hospital.com', 110.00, 'Mon, Wed, Thu', '01:00 PM - 05:00 PM', 'Room 402', 'Active'),
('DOC-105', 'Dr. Priya Patel', 'General Medicine', 'MD (Internal Med)', '+1 (555) 678-9012', 'priya.patel@hospital.com', 60.00, 'Daily (Mon - Sat)', '09:00 AM - 04:00 PM', 'Room 101', 'Active');

-- Insert Patients
INSERT INTO patients (patient_uid, name, age, gender, blood_group, phone, email, address, emergency_contact, medical_history)
VALUES
('PAT-1001', 'James Anderson', 45, 'Male', 'O+', '+1 (555) 789-0123', 'james.a@example.com', '742 Evergreen Terrace, Springfield', 'Mary Anderson (+1 555-789-0124)', 'Hypertension, Mild Asthma'),
('PAT-1002', 'Sophia Martinez', 29, 'Female', 'A+', '+1 (555) 890-1234', 'sophia.m@example.com', '108 Ocean Drive, Miami', 'Carlos Martinez (+1 555-890-1235)', 'No known allergies'),
('PAT-1003', 'David Kim', 62, 'Male', 'B+', '+1 (555) 901-2345', 'david.kim@example.com', '456 Maple Avenue, Seattle', 'Grace Kim (+1 555-901-2346)', 'Type 2 Diabetes, High Cholesterol'),
('PAT-1004', 'Olivia Taylor', 8, 'Female', 'AB-', '+1 (555) 012-3456', 'olivia.parents@example.com', '89 Oak Street, Austin', 'Rachel Taylor (+1 555-012-3457)', 'Penicillin Allergy'),
('PAT-1005', 'Robert Miller', 54, 'Male', 'O-', '+1 (555) 123-4567', 'robert.m@example.com', '23 Pine Lane, Denver', 'Linda Miller (+1 555-123-4568)', 'Previous knee surgery (2021)');

-- Insert Beds
INSERT INTO beds (bed_number, ward_type, charge_per_day, status, description)
VALUES
('ICU-01', 'ICU', 350.00, 'Occupied', 'Intensive Care Unit - Bed 1 with ventilator support'),
('ICU-02', 'ICU', 350.00, 'Available', 'Intensive Care Unit - Bed 2 with cardiac monitor'),
('GW-101', 'General Ward', 75.00, 'Occupied', 'General Male Ward - Bed 101'),
('GW-102', 'General Ward', 75.00, 'Available', 'General Male Ward - Bed 102'),
('GW-201', 'General Ward', 75.00, 'Available', 'General Female Ward - Bed 201'),
('PVT-301', 'Private Suite', 200.00, 'Occupied', 'Private Deluxe Room with attached restroom & AC'),
('PVT-302', 'Private Suite', 200.00, 'Available', 'Private Deluxe Room - Room 302'),
('SP-401', 'Semi-Private', 120.00, 'Available', 'Two-sharing Semi Private Ward - Bed A'),
('EMG-01', 'Emergency', 150.00, 'Available', 'Emergency Triage Bay 1');

-- Insert Bed Allocations
INSERT INTO bed_allocations (bed_id, patient_id, admitted_at, status, notes)
VALUES
(1, 1, CURDATE(), 'Admitted', 'Admitted for acute cardiac monitoring and chest pain observation'),
(3, 3, CURDATE(), 'Admitted', 'Admitted for diabetic ketoacidosis stabilization'),
(6, 5, CURDATE(), 'Admitted', 'Post-operative recovery after orthopedic procedure');

-- Insert Medicines
INSERT INTO medicines (medicine_code, name, category, dosage, stock_quantity, unit_price, expiry_date, manufacturer)
VALUES
('MED-101', 'Amoxicillin 500mg', 'Antibiotic', 'Oral Capsule', 150, 12.50, '2027-10-15', 'Pfizer'),
('MED-102', 'Paracetamol 650mg', 'Analgesic / Antipyretic', 'Oral Tablet', 400, 4.00, '2028-04-20', 'GSK'),
('MED-103', 'Atorvastatin 20mg', 'Cardiovascular', 'Oral Tablet', 85, 18.00, '2027-08-30', 'Novartis'),
('MED-104', 'Metformin 500mg', 'Antidiabetic', 'Oral Tablet', 220, 8.50, '2027-12-01', 'Sanofi'),
('MED-105', 'Ibuprofen 400mg', 'NSAID', 'Oral Tablet', 12, 6.00, '2026-11-15', 'Bayer'),
('MED-106', 'Azithromycin 250mg', 'Antibiotic', 'Oral Tablet', 60, 22.00, '2027-06-18', 'Teva'),
('MED-107', 'Omeprazole 20mg', 'Gastrointestinal', 'Capsule', 180, 9.20, '2028-01-10', 'AstraZeneca'),
('MED-108', 'Cough Relief Syrup', 'Respiratory', '100ml Bottle', 8, 14.50, '2026-12-31', 'Johnson & Johnson');

-- Insert Appointments
INSERT INTO appointments (appointment_uid, patient_id, doctor_id, appointment_date, appointment_time, reason, diagnosis, status)
VALUES
('APP-1001', 1, 1, CURDATE(), '09:30 AM', 'Routine Cardiac Follow-up & ECG Check', 'Mild angina controlled with nitrates', 'Completed'),
('APP-1002', 2, 3, CURDATE(), '10:00 AM', 'Seasonal Allergies and Cough', 'Allergic rhinitis, prescribed antihistamine', 'Completed'),
('APP-1003', 3, 5, CURDATE(), '11:30 AM', 'Blood Sugar Spikes & Fatigue', 'Hyperglycemia review', 'Scheduled'),
('APP-1004', 4, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00 AM', 'Annual Pediatric Wellness Exam', NULL, 'Scheduled'),
('APP-1005', 5, 4, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '02:00 PM', 'Right Knee Joint Stiffness post therapy', NULL, 'Scheduled');

-- Insert Prescriptions
INSERT INTO prescriptions (patient_id, doctor_id, medicine_id, quantity, dosage_instructions, total_price, prescribed_date)
VALUES
(1, 1, 3, 30, 'Take 1 tablet daily at bedtime', 540.00, CURDATE()),
(2, 3, 2, 20, 'Take 1 tablet every 6 hours as needed for fever', 80.00, CURDATE()),
(3, 5, 4, 60, 'Take 1 tablet twice daily after meals', 510.00, CURDATE());

-- Insert Invoices
INSERT INTO invoices (invoice_uid, patient_id, doctor_fee, room_charges, medicine_charges, other_charges, discount, tax_amount, total_amount, payment_status, payment_method, invoice_date, notes)
VALUES
('INV-5001', 1, 120.00, 350.00, 540.00, 45.00, 50.00, 50.25, 1055.25, 'Paid', 'Credit Card', CURDATE(), 'Comprehensive admission and cardiology diagnostics'),
('INV-5002', 2, 80.00, 0.00, 80.00, 20.00, 0.00, 9.00, 189.00, 'Paid', 'UPI', CURDATE(), 'Outpatient pediatric checkup and medicine'),
('INV-5003', 3, 60.00, 75.00, 510.00, 30.00, 25.00, 32.50, 682.50, 'Pending', 'Cash', CURDATE(), 'General ward admission and diabetes care package');

-- Confirm Creation
SELECT 'Database and tables created successfully!' AS Status;
SELECT TABLE_NAME, TABLE_ROWS FROM information_schema.tables WHERE TABLE_SCHEMA = 'hospital_db';
