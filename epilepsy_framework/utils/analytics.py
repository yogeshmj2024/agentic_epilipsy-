"""
Analytics utilities for the Epilepsy Public Health Informatics Framework
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from models.patient import Patient, SeizureEvent
from models.treatment import TreatmentOutcome, MedicationAdherence

logging.basicConfig(level=logging.INFO)

class EpilepsyAnalytics:
    """Analytics class for epilepsy data analysis"""
    
    def __init__(self):
        """Initialize analytics utility"""
        self.logger = logging.getLogger(__name__)
        # Use a compatible style
        try:
            plt.style.use('seaborn')
        except:
            # Fallback to default style
            plt.style.use('default')
        
    def calculate_seizure_frequency(self, patient: Patient, days: int = 30) -> Dict[str, float]:
        """
        Calculate seizure frequency for a patient
        
        Args:
            patient: Patient object
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dictionary with frequency metrics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        seizures = patient.get_seizure_events_by_date_range(start_date, end_date)
        
        total_seizures = len(seizures)
        frequency_per_day = total_seizures / days
        frequency_per_week = frequency_per_day * 7
        frequency_per_month = frequency_per_day * 30
        
        return {
            'total_seizures': total_seizures,
            'frequency_per_day': frequency_per_day,
            'frequency_per_week': frequency_per_week,
            'frequency_per_month': frequency_per_month,
            'analysis_period_days': days
        }
    
    def analyze_seizure_patterns(self, patient: Patient) -> Dict[str, any]:
        """
        Analyze seizure patterns for a patient
        
        Args:
            patient: Patient object
            
        Returns:
            Dictionary with pattern analysis
        """
        if not patient.seizure_events:
            return {'error': 'No seizure events found for analysis'}
        
        # Convert to DataFrame for analysis
        data = []
        for event in patient.seizure_events:
            if event.seizure_date:
                data.append({
                    'date': event.seizure_date,
                    'type': event.seizure_type.value if event.seizure_type else 'Unknown',
                    'duration': event.duration_minutes,
                    'severity': event.severity,
                    'hour': event.seizure_date.hour,
                    'day_of_week': event.seizure_date.weekday(),
                    'month': event.seizure_date.month,
                    'stress_level': event.stress_level,
                    'sleep_hours': event.sleep_hours
                })
        
        if not data:
            return {'error': 'No valid seizure events with dates found'}
        
        df = pd.DataFrame(data)
        
        # Analysis results
        analysis = {
            'total_events': len(df),
            'date_range': {
                'start': df['date'].min(),
                'end': df['date'].max()
            },
            'seizure_types': df['type'].value_counts().to_dict(),
            'average_duration': df['duration'].mean() if df['duration'].notna().any() else None,
            'average_severity': df['severity'].mean() if df['severity'].notna().any() else None,
            'hourly_pattern': df['hour'].value_counts().to_dict(),
            'day_of_week_pattern': df['day_of_week'].value_counts().to_dict(),
            'monthly_pattern': df['month'].value_counts().to_dict(),
            'stress_correlation': df[['stress_level', 'severity']].corr().iloc[0, 1] if df['stress_level'].notna().any() and df['severity'].notna().any() else None
        }
        
        return analysis
    
    def generate_seizure_calendar(self, patient: Patient, year: int = None) -> pd.DataFrame:
        """
        Generate a calendar view of seizures
        
        Args:
            patient: Patient object
            year: Year to analyze (default: current year)
            
        Returns:
            DataFrame with calendar data
        """
        if year is None:
            year = datetime.now().year
        
        # Create date range for the year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        seizures = patient.get_seizure_events_by_date_range(start_date, end_date)
        
        # Create calendar DataFrame
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        calendar_df = pd.DataFrame(index=date_range)
        calendar_df['seizure_count'] = 0
        calendar_df['total_duration'] = 0
        calendar_df['max_severity'] = 0
        
        for event in seizures:
            if event.seizure_date:
                date = event.seizure_date.date()
                if date in calendar_df.index:
                    calendar_df.loc[date, 'seizure_count'] += 1
                    if event.duration_minutes:
                        calendar_df.loc[date, 'total_duration'] += event.duration_minutes
                    if event.severity:
                        calendar_df.loc[date, 'max_severity'] = max(
                            calendar_df.loc[date, 'max_severity'], 
                            event.severity
                        )
        
        return calendar_df
    
    def plot_seizure_frequency_trend(self, patient: Patient, days: int = 90) -> plt.Figure:
        """
        Plot seizure frequency trend over time
        
        Args:
            patient: Patient object
            days: Number of days to plot
            
        Returns:
            Matplotlib figure
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        seizures = patient.get_seizure_events_by_date_range(start_date, end_date)
        
        if not seizures:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No seizure data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'Seizure Frequency Trend - {patient.demographics.full_name}')
            return fig
        
        # Create daily counts
        dates = [event.seizure_date.date() for event in seizures if event.seizure_date]
        daily_counts = pd.Series(dates).value_counts().sort_index()
        
        # Create complete date range
        date_range = pd.date_range(start=start_date.date(), end=end_date.date(), freq='D')
        daily_counts = daily_counts.reindex(date_range, fill_value=0)
        
        # Plot
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2, markersize=4)
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Seizures')
        ax.set_title(f'Seizure Frequency Trend - {patient.demographics.full_name}')
        ax.grid(True, alpha=0.3)
        
        # Add 7-day rolling average
        rolling_avg = daily_counts.rolling(window=7).mean()
        ax.plot(rolling_avg.index, rolling_avg.values, 
               color='red', linestyle='--', linewidth=2, label='7-day average')
        ax.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_seizure_type_distribution(self, patient: Patient) -> plt.Figure:
        """
        Plot distribution of seizure types
        
        Args:
            patient: Patient object
            
        Returns:
            Matplotlib figure
        """
        if not patient.seizure_events:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'No seizure data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'Seizure Type Distribution - {patient.demographics.full_name}')
            return fig
        
        # Count seizure types
        types = [event.seizure_type.value if event.seizure_type else 'Unknown' 
                for event in patient.seizure_events]
        type_counts = pd.Series(types).value_counts()
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(np.linspace(0, 1, len(type_counts)))
        
        wedges, texts, autotexts = ax.pie(type_counts.values, 
                                         labels=type_counts.index, 
                                         autopct='%1.1f%%',
                                         colors=colors,
                                         startangle=90)
        
        ax.set_title(f'Seizure Type Distribution - {patient.demographics.full_name}')
        
        return fig
    
    def analyze_treatment_effectiveness(self, outcomes: List[TreatmentOutcome]) -> Dict[str, any]:
        """
        Analyze treatment effectiveness from outcome data
        
        Args:
            outcomes: List of TreatmentOutcome objects
            
        Returns:
            Dictionary with effectiveness analysis
        """
        if not outcomes:
            return {'error': 'No treatment outcomes provided'}
        
        # Convert to DataFrame
        data = []
        for outcome in outcomes:
            data.append({
                'patient_id': outcome.patient_id,
                'assessment_date': outcome.assessment_date,
                'seizure_reduction': outcome.seizure_reduction_percentage,
                'quality_of_life': outcome.quality_of_life_score,
                'treatment_satisfaction': outcome.treatment_satisfaction,
                'side_effects_severity': outcome.side_effects_severity,
                'seizure_free_period': outcome.seizure_free_period,
                'overall_response': outcome.overall_treatment_response
            })
        
        df = pd.DataFrame(data)
        
        analysis = {
            'total_assessments': len(df),
            'average_seizure_reduction': df['seizure_reduction'].mean() if df['seizure_reduction'].notna().any() else None,
            'average_quality_of_life': df['quality_of_life'].mean() if df['quality_of_life'].notna().any() else None,
            'average_treatment_satisfaction': df['treatment_satisfaction'].mean() if df['treatment_satisfaction'].notna().any() else None,
            'average_side_effects_severity': df['side_effects_severity'].mean() if df['side_effects_severity'].notna().any() else None,
            'response_distribution': df['overall_response'].value_counts().to_dict() if df['overall_response'].notna().any() else None,
            'seizure_free_patients': (df['seizure_free_period'] > 0).sum() if df['seizure_free_period'].notna().any() else 0
        }
        
        return analysis
    
    def generate_patient_summary_report(self, patient: Patient) -> Dict[str, any]:
        """
        Generate a comprehensive summary report for a patient
        
        Args:
            patient: Patient object
            
        Returns:
            Dictionary with comprehensive patient summary
        """
        # Basic demographics
        demographics = {
            'name': patient.demographics.full_name,
            'age': patient.demographics.age,
            'gender': patient.demographics.gender.value if patient.demographics.gender else None,
            'patient_id': patient.patient_id
        }
        
        # Seizure analysis
        seizure_analysis = self.analyze_seizure_patterns(patient)
        frequency_30_days = self.calculate_seizure_frequency(patient, 30)
        frequency_90_days = self.calculate_seizure_frequency(patient, 90)
        
        # Diagnosis information
        diagnosis_info = {}
        if patient.diagnosis:
            diagnosis_info = {
                'epilepsy_type': patient.diagnosis.epilepsy_type.value if patient.diagnosis.epilepsy_type else None,
                'severity_level': patient.diagnosis.severity_level.value if patient.diagnosis.severity_level else None,
                'age_at_onset': patient.diagnosis.age_at_onset,
                'diagnosis_date': patient.diagnosis.diagnosis_date,
                'seizure_types': [st.value for st in patient.diagnosis.seizure_types]
            }
        
        # Compile comprehensive report
        report = {
            'demographics': demographics,
            'diagnosis': diagnosis_info,
            'seizure_analysis': seizure_analysis,
            'frequency_metrics': {
                '30_days': frequency_30_days,
                '90_days': frequency_90_days
            },
            'report_generated': datetime.now().isoformat()
        }
        
        return report

# Global analytics instance
analytics = EpilepsyAnalytics()
