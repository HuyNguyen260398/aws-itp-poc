import json
import logging
import os
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

_FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "synthetic_patients.json"

_NORM = {
    "platelet_count": (0, 500),
    "bleeding_score": (0, 14),
    "age": (18, 80),
    "disease_duration_months": (0, 120),
}


def _feature_vector(patient: dict) -> np.ndarray:
    vec = []
    for key, (lo, hi) in _NORM.items():
        val = patient.get(key)
        vec.append(0.5 if val is None else (float(val) - lo) / (hi - lo + 1e-9))
    return np.array(vec, dtype=np.float32)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


def _fixture_lookup(features: dict, top_k: int) -> list[dict]:
    patients = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    query_vec = _feature_vector(features)
    scored = [
        {
            "patient_id": p["patient_id"],
            "similarity_pct": round(_cosine(query_vec, _feature_vector(p)) * 100, 1),
            "key_features": {k: p[k] for k in ("platelet_count", "bleeding_score", "age")},
            "outcome_bleeding_30d": p.get("outcome_bleeding_30d"),
        }
        for p in patients
    ]
    scored.sort(key=lambda x: x["similarity_pct"], reverse=True)
    return scored[:top_k]


def find_similar_patients(features: dict, top_k: int = 5) -> list[dict]:
    if os.getenv("ITP_USE_FIXTURES", "0") == "1":
        return _fixture_lookup(features, top_k)

    try:
        import boto3
        table_name = os.getenv("ITP_COHORT_TABLE", "itp-cohort-index")
        table = boto3.resource("dynamodb").Table(table_name)
        query_vec = _feature_vector(features)
        items = table.scan().get("Items", [])
        scored = []
        for item in items:
            raw = item.get("feature_vector", b"")
            if isinstance(raw, bytes) and len(raw) >= 16:
                p_arr = np.frombuffer(raw, dtype=np.float32)
                sim = _cosine(query_vec[:len(p_arr)], p_arr)
            else:
                sim = 0.0
            scored.append({
                "patient_id": item.get("patient_id", "?"),
                "similarity_pct": round(sim * 100, 1),
                "key_features": {k: item.get(k) for k in ("platelet_count", "bleeding_score", "age")},
                "outcome_bleeding_30d": item.get("outcome_bleeding_30d"),
            })
        scored.sort(key=lambda x: x["similarity_pct"], reverse=True)
        return scored[:top_k]

    except Exception as e:
        logger.error("DynamoDB error: %s — falling back to fixture", e)
        return _fixture_lookup(features, top_k)
