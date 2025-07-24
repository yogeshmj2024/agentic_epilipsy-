"""
Patient data models for the Epilepsy Public Health Informatics Framework
"""
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid

class Gender(Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer not to say"

class EpilepsyType(Enum):
    GENERALIZED = "Generalized"
    FOCAL = "Focal"
    COMBINED = "Combined"
    UNKNOWN = "Unknown"

class SeizureType(Enum):
    GENERALIZED_TONIC_CLONIC = "Generalized Tonic-Clonic"
    ABSENCE = "Absence"
    MYOCLONIC = "Myoclonic"
    ATONIC = "Atonic"
    FOCAL_AWARE = "Focal Aware"
    FOCAL_IMPAIRED_AWARENESS = "Focal Impaired Awareness"
    FOCAL_TO_BILATERAL_TONIC_CLONIC = "Focal to Bilateral Tonic-Clonic"

class SeverityLevel(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    REFRACTORY = "Refractory"

@dataclass
class PatientDemographics:
    """Patient demographic information"""
    patient_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str = ""
    last_name: str = ""
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    ethnicity: Optional[str] = None
    race: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    insurance_provider: Optional[str] = None
    insurance_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def age(self) -> Optional[int]:
        """Calculate age from date of birth"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}".strip()

@dataclass
class EpilepsyDiagnosis:
    """Epilepsy diagnosis information"""
    diagnosis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    epilepsy_type: Optional[EpilepsyType] = None
    seizure_types: List[SeizureType] = field(default_factory=list)
    severity_level: Optional[SeverityLevel] = None
    age_at_onset: Optional[int] = None
    diagnosis_date: Optional[date] = None
    diagnosing_physician: Optional[str] = None
    etiology: Optional[str] = None  # Cause of epilepsy
    seizure_frequency: Optional[str] = None  # e.g., "Daily", "Weekly", "Monthly"
    last_seizure_date: Optional[date] = None
    seizure_free_period: Optional[int] = None  # Days since last seizure
    eeg_findings: Optional[str] = None
    mri_findings: Optional[str] = None
    genetic_testing: Optional[str] = None
    comorbidities: List[str] = field(default_factory=list)
    family_history: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class SeizureEvent:
    """Individual seizure event record"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    seizure_type: Optional[SeizureType] = None
    seizure_date: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    severity: Optional[int] = None  # 1-10 scale
    triggers: List[str] = field(default_factory=list)
    symptoms_before: List[str] = field(default_factory=list)  # Aura symptoms
    symptoms_during: List[str] = field(default_factory=list)
    symptoms_after: List[str] = field(default_factory=list)  # Post-ictal symptoms
    medication_adherence: Optional[str] = None  # "Good", "Fair", "Poor"
    stress_level: Optional[int] = None  # 1-10 scale
    sleep_hours: Optional[float] = None
    alcohol_consumption: Optional[str] = None
    menstrual_cycle_day: Optional[int] = None  # For female patients
    hospitalization_required: bool = False
    emergency_medication_used: Optional[str] = None
    witnessed_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Patient:
    """Complete patient record"""
    demographics: PatientDemographics = field(default_factory=PatientDemographics)
    diagnosis: Optional[EpilepsyDiagnosis] = None
    seizure_events: List[SeizureEvent] = field(default_factory=list)
    
    @property
    def patient_id(self) -> str:
        """Get patient ID"""
        return self.demographics.patient_id
    
    @property
    def recent_seizures(self) -> List[SeizureEvent]:
        """Get seizures from the last 30 days"""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        return [
            event for event in self.seizure_events
            if event.seizure_date and event.seizure_date >= thirty_days_ago
        ]
    
    @property
    def seizure_frequency_last_month(self) -> int:
        """Get number of seizures in the last month"""
        return len(self.recent_seizures)
    
    def add_seizure_event(self, event: SeizureEvent):
        """Add a new seizure event"""
        event.patient_id = self.patient_id
        self.seizure_events.append(event)
        self.seizure_events.sort(key=lambda x: x.seizure_date or datetime.min)
    
    def get_seizure_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[SeizureEvent]:
        """Get seizure events within a date range"""
        return [
            event for event in self.seizure_events
            if event.seizure_date and start_date <= event.seizure_date <= end_date
        ]
