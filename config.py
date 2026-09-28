# Configuration Settings for MediCare Hospital Management System

# Database Selection: "sqlite" or "mysql"
DB_ENGINE = "sqlite"

# MySQL Workbench / Server Connection Credentials
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",                 # Your MySQL username (default: root)
    "password": "your_password",    # Your MySQL root password in Workbench
    "database": "hospital_db"       # The database created by schema_mysql.sql
}
