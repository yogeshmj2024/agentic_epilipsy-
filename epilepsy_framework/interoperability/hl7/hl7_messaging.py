"""
HL7 (Health Level Seven International) messaging implementation for Epilepsy Framework
"""
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass
from models.patient import Patient, PatientDemographics, EpilepsyDiagnosis, SeizureEvent, Gender
from models.treatment import TreatmentPlan, MedicationPrescription
import logging

@dataclass
class HL7Segment:
    segment_name: str
    fields: List[str]

    def format(self) -> str:
        """Format the segment as an HL7 string"""
        return f"{self.segment_name}|{ '|'.join(self.fields) }"

class HL7Message:
    """HL7 Message for patient information"""
    
    def __init__(self):
        self.segments: List[HL7Segment] = []

    def add_segment(self, segment: HL7Segment):
        self.segments.append(segment)
        
    def to_string(self) -> str:
        """Compile all segments into an HL7 message"""
        return '\n'.join(segment.format() for segment in self.segments)

class HL7MessageBuilder:
    """
    Build HL7 messages from patient and treatment data
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def build_patient_message(self, patient: Patient) -> HL7Message:
        msg = HL7Message()
        
        # PID segment
        pid_fields = [
            "1",  # Set Identifier
            patient.patient_id,  # Patient Identifier List
            "",  # Alternate Patient ID
            f"{patient.demographics.last_name}^{patient.demographics.first_name}",  # Patient Name
            "",  # Mother's Maiden Name
            patient.demographics.date_of_birth.strftime("%Y%m%d") if patient.demographics.date_of_birth else "",  # Date/Time of Birth
            patient.demographics.gender.value if patient.demographics.gender else "U",  # Administrative Sex
            "",  # Patient Alias
            f"{patient.demographics.race}^{patient.demographics.ethnicity}",  # Race
            "",  # Patient Address
            patient.demographics.phone_number,  # Phone Number - Home
            "",  # Phone Number - Business
            "",  # Primary Language
            "",  # Marital Status
            "",  # Religion
            "",  # Patient Account Number
            patient.demographics.ssn if patient.demographics.ssn else "",  # SSN Number - Patient
            ""  # Driver's License Number
        ]
        msg.add_segment(HL7Segment("PID", pid_fields))

        self.logger.info("HL7 PID segment generated for patient %s", patient.patient_id)

        return msg


# Global HL7 message builder instance
hl7_builder = HL7MessageBuilder()

# Example usage
if __name__ == '__main__':
    example_patient = Patient(
        demographics=PatientDemographics(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1985, 4, 23),
            gender=Gender.MALE
        )
    )
    hl7_message = hl7_builder.build_patient_message(example_patient)
    print(hl7_message.to_string())

