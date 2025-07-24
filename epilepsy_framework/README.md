# Epilepsy Public Health Informatics Framework

A comprehensive Python framework for managing patient treatments and analyzing epilepsy disorders in public health settings.

## Overview

The Epilepsy Public Health Informatics Framework provides a complete solution for:
- Patient demographic and clinical data management
- Seizure event tracking and analysis
- Treatment plan management
- Medication adherence monitoring
- Statistical analysis and reporting
- Data visualization and export capabilities

## Features

### Core Functionality
- **Patient Management**: Complete patient record system with demographics, diagnosis, and medical history
- **Seizure Tracking**: Detailed seizure event logging with multiple parameters (type, duration, severity, triggers)
- **Treatment Management**: Comprehensive treatment planning including medications, surgeries, and device therapies
- **Analytics**: Advanced analytics for seizure patterns, treatment effectiveness, and population health metrics
- **Data Validation**: Robust data validation and cleaning utilities
- **Reporting**: Automated report generation with export capabilities

### Key Components

#### 1. Data Models
- **Patient**: Demographics, diagnosis, and seizure events
- **Treatment**: Medications, prescriptions, surgeries, and device therapies
- **Outcomes**: Treatment effectiveness and quality of life metrics

#### 2. Analytics Engine
- Seizure frequency analysis
- Pattern recognition (temporal, triggers, severity)
- Treatment effectiveness evaluation
- Population health statistics
- Predictive modeling capabilities

#### 3. Visualization
- Seizure frequency trends
- Treatment outcome charts
- Population health dashboards
- Calendar views of seizure events

#### 4. Data Management
- SQLite database integration
- Data validation and cleaning
- Export/import capabilities
- Backup and recovery

## Installation

### Prerequisites
- Python 3.7+
- Required packages (see requirements.txt)

### Setup
1. Clone or download the framework
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main application:
   ```bash
   python main.py
   ```

## Usage

### Basic Usage Example

```python
from main import EpilepsyFramework
from datetime import datetime, date

# Initialize framework
framework = EpilepsyFramework()

# Create a patient
patient = framework.create_patient(
    first_name="John",
    last_name="Doe",
    date_of_birth=date(1990, 5, 15),
    gender="Male"
)

# Add epilepsy diagnosis
diagnosis = framework.add_epilepsy_diagnosis(
    patient_id=patient.patient_id,
    epilepsy_type="Focal",
    severity_level="Moderate",
    age_at_onset=25
)

# Add seizure event
event = framework.add_seizure_event(
    patient_id=patient.patient_id,
    seizure_date=datetime(2024, 6, 1, 10, 30),
    seizure_type="Focal Aware",
    duration_minutes=2.5,
    severity=3
)

# Analyze seizure patterns
patterns = framework.analyze_seizure_patterns(patient.patient_id)
print(f"Total events: {patterns['total_events']}")
print(f"Average severity: {patterns['average_severity']}")

# Generate patient summary
summary = framework.get_patient_summary(patient.patient_id)

# Export data
framework.export_patient_data(patient.patient_id)
```

### Advanced Features

#### Data Validation
```python
from utils.validation import DataValidator

validator = DataValidator()
errors = validator.validate_patient_data(patient_data)
if errors:
    print(f"Validation errors: {errors}")
```

#### Analytics
```python
from utils.analytics import EpilepsyAnalytics

analytics = EpilepsyAnalytics()

# Calculate seizure frequency
frequency = analytics.calculate_seizure_frequency(patient, days=30)

# Generate visualizations
trend_plot = analytics.plot_seizure_frequency_trend(patient)
type_plot = analytics.plot_seizure_type_distribution(patient)
```

## Configuration

The framework can be configured via `config/config.py`:

- Database settings
- Logging configuration
- Analytics parameters
- Export formats
- Epilepsy-specific classifications

## File Structure

```
epilepsy_framework/
├── config/
│   └── config.py              # Configuration settings
├── models/
│   ├── patient.py             # Patient data models
│   └── treatment.py           # Treatment data models
├── services/
│   └── database_service.py    # Database operations
├── utils/
│   ├── analytics.py           # Analytics utilities
│   └── validation.py          # Data validation
├── tests/
│   └── test_framework.py      # Test suite
├── data/                      # Database and data files
├── logs/                      # Log files
├── reports/                   # Generated reports
├── main.py                    # Main application
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Data Models

### Patient Demographics
- Personal information (name, age, gender, contact)
- Insurance information
- Emergency contacts

### Epilepsy Diagnosis
- Epilepsy type (Generalized, Focal, Combined)
- Severity level (Mild, Moderate, Severe, Refractory)
- Age at onset
- Diagnostic findings (EEG, MRI, genetic testing)
- Comorbidities

### Seizure Events
- Date and time
- Seizure type (7 standard types)
- Duration and severity
- Triggers and symptoms
- Medication adherence
- Environmental factors

### Treatment Plans
- Current and planned medications
- Non-pharmacological treatments
- Lifestyle modifications
- Monitoring requirements
- Emergency plans

## Analytics Capabilities

### Seizure Analysis
- Frequency calculations (daily, weekly, monthly)
- Pattern recognition (temporal, severity, triggers)
- Seizure-free period tracking
- Correlation analysis

### Treatment Effectiveness
- Seizure reduction percentage
- Quality of life improvements
- Side effect monitoring
- Medication adherence tracking

### Population Health
- Demographic analysis
- Treatment outcome statistics
- Epidemiological trends
- Healthcare utilization patterns

## Testing

Run the comprehensive test suite:
```bash
python tests/test_framework.py
```

The test suite covers:
- Basic framework functionality
- Data validation
- Analytics capabilities
- Export/import operations

## Contributing

This framework is designed for public health informatics applications. Contributions are welcome for:
- Additional seizure types and classifications
- Enhanced analytics algorithms
- Improved visualization capabilities
- Integration with electronic health records
- Mobile application interfaces

## License

This framework is developed for educational and research purposes in public health informatics.

## Support

For questions or issues:
1. Check the test suite for usage examples
2. Review the configuration files
3. Examine the data models for field definitions
4. Test with sample data before production use

## Acknowledgments

Developed as a comprehensive solution for epilepsy public health informatics, incorporating:
- Clinical best practices for epilepsy management
- Public health surveillance requirements
- Data privacy and security considerations
- Scalable architecture for health information systems
