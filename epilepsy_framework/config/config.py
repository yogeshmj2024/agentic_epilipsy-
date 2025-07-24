"""
Configuration settings for the Epilepsy Public Health Informatics Framework
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    db_path: str = "data/epilepsy_db.sqlite"
    backup_path: str = "data/backups/"
    
@dataclass
class LoggingConfig:
    """Logging configuration settings"""
    log_level: str = "INFO"
    log_file: str = "logs/epilepsy_framework.log"
    max_log_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class AnalyticsConfig:
    """Analytics and reporting configuration"""
    reports_path: str = "reports/"
    chart_output_path: str = "reports/charts/"
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['pdf', 'csv', 'json']

@dataclass
class EpilepsyConfig:
    """Epilepsy-specific configuration"""
    seizure_types: List[str] = None
    medication_categories: List[str] = None
    severity_levels: List[str] = None
    
    def __post_init__(self):
        if self.seizure_types is None:
            self.seizure_types = [
                'Generalized Tonic-Clonic',
                'Absence',
                'Myoclonic',
                'Atonic',
                'Focal Aware',
                'Focal Impaired Awareness',
                'Focal to Bilateral Tonic-Clonic'
            ]
        
        if self.medication_categories is None:
            self.medication_categories = [
                'Anticonvulsants',
                'Benzodiazepines',
                'Barbiturates',
                'Carbonic Anhydrase Inhibitors',
                'GABA Analogs',
                'Sodium Channel Blockers',
                'Calcium Channel Blockers'
            ]
        
        if self.severity_levels is None:
            self.severity_levels = ['Mild', 'Moderate', 'Severe', 'Refractory']

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        self.analytics = AnalyticsConfig()
        self.epilepsy = EpilepsyConfig()
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.base_dir / "data",
            self.base_dir / "data/backups",
            self.base_dir / "logs",
            self.base_dir / "reports",
            self.base_dir / "reports/charts"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_db_path(self) -> str:
        """Get the full database path"""
        return str(self.base_dir / self.database.db_path)
    
    def get_log_path(self) -> str:
        """Get the full log file path"""
        return str(self.base_dir / self.logging.log_file)

# Global configuration instance
config = Config()
