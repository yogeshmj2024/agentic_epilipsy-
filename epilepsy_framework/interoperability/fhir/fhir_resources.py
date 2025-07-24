"""
FHIR (Fast Healthcare Interoperability Resources) implementation for Epilepsy Framework
"""
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from models.patient import Patient, PatientDemographics, EpilepsyDiagnosis, SeizureEvent
from models.treatment import TreatmentPlan, MedicationPrescription, TreatmentOutcome
import uuid

class FHIRResourceGenerator:
    """Generate FHIR-compliant resources for epilepsy patients"""
    
    def __init__(self):
        self.base_url = "https://epilepsy-framework.org/fhir"
        self.version = "4.0.1"
    
    def generate_patient_resource(self, patient: Patient) -> Dict[str, Any]:
        """Generate FHIR Patient resource"""
        demographics = patient.demographics
        
        # Build identifier array
        identifiers = [
            {
                "use": "usual",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR",
                            "display": "Medical Record Number"
                        }
                    ]
                },
                "system": f"{self.base_url}/patient-id",
                "value": demographics.patient_id
            }
        ]
        
        # Add insurance identifier if available
        if demographics.insurance_id:
            identifiers.append({
                "use": "secondary",
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MB",
                            "display": "Member Number"
                        }
                    ]
                },
                "system": f"{self.base_url}/insurance-id",
                "value": demographics.insurance_id
            })
        
        # Build name array
        names = [
            {
                "use": "official",
                "family": demographics.last_name,
                "given": [demographics.first_name]
            }
        ]
        
        # Build contact info
        telecoms = []
        if demographics.phone_number:
            telecoms.append({
                "system": "phone",
                "value": demographics.phone_number,
                "use": "home"
            })
        if demographics.email:
            telecoms.append({
                "system": "email",
                "value": demographics.email,
                "use": "home"
            })
        
        # Build address
        addresses = []
        if demographics.address:
            addresses.append({
                "use": "home",
                "type": "both",
                "line": [demographics.address],
                "city": demographics.city,
                "state": demographics.state,
                "postalCode": demographics.zip_code,
                "country": "US"
            })
        
        # Build emergency contact
        contacts = []
        if demographics.emergency_contact:
            contacts.append({
                "relationship": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                                "code": "C",
                                "display": "Emergency Contact"
                            }
                        ]
                    }
                ],
                "name": {
                    "text": demographics.emergency_contact
                },
                "telecom": [
                    {
                        "system": "phone",
                        "value": demographics.emergency_phone,
                        "use": "home"
                    }
                ] if demographics.emergency_phone else []
            })
        
        fhir_patient = {
            "resourceType": "Patient",
            "id": demographics.patient_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": demographics.updated_at.isoformat() if demographics.updated_at else datetime.now().isoformat(),
                "profile": [f"{self.base_url}/StructureDefinition/EpilepsyPatient"]
            },
            "identifier": identifiers,
            "active": True,
            "name": names,
            "telecom": telecoms,
            "gender": demographics.gender.value.lower() if demographics.gender else "unknown",
            "birthDate": demographics.date_of_birth.isoformat() if demographics.date_of_birth else None,
            "address": addresses,
            "contact": contacts
        }
        
        return fhir_patient
    
    def generate_condition_resource(self, patient: Patient, diagnosis: EpilepsyDiagnosis) -> Dict[str, Any]:
        """Generate FHIR Condition resource for epilepsy diagnosis"""
        
        # Map epilepsy types to SNOMED codes
        epilepsy_codes = {
            "Generalized": {
                "system": "http://snomed.info/sct",
                "code": "230456007",
                "display": "Generalized epilepsy"
            },
            "Focal": {
                "system": "http://snomed.info/sct",
                "code": "230407005",
                "display": "Focal epilepsy"
            },
            "Combined": {
                "system": "http://snomed.info/sct",
                "code": "84757009",
                "display": "Epilepsy"
            },
            "Unknown": {
                "system": "http://snomed.info/sct",
                "code": "84757009",
                "display": "Epilepsy"
            }
        }
        
        # Map severity levels
        severity_codes = {
            "Mild": {
                "system": "http://snomed.info/sct",
                "code": "255604002",
                "display": "Mild"
            },
            "Moderate": {
                "system": "http://snomed.info/sct",
                "code": "6736007",
                "display": "Moderate"
            },
            "Severe": {
                "system": "http://snomed.info/sct",
                "code": "24484000",
                "display": "Severe"
            },
            "Refractory": {
                "system": "http://snomed.info/sct",
                "code": "30745007",
                "display": "Drug-resistant epilepsy"
            },
            "Unknown": {
                "system": "http://snomed.info/sct",
                "code": "261665006",
                "display": "Unknown"
            }
        }
        
        epilepsy_type = diagnosis.epilepsy_type.value if diagnosis.epilepsy_type else "Unknown"
        severity_level = diagnosis.severity_level.value if diagnosis.severity_level else "Unknown"
        
        fhir_condition = {
            "resourceType": "Condition",
            "id": diagnosis.diagnosis_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": diagnosis.updated_at.isoformat() if diagnosis.updated_at else datetime.now().isoformat(),
                "profile": [f"{self.base_url}/StructureDefinition/EpilepsyCondition"]
            },
            "clinicalStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active"
                    }
                ]
            },
            "verificationStatus": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                            "code": "encounter-diagnosis",
                            "display": "Encounter Diagnosis"
                        }
                    ]
                }
            ],
            "severity": {
                "coding": [severity_codes.get(severity_level, severity_codes["Unknown"])]
            },
            "code": {
                "coding": [epilepsy_codes.get(epilepsy_type, epilepsy_codes["Unknown"])],
                "text": f"{epilepsy_type} Epilepsy"
            },
            "subject": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.demographics.full_name
            },
            "onsetAge": {
                "value": diagnosis.age_at_onset,
                "unit": "years",
                "system": "http://unitsofmeasure.org",
                "code": "a"
            } if diagnosis.age_at_onset else None,
            "recordedDate": diagnosis.diagnosis_date.isoformat() if diagnosis.diagnosis_date else None,
            "recorder": {
                "display": diagnosis.diagnosing_physician
            } if diagnosis.diagnosing_physician else None,
            "note": []
        }
        
        # Add notes for additional information
        if diagnosis.etiology:
            fhir_condition["note"].append({
                "text": f"Etiology: {diagnosis.etiology}"
            })
        
        if diagnosis.eeg_findings:
            fhir_condition["note"].append({
                "text": f"EEG Findings: {diagnosis.eeg_findings}"
            })
        
        if diagnosis.mri_findings:
            fhir_condition["note"].append({
                "text": f"MRI Findings: {diagnosis.mri_findings}"
            })
        
        return fhir_condition
    
    def generate_observation_resource(self, patient: Patient, seizure_event: SeizureEvent) -> Dict[str, Any]:
        """Generate FHIR Observation resource for seizure event"""
        
        # Map seizure types to SNOMED codes
        seizure_codes = {
            "Generalized Tonic-Clonic": {
                "system": "http://snomed.info/sct",
                "code": "54200006",
                "display": "Generalized tonic-clonic seizure"
            },
            "Absence": {
                "system": "http://snomed.info/sct",
                "code": "25064002",
                "display": "Absence seizure"
            },
            "Myoclonic": {
                "system": "http://snomed.info/sct",
                "code": "91175000",
                "display": "Myoclonic seizure"
            },
            "Atonic": {
                "system": "http://snomed.info/sct",
                "code": "91138005",
                "display": "Atonic seizure"
            },
            "Focal Aware": {
                "system": "http://snomed.info/sct",
                "code": "230401003",
                "display": "Focal aware seizure"
            },
            "Focal Impaired Awareness": {
                "system": "http://snomed.info/sct",
                "code": "230402005",
                "display": "Focal impaired awareness seizure"
            },
            "Focal to Bilateral Tonic-Clonic": {
                "system": "http://snomed.info/sct",
                "code": "230403000",
                "display": "Focal to bilateral tonic-clonic seizure"
            }
        }
        
        seizure_type = seizure_event.seizure_type.value if seizure_event.seizure_type else "Unknown"
        
        fhir_observation = {
            "resourceType": "Observation",
            "id": seizure_event.event_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": seizure_event.created_at.isoformat() if seizure_event.created_at else datetime.now().isoformat(),
                "profile": [f"{self.base_url}/StructureDefinition/SeizureObservation"]
            },
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "survey",
                            "display": "Survey"
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "91175000",
                        "display": "Seizure"
                    }
                ],
                "text": "Seizure Event"
            },
            "subject": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.demographics.full_name
            },
            "effectiveDateTime": seizure_event.seizure_date.isoformat() if seizure_event.seizure_date else None,
            "valueCodeableConcept": {
                "coding": [seizure_codes.get(seizure_type, {
                    "system": "http://snomed.info/sct",
                    "code": "91175000",
                    "display": "Seizure"
                })],
                "text": seizure_type
            },
            "component": []
        }
        
        # Add duration component
        if seizure_event.duration_minutes:
            fhir_observation["component"].append({
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "72133-2",
                            "display": "Duration"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": seizure_event.duration_minutes,
                    "unit": "minutes",
                    "system": "http://unitsofmeasure.org",
                    "code": "min"
                }
            })
        
        # Add severity component
        if seizure_event.severity:
            fhir_observation["component"].append({
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "72514-3",
                            "display": "Severity"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": seizure_event.severity,
                    "unit": "score",
                    "system": "http://unitsofmeasure.org",
                    "code": "1"
                }
            })
        
        # Add stress level component
        if seizure_event.stress_level:
            fhir_observation["component"].append({
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "72133-2",
                            "display": "Stress Level"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": seizure_event.stress_level,
                    "unit": "score",
                    "system": "http://unitsofmeasure.org",
                    "code": "1"
                }
            })
        
        # Add notes for additional information
        if seizure_event.triggers or seizure_event.notes:
            notes = []
            if seizure_event.triggers:
                notes.append(f"Triggers: {', '.join(seizure_event.triggers)}")
            if seizure_event.notes:
                notes.append(f"Notes: {seizure_event.notes}")
            
            fhir_observation["note"] = [{"text": "; ".join(notes)}]
        
        return fhir_observation
    
    def generate_medication_request_resource(self, patient: Patient, prescription: MedicationPrescription) -> Dict[str, Any]:
        """Generate FHIR MedicationRequest resource"""
        
        fhir_medication_request = {
            "resourceType": "MedicationRequest",
            "id": prescription.prescription_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": prescription.updated_at.isoformat() if prescription.updated_at else datetime.now().isoformat(),
                "profile": [f"{self.base_url}/StructureDefinition/EpilepsyMedicationRequest"]
            },
            "status": "active" if prescription.status.value == "Active" else "stopped",
            "intent": "order",
            "medicationCodeableConcept": {
                "text": prescription.medication_id  # This would normally be a proper medication code
            },
            "subject": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.demographics.full_name
            },
            "authoredOn": prescription.prescription_date.isoformat() if prescription.prescription_date else None,
            "requester": {
                "display": prescription.prescribing_physician
            },
            "dosageInstruction": [
                {
                    "text": f"{prescription.dosage} {prescription.frequency}",
                    "route": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "26643006",
                                "display": "Oral route"
                            }
                        ]
                    },
                    "doseAndRate": [
                        {
                            "doseQuantity": {
                                "value": prescription.dosage,
                                "unit": "mg",
                                "system": "http://unitsofmeasure.org",
                                "code": "mg"
                            }
                        }
                    ]
                }
            ],
            "dispenseRequest": {
                "numberOfRepeatsAllowed": prescription.refills_remaining,
                "quantity": {
                    "value": 30,  # Default 30-day supply
                    "unit": "tablets",
                    "system": "http://terminology.hl7.org/CodeSystem/v3-orderableDrugForm",
                    "code": "TAB"
                }
            }
        }
        
        # Add indication
        if prescription.indication:
            fhir_medication_request["reasonCode"] = [
                {
                    "text": prescription.indication
                }
            ]
        
        # Add notes
        if prescription.instructions:
            fhir_medication_request["note"] = [
                {
                    "text": prescription.instructions
                }
            ]
        
        return fhir_medication_request
    
    def generate_care_plan_resource(self, patient: Patient, treatment_plan: TreatmentPlan) -> Dict[str, Any]:
        """Generate FHIR CarePlan resource"""
        
        fhir_care_plan = {
            "resourceType": "CarePlan",
            "id": treatment_plan.plan_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": treatment_plan.updated_at.isoformat() if treatment_plan.updated_at else datetime.now().isoformat(),
                "profile": [f"{self.base_url}/StructureDefinition/EpilepsyCarePlan"]
            },
            "status": "active",
            "intent": "plan",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/careplan-category",
                            "code": "assess-plan",
                            "display": "Assessment and Plan of Treatment"
                        }
                    ]
                }
            ],
            "title": "Epilepsy Treatment Plan",
            "description": "Comprehensive treatment plan for epilepsy management",
            "subject": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.demographics.full_name
            },
            "period": {
                "start": treatment_plan.plan_date.isoformat() if treatment_plan.plan_date else None
            },
            "author": {
                "display": treatment_plan.treating_physician
            },
            "goal": [],
            "activity": []
        }
        
        # Add goals
        for goal in treatment_plan.treatment_goals:
            fhir_care_plan["goal"].append({
                "reference": f"Goal/{uuid.uuid4()}",
                "display": goal
            })
        
        # Add activities for current medications
        for medication in treatment_plan.current_medications:
            fhir_care_plan["activity"].append({
                "detail": {
                    "category": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/careplan-activity-category",
                                "code": "drug",
                                "display": "Drug"
                            }
                        ]
                    },
                    "code": {
                        "text": medication
                    },
                    "status": "in-progress"
                }
            })
        
        # Add activities for planned medications
        for medication in treatment_plan.planned_medications:
            fhir_care_plan["activity"].append({
                "detail": {
                    "category": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/careplan-activity-category",
                                "code": "drug",
                                "display": "Drug"
                            }
                        ]
                    },
                    "code": {
                        "text": medication
                    },
                    "status": "not-started"
                }
            })
        
        # Add notes
        if treatment_plan.notes:
            fhir_care_plan["note"] = [
                {
                    "text": treatment_plan.notes
                }
            ]
        
        return fhir_care_plan
    
    def generate_bundle_resource(self, patient: Patient) -> Dict[str, Any]:
        """Generate FHIR Bundle containing all patient resources"""
        
        entries = []
        
        # Add patient resource
        patient_resource = self.generate_patient_resource(patient)
        entries.append({
            "fullUrl": f"{self.base_url}/Patient/{patient.patient_id}",
            "resource": patient_resource
        })
        
        # Add condition resource if diagnosis exists
        if patient.diagnosis:
            condition_resource = self.generate_condition_resource(patient, patient.diagnosis)
            entries.append({
                "fullUrl": f"{self.base_url}/Condition/{patient.diagnosis.diagnosis_id}",
                "resource": condition_resource
            })
        
        # Add observation resources for seizure events
        for seizure_event in patient.seizure_events:
            observation_resource = self.generate_observation_resource(patient, seizure_event)
            entries.append({
                "fullUrl": f"{self.base_url}/Observation/{seizure_event.event_id}",
                "resource": observation_resource
            })
        
        fhir_bundle = {
            "resourceType": "Bundle",
            "id": f"patient-{patient.patient_id}-bundle",
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat(),
                "profile": [f"{self.base_url}/StructureDefinition/EpilepsyBundle"]
            },
            "type": "collection",
            "timestamp": datetime.now().isoformat(),
            "total": len(entries),
            "entry": entries
        }
        
        return fhir_bundle
    
    def export_to_fhir_json(self, patient: Patient, filename: str = None) -> str:
        """Export patient data as FHIR JSON bundle"""
        
        if filename is None:
            filename = f"fhir_patient_{patient.patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        bundle = self.generate_bundle_resource(patient)
        
        with open(filename, 'w') as f:
            json.dump(bundle, f, indent=2, default=str)
        
        return filename

# Global FHIR resource generator instance
fhir_generator = FHIRResourceGenerator()
