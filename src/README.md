# Local Development Quickstart

## Prerequisites

1. Install `uv` if not already present:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Configure AWS credentials and environment:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials (or leave ITP_USE_FIXTURES=1 for offline mode)
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

## Run the pipeline

```bash
# Run with a clinical note file (fixture mode — no AWS required)
ITP_USE_FIXTURES=1 uv run python main.py --note-file src/fixtures/sample_clinical_note_vi.txt

# Or with an inline note
ITP_USE_FIXTURES=1 uv run python main.py --note "Bệnh nhân nam 55 tuổi, tiểu cầu 12×10⁹/L..."
```

## Smoke test (full pipeline, fixture mode)

```bash
ITP_USE_FIXTURES=1 uv run python scripts/smoke_test_local.py
```

## Test individual agents

```bash
ITP_USE_FIXTURES=1 uv run python src/agents/intake_agent.py
ITP_USE_FIXTURES=1 uv run python src/agents/risk_reasoner_agent.py
ITP_USE_FIXTURES=1 uv run python src/agents/guidelines_agent.py
ITP_USE_FIXTURES=1 uv run python src/agents/cohort_lookup_agent.py
```

> **Note**: For real AWS mode (`ITP_USE_FIXTURES=0`), ensure Bedrock model access is enabled in `us-west-2` for `claude-sonnet-4-5` and `claude-haiku-4-5` cross-region inference profiles.
