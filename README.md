# MediCare Hospital Management System (HMS)

A full-featured, modular **Hospital Management Web Application** developed in **Python** using the **Flask** web framework and **SQLite**. Designed for hospitals, clinics, and health centers to streamline patient records, staff management, appointment scheduling, ward occupancy, pharmacy inventory, and medical billing.

---

## 🚀 Key Modules & Features

### 1. 📊 Executive Dashboard
- **Real-Time KPIs**: Total registered patients, active doctors on duty, today's appointments, inpatient bed occupancy rates, low-stock pharmacy warnings, and revenue metrics.
- **Live Schedules & Invoices**: Direct view of current consultations and recent invoices.
- **One-Click Quick Operations**: Immediate links to register patients, add doctors, allocate beds, dispense meds, and create invoices.

### 2. 👥 Patient Management (EHR)
- **Patient Registration**: Capture full demographics, age, gender, blood group, contact numbers, email, residential address, emergency contact person, and clinical allergies.
- **Comprehensive Patient Profile**: Dedicated 360° health record displaying:
  - Appointment and consultation history.
  - Inpatient bed admissions and stay durations.
  - Pharmacy prescriptions dispensed.
  - Financial invoices and payment receipts.
- **Search & Filter**: Search patients by Name, Phone Number, Unique Patient ID (UID), or Blood Group.

### 3. 🩺 Medical Staff & Doctors Roster
- **Physician Profiles**: Track specialization, qualifications, consulting fees, room/OPD number, available days, and time slots.
- **Staff Status Management**: Active, On Leave, or Inactive status tags.
- Direct booking link for each doctor.

### 4. 📅 Appointment Scheduling
- **Consultation Booking**: Connect patients with specialized doctors on specific dates and time slots.
- **Clinical Lifecycle**: Status progression (`Scheduled`, `Completed`, `Cancelled`).
- **Doctor Findings & Diagnosis**: Record physician observations and remarks per session.

### 5. 🛏️ Inpatient Wards & Bed Allocation (IPD)
- **Ward Matrix**: Categorized rooms including **ICU**, **General Ward**, **Private Suite**, **Semi-Private**, and **Emergency**.
- **Real-Time Bed Status**: Visual occupancy badges (Vacant / Occupied).
- **Admission & Discharge**: Easily allocate beds to patients and process discharges with automatic status toggles.

### 6. 💊 Pharmacy & Medicine Inventory
- **Stock Management**: Track pharmaceutical items, dosage forms, batch expiry dates, unit prices, and manufacturers.
- **Automatic Stock Alerts**: Low-stock indicator badges when items drop below threshold.
- **Medicine Dispensing**: Dispense prescribed medications to patients with automatic inventory deduction.
- **Prescription Log**: Detailed audit log of all issued medications.

### 7. 🧾 Billing, Accounts & Printable Invoices
- **Itemized Billing**: Doctor fees, room/bed tariffs, medication costs, diagnostic services, discounts, and taxes.
- **Live Fee Calculator**: Interactive JavaScript calculator that updates subtotals and grand totals in real-time.
- **Payment Processing**: Track status (`Paid`, `Pending`, `Unpaid`) and modes (`Cash`, `Card`, `UPI`, `Insurance`).
- **Printable Medical Receipt**: Clean, professional invoice template with print stylesheet for instant thermal/A4 printing and PDF export.

---

## 📁 Project Structure

```
hospital_management_system/
├── app.py                     # Main Flask application and URL routes
├── database.py                # Database connection, schemas, initialization, and seed data
├── models.py                  # Data access layer and business logic
├── run.py                     # Convenience launcher script (opens browser automatically)
├── requirements.txt           # Python dependencies (Flask)
├── hospital.db                # SQLite database (auto-generated)
├── static/
│   └── css/
│       └── style.css          # Custom styling and print styles
└── templates/
    ├── base.html              # Base layout with sidebar, navbar, and clock
    ├── dashboard.html         # Executive overview dashboard
    ├── patients/
    │   ├── list.html          # Patient search and directory
    │   ├── form.html          # Patient add/edit form
    │   └── view.html          # 360° Electronic Health Record profile
    ├── doctors/
    │   ├── list.html          # Staff directory
    │   └── form.html          # Add/edit doctor form
    ├── appointments/
    │   ├── list.html          # Appointment schedule with status modals
    │   └── form.html          # Book appointment form
    ├── beds/
    │   └── list.html          # Ward matrix, admission, and discharge
    ├── pharmacy/
    │   ├── list.html          # Medicine stock and prescription log
    │   └── form.html          # Add/edit medicine form
    └── billing/
        ├── list.html          # Billing registry
        ├── form.html          # Invoice creator with live calculator
        └── invoice.html       # Printable receipt
```

---

## 🛠️ How to Run

### Step 1: Open Terminal in the Project Directory
```powershell
cd "C:\Users\Roobarajan\.gemini\antigravity\scratch\hospital_management_system"
```

### Step 2: Ensure Dependencies Are Installed
```bash
pip install -r requirements.txt
```

### Step 3: Start the Application
Run the launcher script:
```bash
python run.py
```
*(Or alternatively: `python app.py`)*

### Step 4: Open in Web Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
*(The `run.py` script automatically attempts to open this in your default browser).*

---

## 🗄️ Database Architecture
The application uses SQLite (`hospital.db`) which requires zero configuration. On first run, the database is automatically created and populated with sample doctors, patients, beds, medicines, appointments, and bills.
