import csv
import random
from datetime import datetime, timedelta

# Constants
diseases = ["Epilepsy", "Migraine", "Parkinson's Disease"]
severities = ["Mild", "Moderate", "Severe"]
medications = ["Levetiracetam", "Lamotrigine", "Valproic Acid"]

# Generate random patient data
def generate_patient_data(num_records=100):
    patient_data = []
    for _ in range(num_records):
        patient = {
            "patient_id": random.randint(1000, 9999),
            "patient_name": f"Patient_{random.randint(1000, 9999)}",
            "age": random.randint(10, 90),
            "gender": random.choice(["Male", "Female"]),
            "disease": random.choice(diseases),
            "seizure_frequency": random.randint(0, 20),
            "seizure_duration": random.uniform(0.1, 10.0),
            "severity": random.choice(severities),
            "medication": random.choice(medications),
            "treatment_outcome": random.choice(["Improved", "Stable", "Worsened"]),
            "record_date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        }
        patient_data.append(patient)
    return patient_data

# Write dataset to CSV
def write_patient_data_to_csv(patient_data, filename="patient_data.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=patient_data[0].keys())
        writer.writeheader()
        writer.writerows(patient_data)


if __name__ == "__main__":
    data = generate_patient_data()
    write_patient_data_to_csv(data)
