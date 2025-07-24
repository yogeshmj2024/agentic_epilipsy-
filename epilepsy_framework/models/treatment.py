"""
Treatment data models for the Epilepsy Public Health Informatics Framework
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid

class MedicationStatus(Enum):
    ACTIVE = "Active"
    DISCONTINUED = "Discontinued"
    TEMPORARY_HOLD = "Temporary Hold"
    DOSE_ADJUSTMENT = "Dose Adjustment"

class TreatmentType(Enum):
    MEDICATION = "Medication"
    SURGERY = "Surgery"
    DEVICE = "Device"
    DIET = "Diet"
    THERAPY = "Therapy"
    LIFESTYLE = "Lifestyle"

class AdministrationRoute(Enum):
    ORAL = "Oral"
    INTRAVENOUS = "Intravenous"
    INTRAMUSCULAR = "Intramuscular"
    SUBCUTANEOUS = "Subcutaneous"
    RECTAL = "Rectal"
    NASAL = "Nasal"
    TOPICAL = "Topical"

class AdherenceLevel(Enum):
    EXCELLENT = "Excellent"  # >95%
    GOOD = "Good"  # 85-95%
    FAIR = "Fair"  # 70-84%
    POOR = "Poor"  # <70%

@dataclass
class Medication:
    """Medication information"""
    medication_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    generic_name: str = ""
    brand_name: Optional[str] = None
    medication_class: Optional[str] = None
    mechanism_of_action: Optional[str] = None
    therapeutic_range: Optional[str] = None
    half_life: Optional[float] = None  # Hours
    common_side_effects: List[str] = field(default_factory=list)
    serious_side_effects: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    drug_interactions: List[str] = field(default_factory=list)
    monitoring_requirements: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class MedicationPrescription:
    """Medication prescription details"""
    prescription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    medication_id: str = ""
    prescribing_physician: str = ""
    prescription_date: date = field(default_factory=date.today)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    dosage: str = ""  # e.g., "500mg"
    frequency: str = ""  # e.g., "Twice daily"
    route: AdministrationRoute = AdministrationRoute.ORAL
    duration: Optional[str] = None  # e.g., "30 days"
    refills_remaining: int = 0
    instructions: Optional[str] = None
    indication: Optional[str] = None  # Reason for prescription
    status: MedicationStatus = MedicationStatus.ACTIVE
    discontinuation_reason: Optional[str] = None
    discontinuation_date: Optional[date] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class MedicationAdherence:
    """Medication adherence tracking"""
    adherence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    prescription_id: str = ""
    assessment_date: date = field(default_factory=date.today)
    adherence_level: AdherenceLevel = AdherenceLevel.GOOD
    missed_doses_last_week: int = 0
    missed_doses_last_month: int = 0
    reasons_for_non_adherence: List[str] = field(default_factory=list)
    side_effects_experienced: List[str] = field(default_factory=list)
    patient_reported_efficacy: Optional[int] = None  # 1-10 scale
    pill_count: Optional[int] = None
    pharmacy_refill_data: Optional[str] = None
    assessment_method: str = "Self-report"  # Self-report, Pill count, Pharmacy data, etc.
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LabResult:
    """Laboratory test results"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    test_name: str = ""
    test_date: date = field(default_factory=date.today)
    result_value: str = ""
    reference_range: Optional[str] = None
    units: Optional[str] = None
    abnormal_flag: Optional[str] = None  # "High", "Low", "Critical"
    ordering_physician: Optional[str] = None
    lab_name: Optional[str] = None
    related_medication: Optional[str] = None  # If monitoring drug levels
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SurgicalTreatment:
    """Surgical treatment information"""
    surgery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    procedure_name: str = ""
    surgery_date: Optional[date] = None
    surgeon: Optional[str] = None
    hospital: Optional[str] = None
    preoperative_assessment: Optional[str] = None
    surgical_approach: Optional[str] = None
    complications: List[str] = field(default_factory=list)
    post_operative_course: Optional[str] = None
    outcome: Optional[str] = None
    seizure_freedom_achieved: Optional[bool] = None
    seizure_reduction_percentage: Optional[float] = None
    follow_up_required: bool = True
    next_follow_up_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DeviceTherapy:
    """Device-based therapy information"""
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    device_type: str = ""  # VNS, RNS, DBS, etc.
    implantation_date: Optional[date] = None
    device_model: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    battery_life: Optional[str] = None
    last_programming_date: Optional[date] = None
    programming_physician: Optional[str] = None
    efficacy_rating: Optional[int] = None  # 1-10 scale
    side_effects: List[str] = field(default_factory=list)
    device_complications: List[str] = field(default_factory=list)
    maintenance_schedule: Optional[str] = None
    next_maintenance_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class TreatmentPlan:
    """Comprehensive treatment plan"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    plan_date: date = field(default_factory=date.today)
    treating_physician: str = ""
    treatment_goals: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    planned_medications: List[str] = field(default_factory=list)
    non_pharmacological_treatments: List[str] = field(default_factory=list)
    lifestyle_modifications: List[str] = field(default_factory=list)
    monitoring_plan: List[str] = field(default_factory=list)
    emergency_plan: Optional[str] = None
    seizure_action_plan: Optional[str] = None
    target_seizure_frequency: Optional[str] = None
    quality_of_life_goals: List[str] = field(default_factory=list)
    review_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class TreatmentOutcome:
    """Treatment outcome assessment"""
    outcome_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str = ""
    assessment_date: date = field(default_factory=date.today)
    assessment_period: str = ""  # e.g., "3 months", "6 months"
    seizure_frequency_before: Optional[str] = None
    seizure_frequency_after: Optional[str] = None
    seizure_reduction_percentage: Optional[float] = None
    seizure_free_period: Optional[int] = None  # Days
    quality_of_life_score: Optional[int] = None  # 1-10 scale
    side_effects_severity: Optional[int] = None  # 1-10 scale
    treatment_satisfaction: Optional[int] = None  # 1-10 scale
    functional_improvement: Optional[str] = None
    employment_status_change: Optional[str] = None
    driving_status_change: Optional[str] = None
    social_functioning_change: Optional[str] = None
    cognitive_changes: Optional[str] = None
    mood_changes: Optional[str] = None
    overall_treatment_response: Optional[str] = None  # "Excellent", "Good", "Fair", "Poor"
    next_assessment_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
