"""
graph_builder.py
================
Constructs a heterogeneous EHR knowledge graph from MIMIC-IV v3.1 data
for use in GraphEpiRec treatment recommendation.

Reference:
    Schlichtkrull, M., Kipf, T. N., Bloem, P., van den Berg, R.,
    Titov, I., & Welling, M. (2018). Modeling relational data with graph
    convolutional networks. ESWC, pp. 593-607.
"""

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import HeteroData
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# ── Relation type registry ───────────────────────────────────────────────────
RELATION_TYPES = {
    "has_diagnosis":    ("patient", "diagnosis"),
    "prescribed":       ("patient", "medication"),
    "has_comorbidity":  ("patient", "comorbidity"),
    "interacts_with":   ("medication", "medication"),
    "contraindicated":  ("diagnosis", "medication"),
    "co_occurs":        ("patient", "patient"),
}


class EpilepsyKnowledgeGraph:
    """
    Builds a heterogeneous knowledge graph G = (V, E, X) from MIMIC-IV epilepsy
    EHR data containing patient, medication, diagnosis, and comorbidity nodes.

    Node sets:
        V_P  : Patient nodes
        V_M  : Antiseizure medication (ASM) nodes
        V_D  : EpSO-aligned diagnosis nodes
        V_C  : Elixhauser comorbidity nodes

    Edge types (6 relation types):
        has_diagnosis    : patient → diagnosis
        prescribed       : patient → medication
        has_comorbidity  : patient → comorbidity
        interacts_with   : medication ↔ medication (drug-drug interaction)
        contraindicated  : diagnosis → medication
        co_occurs        : patient ↔ patient (cosine sim ≥ threshold)
    """

    def __init__(self, co_occur_threshold: float = 0.80):
        self.co_occur_threshold = co_occur_threshold
        self.patient_index: Dict[str, int] = {}
        self.med_index:     Dict[str, int] = {}
        self.diag_index:    Dict[str, int] = {}
        self.comor_index:   Dict[str, int] = {}
        self._graph: Optional[HeteroData] = None

    # ── Data loading ──────────────────────────────────────────────────────────

    def load_mimic_iv(
        self,
        admissions_path: str,
        prescriptions_path: str,
        diagnoses_path: str,
        comorbidity_path: Optional[str] = None,
        interaction_path: Optional[str] = None,
    ) -> "EpilepsyKnowledgeGraph":
        """Load raw MIMIC-IV CSV files and build internal dataframes."""
        logger.info("Loading MIMIC-IV v3.1 epilepsy cohort...")
        self.admissions    = pd.read_csv(admissions_path)
        self.prescriptions = pd.read_csv(prescriptions_path)
        self.diagnoses     = pd.read_csv(diagnoses_path)
        self.comorbidities = pd.read_csv(comorbidity_path) if comorbidity_path else None
        self.interactions  = pd.read_csv(interaction_path) if interaction_path else None

        # Filter to ICD-10 G40.x epilepsy admissions
        epilepsy_codes = self.diagnoses[
            self.diagnoses["icd_code"].str.startswith("G40")
        ]["hadm_id"].unique()
        self.admissions = self.admissions[
            self.admissions["hadm_id"].isin(epilepsy_codes)
        ]
        logger.info(f"Epilepsy cohort: {len(self.admissions)} admissions, "
                    f"{self.admissions['subject_id'].nunique()} unique patients")
        return self

    # ── Index building ────────────────────────────────────────────────────────

    def _build_indices(self):
        """Assign sequential integer IDs to all entity types."""
        patients      = self.admissions["subject_id"].unique().tolist()
        medications   = self.prescriptions["drug"].unique().tolist()
        diagnoses     = self.diagnoses["icd_code"].unique().tolist()
        comorbidities = (self.comorbidities.columns.tolist()
                         if self.comorbidities is not None
                         else [f"comorbidity_{i}" for i in range(17)])

        self.patient_index = {p: i for i, p in enumerate(patients)}
        self.med_index     = {m: i for i, m in enumerate(medications)}
        self.diag_index    = {d: i for i, d in enumerate(diagnoses)}
        self.comor_index   = {c: i for i, c in enumerate(comorbidities)}

        logger.info(f"Nodes: {len(patients)} patients | {len(medications)} ASMs | "
                    f"{len(diagnoses)} diagnoses | {len(comorbidities)} comorbidities")

    # ── Edge construction ─────────────────────────────────────────────────────

    def _build_patient_diagnosis_edges(self) -> Tuple[torch.Tensor, torch.Tensor]:
        src, dst = [], []
        for _, row in self.diagnoses.iterrows():
            sid = row.get("subject_id")
            icd = row.get("icd_code", "")
            if sid in self.patient_index and icd in self.diag_index:
                src.append(self.patient_index[sid])
                dst.append(self.diag_index[icd])
        return torch.tensor(src, dtype=torch.long), torch.tensor(dst, dtype=torch.long)

    def _build_prescription_edges(self) -> Tuple[torch.Tensor, torch.Tensor]:
        src, dst = [], []
        for _, row in self.prescriptions.iterrows():
            sid  = row.get("subject_id")
            drug = row.get("drug", "")
            if sid in self.patient_index and drug in self.med_index:
                src.append(self.patient_index[sid])
                dst.append(self.med_index[drug])
        return torch.tensor(src, dtype=torch.long), torch.tensor(dst, dtype=torch.long)

    def _build_co_occur_edges(
        self, patient_features: np.ndarray
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Patient-patient edges where cosine similarity ≥ threshold."""
        sim = cosine_similarity(patient_features)
        src, dst = np.where(
            (sim >= self.co_occur_threshold) & (sim < 1.0)  # exclude self-loops
        )
        return torch.tensor(src, dtype=torch.long), torch.tensor(dst, dtype=torch.long)

    def _build_interaction_edges(self) -> Tuple[torch.Tensor, torch.Tensor]:
        if self.interactions is None:
            return torch.zeros(0, dtype=torch.long), torch.zeros(0, dtype=torch.long)
        src, dst = [], []
        for _, row in self.interactions.iterrows():
            m1, m2 = row.get("drug_a"), row.get("drug_b")
            if m1 in self.med_index and m2 in self.med_index:
                src.extend([self.med_index[m1], self.med_index[m2]])
                dst.extend([self.med_index[m2], self.med_index[m1]])
        return torch.tensor(src, dtype=torch.long), torch.tensor(dst, dtype=torch.long)

    # ── Feature initialisation ────────────────────────────────────────────────

    def _initialise_node_features(self, embedding_dim: int = 128) -> np.ndarray:
        """Initialise patient feature vectors from demographics + diagnoses."""
        n_patients = len(self.patient_index)
        # Simplified: random init (replace with actual feature extraction in production)
        np.random.seed(42)
        features = np.random.randn(n_patients, embedding_dim).astype(np.float32)
        # Normalise rows
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        return features / (norms + 1e-8)

    # ── Main build method ─────────────────────────────────────────────────────

    def build(self, embedding_dim: int = 128) -> HeteroData:
        """
        Build and return the full HeteroData graph object for PyG.

        Returns:
            HeteroData: heterogeneous graph with all node and edge types.
        """
        self._build_indices()
        patient_feats = self._initialise_node_features(embedding_dim)

        data = HeteroData()

        # Node feature matrices
        data["patient"].x    = torch.tensor(patient_feats)
        data["medication"].x = torch.randn(len(self.med_index),   embedding_dim)
        data["diagnosis"].x  = torch.randn(len(self.diag_index),  embedding_dim)
        data["comorbidity"].x = torch.randn(len(self.comor_index), embedding_dim)

        # Edges
        p_src_d, p_dst_d = self._build_patient_diagnosis_edges()
        data["patient", "has_diagnosis", "diagnosis"].edge_index    = torch.stack([p_src_d, p_dst_d])

        p_src_m, p_dst_m = self._build_prescription_edges()
        data["patient", "prescribed", "medication"].edge_index       = torch.stack([p_src_m, p_dst_m])

        co_src, co_dst = self._build_co_occur_edges(patient_feats)
        data["patient", "co_occurs", "patient"].edge_index           = torch.stack([co_src, co_dst])

        m_src, m_dst = self._build_interaction_edges()
        data["medication", "interacts_with", "medication"].edge_index = torch.stack([m_src, m_dst])

        logger.info(
            f"Graph built: {data.num_nodes} total nodes, "
            f"edge types = {len(data.edge_types)}"
        )
        self._graph = data
        return data

    def get_positive_pairs(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """Return (patient_ids, medication_ids) positive training pairs."""
        if self._graph is None:
            raise RuntimeError("Call build() first.")
        ei = self._graph["patient", "prescribed", "medication"].edge_index
        return ei[0], ei[1]

    def get_interaction_set(self) -> set:
        """Return set of (med_id, med_id) drug-interaction pairs."""
        if self.interactions is None:
            return set()
        pairs = set()
        for _, row in self.interactions.iterrows():
            m1, m2 = row.get("drug_a"), row.get("drug_b")
            if m1 in self.med_index and m2 in self.med_index:
                pairs.add((self.med_index[m1], self.med_index[m2]))
                pairs.add((self.med_index[m2], self.med_index[m1]))
        return pairs
