"""
Database Inspector Script for MediCare Hospital Management System
Run this script in terminal to view tables, schemas, and live records:
    python view_db.py
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hospital.db")

def format_row(values, widths):
    return " | ".join(str(val if val is not None else "").ljust(w) for val, w in zip(values, widths))

def view_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    cols_info = cursor.fetchall()
    col_names = [col[1] for col in cols_info]

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"\n[Table: '{table_name}' is currently empty]\n")
        return

    # Calculate column widths for nice terminal display
    widths = [len(col) for col in col_names]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], min(len(str(val if val is not None else "")), 30))

    header = format_row(col_names, widths)
    separator = "-+-".join("-" * w for w in widths)

    print(f"\n=== Table: {table_name} ({len(rows)} records) ===")
    print(header)
    print(separator)
    for row in rows:
        # Truncate long strings for cleaner terminal output
        truncated_row = [str(v)[:27] + "..." if len(str(v or "")) > 30 else v for v in row]
        print(format_row(truncated_row, widths))
    print("=" * len(header) + "\n")

def show_all_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [t[0] for t in cursor.fetchall()]

    print("\n" + "=" * 60)
    print("    DATABASE SUMMARY: hospital.db")
    print("=" * 60)
    print(f"{'Table Name':<25} | {'Row Count':<15}")
    print("-" * 25 + "-+-" + "-" * 15)

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:<25} | {count:<15}")
    print("=" * 60 + "\n")
    conn.close()
    return tables

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        sys.exit(1)

    tables = show_all_tables()

    if len(sys.argv) > 1:
        tbl = sys.argv[1]
        if tbl in tables:
            view_table(tbl)
        else:
            print(f"Table '{tbl}' does not exist.")
    else:
        print("Viewing all tables:\n")
        for tbl in tables:
            view_table(tbl)
