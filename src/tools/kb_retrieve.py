import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "mock_kb_response.json"


def retrieve_guidelines(query: str, kb_id: str = None) -> list[dict]:
    if os.getenv("ITP_USE_FIXTURES", "0") == "1" or not kb_id:
        data = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        return data["results"]

    try:
        import boto3
        client = boto3.client("bedrock-agent-runtime")
        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
        )
        results = []
        for r in response.get("retrievalResults", []):
            results.append({
                "content": r["content"]["text"],
                "source": r.get("location", {}).get("s3Location", {}).get("uri", "unknown"),
                "score": r.get("score", 0.0),
            })
        return results

    except Exception as e:
        logger.error("Bedrock KB retrieve error: %s — falling back to fixture", e)
        data = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        return data["results"]
