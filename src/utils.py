from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "agents" / "prompts"
_FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_prompt(filename: str) -> str:
    return (_PROMPTS_DIR / filename).read_text(encoding="utf-8")


def get_fixture_path(filename: str) -> str:
    return str(_FIXTURES_DIR / filename)
