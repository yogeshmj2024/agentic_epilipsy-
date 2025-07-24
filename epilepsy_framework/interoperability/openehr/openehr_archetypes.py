"""
OpenEHR Framework implementation for Epilepsy Patient Data
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from models.patient import Patient, EpilepsyDiagnosis, SeizureEvent
from models.treatment import TreatmentPlan
import uuid

@dataclass
class OpenEHRComposition:
    """OpenEHR Composition structure"""
    uid: str
    archetype_node_id: str
    name: str
    language: str
    territory: str
    category: str
    composer: str
    context: Dict[str, Any]
    content: List[Dict[str, Any]]
    
class OpenEHRGenerator:
    """Generate OpenEHR-compliant archetypes for epilepsy data"""
    
    def __init__(self):
        self.base_url = "https://epilepsy-framework.org/openehr"
        self.territory = "US"
        self.language = "en"
        
    def create_patient_summary_composition(self, patient: Patient) -> OpenEHRComposition:
        """Create OpenEHR composition for patient summary"""
        
        composition_uid = str(uuid.uuid4())
        
        # Context
        context = {
            "start_time": datetime.now().isoformat(),
            "setting": {
                "value": "primary medical care",
                "defining_code": {
                    "terminology_id": "openehr",
                    "code_string": "228"
                }
            },
            "health_care_facility": {
                "name": "Epilepsy Framework System"
            }
        }
        
        # Content - Patient demographics
        content = []
        
        # Administrative entry for patient demographics
        demographics_entry = {
            "archetype_node_id": "openEHR-EHR-ADMIN_ENTRY.person_data.v0",
            "name": {
                "value": "Person data"
            },
            "data": {
                "archetype_node_id": "at0001",
                "name": {
                    "value": "Person data"
                },
                "items": [
                    {
                        "archetype_node_id": "at0002",
                        "name": {
                            "value": "Name"
                        },
                        "value": {
                            "value": patient.demographics.full_name
                        }
                    },
                    {
                        "archetype_node_id": "at0003",
                        "name": {
                            "value": "Date of birth"
                        },
                        "value": {
                            "value": patient.demographics.date_of_birth.isoformat() if patient.demographics.date_of_birth else None
                        }
                    },
                    {
                        "archetype_node_id": "at0004",
                        "name": {
                            "value": "Gender"
                        },
                        "value": {
                            "value": patient.demographics.gender.value if patient.demographics.gender else "unknown",
                            "defining_code": {
                                "terminology_id": "local",
                                "code_string": "at0005"
                            }
                        }
                    }
                ]
            }
        }
        content.append(demographics_entry)
        
        # Evaluation entry for epilepsy diagnosis
        if patient.diagnosis:
            diagnosis_entry = {
                "archetype_node_id": "openEHR-EHR-EVALUATION.problem_diagnosis.v1",
                "name": {
                    "value": "Problem/Diagnosis"
                },
                "data": {
                    "archetype_node_id": "at0001",
                    "name": {
                        "value": "structure"
                    },
                    "items": [
                        {
                            "archetype_node_id": "at0002",
                            "name": {
                                "value": "Problem/Diagnosis name"
                            },
                            "value": {
                                "value": "Epilepsy",
                                "defining_code": {
                                    "terminology_id": "SNOMED-CT",
                                    "code_string": "84757009"
                                }
                            }
                        },
                        {
                            "archetype_node_id": "at0009",
                            "name": {
                                "value": "Clinical description"
                            },
                            "value": {
                                "value": f"{patient.diagnosis.epilepsy_type.value} epilepsy, {patient.diagnosis.severity_level.value} severity" if patient.diagnosis.epilepsy_type and patient.diagnosis.severity_level else "Epilepsy"
                            }
                        },
                        {
                            "archetype_node_id": "at0012",
                            "name": {
                                "value": "Date/time of onset"
                            },
                            "value": {
                                "value": patient.diagnosis.diagnosis_date.isoformat() if patient.diagnosis.diagnosis_date else None
                            }
                        },
                        {
                            "archetype_node_id": "at0077",
                            "name": {
                                "value": "Episodicity"
                            },
                            "value": {
                                "value": "Ongoing episode",
                                "defining_code": {
                                    "terminology_id": "local",
                                    "code_string": "at0078"
                                }
                            }
                        }
                    ]
                }
            }
            content.append(diagnosis_entry)
        
        # Observation entries for seizure events
        for seizure_event in patient.seizure_events[-5:]:  # Last 5 events
            seizure_entry = {
                "archetype_node_id": "openEHR-EHR-OBSERVATION.seizure_event.v0",
                "name": {
                    "value": "Seizure event"
                },
                "data": {
                    "archetype_node_id": "at0001",
                    "name": {
                        "value": "Event Series"
                    },
                    "events": [
                        {
                            "archetype_node_id": "at0002",
                            "name": {
                                "value": "Any event"
                            },
                            "time": {
                                "value": seizure_event.seizure_date.isoformat() if seizure_event.seizure_date else None
                            },
                            "data": {
                                "archetype_node_id": "at0003",
                                "name": {
                                    "value": "Tree"
                                },
                                "items": [
                                    {
                                        "archetype_node_id": "at0004",
                                        "name": {
                                            "value": "Seizure type"
                                        },
                                        "value": {
                                            "value": seizure_event.seizure_type.value if seizure_event.seizure_type else "Unknown",
                                            "defining_code": {
                                                "terminology_id": "local",
                                                "code_string": "at0005"
                                            }
                                        }
                                    },
                                    {
                                        "archetype_node_id": "at0006",
                                        "name": {
                                            "value": "Duration"
                                        },
                                        "value": {
                                            "magnitude": seizure_event.duration_minutes,
                                            "units": "min"
                                        }
                                    } if seizure_event.duration_minutes else None,
                                    {
                                        "archetype_node_id": "at0007",
                                        "name": {
                                            "value": "Severity"
                                        },
                                        "value": {
                                            "magnitude": seizure_event.severity,
                                            "units": "1"
                                        }
                                    } if seizure_event.severity else None
                                ]
                            }
                        }
                    ]
                }
            }
            # Remove None items
            seizure_entry["data"]["events"][0]["data"]["items"] = [
                item for item in seizure_entry["data"]["events"][0]["data"]["items"] 
                if item is not None
            ]
            content.append(seizure_entry)
        
        return OpenEHRComposition(
            uid=composition_uid,
            archetype_node_id="openEHR-EHR-COMPOSITION.health_summary.v1",
            name="Epilepsy Patient Summary",
            language=self.language,
            territory=self.territory,
            category="persistent",
            composer="Epilepsy Framework System",
            context=context,
            content=content
        )
    
    def create_seizure_observation_archetype(self, seizure_event: SeizureEvent) -> Dict[str, Any]:
        """Create OpenEHR observation archetype for seizure event"""
        
        archetype = {
            "archetype_id": {
                "value": "openEHR-EHR-OBSERVATION.seizure_event.v1"
            },
            "concept": {
                "value": "Seizure event observation"
            },
            "language": {
                "value": self.language
            },
            "definition": {
                "rm_type_name": "OBSERVATION",
                "node_id": "at0000",
                "attributes": [
                    {
                        "rm_attribute_name": "data",
                        "children": [
                            {
                                "rm_type_name": "HISTORY",
                                "node_id": "at0001",
                                "attributes": [
                                    {
                                        "rm_attribute_name": "events",
                                        "children": [
                                            {
                                                "rm_type_name": "EVENT",
                                                "node_id": "at0002",
                                                "attributes": [
                                                    {
                                                        "rm_attribute_name": "data",
                                                        "children": [
                                                            {
                                                                "rm_type_name": "ITEM_TREE",
                                                                "node_id": "at0003",
                                                                "attributes": [
                                                                    {
                                                                        "rm_attribute_name": "items",
                                                                        "children": [
                                                                            {
                                                                                "rm_type_name": "ELEMENT",
                                                                                "node_id": "at0004",
                                                                                "attributes": [
                                                                                    {
                                                                                        "rm_attribute_name": "value",
                                                                                        "children": [
                                                                                            {
                                                                                                "rm_type_name": "DV_CODED_TEXT",
                                                                                                "node_id": "at0005"
                                                                                            }
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "terminology": {
                "term_definitions": {
                    self.language: {
                        "at0000": {
                            "text": "Seizure event",
                            "description": "Observation of a seizure event"
                        },
                        "at0001": {
                            "text": "Event Series",
                            "description": "@ internal @"
                        },
                        "at0002": {
                            "text": "Any event",
                            "description": "Default, unspecified point in time or interval event"
                        },
                        "at0003": {
                            "text": "Tree",
                            "description": "@ internal @"
                        },
                        "at0004": {
                            "text": "Seizure type",
                            "description": "Type of seizure observed"
                        },
                        "at0005": {
                            "text": "Seizure type value",
                            "description": "Specific seizure type"
                        }
                    }
                }
            }
        }
        
        return archetype
    
    def create_medication_archetype(self, medication_name: str, dosage: str, frequency: str) -> Dict[str, Any]:
        """Create OpenEHR medication archetype"""
        
        archetype = {
            "archetype_id": {
                "value": "openEHR-EHR-INSTRUCTION.medication_order.v2"
            },
            "concept": {
                "value": "Medication order"
            },
            "language": {
                "value": self.language
            },
            "definition": {
                "rm_type_name": "INSTRUCTION",
                "node_id": "at0000",
                "attributes": [
                    {
                        "rm_attribute_name": "activities",
                        "children": [
                            {
                                "rm_type_name": "ACTIVITY",
                                "node_id": "at0001",
                                "attributes": [
                                    {
                                        "rm_attribute_name": "description",
                                        "children": [
                                            {
                                                "rm_type_name": "ITEM_TREE",
                                                "node_id": "at0002",
                                                "attributes": [
                                                    {
                                                        "rm_attribute_name": "items",
                                                        "children": [
                                                            {
                                                                "rm_type_name": "ELEMENT",
                                                                "node_id": "at0003",
                                                                "attributes": [
                                                                    {
                                                                        "rm_attribute_name": "value",
                                                                        "children": [
                                                                            {
                                                                                "rm_type_name": "DV_TEXT",
                                                                                "node_id": "at0004"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "terminology": {
                "term_definitions": {
                    self.language: {
                        "at0000": {
                            "text": "Medication order",
                            "description": "Details of a medicine, vaccine or other therapeutic good with instructions for use"
                        },
                        "at0001": {
                            "text": "Order",
                            "description": "Order details"
                        },
                        "at0002": {
                            "text": "Tree",
                            "description": "@ internal @"
                        },
                        "at0003": {
                            "text": "Medication item",
                            "description": "Name of the medication, vaccine or other therapeutic good"
                        },
                        "at0004": {
                            "text": "Medication name",
                            "description": "Medication name"
                        }
                    }
                }
            }
        }
        
        return archetype
    
    def export_to_openehr_json(self, patient: Patient, filename: str = None) -> str:
        """Export patient data as OpenEHR JSON"""
        
        if filename is None:
            filename = f"openehr_patient_{patient.patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        composition = self.create_patient_summary_composition(patient)
        
        # Convert composition to dictionary
        composition_dict = {
            "uid": composition.uid,
            "archetype_node_id": composition.archetype_node_id,
            "name": {
                "value": composition.name
            },
            "language": {
                "terminology_id": "ISO_639-1",
                "code_string": composition.language
            },
            "territory": {
                "terminology_id": "ISO_3166-1",
                "code_string": composition.territory
            },
            "category": {
                "value": composition.category,
                "defining_code": {
                    "terminology_id": "openehr",
                    "code_string": "433"
                }
            },
            "composer": {
                "name": composition.composer
            },
            "context": composition.context,
            "content": composition.content
        }
        
        with open(filename, 'w') as f:
            json.dump(composition_dict, f, indent=2, default=str)
        
        return filename

# Global OpenEHR generator instance
openehr_generator = OpenEHRGenerator()
