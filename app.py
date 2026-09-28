import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import models

app = Flask(__name__)
app.secret_key = "hospital_management_secret_key_2026"

# Ensure database tables exist and sample data is seeded on startup
database.init_db()
database.seed_db()

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

# ==============================================================================
# DASHBOARD
# ==============================================================================
@app.route("/dashboard")
def dashboard():
    stats = models.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)

# ==============================================================================
# PATIENTS
# ==============================================================================
@app.route("/patients")
def patient_list():
    query = request.args.get("q", "").strip()
    patients = models.get_all_patients(query if query else None)
    return render_template("patients/list.html", patients=patients, query=query)

@app.route("/patients/add", methods=["GET", "POST"])
def patient_add():
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "blood_group": request.form.get("blood_group"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address"),
            "emergency_contact": request.form.get("emergency_contact"),
            "medical_history": request.form.get("medical_history")
        }
        if not data["name"] or not data["phone"]:
            flash("Patient name and phone number are required.", "danger")
            return render_template("patients/form.html", patient=data, action="Add")
        
        patient_id = models.create_patient(data)
        flash("Patient registered successfully!", "success")
        return redirect(url_for("patient_view", patient_id=patient_id))
    
    return render_template("patients/form.html", patient=None, action="Add")

@app.route("/patients/<int:patient_id>")
def patient_view(patient_id):
    record = models.get_patient_complete_record(patient_id)
    if not record:
        flash("Patient not found.", "warning")
        return redirect(url_for("patient_list"))
    return render_template("patients/view.html", record=record)

@app.route("/patients/edit/<int:patient_id>", methods=["GET", "POST"])
def patient_edit(patient_id):
    patient = models.get_patient_by_id(patient_id)
    if not patient:
        flash("Patient not found.", "warning")
        return redirect(url_for("patient_list"))
    
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender"),
            "blood_group": request.form.get("blood_group"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address"),
            "emergency_contact": request.form.get("emergency_contact"),
            "medical_history": request.form.get("medical_history")
        }
        models.update_patient(patient_id, data)
        flash("Patient profile updated successfully!", "success")
        return redirect(url_for("patient_view", patient_id=patient_id))
    
    return render_template("patients/form.html", patient=patient, action="Edit")

@app.route("/patients/delete/<int:patient_id>", methods=["POST"])
def patient_delete(patient_id):
    models.delete_patient(patient_id)
    flash("Patient record deleted successfully.", "info")
    return redirect(url_for("patient_list"))

# ==============================================================================
# DOCTORS
# ==============================================================================
@app.route("/doctors")
def doctor_list():
    query = request.args.get("q", "").strip()
    doctors = models.get_all_doctors(query if query else None)
    return render_template("doctors/list.html", doctors=doctors, query=query)

@app.route("/doctors/add", methods=["GET", "POST"])
def doctor_add():
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "specialization": request.form.get("specialization"),
            "qualification": request.form.get("qualification"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "consultation_fee": request.form.get("consultation_fee"),
            "available_days": request.form.get("available_days"),
            "available_time": request.form.get("available_time"),
            "room_number": request.form.get("room_number"),
            "status": request.form.get("status", "Active")
        }
        if not data["name"] or not data["specialization"]:
            flash("Doctor name and specialization are required.", "danger")
            return render_template("doctors/form.html", doctor=data, action="Add")
        
        models.create_doctor(data)
        flash("Doctor added to staff roster!", "success")
        return redirect(url_for("doctor_list"))
    
    return render_template("doctors/form.html", doctor=None, action="Add")

@app.route("/doctors/edit/<int:doctor_id>", methods=["GET", "POST"])
def doctor_edit(doctor_id):
    doctor = models.get_doctor_by_id(doctor_id)
    if not doctor:
        flash("Doctor not found.", "warning")
        return redirect(url_for("doctor_list"))
    
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "specialization": request.form.get("specialization"),
            "qualification": request.form.get("qualification"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "consultation_fee": request.form.get("consultation_fee"),
            "available_days": request.form.get("available_days"),
            "available_time": request.form.get("available_time"),
            "room_number": request.form.get("room_number"),
            "status": request.form.get("status")
        }
        models.update_doctor(doctor_id, data)
        flash("Doctor details updated successfully!", "success")
        return redirect(url_for("doctor_list"))
    
    return render_template("doctors/form.html", doctor=doctor, action="Edit")

@app.route("/doctors/delete/<int:doctor_id>", methods=["POST"])
def doctor_delete(doctor_id):
    models.delete_doctor(doctor_id)
    flash("Doctor removed from staff roster.", "info")
    return redirect(url_for("doctor_list"))

# ==============================================================================
# APPOINTMENTS
# ==============================================================================
@app.route("/appointments")
def appointment_list():
    date_filter = request.args.get("date", "").strip()
    status_filter = request.args.get("status", "All").strip()
    appointments = models.get_all_appointments(date_filter if date_filter else None, status_filter)
    return render_template("appointments/list.html", appointments=appointments, date_filter=date_filter, status_filter=status_filter)

@app.route("/appointments/book", methods=["GET", "POST"])
def appointment_book():
    if request.method == "POST":
        data = {
            "patient_id": request.form.get("patient_id"),
            "doctor_id": request.form.get("doctor_id"),
            "appointment_date": request.form.get("appointment_date"),
            "appointment_time": request.form.get("appointment_time"),
            "reason": request.form.get("reason")
        }
        if not data["patient_id"] or not data["doctor_id"] or not data["appointment_date"] or not data["appointment_time"]:
            flash("All appointment fields are mandatory.", "danger")
            return redirect(url_for("appointment_book"))
        
        models.create_appointment(data)
        flash("Appointment scheduled successfully!", "success")
        return redirect(url_for("appointment_list"))

    patients = models.get_all_patients()
    doctors = models.get_all_doctors()
    preselected_patient = request.args.get("patient_id")
    return render_template("appointments/form.html", patients=patients, doctors=doctors, preselected_patient=preselected_patient)

@app.route("/appointments/status/<int:appointment_id>", methods=["POST"])
def appointment_update_status(appointment_id):
    status = request.form.get("status")
    diagnosis = request.form.get("diagnosis")
    models.update_appointment_status(appointment_id, status, diagnosis)
    flash(f"Appointment status updated to '{status}'.", "success")
    return redirect(request.referrer or url_for("appointment_list"))

@app.route("/appointments/delete/<int:appointment_id>", methods=["POST"])
def appointment_delete(appointment_id):
    models.delete_appointment(appointment_id)
    flash("Appointment cancelled and removed.", "info")
    return redirect(url_for("appointment_list"))

# ==============================================================================
# BED / INPATIENT (IPD) MANAGEMENT
# ==============================================================================
@app.route("/beds")
def bed_list():
    beds = models.get_all_beds()
    patients = models.get_all_patients()
    available_beds = [b for b in beds if b["status"] == "Available"]
    occupied_beds = [b for b in beds if b["status"] == "Occupied"]
    return render_template("beds/list.html", beds=beds, available_beds=available_beds, occupied_beds=occupied_beds, patients=patients)

@app.route("/beds/allocate", methods=["POST"])
def bed_allocate():
    bed_id = request.form.get("bed_id")
    patient_id = request.form.get("patient_id")
    notes = request.form.get("notes", "")

    if not bed_id or not patient_id:
        flash("Please select both a bed and a patient.", "danger")
        return redirect(url_for("bed_list"))

    models.allocate_bed(bed_id, patient_id, notes)
    flash("Patient admitted and bed allocated successfully!", "success")
    return redirect(url_for("bed_list"))

@app.route("/beds/discharge/<int:allocation_id>", methods=["POST"])
def bed_discharge(allocation_id):
    models.discharge_bed(allocation_id)
    flash("Patient discharged and bed is now marked Available.", "success")
    return redirect(url_for("bed_list"))

# ==============================================================================
# PHARMACY & MEDICINE INVENTORY
# ==============================================================================
@app.route("/pharmacy")
def pharmacy_list():
    query = request.args.get("q", "").strip()
    medicines = models.get_all_medicines(query if query else None)
    prescriptions = models.get_prescriptions_list()
    patients = models.get_all_patients()
    doctors = models.get_all_doctors()
    return render_template("pharmacy/list.html", medicines=medicines, prescriptions=prescriptions, patients=patients, doctors=doctors, query=query)

@app.route("/pharmacy/add", methods=["GET", "POST"])
def pharmacy_add():
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "category": request.form.get("category"),
            "dosage": request.form.get("dosage"),
            "stock_quantity": request.form.get("stock_quantity"),
            "unit_price": request.form.get("unit_price"),
            "expiry_date": request.form.get("expiry_date"),
            "manufacturer": request.form.get("manufacturer")
        }
        if not data["name"] or not data["unit_price"]:
            flash("Medicine name and unit price are required.", "danger")
            return render_template("pharmacy/form.html", medicine=data, action="Add")

        models.create_medicine(data)
        flash("New medicine added to pharmacy inventory!", "success")
        return redirect(url_for("pharmacy_list"))

    return render_template("pharmacy/form.html", medicine=None, action="Add")

@app.route("/pharmacy/edit/<int:medicine_id>", methods=["GET", "POST"])
def pharmacy_edit(medicine_id):
    med = models.get_medicine_by_id(medicine_id)
    if not med:
        flash("Medicine not found.", "warning")
        return redirect(url_for("pharmacy_list"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "category": request.form.get("category"),
            "dosage": request.form.get("dosage"),
            "stock_quantity": request.form.get("stock_quantity"),
            "unit_price": request.form.get("unit_price"),
            "expiry_date": request.form.get("expiry_date"),
            "manufacturer": request.form.get("manufacturer")
        }
        models.update_medicine(medicine_id, data)
        flash("Medicine inventory updated successfully!", "success")
        return redirect(url_for("pharmacy_list"))

    return render_template("pharmacy/form.html", medicine=med, action="Edit")

@app.route("/pharmacy/dispense", methods=["POST"])
def pharmacy_dispense():
    patient_id = request.form.get("patient_id")
    medicine_id = request.form.get("medicine_id")
    doctor_id = request.form.get("doctor_id") or None
    quantity = int(request.form.get("quantity", 1))
    dosage_instructions = request.form.get("dosage_instructions", "")

    success, message = models.dispense_medicine(patient_id, medicine_id, doctor_id, quantity, dosage_instructions)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for("pharmacy_list"))

@app.route("/pharmacy/delete/<int:medicine_id>", methods=["POST"])
def pharmacy_delete(medicine_id):
    models.delete_medicine(medicine_id)
    flash("Medicine removed from inventory.", "info")
    return redirect(url_for("pharmacy_list"))

# ==============================================================================
# BILLING & INVOICING
# ==============================================================================
@app.route("/billing")
def billing_list():
    invoices = models.get_all_invoices()
    return render_template("billing/list.html", invoices=invoices)

@app.route("/billing/create", methods=["GET", "POST"])
def billing_create():
    if request.method == "POST":
        data = {
            "patient_id": request.form.get("patient_id"),
            "doctor_fee": request.form.get("doctor_fee"),
            "room_charges": request.form.get("room_charges"),
            "medicine_charges": request.form.get("medicine_charges"),
            "other_charges": request.form.get("other_charges"),
            "discount": request.form.get("discount"),
            "tax_percent": request.form.get("tax_percent"),
            "payment_status": request.form.get("payment_status"),
            "payment_method": request.form.get("payment_method"),
            "notes": request.form.get("notes")
        }
        if not data["patient_id"]:
            flash("Patient selection is required for invoice creation.", "danger")
            return redirect(url_for("billing_create"))

        inv_id = models.create_invoice(data)
        flash("Invoice generated successfully!", "success")
        return redirect(url_for("billing_invoice", invoice_id=inv_id))

    patients = models.get_all_patients()
    preselected_patient = request.args.get("patient_id")
    return render_template("billing/form.html", patients=patients, preselected_patient=preselected_patient)

@app.route("/billing/invoice/<int:invoice_id>")
def billing_invoice(invoice_id):
    invoice = models.get_invoice_by_id(invoice_id)
    if not invoice:
        flash("Invoice not found.", "warning")
        return redirect(url_for("billing_list"))
    return render_template("billing/invoice.html", invoice=invoice)

@app.route("/billing/payment/<int:invoice_id>", methods=["POST"])
def billing_update_payment(invoice_id):
    status = request.form.get("payment_status")
    method = request.form.get("payment_method")
    models.update_invoice_payment(invoice_id, status, method)
    flash("Payment details updated successfully!", "success")
    return redirect(url_for("billing_invoice", invoice_id=invoice_id))

@app.route("/billing/delete/<int:invoice_id>", methods=["POST"])
def billing_delete(invoice_id):
    models.delete_invoice(invoice_id)
    flash("Invoice deleted.", "info")
    return redirect(url_for("billing_list"))

# ==============================================================================
# DATABASE EXPLORER
# ==============================================================================
@app.route("/db-explorer", methods=["GET", "POST"])
def db_explorer():
    conn = database.get_db_connection()
    cursor = conn.cursor()

    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    raw_tables = [row["name"] for row in cursor.fetchall()]

    tables = []
    for t in raw_tables:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {t}")
        tables.append({"name": t, "count": cursor.fetchone()["count"]})

    selected_table = request.args.get("table", raw_tables[0] if raw_tables else "")
    custom_sql = request.form.get("custom_sql", "").strip() if request.method == "POST" else None
    query_error = None
    rows = []
    columns = []

    if custom_sql:
        # Simple safety check: allow only SELECT queries
        if not custom_sql.strip().upper().startswith("SELECT"):
            query_error = "Only SELECT statements are allowed in this viewer for security."
        else:
            try:
                cursor.execute(custom_sql)
                rows = cursor.fetchall()
                if rows:
                    columns = rows[0].keys()
                elif cursor.description:
                    columns = [d[0] for d in cursor.description]
            except Exception as e:
                query_error = str(e)
    elif selected_table:
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns = [col["name"] for col in cursor.fetchall()]
        cursor.execute(f"SELECT * FROM {selected_table} ORDER BY id DESC")
        rows = cursor.fetchall()

    conn.close()
    return render_template(
        "database/explorer.html",
        tables=tables,
        selected_table=selected_table,
        columns=columns,
        rows=rows,
        current_query=custom_sql,
        query_error=query_error
    )

if __name__ == "__main__":
    print("Starting Hospital Management System Web Server...")
    print("Access the portal at http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
