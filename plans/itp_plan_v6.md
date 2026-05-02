# ITP Bleeding Prediction Research Plan — v0.0.6

## Multi-Agent Architecture aligned with AWS Reference Guidance

**Project**: Bước đầu đánh giá hiệu quả dự đoán chảy máu của các mô hình học máy ở bệnh nhân người lớn giảm tiểu cầu miễn dịch tại Bệnh viện Truyền máu Huyết học giai đoạn 2022–2026

**Researcher**: Trần Xuân Nhiên (Master's Thesis, 2025–2027)

**Technical Support**: Huy (Software Engineer, AWS DevOps focus)

**Version**: 0.0.6

**Status**: Refinement of v0.0.5 — same architectural intent (pure multi-agent), but reworked to align with the official AWS Solutions Library reference architectures.

**Changelog**:
- v0.0.1–0.0.4: Hybrid ML + Agentic AI
- v0.0.5: Pivot to pure multi-agent
- **v0.0.6**: Re-architected against AWS official "Multi-Agent Orchestration on AWS" guidance (AgentCore + Strands variant). Adds Strands SDK, AgentCore Runtime/Memory/Gateway/Identity/Observability, and a pragmatic three-deployment-pattern decision framework. Cost model rebuilt from AWS reference (~$1,456/month baseline).

---

## 1. What changed since v0.0.5

v0.0.5 made the right architectural call (pure multi-agent), but built the design from first principles. The two AWS reference architectures Huy supplied are official solutions library guidance and they change the implementation in three important ways:

1. **AgentCore is now the recommended runtime, not Bedrock Agents directly.** AgentCore is a serverless container runtime purpose-built for agents, with built-in identity (JWT), memory, gateway (MCP), and observability. v0.0.5 wired all of these manually with Lambda + API Gateway + DynamoDB; v0.0.6 uses AgentCore.
2. **Strands Agents SDK is the recommended framework for agent code.** Strands is an open-source Python SDK that wraps the AgentCore primitives, enables the "Agents as Tools" pattern (where one agent calls another as a function), and supports A2A (Agent-to-Agent) protocol. v0.0.5 wrote its own orchestration in supervisor prompts; v0.0.6 uses Strands.
3. **AWS publishes three valid deployment patterns**, not one. We need to pick which fits Nhiên's thesis best.

The medical/clinical caveat from v0.0.5 § 2 (LLM agents underperform XGBoost on tabular prediction) **is unchanged and remains the most important issue**. v0.0.6 doesn't relitigate it. Read v0.0.5 § 2 first; everything below assumes Option 1 (reframe Mục tiêu 2) is the chosen path.

---

## 2. The three AWS deployment patterns

AWS publishes three reference patterns for multi-agent orchestration:

| Pattern | Runtime | Best for | Complexity | Baseline cost |
|---------|---------|----------|------------|---------------|
| **A. AgentCore + Strands SDK** | AgentCore Runtime (serverless ARM64 microVMs) | Production-grade systems, JWT-secured agents, OpenTelemetry tracing | High (Docker, CDK, multiple stacks) | ~$1,456/mo |
| **B. Bedrock Multi-Agent Collaboration** | Bedrock-managed (no container) | Fastest path from idea to demo, all-AWS-managed | Low (CDK or console) | ~$300–500/mo |
| **C. LangGraph on ECS** | Amazon ECS containers | Teams with existing LangGraph code, full control | High (ECS, LangGraph, ALB, checkpointer) | ~$600–900/mo |

### What we used in v0.0.5

v0.0.5 implicitly assumed Pattern B (Bedrock Multi-Agent Collaboration) because that was the only mature option when the v0.0.5 plan was drafted. The April 2025 release of AgentCore (Pattern A) and the maturation of Strands SDK changes this.

### Recommendation for v0.0.6

**Pattern A (AgentCore + Strands)** for the production deliverable; **Pattern B as the development/prototype path**. Concretely:

- **Phase 2a (Months 3–4)** — Prototype on Pattern B for fast iteration; use Bedrock Multi-Agent Collaboration directly via console/SDK. Get the agent prompts working, tune the RAG pipeline.
- **Phase 2b (Months 5–6)** — Migrate the working prototype to Pattern A (AgentCore + Strands). Get JWT-secured runtime, AgentCore Memory, OpenTelemetry tracing, full CDK deployment.

This staged approach front-loads agent prompt engineering (where most risk lies) before committing to AgentCore's heavier infrastructure. Once prompts are stable, Pattern A migration is mostly mechanical.

Pattern C (LangGraph on ECS) is rejected for this project because Huy doesn't have existing LangGraph code to bring forward, and the ECS overhead doesn't buy us anything for ~10K queries/month.

---

## 3. Architecture (Pattern A — production target)

### 3.1 Component map

The architecture mirrors the AWS reference design in `aws-solutions-library-samples/guidance-for-multi-agent-orchestration-using-bedrock-agentcore-on-aws`. Five agent runtimes (one supervisor + four specialists), all on AgentCore.

| Layer | Service | Role for ITP system |
|-------|---------|---------------------|
| **User access** | CloudFront + S3 + Cognito + WAF | React app delivery; clinician auth via JWT |
| **Edge** | AgentCore Runtime endpoint | Validates JWT, routes to supervisor, streams SSE |
| **Orchestration** | Strands `Supervisor-Agent` on AgentCore Runtime | Analyzes Vietnamese clinical query, delegates via Agents-as-Tools pattern |
| **Specialists (× 4)** | Each on its own AgentCore Runtime | Intake, Risk-Reasoner, Guidelines, Cohort-Lookup |
| **Tools layer** | AgentCore Gateway → MCP endpoints | All external tool calls go through Gateway as MCP servers |
| **Memory** | AgentCore Memory | Short-term (current chat) + long-term (clinician preferences, common patient patterns) |
| **Knowledge** | Bedrock Knowledge Bases over OpenSearch Serverless | ASH/ISTH/BV TMHH guideline embeddings |
| **Identity** | AgentCore Identity + Cognito | JWT propagated end-to-end, validated at each runtime + gateway |
| **Observability** | AgentCore Observability + CloudWatch + OpenTelemetry | Distributed tracing across all 5 runtimes |
| **Compute (tools)** | AWS Lambda functions (8 endpoints, exposed as MCP via Gateway) | DynamoDB queries, Comprehend Medical wrappers, code execution |

### 3.2 Why AgentCore over plain Bedrock Agents

The AWS reference cost table prices AgentCore at $400/mo for 5 runtimes (~150 hours/month) — meaningfully higher than Bedrock-managed agents. The reasons to pay it:

- **Session isolation per user** via dedicated microVMs. For clinical data this matters: one clinician's session can't leak into another's even if an agent prompt is compromised.
- **JWT validation at every service boundary** (Runtime, Gateway). v0.0.5 had to wire this manually with API Gateway authorizers; AgentCore does it natively.
- **AgentCore Memory** with semantic + summary + user-preference strategies. The supervisor agent automatically learns each clinician's style preferences (e.g. "Bs. An prefers concise replies with citations only at the end").
- **OpenTelemetry tracing out of the box** through AgentCore Observability. Critical for clinical audit (who saw what, what reasoning was used).
- **A2A protocol support** (announced after v0.0.5) — agents can call agents directly, enabling Strands' Graph/Swarm/Workflow patterns we may want later.

### 3.3 Strands "Agents as Tools" pattern

v0.0.5's supervisor used Bedrock collaborator-agent associations (`AssociateAgentCollaborator` API). v0.0.6 replaces this with Strands' Agents-as-Tools pattern:

```python
# Pseudocode for the Supervisor agent (Strands)
from strands import Agent, tool

@tool
def intake_agent_tool(clinical_note: str) -> dict:
    """Extract 11 ITP variables from unstructured Vietnamese clinical note."""
    return invoke_runtime("intake-agent-arn", payload={"note": clinical_note})

@tool
def risk_reasoner_tool(features: dict) -> dict:
    """Compute literature-anchored bleeding risk score."""
    return invoke_runtime("risk-reasoner-arn", payload={"features": features})

@tool
def guidelines_tool(query: str) -> dict:
    """Retrieve ASH/ISTH/BV TMHH guidelines for a clinical question."""
    return invoke_runtime("guidelines-agent-arn", payload={"query": query})

@tool
def cohort_lookup_tool(features: dict) -> dict:
    """Find 5 most similar past patients in BV TMHH cohort."""
    return invoke_runtime("cohort-agent-arn", payload={"features": features})

supervisor = Agent(
    model="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    tools=[intake_agent_tool, risk_reasoner_tool, guidelines_tool, cohort_lookup_tool],
    system_prompt=load_prompt("supervisor_vi.txt"),
    session_manager=AgentCoreMemorySessionManager(memory_id=ITP_MEMORY_ID),
)
```

The five agent processes from v0.0.5 collapse into **four sub-agents + a supervisor** (the Explanation agent's role moves into the supervisor's response synthesis, which is the canonical Strands pattern). Each tool call is a separate JWT-validated runtime invocation.

### 3.4 What replaces SageMaker — refined

v0.0.5 had the Risk-Reasoner use AgentCore Code Interpreter to compute literature priors. v0.0.6 keeps this but adds two refinements from the reference architecture:

1. **Risk-Reasoner is its own AgentCore Runtime** with the Code Interpreter as a Strands tool. This isolates the code execution from supervisor reasoning — important for audit (we can replay exactly what code was run, with what inputs, when).
2. **The literature-priors module is loaded as a knowledge-base document**, not hardcoded. This way Nhiên (a hematologist, not a coder) can update the priors when new ITP literature appears, without redeploying.

```python
# Pseudocode for Risk-Reasoner agent
from strands import Agent, tool
from strands.tools import code_interpreter, knowledge_base

risk_reasoner = Agent(
    model="global.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[
        code_interpreter,                    # AgentCore Code Interpreter
        knowledge_base("itp-priors-kb"),     # Literature priors as KB docs
    ],
    system_prompt=load_prompt("risk_reasoner_vi.txt"),
)
```

---

## 4. Revised cost analysis

The AWS reference cost ($1,456/mo) is for 100,000 conversations/month at 1,000 input + 500 output tokens. Nhiên's clinical evaluation phase will run ~50–200 conversations/month — about 0.1% of the reference workload. We rescale accordingly:

### Option A (Pattern A, full AgentCore stack — production target)

| Service | Reference cost | ITP project cost | Notes |
|---------|----------------|------------------|-------|
| AgentCore Runtime (5 agents) | $400 | $80–150 | ~30 hrs/mo active during evaluation, ARM64 |
| Bedrock Sonnet 4.5 (supervisor) | $195 | $20–40 | ~2,000 invocations/mo |
| Bedrock Haiku 4.5 (4 sub-agents) | $168 | $15–30 | ~6,000 invocations/mo total |
| Bedrock Knowledge Bases | $85 | $20–30 | Smaller corpus (~500MB guidelines) |
| AgentCore Memory | $50 | $15–25 | Lower volume, 60-day retention |
| AgentCore Gateway (8 MCP endpoints) | $25 | $10–15 | Lower invocation count |
| OpenSearch Serverless (2 collections) | $438 | $350–400 | **Floor cost — same as reference** |
| Cognito (50 MAU) | $25 | $0–5 | Free tier covers research scale |
| Lambda (9 functions) | $8.50 | $2–5 | Mostly free tier |
| ECR (5 repos × 2 GB) | $5 | $5 | Same |
| S3 + CloudFront + WAF | $11.35 | $5–10 | Lower traffic |
| CloudWatch Logs | $45 | $15–25 | 7-day retention, smaller volume |
| KMS | $1.50 | $1.50 | Same |
| **Monthly total** | **$1,456** | **$540–745** | |
| **9-month total** | — | **$4,860–6,705** | ≈ 124–171 triệu VNĐ |

### Option B (Pattern B, Bedrock Multi-Agent — cost-optimized prototype)

| Service | Cost/mo | Notes |
|---------|---------|-------|
| Bedrock Multi-Agent Collaboration (Sonnet supervisor + Haiku sub-agents) | $80–140 | Same model split; no AgentCore Runtime fee |
| Bedrock Knowledge Base | $20–30 | |
| Aurora Serverless v2 with pgvector (replaces OpenSearch) | $15–30 | **Saves ~$370/mo vs Option A** |
| Bedrock Guardrails | $20–35 | |
| AgentCore Code Interpreter (only) | $20–40 | Used as a tool, not a runtime host |
| Lambda + API Gateway + Cognito + DynamoDB | $5–15 | Free tier covers most |
| S3 + CloudFront | $3–8 | |
| CloudWatch (basic) | $10–20 | |
| **Monthly total** | **$173–318** | |
| **9-month total** | **$1,560–2,860** | ≈ 40–73 triệu VNĐ |

### Comparison vs v0.0.5

v0.0.5 Option B cost was $178–353/mo. v0.0.6 Option B is essentially unchanged ($173–318) — we kept the same Bedrock-managed pattern but cleaned up the architecture description. v0.0.6 Option A ($540–745) is **lower than v0.0.5 Option A** ($805–1,195) because the AWS reference cost model is more precise than my v0.0.5 estimates.

### Decision matrix

| You want… | Pick |
|-----------|------|
| Lowest cost, fastest prototype, thesis demo | **Option B** |
| Production-grade, JWT-secured, OpenTelemetry-traced, deployable to a real hospital | **Option A** |
| Both? Build B first, migrate to A in Phase 2b | **Staged approach** |

The staged approach (B → A migration) costs roughly **$2,800–4,500 over 9 months** (Option B for months 1–4, Option A for months 5–9). This is what I recommend.

---

## 5. Revised 9-month timeline (with B→A migration)

### Phase 1: Foundation and data engineering (Months 1–2) — unchanged

Same as v0.0.5: AWS account, IAM, S3 buckets, Glue ETL, cohort similarity index in DynamoDB, guideline embeddings in Aurora pgvector (which we'll migrate to OpenSearch in Phase 2b only if Option A is chosen).

### Phase 2a: Pattern B prototype (Months 3–4) — fast iteration

| Week | Task | Deliverable |
|------|------|-------------|
| 9–10 | Set up Bedrock multi-agent collaboration in console; build supervisor + 4 sub-agents | Working agent system |
| 11–12 | Wire up Knowledge Base RAG, Lambda action groups for cohort lookup, Comprehend Medical for intake | Full pipeline working |
| 13–14 | Vietnamese prompt tuning, few-shot example curation (~20 medical Q&A pairs), Guardrails | Production-quality prompts |
| 15–16 | Internal testing, edge case handling, latency profiling | Prompt-stable prototype |

**Decision point at end of Phase 2a**: based on prototype performance, decide whether to migrate to Pattern A or stay on Pattern B for the rest of the project.

### Phase 2b: Pattern A migration (Months 5–6) — only if Pattern A is chosen

| Week | Task | Deliverable |
|------|------|-------------|
| 17–18 | Install Strands SDK; rewrite supervisor prompts as Strands `Agent` definitions | 5 Strands agents (local) |
| 19–20 | Build CDK stacks (one per agent runtime + shared infra); Dockerize for ARM64 | Deployable IaC |
| 21–22 | Migrate Knowledge Base from Aurora pgvector → OpenSearch Serverless; wire AgentCore Memory | Migrated knowledge layer |
| 23–24 | Deploy to AgentCore Runtimes; configure JWT propagation; turn on Observability | Production system online |

If Pattern B is kept, Months 5–6 instead extend Phase 2a with: clinician-feedback loop in DynamoDB, A/B tests of supervisor prompts, hardening.

### Phase 3: Application development (Month 7) — adjusted

| Week | Task | Deliverable |
|------|------|-------------|
| 25–26 | React app: AWS Amplify auth (Cognito), SSE streaming from agent endpoint, Vietnamese UI | Frontend |
| 27–28 | Clinical UX components: risk panel, citation panel, audit log viewer | Complete clinical UI |

### Phase 4: Clinical evaluation (Months 7–8) — same as v0.0.5

50-case prospective study comparing system recommendations vs. 3 hematologists' judgments. Kappa agreement, Likert satisfaction, manual audit of 30 random explanations.

### Phase 5: Analysis and writing (Month 9) — same as v0.0.5

---

## 6. Updated technical stack

### Always present (in both Patterns A and B)
- Amazon Bedrock Knowledge Bases (RAG)
- Amazon S3 (data lake)
- Amazon DynamoDB (cohort + sessions)
- AWS Lambda (action groups / MCP tool implementations)
- Amazon Cognito (clinician auth)
- Amazon CloudFront + S3 (frontend)
- Amazon CloudWatch (logs + metrics)
- AWS WAF (CloudFront protection)
- AWS Comprehend Medical (clinical NER)

### Pattern A only
- **Amazon Bedrock AgentCore Runtime** (5 agent runtimes)
- **Amazon Bedrock AgentCore Memory** (STM + LTM)
- **Amazon Bedrock AgentCore Gateway** (MCP endpoints)
- **Amazon Bedrock AgentCore Identity** (JWT propagation)
- **Amazon Bedrock AgentCore Observability** (OpenTelemetry)
- **Strands Agents SDK** (open source, no AWS fee)
- Amazon OpenSearch Serverless (vector store)
- Amazon ECR (5 ARM64 container repos)
- AWS KMS (encryption keys)
- AWS CDK v2.220+ (infrastructure as code)
- AWS Amplify (frontend hosting + auth wiring)

### Pattern B only
- **Amazon Bedrock Agents** (multi-agent collaboration mode)
- **Amazon Bedrock Guardrails** (more directly accessible than via AgentCore)
- Aurora Serverless v2 with pgvector (vector store, replaces OpenSearch)

### Removed from v0.0.5
- The "Explanation Agent" as a separate agent — its role merges into the Supervisor's response synthesis (Strands canonical pattern).

---

## 7. Reference implementations

These are the resources we will fork or pattern-match against during build:

1. **`aws-solutions-library-samples/guidance-for-multi-agent-orchestration-using-bedrock-agentcore-on-aws`** — the Pattern A reference. Contains agents/, frontend/, infrastructure/ (CDK), lambda/. Forked at start of Phase 2b.
2. **`aws-solutions-library-samples/guidance-for-multi-agent-orchestration-on-aws`** — the umbrella repo with Pattern B and Pattern C variants too. Reference for Phase 2a.
3. **`aws-samples/bedrock-multi-agents-collaboration-workshop`** — hands-on workshop for Pattern B. Foundation for Phase 2a learning.
4. **`awslabs/amazon-bedrock-agentcore-samples`** — AgentCore SDK samples including Code Interpreter integrations. Reference for Risk-Reasoner agent.
5. **Strands documentation** — `strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/index.md`. Reference for the Agents-as-Tools pattern Phase 2b is built on.

---

## 8. Risk register (delta from v0.0.5)

Risks unchanged from v0.0.5:
- Thesis committee rejects Option 1 reframing (still the #1 risk)
- LLM accuracy on tabular prediction (still real, still requires honest framing)
- Vietnamese clinical terminology gaps
- Prompt injection attacks
- Hallucinated cohort statistics

New risks introduced by Pattern A:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Docker ARM64 build complexity (15–20 min builds on x86) | High | Low | Use ARM-native machine if possible (Apple Silicon, AWS Graviton); cache layers aggressively |
| AgentCore region availability (`us-east-1` and `us-west-2` only) | High | Medium | Accept higher latency from Vietnam (~250ms RTT to us-west-2); monitor for ap-southeast-1 GA |
| AgentCore service quotas (5 runtimes by default) | Low | Low | Request quota increase early in Phase 2b |
| OpenSearch Serverless cost floor ($350+/mo) | Certain | Medium | Already factored into Option A budget; alternative is to stay on Pattern B |
| CDK deployment failures cascading across 7 stacks | Medium | Low | Deploy stacks individually first, then run end-to-end script; use `cdk diff` before every push |

Risks removed by Pattern A:
- Manual JWT validation (Cognito authorizers on API Gateway) — handled natively by AgentCore Identity
- Agent-to-agent auth wiring — JWT propagated automatically through Strands invocations
- Manual OpenTelemetry instrumentation — AgentCore Observability emits traces automatically

---

## 9. What this v6 plan does NOT include

Same exclusions as v0.0.5 (no SageMaker training, no QuickSight, no SHAP) plus:

- **No LangGraph (Pattern C)** — rejected. Strands SDK gives us the same orchestration patterns with native AgentCore integration; LangGraph would require running ECS clusters with no benefit.
- **No A2A protocol usage in v6** — AgentCore A2A is GA but adds complexity; we'll stick with the simpler Agents-as-Tools pattern. A2A is a future-work item if the system needs Graph/Swarm patterns later.
- **No production deployment to BV TMHH** — the Phase 4 evaluation uses a staging environment with de-identified data. Production handover to the hospital is post-thesis work.

---

## 10. Decision summary for the next conversation

To move forward, three decisions are needed (in order):

1. **(Nhiên + advisor)** — Confirm thesis reframing per v0.0.5 § 2 (Option 1 vs Option 2 vs no change). Without this, no architecture matters.
2. **(Huy)** — Confirm staged Pattern B → Pattern A migration approach, or pick one pattern and stay on it. My recommendation: staged.
3. **(Huy + Nhiên)** — Confirm 9-month timeline still fits, or adjust phase durations. The staged approach makes Months 5–6 heavier than v0.0.5; if that's a problem, we drop the migration and stay on Pattern B.

Once these three are decided, the next deliverable is a **CDK skeleton repo** that mirrors the AWS reference structure but with our 5-agent topology and ITP domain prompts. ~1 week of work to get a deployable "hello world" supervisor + 1 specialist.

---

*v0.0.6 brings the v0.0.5 multi-agent design into alignment with AWS's official solutions library guidance. The architectural intent is unchanged; what changes is that we now use AWS-blessed patterns (AgentCore + Strands) rather than building from primitives, which reduces operational risk, brings JWT/observability/memory for free, and gives us a forkable reference codebase as the starting point. The clinical caveat from v0.0.5 § 2 is unchanged and remains the gating concern for the thesis.*
