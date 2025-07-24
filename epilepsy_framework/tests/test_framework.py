"""
Test file to demonstrate the Epilepsy Public Health Informatics Framework capabilities
"""
import sys
import os
from datetime import datetime, date
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from main import EpilepsyFramework
from utils.validation import DataValidator
from utils.analytics import EpilepsyAnalytics

def test_framework_basic_functionality():
    """Test basic framework functionality"""
    print("=== Testing Framework Basic Functionality ===")
    
    # Initialize framework
    framework = EpilepsyFramework()
    
    # Test 1: Create multiple patients
    print("\n1. Creating multiple patients...")
    patients = []
    
    patient_data = [
        {"first_name": "Alice", "last_name": "Johnson", "date_of_birth": date(1985, 3, 20), "gender": "Female"},
        {"first_name": "Bob", "last_name": "Smith", "date_of_birth": date(1992, 7, 15), "gender": "Male"},
        {"first_name": "Carol", "last_name": "Davis", "date_of_birth": date(1978, 11, 30), "gender": "Female"}
    ]
    
    for data in patient_data:
        patient = framework.create_patient(**data)
        patients.append(patient)
        print(f"Created: {patient.demographics.full_name} (Age: {patient.demographics.age})")
    
    # Test 2: Add diagnoses
    print("\n2. Adding epilepsy diagnoses...")
    diagnoses = [
        {"epilepsy_type": "Generalized", "severity_level": "Mild", "age_at_onset": 16},
        {"epilepsy_type": "Focal", "severity_level": "Severe", "age_at_onset": 22},
        {"epilepsy_type": "Combined", "severity_level": "Moderate", "age_at_onset": 35}
    ]
    
    for i, diagnosis_data in enumerate(diagnoses):
        diagnosis = framework.add_epilepsy_diagnosis(
            patient_id=patients[i].patient_id,
            **diagnosis_data
        )
        print(f"Added diagnosis for {patients[i].demographics.full_name}: {diagnosis.epilepsy_type.value} - {diagnosis.severity_level.value}")
    
    # Test 3: Add seizure events
    print("\n3. Adding seizure events...")
    seizure_events = [
        # Alice - fewer seizures (mild case)
        [
            {"seizure_date": datetime(2024, 6, 1, 14, 30), "seizure_type": "Absence", "duration_minutes": 1.5, "severity": 2},
            {"seizure_date": datetime(2024, 6, 15, 9, 15), "seizure_type": "Absence", "duration_minutes": 2.0, "severity": 3}
        ],
        # Bob - more frequent seizures (severe case)
        [
            {"seizure_date": datetime(2024, 6, 2, 11, 45), "seizure_type": "Focal Aware", "duration_minutes": 5.0, "severity": 7},
            {"seizure_date": datetime(2024, 6, 5, 16, 20), "seizure_type": "Focal Impaired Awareness", "duration_minutes": 8.5, "severity": 8},
            {"seizure_date": datetime(2024, 6, 8, 7, 30), "seizure_type": "Focal Aware", "duration_minutes": 4.5, "severity": 6},
            {"seizure_date": datetime(2024, 6, 12, 13, 15), "seizure_type": "Focal to Bilateral Tonic-Clonic", "duration_minutes": 12.0, "severity": 9}
        ],
        # Carol - moderate seizures
        [
            {"seizure_date": datetime(2024, 6, 3, 10, 10), "seizure_type": "Generalized Tonic-Clonic", "duration_minutes": 3.5, "severity": 5},
            {"seizure_date": datetime(2024, 6, 10, 15, 45), "seizure_type": "Myoclonic", "duration_minutes": 1.0, "severity": 4},
            {"seizure_date": datetime(2024, 6, 20, 12, 30), "seizure_type": "Generalized Tonic-Clonic", "duration_minutes": 4.0, "severity": 6}
        ]
    ]
    
    for i, patient_events in enumerate(seizure_events):
        for event_data in patient_events:
            event = framework.add_seizure_event(
                patient_id=patients[i].patient_id,
                **event_data
            )
            print(f"Added seizure for {patients[i].demographics.full_name}: {event.seizure_type.value}")
    
    # Test 4: Analyze patterns
    print("\n4. Analyzing seizure patterns...")
    for patient in patients:
        patterns = framework.analyze_seizure_patterns(patient.patient_id)
        print(f"\\n{patient.demographics.full_name}:")
        print(f"  Total events: {patterns.get('total_events', 0)}")
        print(f"  Average severity: {patterns.get('average_severity', 'N/A')}")
        print(f"  Average duration: {patterns.get('average_duration', 'N/A')}")
        print(f"  Seizure types: {list(patterns.get('seizure_types', {}).keys())}")
    
    # Test 5: Framework statistics
    print("\n5. Framework statistics...")
    stats = framework.get_framework_statistics()
    print(f"Total patients: {stats['total_patients']}")
    print(f"Total seizure events: {stats['total_seizure_events']}")
    print(f"Patients with diagnosis: {stats['patients_with_diagnosis']}")
    print(f"Average seizures per patient: {stats['average_seizures_per_patient']:.2f}")
    
    # Test 6: Export all patient data
    print("\n6. Exporting patient data...")
    for patient in patients:
        filename = framework.export_patient_data(patient.patient_id)
        print(f"Exported {patient.demographics.full_name} to {filename}")
    
    print("\n=== Framework Basic Functionality Test Completed ===")

def test_data_validation():
    """Test data validation functionality"""
    print("\n=== Testing Data Validation ===")
    
    validator = DataValidator()
    
    # Test valid data
    valid_patient_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'date_of_birth': date(1990, 1, 1),
        'email': 'john.doe@example.com',
        'phone_number': '(555) 123-4567',
        'zip_code': '12345',
        'gender': 'Male'
    }
    
    errors = validator.validate_patient_data(valid_patient_data)
    print(f"Valid data validation errors: {errors}")
    
    # Test invalid data
    invalid_patient_data = {
        'first_name': '',  # Empty first name
        'last_name': 'Doe',
        'date_of_birth': date(2030, 1, 1),  # Future date
        'email': 'invalid-email',  # Invalid email
        'phone_number': '123',  # Invalid phone
        'zip_code': 'invalid',  # Invalid zip
        'gender': 'InvalidGender'  # Invalid gender
    }
    
    errors = validator.validate_patient_data(invalid_patient_data)
    print(f"Invalid data validation errors: {errors}")
    
    print("=== Data Validation Test Completed ===")

def test_analytics():
    """Test analytics functionality"""
    print("\n=== Testing Analytics ===")
    
    # Create a sample patient with multiple seizure events
    framework = EpilepsyFramework()
    patient = framework.create_patient(
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1985, 5, 15),
        gender="Female"
    )
    
    # Add diagnosis
    framework.add_epilepsy_diagnosis(
        patient_id=patient.patient_id,
        epilepsy_type="Focal",
        severity_level="Moderate",
        age_at_onset=30
    )
    
    # Add various seizure events
    seizure_dates = [
        datetime(2024, 6, 1, 10, 30),
        datetime(2024, 6, 3, 15, 45),
        datetime(2024, 6, 5, 9, 15),
        datetime(2024, 6, 8, 14, 20),
        datetime(2024, 6, 12, 11, 10),
        datetime(2024, 6, 15, 16, 30),
        datetime(2024, 6, 20, 13, 45)
    ]
    
    seizure_types = ["Focal Aware", "Focal Impaired Awareness", "Focal Aware", 
                    "Focal to Bilateral Tonic-Clonic", "Focal Aware", "Focal Impaired Awareness", "Focal Aware"]
    
    for i, seizure_date in enumerate(seizure_dates):
        framework.add_seizure_event(
            patient_id=patient.patient_id,
            seizure_date=seizure_date,
            seizure_type=seizure_types[i],
            duration_minutes=2.0 + i * 0.5,
            severity=3 + (i % 4),
            stress_level=4 + (i % 3)
        )
    
    # Test analytics
    analytics = EpilepsyAnalytics()
    
    # Test seizure frequency calculation
    frequency = analytics.calculate_seizure_frequency(patient, 30)
    print(f"Seizure frequency (30 days): {frequency}")
    
    # Test pattern analysis
    patterns = analytics.analyze_seizure_patterns(patient)
    print(f"Seizure patterns: {patterns}")
    
    # Test calendar generation
    calendar = analytics.generate_seizure_calendar(patient, 2024)
    print(f"Calendar generated with {len(calendar)} days")
    
    print("=== Analytics Test Completed ===")

def main():
    """Main test function"""
    test_framework_basic_functionality()
    test_data_validation()
    test_analytics()
    print("\n=== All Tests Completed Successfully! ===")

if __name__ == "__main__":
    main()
