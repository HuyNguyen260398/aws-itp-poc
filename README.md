<div align="center">

# AWS ITP Bleeding Prediction POC

### Multi-Agent AI for Clinical Decision Support

A proof-of-concept system on AWS for assessing bleeding risk in adult patients with **Primary Immune Thrombocytopenia (ITP)**, using a multi-agent AI architecture with Vietnamese-language clinical decision support.

---

![Status](https://img.shields.io/badge/status-planning-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
![Plan](https://img.shields.io/badge/plan-v0.0.6-blue)

![AWS CDK](https://img.shields.io/badge/AWS%20CDK-232F3E?logo=amazonaws&logoColor=white)
![Amazon Bedrock](https://img.shields.io/badge/Bedrock-222222?logo=amazon&logoColor=white)
![Claude](https://img.shields.io/badge/Claude%20Sonnet%2FHaiku-D97757?logo=anthropic&logoColor=white)
![Strands SDK](https://img.shields.io/badge/Strands%20SDK-7B2FBE)

</div>

---

## Overview

Primary ITP is an autoimmune disorder where bleeding risk becomes difficult to predict once platelet counts exceed 10 x 10^9/L. This project builds a clinical decision-support tool using a pure multi-agent AI architecture:

- **Supervisor agent** — Claude Sonnet 4.5 on AgentCore Runtime, orchestrating four specialist sub-agents via the Strands Agents-as-Tools pattern, producing Vietnamese-language guideline-backed explanations.
- **Specialist sub-agents** — Intake (clinical NER), Risk-Reasoner (literature-prior scoring with Code Interpreter), Guidelines (RAG over ASH/ISTH/BV TMHH protocols), and Cohort-Lookup (similar past patients from DynamoDB).

The system is built against the official AWS Solutions Library multi-agent reference architecture (AgentCore + Strands).

## Project Context

**Research Objectives**

1. Describe clinical characteristics, laboratory findings, and bleeding status of adult ITP patients at BV TMHH (2022-2026)
2. Build a multi-agent AI system that assesses bleeding risk and generates guideline-backed explanations in Vietnamese
3. Deliver an online application enabling clinicians to rapidly assess bleeding risk and review reasoning

## Architecture

The production target (Pattern A) follows the AWS AgentCore + Strands reference design:

| Layer | Components |
|-------|-----------|
| **User access** | CloudFront + S3, Cognito (JWT), WAF |
| **Edge** | AgentCore Runtime endpoint — validates JWT, routes to supervisor, streams SSE |
| **Orchestration** | Strands Supervisor-Agent on AgentCore Runtime — delegates to sub-agents via Agents-as-Tools |
| **Specialists (x4)** | Intake, Risk-Reasoner, Guidelines, Cohort-Lookup — each on its own AgentCore Runtime |
| **Tools** | AgentCore Gateway exposing 8 Lambda functions as MCP endpoints; Comprehend Medical for NER |
| **Memory** | AgentCore Memory (short-term session + long-term clinician preferences) |
| **Knowledge** | Bedrock Knowledge Bases over OpenSearch Serverless (ASH/ISTH/BV TMHH guidelines) |
| **Identity** | AgentCore Identity — JWT propagated end-to-end across all runtimes |
| **Observability** | AgentCore Observability + CloudWatch + OpenTelemetry |
| **Data** | S3 (data lake), DynamoDB (cohort index + sessions), Aurora Serverless v2 pgvector (prototype RAG) |

Full details — including agent prompts, cost estimates, and risk register — are in [`plans/itp_plan_v6.md`](./plans/itp_plan_v6.md).

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **Languages** | Python 3.11+, TypeScript |
| **Agent framework** | Strands Agents SDK, Amazon Bedrock AgentCore (Runtime, Memory, Gateway, Identity, Observability) |
| **LLM** | Claude Sonnet 4.5 (supervisor), Claude Haiku 4.5 (sub-agents) |
| **RAG / Knowledge** | Amazon Bedrock Knowledge Bases, OpenSearch Serverless (Pattern A), Aurora Serverless v2 pgvector (Pattern B) |
| **Data** | Amazon S3, Amazon DynamoDB, AWS Glue |
| **Compute** | AWS Lambda (8 action-group functions), Amazon ECR (ARM64 containers) |
| **NLP** | Amazon Comprehend Medical (clinical NER) |
| **Application** | React.js, Amazon CloudFront, Amazon Cognito, AWS Amplify, AWS WAF |
| **IaC** | AWS CDK v2 |
| **Observability** | Amazon CloudWatch, OpenTelemetry |
| **Security** | AWS KMS, AgentCore Identity (JWT), Bedrock Guardrails |

## Clinical Inputs (11 Features)

Infection · uncontrolled diabetes · age · ITP type · cardiovascular disease · low lymphocyte count · skin/mucosa bleeding · initial platelet count · current platelet count <20 x 10^9/L · disease duration · active treatment.

**Outcome**: Hemorrhage >= Grade 2 (WHO scale), binary risk assessment.

## Implementation Phases

The plan uses a staged Pattern B (prototype) to Pattern A (production) migration:

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **1. Foundation** | Months 1-2 | AWS setup, IAM, S3, Glue ETL, DynamoDB cohort index, Aurora pgvector for guidelines |
| **2a. Pattern B Prototype** | Months 3-4 | Bedrock multi-agent collaboration, RAG pipeline, Vietnamese prompt tuning |
| **2b. Pattern A Migration** | Months 5-6 | Strands SDK rewrite, CDK stacks, AgentCore deployment, OpenSearch migration |
| **3. Application** | Month 7 | React frontend, Cognito auth, SSE streaming, clinical UX components |
| **4. Clinical Evaluation** | Months 7-8 | 50-case prospective study vs. 3 hematologists; Kappa agreement, Likert satisfaction |
| **5. Analysis & Writing** | Month 9 | Thesis analysis, audit of explanations, final report |

Decision point at end of Phase 2a: confirm Pattern A migration or remain on Pattern B.

## Status

**Planning** — v0.0.6 architecture is finalised; implementation begins in Phase 1.

## Security & Compliance

- All AWS services selected are HIPAA-eligible (BAA required)
- Patient data is de-identified before entering the system
- SSE-S3 at rest, TLS 1.2+ in transit
- Cognito MFA for clinician authentication; JWT propagated end-to-end via AgentCore Identity
- Bedrock Guardrails enforce PHI filtering and restrict scope to ITP risk assessment (not treatment prescription)
- OpenTelemetry audit trail across all agent runtimes

## References

- **An et al. (2023)** — *Life-threatening bleeding prediction model for ITP based on personalized ML*, Science Bulletin 68:2106-2114
- **Dhiman et al. (2026)** — *An Agentic AI system for disease diagnosis with explanations*, Informatics and Health 3:32-40
- **Shen et al. (2025)** — *Prediction of moderate-to-severe bleeding risk in pediatric ITP using ML*, Eur J Pediatr 184:283

Full reference list in the research plan.

## License

Released under the [MIT License](./LICENSE).
