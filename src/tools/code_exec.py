import subprocess
import tempfile
from pathlib import Path

# LOCAL DEV ONLY — replace with AgentCore Code Interpreter in production


def execute_python(code: str) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["uv", "run", "python", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Timeout after 10 seconds", "returncode": -1}
    finally:
        Path(tmp_path).unlink(missing_ok=True)
