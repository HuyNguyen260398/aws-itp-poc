# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Pure Multi-Agent AI** proof-of-concept for ITP (Primary Immune Thrombocytopenia) bleeding risk prediction, built on AWS. The system uses an agentic AI layer (Amazon Bedrock + AgentCore + Strands SDK) for Vietnamese-language clinical decision support, replacing the earlier hybrid ML approach.

**Context**: Supporting a master's thesis by Trần Xuân Nhiên (2025–2027) at BV Truyền máu Huyết học. The agentic layer provides the novel academic contribution; literature-anchored risk reasoning replaces classical ML model training.

The detailed architecture is in `plans/itp_plan_v6.md` (current). Legacy plan files are in `plans/` for reference.

## Architecture

Two deployment patterns — Pattern B is the prototype path, Pattern A is the production target:

### Pattern A — Production target (AgentCore + Strands SDK)

```
User access:     CloudFront + S3 + Cognito + WAF → React App (Vietnamese)
Edge:            AgentCore Runtime endpoint (JWT validation, SSE streaming)
Orchestration:   Strands Supervisor-Agent on AgentCore Runtime
Specialists:     Intake Agent | Risk-Reasoner Agent | Guidelines Agent | Cohort-Lookup Agent
                 (each on its own AgentCore Runtime, invoked via Agents-as-Tools pattern)
Tools layer:     AgentCore Gateway → MCP endpoints → Lambda functions (8 endpoints)
Memory:          AgentCore Memory (short-term chat + long-term clinician preferences)
Knowledge:       Bedrock Knowledge Bases over OpenSearch Serverless (ASH/ISTH/BV TMHH guidelines)
Identity:        AgentCore Identity + Cognito (JWT propagated end-to-end)
Observability:   AgentCore Observability + CloudWatch + OpenTelemetry
```

### Pattern B — Prototype path (Bedrock Multi-Agent Collaboration)

```
User access:     CloudFront + S3 + Cognito + WAF → React App (Vietnamese)
Orchestration:   Bedrock Multi-Agent Collaboration (Supervisor + 4 sub-agents, fully managed)
Knowledge:       Bedrock Knowledge Bases over Aurora Serverless v2 (pgvector)
Tools:           Lambda action groups (DynamoDB, Comprehend Medical)
Guardrails:      Bedrock Guardrails (PHI filtering, ITP/hematology scope)
```

**Key design decisions (v0.0.6):**
- Foundation model: Claude Sonnet 4.5 (supervisor) + Claude Haiku 4.5 (sub-agents) via Bedrock
- Agents-as-Tools pattern via Strands SDK (Pattern A) — supervisor calls sub-agents as typed Python functions
- Vector store: OpenSearch Serverless (Pattern A) or Aurora Serverless v2 pgvector (Pattern B)
- Risk reasoning: AgentCore Code Interpreter + literature-priors knowledge base (no SageMaker/SHAP)
- Staged migration: build on Pattern B first (Months 3–4), migrate to Pattern A (Months 5–6)
- AgentCore regions: `us-east-1` and `us-west-2` only (monitor for `ap-southeast-1` GA)
- Infrastructure as code: AWS CDK v2.220+ with one CDK stack per AgentCore Runtime

## Implementation Phases (9-Month Plan)

- **Phase 1** (Months 1–2): AWS setup + data engineering + cohort index in DynamoDB + guideline embeddings
- **Phase 2a** (Months 3–4): Pattern B prototype — Bedrock Multi-Agent Collaboration, prompt tuning, RAG pipeline
- **Phase 2b** (Months 5–6): Pattern A migration — Strands SDK, AgentCore Runtimes, CDK stacks, JWT + observability
- **Phase 3** (Month 7): React frontend (SSE streaming, Vietnamese UI, Cognito auth, audit log viewer)
- **Phase 4** (Months 7–8): Clinical evaluation — 50-case prospective study vs. 3 hematologists
- **Phase 5** (Month 9): Analysis and thesis writing

**Decision point**: End of Phase 2a — confirm Pattern A migration or stay on Pattern B for the remainder.

## Tech Stack

- **Python 3.11+** — Lambda functions, Strands agent code, data processing
- **Strands Agents SDK** — open-source, wraps AgentCore primitives, Agents-as-Tools pattern (Pattern A)
- **React.js** — frontend with Vietnamese i18n, hosted on S3 + CloudFront
- **AWS services (both patterns)**: S3, DynamoDB, Lambda, Cognito, CloudFront, CloudWatch, WAF, Bedrock Knowledge Bases, Comprehend Medical
- **AWS services (Pattern A only)**: AgentCore Runtime, AgentCore Memory, AgentCore Gateway, AgentCore Identity, AgentCore Observability, OpenSearch Serverless, ECR, KMS, CDK
- **AWS services (Pattern B only)**: Bedrock Agents (multi-agent collaboration), Bedrock Guardrails, Aurora Serverless v2 (pgvector)
- **Cost profile**: Option B ~$173–318/month; Option A ~$540–745/month; staged B→A migration ~$2,800–4,500 over 9 months

## Expected Directory Structure (not yet created)

```
infrastructure/     # CDK stacks (one per AgentCore Runtime + shared infra)
src/
  agents/           # Strands agent definitions and system prompts (supervisor_vi.txt, etc.)
  lambda/           # MCP tool implementations (DynamoDB queries, Comprehend Medical wrappers)
  frontend/         # React app (Vietnamese UI, SSE streaming, audit log viewer)
data/
  raw/              # Local copies of anonymised sample data (never real PHI)
  processed/        # Feature-engineered outputs
  guidelines/       # ASH/ISTH/BV TMHH guideline documents for Knowledge Base ingestion
docs/               # Architecture diagrams, API specs
```

## Reference Implementations

- `aws-solutions-library-samples/guidance-for-multi-agent-orchestration-using-bedrock-agentcore-on-aws` — Pattern A reference (fork at start of Phase 2b)
- `aws-solutions-library-samples/guidance-for-multi-agent-orchestration-on-aws` — Pattern B/C umbrella reference
- `aws-samples/bedrock-multi-agents-collaboration-workshop` — Pattern B hands-on workshop (Phase 2a learning)
- `awslabs/amazon-bedrock-agentcore-samples` — AgentCore Code Interpreter samples (Risk-Reasoner)

## Coding Guidelines

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Compliance Constraints

- All patient data must be de-identified before entering the system
- HIPAA BAA with AWS required before using HIPAA-eligible services
- Bedrock Guardrails must filter PHI and restrict LLM scope to ITP/hematology
- Lambda functions must not log patient data
- IAM: least-privilege roles per layer (data role, agent role, app role)
- AgentCore Identity propagates JWT end-to-end; no manual Cognito authorizer wiring needed (Pattern A)
