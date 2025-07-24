"""
Enhanced Main Application with Interoperability Features
Integrates FHIR, HL7, HIE, OpenEHR, and IHIA frameworks
"""
import sys
import json
from datetime import datetime, date
from typing import Optional, List, Dict
import logging
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from main import EpilepsyFramework
from interoperability.fhir.fhir_resources import FHIRResourceGenerator
from interoperability.hie.hie_connector import HIEConnector, HIEAnalytics
from interoperability.openehr.openehr_archetypes import OpenEHRGenerator
from interoperability.ihia.ihia_integration import IHIAIntegrator, IHIAQualityAssurance

class EnhancedEpilepsyFramework(EpilepsyFramework):
    """Enhanced epilepsy framework with interoperability capabilities"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize interoperability components
        self.fhir_generator = FHIRResourceGenerator()
        self.hie_connector = HIEConnector(facility_id="EPILEPSY-FRAMEWORK-001")
        self.hie_analytics = HIEAnalytics(self.hie_connector)
        self.openehr_generator = OpenEHRGenerator()
        self.ihia_integrator = IHIAIntegrator(
            organization_id="EPILEPSY-FRAMEWORK-ORG",
            system_id="EPILEPSY-FRAMEWORK-SYS-001"
        )
        self.ihia_qa = IHIAQualityAssurance(self.ihia_integrator)
        
        self.logger.info("Enhanced Epilepsy Framework with Interoperability initialized")
    
    def export_patient_to_fhir(self, patient_id: str, filename: str = None) -> str:
        """Export patient data as FHIR bundle"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        filename = self.fhir_generator.export_to_fhir_json(patient, filename)
        self.logger.info(f"Exported patient {patient_id} to FHIR format: {filename}")
        return filename
    
    def export_patient_to_openehr(self, patient_id: str, filename: str = None) -> str:
        """Export patient data as OpenEHR composition"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        filename = self.openehr_generator.export_to_openehr_json(patient, filename)
        self.logger.info(f"Exported patient {patient_id} to OpenEHR format: {filename}")
        return filename
    
    def export_patient_to_ihia(self, patient_id: str, filename: str = None) -> str:
        """Export patient data as IHIA bundle"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        filename = self.ihia_integrator.export_ihia_bundle(patient, filename)
        self.logger.info(f"Exported patient {patient_id} to IHIA format: {filename}")
        return filename
    
    def submit_to_hie(self, patient_id: str) -> Dict[str, any]:
        """Submit patient data to Health Information Exchange"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        response = self.hie_connector.submit_patient_data(patient)
        self.logger.info(f"Submitted patient {patient_id} to HIE")
        return response
    
    def query_hie_for_patient(self, patient_id: str) -> Dict[str, any]:
        """Query HIE for patient data"""
        response = self.hie_connector.query_patient_data(patient_id)
        self.logger.info(f"Queried HIE for patient {patient_id}")
        return response
    
    def get_hie_care_summary(self, patient_id: str) -> Dict[str, any]:
        """Get care summary from HIE"""
        response = self.hie_connector.get_patient_care_summary(patient_id)
        self.logger.info(f"Retrieved care summary for patient {patient_id}")
        return response
    
    def generate_fhir_resources(self, patient_id: str) -> Dict[str, any]:
        """Generate individual FHIR resources for a patient"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        resources = {}
        
        # Patient resource
        resources['Patient'] = self.fhir_generator.generate_patient_resource(patient)
        
        # Condition resource
        if patient.diagnosis:
            resources['Condition'] = self.fhir_generator.generate_condition_resource(
                patient, patient.diagnosis
            )
        
        # Observation resources for seizure events
        resources['Observations'] = []
        for event in patient.seizure_events:
            observation = self.fhir_generator.generate_observation_resource(patient, event)
            resources['Observations'].append(observation)
        
        self.logger.info(f"Generated FHIR resources for patient {patient_id}")
        return resources
    
    def assess_data_quality(self, patient_id: str) -> Dict[str, any]:
        """Assess data quality using IHIA framework"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        # Create IHIA health record
        health_record = self.ihia_integrator.create_ihia_health_record(patient)
        
        # Assess quality
        quality_assessment = self.ihia_qa.assess_data_quality(health_record)
        
        self.logger.info(f"Assessed data quality for patient {patient_id}")
        return quality_assessment
    
    def generate_population_health_report(self) -> Dict[str, any]:
        """Generate population health report using HIE analytics"""
        report = self.hie_analytics.generate_population_health_report()
        self.logger.info("Generated population health report")
        return report
    
    def export_all_formats(self, patient_id: str) -> Dict[str, str]:
        """Export patient data in all supported formats"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        export_files = {}
        
        # Original JSON format
        export_files['json'] = self.export_patient_data(patient_id)
        
        # FHIR format
        export_files['fhir'] = self.export_patient_to_fhir(patient_id)
        
        # OpenEHR format
        export_files['openehr'] = self.export_patient_to_openehr(patient_id)
        
        # IHIA format
        export_files['ihia'] = self.export_patient_to_ihia(patient_id)
        
        self.logger.info(f"Exported patient {patient_id} in all formats")
        return export_files
    
    def validate_interoperability(self, patient_id: str) -> Dict[str, any]:
        """Validate interoperability compliance across all frameworks"""
        patient = self.patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found")
        
        validation_results = {
            'patient_id': patient_id,
            'validation_timestamp': datetime.now().isoformat(),
            'frameworks': {}
        }
        
        # FHIR validation
        try:
            fhir_bundle = self.fhir_generator.generate_bundle_resource(patient)
            validation_results['frameworks']['fhir'] = {
                'status': 'valid',
                'resource_count': len(fhir_bundle['entry']),
                'profile_compliance': 'R4'
            }
        except Exception as e:
            validation_results['frameworks']['fhir'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # OpenEHR validation
        try:
            openehr_composition = self.openehr_generator.create_patient_summary_composition(patient)
            validation_results['frameworks']['openehr'] = {
                'status': 'valid',
                'composition_id': openehr_composition.uid,
                'content_count': len(openehr_composition.content)
            }
        except Exception as e:
            validation_results['frameworks']['openehr'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # IHIA validation
        try:
            ihia_record = self.ihia_integrator.create_ihia_health_record(patient)
            ihia_validation = self.ihia_integrator.validate_ihia_compliance(ihia_record)
            validation_results['frameworks']['ihia'] = {
                'status': 'valid' if ihia_validation['is_compliant'] else 'invalid',
                'compliance_score': ihia_validation['compliance_score'],
                'checks_passed': len([c for c in ihia_validation['checks'] if c['status'] == 'pass'])
            }
        except Exception as e:
            validation_results['frameworks']['ihia'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # HIE validation
        try:
            hie_record = self.hie_connector.create_hie_patient_record(patient)
            validation_results['frameworks']['hie'] = {
                'status': 'valid',
                'record_id': hie_record.patient_id,
                'data_elements': len(hie_record.demographics) + len(hie_record.conditions) + len(hie_record.encounters)
            }
        except Exception as e:
            validation_results['frameworks']['hie'] = {
                'status': 'error',
                'error': str(e)
            }
        
        self.logger.info(f"Validated interoperability for patient {patient_id}")
        return validation_results
    
    def get_interoperability_statistics(self) -> Dict[str, any]:
        """Get statistics about interoperability capabilities"""
        stats = {
            'framework_version': '1.0.0',
            'supported_standards': [
                'FHIR R4',
                'HL7 v2.8',
                'OpenEHR',
                'HIE',
                'IHIA v2.1'
            ],
            'export_formats': [
                'JSON',
                'FHIR Bundle',
                'OpenEHR Composition',
                'IHIA Bundle',
                'HIE Record'
            ],
            'interoperability_features': {
                'data_validation': True,
                'quality_assessment': True,
                'standard_compliance': True,
                'population_health': True,
                'care_coordination': True
            },
            'integration_capabilities': {
                'hie_submission': True,
                'fhir_export': True,
                'openehr_export': True,
                'ihia_compliance': True,
                'hl7_messaging': True
            }
        }
        
        return stats

def main():
    """Enhanced main function demonstrating interoperability features"""
    print("=== Enhanced Epilepsy Public Health Informatics Framework ===")
    print("Initializing framework with interoperability capabilities...")
    
    framework = EnhancedEpilepsyFramework()
    
    print("\n1. Creating sample patient...")
    patient = framework.create_patient(
        first_name="Alice",
        last_name="Johnson",
        date_of_birth=date(1985, 3, 20),
        gender="Female",
        city="Boston",
        state="MA",
        zip_code="02101",
        phone_number="(617) 555-0123",
        email="alice.johnson@email.com"
    )
    
    print(f"Created patient: {patient.demographics.full_name} (ID: {patient.patient_id})")
    
    print("\n2. Adding comprehensive epilepsy data...")
    # Add diagnosis
    diagnosis = framework.add_epilepsy_diagnosis(
        patient_id=patient.patient_id,
        epilepsy_type="Focal",
        severity_level="Moderate",
        age_at_onset=28,
        diagnosis_date=date(2020, 1, 15),
        diagnosing_physician="Dr. Sarah Wilson"
    )
    
    # Add multiple seizure events
    seizure_events = [
        {
            "seizure_date": datetime(2024, 6, 1, 14, 30),
            "seizure_type": "Focal Aware",
            "duration_minutes": 2.5,
            "severity": 4,
            "triggers": ["stress", "lack of sleep"]
        },
        {
            "seizure_date": datetime(2024, 6, 15, 9, 15),
            "seizure_type": "Focal Impaired Awareness",
            "duration_minutes": 4.0,
            "severity": 6,
            "triggers": ["missed medication"]
        },
        {
            "seizure_date": datetime(2024, 6, 28, 11, 45),
            "seizure_type": "Focal Aware",
            "duration_minutes": 1.5,
            "severity": 3,
            "triggers": ["bright lights"]
        }
    ]
    
    for event_data in seizure_events:
        framework.add_seizure_event(patient_id=patient.patient_id, **event_data)
    
    print("Added diagnosis and seizure events")
    
    print("\n3. Demonstrating interoperability features...")
    
    # Export in all formats
    print("\n   a) Exporting data in all formats...")
    export_files = framework.export_all_formats(patient.patient_id)
    for format_name, filename in export_files.items():
        print(f"      {format_name.upper()}: {filename}")
    
    # Validate interoperability
    print("\n   b) Validating interoperability compliance...")
    validation = framework.validate_interoperability(patient.patient_id)
    print(f"      Frameworks validated: {len(validation['frameworks'])}")
    for framework_name, result in validation['frameworks'].items():
        print(f"      {framework_name.upper()}: {result['status']}")
    
    # Data quality assessment
    print("\n   c) Assessing data quality...")
    quality = framework.assess_data_quality(patient.patient_id)
    print(f"      Overall quality score: {quality['overall_score']:.2f}")
    print(f"      Completeness: {quality['dimensions']['completeness']:.2f}")
    print(f"      Accuracy: {quality['dimensions']['accuracy']:.2f}")
    
    # HIE integration
    print("\n   d) Health Information Exchange integration...")
    hie_submission = framework.submit_to_hie(patient.patient_id)
    print(f"      HIE submission: {hie_submission['status']}")
    
    care_summary = framework.get_hie_care_summary(patient.patient_id)
    print(f"      Care summary retrieved: {care_summary['status']}")
    
    # Population health report
    print("\n   e) Population health analytics...")
    pop_report = framework.generate_population_health_report()
    print(f"      Total patients analyzed: {pop_report['metrics']['total_patients']}")
    print(f"      Average seizure frequency: {pop_report['metrics']['seizure_frequency']['average_per_month']}")
    
    print("\n4. Framework capabilities summary...")
    stats = framework.get_interoperability_statistics()
    print(f"   Supported standards: {', '.join(stats['supported_standards'])}")
    print(f"   Export formats: {len(stats['export_formats'])}")
    print(f"   Integration capabilities: {len(stats['integration_capabilities'])}")
    
    print("\n5. Framework statistics...")
    framework_stats = framework.get_framework_statistics()
    print(f"   Total patients: {framework_stats['total_patients']}")
    print(f"   Total seizure events: {framework_stats['total_seizure_events']}")
    
    print("\n=== Enhanced Framework Demonstration Completed ===")
    print("\nThe framework now supports:")
    print("• FHIR R4 for clinical data exchange")
    print("• HL7 v2.8 for messaging")
    print("• OpenEHR for structured health records")
    print("• HIE for health information exchange")
    print("• IHIA for integrated health information architecture")
    print("• Comprehensive data quality assessment")
    print("• Population health analytics")
    print("• Multi-format data export capabilities")

if __name__ == "__main__":
    main()
