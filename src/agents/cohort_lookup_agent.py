import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strands import Agent, tool
from src.utils import load_prompt
from src.tools.cohort_similarity import find_similar_patients


@tool
def run_cohort_lookup(features: dict) -> list:
    """Tìm kiếm các bệnh nhân ITP tương tự trong cơ sở dữ liệu lịch sử và trả về danh sách top-5 bệnh nhân có độ tương đồng cao nhất."""
    return find_similar_patients(features, top_k=5)


cohort_lookup_agent = Agent(
    model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[run_cohort_lookup],
    system_prompt=load_prompt("cohort_lookup_vi.txt"),
    callback_handler=None,
)


if __name__ == "__main__":
    test_features = {
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
    }
    result = cohort_lookup_agent(str(test_features))
    print(result)
