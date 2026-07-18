# EHR-EpSO: Semantically Intelligent Epilepsy Surveillance Framework

[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![FHIR R4](https://img.shields.io/badge/FHIR-R4--Compliant-green.svg)](https://hl7.org/fhir/R4/)
[![MIMIC-IV v3.1](https://img.shields.io/badge/Dataset-MIMIC--IV%20v3.1-orange.svg)](https://physionet.org/content/mimiciv/3.1/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An ontology-driven Electronic Health Record (EHR) informatics framework unifying the **Epilepsy and Seizure Ontology (EpSO)**, **HL7 Fast Healthcare Interoperability Resources Release 4 (FHIR R4)** standards, and a modular machine learning analytics engine (Transformer, BiLSTM, XGBoost) for population-scale neurological surveillance and predictive clinical decision support.

---

## 📄 Enhanced Research Paper Deliverables

- **Publication PDF:** [`EHR_EpSO_Enhanced_Paper.pdf`](EHR_EpSO_Enhanced_Paper.pdf)
- **LaTeX Source:** [`EHR_EpSO_Enhanced_Paper.tex`](EHR_EpSO_Enhanced_Paper.tex)
- **Peer Review Resolution Summary:** [`FRAMEWORK_SUMMARY.md`](FRAMEWORK_SUMMARY.md)

---

## 🌟 Key Features & Benchmark Highlights

- **94.1% EpSO Concept Resolution (CR):** Three-stage hybrid NLP pipeline (prefix-tree lookup over 3,847 EpSO concept labels coupled with BioWordVec 300D contextual disambiguation) significantly outperforming standard clinical NLP baselines (**MetaMap: 81.4%**, **QuickUMLS: 84.7%**, **scispaCy: 86.2%**).
- **99.2% HL7 FHIR R4 Compliance:** Automated serialization of free-text clinical notes, EEG impressions, and pharmacy administration logs into fully validated FHIR R4 resource bundles (`Condition`, `Observation`, `MedicationRequest`).
- **High-Precision Predictive Analytics:** Validated on **4,187 hospital admissions across 3,641 unique patients** from MIMIC-IV v3.1 (2008–2022). A Transformer-encoder architecture achieved:
  - **AUROC 0.876 (95% CI: 0.856–0.896)** for **30-Day Seizure Recurrence Prediction**
  - **AUROC 0.839 (95% CI: 0.815–0.863)** for **Treatment Non-Adherence Classification**
- **Dual-Model Interpretability:** Feature attribution via **TreeSHAP** (XGBoost) and **Integrated Gradients** (Transformer), identifying prior 12-month admission frequency and Medicaid insurance coverage as primary drivers of recurrence and non-adherence, respectively.
- **Harmonized 5-Fold Stratified CV & Held-Out Test Evaluation:** Resolving evaluation protocol ambiguities, reporting 5-fold cross-validation variance ($\text{mean} \pm \text{SD}$) alongside independent held-out test performance ($n=629$).
- **Enterprise-Grade Database Scalability:** Supports lightweight SQLite for research benchmarking and multi-threaded PostgreSQL connection pooling via SQLAlchemy for hospital-scale write throughput.

---

## 📐 System Architecture

![EHR-EpSO System Architecture](fig1_architecture.png)

The framework operates across five modular pipeline layers:
1. **Data Ingestion & Preprocessing:** MIMIC-IV v3.1 database extraction, ICD-10 G40/G41 filtering, free-text EEG report NLP feature extraction, and Elixhauser comorbidity scoring (Quan et al. ICD-10 adaptation).
2. **Three-Stage EpSO Ontology Alignment:** Text tokenization and WordNet lemmatization, prefix-trie lookup ($\ge 4$ char matching), and BioWordVec cosine similarity disambiguation ($\tau = 0.65$).
3. **FHIR R4 Serialization & Validation:** HAPI FHIR strict validator engine generating US Core R4 compliant resource bundles.
4. **Machine Learning Analytics Engine:** XGBoost ensemble, BiLSTM recurrent model over 48h laboratory time-series, and Transformer encoder ($d_{\text{model}}=128$, $d_{\text{ff}}=256$, 4 heads, 2 layers).
5. **Clinical Surveillance & Decision Support:** Post-discharge seizure-free survival curves, risk stratification alerts, and SHAP/Integrated Gradients attribution dashboards.

---

## 📊 Experimental Results

### 1. EpSO Ontology Alignment vs. Standard NLP Tools

| Clinical Entry Source / Tool | Total Entries | Resolved | Concept Res. CR (%) | Mean Cosine Sim. (MCS) |
| :--- | :---: | :---: | :---: | :---: |
| Discharge Summary Diagnoses | 8,214 | 7,836 | 95.4% (94.9–95.9) | 0.84 $\pm$ 0.07 |
| ICD-10 Code Descriptions | 6,129 | 5,897 | 96.2% (95.7–96.7) | 0.89 $\pm$ 0.05 |
| EEG Report Impressions | 2,841 | 2,541 | 89.4% (88.2–90.6) | 0.77 $\pm$ 0.10 |
| Physician Narrative Notes | 1,248 | 1,065 | 85.3% (83.3–87.3) | 0.74 $\pm$ 0.12 |
| **Overall EHR-EpSO Pipeline** | **18,432** | **17,339** | **94.1% (93.2–95.0)** | **0.83 $\pm$ 0.09** |
| *MetaMap (UMLS Metathesaurus)* | 18,432 | 15,004 | 81.4% (80.8–82.0) | 0.71 $\pm$ 0.14 |
| *QuickUMLS* | 18,432 | 15,612 | 84.7% (84.2–85.2) | 0.75 $\pm$ 0.12 |
| *scispaCy (`en_core_sci_lg`)* | 18,432 | 15,888 | 86.2% (85.7–86.7) | 0.76 $\pm$ 0.11 |

---

### 2. Predictive Model Discrimination & Calibration

![ROC Curves](fig2_roc_curves.png)

| Task & Model Family | Evaluation Split | AUROC (95% CI) | AUPRC (95% CI) | F1-Score | Brier Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Task 1: 30-Day Recurrence** | | | | | |
| XGBoost | Held-Out Test ($n=629$) | 0.845 (0.821–0.869) | 0.628 (0.598–0.658) | 0.608 | 0.161 |
| BiLSTM | Held-Out Test ($n=629$) | 0.866 (0.844–0.888)* | 0.654 (0.625–0.683) | 0.631 | 0.150 |
| **Transformer Encoder** | **Held-Out Test ($n=629$)** | **0.876 (0.856–0.896)\*** | **0.671 (0.642–0.700)** | **0.645** | **0.144** |
| **Task 2: Non-Adherence** | | | | | |
| XGBoost | Held-Out Test ($n=629$) | 0.810 (0.784–0.836) | 0.598 (0.567–0.629) | 0.590 | 0.169 |
| BiLSTM | Held-Out Test ($n=629$) | 0.829 (0.804–0.854)* | 0.619 (0.589–0.649) | 0.608 | 0.160 |
| **Transformer Encoder** | **Held-Out Test ($n=629$)** | **0.839 (0.815–0.863)\*** | **0.632 (0.602–0.662)** | **0.619** | **0.154** |

*\* Denotes $p < 0.01$ statistical improvement over XGBoost via DeLong's test.*

---

### 3. Dual-Model Feature Attribution Analysis

![SHAP Importance](fig3_shap_importance.png)

---

### 4. Kaplan-Meier Seizure-Free Survival Trajectories

![Surveillance & Survival](fig4_surveillance.png)

- **Status Epilepticus (G41.x):** Median seizure-free interval = **18 days** (95% CI: 14–22 days)
- **Generalized Epilepsy (G40.3–G40.4):** Median seizure-free interval = **61 days** (95% CI: 53–70 days)
- **Focal Epilepsy (G40.1–G40.2):** Median seizure-free interval = **74 days** (95% CI: 67–82 days)

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.9+
- SQLite (included) or PostgreSQL 12+

### Installation Steps

```bash
# Clone the repository
git clone https://github.com/yogeshmj2024/agentic_epilepsy.git
cd agentic_epilepsy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the End-to-End Pipeline

```bash
# Execute dataset generation and ontology alignment test
python test_full_framework_with_visualization.py

# Run main interoperability and FHIR R4 adapter engine
python main_interop.py
```

---

## 📁 Repository Directory Structure

```
agentic_epilepsy/
├── EHR_EpSO_Enhanced_Paper.pdf     # Enhanced publication PDF
├── EHR_EpSO_Enhanced_Paper.tex     # Complete LaTeX source file
├── fig1_architecture.png          # System Architecture diagram
├── fig2_roc_curves.png            # ROC Curves plot
├── fig3_shap_importance.png       # Feature attribution plot
├── fig4_surveillance.png          # Kaplan-Meier & Ontology resolution plot
├── generate_paper_figures.py      # Publication figure generator
├── compile_enhanced_pdf.py        # PDF compilation script
├── config/                        # Framework configuration settings
├── data/                          # MIMIC-IV cohort database & EpSO lexicon
├── interoperability/              # FHIR R4 & OpenEHR serialization adapters
├── models/                        # Patient, Treatment, and ML Data Models
├── services/                      # Database & NLP service engines
├── utils/                         # Analytics, validation, and visualization tools
├── main.py                        # Core application entry point
├── main_interop.py                # Interoperability test pipeline
└── requirements.txt               # Python package dependencies
```

---

## 📜 Authors & Citation

**M J Yogesh** &nbsp;|&nbsp; **Dr. Karthikeyan J**  
School of Computer Science Engineering and Information Systems,  
Vellore Institute of Technology, Vellore 632 014, Tamil Nadu, India.  
*Corresponding Emails:* `yogeshmj.nie@gmail.com`, `karthikeyan.jk@vit.ac.in`

```bibtex
@article{yogesh2026ehrepso,
  title={Semantically Intelligent Epilepsy Surveillance: An Ontology-Driven Electronic Health Record Framework Integrating MIMIC-IV v3.1, HL7 FHIR R4, and Machine Learning for Population-Scale Neurological Analytics},
  author={Yogesh, M J and Karthikeyan, J},
  journal={IEEE Journal of Biomedical and Health Informatics (Under Review)},
  year={2026}
}
```

---

## ⚖️ License & AI Disclosure

This project is licensed under the MIT License. In compliance with publishing policies, AI coding tools were utilized solely for code formatting and syntax verification; all scientific concepts, dataset curation, model architectures, and statistical evaluations were independently created by the authors.
