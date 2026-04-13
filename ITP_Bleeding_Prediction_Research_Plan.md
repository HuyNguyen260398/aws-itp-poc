# ITP Bleeding Prediction Research Plan

## Hybrid ML + Agentic AI System on AWS

**Project**: Bước đầu đánh giá hiệu quả dự đoán chảy máu của các mô hình học máy ở bệnh nhân người lớn giảm tiểu cầu miễn dịch tại Bệnh viện Truyền máu Huyết học giai đoạn 2022–2026

**Researcher**: Trần Xuân Nhiên (Master's Thesis, 2025–2027)

**Technical Support**: Huy (Software Engineer)

**Date**: April 2026

---

## 1. Problem Statement

Primary immune thrombocytopenia (ITP) is an autoimmune disorder characterized by isolated thrombocytopenia (platelet count < 100 × 10⁹/L). The core clinical challenge is an increased bleeding risk that is difficult to predict — the relationship between platelet count and bleeding risk becomes non-linear and even loses correlation above 10 × 10⁹/L (Chen, 2021).

Current discharge and risk-assessment decisions rely primarily on clinical experience (Grade C evidence), leading to inconsistency across facilities and resource waste. In Vietnam, research has focused on treatment response rather than building data-driven discharge criteria.

Machine learning models (Random Forest, XGBoost, LightGBM) have demonstrated superior predictive performance internationally, achieving AUC values of 0.82–0.89 for hemorrhagic events. However, Vietnam has not yet systematically applied these technologies to ITP patient management.

---

## 2. Research Objectives

1. **Objective 1**: Describe clinical characteristics, laboratory findings, and bleeding status of adult ITP patients at BV Truyền máu Huyết học (2022–2026)
2. **Objective 2**: Identify and compare predictive performance (AUC, sensitivity, specificity) of ML models: Random Forest, XGBoost, LightGBM, and Logistic Regression; determine feature importance
3. **Objective 3**: Build an online application to help clinicians rapidly identify bleeding risk

---

## 3. Approach Comparison: Classical ML vs. Agentic AI

### Approach 1: Classical ML (Similar to An et al., 2023)

**Pros:**
- Directly replicable — An et al. provides a clear blueprint with the same ML algorithms
- Strong precedent: RF achieved AUC of 0.89 in retrospective cohort; Shen et al. (2025) achieved AUC of 0.886 with XGBoost for pediatric ITP
- Works well with small datasets (n ≥ 150) — ensemble methods handle this scale
- Thesis committees in medical schools understand and accept this methodology
- SHAP explainability is well-established and clinically trusted
- Faster to implement with Python/Scikit-learn

**Cons:**
- Limited novelty — essentially replicating existing work on a Vietnamese cohort
- No natural language interaction for clinicians
- Static predictions with no reasoning or guideline-backed explanations
- Cannot process unstructured clinical notes

### Approach 2: Agentic AI (Similar to Dhiman et al., 2026)

**Pros:**
- High novelty — agentic AI in healthcare is an exploding research area (2025+)
- Can generate natural language explanations backed by clinical guidelines via RAG
- Processes multimodal data (structured labs + clinical notes)
- AWS provides production-ready infrastructure (Bedrock, SageMaker)
- Scalable and extensible to other hematologic conditions
- Software engineering background is a perfect fit

**Cons:**
- Very few published examples in hematology specifically
- LLM fine-tuning for disease prediction requires much larger datasets than n=150
- Risk of hallucination in clinical settings
- More complex for a medical thesis committee unfamiliar with agentic AI
- Higher infrastructure cost
- Harder to validate clinically in a master's thesis timeframe

### Recommended: Hybrid Approach

The hybrid strategy uses **classical ML as the prediction core** (satisfying the medical thesis requirements) wrapped with an **Agentic AI layer** for explainability, natural language interaction, and guideline-backed reasoning.

- **Phase 1 (ML Core)**: Train RF, XGBoost, LightGBM, LR on hospital ITP data → produces AUC comparisons, SHAP analysis, clinical validation
- **Phase 2 (Agentic AI Wrapper)**: Deploy best ML model on AWS, wrap with LLM agents for explanation generation and Vietnamese-language clinical interface

---

## 4. Key Reference Articles

### Primary Reference (Original Inspiration)
- **An et al. (2023)** — "A life-threatening bleeding prediction model for immune thrombocytopenia based on personalized machine learning: a nationwide prospective cohort study." *Science Bulletin*, 68, 2106–2114. DOI: 10.1016/j.scib.2023.08.001
  - Retrospective cohort: 2,094 patients from 8 centers; Prospective: 1,097 patients from 39 centers
  - RF achieved best AUC: 0.89 (retrospective), 0.82 (prospective inpatient), 0.74 (outpatient)
  - Top 10 features: infection, uncontrolled diabetes, age, ITP type, CVD, low lymphocyte count, skin/mucosa bleeding, initial PLT, low PLT (<20×10⁹/L), disease duration
  - Built a web-based prediction tool

### Agentic AI Reference
- **Dhiman et al. (2026)** — "An Agentic AI system for disease diagnosis with explanations." *Informatics and Health*, 3, 32–40. DOI: 10.1016/j.infoh.2026.01.001
  - Framework: 4 agents (IDA, SPA, DA, EA) with LLM backbone
  - LLaMA-3 best performance: 0.88 AUROC (CHF), 0.90 AUPRC (UTI)
  - Uses Knowledge Graph, QLoRA fine-tuning, RAG for explanations
  - Tested on MIMIC-Eye multimodal dataset

### Additional ML in ITP Literature
- **Shen et al. (2025)** — "Prediction of moderate to severe bleeding risk in pediatric ITP using machine learning." *Eur J Pediatr*, 184, 283. DOI: 10.1007/s00431-025-06123-7
  - XGBoost model, AUC = 0.886; Key predictors: child age, age at diagnosis, initial PLT count

- **Kasser et al. (2026)** — "Predicting Chronicity in Children and Adolescents With Newly Diagnosed ITP at the Timepoint of Diagnosis Using ML." *Pediatric Blood & Cancer*. DOI: 10.1002/1545-5017.70103
  - ML on PARC-ITP Registry; Key predictors: age, sex, platelet count, leukocyte count, hepatitis C, cutaneous bleeding

- **Ma et al. (2025)** — "Machine learning to forecast rituximab responses for paediatric ITP." *Br J Haematol*, 207(2), 463–474. DOI: 10.1111/bjh.20251
  - Predictors: ANA titre, thyroglobulin antibody, corticosteroid response, bleeding severity

- **Grdinic et al. (2024)** — "Developing a machine learning model for bleeding prediction in patients with cancer-associated thrombosis." *J Thromb Haemost*, 22(4), 1094–1104. DOI: 10.1016/j.jtha.2023.12.034
  - First ML-based risk model for bleeding in CAT, outperforming conventional CAT-BLEED score

### Agentic AI in Healthcare Literature
- **Frontiers in Medicine (2025)** — "A self-correcting Agentic Graph RAG for clinical decision support in hepatology." DOI: 10.3389/fmed.2025.1716327
  - Agentic Graph RAG with self-correcting "retrieve-evaluate-refine" loop; closely aligns with proposed architecture

- **AWS (2026)** — Amazon Connect Health: agentic AI for healthcare built for care delivery
  - Production example of agentic AI in clinical settings using AWS infrastructure

- **GitHub: AgenticHealthAI/Awesome-AI-Agents-for-Healthcare** — Curated list of 100+ papers on AI agents in healthcare (2024–2025)

---

## 5. AWS Architecture — Detailed Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 Layer 4: Application & Delivery              │
│  API Gateway + Cognito │ React Web App (Vietnamese) │ Guardrails │
├─────────────────────────────────────────────────────────────┤
│              Layer 3: Agentic AI Orchestration               │
│         Bedrock Agent (IDA) — Supervisor Agent               │
│    ┌──────────────┬──────────────┬──────────────┐           │
│    │ Data Process  │ Prediction   │ Explanation   │           │
│    │ Agent         │ Agent        │ Agent         │           │
│    │ (Lambda)      │ (Lambda→SM)  │ (RAG+Bedrock) │           │
│    └──────────────┴──────────────┴──────────────┘           │
├─────────────────────────────────────────────────────────────┤
│            Layer 2: ML Model Training & Serving              │
│  SageMaker Studio │ SageMaker Endpoint │ SageMaker Clarify   │
├─────────────────────────────────────────────────────────────┤
│             Layer 1: Data Ingestion & Storage                │
│  Amazon S3 │ AWS Glue │ DynamoDB │ OpenSearch Serverless     │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Data Ingestion and Storage

#### Amazon S3 — Data Lake
- **Purpose**: Store raw EHR exports from BV TMHH
- **Bucket structure**:
  - `s3://itp-project/raw/` — Original CSV/JSON exports
  - `s3://itp-project/processed/` — Cleaned, transformed data
  - `s3://itp-project/models/` — Trained model artifacts
  - `s3://itp-project/guidelines/` — ASH/ISTH guideline PDFs
- **Encryption**: SSE-S3 (AES-256) at rest
- **Versioning**: Enabled for data lineage tracking

#### AWS Glue — ETL Pipeline
- **Purpose**: Data cleaning, transformation, and feature engineering
- **Tasks**:
  - Handle missing values (multiple imputation for <20% missing)
  - Encode categorical variables (ITP type, infection status, etc.)
  - SMOTE oversampling for class imbalance
  - Train/test split (80/20)
  - Feature scaling and normalization
- **Output**: Clean feature matrices written to S3 processed bucket

#### Amazon DynamoDB — Patient Feature Store
- **Purpose**: Low-latency storage for patient feature vectors
- **Schema**: Patient ID (partition key) + 10 clinical features
- **Use case**: Prediction agent reads features in real-time for inference
- **On-demand capacity**: Scales automatically for variable workloads

#### Amazon OpenSearch Serverless — Vector Store
- **Purpose**: Store embeddings of clinical guidelines for RAG retrieval
- **Content indexed**:
  - ASH 2019 ITP Guidelines
  - ISTH Critical Bleeding Criteria (Sirotich et al., 2021)
  - Provan et al. (2019) International Consensus Report
  - Vietnamese clinical protocols from BV TMHH
- **Embedding model**: Amazon Titan Embeddings v2 (via Bedrock)
- **Chunking strategy**: RecursiveCharacterTextSplitter, 512 tokens per chunk, 50 token overlap
- **Similarity search**: Maximal Marginal Relevance (MMR) for diverse retrieval

#### Amazon CloudWatch — Monitoring
- **Purpose**: Logging, monitoring, and audit trail for all components
- **Tracks**: API calls, model inference latency, agent execution traces, error rates

### Layer 2: ML Model Training and Serving

#### SageMaker Studio — Model Development
- **Purpose**: Train and evaluate the 4 ML models
- **Algorithms**:
  - **Random Forest**: SageMaker built-in algorithm (optimized for distributed training)
  - **XGBoost**: SageMaker built-in algorithm
  - **LightGBM**: Custom container via Scikit-learn framework
  - **Logistic Regression**: Custom container via Scikit-learn framework
- **Hyperparameter optimization**: GridSearchCV within SageMaker Processing jobs
- **Cross-validation**: 5-fold or 10-fold CV
- **Instance type**: `ml.m5.xlarge` (4 vCPU, 16 GB RAM) — sufficient for tabular data

#### SageMaker Endpoint — Real-Time Inference
- **Purpose**: Deploy the best-performing model for real-time predictions
- **Deployment**: Single model endpoint (likely RF or XGBoost based on An et al. precedent)
- **Instance type**: `ml.m5.large` (cost-effective for inference)
- **Auto-scaling**: Scale to zero when idle (Serverless Inference option available)
- **A/B testing**: Optional — deploy two models to compare in production
- **Input**: 10-feature vector (JSON)
- **Output**: Bleeding risk probability (0–1) + confidence interval

#### SageMaker Clarify — Explainability
- **Purpose**: Generate SHAP explanations for each prediction automatically
- **Output**: Per-feature SHAP values showing contribution to bleeding risk
- **Bias detection**: Monitor for demographic bias (age, gender) in predictions
- **Integration**: SHAP values passed to Explanation Agent for natural language generation

### Layer 3: Agentic AI Orchestration

#### Bedrock Agent: IDA (Intelligent Doctor Assistant) — Supervisor
- **Purpose**: Receive clinician queries and orchestrate sub-agents
- **Foundation Model**: Claude 3 Haiku (via Bedrock) — fast, cost-effective, multilingual
- **Agent description**: "You are a clinical decision support assistant for ITP bleeding risk assessment at BV Truyền máu Huyết học. You help clinicians assess patient bleeding risk by coordinating data processing, prediction, and explanation agents."
- **Action groups**: Three action groups mapping to the three sub-agents
- **Language**: Vietnamese (Claude supports Vietnamese natively)

#### Data Processing Agent
- **Implementation**: AWS Lambda function (Python runtime)
- **Purpose**: Validate and transform raw patient input into the 10-feature vector
- **Input validation**:
  - Age: numeric, 18–120
  - PLT count: numeric, 0–500 × 10⁹/L
  - ITP type: one of [newly_diagnosed, persistent, chronic]
  - Binary variables: infection, diabetes, CVD, low lymphocyte, skin bleeding, low PLT
  - Disease duration: numeric, months
- **Error handling**: Return clear Vietnamese error messages for invalid inputs
- **Output**: Structured JSON feature vector ready for ML inference

#### Prediction Agent
- **Implementation**: AWS Lambda function (Python + boto3)
- **Purpose**: Invoke the SageMaker endpoint and return the prediction
- **Workflow**:
  1. Receive validated feature vector from Data Processing Agent
  2. Call SageMaker endpoint via `invoke_endpoint()`
  3. Parse prediction response (risk probability)
  4. Call SageMaker Clarify for SHAP values
  5. Return structured result: `{risk_score: 0.78, risk_level: "high", shap_values: {...}}`

#### Explanation Agent
- **Implementation**: Bedrock Agent with Knowledge Base (RAG)
- **Purpose**: Generate clinician-friendly, guideline-backed explanations
- **Knowledge Base**: Amazon Bedrock Knowledge Base connected to OpenSearch Serverless
- **Prompt template**:
  ```
  Based on the following patient data and ML prediction, generate a clinical 
  explanation in Vietnamese for the attending physician:
  
  Patient features: {features}
  Predicted bleeding risk: {risk_score} ({risk_level})
  Top contributing factors (SHAP): {shap_top_3}
  
  Reference the relevant ASH/ISTH guidelines to support your explanation.
  Include specific recommendations for monitoring or intervention.
  ```
- **Output example**:
  > "Bệnh nhân có nguy cơ xuất huyết cao (78%). Các yếu tố đóng góp chính: (1) Nhiễm trùng kèm theo — theo ISTH, nhiễm trùng là yếu tố nguy cơ hàng đầu cho xuất huyết nghiêm trọng; (2) Tiểu cầu thấp <20×10⁹/L — theo ASH 2019, mức này cần theo dõi sát; (3) Bệnh lý tim mạch — tăng nguy cơ do thoái hóa mạch máu. Khuyến nghị: Theo dõi dấu hiệu xuất huyết nội tạng, cân nhắc truyền tiểu cầu nếu có triệu chứng."

### Layer 4: Application and Delivery

#### API Gateway + Cognito — Authentication & API
- **API Gateway**: RESTful API endpoints
  - `POST /predict` — Submit patient data, receive prediction + explanation
  - `GET /history/{patient_id}` — Retrieve past predictions
  - `GET /model-info` — Model performance metrics
- **Cognito**: User authentication
  - User pool for BV TMHH clinicians
  - MFA enabled
  - Role-based access (physician, nurse, admin)

#### Amplify / CloudFront — Web Application
- **Framework**: React.js with Vietnamese localization
- **Hosting**: AWS Amplify (CI/CD built-in) or S3 + CloudFront
- **UI Components**:
  - Patient data input form (10 clinical variables)
  - Risk score visualization (gauge chart, color-coded)
  - SHAP waterfall chart (feature contributions)
  - Natural language explanation panel
  - Patient history timeline
- **Responsive**: Works on desktop and mobile (tablet in clinic)

#### Bedrock Guardrails — Safety
- **Content filtering**: Block inappropriate or non-medical responses
- **PHI protection**: Ensure patient identifiers are not logged or exposed
- **Topic restrictions**: Limit LLM responses to ITP/hematology scope
- **Word filters**: Block any treatment prescriptions (system is for risk assessment only, not treatment decisions)

---

## 6. Key Clinical Variables (10 Features)

| # | Variable | Type | Values / Units | Collection |
|---|----------|------|----------------|------------|
| 1 | Infection | Categorical | Yes / No | EHR |
| 2 | Uncontrolled diabetes | Categorical | Yes / No | EHR |
| 3 | Age | Continuous | Years (median, Q1-Q3) | EHR |
| 4 | ITP type | Categorical | Newly diagnosed / Persistent / Chronic | EHR |
| 5 | Cardiovascular disease | Categorical | Yes / No | EHR |
| 6 | Low lymphocyte count | Categorical | < 1 × 10⁹/L | Lab results |
| 7 | Skin and mucosa bleeding | Categorical | Yes / No | Clinical exam |
| 8 | Initial PLT count | Continuous | × 10⁹/L | Lab at diagnosis |
| 9 | Low PLT (current) | Categorical | < 20 × 10⁹/L | Latest lab |
| 10 | Disease duration | Continuous | Months / Years | Medical history |

**Outcome variable**: Hemorrhage ≥ Grade 2 (WHO scale) — binary (Yes/No)

---

## 7. Implementation Timeline

### Phase 1: Data & ML Core (Months 1–2)
- [ ] Set up AWS account with HIPAA-eligible services
- [ ] Configure S3 buckets, IAM roles, VPC
- [ ] Build AWS Glue ETL pipeline for hospital data
- [ ] Clean and preprocess data (handle missing values, SMOTE)
- [ ] Train 4 ML models in SageMaker Studio
- [ ] Evaluate models: AUC, sensitivity, specificity, accuracy
- [ ] Generate SHAP analysis with SageMaker Clarify
- [ ] **Deliverable**: All results for Nhiên's thesis Objectives 1 & 2

### Phase 2: Agentic AI Layer (Months 3–4)
- [ ] Deploy best ML model to SageMaker Endpoint
- [ ] Chunk and embed clinical guidelines into OpenSearch Serverless
- [ ] Build Bedrock Knowledge Base (RAG pipeline)
- [ ] Implement Data Processing Agent (Lambda)
- [ ] Implement Prediction Agent (Lambda → SageMaker)
- [ ] Implement Explanation Agent (Bedrock + RAG)
- [ ] Configure Bedrock Agents orchestration (IDA supervisor)
- [ ] Set up Bedrock Guardrails for safety
- [ ] **Deliverable**: Working agentic AI pipeline

### Phase 3: Application & Testing (Months 5–6)
- [ ] Build React web application with Vietnamese UI
- [ ] Set up API Gateway + Cognito authentication
- [ ] Deploy via Amplify / CloudFront
- [ ] User acceptance testing with clinicians at BV TMHH
- [ ] Collect feedback and iterate
- [ ] Performance benchmarking (latency, accuracy in real use)
- [ ] **Deliverable**: Production-ready clinical tool (Nhiên's Objective 3)

---

## 8. Cost Estimate (Monthly, Development Phase)

| Service | Estimated Cost | Notes |
|---------|---------------|-------|
| SageMaker Training | $20–40 | ml.m5.xlarge spot instances |
| SageMaker Endpoint | $30–50 | ml.m5.large, scale to zero when idle |
| Bedrock API (Claude Haiku) | $10–30 | Pay per token (~$0.25/1M input tokens) |
| OpenSearch Serverless | $10–20 | Minimum 0.5 OCU |
| S3 + DynamoDB + Lambda | $5–10 | Negligible at research scale |
| Amplify + CloudFront | $5–10 | Free tier covers most usage |
| **Total** | **$80–160/month** | |

**Cost optimization tips**:
- Use SageMaker Serverless Inference (pay per request) instead of always-on endpoints during development
- Use Bedrock Claude Haiku (cheapest) for development, upgrade to Sonnet for production if needed
- Leverage AWS Free Tier for Lambda, S3, DynamoDB, CloudWatch
- Apply for AWS Healthcare credits or research credits

---

## 9. Security and Compliance Considerations

- **HIPAA**: All AWS services used are HIPAA-eligible; sign BAA with AWS
- **Data encryption**: SSE-S3 at rest, TLS 1.2+ in transit
- **VPC isolation**: All compute resources in private subnets
- **IAM**: Least-privilege access; separate roles for data, ML, and application layers
- **Cognito**: MFA for clinician authentication
- **Bedrock Guardrails**: PHI filtering, topic restrictions
- **CloudWatch**: Full audit trail of all predictions and agent actions
- **Data de-identification**: Patient data de-identified before entering the system (hospital responsibility)

---

## 10. Technical Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Lake | Amazon S3 | Raw and processed data storage |
| ETL | AWS Glue | Data cleaning and transformation |
| Feature Store | Amazon DynamoDB | Low-latency feature retrieval |
| Vector Store | OpenSearch Serverless | RAG embeddings for guidelines |
| ML Training | SageMaker Studio | Train RF, XGBoost, LightGBM, LR |
| ML Serving | SageMaker Endpoint | Real-time bleeding risk prediction |
| Explainability | SageMaker Clarify | SHAP values and bias detection |
| LLM | Amazon Bedrock (Claude) | Natural language explanation generation |
| Agent Orchestration | Bedrock Agents | IDA supervisor + sub-agents |
| RAG | Bedrock Knowledge Base | Guideline retrieval for explanations |
| Safety | Bedrock Guardrails | Content filtering, PHI protection |
| Serverless Compute | AWS Lambda | Agent action implementations |
| API | API Gateway | RESTful API for web app |
| Authentication | Amazon Cognito | Clinician login with MFA |
| Frontend | React.js + Amplify | Vietnamese-language web application |
| CDN | CloudFront | Fast content delivery in Vietnam |
| Monitoring | CloudWatch | Logging, metrics, audit trail |
| Programming | Python 3.11+ | ML (Scikit-learn, XGBoost), Lambda functions |

---

## 11. Research Novelty and Contributions

1. **First ML-based ITP bleeding prediction model in Vietnam** — addresses the research gap identified in the proposal
2. **Agentic AI for hematology** — novel application of autonomous multi-agent systems to ITP, combining prediction with guideline-backed reasoning
3. **Vietnamese-language clinical interface** — practical tool for clinicians at BV TMHH
4. **Hybrid architecture** — demonstrates how classical ML (trusted, validated) can be enhanced with modern AI (explainable, interactive) for clinical decision support
5. **AWS cloud deployment** — scalable infrastructure that can extend to other hematologic conditions

---

*This document serves as the technical blueprint for the ITP Bleeding Prediction project. The ML core satisfies the medical thesis requirements, while the Agentic AI wrapper provides the technical innovation and practical clinical tool.*
