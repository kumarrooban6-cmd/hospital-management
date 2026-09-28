import os
import sys
import webbrowser
import threading
import time
from app import app

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("=" * 65)
    print("  MediCare Hospital Management System (HMS) - Web Application")
    print("=" * 65)
    print("  * System URL: http://127.0.0.1:5000")
    print("  * Database:   hospital.db (SQLite)")
    print("  * Modules:    Patients, Doctors, Appointments, Wards/Beds,")
    print("                Pharmacy Inventory, Invoices & Medical Receipts")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server.")
    print("=" * 65)

    # Automatically open default web browser
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host="127.0.0.1", port=5000, debug=False)
