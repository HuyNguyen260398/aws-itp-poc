import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strands import Agent, tool
from src.utils import load_prompt
from src.tools.kb_retrieve import retrieve_guidelines


@tool
def run_kb_retrieve(query: str) -> list:
    """Truy xuất các hướng dẫn điều trị ITP từ Bedrock Knowledge Base và trả về danh sách kết quả có nội dung và nguồn trích dẫn."""
    kb_id = os.getenv("ITP_KB_ID")
    return retrieve_guidelines(query, kb_id=kb_id)


guidelines_agent = Agent(
    model="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[run_kb_retrieve],
    system_prompt=load_prompt("guidelines_vi.txt"),
    callback_handler=None,
)


if __name__ == "__main__":
    result = guidelines_agent("Khuyến cáo điều trị ITP kháng corticosteroid với tiểu cầu dưới 30?")
    print(result)
