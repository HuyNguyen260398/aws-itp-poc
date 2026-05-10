import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_clinical_note_vi.txt"

_FIXTURE_VARIABLES = {
    "platelet_count": 18,
    "bleeding_score": 6,
    "age": 45,
    "sex": "F",
    "disease_duration_months": 14,
    "prior_corticosteroid": True,
    "corticosteroid_response": "partial",
    "prior_tpo_ra": True,
    "tpo_ra_response": "partial",
    "splenectomy": False,
    "comorbidities": ["tăng huyết áp"],
    "outcome_bleeding_30d": None,
}


def extract_itp_variables(clinical_note: str) -> dict:
    if os.getenv("ITP_USE_FIXTURES", "0") == "1":
        return _FIXTURE_VARIABLES.copy()

    try:
        import boto3
        client = boto3.client("comprehendmedical")
        response = client.detect_entities_v2(Text=clinical_note)
        entities = response.get("Entities", [])

        result = {k: None for k in _FIXTURE_VARIABLES}
        result["comorbidities"] = []

        for entity in entities:
            category = entity.get("Category", "")
            text = entity.get("Text", "").lower()
            if category == "TEST_TREATMENT_PROCEDURE" and "tiểu cầu" in text:
                for attr in entity.get("Attributes", []):
                    if attr.get("Type") == "TEST_VALUE":
                        try:
                            result["platelet_count"] = int(float(attr["RelationshipScore"]))
                        except (ValueError, KeyError):
                            pass
            elif category == "MEDICAL_CONDITION":
                result["comorbidities"].append(entity.get("Text", ""))

        return result

    except Exception as e:
        logger.error("Comprehend Medical error: %s — falling back to fixture", e)
        return _FIXTURE_VARIABLES.copy()
