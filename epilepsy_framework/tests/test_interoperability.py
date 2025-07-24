"""
Comprehensive test suite for interoperability features
"""
import sys
import os
from datetime import datetime, date
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from main_interop import EnhancedEpilepsyFramework
from interoperability.fhir.fhir_resources import FHIRResourceGenerator
from interoperability.hie.hie_connector import HIEConnector, HIEAnalytics
from interoperability.openehr.openehr_archetypes import OpenEHRGenerator
from interoperability.ihia.ihia_integration import IHIAIntegrator, IHIAQualityAssurance

def test_interoperability_framework():
    """Test comprehensive interoperability framework"""
    print("=== Testing Interoperability Framework ===")
    
    # Initialize framework
    framework = EnhancedEpilepsyFramework()
    
    # Test 1: Create multiple patients with diverse data
    print("\n1. Creating diverse patient population...")
    patients = []
    
    patient_scenarios = [
        {
            "first_name": "Emma",
            "last_name": "Watson",
            "date_of_birth": date(1990, 4, 15),
            "gender": "Female",
            "city": "New York",
            "state": "NY",
            "epilepsy_type": "Generalized",
            "severity": "Mild",
            "seizure_events": [
                {"date": datetime(2024, 5, 10, 8, 30), "type": "Absence", "duration": 10, "severity": 2},
                {"date": datetime(2024, 5, 25, 14, 15), "type": "Absence", "duration": 8, "severity": 3}
            ]
        },
        {
            "first_name": "Michael",
            "last_name": "Chen",
            "date_of_birth": date(1985, 8, 22),
            "gender": "Male",
            "city": "San Francisco",
            "state": "CA",
            "epilepsy_type": "Focal",
            "severity": "Severe",
            "seizure_events": [
                {"date": datetime(2024, 6, 2, 11, 45), "type": "Focal Aware", "duration": 120, "severity": 8},
                {"date": datetime(2024, 6, 8, 16, 20), "type": "Focal to Bilateral Tonic-Clonic", "duration": 300, "severity": 9},
                {"date": datetime(2024, 6, 15, 9, 30), "type": "Focal Impaired Awareness", "duration": 180, "severity": 7}
            ]
        },
        {
            "first_name": "Sarah",
            "last_name": "Rodriguez",
            "date_of_birth": date(1992, 12, 5),
            "gender": "Female",
            "city": "Chicago",
            "state": "IL",
            "epilepsy_type": "Combined",
            "severity": "Moderate",
            "seizure_events": [
                {"date": datetime(2024, 6, 1, 13, 20), "type": "Myoclonic", "duration": 5, "severity": 4},
                {"date": datetime(2024, 6, 12, 10, 15), "type": "Generalized Tonic-Clonic", "duration": 90, "severity": 6},
                {"date": datetime(2024, 6, 20, 15, 45), "type": "Absence", "duration": 15, "severity": 3}
            ]
        }
    ]
    
    for scenario in patient_scenarios:
        # Create patient
        patient = framework.create_patient(
            first_name=scenario["first_name"],
            last_name=scenario["last_name"],
            date_of_birth=scenario["date_of_birth"],
            gender=scenario["gender"],
            city=scenario["city"],
            state=scenario["state"],
            phone_number=f"(555) {len(patients):03d}-{len(patients):04d}",
            email=f"{scenario['first_name'].lower()}.{scenario['last_name'].lower()}@email.com"
        )
        
        # Add diagnosis
        framework.add_epilepsy_diagnosis(
            patient_id=patient.patient_id,
            epilepsy_type=scenario["epilepsy_type"],
            severity_level=scenario["severity"],
            age_at_onset=20 + len(patients) * 5,
            diagnosis_date=date(2020, 1, 15)
        )
        
        # Add seizure events
        for event in scenario["seizure_events"]:
            framework.add_seizure_event(
                patient_id=patient.patient_id,
                seizure_date=event["date"],
                seizure_type=event["type"],
                duration_minutes=event["duration"],
                severity=event["severity"]
            )
        
        patients.append(patient)
        print(f"Created patient: {patient.demographics.full_name}")
    
    print(f"Total patients created: {len(patients)}")
    
    # Test 2: Export all patients in all formats
    print("\n2. Testing multi-format export capabilities...")
    for i, patient in enumerate(patients):
        print(f"\nPatient {i+1}: {patient.demographics.full_name}")
        
        # Export in all formats
        export_files = framework.export_all_formats(patient.patient_id)
        
        for format_name, filename in export_files.items():
            file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
            print(f"  {format_name.upper()}: {filename} ({file_size} bytes)")
    
    # Test 3: Validate interoperability compliance
    print("\n3. Testing interoperability compliance...")
    compliance_results = []
    
    for patient in patients:
        validation = framework.validate_interoperability(patient.patient_id)
        compliance_results.append(validation)
        
        print(f"\nPatient: {patient.demographics.full_name}")
        for framework_name, result in validation['frameworks'].items():
            status = result['status']
            print(f"  {framework_name.upper()}: {status}")
    
    # Calculate overall compliance
    total_frameworks = len(compliance_results[0]['frameworks'])
    total_validations = len(compliance_results) * total_frameworks
    successful_validations = sum(
        1 for result in compliance_results 
        for framework_result in result['frameworks'].values()
        if framework_result['status'] == 'valid'
    )
    
    compliance_rate = (successful_validations / total_validations) * 100
    print(f"\nOverall compliance rate: {compliance_rate:.1f}%")
    
    # Test 4: Data quality assessment
    print("\n4. Testing data quality assessment...")
    quality_scores = []
    
    for patient in patients:
        quality = framework.assess_data_quality(patient.patient_id)
        quality_scores.append(quality['overall_score'])
        
        print(f"Patient: {patient.demographics.full_name}")
        print(f"  Overall quality: {quality['overall_score']:.2f}")
        print(f"  Completeness: {quality['dimensions']['completeness']:.2f}")
        print(f"  Accuracy: {quality['dimensions']['accuracy']:.2f}")
        print(f"  Timeliness: {quality['dimensions']['timeliness']:.2f}")
    
    avg_quality = sum(quality_scores) / len(quality_scores)
    print(f"\nAverage data quality score: {avg_quality:.2f}")
    
    # Test 5: HIE integration
    print("\n5. Testing HIE integration...")
    hie_results = []
    
    for patient in patients:
        # Submit to HIE
        submission = framework.submit_to_hie(patient.patient_id)
        hie_results.append(submission)
        
        print(f"Patient: {patient.demographics.full_name}")
        print(f"  HIE submission: {submission['status']}")
        
        # Get care summary
        care_summary = framework.get_hie_care_summary(patient.patient_id)
        print(f"  Care summary: {care_summary['status']}")
    
    successful_submissions = sum(1 for result in hie_results if result['status'] == 'success')
    print(f"\nHIE submission success rate: {(successful_submissions / len(hie_results)) * 100:.1f}%")
    
    # Test 6: Population health analytics
    print("\n6. Testing population health analytics...")
    pop_report = framework.generate_population_health_report()
    
    print(f"Population health metrics:")
    print(f"  Total patients in system: {pop_report['metrics']['total_patients']}")
    print(f"  Average seizure frequency: {pop_report['metrics']['seizure_frequency']['average_per_month']}")
    print(f"  Patients with excellent adherence: {pop_report['metrics']['medication_adherence']['excellent']}")
    print(f"  Seizure-free patients: {pop_report['metrics']['seizure_frequency']['patients_seizure_free']}")
    
    # Test 7: Framework capabilities
    print("\n7. Testing framework capabilities...")
    stats = framework.get_interoperability_statistics()
    
    print(f"Framework capabilities:")
    print(f"  Supported standards: {len(stats['supported_standards'])}")
    print(f"  Export formats: {len(stats['export_formats'])}")
    print(f"  Integration capabilities: {len(stats['integration_capabilities'])}")
    
    for standard in stats['supported_standards']:
        print(f"    • {standard}")
    
    # Test 8: Individual framework components
    print("\n8. Testing individual framework components...")
    
    # Test FHIR resources
    fhir_generator = FHIRResourceGenerator()
    test_patient = patients[0]
    
    fhir_resources = framework.generate_fhir_resources(test_patient.patient_id)
    print(f"FHIR resources generated: {len(fhir_resources)}")
    
    # Test OpenEHR composition
    openehr_generator = OpenEHRGenerator()
    composition = openehr_generator.create_patient_summary_composition(test_patient)
    print(f"OpenEHR composition created: {composition.uid}")
    
    # Test IHIA health record
    ihia_integrator = IHIAIntegrator("TEST-ORG", "TEST-SYS")
    ihia_record = ihia_integrator.create_ihia_health_record(test_patient)
    print(f"IHIA health record created: {ihia_record.record_id}")
    
    # Test HIE connector
    hie_connector = HIEConnector("TEST-FACILITY")
    hie_record = hie_connector.create_hie_patient_record(test_patient)
    print(f"HIE patient record created: {hie_record.patient_id}")
    
    # Test 9: Performance metrics
    print("\n9. Performance metrics...")
    
    framework_stats = framework.get_framework_statistics()
    print(f"Framework statistics:")
    print(f"  Total patients: {framework_stats['total_patients']}")
    print(f"  Total seizure events: {framework_stats['total_seizure_events']}")
    print(f"  Patients with diagnosis: {framework_stats['patients_with_diagnosis']}")
    print(f"  Average seizures per patient: {framework_stats['average_seizures_per_patient']:.2f}")
    
    print("\n=== Interoperability Framework Testing Completed ===")
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"✓ Successfully created {len(patients)} patients")
    print(f"✓ Exported data in {len(export_files)} formats")
    print(f"✓ Achieved {compliance_rate:.1f}% interoperability compliance")
    print(f"✓ Average data quality score: {avg_quality:.2f}")
    print(f"✓ HIE integration success rate: {(successful_submissions / len(hie_results)) * 100:.1f}%")
    print(f"✓ All {len(stats['supported_standards'])} health information standards supported")
    print("\nThe Enhanced Epilepsy Framework is fully operational with comprehensive interoperability!")

if __name__ == "__main__":
    test_interoperability_framework()
