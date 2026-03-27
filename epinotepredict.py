"""
epinotepredict.py
=================
ClinicalLongformer-based context-aware classifier for noteworthy utterance
prediction in physician-patient epilepsy consultations.

References:
    Beltagy, I., Peters, M. E., & Cohan, A. (2020). Longformer: The long-document
        transformer. arXiv:2004.05150.
    Li, Y. et al. (2023). ClinicalLongformer for NER in clinical trial eligibility.
        Journal of Biomedical Informatics, 138, 104051.
    Alsentzer, E. et al. (2019). Publicly available clinical BERT embeddings.
        Proceedings of the 2nd Clinical NLP Workshop, pp. 72-78.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel, AutoConfig
from typing import List, Dict, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

SPEAKER_TOKENS = {"doctor": "[DOC]", "patient": "[PAT]"}
MAX_LENGTH = 4096   # Longformer supports up to 4,096 tokens


class EpiNotePredict(nn.Module):
    """
    Context-aware noteworthy utterance classifier using ClinicalLongformer.

    Key design: the entire consultation dialogue is serialised as one long
    token sequence with speaker-turn markers. The Longformer's sliding-window
    local attention captures intra-utterance syntax, while global attention on
    [SEP] tokens propagates information across the full dialogue. Each
    utterance is classified from the hidden state of its boundary [SEP] token,
    enabling classification conditioned on full conversational context.

    Architecture follows Equation (4) from the paper:
        ŷ_i = σ(W_s · h_[SEP]_i + b_s)

    Args:
        model_name  : HuggingFace model identifier for ClinicalLongformer.
        num_labels  : Number of output classes (default: 2 for binary NW prediction).
        dropout     : Classification head dropout probability (default: 0.1).
        window_size : Longformer local attention window (default: 512).
        freeze_base : If True, freeze the transformer backbone weights.
    """

    LONGFORMER_DIM = 768

    def __init__(
        self,
        model_name: str = "yikuan8/Clinical-Longformer",
        num_labels: int = 2,
        dropout: float = 0.1,
        window_size: int = 512,
        freeze_base: bool = False,
    ):
        super().__init__()
        self.num_labels  = num_labels

        config = AutoConfig.from_pretrained(model_name)
        config.attention_window = [window_size] * config.num_hidden_layers

        self.tokeniser = AutoTokenizer.from_pretrained(model_name)
        self.longformer = AutoModel.from_pretrained(model_name, config=config)

        if freeze_base:
            for param in self.longformer.parameters():
                param.requires_grad = False

        # Add speaker tokens to vocabulary
        special_tokens = list(SPEAKER_TOKENS.values())
        self.tokeniser.add_special_tokens({"additional_special_tokens": special_tokens})
        self.longformer.resize_token_embeddings(len(self.tokeniser))

        # Classification head: h_[SEP]_i → ŷ_i
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.LONGFORMER_DIM, self.LONGFORMER_DIM // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(self.LONGFORMER_DIM // 2, num_labels),
        )

    # ── Dialogue serialisation ─────────────────────────────────────────────

    def serialise_dialogue(self, utterances: List[str],
                            speakers: List[str]) -> str:
        """
        Serialise dialogue as a single string with speaker tokens and [SEP] markers.

        Format:
            [CLS] [DOC] u_1 [SEP] [PAT] u_2 [SEP] ... u_T [SEP]
        """
        parts = []
        for utt, spk in zip(utterances, speakers):
            tok = SPEAKER_TOKENS.get(spk.lower(), "[UNK]")
            parts.append(f"{tok} {utt}")
        return " [SEP] ".join(parts)

    def find_sep_positions(self, input_ids: torch.Tensor) -> List[List[int]]:
        """Find [SEP] token positions for each item in a batch."""
        sep_id = self.tokeniser.sep_token_id
        positions = []
        for ids in input_ids:
            pos = (ids == sep_id).nonzero(as_tuple=True)[0].tolist()
            positions.append(pos)
        return positions

    # ── Forward pass ──────────────────────────────────────────────────────

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        global_attention_mask: torch.Tensor,
        sep_positions: List[List[int]],
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass over a batch of serialised dialogues.

        Args:
            input_ids              : Token IDs. Shape (B, L).
            attention_mask         : Local attention mask. Shape (B, L).
            global_attention_mask  : Global attention on [SEP] positions. Shape (B, L).
            sep_positions          : List of [SEP] token positions per batch item.
            labels                 : Binary noteworthiness labels per utterance.
                                     Packed tensor of shape (total_utterances,).

        Returns:
            Dictionary with 'logits' and optionally 'loss'.
        """
        outputs = self.longformer(
            input_ids=input_ids,
            attention_mask=attention_mask,
            global_attention_mask=global_attention_mask,
        )
        hidden_states = outputs.last_hidden_state   # (B, L, 768)

        # Extract [SEP] representations for each utterance
        sep_reps = []
        for b_idx, positions in enumerate(sep_positions):
            for pos in positions:
                if pos < hidden_states.size(1):
                    sep_reps.append(hidden_states[b_idx, pos, :])

        if not sep_reps:
            return {"logits": torch.zeros(0, self.num_labels)}

        sep_tensor = torch.stack(sep_reps, dim=0)       # (total_utts, 768)
        logits = self.classifier(sep_tensor)             # (total_utts, 2)

        result = {"logits": logits}
        if labels is not None:
            loss = F.cross_entropy(logits, labels)
            result["loss"] = loss
        return result

    # ── Batch preparation ─────────────────────────────────────────────────

    def prepare_batch(
        self,
        dialogues: List[Tuple[List[str], List[str]]],
        device: torch.device,
        max_length: int = MAX_LENGTH,
    ) -> Dict:
        """
        Prepare a batch of (utterances, speakers) pairs for model input.

        Args:
            dialogues: List of (utterance_list, speaker_list) tuples.
            device   : Target device.
            max_length: Maximum sequence length (Longformer: 4096).

        Returns:
            Dictionary with input_ids, attention_mask, global_attention_mask,
            sep_positions.
        """
        serialised = [
            self.serialise_dialogue(utts, spks) for utts, spks in dialogues
        ]
        encoded = self.tokeniser(
            serialised,
            max_length=max_length,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        input_ids      = encoded["input_ids"].to(device)
        attention_mask = encoded["attention_mask"].to(device)

        # Global attention on [CLS] and all [SEP] tokens
        global_mask = torch.zeros_like(attention_mask)
        global_mask[:, 0] = 1   # [CLS]
        sep_positions = self.find_sep_positions(input_ids)
        for b_idx, positions in enumerate(sep_positions):
            for pos in positions:
                if pos < global_mask.size(1):
                    global_mask[b_idx, pos] = 1

        return {
            "input_ids":              input_ids,
            "attention_mask":         attention_mask,
            "global_attention_mask":  global_mask,
            "sep_positions":          sep_positions,
        }

    # ── Inference ─────────────────────────────────────────────────────────

    @torch.no_grad()
    def predict(
        self,
        utterances: List[str],
        speakers:   Optional[List[str]] = None,
        threshold:  float = 0.5,
        device:     Optional[torch.device] = None,
    ) -> Dict:
        """
        Predict noteworthiness for utterances in a single consultation.

        Args:
            utterances: List of raw utterance strings.
            speakers  : List of speaker labels ('doctor' or 'patient').
                        If None, alternating doctor/patient is assumed.
            threshold : Classification threshold (default: 0.5).
            device    : Compute device (defaults to model device).

        Returns:
            Dictionary with 'scores' (float probabilities) and 'labels' (bool).
        """
        self.eval()
        if device is None:
            device = next(self.parameters()).device

        if speakers is None:
            speakers = ["doctor" if i % 2 == 0 else "patient"
                        for i in range(len(utterances))]

        batch = self.prepare_batch([(utterances, speakers)], device)
        out   = self.forward(**batch)
        probs = F.softmax(out["logits"], dim=-1)[:, 1].cpu().numpy()

        # Align with utterance count (may differ due to tokenisation)
        n = len(utterances)
        if len(probs) != n:
            probs = np.pad(probs, (0, max(0, n - len(probs))))[:n]

        return {
            "scores": probs.tolist(),
            "labels": (probs >= threshold).tolist(),
            "noteworthy_utterances": [
                utt for utt, lbl in zip(utterances, probs >= threshold) if lbl
            ],
        }

    @classmethod
    def from_pretrained(cls, checkpoint_path: str, **kwargs) -> "EpiNotePredict":
        """Load a fine-tuned EpiNotePredict model from a checkpoint."""
        model = cls(**kwargs)
        state = torch.load(checkpoint_path, map_location="cpu")
        model.load_state_dict(state)
        logger.info(f"Loaded EpiNotePredict weights from {checkpoint_path}")
        return model
