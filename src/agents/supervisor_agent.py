import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from strands import Agent, tool
from src.utils import load_prompt
from src.agents.intake_agent import intake_agent
from src.agents.risk_reasoner_agent import risk_reasoner_agent
from src.agents.guidelines_agent import guidelines_agent
from src.agents.cohort_lookup_agent import cohort_lookup_agent


@tool
def intake_agent_tool(clinical_note: str) -> str:
    """Trích xuất các biến lâm sàng ITP từ ghi chú lâm sàng tiếng Việt. Phải gọi công cụ này đầu tiên với nội dung ghi chú lâm sàng thô."""
    return str(intake_agent(clinical_note))


@tool
def risk_reasoner_tool(features: str) -> str:
    """Tính toán điểm nguy cơ chảy máu (0–100) và phân tầng nguy cơ (Thấp/Trung bình/Cao) dựa trên các biến lâm sàng đã trích xuất. Truyền vào chuỗi JSON của dict các biến lâm sàng."""
    return str(risk_reasoner_agent(features))


@tool
def guidelines_tool(query: str) -> str:
    """Truy xuất và tóm tắt các hướng dẫn điều trị ITP từ ASH, ISTH, và BV Truyền máu Huyết học có liên quan đến câu hỏi lâm sàng."""
    return str(guidelines_agent(query))


@tool
def cohort_lookup_tool(features: str) -> str:
    """Tìm kiếm các bệnh nhân ITP tương tự trong cơ sở dữ liệu lịch sử và trả về top-5 bệnh nhân có độ tương đồng cao nhất cùng kết quả điều trị. Truyền vào chuỗi JSON của dict các biến lâm sàng."""
    return str(cohort_lookup_agent(features))


supervisor_agent = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    tools=[intake_agent_tool, risk_reasoner_tool, guidelines_tool, cohort_lookup_tool],
    system_prompt=load_prompt("supervisor_vi.txt"),
)
