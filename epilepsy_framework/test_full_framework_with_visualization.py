import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Mock data for demonstration

mock_data = {
    'PatientID': [1, 2, 3],
    'Condition': ['Epilepsy', 'Epilepsy', 'Epilepsy'],
    'SeizureFrequency': [5, 3, 8],
    'Medication': ['med1', 'med2', 'med3'],
    'CarePlan': ['PlanA', 'PlanB', 'PlanC']
}

df = pd.DataFrame(mock_data)

# Display the data
print("Patient Data:")
print(df)

# Visualization
sns.set(style='whitegrid')

fig, axs = plt.subplots(2, 2, figsize=(16, 10))

# Seizure Frequency Distribution
sns.histplot(df['SeizureFrequency'], bins=10, ax=axs[0, 0])
axs[0, 0].set_title('Seizure Frequency Distribution')

# Medication distribution
sns.countplot(x='Medication', data=df, ax=axs[0, 1])
axs[0, 1].set_title('Medication Distribution')

# CarePlan distribution
sns.countplot(x='CarePlan', data=df, ax=axs[1, 0])
axs[1, 0].set_title('Care Plan Distribution')

# Seizure Frequency by Medication
sns.boxplot(x='Medication', y='SeizureFrequency', data=df, ax=axs[1, 1])
axs[1, 1].set_title('Seizure Frequency by Medication')

plt.tight_layout()
plt.show()
