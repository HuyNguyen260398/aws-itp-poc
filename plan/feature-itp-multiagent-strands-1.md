---
goal: Build ITP Bleeding Risk Prediction Multi-Agent System using AWS Strands Agents SDK
version: 1.0
date_created: 2026-05-10
last_updated: 2026-05-10
owner: Huy (Software Engineer) + Trần Xuân Nhiên (Researcher)
status: 'Planned'
tags: [feature, architecture, multi-agent, aws, strands-sdk, bedrock, agentcore, clinical-ai]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan covers the end-to-end implementation of the ITP (Primary Immune Thrombocytopenia) bleeding risk prediction multi-agent system for Trần Xuân Nhiên's master's thesis (2025–2027). The system uses the AWS Strands Agents SDK to implement a supervisor + 4 specialist agent topology on Amazon Bedrock AgentCore, providing Vietnamese-language clinical decision support for hematologists at BV Truyền máu Huyết học.

The implementation follows a staged migration: **Pattern B** (Bedrock Multi-Agent Collaboration, Months 3–4) provides a fast prototype to validate agent prompts and RAG pipelines; **Pattern A** (AgentCore + Strands SDK, Months 5–6) delivers the production-grade system with JWT isolation, OpenTelemetry tracing, and AgentCore Memory. This plan focuses on Pattern A — the Strands SDK implementation — building on a stable Pattern B prototype.

---

## 1. Requirements & Constraints

- **REQ-001**: Supervisor agent must orchestrate 4 specialist sub-agents (Intake, Risk-Reasoner, Guidelines, Cohort-Lookup) using the Strands Agents-as-Tools pattern — each sub-agent invoked as a typed Python `@tool` function.
- **REQ-002**: Intake Agent must extract exactly 11 ITP clinical variables from unstructured Vietnamese clinical notes using Amazon Comprehend Medical as a Strands tool.
- **REQ-003**: Risk-Reasoner Agent must compute a literature-anchored bleeding risk score using AgentCore Code Interpreter; risk priors must be stored in a Bedrock Knowledge Base document (not hardcoded) so the researcher can update them without redeployment.
- **REQ-004**: Guidelines Agent must perform RAG retrieval over ASH/ISTH/BV TMHH guideline documents ingested into a Bedrock Knowledge Base backed by OpenSearch Serverless.
- **REQ-005**: Cohort-Lookup Agent must query a DynamoDB table to return the 5 most similar past ITP patients by feature vector distance.
- **REQ-006**: All 5 agents (supervisor + 4 specialists) must run on separate AgentCore Runtime instances (serverless ARM64 microVMs).
- **REQ-007**: AgentCore Memory must be configured with short-term (current chat session) and long-term (clinician preferences) strategies; memory ID `ITP_MEMORY_ID` must be provisioned before agent deployment.
- **REQ-008**: AgentCore Gateway must expose 8 MCP endpoints backed by Lambda functions; all tool calls from agents must route through the Gateway.
- **REQ-009**: Frontend must be a React.js application with Vietnamese i18n, real-time SSE streaming from the supervisor agent endpoint, and Cognito-based clinician authentication.
- **REQ-010**: Infrastructure must be defined as AWS CDK v2.220+ stacks — one CDK stack per AgentCore Runtime plus one shared-infra stack; all stacks must be deployable independently via `cdk deploy <StackName>`.
- **REQ-011**: Foundation models: Claude Sonnet 4.5 (`us.anthropic.claude-sonnet-4-5-20250929-v1:0`) for the supervisor; Claude Haiku 4.5 (`global.anthropic.claude-haiku-4-5-20251001-v1:0`) for the 4 sub-agents.
- **SEC-001**: JWT tokens issued by Cognito must be validated at every AgentCore Runtime boundary and AgentCore Gateway call; no unauthenticated invocation is permitted.
- **SEC-002**: No patient PHI may appear in CloudWatch logs; Lambda functions must strip identifiable fields before logging.
- **SEC-003**: Bedrock Guardrails must be applied to all Bedrock model invocations to filter PHI and restrict LLM scope to ITP/hematology topics.
- **SEC-004**: All data at rest must be encrypted with KMS customer-managed keys; all data in transit must use TLS 1.2+.
- **SEC-005**: IAM roles must follow least-privilege: separate data role (S3/DynamoDB read), agent role (Bedrock/AgentCore invoke), and app role (Cognito/CloudFront) with no cross-role elevation.
- **CON-001**: AgentCore Runtime is available only in `us-east-1` and `us-west-2`; the primary deployment region is `us-west-2` (lowest RTT from Vietnam, ~250ms).
- **CON-002**: OpenSearch Serverless has a cost floor of ~$350/month regardless of usage; this is accepted and budgeted in Option A (~$540–745/month total).
- **CON-003**: Docker ARM64 images are required for AgentCore Runtime (Graviton); all `cdk synth`/`cdk deploy` commands must be run on an ARM64 machine (Apple Silicon or AWS Graviton) or with cross-compilation configured.
- **CON-004**: The Strands Agents SDK (`strands-agents`) must be pinned to the version that shipped AgentCore Memory `SessionManager` support; verify compatibility before upgrading.
- **CON-005**: All patient data used during development and evaluation must be de-identified; real PHI must never enter any AWS account used for this project.
- **GUD-001**: Follow the AWS reference implementation structure from `aws-solutions-library-samples/guidance-for-multi-agent-orchestration-using-bedrock-agentcore-on-aws` — directories: `agents/`, `frontend/`, `infrastructure/`, `lambda/`.
- **GUD-002**: System prompts must be stored as external `.txt` files (e.g., `supervisor_vi.txt`, `intake_vi.txt`) loadable at agent startup via `load_prompt()` — never inline strings in Python code.
- **GUD-003**: Agent response language must default to Vietnamese; English is used only for internal tool call parameters and Lambda payloads.
- **PAT-001**: Use the Strands Agents-as-Tools pattern exclusively for supervisor→sub-agent delegation; do NOT use Bedrock `AssociateAgentCollaborator` API in Pattern A.
- **PAT-002**: Each CDK stack must use `cdk diff` before `cdk deploy` in CI; no blind deploys.

---

## 2. Implementation Steps

### Implementation Phase 1 — AWS Foundation & Data Engineering (Months 1–2)

- GOAL-001: Provision the AWS account baseline, data lake, cohort index, and guideline knowledge base so all subsequent phases have a stable data layer to build against.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create AWS account structure: enable `us-west-2` as primary region; enable AWS Organizations SCP to block `us-east-1` as fallback; tag all resources with `project=itp-poc`, `env=dev\|staging\|prod` | | |
| TASK-002 | Bootstrap CDK in `us-west-2`: run `cdk bootstrap aws://<ACCOUNT_ID>/us-west-2`; commit bootstrap outputs to `infrastructure/bootstrap-outputs.json` | | |
| TASK-003 | Create shared-infra CDK stack `ITPSharedInfraStack` in `infrastructure/stacks/shared_infra.py`: provisions S3 data lake bucket (versioning + KMS), DynamoDB cohort table (partition key: `patient_id`, sort key: `admission_date`), KMS CMK, CloudWatch log groups with 7-day retention | | |
| TASK-004 | Write Glue ETL job in `src/etl/glue_itp_transform.py`: reads raw CSV from `s3://itp-data-lake/raw/`, applies de-identification (drop `name`, `dob`, `address`, `mrn`), outputs Parquet to `s3://itp-data-lake/processed/`; register as a Glue job named `itp-deidentify-transform` | | |
| TASK-005 | Build DynamoDB cohort index loader in `src/etl/load_cohort_index.py`: reads processed Parquet, computes normalized feature vectors for the 11 ITP variables (platelet count, bleeding score, treatment history, age, sex, disease duration, prior treatments, comorbidities, corticosteroid response, TPO-RA response, splenectomy status), writes one item per patient to DynamoDB with attribute `feature_vector` (Binary, 44 bytes for 11 float32 values) | | |
| TASK-006 | Ingest guideline documents into Bedrock Knowledge Base: upload ASH 2019, ISTH 2020, BV TMHH internal protocol PDFs to `s3://itp-data-lake/guidelines/`; create Knowledge Base `itp-guidelines-kb` via CDK using `aws_bedrock.CfnKnowledgeBase` with OpenSearch Serverless collection `itp-guidelines-vectors`; run initial sync | | |
| TASK-007 | Create risk-priors Knowledge Base document `data/guidelines/itp_risk_priors_v1.md`: structured Markdown table of literature-derived bleeding risk weights per ITP variable (format: `| Variable | Low-risk threshold | High-risk threshold | Odds Ratio | Source |`); ingest into separate KB `itp-priors-kb` | | |
| TASK-008 | Verify data layer: run `scripts/verify_data_layer.py` which asserts (a) DynamoDB table contains ≥1 item, (b) both KBs report sync status `COMPLETE`, (c) S3 processed prefix contains `.parquet` files, (d) KMS key is enabled | | |

### Implementation Phase 2a — Pattern B Prototype (Months 3–4)

- GOAL-002: Build a working Pattern B prototype (Bedrock Multi-Agent Collaboration) to validate agent prompts, RAG quality, and the end-to-end clinical workflow before committing to AgentCore infrastructure.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-009 | Write system prompts for all 5 agents in `src/agents/prompts/`: `supervisor_vi.txt` (Vietnamese orchestration instructions, tool delegation rules), `intake_vi.txt` (11-variable extraction schema), `risk_reasoner_vi.txt` (code-based scoring instructions), `guidelines_vi.txt` (RAG + citation formatting), `cohort_lookup_vi.txt` (similarity search instructions) | | |
| TASK-010 | Create Bedrock Multi-Agent Collaboration supervisor via AWS Console or Boto3 script `scripts/create_pattern_b_agents.py`: supervisor model = Claude Sonnet 4.5, 4 sub-agents model = Claude Haiku 4.5; associate Knowledge Base `itp-guidelines-kb` with Guidelines sub-agent | | |
| TASK-011 | Implement Lambda action group `src/lambda/cohort_lookup/handler.py`: receives `features` dict (11 variables), reads all DynamoDB items, computes cosine similarity vs query vector using numpy, returns top-5 matches with `patient_id`, `similarity_score`, `key_features`; deploy as Lambda function `itp-cohort-lookup` with DynamoDB read-only IAM role | | |
| TASK-012 | Implement Lambda action group `src/lambda/comprehend_intake/handler.py`: receives `clinical_note` string (Vietnamese), calls `comprehend_medical:DetectEntitiesV2`, maps detected entities to the 11 ITP variable schema, returns structured dict; deploy as Lambda function `itp-comprehend-intake` | | |
| TASK-013 | Create 20 Vietnamese clinical Q&A few-shot examples in `src/agents/prompts/few_shot_examples_vi.jsonl`: each line = `{"input": "<Vietnamese clinical query>", "expected_output": "<structured agent response with citations>"}` covering standard cases, edge cases (low platelet but no bleeding), and rejection cases (non-ITP queries) | | |
| TASK-014 | Run Pattern B end-to-end tests using `scripts/test_pattern_b.py`: sends 5 synthetic Vietnamese clinical notes through the Bedrock multi-agent system, asserts all 11 variables extracted in Intake output, asserts Risk-Reasoner returns a score between 0.0–1.0, asserts Guidelines response contains ≥1 citation | | |
| TASK-015 | Latency profiling: run `scripts/profile_latency.py` logging time-to-first-token and total-completion-time for 10 requests; record results in `docs/latency_profile_pattern_b.md`; decision threshold: if P95 total completion > 30s, flag for optimization before Pattern A migration | | |
| TASK-016 | **Decision point**: review prompt quality, RAG accuracy, and latency results; decide Pattern A migration (continue to Phase 2b) or remain on Pattern B (skip to Phase 3) | | |

### Implementation Phase 2b — Pattern A: Strands SDK & AgentCore (Months 5–6)

- GOAL-003: Migrate the stable Pattern B prototype to Pattern A — rewrite agents with Strands SDK, deploy to AgentCore Runtimes, configure JWT propagation and AgentCore Memory, and wire AgentCore Gateway for all tool calls.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-017 | Install Strands SDK: add `strands-agents>=0.1.0`, `strands-agents-tools>=0.1.0`, `amazon-bedrock-agentcore>=0.1.0` to `src/agents/requirements.txt`; pin versions in `src/agents/requirements.lock` | | |
| TASK-018 | Implement Intake Agent in `src/agents/intake_agent.py`: Strands `Agent` with model `claude-haiku-4-5`, system prompt loaded from `prompts/intake_vi.txt`, tool = `comprehend_intake` MCP endpoint via AgentCore Gateway; expose as AgentCore Runtime-compatible handler function `handler(event, context)` | | |
| TASK-019 | Implement Risk-Reasoner Agent in `src/agents/risk_reasoner_agent.py`: Strands `Agent` with model `claude-haiku-4-5`, tools = `[code_interpreter, knowledge_base("itp-priors-kb")]`; system prompt from `prompts/risk_reasoner_vi.txt`; the agent must generate Python code that computes a weighted score from the 11 features using priors fetched from the KB | | |
| TASK-020 | Implement Guidelines Agent in `src/agents/guidelines_agent.py`: Strands `Agent` with model `claude-haiku-4-5`, tool = Bedrock Knowledge Base retrieval for `itp-guidelines-kb`; response must include inline citations in format `[ASH 2019, p.X]`; system prompt from `prompts/guidelines_vi.txt` | | |
| TASK-021 | Implement Cohort-Lookup Agent in `src/agents/cohort_lookup_agent.py`: Strands `Agent` with model `claude-haiku-4-5`, tool = `cohort_lookup` MCP endpoint via AgentCore Gateway; response format: top-5 similar patients with similarity score and key differentiating features; system prompt from `prompts/cohort_lookup_vi.txt` | | |
| TASK-022 | Implement Supervisor Agent in `src/agents/supervisor_agent.py` using Strands Agents-as-Tools pattern: define 4 `@tool`-decorated functions (`intake_agent_tool`, `risk_reasoner_tool`, `guidelines_tool`, `cohort_lookup_tool`) each calling `invoke_runtime("<agent-arn>", payload=...)` with JWT forwarding; instantiate `Agent` with model `claude-sonnet-4-5`, all 4 tool functions, system prompt from `prompts/supervisor_vi.txt`, and `AgentCoreMemorySessionManager(memory_id=ITP_MEMORY_ID)` | | |
| TASK-023 | Dockerize all 5 agents: create `src/agents/Dockerfile` (multi-stage, Python 3.11 slim, ARM64 target `--platform linux/arm64`); build and push to 5 ECR repos (`itp-supervisor`, `itp-intake`, `itp-risk-reasoner`, `itp-guidelines`, `itp-cohort-lookup`) via `scripts/build_and_push.sh` | | |
| TASK-024 | Implement 8 Lambda MCP tool functions under `src/lambda/`: `comprehend_intake/`, `cohort_lookup/`, `kb_retrieve/`, `code_exec_wrapper/`, `patient_summary/`, `treatment_history/`, `platelet_trend/`, `risk_score_cache/`; each handler must accept MCP-format JSON `{"tool": "<name>", "parameters": {...}}` and return `{"result": ..., "error": null}` | | |
| TASK-025 | Create CDK stack `ITPAgentCoreGatewayStack` in `infrastructure/stacks/agentcore_gateway.py`: provisions AgentCore Gateway with 8 MCP endpoint configurations pointing to the 8 Lambda ARNs; attach IAM policy granting each AgentCore Runtime role `bedrock:InvokeAgentCoreGateway` | | |
| TASK-026 | Create CDK stack `ITPAgentCoreMemoryStack` in `infrastructure/stacks/agentcore_memory.py`: provisions AgentCore Memory with strategies `[SHORT_TERM_CONVERSATION, LONG_TERM_USER_PREFERENCE]`, retention 60 days, output `ITP_MEMORY_ID` as SSM parameter `/itp/agentcore/memory-id` | | |
| TASK-027 | Create 5 AgentCore Runtime CDK stacks in `infrastructure/stacks/`: `SupervisorRuntimeStack`, `IntakeRuntimeStack`, `RiskReasonerRuntimeStack`, `GuidelinesRuntimeStack`, `CohortLookupRuntimeStack`; each stack provisions one `CfnAgentCoreRuntime` with ECR image URI, ARM64 architecture, environment variables (`MEMORY_ID`, `GATEWAY_ENDPOINT`, `KB_ID`), and IAM execution role | | |
| TASK-028 | Configure JWT propagation: in each AgentCore Runtime stack, set `authorizationConfig` to `AMAZON_COGNITO` with the Cognito User Pool ARN; in `supervisor_agent.py`, extract JWT from incoming request context and pass as `x-agent-jwt` header in all `invoke_runtime()` calls | | |
| TASK-029 | Enable AgentCore Observability: in each Runtime stack, set `observabilityConfig.enabled=True`; create CloudWatch dashboard `ITPAgentDashboard` with widgets for invocation count, P50/P95 latency, and error rate per agent; set log retention to 7 days | | |
| TASK-030 | Deploy all CDK stacks in order: `ITPSharedInfraStack` → `ITPAgentCoreMemoryStack` → `ITPAgentCoreGatewayStack` → 5 Runtime stacks; run `cdk diff <StackName>` before each `cdk deploy`; record stack outputs in `docs/stack_outputs.json` | | |
| TASK-031 | Run Pattern A integration tests via `scripts/test_pattern_a.py`: invoke supervisor Runtime endpoint with a signed JWT from Cognito test user, assert SSE stream produces `intake_result`, `risk_score`, `guidelines`, `cohort_matches` events within 60s; assert CloudWatch traces show all 5 agent spans | | |

### Implementation Phase 3 — React Frontend (Month 7)

- GOAL-004: Build a Vietnamese-language React frontend that authenticates clinicians via Cognito, streams agent responses via SSE, and renders the structured clinical output (risk panel, citation panel, cohort panel, audit log).

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-032 | Scaffold React app in `src/frontend/` using Vite + TypeScript: run `npm create vite@latest frontend -- --template react-ts`; add dependencies `aws-amplify`, `@aws-amplify/ui-react`, `react-i18next`, `i18next` | | |
| TASK-033 | Configure AWS Amplify Auth in `src/frontend/src/amplifyConfig.ts`: set `Auth.Cognito.userPoolId`, `userPoolClientId`, `identityPoolId` from CDK stack outputs; wrap `<App>` with `<Authenticator>` component using Vietnamese labels via i18n overrides | | |
| TASK-034 | Implement SSE streaming hook `src/frontend/src/hooks/useAgentStream.ts`: opens `EventSource` to supervisor AgentCore Runtime endpoint with `Authorization: Bearer <JWT>` header via `fetch` + `ReadableStream`; parses SSE event types (`intake_result`, `risk_score`, `guidelines`, `cohort_matches`, `error`, `done`); exposes `{ status, intakeResult, riskScore, guidelines, cohortMatches, error }` state | | |
| TASK-035 | Build clinical query form component `src/frontend/src/components/ClinicalQueryForm.tsx`: textarea for Vietnamese clinical note input (min 50 chars), patient ID field, submit button; on submit, calls `useAgentStream` hook; all labels and placeholders in Vietnamese via `src/frontend/src/i18n/vi.json` | | |
| TASK-036 | Build risk panel component `src/frontend/src/components/RiskPanel.tsx`: displays computed bleeding risk score as a gauge (0–100), color-coded (green <30, yellow 30–70, red >70), plus the 11 extracted ITP variable values in a structured table | | |
| TASK-037 | Build citation panel component `src/frontend/src/components/CitationPanel.tsx`: renders guidelines agent response with inline citations linked to source documents; each citation `[ASH 2019, p.X]` renders as a tooltip showing the full guideline excerpt | | |
| TASK-038 | Build cohort panel component `src/frontend/src/components/CohortPanel.tsx`: renders top-5 similar patients as cards showing similarity score (%), key matching features, and outcome (if available); patient IDs displayed as anonymized hashes | | |
| TASK-039 | Build audit log viewer `src/frontend/src/components/AuditLogViewer.tsx`: fetches last 20 CloudWatch log events for the current session from a Lambda proxy endpoint `GET /api/audit?sessionId=<id>`; displays timestamp, agent name, action, and truncated input/output | | |
| TASK-040 | Create CDK stack `ITPFrontendStack` in `infrastructure/stacks/frontend.py`: S3 bucket (static hosting), CloudFront distribution (OAC, HTTPS only), WAF WebACL (managed rules: AWSManagedRulesCommonRuleSet + AWSManagedRulesBotControlRuleSet), Cognito User Pool + App Client; output CloudFront URL | | |
| TASK-041 | Build and deploy frontend: run `npm run build` in `src/frontend/`, sync `dist/` to S3 via `aws s3 sync`, create CloudFront invalidation `/*`; verify app loads at CloudFront URL with Cognito login page in Vietnamese | | |

### Implementation Phase 4 — Clinical Evaluation (Months 7–8)

- GOAL-005: Conduct a 50-case prospective study comparing the system's bleeding risk recommendations against 3 hematologists' judgments using pre-registered evaluation metrics.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-042 | Prepare 50 de-identified ITP case summaries in `data/evaluation/cases_v1.jsonl`: each case = `{"case_id": "E001", "clinical_note_vi": "...", "true_bleeding_event_30d": true|false, "hematologist_risk_scores": [0–4, 0–4, 0–4]}` | | |
| TASK-043 | Write evaluation runner `scripts/run_evaluation.py`: for each case, invoke supervisor endpoint, record system risk score (0–100) and risk tier (low/moderate/high), log to `data/evaluation/results_v1.jsonl`; include retry logic (3 attempts, exponential backoff) | | |
| TASK-044 | Compute evaluation metrics in `scripts/compute_metrics.py`: inter-rater agreement (Cohen's κ) between system and each hematologist, sensitivity and specificity for bleeding event prediction, Likert satisfaction scores (1–5 scale, collected via separate form); output to `docs/evaluation_results.md` | | |
| TASK-045 | Manual audit: randomly sample 30 cases from results, review agent reasoning traces in CloudWatch for hallucinated citations or incorrect variable extraction; record findings in `docs/audit_findings.md` | | |

### Implementation Phase 5 — Analysis & Thesis Writing (Month 9)

- GOAL-006: Synthesize evaluation results into thesis chapter deliverables and prepare the system for thesis committee review.

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-046 | Generate architecture diagrams: use `scripts/generate_diagrams.py` with the `diagrams` Python library to produce `docs/architecture_pattern_a.png` (full AgentCore stack) and `docs/architecture_pattern_b.png` (Bedrock-managed) | | |
| TASK-047 | Write thesis Chapter 3 (System Design) draft covering: agent topology, Strands Agents-as-Tools pattern, AgentCore Memory strategies, knowledge base design, CDK deployment model | | |
| TASK-048 | Write thesis Chapter 4 (Results) draft: evaluation metrics table, κ agreement analysis, latency profile comparison (Pattern B vs Pattern A), cost analysis (actual vs projected) | | |
| TASK-049 | Prepare thesis committee demo environment: deploy a stable tagged version to staging environment; create demo script `scripts/demo_5_cases.py` that runs 5 curated cases end-to-end in front of the committee | | |

---

## 3. Alternatives

- **ALT-001**: Pattern C — LangGraph on ECS. Rejected because Huy has no existing LangGraph codebase to bring forward, ECS cluster overhead adds ~$200/month with no functional benefit over AgentCore, and Strands SDK provides the same orchestration patterns (graph, swarm, workflow) with native AgentCore integration.
- **ALT-002**: Keep Pattern B as the final architecture (no Pattern A migration). Valid if Pattern B prototype latency is acceptable and cost reduction ($173–318/month vs $540–745/month) outweighs the loss of JWT isolation and OpenTelemetry tracing. Decision deferred to end of Phase 2a (TASK-016).
- **ALT-003**: SageMaker Endpoints for risk scoring instead of AgentCore Code Interpreter. Rejected per v0.0.5 § 2 — LLM agents underperform classical XGBoost on tabular prediction; the academic contribution is the agentic literature-reasoning approach, not a trained ML model. Using Code Interpreter with knowledge-base priors avoids SageMaker training costs and reframes the thesis contribution correctly.
- **ALT-004**: Aurora Serverless v2 (pgvector) as the vector store for Pattern A. Rejected because the OpenSearch Serverless cost floor is already budgeted in Option A, and pgvector's approximate nearest-neighbor performance degrades beyond 1M vectors while OpenSearch Serverless scales without capacity planning.
- **ALT-005**: A2A (Agent-to-Agent) protocol for supervisor→sub-agent communication instead of Strands Agents-as-Tools. Deferred to post-thesis work — A2A adds complexity and requires a second AgentCore Runtime invocation path; Agents-as-Tools is simpler and the canonical Strands pattern for this topology.

---

## 4. Dependencies

- **DEP-001**: `strands-agents>=0.1.0` — Strands Agents SDK (open source, no AWS fee); must support `AgentCoreMemorySessionManager` and `@tool` decorator for sub-agent wrapping.
- **DEP-002**: `amazon-bedrock-agentcore>=0.1.0` — AgentCore Python SDK; required for `invoke_runtime()`, Memory, and Gateway client calls.
- **DEP-003**: `aws-cdk-lib>=2.220.0` — CDK v2 library; version must include `aws_bedrock.CfnAgentCoreRuntime` and `CfnKnowledgeBase` L1 constructs.
- **DEP-004**: `boto3>=1.35.0` — AWS SDK for Python; used in Lambda functions and ETL scripts.
- **DEP-005**: `numpy>=1.26.0` — used in cohort similarity computation (`src/lambda/cohort_lookup/handler.py`).
- **DEP-006**: Docker with `buildx` and `--platform linux/arm64` support — required for building AgentCore Runtime images; recommend running on Apple Silicon or AWS Graviton instance.
- **DEP-007**: Node.js 20+ and npm 10+ — required for React frontend build and CDK CLI.
- **DEP-008**: AWS CLI v2 configured with credentials for `us-west-2` deployment account.
- **DEP-009**: Bedrock Knowledge Bases service must be enabled in `us-west-2` with at least 2 KB quotas available.
- **DEP-010**: OpenSearch Serverless must be enabled in `us-west-2`; request quota increase for collections if default (2) is insufficient.
- **DEP-011**: AgentCore Runtime service quota: default is 5 runtimes; this project needs exactly 5 — no quota increase required unless other runtimes exist in the account.
- **DEP-012**: Amazon Comprehend Medical must be enabled in `us-west-2`; note it does not natively support Vietnamese — the intake agent prompt must instruct Claude to transliterate clinical terms before passing to Comprehend Medical.

---

## 5. Files

- **FILE-001**: `infrastructure/stacks/shared_infra.py` — CDK stack for S3, DynamoDB, KMS, CloudWatch; created in TASK-003.
- **FILE-002**: `infrastructure/stacks/agentcore_gateway.py` — CDK stack for AgentCore Gateway + 8 MCP endpoints; created in TASK-025.
- **FILE-003**: `infrastructure/stacks/agentcore_memory.py` — CDK stack for AgentCore Memory; created in TASK-026.
- **FILE-004**: `infrastructure/stacks/supervisor_runtime.py` — CDK stack for Supervisor AgentCore Runtime; created in TASK-027.
- **FILE-005**: `infrastructure/stacks/intake_runtime.py` — CDK stack for Intake AgentCore Runtime; created in TASK-027.
- **FILE-006**: `infrastructure/stacks/risk_reasoner_runtime.py` — CDK stack for Risk-Reasoner AgentCore Runtime; created in TASK-027.
- **FILE-007**: `infrastructure/stacks/guidelines_runtime.py` — CDK stack for Guidelines AgentCore Runtime; created in TASK-027.
- **FILE-008**: `infrastructure/stacks/cohort_lookup_runtime.py` — CDK stack for Cohort-Lookup AgentCore Runtime; created in TASK-027.
- **FILE-009**: `infrastructure/stacks/frontend.py` — CDK stack for S3, CloudFront, WAF, Cognito; created in TASK-040.
- **FILE-010**: `src/agents/supervisor_agent.py` — Strands Supervisor Agent with Agents-as-Tools pattern; created in TASK-022.
- **FILE-011**: `src/agents/intake_agent.py` — Strands Intake Agent; created in TASK-018.
- **FILE-012**: `src/agents/risk_reasoner_agent.py` — Strands Risk-Reasoner Agent; created in TASK-019.
- **FILE-013**: `src/agents/guidelines_agent.py` — Strands Guidelines Agent; created in TASK-020.
- **FILE-014**: `src/agents/cohort_lookup_agent.py` — Strands Cohort-Lookup Agent; created in TASK-021.
- **FILE-015**: `src/agents/Dockerfile` — multi-stage ARM64 Docker image for all agents; created in TASK-023.
- **FILE-016**: `src/agents/prompts/supervisor_vi.txt` — Vietnamese supervisor system prompt; created in TASK-009.
- **FILE-017**: `src/agents/prompts/intake_vi.txt` — Vietnamese intake extraction system prompt; created in TASK-009.
- **FILE-018**: `src/agents/prompts/risk_reasoner_vi.txt` — Vietnamese risk reasoning system prompt; created in TASK-009.
- **FILE-019**: `src/agents/prompts/guidelines_vi.txt` — Vietnamese guidelines RAG system prompt; created in TASK-009.
- **FILE-020**: `src/agents/prompts/cohort_lookup_vi.txt` — Vietnamese cohort lookup system prompt; created in TASK-009.
- **FILE-021**: `src/agents/prompts/few_shot_examples_vi.jsonl` — 20 Vietnamese Q&A examples; created in TASK-013.
- **FILE-022**: `src/lambda/comprehend_intake/handler.py` — Comprehend Medical NER Lambda; created in TASK-012.
- **FILE-023**: `src/lambda/cohort_lookup/handler.py` — DynamoDB cosine similarity Lambda; created in TASK-011.
- **FILE-024**: `src/lambda/kb_retrieve/handler.py` — Knowledge Base retrieval proxy Lambda; created in TASK-024.
- **FILE-025**: `src/lambda/code_exec_wrapper/handler.py` — Code Interpreter invocation Lambda; created in TASK-024.
- **FILE-026**: `src/lambda/patient_summary/handler.py` — Patient summary lookup Lambda; created in TASK-024.
- **FILE-027**: `src/lambda/treatment_history/handler.py` — Treatment history lookup Lambda; created in TASK-024.
- **FILE-028**: `src/lambda/platelet_trend/handler.py` — Platelet trend query Lambda; created in TASK-024.
- **FILE-029**: `src/lambda/risk_score_cache/handler.py` — Risk score caching Lambda; created in TASK-024.
- **FILE-030**: `src/etl/glue_itp_transform.py` — Glue ETL de-identification job; created in TASK-004.
- **FILE-031**: `src/etl/load_cohort_index.py` — DynamoDB cohort index loader; created in TASK-005.
- **FILE-032**: `src/frontend/src/hooks/useAgentStream.ts` — SSE streaming React hook; created in TASK-034.
- **FILE-033**: `src/frontend/src/components/ClinicalQueryForm.tsx` — Clinical note input form; created in TASK-035.
- **FILE-034**: `src/frontend/src/components/RiskPanel.tsx` — Bleeding risk gauge component; created in TASK-036.
- **FILE-035**: `src/frontend/src/components/CitationPanel.tsx` — Guidelines citation panel; created in TASK-037.
- **FILE-036**: `src/frontend/src/components/CohortPanel.tsx` — Similar patient cards panel; created in TASK-038.
- **FILE-037**: `src/frontend/src/components/AuditLogViewer.tsx` — Session audit log viewer; created in TASK-039.
- **FILE-038**: `data/guidelines/itp_risk_priors_v1.md` — Literature-derived bleeding risk priors document; created in TASK-007.
- **FILE-039**: `data/evaluation/cases_v1.jsonl` — 50 de-identified evaluation cases; created in TASK-042.
- **FILE-040**: `scripts/verify_data_layer.py` — Data layer validation script; created in TASK-008.
- **FILE-041**: `scripts/test_pattern_b.py` — Pattern B end-to-end test runner; created in TASK-014.
- **FILE-042**: `scripts/test_pattern_a.py` — Pattern A integration test runner; created in TASK-031.
- **FILE-043**: `scripts/run_evaluation.py` — Clinical evaluation batch runner; created in TASK-043.
- **FILE-044**: `scripts/compute_metrics.py` — Cohen's κ and metric computation; created in TASK-044.
- **FILE-045**: `docs/stack_outputs.json` — CDK stack output values (ARNs, endpoints, IDs); created in TASK-030.
- **FILE-046**: `infrastructure/app.py` — CDK app entry point; instantiates all stacks with correct dependency ordering.

---

## 6. Testing

- **TEST-001**: `scripts/verify_data_layer.py` — asserts DynamoDB has ≥1 item, both KBs report `COMPLETE` sync, S3 processed prefix has `.parquet` files, KMS key is enabled. Run after TASK-008.
- **TEST-002**: `scripts/test_pattern_b.py` — sends 5 synthetic Vietnamese clinical notes through Bedrock multi-agent system; asserts all 11 ITP variables present in Intake output JSON, Risk-Reasoner score ∈ [0.0, 1.0], Guidelines response contains ≥1 citation string matching `\[ASH|ISTH|BV TMHH`. Run after TASK-014.
- **TEST-003**: `scripts/profile_latency.py` — records time-to-first-token and total completion time for 10 requests; asserts P95 total completion ≤ 30s. Run after TASK-015.
- **TEST-004**: Unit test `src/lambda/cohort_lookup/test_handler.py` — mocks DynamoDB scan response with 10 synthetic patients, asserts handler returns exactly 5 items sorted by similarity descending, similarity scores ∈ [0.0, 1.0]. Run after TASK-011.
- **TEST-005**: Unit test `src/lambda/comprehend_intake/test_handler.py` — sends a fixture Vietnamese clinical note to Comprehend Medical (or mocked response), asserts output dict contains exactly the 11 ITP variable keys with non-null values. Run after TASK-012.
- **TEST-006**: `scripts/test_pattern_a.py` — invokes supervisor AgentCore Runtime endpoint with a signed Cognito JWT, sends a Vietnamese clinical note, asserts SSE stream emits events `intake_result`, `risk_score`, `guidelines`, `cohort_matches`, and `done` within 60s; asserts CloudWatch X-Ray trace shows 5 distinct agent spans. Run after TASK-031.
- **TEST-007**: JWT rejection test in `scripts/test_pattern_a.py` — sends request to supervisor Runtime without Authorization header; asserts HTTP 401 response. Run after TASK-028.
- **TEST-008**: CDK diff test — `scripts/ci_cdk_diff.sh` runs `cdk diff <StackName>` for all 9 stacks; CI pipeline fails if any stack diff shows unexpected resource deletions. Run on every PR.
- **TEST-009**: Frontend Cognito auth test — manual: open CloudFront URL in browser, verify Vietnamese login page loads, sign in with test clinician credentials, verify redirect to clinical query form. Run after TASK-041.
- **TEST-010**: `scripts/run_evaluation.py` — processes all 50 evaluation cases; asserts all 50 complete without exception (retry failures are logged but not counted as test failures). Run during Phase 4.
- **TEST-011**: `scripts/compute_metrics.py` — asserts Cohen's κ is computed for all 3 hematologist pairs, outputs are written to `docs/evaluation_results.md`. Run after TASK-044.

---

## 7. Risks & Assumptions

- **RISK-001**: AgentCore ARM64 Docker builds on x86 machines take 15–20 minutes per image. Mitigation: use Apple Silicon Mac or AWS Graviton build instance; cache Docker layers aggressively in ECR; add `--cache-from` flag to `docker buildx build`.
- **RISK-002**: AgentCore Runtime availability is limited to `us-east-1` and `us-west-2`. If `ap-southeast-1` becomes GA before Phase 2b, migrate to reduce RTT from Vietnam to ~30ms vs ~250ms. Monitor AWS service announcements monthly.
- **RISK-003**: OpenSearch Serverless $350/month cost floor may exceed budget if the thesis committee requires a cost reduction. Mitigation: fall back to Aurora Serverless v2 pgvector (stays on Pattern B) per ALT-004.
- **RISK-004**: Amazon Comprehend Medical does not natively support Vietnamese. Mitigation: Intake Agent prompt instructs Claude Haiku to transliterate Vietnamese clinical terms to English before Comprehend Medical call; validate extraction accuracy on 20 synthetic notes before Phase 2a completion.
- **RISK-005**: CDK deployment failures across 9 stacks can leave the account in a partial state. Mitigation: deploy stacks individually in the order specified in TASK-030; run `cdk diff` before each deploy; maintain `cdk destroy` commands for rollback in `scripts/destroy_all_stacks.sh`.
- **RISK-006**: Strands SDK is an early-stage open-source library; breaking changes in minor versions could require rework. Mitigation: pin all dependencies in `requirements.lock`; track upstream changelog; assign 1 week buffer in Phase 2b schedule.
- **RISK-007**: Thesis committee rejects the "reframed Mục tiêu 2" (agentic system as the academic contribution instead of classical ML). This is the #1 project-level risk per v0.0.5 § 2. Mitigation: confirm reframing with Nhiên's advisor before Phase 2a begins; this implementation plan proceeds assuming confirmation.
- **RISK-008**: LLM (Claude Haiku) hallucination of cohort statistics or guideline citations. Mitigation: Bedrock Guardrails applied to all model invocations; manual audit of 30 random evaluation cases (TASK-045); citation panel links directly to source KB documents for clinician verification.
- **ASSUMPTION-001**: The thesis committee has confirmed the agentic reframing of Mục tiêu 2 (Option 1 per v0.0.5 § 2) before implementation begins.
- **ASSUMPTION-002**: De-identified ITP patient data (≥100 historical cases) is available and approved for use by BV Truyền máu Huyết học before Phase 1 starts.
- **ASSUMPTION-003**: The AWS account has a HIPAA BAA in place before any patient data (even de-identified) is ingested into AWS services.
- **ASSUMPTION-004**: Huy has access to an Apple Silicon Mac or ARM64 build environment for Docker image builds throughout Phase 2b.
- **ASSUMPTION-005**: The Strands Agents SDK `AgentCoreMemorySessionManager` API is stable and publicly available at the start of Phase 2b (Month 5).

---

## 8. Related Specifications / Further Reading

- [ITP Plan v0.0.6 — Full Architecture](../plans/itp_plan_v6.md)
- [AWS Reference: guidance-for-multi-agent-orchestration-using-bedrock-agentcore-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-multi-agent-orchestration-using-bedrock-agentcore-on-aws) — Pattern A reference implementation to fork at start of Phase 2b
- [AWS Reference: guidance-for-multi-agent-orchestration-on-aws](https://github.com/aws-solutions-library-samples/guidance-for-multi-agent-orchestration-on-aws) — Pattern B/C umbrella reference for Phase 2a
- [Strands Agents SDK — Agents as Tools pattern](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/index.md)
- [Amazon Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-agentcore.html)
- [aws-samples/bedrock-multi-agents-collaboration-workshop](https://github.com/aws-samples/bedrock-multi-agents-collaboration-workshop) — Phase 2a hands-on learning
- [awslabs/amazon-bedrock-agentcore-samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples) — AgentCore Code Interpreter samples for Risk-Reasoner agent
