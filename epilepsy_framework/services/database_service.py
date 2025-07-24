"""
Database service for the Epilepsy Public Health Informatics Framework
"""
import sqlite3
from sqlite3 import Error
from models.patient import Patient
from models.treatment import TreatmentPlan
from config.config import config
import logging

logging.basicConfig(level=logging.INFO)

class DatabaseService:
    """Service for handling database operations"""
    def __init__(self):
        """Initialize the database service"""
        self.database_path = config.get_db_path()
        self.connection = None

    def create_connection(self):
        """Create a database connection"""
        try:
            self.connection = sqlite3.connect(self.database_path)
            logging.info(f"Connected to SQLite database at {self.database_path}")
        except Error as e:
            logging.error(f"Error connecting to database: {e}")
            return None
        return self.connection

    def create_patient_table(self):
        """Create the patient table"""
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            gender TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            phone_number TEXT,
            email TEXT,
            insurance_provider TEXT,
            insurance_id TEXT
        )
        '''
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            logging.info("Patient table created or already exists.")
        except Error as e:
            logging.error(f"Error creating patient table: {e}")

    def create_treatment_table(self):
        """Create the treatment plan table"""
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS treatments (
            plan_id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            plan_date DATE,
            treating_physician TEXT,
            treatment_goals TEXT,
            current_medications TEXT,
            planned_medications TEXT,
            non_pharmacological_treatments TEXT,
            lifestyle_modifications TEXT,
            monitoring_plan TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
        '''
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            logging.info("Treatment table created or already exists.")
        except Error as e:
            logging.error(f"Error creating treatment table: {e}")

    def close_connection(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            logging.info("SQLite connection closed.")

# Global instance of the database service
db_service = DatabaseService()
db_service.create_connection()
db_service.create_patient_table()
db_service.create_treatment_table()
db_service.close_connection()
