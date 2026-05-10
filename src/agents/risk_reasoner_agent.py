import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strands import Agent, tool
from src.utils import load_prompt
from src.tools.code_exec import execute_python

_RISK_PRIORS_PATH = Path(__file__).parent.parent.parent / "data" / "guidelines" / "itp_risk_priors_v1.md"
try:
    RISK_PRIORS_TEXT = _RISK_PRIORS_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    RISK_PRIORS_TEXT = ""


@tool
def run_code_exec(code: str) -> dict:
    """Thực thi mã Python để tính toán điểm nguy cơ chảy máu và trả về stdout, stderr, returncode."""
    return execute_python(code)


risk_reasoner_agent = Agent(
    model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[run_code_exec],
    system_prompt=load_prompt("risk_reasoner_vi.txt") + f"\n\n## Bảng trọng số nguy cơ\n{RISK_PRIORS_TEXT}",
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
    result = risk_reasoner_agent(str(test_features))
    print(result)
