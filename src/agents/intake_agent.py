import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strands import Agent, tool
from src.utils import load_prompt
from src.tools.comprehend_intake import extract_itp_variables


@tool
def run_intake(clinical_note: str) -> dict:
    """Trích xuất 11 biến lâm sàng ITP từ ghi chú lâm sàng tiếng Việt và trả về dưới dạng dict có cấu trúc."""
    return extract_itp_variables(clinical_note)


intake_agent = Agent(
    model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[run_intake],
    system_prompt=load_prompt("intake_vi.txt"),
    callback_handler=None,
)


if __name__ == "__main__":
    note_path = Path(__file__).parent.parent / "fixtures" / "sample_clinical_note_vi.txt"
    note = note_path.read_text(encoding="utf-8")
    result = intake_agent(note)
    print(result)
