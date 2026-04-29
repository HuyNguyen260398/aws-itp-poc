# ITP Bleeding Prediction Research Plan — v0.0.4

## Hybrid ML + Agentic AI System on AWS

**Project**: Bước đầu đánh giá hiệu quả dự đoán chảy máu của các mô hình học máy ở bệnh nhân người lớn giảm tiểu cầu miễn dịch tại Bệnh viện Truyền máu Huyết học giai đoạn 2022–2026

**Researcher**: Trần Xuân Nhiên (Master's Thesis, 2025–2027)

**Technical Support**: Huy (Software Engineer)

**Version**: 0.0.4

**Last Updated**: April 2026

**Changelog**:
- v0.0.1 (April 2026): Initial 6-month plan
- v0.0.2 (April 2026): Extended to 9-month timeline; added technical improvements, detailed cost analysis (Option A/B), similar AWS architecture references, risk mitigation, and architecture decision matrix
- v0.0.3 (April 2026): Delta document — focused update on timeline, cost, and technical improvements (not standalone)
- v0.0.4 (April 2026): Merged v0.0.2 and v0.0.3 into a single comprehensive document; reconciled all section differences

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

- **Phase 1–2 (ML Core)**: Train RF, XGBoost, LightGBM, LR on hospital ITP data → produces AUC comparisons, SHAP analysis, clinical validation
- **Phase 3–4 (Agentic AI Wrapper)**: Deploy best ML model on AWS, wrap with LLM agents for explanation generation and Vietnamese-language clinical interface

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
│  Amazon S3 │ AWS Glue │ DynamoDB │ Aurora pgvector (RAG)     │
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
- **Purpose**: Low-latency storage for patient feature vectors and feedback
- **Schema**: Patient ID (partition key) + 10 clinical features
- **Use case**: Prediction agent reads features in real-time for inference; also stores clinician feedback (👍/👎) for future retraining
- **On-demand capacity**: Scales automatically for variable workloads

#### Amazon Aurora Serverless v2 (pgvector) — Vector Store *(replaces OpenSearch Serverless)*
- **Purpose**: Store embeddings of clinical guidelines for RAG retrieval
- **Rationale**: Eliminates the $350/month OpenSearch Serverless cost floor; scales to ~0.5 ACU minimum (~$15/month)
- **Content indexed**:
  - ASH 2019 ITP Guidelines
  - ISTH Critical Bleeding Criteria (Sirotich et al., 2021)
  - Provan et al. (2019) International Consensus Report
  - Vietnamese clinical protocols from BV TMHH
- **Embedding model**: Amazon Titan Embeddings v2 (via Bedrock)
- **Chunking strategy**: RecursiveCharacterTextSplitter, 512 tokens per chunk, 50 token overlap
- **Similarity search**: Maximal Marginal Relevance (MMR) for diverse retrieval
- **Upgrade path**: Can migrate to OpenSearch Serverless if RAG quality is insufficient at scale

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
- **Hyperparameter optimization**: SageMaker Automatic Model Tuning (Bayesian optimization) — replaces GridSearchCV for better parameter search
- **Cross-validation**: Stratified 10-fold CV for robust evaluation on small dataset
- **Ensemble stacking**: Meta-model stacking RF, XGBoost, LightGBM, and LR predictions for potentially higher AUC
- **Calibration**: Platt scaling or isotonic regression for well-calibrated risk probabilities (critical for clinical use)
- **Instance type**: `ml.m5.xlarge` (4 vCPU, 16 GB RAM) — sufficient for tabular data; spot instances for 60–90% savings

#### SageMaker Endpoint — Real-Time Inference
- **Purpose**: Deploy the best-performing model for real-time predictions
- **Deployment**: SageMaker Serverless Inference (pay per request, scales to zero) — upgradeable to always-on `ml.m5.large` if UAT latency is a problem
- **A/B testing**: Optional — deploy two models to compare in production (Months 8–9)
- **Input**: 10-feature vector (JSON)
- **Output**: Bleeding risk probability (0–1) + confidence interval
- **Cold start**: 1–3 seconds acceptable for research; upgrade to always-on for production

#### SageMaker Clarify — Explainability
- **Purpose**: Generate SHAP explanations for each prediction automatically
- **Output**: Per-feature SHAP values showing contribution to bleeding risk
- **Bias detection**: Monitor for demographic bias (age, gender) in predictions
- **Integration**: SHAP values passed to Explanation Agent for natural language generation

#### SageMaker Model Monitor
- **Purpose**: Detect data drift and model degradation over time
- **Schedule**: Monthly checks during research phase; move to continuous if deployed in production

### Layer 3: Agentic AI Orchestration

#### Bedrock Agent: IDA (Intelligent Doctor Assistant) — Supervisor
- **Purpose**: Receive clinician queries and orchestrate sub-agents
- **Foundation Model**: Claude 3 Haiku (via Bedrock) — fast, cost-effective, multilingual; upgradeable to Sonnet if explanation quality needs improvement
- **Intelligent routing**: Simple queries → Nova Micro / Haiku; complex queries → Sonnet (Bedrock routing feature)
- **Prompt caching**: Cache system prompt and clinical guidelines context to reduce latency and cost by up to 90% on repeated queries
- **Multi-turn conversation**: Session management for follow-up questions (e.g., "What if the patient also has infection?")
- **Agent description**: "You are a clinical decision support assistant for ITP bleeding risk assessment at BV Truyền máu Huyết học. You help clinicians assess patient bleeding risk by coordinating data processing, prediction, and explanation agents."
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
- **Knowledge Base**: Amazon Bedrock Knowledge Base connected to Aurora pgvector
- **Self-correcting RAG**: Retrieve-evaluate-refine loop where the agent evaluates its own retrieval quality before generating explanations (based on Agentic Graph RAG for hepatology pattern)
- **LLM-as-a-judge**: A second LLM evaluates explanation quality, accuracy, and clinical relevance (Months 8–9)
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

#### S3 + CloudFront — Web Application *(replaces Amplify)*
- **Framework**: React.js with Vietnamese localization
- **Hosting**: S3 static site + CloudFront CDN (simpler, cheaper than Amplify for research)
- **UI Components**:
  - Patient data input form (10 clinical variables)
  - Risk score visualization (gauge chart, color-coded)
  - SHAP waterfall chart (feature contributions — built-in React charts, no QuickSight)
  - Natural language explanation panel
  - Patient history timeline
  - Clinician feedback buttons (👍/👎) stored in DynamoDB
  - Offline mode: cache frequently used guideline responses locally (important for Vietnamese hospital connectivity)
- **Responsive**: Optimized for tablet use at the bedside

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

## 7. Implementation Timeline (9-Month Plan)

### Phase 1: Foundation and Data Engineering (Months 1–2)

| Week | Task | Deliverable |
|------|------|-------------|
| 1–2 | AWS account setup, IAM roles, VPC configuration, HIPAA compliance review | Secure cloud environment |
| 3–4 | Build S3 data lake structure; develop AWS Glue ETL pipeline | Automated data ingestion |
| 5–6 | Data cleaning, missing value imputation, exploratory data analysis | Clean dataset + EDA report |
| 7–8 | Feature engineering, SMOTE oversampling, train/test split | Feature store in DynamoDB + S3 |

**Nhiên's thesis output**: Objective 1 — clinical/lab characteristics + bleeding status description

### Phase 2: ML Model Development and Evaluation (Months 3–4)

| Week | Task | Deliverable |
|------|------|-------------|
| 9–10 | Train 4 ML models (RF, XGBoost, LightGBM, LR) in SageMaker Studio | Trained model artifacts |
| 11–12 | Bayesian hyperparameter optimization via SageMaker Automatic Model Tuning | Optimized models |
| 13–14 | Model evaluation: AUC, sensitivity, specificity, accuracy, calibration curves | Performance comparison report |
| 15–16 | SHAP analysis with SageMaker Clarify; ensemble stacking meta-model | Explainability report + stacked model |

**Nhiên's thesis output**: Objective 2 — model comparison + feature importance analysis

### Phase 3: Agentic AI Layer (Months 5–6)

| Week | Task | Deliverable |
|------|------|-------------|
| 17–18 | Deploy best ML model to SageMaker Serverless endpoint; build Lambda action functions | Real-time inference API |
| 19–20 | Chunk and embed clinical guidelines (ASH, ISTH, Vietnamese protocols) into Aurora pgvector; build Bedrock Knowledge Base | RAG knowledge base |
| 21–22 | Build Bedrock Agents: IDA supervisor, data processing, prediction, explanation agents | Working agent pipeline |
| 23–24 | Configure Bedrock Guardrails; implement prompt caching; configure intelligent routing; test agent orchestration | Safe, optimized agent system |

### Phase 4: Application Development (Month 7)

| Week | Task | Deliverable |
|------|------|-------------|
| 25–26 | Build React web app with Vietnamese UI; integrate API Gateway + Cognito | Frontend application |
| 27–28 | Build dashboard: risk gauge, SHAP waterfall chart, explanation panel, patient history, feedback buttons | Complete clinical interface |

**Nhiên's thesis output**: Objective 3 — online clinical tool

### Phase 5: Testing, Validation, and Optimization (Months 8–9)

| Week | Task | Deliverable |
|------|------|-------------|
| 29–30 | Internal testing: unit tests, integration tests, load testing | Test reports |
| 31–32 | User acceptance testing with 5–10 clinicians at BV TMHH | UAT feedback |
| 33–34 | A/B testing between models; RAG evaluation using LLM-as-a-judge | Model selection validation |
| 35–36 | Cost optimization, documentation, final deployment, thesis writing support | Production system + thesis |

---

## 8. Technical Improvements (Enabled by 9-Month Timeline)

### 8.1 Model Improvements

- **Bayesian Hyperparameter Optimization**: SageMaker Automatic Model Tuning (Bayesian optimization) — replaces GridSearchCV for better parameter search across all 4 models
- **Ensemble Stacking**: Meta-model stacking RF, XGBoost, LightGBM, and LR predictions for potentially higher AUC than any single model
- **Calibration Curves**: Platt scaling or isotonic regression to ensure predicted probabilities are well-calibrated (critical for clinical risk scores)
- **Cross-Validation Strategy**: Stratified 10-fold CV for robust evaluation on small dataset (n~150)
- **Model Monitoring**: SageMaker Model Monitor (monthly checks) for data drift and model degradation detection

### 8.2 Agentic AI Improvements

- **Multi-Turn Conversation**: IDA agent handles follow-up questions (e.g., "What if the patient also has infection?") using Bedrock session management
- **LLM-as-a-Judge Evaluation**: Second LLM evaluates quality, accuracy, and clinical relevance of Explanation Agent output (Months 8–9)
- **Prompt Caching**: Cache system prompt and clinical guidelines context — up to 90% latency and cost reduction on repeated queries
- **Intelligent Prompt Routing**: Route simple queries to Nova Micro/Haiku and complex queries to Sonnet via Bedrock routing
- **Self-Correcting RAG**: Retrieve-evaluate-refine loop where the agent evaluates its own retrieval quality before generating explanations

### 8.3 Application Improvements

- **Feedback Loop**: Clinicians rate prediction quality (👍/👎); feedback stored in DynamoDB for future model retraining
- **A/B Testing Framework**: Deploy two models simultaneously and compare real-world performance (Months 8–9)
- **Offline Mode**: Cache frequently used guideline responses locally for intermittent hospital internet connectivity
- **Mobile Responsive**: React app optimized for tablet use at the bedside

### 8.4 Data Engineering Improvements

- **Data Version Control**: S3 versioning + AWS Glue Data Catalog for full data lineage
- **Automated Retraining Pipeline**: SageMaker Pipelines to retrain models when new patient data reaches a threshold
- **Simpler Feature Store**: S3 + DynamoDB (avoids SageMaker Feature Store overhead at research scale)

---

## 9. Similar AWS Architectures and Solutions

### 9.1 AWS Healthcare Industry Lens — ML Reference Architecture

The official AWS Well-Architected Healthcare Industry Lens reference architecture:
1. Data collected and pre-processed using a data lake (S3 + Glue)
2. Features extracted and stored in feature stores for model training
3. Ground truth labels populated and reviewed by humans
4. Standard ML training, tuning, and evaluation workflows
5. Models reviewed by cross-functional stakeholders (clinical + regulatory)
6. Accepted models integrated with care delivery IT systems (EHRs)

**Alignment**: Our architecture follows this reference pattern exactly, with the addition of an Agentic AI layer between the ML model and the end-user interface.

### 9.2 AWS Guidance for Multi-Modal Data Analysis with Health and ML Services

AWS Solutions Library guidance demonstrating S3 → ETL → Feature Store → SageMaker → QuickSight pipeline for patient outcome prediction.

**Alignment**: While our project uses structured tabular data (not imaging), the data pipeline pattern is identical. We replace QuickSight with React built-in charts.

### 9.3 ALMA (Advanced Learning Medical Assistant) — CatSalut, Spain

Catalonia's public health service Bedrock agent + RAG architecture over clinical guidelines. Results: 65% of 20,000 healthcare professionals adopted it, 98% user satisfaction, 98% accuracy.

**Alignment**: Very similar architecture — validates the feasibility of our Explanation Agent approach in a real healthcare system.

### 9.4 NoHarm — Brazil Public Health System

Deployed in 200+ hospitals, analyzing 5 million prescriptions/month. Uses NER for clinical notes, LLM-based summarization, and feedback-driven learning loops.

**Alignment**: Demonstrates LLM-powered clinical decision support at scale in a developing country's healthcare system — directly relevant to Vietnam.

### 9.5 AWS Healthcare RAG Evaluation (Radiology)

AWS Machine Learning Blog (2025): LLM-as-a-judge for evaluating clinical AI output quality using Amazon Bedrock Knowledge Bases evaluation capabilities.

**Alignment**: We adopt the same LLM-as-a-judge approach to evaluate our Explanation Agent during Phase 5.

### 9.6 OMOP CDM on AWS — Clinical Data Platform

S3 → Glue → Feature Store → SageMaker pipeline with governance via Lake Formation and Macie for PHI detection.

**Alignment**: Our data pipeline follows the same pattern. Could adopt OMOP CDM if BV TMHH standardizes their data model in the future.

---

## 10. Cost Analysis

### Assumptions
- 9-month project duration
- Development and testing usage (not production scale)
- ~50 predictions/day during testing (Months 7–9)
- ~100 RAG queries/day during testing
- 1–2 developers
- AWS region: ap-southeast-1 (Singapore) — closest to Vietnam

### Option A: Full Potential Implementation

Maximum-capability architecture with best performance, full features, and production-grade infrastructure.

| Service | Purpose | Monthly Cost | Notes |
|---------|---------|-------------|-------|
| SageMaker Studio | ML development notebooks | $50–80 | ml.m5.xlarge, ~4h/day usage |
| SageMaker Training | Model training jobs | $30–60 | ml.m5.xlarge spot instances |
| SageMaker Endpoint | Real-time ML inference (always-on) | $80–120 | ml.m5.large |
| SageMaker Clarify | SHAP explanations | $20–30 | Per-inference SHAP computation |
| SageMaker Feature Store | Feature versioning + serving | $15–25 | Online + offline store |
| SageMaker Model Monitor | Drift detection | $10–15 | Continuous monitoring |
| Bedrock (Claude Sonnet) | LLM for explanation agent | $60–120 | ~100 queries/day, ~3K input + 500 output tokens |
| Bedrock Agents | Agent orchestration | $20–40 | Token overhead for agent reasoning |
| Bedrock Knowledge Base | RAG pipeline | $10–15 | Embedding + retrieval |
| Bedrock Guardrails | Safety filtering | $10–20 | Per-request filtering |
| OpenSearch Serverless | Vector store for RAG | $350–400 | **Minimum floor: ~$350/month (0.5 OCU)** |
| Amazon S3 | Data lake | $5–10 | Storage + requests |
| AWS Glue | ETL pipeline | $10–20 | Crawler + ETL job runs |
| DynamoDB | Patient data + feedback | $5–10 | On-demand capacity |
| Lambda | Agent action functions | $2–5 | Pay per invocation |
| API Gateway | REST API | $5–10 | Per-request pricing |
| Cognito | Authentication | $0–5 | Free tier covers <50K MAU |
| Amplify / CloudFront | Web hosting + CDN | $5–10 | Low traffic during research |
| CloudWatch | Monitoring + logging | $10–20 | Logs, metrics, alarms |
| QuickSight | Analytics dashboard | $24 | 1 author license |

**Option A Monthly Total: $720–1,040/month**

**Option A 9-Month Total: $6,500–$9,400**

**AWS Services: 20**

### Option B: Cost-Optimized Implementation *(Recommended)*

Achieves all core research goals with significant cost reductions. Trades some production-grade features for affordability.

#### Key Cost Optimization Strategies

1. **Replace OpenSearch Serverless with pgvector on Aurora Serverless v2** — eliminates the $350/month floor
2. **Use SageMaker Serverless Inference** instead of always-on endpoints — pay only per request
3. **Use Amazon Nova Micro / Claude Haiku** instead of Sonnet — 10–50x cheaper per token
4. **Use Intelligent Prompt Routing** — auto-route simple queries to cheapest model
5. **Enable Prompt Caching** — cache system prompts and guideline context (up to 90% savings)
6. **Use Batch inference** for non-real-time tasks (50% discount)
7. **Replace SageMaker Studio with local Jupyter** — train locally, deploy on AWS
8. **Use S3 + DynamoDB instead of SageMaker Feature Store** — simpler, effectively free
9. **Skip QuickSight** — use built-in React charts instead
10. **Use SageMaker Model Monitor only monthly** — not continuous

| Service | Purpose | Monthly Cost | Notes |
|---------|---------|-------------|-------|
| Local Jupyter + S3 | ML development | $0 | Train locally, upload artifacts to S3 |
| SageMaker Training | Model training jobs | $10–20 | Spot instances, infrequent runs |
| SageMaker Serverless Inference | ML inference | $5–15 | Pay per request, scales to zero |
| Bedrock (Nova Micro + Haiku) | LLM for explanation agent | $5–15 | Nova Micro: $0.035/1M input, Haiku: $0.80/1M input |
| Bedrock Agents | Agent orchestration | $5–10 | Cheaper with Haiku backbone |
| Bedrock Knowledge Base | RAG pipeline | $5–10 | Embedding costs only |
| Bedrock Prompt Caching | Reduce repeated context cost | -$5 to -$10 | Savings on cached guideline context |
| Aurora Serverless v2 (pgvector) | Vector store for RAG | $15–30 | ~$0.12/ACU-hour, scales to 0.5 ACU |
| Amazon S3 | Data lake + feature store | $3–5 | Also used as simple feature store |
| AWS Glue | ETL pipeline | $5–10 | Minimal jobs |
| DynamoDB | Patient data + feedback | $2–5 | On-demand, low volume |
| Lambda | Agent action functions | $1–3 | Free tier: 1M requests/month |
| API Gateway | REST API | $2–5 | Low volume |
| Cognito | Authentication | $0 | Free tier |
| S3 + CloudFront | Web hosting | $2–5 | Static site hosting |
| CloudWatch | Monitoring (basic) | $5–10 | Essential metrics only |

**Option B Monthly Total: $65–155/month**

**Option B 9-Month Total: $585–$1,395**

**AWS Services: 14**

### Cost Comparison Summary

| Metric | Option A: Full Potential | Option B: Cost-Optimized |
|--------|--------------------------|--------------------------|
| **Monthly cost** | $720–1,040 | $65–155 |
| **9-month total** | $6,500–9,400 | $585–1,395 |
| **AWS services** | 20 | 14 |
| **LLM model** | Claude Sonnet (best quality) | Nova Micro / Haiku (good quality) |
| **Vector store** | OpenSearch Serverless ($350 floor) | Aurora pgvector (scales to ~$15) |
| **ML inference** | Always-on endpoint | Serverless (pay per request) |
| **Monitoring** | Continuous (Model Monitor + CloudWatch) | Basic (monthly checks) |
| **Dashboard** | QuickSight (professional) | React charts (built-in) |
| **Feature store** | SageMaker Feature Store | S3 + DynamoDB (simple) |
| **Explanation quality** | High (Sonnet) | Good (Haiku) — adequate for research |
| **Cold start latency** | None (always-on) | 1–3 seconds (serverless) |
| **Best for** | Publication-ready, production-grade | Research project, thesis demonstration |

### Recommendation

**Start with Option B** during Months 1–7 (development and initial testing), then **selectively upgrade to Option A components** in Months 8–9 if budget allows. Staged upgrade path:

1. First upgrade: Aurora pgvector → OpenSearch Serverless (only if RAG quality is insufficient)
2. Second upgrade: Haiku → Sonnet (only if explanation quality needs improvement)
3. Third upgrade: Serverless Inference → always-on endpoint (only if latency is a problem during UAT)

This staged approach keeps the 9-month total at approximately **$800–2,500** while maintaining flexibility to scale up where it matters.

---

## 11. Cost Optimization Tips

- **AWS Activate for Research**: Apply for AWS credits (up to $5,000–$100,000) — academic/research projects often qualify
- **AWS Free Tier**: Lambda (1M requests), DynamoDB (25GB), S3 (5GB), Cognito (50K MAU), CloudWatch (basic) are free
- **Spot Instances**: Use for SageMaker training — 60–90% savings over on-demand
- **Bedrock Flex Tier**: 50% discount for non-urgent inference (same API, asynchronous processing)
- **Prompt Caching**: Cache ASH/ISTH guidelines system prompt — up to 90% savings on repeated context
- **AWS Budgets**: Set hard monthly limits and alerts at 50%, 80%, 100% thresholds
- **Turn off idle resources**: Delete SageMaker endpoints and notebook instances when not in use — idle endpoints are the #1 cause of unexpected AWS ML bills
- **Region selection**: ap-southeast-1 (Singapore) is closest to Vietnam; consider us-east-1 if data residency is not a concern

---

## 12. Security and Compliance Considerations

- **HIPAA**: All AWS services used are HIPAA-eligible; sign BAA with AWS
- **Data encryption**: SSE-S3 at rest, TLS 1.2+ in transit
- **VPC isolation**: All compute resources in private subnets
- **IAM**: Least-privilege access; separate roles for data, ML, and application layers
- **Cognito**: MFA for clinician authentication
- **Bedrock Guardrails**: PHI filtering, topic restrictions, treatment prescription blocking
- **CloudWatch**: Full audit trail of all predictions and agent actions
- **Data de-identification**: Patient data de-identified before entering the system (hospital responsibility)
- **Lambda**: Functions must not log patient data

---

## 13. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenSearch Serverless cost floor ($350/month) | Budget overrun | Use Aurora pgvector (Option B default) |
| Bedrock agent token multiplication (5–10x) | Unexpected LLM costs | Set MaxTokens limits; use prompt caching; intelligent routing |
| Idle SageMaker endpoint running 24/7 | $80–120/month wasted | Use Serverless Inference; auto-shutdown schedule |
| CloudWatch log volume | $0.50/GB ingestion adds up | Set log retention to 7 days; filter verbose logs |
| LLM hallucination in clinical context | Patient safety | Bedrock Guardrails + structured output templates + self-correcting RAG |
| Small dataset (n~150) overfitting | Poor generalization | Stratified 10-fold CV, regularization, ensemble methods, calibration |
| Data quality from hospital EHR | Noisy features | Extensive EDA in Phase 1; clinical validation by Nhiên |
| Cold start latency (serverless inference) | Poor UAT experience | Upgrade to always-on endpoint in Phase 5 if needed |

---

## 14. Architecture Decision Matrix

| Decision | Option A Choice | Option B Choice | v0.0.4 Recommendation |
|----------|----------------|----------------|----------------------|
| ML training environment | SageMaker Studio | Local Jupyter | Start local; move to SageMaker if needed |
| ML inference | SageMaker Endpoint (always-on) | SageMaker Serverless | Serverless for research |
| LLM model | Claude Sonnet | Nova Micro + Haiku | Haiku (best quality/cost balance) |
| Vector database | OpenSearch Serverless | Aurora pgvector | **Aurora pgvector** |
| Feature store | SageMaker Feature Store | S3 + DynamoDB | **S3 + DynamoDB** |
| Monitoring | Model Monitor + CloudWatch | CloudWatch basic | **CloudWatch basic** |
| Dashboard | QuickSight | React built-in charts | **React charts** |
| Web hosting | Amplify | S3 + CloudFront | **S3 + CloudFront** |
| Hyperparameter tuning | GridSearchCV | Bayesian (SageMaker AMT) | **Bayesian (SageMaker AMT)** |
| Prompt routing | Single model | Intelligent routing | **Intelligent routing** |

---

## 15. Technical Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Data Lake | Amazon S3 | Raw and processed data storage |
| ETL | AWS Glue | Data cleaning and transformation |
| Feature Store | S3 + Amazon DynamoDB | Low-latency feature retrieval + feedback storage |
| Vector Store | Aurora Serverless v2 (pgvector) | RAG embeddings for clinical guidelines |
| ML Training | SageMaker (spot instances) | Train RF, XGBoost, LightGBM, LR |
| Hyperparameter Tuning | SageMaker Automatic Model Tuning | Bayesian optimization across all models |
| ML Serving | SageMaker Serverless Inference | Real-time bleeding risk prediction |
| Explainability | SageMaker Clarify | SHAP values and bias detection |
| Model Monitoring | SageMaker Model Monitor (monthly) | Data drift and degradation detection |
| LLM | Amazon Bedrock (Nova Micro + Haiku) | Natural language explanation generation |
| Agent Orchestration | Bedrock Agents | IDA supervisor + sub-agents |
| RAG | Bedrock Knowledge Base | Guideline retrieval for explanations |
| Safety | Bedrock Guardrails | Content filtering, PHI protection |
| Prompt Optimization | Bedrock Prompt Caching + Routing | Latency and cost reduction |
| Serverless Compute | AWS Lambda | Agent action implementations |
| API | API Gateway | RESTful API for web app |
| Authentication | Amazon Cognito | Clinician login with MFA |
| Frontend | React.js + S3 + CloudFront | Vietnamese-language web application with CDN |
| Monitoring | CloudWatch | Logging, metrics, audit trail |
| Programming | Python 3.11+ | ML (Scikit-learn, XGBoost), Lambda functions |

---

## 16. Research Novelty and Contributions

1. **First ML-based ITP bleeding prediction model in Vietnam** — addresses the research gap identified in the proposal
2. **Agentic AI for hematology** — novel application of autonomous multi-agent systems to ITP, combining prediction with guideline-backed reasoning
3. **Vietnamese-language clinical interface** — practical tool for clinicians at BV TMHH
4. **Hybrid architecture** — demonstrates how classical ML (trusted, validated) can be enhanced with modern AI (explainable, interactive) for clinical decision support
5. **Self-correcting RAG** — retrieve-evaluate-refine loop applied to hematology guidelines, novel contribution beyond Dhiman et al.
6. **AWS cloud deployment** — scalable infrastructure that can extend to other hematologic conditions
7. **Feedback-driven learning** — clinician feedback loop enabling continuous model improvement post-deployment

---

*This document is version 0.0.4 — a complete merge of v0.0.2 (comprehensive architecture blueprint) and v0.0.3 (timeline, cost, and technical improvements update). The ML core satisfies the medical thesis requirements (Objectives 1–3), while the Agentic AI wrapper provides technical innovation and a practical clinical tool. The 9-month timeline and cost-optimized Option B architecture are the recommended path for the master's thesis context.*
