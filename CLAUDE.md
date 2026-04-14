# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Hybrid ML + Agentic AI** proof-of-concept for ITP (Primary Immune Thrombocytopenia) bleeding risk prediction, built on AWS. The system combines classical ML models (Random Forest, XGBoost, LightGBM, Logistic Regression) with an Agentic AI layer using Amazon Bedrock for Vietnamese-language clinical decision support.

**Context**: Supporting a master's thesis by Trần Xuân Nhiên (2025–2027) at BV Truyền máu Huyết học. The ML core satisfies academic requirements; the agentic layer provides novel contribution.

The detailed architecture is in `ITP_Bleeding_Prediction_Research_Plan.md`.

## Architecture

Four-layer AWS architecture:

```
Layer 4: API Gateway + Cognito → React Web App (Vietnamese) → Bedrock Guardrails
Layer 3: Bedrock Agent "IDA" (supervisor) → Data Processing Agent (Lambda) + Prediction Agent (Lambda→SageMaker) + Explanation Agent (RAG+Bedrock)
Layer 2: SageMaker Studio (training) → SageMaker Endpoint (serving) → SageMaker Clarify (SHAP)
Layer 1: S3 (data lake) → Glue (ETL) → DynamoDB (feature store) → OpenSearch Serverless (RAG vector store)
```

**Key design decisions:**
- Foundation model: Claude 3 Haiku via Bedrock (multilingual Vietnamese support, cost-effective)
- RAG source: ASH 2019 / ISTH guidelines + Vietnamese clinical protocols, stored in OpenSearch Serverless
- Prediction input: 10 clinical features (see Section 6 of the plan)
- Output: bleeding risk probability (0–1) + SHAP attribution + Vietnamese explanation

## Implementation Phases

- **Phase 1** (Months 1–2): Data pipeline + ML training on SageMaker
- **Phase 2** (Months 3–4): Bedrock Agents orchestration + RAG pipeline
- **Phase 3** (Months 5–6): React frontend + API Gateway + Cognito + UAT

## Tech Stack

- **Python 3.11+** — all Lambda functions, SageMaker jobs, data processing
- **React.js** — frontend with Vietnamese i18n
- **AWS services**: S3, Glue, DynamoDB, OpenSearch Serverless, SageMaker, Bedrock, Lambda, API Gateway, Cognito, Amplify, CloudFront, CloudWatch
- **ML libraries**: Scikit-learn, XGBoost, LightGBM (SageMaker built-in or custom containers)

## Expected Directory Structure (not yet created)

```
infrastructure/     # Terraform or CDK for AWS resources
src/
  lambda/           # Data processing, prediction, and explanation agent handlers
  ml/               # SageMaker training scripts (train.py per algorithm)
  frontend/         # React app (Vietnamese UI)
  agents/           # Bedrock agent definitions and prompt templates
data/
  raw/              # Local copies of anonymised sample data (never real PHI)
  processed/        # Feature-engineered outputs
docs/               # Architecture diagrams, API specs
```

## Compliance Constraints

- All patient data must be de-identified before entering the system
- HIPAA BAA with AWS required before using HIPAA-eligible services
- Bedrock Guardrails must filter PHI and restrict LLM scope to ITP/hematology
- Lambda functions must not log patient data
- IAM: least-privilege roles per layer (data role, ML role, app role)
