# GraphEpiRec 🧠💊

**Graph Convolutional Network-Based Dialogue-Driven Recommendation System for Personalised Epilepsy Treatment**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-GPL--3.0-green)](LICENSE)

> **Authors:** M J Yogesh & Dr. Karthikeyan J  
> School of Computer Science Engineering and Information Systems,  
> Vellore Institute of Technology, Vellore, India  
> Contact: yogeshmj.nie@gmail.com | karthikeyan.jk@vit.ac.in  

---

## Overview

GraphEpiRec is an open-source framework for personalised antiseizure medication (ASM) recommendation using:
- **Relational Graph Convolutional Networks (RGCN)** over heterogeneous EHR knowledge graphs
- **BioBERT dialogue context encoder** with attention pooling
- **Bayesian Personalised Ranking (BPR)** loss for pairwise training
- **Drug-interaction safety filtering** using contraindication edge propagation

The system is evaluated on a **3,641-patient epilepsy cohort** from MIMIC-IV v3.1 and achieves **Precision@5 = 0.813** and **NDCG@10 = 0.791**.

---

## Repository Structure

```
graphepirec_repo/
├── src/
│   ├── graph_builder.py       # Knowledge graph construction from EHR data
│   ├── rgcn_encoder.py        # Relational GCN encoder (L=2 layers, d=128)
│   ├── dialogue_encoder.py    # BioBERT dialogue context encoder
│   ├── recommendation.py      # Scoring, ranking, and BPR training
│   └── safety_filter.py       # Drug-interaction safety checker
├── models/
│   ├── graphepirec.py         # Full GraphEpiRec model
│   └── baselines.py           # CF, MF, TransE baselines
├── utils/
│   ├── data_loader.py         # MIMIC-IV data loading utilities
│   ├── metrics.py             # Precision@k, NDCG@k, Jaccard
│   └── preprocessing.py       # Feature extraction and normalisation
├── notebooks/
│   └── demo.ipynb             # End-to-end demo notebook
├── tests/
│   └── test_graphepirec.py    # Unit and integration tests
├── requirements.txt
└── train.py                   # Main training script
```

---

## Installation

```bash
git clone https://github.com/yogeshmj2024/agentic_epilipsy-.git
cd agentic_epilipsy-/graphepirec_repo

pip install -r requirements.txt
```

### Requirements
```
torch>=2.0.0
torch-geometric>=2.3.0
transformers>=4.30.0
scikit-learn>=1.2.0
numpy>=1.24.0
pandas>=2.0.0
networkx>=3.1
tqdm>=4.65.0
```

---

## Quick Start

```python
from src.graph_builder import EpilepsyKnowledgeGraph
from models.graphepirec import GraphEpiRec

# Build knowledge graph from EHR data
kg = EpilepsyKnowledgeGraph()
kg.load_mimic_iv(admissions_path="data/admissions.csv",
                 prescriptions_path="data/prescriptions.csv",
                 diagnoses_path="data/diagnoses_icd.csv")
graph_data = kg.build()

# Initialise and train GraphEpiRec
model = GraphEpiRec(
    num_patients=3641,
    num_medications=42,
    num_diagnoses=87,
    num_comorbidities=17,
    embedding_dim=128,
    num_gcn_layers=2,
    dialogue_model="dmis-lab/biobert-base-cased-v1.2"
)

model.train(graph_data, epochs=50, lr=1e-3, lambda_reg=1e-4)

# Get recommendations for a patient
patient_id = "P00247"
dialogue_text = "Patient reports 4 focal seizures this month, sleep-deprived."
recommendations = model.recommend(patient_id, dialogue_text, top_k=5)
print(recommendations)
# ['Levetiracetam', 'Lacosamide', 'Lamotrigine', 'Valproate', 'Perampanel']
```

---

## Citation

If you use GraphEpiRec in your research, please cite:

```bibtex
@article{yogesh2025graphepirec,
  title   = {From Conversations to Cures: A Graph Convolutional Network Framework
             for Dialogue-Driven Antiseizure Medication Recommendation},
  author  = {Yogesh, M J and Karthikeyan, J},
  journal = {Artificial Intelligence in Medicine},
  year    = {2025},
  note    = {Manuscript under review}
}
```

### Key References

- Kipf, T. N., & Welling, M. (2017). Semi-supervised classification with graph convolutional networks. *ICLR 2017*.
- Schlichtkrull, M., Kipf, T. N., Bloem, P., van den Berg, R., Titov, I., & Welling, M. (2018). Modeling relational data with graph convolutional networks. *ESWC*, pp. 593–607.
- Rendle, S., Freudenthaler, C., Gantner, Z., & Schmidt-Thieme, L. (2009). BPR: Bayesian personalised ranking from implicit feedback. *UAI*, pp. 452–461.
- Shang, J., Xiao, C., Ma, T., Li, H., & Sun, J. (2019). GAMENet: Graph augmented memory networks for recommending medication combination. *AAAI*, 33(1), 1126–1133.
- Yang, C., Xiao, C., Ma, F., Glass, L., & Sun, J. (2021). SafeDrug: Dual molecular graph encoders for safe drug recommendations. *IJCAI*, pp. 3735–3741.
- Lee, J., Yoon, W., Kim, S., Kim, D., Kim, S., So, C. H., & Kang, J. (2020). BioBERT: A pre-trained biomedical language representation model. *Bioinformatics*, 36(4), 1234–1240.
- Johnson, A., Bulgarelli, L., Pollard, T., Gow, B., Moody, B., Horng, S., Celi, L. A., & Mark, R. (2024). *MIMIC-IV (version 3.1)*. PhysioNet. https://doi.org/10.13026/kpb9-mt58
- Tang, H., Ma, G., Intan, R., Zheng, S., Zhang, L., Hu, J., & Li, P. (2022). BrainGB: A benchmark for brain network analysis with graph neural networks. *IEEE Transactions on Medical Imaging*, 42(2), 493–506.

---

## License
GPL-3.0 © 2025 M J Yogesh, Dr. Karthikeyan J — VIT Vellore
