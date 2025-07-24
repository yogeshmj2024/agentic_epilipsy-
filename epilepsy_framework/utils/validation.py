"""
Data validation utilities for the Epilepsy Public Health Informatics Framework
"""
import re
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from models.patient import Gender, EpilepsyType, SeizureType, SeverityLevel

class DataValidator:
    """Data validation utility class"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        return len(digits) == 10 or len(digits) == 11
    
    @staticmethod
    def validate_zip_code(zip_code: str) -> bool:
        """Validate ZIP code format"""
        if not zip_code:
            return False
        # US ZIP code format: 5 digits or 5+4 digits
        pattern = r'^\d{5}(-\d{4})?$'
        return re.match(pattern, zip_code) is not None
    
    @staticmethod
    def validate_date_of_birth(dob: date) -> bool:
        """Validate date of birth (must be in the past and reasonable)"""
        if not dob:
            return False
        today = date.today()
        # Check if date is in the past
        if dob >= today:
            return False
        # Check if age is reasonable (0-120 years)
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return 0 <= age <= 120
    
    @staticmethod
    def validate_severity_scale(severity: int) -> bool:
        """Validate severity scale (1-10)"""
        if severity is None:
            return True  # Optional field
        return 1 <= severity <= 10
    
    @staticmethod
    def validate_duration(duration: float) -> bool:
        """Validate seizure duration (must be positive)"""
        if duration is None:
            return True  # Optional field
        return duration > 0
    
    @staticmethod
    def validate_age_at_onset(age: int) -> bool:
        """Validate age at onset (must be reasonable)"""
        if age is None:
            return True  # Optional field
        return 0 <= age <= 120
    
    @staticmethod
    def validate_seizure_date(seizure_date: datetime) -> bool:
        """Validate seizure date (must be in the past)"""
        if not seizure_date:
            return False
        return seizure_date <= datetime.now()
    
    @staticmethod
    def validate_patient_data(patient_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate patient data and return validation errors
        
        Args:
            patient_data: Dictionary containing patient data
            
        Returns:
            Dictionary with validation errors
        """
        errors = {}
        
        # Required fields
        if not patient_data.get('first_name'):
            errors.setdefault('first_name', []).append('First name is required')
        
        if not patient_data.get('last_name'):
            errors.setdefault('last_name', []).append('Last name is required')
        
        # Date of birth validation
        dob = patient_data.get('date_of_birth')
        if dob and not DataValidator.validate_date_of_birth(dob):
            errors.setdefault('date_of_birth', []).append('Invalid date of birth')
        
        # Email validation
        email = patient_data.get('email')
        if email and not DataValidator.validate_email(email):
            errors.setdefault('email', []).append('Invalid email format')
        
        # Phone validation
        phone = patient_data.get('phone_number')
        if phone and not DataValidator.validate_phone(phone):
            errors.setdefault('phone_number', []).append('Invalid phone number format')
        
        # ZIP code validation
        zip_code = patient_data.get('zip_code')
        if zip_code and not DataValidator.validate_zip_code(zip_code):
            errors.setdefault('zip_code', []).append('Invalid ZIP code format')
        
        # Gender validation
        gender = patient_data.get('gender')
        if gender:
            try:
                Gender(gender)
            except ValueError:
                errors.setdefault('gender', []).append('Invalid gender value')
        
        return errors
    
    @staticmethod
    def validate_seizure_event_data(event_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate seizure event data and return validation errors
        
        Args:
            event_data: Dictionary containing seizure event data
            
        Returns:
            Dictionary with validation errors
        """
        errors = {}
        
        # Required fields
        if not event_data.get('patient_id'):
            errors.setdefault('patient_id', []).append('Patient ID is required')
        
        if not event_data.get('seizure_date'):
            errors.setdefault('seizure_date', []).append('Seizure date is required')
        
        # Seizure date validation
        seizure_date = event_data.get('seizure_date')
        if seizure_date and not DataValidator.validate_seizure_date(seizure_date):
            errors.setdefault('seizure_date', []).append('Seizure date must be in the past')
        
        # Duration validation
        duration = event_data.get('duration_minutes')
        if duration and not DataValidator.validate_duration(duration):
            errors.setdefault('duration_minutes', []).append('Duration must be positive')
        
        # Severity validation
        severity = event_data.get('severity')
        if severity and not DataValidator.validate_severity_scale(severity):
            errors.setdefault('severity', []).append('Severity must be between 1 and 10')
        
        # Stress level validation
        stress_level = event_data.get('stress_level')
        if stress_level and not DataValidator.validate_severity_scale(stress_level):
            errors.setdefault('stress_level', []).append('Stress level must be between 1 and 10')
        
        # Seizure type validation
        seizure_type = event_data.get('seizure_type')
        if seizure_type:
            try:
                SeizureType(seizure_type)
            except ValueError:
                errors.setdefault('seizure_type', []).append('Invalid seizure type')
        
        return errors
    
    @staticmethod
    def validate_diagnosis_data(diagnosis_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate diagnosis data and return validation errors
        
        Args:
            diagnosis_data: Dictionary containing diagnosis data
            
        Returns:
            Dictionary with validation errors
        """
        errors = {}
        
        # Required fields
        if not diagnosis_data.get('patient_id'):
            errors.setdefault('patient_id', []).append('Patient ID is required')
        
        # Epilepsy type validation
        epilepsy_type = diagnosis_data.get('epilepsy_type')
        if epilepsy_type:
            try:
                EpilepsyType(epilepsy_type)
            except ValueError:
                errors.setdefault('epilepsy_type', []).append('Invalid epilepsy type')
        
        # Severity level validation
        severity_level = diagnosis_data.get('severity_level')
        if severity_level:
            try:
                SeverityLevel(severity_level)
            except ValueError:
                errors.setdefault('severity_level', []).append('Invalid severity level')
        
        # Age at onset validation
        age_at_onset = diagnosis_data.get('age_at_onset')
        if age_at_onset and not DataValidator.validate_age_at_onset(age_at_onset):
            errors.setdefault('age_at_onset', []).append('Age at onset must be between 0 and 120')
        
        # Diagnosis date validation
        diagnosis_date = diagnosis_data.get('diagnosis_date')
        if diagnosis_date and diagnosis_date > date.today():
            errors.setdefault('diagnosis_date', []).append('Diagnosis date cannot be in the future')
        
        return errors

class DataCleaner:
    """Data cleaning utility class"""
    
    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Clean and format phone number"""
        if not phone:
            return ""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Format as (XXX) XXX-XXXX if 10 digits, or 1-(XXX) XXX-XXXX if 11 digits
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"1-({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone  # Return original if can't format
    
    @staticmethod
    def clean_zip_code(zip_code: str) -> str:
        """Clean and format ZIP code"""
        if not zip_code:
            return ""
        # Remove all non-digit and non-dash characters
        cleaned = re.sub(r'[^\d-]', '', zip_code)
        # Format as XXXXX or XXXXX-XXXX
        if len(cleaned) == 5:
            return cleaned
        elif len(cleaned) == 9:
            return f"{cleaned[:5]}-{cleaned[5:]}"
        return zip_code  # Return original if can't format
    
    @staticmethod
    def clean_text_field(text: str) -> str:
        """Clean text field (trim whitespace, capitalize words)"""
        if not text:
            return ""
        return text.strip().title()
    
    @staticmethod
    def clean_email(email: str) -> str:
        """Clean email (lowercase, trim whitespace)"""
        if not email:
            return ""
        return email.strip().lower()

# Global instances
validator = DataValidator()
cleaner = DataCleaner()
