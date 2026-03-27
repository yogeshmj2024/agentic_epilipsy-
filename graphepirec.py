"""
graphepirec.py
==============
Full GraphEpiRec model: Relational GCN + BioBERT dialogue encoder + BPR training.

References:
    Schlichtkrull et al. (2018). Modeling relational data with GCNs. ESWC.
    Rendle et al. (2009). BPR: Bayesian personalised ranking. UAI.
    Lee et al. (2020). BioBERT. Bioinformatics, 36(4), 1234-1240.
    Kipf & Welling (2017). Semi-supervised classification with GCNs. ICLR.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import RGCNConv
from transformers import AutoTokenizer, AutoModel
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


# ── Relational GCN Encoder ───────────────────────────────────────────────────

class RGCNEncoder(nn.Module):
    """
    Two-layer Relational GCN encoder.

    Implements Equation (1) from the paper:
        h_v^(l+1) = σ( W_0^(l) h_v^(l) + Σ_r Σ_{u ∈ N_r(v)} (1/c_{v,r}) W_r^(l) h_u^(l) )

    Args:
        in_channels  : Input feature dimensionality.
        hidden_dim   : Hidden and output embedding dimensionality (default: 128).
        num_relations: Number of distinct relation/edge types.
        num_layers   : Number of GCN propagation layers (default: 2).
        dropout      : Dropout rate applied between layers (default: 0.1).
    """

    def __init__(
        self,
        in_channels: int,
        hidden_dim: int = 128,
        num_relations: int = 6,
        num_layers: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.layers = nn.ModuleList()
        self.dropout = nn.Dropout(dropout)

        for i in range(num_layers):
            in_ch = in_channels if i == 0 else hidden_dim
            self.layers.append(
                RGCNConv(in_ch, hidden_dim, num_relations=num_relations)
            )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor,
                edge_type: torch.Tensor) -> torch.Tensor:
        h = x
        for i, layer in enumerate(self.layers):
            h = layer(h, edge_index, edge_type)
            if i < len(self.layers) - 1:
                h = F.relu(h)
                h = self.dropout(h)
        return h


# ── Dialogue Context Encoder ─────────────────────────────────────────────────

class DialogueContextEncoder(nn.Module):
    """
    BioBERT-based dialogue encoder with trainable attention pooling.

    Implements Equations (2) and (3) from the paper:
        alpha_i = softmax(q^T e_i)
        c_D     = Σ_i alpha_i * e_i
        c_D_proj = P * c_D   (projection to embedding_dim)

    Args:
        model_name   : HuggingFace model identifier for BioBERT.
        embedding_dim: Target output dimensionality (must match GCN output).
        max_length   : Maximum token sequence length.
        freeze_bert  : If True, freeze BioBERT weights (faster training).
    """

    BIOBERT_DIM = 768

    def __init__(
        self,
        model_name: str = "dmis-lab/biobert-base-cased-v1.2",
        embedding_dim: int = 128,
        max_length: int = 256,
        freeze_bert: bool = False,
    ):
        super().__init__()
        self.max_length = max_length

        self.tokeniser = AutoTokenizer.from_pretrained(model_name)
        self.bert      = AutoModel.from_pretrained(model_name)

        if freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False

        # Trainable attention query vector q ∈ R^768
        self.query = nn.Parameter(torch.randn(self.BIOBERT_DIM))

        # Projection matrix P ∈ R^{embedding_dim × 768}
        self.projection = nn.Linear(self.BIOBERT_DIM, embedding_dim, bias=False)

    def encode_utterances(self, utterances: List[str],
                          device: torch.device) -> torch.Tensor:
        """Encode a list of utterances into per-utterance embeddings."""
        enc = self.tokeniser(
            utterances,
            max_length=self.max_length,
            padding=True,
            truncation=True,
            return_tensors="pt",
        ).to(device)
        with torch.no_grad() if not self.bert.training else torch.enable_grad():
            out = self.bert(**enc)
        # Mean-pool token representations: (n_utterances, 768)
        return out.last_hidden_state.mean(dim=1)

    def forward(self, dialogue: List[str], device: torch.device) -> torch.Tensor:
        """
        Args:
            dialogue: List of utterance strings constituting one consultation.
            device  : Compute device.
        Returns:
            c_proj: Context vector projected to embedding_dim. Shape: (embedding_dim,)
        """
        if not dialogue:
            return torch.zeros(self.projection.out_features, device=device)

        e = self.encode_utterances(dialogue, device)          # (T, 768)
        scores = torch.matmul(e, self.query)                   # (T,)
        alpha  = torch.softmax(scores, dim=0)                  # (T,)
        c_d    = (alpha.unsqueeze(-1) * e).sum(dim=0)          # (768,)
        return self.projection(c_d)                            # (embedding_dim,)


# ── Full GraphEpiRec Model ───────────────────────────────────────────────────

class GraphEpiRec(nn.Module):
    """
    GraphEpiRec: GCN + Dialogue Context + Bilinear Scoring + BPR Training.

    Architecture:
        1. RGCN encodes all graph nodes into a shared embedding space.
        2. Dialogue encoder produces a context vector c_D from consultation text.
        3. Fused patient rep: h̃_p = h_p^(2) + β * c_D_proj
        4. Bilinear scoring: s(p, m) = h̃_p^T M h_m^(2)
        5. BPR loss optimises pairwise ranking.

    Args:
        num_patients    : Total number of patient nodes.
        num_medications : Total number of ASM nodes.
        num_diagnoses   : Total number of diagnosis nodes.
        num_comorbidities: Total number of comorbidity nodes.
        embedding_dim   : Shared latent space dimensionality (default: 128).
        num_gcn_layers  : Number of RGCN propagation layers (default: 2).
        dialogue_model  : HuggingFace model name for dialogue encoder.
        dropout         : Dropout probability (default: 0.1).
    """

    NUM_RELATION_TYPES = 6  # has_diagnosis, prescribed, has_comorbidity,
                             # interacts_with, contraindicated, co_occurs

    def __init__(
        self,
        num_patients: int,
        num_medications: int,
        num_diagnoses: int,
        num_comorbidities: int,
        embedding_dim: int = 128,
        num_gcn_layers: int = 2,
        dialogue_model: str = "dmis-lab/biobert-base-cased-v1.2",
        dropout: float = 0.1,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim

        # Learnable initial embeddings for each node type
        self.patient_emb    = nn.Embedding(num_patients,     embedding_dim)
        self.med_emb        = nn.Embedding(num_medications,  embedding_dim)
        self.diag_emb       = nn.Embedding(num_diagnoses,    embedding_dim)
        self.comor_emb      = nn.Embedding(num_comorbidities, embedding_dim)

        # RGCN encoder (operates over all nodes in concatenated form)
        self.rgcn = RGCNEncoder(
            in_channels=embedding_dim,
            hidden_dim=embedding_dim,
            num_relations=self.NUM_RELATION_TYPES,
            num_layers=num_gcn_layers,
            dropout=dropout,
        )

        # Dialogue context encoder
        self.dialogue_encoder = DialogueContextEncoder(
            model_name=dialogue_model,
            embedding_dim=embedding_dim,
        )

        # Learnable fusion scalar β (initialised to 0.3, paper optimal value)
        self.beta = nn.Parameter(torch.tensor(0.3))

        # Bilinear interaction matrix M ∈ R^{d × d}
        self.M = nn.Parameter(
            torch.empty(embedding_dim, embedding_dim)
        )
        nn.init.xavier_uniform_(self.M)

    # ── Forward pass ─────────────────────────────────────────────────────────

    def encode_graph(
        self,
        edge_index: torch.Tensor,
        edge_type:  torch.Tensor,
        num_patients: int,
        num_meds: int,
    ) -> tuple:
        """
        Run RGCN over the full heterogeneous graph.
        Returns (patient_embeddings, medication_embeddings).
        """
        # Build global node feature matrix by concatenating all node types
        all_nodes = torch.cat([
            self.patient_emb.weight,
            self.med_emb.weight,
            self.diag_emb.weight,
            self.comor_emb.weight,
        ], dim=0)

        h = self.rgcn(all_nodes, edge_index, edge_type)

        h_patients = h[:num_patients]
        h_meds     = h[num_patients: num_patients + num_meds]
        return h_patients, h_meds

    def forward(
        self,
        edge_index: torch.Tensor,
        edge_type:  torch.Tensor,
        patient_ids: torch.Tensor,
        pos_med_ids: torch.Tensor,
        neg_med_ids: torch.Tensor,
        dialogue_texts: Optional[List[List[str]]] = None,
        device: Optional[torch.device] = None,
    ) -> torch.Tensor:
        """
        Compute BPR training loss for a batch of (patient, pos_med, neg_med) triples.

        Returns:
            loss: BPR loss scalar.
        """
        if device is None:
            device = next(self.parameters()).device

        n_patients = self.patient_emb.num_embeddings
        n_meds     = self.med_emb.num_embeddings

        h_p, h_m = self.encode_graph(edge_index, edge_type, n_patients, n_meds)

        # Gather patient and medication embeddings for this batch
        hp = h_p[patient_ids]    # (B, d)
        hm_pos = h_m[pos_med_ids]  # (B, d)
        hm_neg = h_m[neg_med_ids]  # (B, d)

        # Inject dialogue context if provided
        if dialogue_texts:
            ctx_vecs = torch.stack([
                self.dialogue_encoder(dlg, device)
                for dlg in dialogue_texts
            ], dim=0)                                     # (B, d)
            hp = hp + self.beta * ctx_vecs

        # Bilinear scoring: s = h̃_p^T M h_m
        hp_M = torch.matmul(hp, self.M)                   # (B, d)
        s_pos = (hp_M * hm_pos).sum(dim=-1)               # (B,)
        s_neg = (hp_M * hm_neg).sum(dim=-1)               # (B,)

        # BPR loss: L = -Σ ln σ(s_pos - s_neg) + λ||Θ||²
        loss = -F.logsigmoid(s_pos - s_neg).mean()
        return loss

    # ── Inference ─────────────────────────────────────────────────────────────

    @torch.no_grad()
    def recommend(
        self,
        patient_id: int,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
        dialogue: Optional[List[str]] = None,
        top_k: int = 5,
        interaction_set: Optional[set] = None,
    ) -> List[int]:
        """
        Generate top-k ASM recommendations for a single patient.

        Args:
            patient_id     : Integer index of the target patient node.
            edge_index     : Full graph edge index tensor.
            edge_type      : Full graph edge type tensor.
            dialogue       : List of utterance strings from the consultation.
            top_k          : Number of recommendations to return.
            interaction_set: Set of (med_id, med_id) interaction pairs to penalise.

        Returns:
            List of top-k medication node indices.
        """
        device = next(self.parameters()).device
        n_patients = self.patient_emb.num_embeddings
        n_meds     = self.med_emb.num_embeddings

        h_p, h_m = self.encode_graph(edge_index, edge_type, n_patients, n_meds)
        hp = h_p[patient_id].unsqueeze(0)   # (1, d)

        if dialogue:
            ctx = self.dialogue_encoder(dialogue, device).unsqueeze(0)
            hp  = hp + self.beta * ctx

        # Score all medications
        hp_M   = torch.matmul(hp, self.M)              # (1, d)
        scores = torch.matmul(hp_M, h_m.T).squeeze(0)  # (n_meds,)

        # Safety: penalise interacting medications already in top candidates
        if interaction_set:
            top_cands = scores.argsort(descending=True)[:top_k*3].tolist()
            for j, cand in enumerate(top_cands):
                for seen in top_cands[:j]:
                    if (seen, cand) in interaction_set:
                        scores[cand] -= 1e6

        return scores.argsort(descending=True)[:top_k].tolist()


# ── Training utilities ────────────────────────────────────────────────────────

def negative_sample_bpr(
    pos_patient: torch.Tensor,
    pos_med: torch.Tensor,
    num_medications: int,
    popularity: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """
    Popularity-weighted negative sampling for BPR training.
    Less popular medications have higher probability of being sampled as negatives,
    following Yang et al. (2021) SafeDrug.
    """
    batch_size = pos_patient.size(0)
    if popularity is not None:
        weights = 1.0 / (popularity + 1e-6)
        weights = weights / weights.sum()
        neg_meds = torch.multinomial(
            weights.repeat(batch_size, 1),
            num_samples=1,
        ).squeeze(-1)
    else:
        neg_meds = torch.randint(0, num_medications, (batch_size,))
    return neg_meds
