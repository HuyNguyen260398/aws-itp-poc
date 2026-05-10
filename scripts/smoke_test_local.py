import os
import sys
from pathlib import Path

os.environ["ITP_USE_FIXTURES"] = "1"

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.agents.supervisor_agent import supervisor_agent

NOTE_PATH = Path(__file__).parent.parent / "src" / "fixtures" / "sample_clinical_note_vi.txt"
note = NOTE_PATH.read_text(encoding="utf-8")

print("Running smoke test with fixture mode...")
try:
    result = supervisor_agent(note)
    response_text = str(result)
except Exception as e:
    print(f"FAILED: exception during agent call: {e}")
    sys.exit(1)

errors = []

if len(response_text) < 100:
    errors.append(f"Response too short: {len(response_text)} chars")

vietnamese_keywords = ["Nguy cơ", "chảy máu", "tiểu cầu", "điều trị"]
if not any(kw in response_text for kw in vietnamese_keywords):
    errors.append(f"Missing Vietnamese clinical keywords (checked: {vietnamese_keywords})")

risk_tiers = ["Thấp", "Trung bình", "Cao"]
if not any(tier in response_text for tier in risk_tiers):
    errors.append(f"Missing risk tier label (checked: {risk_tiers})")

if errors:
    for err in errors:
        print(f"FAILED: {err}")
    sys.exit(1)

print("PASSED")
sys.exit(0)
