---
goal: Build and Run ITP Multi-Agent System Locally with AWS Strands Agents SDK
version: 1.0
date_created: 2026-05-10
last_updated: 2026-05-10
owner: Huy (Software Engineer)
status: 'Planned'
tags: [feature, multi-agent, strands-sdk, bedrock, local-dev, itp]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan covers building and running all 5 ITP agents (Supervisor + Intake + Risk-Reasoner + Guidelines + Cohort-Lookup) on a local developer machine using the AWS Strands Agents SDK. There is **no deployment, no AgentCore Runtime, no CDK, and no Docker** in this plan — those are covered in a subsequent plan.

The deliverable is a single `python main.py` command that accepts a Vietnamese clinical note, runs the full multi-agent pipeline against real Amazon Bedrock models, and streams the supervisor's structured response to stdout. Tools that require AWS infrastructure (Comprehend Medical, Knowledge Bases, DynamoDB) fall back to local fixtures when those resources are not yet provisioned, making this plan executable from day one of development.

This plan corresponds to TASK-009 and TASK-017–TASK-022 of the full plan at `plan/feature-itp-multiagent-strands-1.md`.

---

## 1. Requirements & Constraints

- **REQ-001**: All 5 agents must be implemented as Strands `Agent` objects using the `strands-agents` Python SDK; no LangChain, no boto3 Bedrock `invoke_model` calls directly inside agent logic.
- **REQ-002**: The Supervisor Agent must use the Strands Agents-as-Tools pattern — each of the 4 sub-agents is wrapped in a `@tool`-decorated function and passed to the Supervisor's `tools=` list; sub-agents are called in-process, not via HTTP.
- **REQ-003**: Foundation models must be invoked via Amazon Bedrock cross-region inference profiles: Supervisor uses `us.anthropic.claude-sonnet-4-5-20250929-v1:0`; all 4 sub-agents use `us.anthropic.claude-haiku-4-5-20251001-v1:0`.
- **REQ-004**: All system prompts must be stored as external `.txt` files under `src/agents/prompts/` and loaded at agent startup via a `load_prompt(filename: str) -> str` helper; no inline prompt strings in Python files.
- **REQ-005**: System prompts and all agent-facing text must be in Vietnamese; internal function parameters and fixture data keys may be in English.
- **REQ-006**: Each tool module (`src/tools/*.py`) must implement a `USE_FIXTURES` flag (read from env var `ITP_USE_FIXTURES=1`); when set, the tool returns data from local fixture files instead of calling AWS services. This allows the full pipeline to run without any AWS infrastructure.
- **REQ-007**: The Risk-Reasoner Agent must load bleeding risk priors from `data/guidelines/itp_risk_priors_v1.md` at startup and pass them as context to Claude; it must not hardcode any numeric weight values in Python.
- **REQ-008**: `main.py` must accept a clinical note either as a command-line argument (`--note "..."`) or from a file (`--note-file path/to/note.txt`), and stream the supervisor response token-by-token to stdout.
- **REQ-009**: The smoke test script `scripts/smoke_test_local.py` must exit with code 0 on success and code 1 on any assertion failure; it must not require pytest.
- **CON-001**: Python version must be 3.11 or higher; use `uv` for all virtual environment creation and dependency management — do not use `pip`, `pip-tools`, or `python -m venv` directly. The virtual environment is created at `.venv/` by `uv sync`.
- **CON-002**: AWS credentials must be configured via `~/.aws/credentials` or environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=us-west-2`) before running any agent that uses real AWS services.
- **CON-003**: When `ITP_USE_FIXTURES=1`, no AWS API calls are made; the pipeline must complete end-to-end offline using only local files.
- **CON-004**: The Strands `code_interpreter` built-in tool requires a sandboxed execution environment; for local dev, use the `subprocess`-based local code execution tool in `src/tools/code_exec.py` instead, which runs generated Python in a subprocess with a 10-second timeout.
- **CON-005**: Do not commit any real patient data or AWS credentials to the repository; `data/raw/` and `.env` are already in `.gitignore`.
- **GUD-001**: Follow the Strands SDK Agents-as-Tools pattern exactly as documented — the `@tool` decorator must include a docstring that describes the tool to the LLM; the docstring IS the tool description used in the model's context.
- **GUD-002**: Each agent file must be independently runnable for isolated testing: `uv run python src/agents/intake_agent.py` must invoke the agent with a hardcoded fixture note and print the result.
- **GUD-003**: Use `python-dotenv` to load `.env` file at startup in `main.py`; `.env.example` must be committed with all required variable names and empty values.
- **PAT-001**: Strands Agents-as-Tools — supervisor's `@tool` functions must call the sub-agent's `.run(input)` method directly (in-process), not via any HTTP endpoint or queue.
- **PAT-002**: Tool fallback pattern — every tool function must check `os.getenv("ITP_USE_FIXTURES", "0") == "1"` at the top of the function body and return fixture data if set, before any AWS SDK call.

---

## 2. Implementation Steps

### Implementation Phase 1 — Project Scaffold & Environment Setup

- GOAL-001: Create the project directory structure, virtual environment, dependency file, and environment configuration so all subsequent phases have a consistent foundation.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create directory tree: `mkdir -p src/agents/prompts src/tools src/fixtures data/guidelines scripts`; verify with `ls -R src/` | | |
| TASK-002 | Create `pyproject.toml` in project root using `uv init --python 3.11` (or write manually). Set `[project] name="itp-poc"`, `requires-python=">=3.11"`. Add dependencies under `[project.dependencies]`: `strands-agents>=0.1.0`, `boto3>=1.35.0`, `python-dotenv>=1.0.0`, `numpy>=1.26.0`, `rich>=13.0.0`. Run `uv lock` to generate `uv.lock`; commit both `pyproject.toml` and `uv.lock`. Do not create a `requirements.txt`. | | |
| TASK-003 | Install dependencies and create virtual environment: run `uv sync` in the project root — uv reads `pyproject.toml`, creates `.venv/` at Python 3.11, and installs all dependencies. Verify with `uv run python -c "import strands; print(strands.__version__)"`. Add `.venv/` to `.gitignore` if not already present. | | |
| TASK-004 | Create `.env.example` in project root with contents: `AWS_DEFAULT_REGION=us-west-2`, `AWS_ACCESS_KEY_ID=`, `AWS_SECRET_ACCESS_KEY=`, `ITP_USE_FIXTURES=1`, `ITP_KB_ID=`, `ITP_PRIORS_KB_ID=`, `ITP_COHORT_TABLE=itp-cohort-index`; commit this file | | |
| TASK-005 | Create `src/__init__.py`, `src/agents/__init__.py`, `src/tools/__init__.py` as empty files so all modules are importable as packages | | |
| TASK-006 | Create `src/utils.py` with two functions: `load_prompt(filename: str) -> str` that reads `src/agents/prompts/{filename}` and returns its contents as a string; `get_fixture_path(filename: str) -> str` that returns the absolute path to `src/fixtures/{filename}` | | |

### Implementation Phase 2 — Fixtures & Risk Priors Data

- GOAL-002: Create all local fixture files used by tools when `ITP_USE_FIXTURES=1`, and the risk priors document used by the Risk-Reasoner Agent in all modes.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-007 | Create `src/fixtures/synthetic_patients.json`: a JSON array of 10 objects, each with keys `patient_id` (string, e.g. `"P001"`), `platelet_count` (int, units: ×10⁹/L), `bleeding_score` (int, 0–14, ITP-BAT scale), `age` (int), `sex` (string, `"M"` or `"F"`), `disease_duration_months` (int), `prior_corticosteroid` (bool), `corticosteroid_response` (string, `"complete"\|"partial"\|"none"\|"na"`), `prior_tpo_ra` (bool), `tpo_ra_response` (string, same values), `splenectomy` (bool), `comorbidities` (list of strings), `outcome_bleeding_30d` (bool). Values must be medically plausible but entirely synthetic (no real patients). | | |
| TASK-008 | Create `src/fixtures/sample_clinical_note_vi.txt`: a single synthetic Vietnamese clinical note (~200 words) describing a fictional adult ITP patient. Must include: platelet count in ×10⁹/L, bleeding symptoms described in Vietnamese medical terminology, current treatment, duration of disease, and relevant comorbidities. The note must contain all 11 ITP variables so the Intake Agent can extract them. | | |
| TASK-009 | Create `src/fixtures/mock_kb_response.json`: a JSON object simulating a Bedrock Knowledge Base retrieval response with keys `results` (list of 3 objects, each with `content` (string, a short Vietnamese guideline excerpt mentioning ITP treatment), `source` (string, e.g. `"ASH 2019 Guidelines, p.12"`), `score` (float, 0.85–0.95)) | | |
| TASK-010 | Create `data/guidelines/itp_risk_priors_v1.md`: a Markdown file with a table of literature-derived bleeding risk weights for the 11 ITP variables. Columns: `Variable`, `Low-risk threshold`, `High-risk threshold`, `Odds Ratio`, `Source`. Include rows for: platelet count (<30 = high, ≥30 = low; OR 3.2; [Provan 2010]), bleeding score (≥3 = high; OR 4.1; [Page 2016]), age (>60 = high; OR 1.8; [Frederiksen 1999]), prior treatment failure (≥2 lines = high; OR 2.5; [Neunert 2019 ASH]), and 7 remaining variables with similar format. | | |

### Implementation Phase 3 — Vietnamese System Prompts

- GOAL-003: Write all 5 Vietnamese system prompt `.txt` files that define each agent's role, output format, and behavioral constraints.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-011 | Create `src/agents/prompts/supervisor_vi.txt`: Vietnamese prompt that instructs Claude Sonnet to act as a clinical decision support orchestrator for ITP at BV Truyền máu Huyết học. Must specify: (1) always call `intake_agent_tool` first on any clinical note input, (2) then call `risk_reasoner_tool` with the extracted features, (3) call `guidelines_tool` with the clinical question, (4) call `cohort_lookup_tool` with the extracted features, (5) synthesize all results into a final Vietnamese response with sections: "Đặc điểm lâm sàng" (clinical features), "Nguy cơ chảy máu" (bleeding risk), "Khuyến cáo điều trị" (treatment recommendations), "Bệnh nhân tương tự" (similar patients). Must include instruction: "Không bao giờ bịa đặt số liệu thống kê hoặc trích dẫn không có trong kết quả công cụ." | | |
| TASK-012 | Create `src/agents/prompts/intake_vi.txt`: Vietnamese prompt that instructs Claude Haiku to extract exactly 11 ITP variables from an unstructured Vietnamese clinical note. Must specify the exact JSON output schema with all 11 field names in English (matching `synthetic_patients.json` keys) and Vietnamese descriptions of each field. Must include instruction to return `null` for any variable not mentioned in the note, and never to infer or assume values not stated. | | |
| TASK-013 | Create `src/agents/prompts/risk_reasoner_vi.txt`: Vietnamese prompt that instructs Claude Haiku to compute a bleeding risk score using the provided risk priors context. Must instruct the agent to: (1) write Python code that computes a weighted sum using the priors table, (2) execute the code using the `code_exec` tool, (3) return a score between 0–100 and a risk tier ("Thấp" <30, "Trung bình" 30–70, "Cao" >70), (4) cite the specific prior used for each variable in the explanation. | | |
| TASK-014 | Create `src/agents/prompts/guidelines_vi.txt`: Vietnamese prompt that instructs Claude Haiku to retrieve and summarize relevant ITP treatment guidelines. Must specify: (1) use the `kb_retrieve` tool with the clinical question as the query, (2) synthesize retrieved passages into a Vietnamese summary with inline citations in format `[Nguồn: {source}]`, (3) if no relevant passages are found, state "Không tìm thấy khuyến cáo phù hợp" and do not fabricate guidelines. | | |
| TASK-015 | Create `src/agents/prompts/cohort_lookup_vi.txt`: Vietnamese prompt that instructs Claude Haiku to find and describe similar past ITP patients. Must specify: (1) use the `cohort_similarity` tool with the feature dict, (2) present results as a numbered list with each patient's similarity percentage, key matching features in Vietnamese, and 30-day bleeding outcome if available, (3) note explicitly that patient IDs are anonymized. | | |
| TASK-016 | Create `src/agents/prompts/few_shot_examples_vi.jsonl`: 5 JSONL lines (one per line), each `{"input": "<Vietnamese clinical query>", "expected_output": "<structured Vietnamese response>"}` covering: (1) standard moderate-risk ITP patient, (2) high-risk patient with platelet <10, (3) patient in remission (low risk), (4) query about treatment escalation, (5) non-ITP query that should be rejected with "Câu hỏi không thuộc phạm vi hệ thống ITP." | | |

### Implementation Phase 4 — Tool Implementations

- GOAL-004: Implement the 4 tool modules used by sub-agents, each with a fixture fallback mode and a real AWS service mode.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Create `src/tools/comprehend_intake.py`: define function `extract_itp_variables(clinical_note: str) -> dict`. If `ITP_USE_FIXTURES=1`, parse `src/fixtures/sample_clinical_note_vi.txt` and return a hardcoded dict with all 11 variables. If `ITP_USE_FIXTURES=0`, call `boto3.client("comprehend-medical").detect_entities_v2(Text=clinical_note)`, map detected entities (MEDICATION, MEDICAL_CONDITION, TEST_TREATMENT_PROCEDURE) to the 11 ITP variable keys using a hardcoded entity-to-variable mapping dict, and return the result dict. Handle `botocore.exceptions.ClientError` by logging the error and returning the fixture data as fallback. | | |
| TASK-018 | Create `src/tools/kb_retrieve.py`: define function `retrieve_guidelines(query: str, kb_id: str = None) -> list[dict]`. If `ITP_USE_FIXTURES=1` or `kb_id` is None/empty, load and return `src/fixtures/mock_kb_response.json` as a list of result dicts. If real KB: call `boto3.client("bedrock-agent-runtime").retrieve(knowledgeBaseId=kb_id, retrievalQuery={"text": query}, retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}})`, extract `retrievalResults`, return list of `{"content": r["content"]["text"], "source": r["location"]["s3Location"]["uri"], "score": r["score"]}` dicts. | | |
| TASK-019 | Create `src/tools/cohort_similarity.py`: define function `find_similar_patients(features: dict, top_k: int = 5) -> list[dict]`. If `ITP_USE_FIXTURES=1`, load `src/fixtures/synthetic_patients.json`, compute cosine similarity between `features` and each patient's numeric fields (`platelet_count`, `bleeding_score`, `age`, `disease_duration_months`) using `numpy`, return top-k sorted by similarity. If `ITP_USE_FIXTURES=0`, scan the DynamoDB table named by `os.getenv("ITP_COHORT_TABLE", "itp-cohort-index")` using `boto3`, deserialize `feature_vector` attribute (Binary, 11 float32 values), compute cosine similarity, return top-k. Return list of `{"patient_id": str, "similarity_pct": float, "key_features": dict, "outcome_bleeding_30d": bool|None}` dicts. | | |
| TASK-020 | Create `src/tools/code_exec.py`: define function `execute_python(code: str) -> dict`. Writes `code` to a temp file `_tmp_exec.py`, runs `subprocess.run(["uv", "run", "python", "_tmp_exec.py"], capture_output=True, text=True, timeout=10)` so the subprocess inherits the project's uv-managed venv, deletes the temp file, returns `{"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}`. If timeout is exceeded, return `{"stdout": "", "stderr": "Timeout after 10 seconds", "returncode": -1}`. This tool is used by the Risk-Reasoner Agent in all modes (fixture or real). | | |

### Implementation Phase 5 — Agent Implementations

- GOAL-005: Implement all 5 Strands Agent objects, each independently runnable and integrated into the Agents-as-Tools supervisor pattern.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-021 | Create `src/agents/intake_agent.py`: import `Agent` from `strands`, `load_prompt` from `src.utils`, `extract_itp_variables` from `src.tools.comprehend_intake`. Define a Strands `@tool`-compatible wrapper `run_intake(clinical_note: str) -> dict` that calls `extract_itp_variables(clinical_note)`. Instantiate `intake_agent = Agent(model="us.anthropic.claude-haiku-4-5-20251001-v1:0", tools=[run_intake], system_prompt=load_prompt("intake_vi.txt"))`. Add `if __name__ == "__main__":` block that reads `src/fixtures/sample_clinical_note_vi.txt` and calls `intake_agent(content)`, printing the result. | | |
| TASK-022 | Create `src/agents/risk_reasoner_agent.py`: import `Agent` from `strands`, `load_prompt` from `src.utils`, `execute_python` from `src.tools.code_exec`. Load risk priors at module level: `RISK_PRIORS = Path("data/guidelines/itp_risk_priors_v1.md").read_text()`. Instantiate `risk_reasoner_agent = Agent(model="us.anthropic.claude-haiku-4-5-20251001-v1:0", tools=[execute_python], system_prompt=load_prompt("risk_reasoner_vi.txt") + f"\n\n## Bảng trọng số nguy cơ\n{RISK_PRIORS}")`. Add standalone `__main__` block with synthetic features dict for isolated testing. | | |
| TASK-023 | Create `src/agents/guidelines_agent.py`: import `Agent` from `strands`, `load_prompt` from `src.utils`, `retrieve_guidelines` from `src.tools.kb_retrieve`. Define `@tool`-compatible wrapper `run_kb_retrieve(query: str) -> list` that calls `retrieve_guidelines(query, kb_id=os.getenv("ITP_KB_ID"))`. Instantiate `guidelines_agent = Agent(model="us.anthropic.claude-haiku-4-5-20251001-v1:0", tools=[run_kb_retrieve], system_prompt=load_prompt("guidelines_vi.txt"))`. Add standalone `__main__` block with sample Vietnamese query. | | |
| TASK-024 | Create `src/agents/cohort_lookup_agent.py`: import `Agent` from `strands`, `load_prompt` from `src.utils`, `find_similar_patients` from `src.tools.cohort_similarity`. Define `@tool`-compatible wrapper `run_cohort_lookup(features: dict) -> list` that calls `find_similar_patients(features, top_k=5)`. Instantiate `cohort_lookup_agent = Agent(model="us.anthropic.claude-haiku-4-5-20251001-v1:0", tools=[run_cohort_lookup], system_prompt=load_prompt("cohort_lookup_vi.txt"))`. Add standalone `__main__` block. | | |
| TASK-025 | Create `src/agents/supervisor_agent.py`: import `Agent`, `tool` from `strands`; import all 4 sub-agent instances. Define 4 `@tool`-decorated functions with Vietnamese docstrings: `intake_agent_tool(clinical_note: str) -> dict` calls `intake_agent(clinical_note)` and returns parsed result; `risk_reasoner_tool(features: dict) -> dict` calls `risk_reasoner_agent(str(features))` and returns parsed result; `guidelines_tool(query: str) -> dict` calls `guidelines_agent(query)` and returns result; `cohort_lookup_tool(features: dict) -> list` calls `cohort_lookup_agent(str(features))` and returns result. Instantiate `supervisor_agent = Agent(model="us.anthropic.claude-sonnet-4-5-20250929-v1:0", tools=[intake_agent_tool, risk_reasoner_tool, guidelines_tool, cohort_lookup_tool], system_prompt=load_prompt("supervisor_vi.txt"))`. | | |

### Implementation Phase 6 — CLI Entrypoint & Smoke Test

- GOAL-006: Build the `main.py` CLI and `scripts/smoke_test_local.py` validation script that confirm the full local pipeline works end-to-end.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-026 | Create `main.py` in project root: use `argparse` to define `--note` (inline string) and `--note-file` (path to .txt file) arguments; exactly one must be provided. Load `.env` with `dotenv.load_dotenv()`. Import `supervisor_agent` from `src.agents.supervisor_agent`. Call `supervisor_agent.stream(note)` and print each streamed token to stdout using `rich.console.Console().print()` with no buffering. Exit code 0 on success, 1 on exception. | | |
| TASK-027 | Create `scripts/smoke_test_local.py`: set `os.environ["ITP_USE_FIXTURES"] = "1"` before any imports. Read `src/fixtures/sample_clinical_note_vi.txt` as the test input. Import and call `supervisor_agent(note)`, capturing full response as a string. Assert (a) response length > 100 characters, (b) response contains at least one of `["Nguy cơ", "chảy máu", "tiểu cầu", "điều trị"]` (Vietnamese clinical keywords), (c) response contains `"Thấp"`, `"Trung bình"`, or `"Cao"` (risk tier label). Print `"PASSED"` and exit 0 if all assertions pass; print the failed assertion message and exit 1 otherwise. | | |
| TASK-028 | Create `README.md` section "Local Development Quickstart" (append to existing README.md): steps to (1) install uv if not present: `curl -LsSf https://astral.sh/uv/install.sh \| sh`, (2) `cp .env.example .env` and edit AWS credentials, (3) `uv sync` to install dependencies, (4) `uv run python main.py --note-file src/fixtures/sample_clinical_note_vi.txt`, (5) `ITP_USE_FIXTURES=1 uv run python scripts/smoke_test_local.py` to run the smoke test. | | |

---

## 3. Alternatives

- **ALT-001**: Use LangChain instead of Strands SDK for local agent orchestration. Rejected — the full plan (Pattern A) targets Strands SDK + AgentCore; using LangChain locally would create a local/production divergence that complicates migration. Strands SDK runs locally against Bedrock without AgentCore.
- **ALT-002**: Use the Strands built-in `code_interpreter` tool instead of the custom `src/tools/code_exec.py` subprocess tool. Deferred — the built-in `code_interpreter` tool requires AgentCore to be configured even locally (it calls AgentCore Code Interpreter service). The subprocess-based `code_exec.py` is a local substitute that will be replaced by the built-in tool in the deployment plan.
- **ALT-003**: Use a local vector store (FAISS or ChromaDB) as the Guidelines Agent knowledge base instead of real Bedrock Knowledge Bases. Not chosen as the primary path — the fixture fallback (`ITP_USE_FIXTURES=1`) already enables offline testing without a real KB. Adding a local vector store would require embedding the guideline documents locally, which adds complexity without benefit at this stage.
- **ALT-004**: Use `asyncio` for concurrent sub-agent invocation inside the Supervisor. Deferred — Strands SDK's Agents-as-Tools pattern is synchronous at this stage; concurrent invocation is possible but requires async agent support that is being validated against Strands' current API surface.

---

## 4. Dependencies

- **DEP-001**: `uv>=0.5.0` — package manager and virtual environment tool; install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `brew install uv`; must be on `PATH` before any other setup step. All dependency install and script execution commands use `uv`.
- **DEP-002**: `strands-agents>=0.1.0` — declared in `pyproject.toml`; installed by `uv sync`; verify with `uv run python -c "from strands import Agent, tool"`.
- **DEP-003**: `boto3>=1.35.0` — declared in `pyproject.toml`; used for Comprehend Medical, Bedrock Knowledge Base, and DynamoDB calls in non-fixture mode.
- **DEP-004**: `python-dotenv>=1.0.0` — declared in `pyproject.toml`; loads `.env` in `main.py`.
- **DEP-005**: `numpy>=1.26.0` — declared in `pyproject.toml`; used in `src/tools/cohort_similarity.py` for cosine similarity computation.
- **DEP-006**: `rich>=13.0.0` — declared in `pyproject.toml`; used in `main.py` for streaming token output to terminal.
- **DEP-007**: Python 3.11+ — managed by uv via `requires-python = ">=3.11"` in `pyproject.toml`; uv downloads and pins the interpreter automatically if not present.
- **DEP-008**: AWS credentials with permissions: `bedrock:InvokeModel`, `bedrock:Retrieve` (if using real KB), `comprehend-medical:DetectEntitiesV2` (if using real Comprehend), `dynamodb:Scan` (if using real DynamoDB). In fixture mode (`ITP_USE_FIXTURES=1`), no AWS credentials are needed.
- **DEP-009**: Amazon Bedrock model access must be enabled in `us-west-2` for `claude-sonnet-4-5` and `claude-haiku-4-5` via the Bedrock console Model Access page before running in non-fixture mode.

---

## 5. Files

- **FILE-001**: `pyproject.toml` — project metadata and Python dependencies declared for uv; created in TASK-002.
- **FILE-001b**: `uv.lock` — uv lockfile with fully resolved, pinned dependency tree; generated by `uv lock` in TASK-002; committed to the repository.
- **FILE-002**: `.env.example` — environment variable template; created in TASK-004.
- **FILE-003**: `src/__init__.py`, `src/agents/__init__.py`, `src/tools/__init__.py` — package init files; created in TASK-005.
- **FILE-004**: `src/utils.py` — `load_prompt()` and `get_fixture_path()` helpers; created in TASK-006.
- **FILE-005**: `src/fixtures/synthetic_patients.json` — 10 synthetic ITP patient records; created in TASK-007.
- **FILE-006**: `src/fixtures/sample_clinical_note_vi.txt` — sample Vietnamese clinical note; created in TASK-008.
- **FILE-007**: `src/fixtures/mock_kb_response.json` — mock Bedrock KB retrieval response; created in TASK-009.
- **FILE-008**: `data/guidelines/itp_risk_priors_v1.md` — literature-derived bleeding risk weights table; created in TASK-010.
- **FILE-009**: `src/agents/prompts/supervisor_vi.txt` — Supervisor Agent Vietnamese system prompt; created in TASK-011.
- **FILE-010**: `src/agents/prompts/intake_vi.txt` — Intake Agent Vietnamese system prompt; created in TASK-012.
- **FILE-011**: `src/agents/prompts/risk_reasoner_vi.txt` — Risk-Reasoner Agent Vietnamese system prompt; created in TASK-013.
- **FILE-012**: `src/agents/prompts/guidelines_vi.txt` — Guidelines Agent Vietnamese system prompt; created in TASK-014.
- **FILE-013**: `src/agents/prompts/cohort_lookup_vi.txt` — Cohort-Lookup Agent Vietnamese system prompt; created in TASK-015.
- **FILE-014**: `src/agents/prompts/few_shot_examples_vi.jsonl` — 5 Vietnamese Q&A few-shot examples; created in TASK-016.
- **FILE-015**: `src/tools/comprehend_intake.py` — Comprehend Medical wrapper with fixture fallback; created in TASK-017.
- **FILE-016**: `src/tools/kb_retrieve.py` — Bedrock Knowledge Base retrieval wrapper with fixture fallback; created in TASK-018.
- **FILE-017**: `src/tools/cohort_similarity.py` — cosine similarity search (fixture or DynamoDB); created in TASK-019.
- **FILE-018**: `src/tools/code_exec.py` — local subprocess Python execution tool; created in TASK-020.
- **FILE-019**: `src/agents/intake_agent.py` — Strands Intake Agent; created in TASK-021.
- **FILE-020**: `src/agents/risk_reasoner_agent.py` — Strands Risk-Reasoner Agent; created in TASK-022.
- **FILE-021**: `src/agents/guidelines_agent.py` — Strands Guidelines Agent; created in TASK-023.
- **FILE-022**: `src/agents/cohort_lookup_agent.py` — Strands Cohort-Lookup Agent; created in TASK-024.
- **FILE-023**: `src/agents/supervisor_agent.py` — Strands Supervisor Agent (Agents-as-Tools); created in TASK-025.
- **FILE-024**: `main.py` — CLI entrypoint; created in TASK-026.
- **FILE-025**: `scripts/smoke_test_local.py` — end-to-end smoke test (no pytest); created in TASK-027.

---

## 6. Testing

- **TEST-001**: Isolated Intake Agent test — `ITP_USE_FIXTURES=1 uv run python src/agents/intake_agent.py`; assert stdout contains a JSON dict with all 11 ITP variable keys (`platelet_count`, `bleeding_score`, `age`, `sex`, `disease_duration_months`, `prior_corticosteroid`, `corticosteroid_response`, `prior_tpo_ra`, `tpo_ra_response`, `splenectomy`, `comorbidities`). Run after TASK-021.
- **TEST-002**: Isolated Risk-Reasoner Agent test — `ITP_USE_FIXTURES=1 uv run python src/agents/risk_reasoner_agent.py`; assert stdout contains a numeric value between 0 and 100 and one of the strings `"Thấp"`, `"Trung bình"`, or `"Cao"`. Run after TASK-022.
- **TEST-003**: Isolated Guidelines Agent test — `ITP_USE_FIXTURES=1 uv run python src/agents/guidelines_agent.py`; assert stdout contains at least one `[Nguồn:` citation string. Run after TASK-023.
- **TEST-004**: Isolated Cohort-Lookup Agent test — `ITP_USE_FIXTURES=1 uv run python src/agents/cohort_lookup_agent.py`; assert stdout contains exactly 5 patient references with similarity percentage values. Run after TASK-024.
- **TEST-005**: `ITP_USE_FIXTURES=1 uv run python scripts/smoke_test_local.py` — full pipeline smoke test; asserts response length, Vietnamese keywords, and risk tier presence; exits 0 on pass. Run after TASK-027. This is the primary acceptance test for this plan.
- **TEST-006**: `ITP_USE_FIXTURES=1 uv run python main.py --note-file src/fixtures/sample_clinical_note_vi.txt` — CLI entrypoint test; assert command runs without exception and prints streaming output to stdout. Run after TASK-026.
- **TEST-007**: `uv run python main.py` with no arguments — assert exit code 1 and error message "Provide --note or --note-file". Run after TASK-026.
- **TEST-008**: Fixture-off connectivity check (optional, requires real AWS) — `ITP_USE_FIXTURES=0 uv run python src/agents/intake_agent.py`; assert no `botocore.exceptions.ClientError` and output dict contains ≥1 non-null ITP variable. Run only when AWS credentials and Bedrock access are confirmed.

---

## 7. Risks & Assumptions

- **RISK-001**: Strands SDK `Agent.stream()` API may differ from `Agent.__call__()` in token delivery format. Mitigation: check Strands changelog for streaming API documentation before TASK-026; fall back to `Agent.__call__()` with full response if streaming is not yet stable.
- **RISK-002**: Strands SDK Agents-as-Tools pattern may require sub-agent instances to be wrapped differently than `agent(input)` direct call — some SDK versions expect `agent.run(input)`. Mitigation: test TASK-025 against the exact installed version before writing the supervisor; adjust call syntax to match SDK's actual public API.
- **RISK-003**: Amazon Comprehend Medical entity detection accuracy on Vietnamese clinical text is unknown. Vietnamese is not a supported language for Comprehend Medical. Mitigation: `ITP_USE_FIXTURES=1` avoids this entirely in local dev; when real mode is needed, the Intake Agent prompt instructs Claude Haiku to pre-translate clinical terms before passing to Comprehend Medical.
- **RISK-004**: `subprocess`-based code execution in `code_exec.py` is a security risk if the Risk-Reasoner Agent generates malicious code. Mitigation: acceptable in local dev only; this tool will be replaced by AgentCore Code Interpreter (sandboxed) in the deployment plan. Add a comment in `code_exec.py`: `# LOCAL DEV ONLY — replace with AgentCore Code Interpreter in production`.
- **RISK-005**: Cosine similarity over 11 variables with different scales (platelet count 0–500 vs bleeding score 0–14) will produce biased results. Mitigation: normalize each feature to [0,1] range using known clinical min/max values before computing similarity in `cohort_similarity.py`. Document the normalization constants in the function's docstring.
- **ASSUMPTION-001**: `uv` is installed on the developer's machine before starting Phase 1; the `strands-agents` package is published on PyPI and resolvable by `uv sync` at the start of implementation.
- **ASSUMPTION-002**: Amazon Bedrock model access for `claude-sonnet-4-5` and `claude-haiku-4-5` cross-region inference profiles is already enabled in the developer's AWS account in `us-west-2`.
- **ASSUMPTION-003**: `ITP_USE_FIXTURES=1` mode is sufficient for all development and review until AWS infrastructure (DynamoDB, Knowledge Bases) is provisioned in a subsequent plan.
- **ASSUMPTION-004**: The Strands SDK `@tool` decorator accepts regular Python functions that call other `Agent` instances directly (in-process); no async event loop or thread isolation is required for local dev.

---

## 8. Related Specifications / Further Reading

- [Full ITP Multi-Agent Implementation Plan (all phases)](./feature-itp-multiagent-strands-1.md)
- [ITP Architecture Plan v0.0.6](../plans/itp_plan_v6.md)
- [Strands Agents SDK — Agents as Tools pattern](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/)
- [Strands Agents SDK — Getting Started](https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/)
- [Amazon Bedrock cross-region inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles.html)
- [Amazon Comprehend Medical — DetectEntitiesV2](https://docs.aws.amazon.com/comprehend-medical/latest/dev/extracted-information.html)
