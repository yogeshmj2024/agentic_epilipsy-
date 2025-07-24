"""
Health Information Exchange (HIE) Framework for Epilepsy Patient Data
"""
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from models.patient import Patient, SeizureEvent
from models.treatment import TreatmentPlan, TreatmentOutcome
import logging

@dataclass
class HIEPatientRecord:
    """Standardized patient record for HIE"""
    patient_id: str
    facility_id: str
    medical_record_number: str
    demographics: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    encounters: List[Dict[str, Any]]
    medications: List[Dict[str, Any]]
    lab_results: List[Dict[str, Any]]
    last_updated: datetime
    
class HIEConnector:
    """Health Information Exchange connector for sharing epilepsy patient data"""
    
    def __init__(self, facility_id: str, api_endpoint: str = None):
        self.facility_id = facility_id
        self.api_endpoint = api_endpoint or "https://hie.health.gov/api/v1"
        self.logger = logging.getLogger(__name__)
        
    def create_hie_patient_record(self, patient: Patient) -> HIEPatientRecord:
        """Convert internal patient data to HIE format"""
        
        # Demographics
        demographics = {
            "first_name": patient.demographics.first_name,
            "last_name": patient.demographics.last_name,
            "date_of_birth": patient.demographics.date_of_birth.isoformat() if patient.demographics.date_of_birth else None,
            "gender": patient.demographics.gender.value if patient.demographics.gender else None,
            "race": patient.demographics.race,
            "ethnicity": patient.demographics.ethnicity,
            "address": {
                "street": patient.demographics.address,
                "city": patient.demographics.city,
                "state": patient.demographics.state,
                "zip_code": patient.demographics.zip_code
            },
            "contact": {
                "phone": patient.demographics.phone_number,
                "email": patient.demographics.email
            },
            "emergency_contact": {
                "name": patient.demographics.emergency_contact,
                "phone": patient.demographics.emergency_phone
            }
        }
        
        # Conditions
        conditions = []
        if patient.diagnosis:
            conditions.append({
                "condition_id": patient.diagnosis.diagnosis_id,
                "condition_code": "G40.9",  # ICD-10 code for epilepsy
                "condition_name": "Epilepsy",
                "condition_type": patient.diagnosis.epilepsy_type.value if patient.diagnosis.epilepsy_type else None,
                "severity": patient.diagnosis.severity_level.value if patient.diagnosis.severity_level else None,
                "onset_age": patient.diagnosis.age_at_onset,
                "diagnosis_date": patient.diagnosis.diagnosis_date.isoformat() if patient.diagnosis.diagnosis_date else None,
                "status": "active",
                "clinician": patient.diagnosis.diagnosing_physician
            })
        
        # Encounters (seizure events)
        encounters = []
        for event in patient.seizure_events:
            encounters.append({
                "encounter_id": event.event_id,
                "encounter_type": "seizure_event",
                "encounter_date": event.seizure_date.isoformat() if event.seizure_date else None,
                "seizure_type": event.seizure_type.value if event.seizure_type else None,
                "duration_minutes": event.duration_minutes,
                "severity": event.severity,
                "triggers": event.triggers,
                "hospitalization_required": event.hospitalization_required,
                "notes": event.notes
            })
        
        # Medications (placeholder - would need actual prescription data)
        medications = []
        
        # Lab results (placeholder - would need actual lab data)
        lab_results = []
        
        return HIEPatientRecord(
            patient_id=patient.patient_id,
            facility_id=self.facility_id,
            medical_record_number=patient.patient_id,
            demographics=demographics,
            conditions=conditions,
            encounters=encounters,
            medications=medications,
            lab_results=lab_results,
            last_updated=datetime.now()
        )
    
    def submit_patient_data(self, patient: Patient) -> Dict[str, Any]:
        """Submit patient data to HIE"""
        try:
            hie_record = self.create_hie_patient_record(patient)
            
            # Convert to dictionary for JSON serialization
            record_dict = asdict(hie_record)
            
            # In a real implementation, this would make an API call
            # For demo purposes, we'll simulate the response
            self.logger.info(f"Submitting patient {patient.patient_id} to HIE")
            
            # Simulated API response
            response = {
                "status": "success",
                "message": "Patient data successfully submitted to HIE",
                "hie_patient_id": f"HIE-{patient.patient_id}",
                "timestamp": datetime.now().isoformat(),
                "data_points_submitted": {
                    "demographics": 1,
                    "conditions": len(hie_record.conditions),
                    "encounters": len(hie_record.encounters),
                    "medications": len(hie_record.medications),
                    "lab_results": len(hie_record.lab_results)
                }
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error submitting patient data to HIE: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def query_patient_data(self, patient_id: str, external_facility_id: str = None) -> Dict[str, Any]:
        """Query patient data from HIE"""
        try:
            self.logger.info(f"Querying HIE for patient {patient_id}")
            
            # Simulated HIE query response
            response = {
                "status": "success",
                "patient_id": patient_id,
                "facilities_with_data": [
                    {
                        "facility_id": "HOSP001",
                        "facility_name": "General Hospital",
                        "last_encounter": "2024-06-15T14:30:00Z",
                        "data_types": ["demographics", "conditions", "encounters", "medications"]
                    },
                    {
                        "facility_id": "CLINIC002",
                        "facility_name": "Neurology Clinic",
                        "last_encounter": "2024-06-20T10:15:00Z",
                        "data_types": ["encounters", "medications", "lab_results"]
                    }
                ],
                "consent_status": "active",
                "query_timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error querying HIE for patient data: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_patient_care_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive care summary from HIE"""
        try:
            self.logger.info(f"Retrieving care summary for patient {patient_id}")
            
            # Simulated care summary response
            response = {
                "status": "success",
                "patient_id": patient_id,
                "care_summary": {
                    "active_conditions": [
                        {
                            "condition": "Epilepsy",
                            "type": "Focal",
                            "severity": "Moderate",
                            "last_updated": "2024-06-15T14:30:00Z"
                        }
                    ],
                    "recent_encounters": [
                        {
                            "date": "2024-06-20T10:15:00Z",
                            "type": "seizure_event",
                            "facility": "Neurology Clinic",
                            "severity": 6
                        }
                    ],
                    "active_medications": [
                        {
                            "medication": "Levetiracetam",
                            "dosage": "500mg",
                            "frequency": "twice daily",
                            "prescribing_facility": "General Hospital"
                        }
                    ],
                    "alerts": [
                        {
                            "type": "drug_interaction",
                            "message": "Check for interactions with new prescriptions",
                            "priority": "medium"
                        }
                    ]
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error retrieving care summary: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def notify_care_team(self, patient_id: str, event_type: str, message: str) -> Dict[str, Any]:
        """Send notification to care team members"""
        try:
            self.logger.info(f"Sending care team notification for patient {patient_id}")
            
            # Simulated notification response
            response = {
                "status": "success",
                "notification_id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "patient_id": patient_id,
                "event_type": event_type,
                "message": message,
                "recipients": [
                    {
                        "provider": "Dr. Sarah Johnson",
                        "role": "Neurologist",
                        "facility": "Neurology Clinic",
                        "notification_method": "secure_message"
                    },
                    {
                        "provider": "Dr. Michael Chen",
                        "role": "Primary Care Physician",
                        "facility": "General Hospital",
                        "notification_method": "email"
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error sending care team notification: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

class HIEAnalytics:
    """Analytics for HIE data sharing and utilization"""
    
    def __init__(self, hie_connector: HIEConnector):
        self.hie = hie_connector
        self.logger = logging.getLogger(__name__)
    
    def generate_population_health_report(self, condition: str = "epilepsy") -> Dict[str, Any]:
        """Generate population health report from HIE data"""
        
        # Simulated population health data
        report = {
            "condition": condition,
            "reporting_period": {
                "start": "2024-01-01",
                "end": "2024-06-30"
            },
            "metrics": {
                "total_patients": 1250,
                "new_diagnoses": 45,
                "active_patients": 1205,
                "seizure_frequency": {
                    "average_per_month": 2.3,
                    "patients_seizure_free": 312,
                    "patients_reduced_frequency": 678
                },
                "medication_adherence": {
                    "excellent": 456,
                    "good": 523,
                    "fair": 189,
                    "poor": 82
                },
                "quality_metrics": {
                    "patients_with_care_plan": 1134,
                    "patients_with_emergency_plan": 987,
                    "patients_receiving_specialty_care": 1098
                }
            },
            "geographic_distribution": {
                "urban": 754,
                "suburban": 389,
                "rural": 107
            },
            "demographic_breakdown": {
                "age_groups": {
                    "0-17": 234,
                    "18-34": 378,
                    "35-54": 456,
                    "55+": 182
                },
                "gender": {
                    "male": 612,
                    "female": 638
                }
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def track_care_coordination(self, patient_id: str) -> Dict[str, Any]:
        """Track care coordination across facilities"""
        
        # Simulated care coordination data
        coordination_data = {
            "patient_id": patient_id,
            "facilities_involved": [
                {
                    "facility_id": "HOSP001",
                    "facility_name": "General Hospital",
                    "role": "Primary Care",
                    "last_interaction": "2024-06-15T14:30:00Z"
                },
                {
                    "facility_id": "CLINIC002",
                    "facility_name": "Neurology Clinic",
                    "role": "Specialty Care",
                    "last_interaction": "2024-06-20T10:15:00Z"
                }
            ],
            "care_transitions": [
                {
                    "from_facility": "Emergency Department",
                    "to_facility": "Neurology Clinic",
                    "date": "2024-06-15T16:00:00Z",
                    "reason": "Seizure episode"
                }
            ],
            "information_sharing": {
                "records_shared": 8,
                "average_sharing_time": "4.2 minutes",
                "duplicate_tests_avoided": 3
            },
            "coordination_score": 8.5,
            "timestamp": datetime.now().isoformat()
        }
        
        return coordination_data

# Global HIE connector instance
hie_connector = HIEConnector(facility_id="EPILEPSY-FRAMEWORK-001")
hie_analytics = HIEAnalytics(hie_connector)
