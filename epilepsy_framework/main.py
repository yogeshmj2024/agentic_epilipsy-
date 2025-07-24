"""
Main application interface for the Epilepsy Public Health Informatics Framework
"""
import sys
import json
from flask import Flask, request, jsonify
from datetime import datetime, date
from typing import Optional, List, Dict
import logging
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from models.patient import Patient, PatientDemographics, EpilepsyDiagnosis, SeizureEvent
from models.patient import Gender, EpilepsyType, SeizureType, SeverityLevel
from models.treatment import TreatmentPlan, TreatmentOutcome, MedicationPrescription
from utils.analytics import EpilepsyAnalytics
from services.database_service import DatabaseService
from config.config import config

class EpilepsyFramework:
    """Main application class for the Epilepsy Public Health Informatics Framework"""
    
    def __init__(self):
        """Initialize the framework"""
        self.logger = logging.getLogger(__name__)
        self.db_service = DatabaseService()
        self.analytics = EpilepsyAnalytics()
        self.patients = {}  # In-memory storage for this demo
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.logging.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.logger.info("Epilepsy Public Health Informatics Framework initialized")
    
    def create_patient(self, 
                      first_name: str, 
                      last_name: str, 
                      date_of_birth: date, 
                      gender: str = None,
                      **kwargs) -> Patient:
        """
        Create a new patient record
        
        Args:
            first_name: Patient's first name
            last_name: Patient's last name
            date_of_birth: Date of birth
            gender: Patient's gender
            **kwargs: Additional demographic information
            
        Returns:
            Patient object
        """
        # Create demographics
        demographics = PatientDemographics(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=Gender(gender) if gender else None,
            **kwargs
        )
        
        # Create patient
        patient = Patient(demographics=demographics)
        
        # Store in memory
        self.patients[patient.patient_id] = patient
        
        self.logger.info(f"Created patient: {patient.demographics.full_name} (ID: {patient.patient_id})")
        
        return patient
    
    def add_epilepsy_diagnosis(self, 
                              patient_id: str, 
                              epilepsy_type: str,
                              severity_level: str,
                              age_at_onset: int = None,
                              **kwargs) -> EpilepsyDiagnosis:
        """
        Add epilepsy diagnosis to a patient
        
        Args:
            patient_id: Patient ID
            epilepsy_type: Type of epilepsy
            severity_level: Severity level
            age_at_onset: Age at onset
            **kwargs: Additional diagnosis information
            
        Returns:
            EpilepsyDiagnosis object
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        diagnosis = EpilepsyDiagnosis(
            patient_id=patient_id,
            epilepsy_type=EpilepsyType(epilepsy_type),
            severity_level=SeverityLevel(severity_level),
            age_at_onset=age_at_onset,
            **kwargs
        )
        
        patient.diagnosis = diagnosis
        
        self.logger.info(f"Added epilepsy diagnosis for patient {patient_id}")
        
        return diagnosis
    
    def add_seizure_event(self, 
                         patient_id: str, 
                         seizure_date: datetime,
                         seizure_type: str = None,
                         duration_minutes: float = None,
                         severity: int = None,
                         **kwargs) -> SeizureEvent:
        """
        Add a seizure event to a patient
        
        Args:
            patient_id: Patient ID
            seizure_date: Date and time of seizure
            seizure_type: Type of seizure
            duration_minutes: Duration in minutes
            severity: Severity (1-10 scale)
            **kwargs: Additional event information
            
        Returns:
            SeizureEvent object
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        event = SeizureEvent(
            patient_id=patient_id,
            seizure_date=seizure_date,
            seizure_type=SeizureType(seizure_type) if seizure_type else None,
            duration_minutes=duration_minutes,
            severity=severity,
            **kwargs
        )
        
        patient.add_seizure_event(event)
        
        self.logger.info(f"Added seizure event for patient {patient_id}")
        
        return event
    
    def get_patient_summary(self, patient_id: str) -> Dict:
        """
        Get a comprehensive summary for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with patient summary
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        return self.analytics.generate_patient_summary_report(patient)
    
    def analyze_seizure_patterns(self, patient_id: str) -> Dict:
        """
        Analyze seizure patterns for a patient
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with pattern analysis
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        return self.analytics.analyze_seizure_patterns(patient)
    
    def calculate_seizure_frequency(self, patient_id: str, days: int = 30) -> Dict:
        """
        Calculate seizure frequency for a patient
        
        Args:
            patient_id: Patient ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with frequency metrics
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        return self.analytics.calculate_seizure_frequency(patient, days)
    
    def generate_seizure_trend_plot(self, patient_id: str, days: int = 90):
        """
        Generate seizure frequency trend plot
        
        Args:
            patient_id: Patient ID
            days: Number of days to plot
            
        Returns:
            Matplotlib figure
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        return self.analytics.plot_seizure_frequency_trend(patient, days)
    
    def generate_seizure_type_plot(self, patient_id: str):
        """
        Generate seizure type distribution plot
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Matplotlib figure
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        return self.analytics.plot_seizure_type_distribution(patient)
    
    def list_patients(self) -> List[Dict]:
        """
        List all patients with basic information
        
        Returns:
            List of patient dictionaries
        """
        patient_list = []
        for patient_id, patient in self.patients.items():
            patient_info = {
                'patient_id': patient_id,
                'name': patient.demographics.full_name,
                'age': patient.demographics.age,
                'gender': patient.demographics.gender.value if patient.demographics.gender else None,
                'seizure_events_count': len(patient.seizure_events),
                'has_diagnosis': patient.diagnosis is not None
            }
            patient_list.append(patient_info)
        
        return patient_list
    
    def export_patient_data(self, patient_id: str, filename: str = None) -> str:
        """
        Export patient data to JSON file
        
        Args:
            patient_id: Patient ID
            filename: Output filename (optional)
            
        Returns:
            Path to exported file
        """
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        if filename is None:
            filename = f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = self.get_patient_summary(patient_id)
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Exported patient data to {filename}")
        
        return filename
    
    def get_framework_statistics(self) -> Dict:
        """
        Get overall framework statistics
        
        Returns:
            Dictionary with framework statistics
        """
        total_patients = len(self.patients)
        total_seizures = sum(len(p.seizure_events) for p in self.patients.values())
        patients_with_diagnosis = sum(1 for p in self.patients.values() if p.diagnosis)
        
        return {
            'total_patients': total_patients,
            'total_seizure_events': total_seizures,
            'patients_with_diagnosis': patients_with_diagnosis,
            'average_seizures_per_patient': total_seizures / total_patients if total_patients > 0 else 0
        }

# Initialize Flask app and framework
app = Flask(__name__)
framework = EpilepsyFramework()

@app.route('/')
def index():
    from flask import render_template
    return render_template('index.html')

@app.route('/create_patient', methods=['POST'])
def create_patient_route():
    try:
        data = request.json
        patient = framework.create_patient(
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=date.fromisoformat(data['date_of_birth']),
            gender=data.get('gender')
        )
        return jsonify({'patient_id': patient.patient_id, 'full_name': patient.demographics.full_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/add_epilepsy_diagnosis', methods=['POST'])
def add_epilepsy_diagnosis_route():
    try:
        data = request.json
        diagnosis = framework.add_epilepsy_diagnosis(
            patient_id=data['patient_id'],
            epilepsy_type=data['epilepsy_type'],
            severity_level=data['severity_level']
        )
        return jsonify({'diagnosis': diagnosis.epilepsy_type.value})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/add_seizure_event', methods=['POST'])
def add_seizure_event_route():
    try:
        data = request.json
        event = framework.add_seizure_event(
            patient_id=data['patient_id'],
            seizure_date=datetime.fromisoformat(data['seizure_date']),
            seizure_type=data.get('seizure_type'),
            duration_minutes=data.get('duration_minutes'),
            severity=data.get('severity')
        )
        return jsonify({'event_id': event.seizure_date.isoformat(), 'seizure_type': event.seizure_type.value if event.seizure_type else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/list_patients', methods=['GET'])
def list_patients_route():
    try:
        return jsonify(framework.list_patients())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/patient_summary/<patient_id>', methods=['GET'])
def patient_summary_route(patient_id):
    try:
        summary = framework.get_patient_summary(patient_id)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/statistics', methods=['GET'])
def statistics_route():
    try:
        stats = framework.get_framework_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def main():
    """Main function to demonstrate the framework"""
    print("=== Epilepsy Public Health Informatics Framework ===")
    print("Initializing framework...")
    
    framework = EpilepsyFramework()
    
    print("\n1. Creating sample patient...")
    patient = framework.create_patient(
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 5, 15),
        gender="Male",
        city="New York",
        state="NY"
    )
    
    print(f"Created patient: {patient.demographics.full_name} (ID: {patient.patient_id})")
    
    print("\n2. Adding epilepsy diagnosis...")
    diagnosis = framework.add_epilepsy_diagnosis(
        patient_id=patient.patient_id,
        epilepsy_type="Focal",
        severity_level="Moderate",
        age_at_onset=25,
        diagnosis_date=date(2020, 1, 15)
    )
    
    print(f"Added diagnosis: {diagnosis.epilepsy_type.value} epilepsy, {diagnosis.severity_level.value} severity")
    
    print("\n3. Adding sample seizure events...")
    # Add some sample seizure events
    seizure_dates = [
        datetime(2024, 6, 1, 10, 30),
        datetime(2024, 6, 8, 15, 45),
        datetime(2024, 6, 15, 9, 15),
        datetime(2024, 6, 22, 14, 20),
        datetime(2024, 6, 29, 11, 10)
    ]
    
    for i, seizure_date in enumerate(seizure_dates):
        event = framework.add_seizure_event(
            patient_id=patient.patient_id,
            seizure_date=seizure_date,
            seizure_type="Focal Aware",
            duration_minutes=2.5 + i * 0.5,
            severity=3 + i % 3,
            stress_level=5 + i % 4
        )
        print(f"Added seizure event: {event.seizure_date}")
    
    print("\n4. Analyzing seizure patterns...")
    patterns = framework.analyze_seizure_patterns(patient.patient_id)
    print(f"Total seizure events: {patterns.get('total_events', 0)}")
    print(f"Average severity: {patterns.get('average_severity', 'N/A')}")
    
    print("\n5. Calculating seizure frequency...")
    frequency = framework.calculate_seizure_frequency(patient.patient_id, 30)
    print(f"Seizures in last 30 days: {frequency['total_seizures']}")
    print(f"Frequency per week: {frequency['frequency_per_week']:.2f}")
    
    print("\n6. Generating patient summary report...")
    summary = framework.get_patient_summary(patient.patient_id)
    print(f"Patient: {summary['demographics']['name']}")
    print(f"Age: {summary['demographics']['age']}")
    print(f"Diagnosis: {summary['diagnosis'].get('epilepsy_type', 'N/A')}")
    
    print("\n7. Framework statistics...")
    stats = framework.get_framework_statistics()
    print(f"Total patients: {stats['total_patients']}")
    print(f"Total seizure events: {stats['total_seizure_events']}")
    
    print("\n8. Exporting patient data...")
    export_file = framework.export_patient_data(patient.patient_id)
    print(f"Exported to: {export_file}")
    
    print("\n=== Framework demonstration completed ===")

if __name__ == "__main__":
    main()
