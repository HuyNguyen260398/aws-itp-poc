# ITP Bleeding Prediction Research Plan — v0.0.7

## Multi-Agent Architecture with ML-as-a-Tool, Built for Longitudinal Patient Records

**Project**: Bước đầu đánh giá hiệu quả dự đoán chảy máu của các mô hình học máy ở bệnh nhân người lớn giảm tiểu cầu miễn dịch tại Bệnh viện Truyền máu Huyết học giai đoạn 2022–2026

**Researcher**: Trần Xuân Nhiên (Master's Thesis, 2025–2027)

**Technical Support**: Huy (Software Engineer, AWS DevOps focus)

**Version**: 0.0.7

**Status**: Major revision based on new evidence about input data format and prediction target.

**Changelog**:
- v0.0.1–0.0.4: Hybrid ML + Agentic AI (ML as core)
- v0.0.5: Pivot to pure multi-agent (no ML)
- v0.0.6: Multi-agent refactored to align with AWS AgentCore + Strands reference
- **v0.0.7**: Architecture grounded in actual hospital document format (Word discharge summaries) and trajectory-based prediction. ML returns as a *tool* the agent calls. Phase 0 added for document understanding. Timeline extended to 11 months with optional 9-month variant.

---

## 1. What changed since v0.0.6 — and why

Three pieces of new information forced this revision:

**Discovery 1**: The actual production input is **unstructured Vietnamese clinical narrative** — BV TMHH discharge summary forms (`MS 52/BV2`) in Word format, containing free-text patient history, multi-episode admission narratives, comorbidities in prose, 30+ lab values per patient, and treatment timelines.

**Discovery 2**: Patients have **multiple admissions across years**. The example patient `MAI NGỌC CƯỜNG` has four years of disease history across multiple hospitals, with documented treatment failures, HBV reactivation risk, and Cushingoid complications.

**Discovery 3**: The training data will come from the **same Word document format**, processed through a data preparation step before feeding to ML.

These three together change the architecture in fundamental ways that v0.0.6 didn't anticipate:

- **Data preparation is its own substantial subsystem**, not a one-week task. It serves both training-time and inference-time use.
- **Prediction is trajectory-based**, not snapshot-based. This changes the ML problem and the feature space.
- **The Intake-Agent becomes the dominant engineering risk** — if document understanding fails, both training and inference fail.

The ML decision from prior version analysis (keep ML as an agent tool) is **confirmed and strengthened** by these findings. The reasoning is detailed in § 3.

---

## 2. Three open questions for Nhiên

Before this plan can be finalized, three decisions are needed from Nhiên (and her advisor where relevant):

### Question 1 — Prediction window

From the latest patient record ("now"), predict bleeding within:
- **(a)** During the current admission only (matches An et al. 2023 most closely)
- **(b)** Within 30 days of the latest record (clinically useful, matches discharge planning)
- **(c)** Within 60 days (longer-term planning)
- **(d)** At any future point in available follow-up (largest target, hardest to validate)

**Plan default**: Option (b), 30 days. Justification: matches the clinical question "is it safe to discharge?" which is what the thesis ultimately addresses. Can switch to (a) if advisor wants strict comparability with An et al.

### Question 2 — Feature scope

The original proposal lists 11 variables (taken from An et al.). The documents contain much richer data. Options:
- **(a)** Stick with the original 11 (academically safest, matches proposal exactly)
- **(b)** Expand to 20–25 features including treatment history, lab trends, and additional comorbidities (richer but risks overfitting at n=150)
- **(c)** Use the 11 plus a small set of trajectory-derived features (PLT slope, steroid response, time-since-diagnosis) — a middle path

**Plan default**: Option (c). Justification: stays close to the proposal, adds the trajectory signals that the longitudinal data uniquely supports, manageable overfitting risk with proper cross-validation.

### Question 3 — Human-in-the-loop validation

Will Nhiên (or another hematologist) review Intake-Agent extraction quality during training data preparation?
- **(a)** Yes — review every extracted patient record before it enters the training set (highest quality, costs ~20 hours of Nhiên's time)
- **(b)** Yes, but only a sample — review 20% randomly, accept the rest (balanced)
- **(c)** No — accept whatever the agent extracts, with automated sanity checks only (cheapest, lower training data quality, lower XGBoost AUC)

**Plan default**: Option (b). Justification: catches systematic errors without consuming Nhiên's time linearly. Sample size is statistically defensible.

**These defaults can be changed; the rest of the plan assumes them. Sections affected by each are flagged.**

---

## 3. Why ML stays — final answer

The recommendation across the entire conversation has gone back and forth. v0.0.7 settles it. **ML stays, as a tool the agent calls.** The reasoning:

**The data shape favors ML for prediction.** Tabular features (even with trajectory derivatives) on n≈150 patients is gradient-boosted-trees home turf. ClinicalBench (2024) and EHRSHOT (Nov 2025) both confirm XGBoost still wins or ties LLMs on tabular clinical prediction in 2026.

**The thesis audience expects ML numbers.** A Vietnamese hematology master's thesis committee will evaluate on AUC, sensitivity, specificity. Even with a forward-thinking advisor, defending "we built agents instead of training models" against tradition is risk Nhiên doesn't need to take.

**The marginal cost is small.** SageMaker Serverless Inference for one XGBoost endpoint is $5–15/month. Training and feature engineering work is 2–3 weeks once the data preparation pipeline exists.

**The agent layer is genuinely better with ML in it.** The Risk-Reasoner agent's job becomes synthesis — taking the XGBoost probability, the cohort comparison, the literature priors, and the guideline retrieval, then explaining the result in Vietnamese trajectory terms. This is a stronger agentic design than agent-alone reasoning.

**The architectural pattern is now well-understood**. v0.0.4 made ML the prediction core with agents as an explanation wrapper. v0.0.7 inverts this: **agents are the system, ML is one of several tools the system uses**. This is the canonical "agents with tools" pattern, not a hybrid in the v0.0.4 sense.

What this is not: a return to v0.0.4. The architecture remains agent-first (Strands + AgentCore per v0.0.6), the operational model remains lightweight (one XGBoost endpoint, not a SageMaker model factory), and the thesis framing remains agent-centric.

---

## 4. Revised objectives

**Mục tiêu 1** (unchanged) — Mô tả đặc điểm lâm sàng, cận lâm sàng và thực trạng xuất huyết của bệnh nhân GTCMD người lớn tại BV TMHH giai đoạn 2022–2026.

**Mục tiêu 2 (revised)** — Xây dựng, đánh giá và so sánh:
- Hiệu suất dự đoán xuất huyết của mô hình học máy XGBoost huấn luyện trên cohort BV TMHH (AUC, độ nhạy, độ đặc hiệu) — đối chiếu với baseline An et al. 2023
- Khả năng phân loại nguy cơ và đưa ra giải thích lâm sàng của hệ thống đa tác tử trên AWS (kappa agreement với bác sĩ, n=50 ca; chất lượng giải thích đánh giá bởi Likert 5 điểm; độ trung thành với hướng dẫn ASH/ISTH thông qua manual audit của 30 phản hồi ngẫu nhiên)

**Mục tiêu 3** (unchanged) — Xây dựng ứng dụng web tiếng Việt cho bác sĩ tại BV TMHH.

The revised Mục tiêu 2 satisfies both audiences: the AUC component matches the medical thesis tradition, the agent evaluation component captures what's actually novel. Both can be reported in the same thesis.

---

## 5. Architecture

### 5.1 Overall design — layered, with longitudinal data at the core

The system has four logical layers:

1. **Data preparation layer** — Word documents in, structured longitudinal patient records out. Used at training time (to build the ML dataset) and at inference time (to process incoming patient cases).
2. **Storage layer** — Event store for patient trajectories (DynamoDB), feature store for ML inputs (DynamoDB), vector store for guidelines (Aurora pgvector or OpenSearch Serverless), audit logs (S3 + CloudWatch).
3. **Multi-agent reasoning layer** — Strands agents on AgentCore Runtime: Supervisor + Intake + Risk-Reasoner + Guidelines + Cohort-Lookup.
4. **Application layer** — React app for clinicians, JWT auth via Cognito.

This is v0.0.6's architecture with the addition of Layer 1 (data preparation) and the storage layer redesigned around longitudinal event data instead of flat features.

### 5.2 Data model — event store, not flat features

The DynamoDB schema models trajectories explicitly:

```
patients
  patient_id (PK)
  name (encrypted)
  birth_year
  sex
  bhyt_number (encrypted, used for cross-document linking)
  first_diagnosis_date
  current_classification (mới chẩn đoán / dai dẳng / mạn tính)

admission_episodes
  patient_id (PK), episode_start_date (SK)
  admission_reason
  diagnosis_in
  diagnosis_out
  discharge_status
  treatment_summary
  bleeding_events_during_episode

lab_measurements
  patient_id (PK), measurement_timestamp (SK)
  lab_panel (huyết đồ / sinh hóa / đông máu / miễn dịch / vi sinh)
  values (map of canonical_name -> {value, unit, ref_range})

treatment_events
  patient_id (PK), event_timestamp (SK)
  drug_name (canonical)
  dose
  route
  duration_days
  response_assessment

bleeding_events
  patient_id (PK), event_timestamp (SK)
  who_grade
  bleeding_site (skin / mucosa / gi / cns / other)
  source_episode_id
```

This is a write-once event store. Features for ML are *derived* from queries against it, not stored separately. Trajectory features (PLT slope over 30 days, time since diagnosis, etc.) are computed at the time a prediction is requested.

### 5.3 Multi-agent topology — same as v0.0.6 with one addition

Five Strands agents on AgentCore Runtime:

| Role | Backbone | Tools | Notes |
|------|----------|-------|-------|
| Supervisor | Claude Sonnet | (none — orchestrates via Agents-as-Tools) | Same as v0.0.6 |
| Intake-Agent | Claude Sonnet (Haiku for simple cases) | Document parser, Comprehend Medical, schema validator | **Promoted to Sonnet** — extraction quality is critical |
| Risk-Reasoner | Claude Sonnet | XGBoost endpoint (via MCP), Code Interpreter, trajectory feature computer | **ML tool added here** |
| Guidelines | Claude Haiku | Bedrock Knowledge Base (RAG) | Same as v0.0.6 |
| Cohort-Lookup | Claude Haiku | DynamoDB similarity query over feature vectors | Same as v0.0.6 |

The Intake-Agent moves from Haiku in v0.0.6 to Sonnet in v0.0.7. The reasoning: document understanding quality directly determines both training data quality and inference quality. Saving $50/month on Haiku is a false economy if it costs us 5% XGBoost AUC and 10% explanation accuracy.

### 5.4 The Intake-Agent — what it actually does

This agent is the foundation of the system. Concretely it must:

1. **Parse Word document structure** (sections, tables, prose paragraphs)
2. **Extract patient demographics** (handling encrypted fields appropriately)
3. **Extract all admission episodes** with timestamps, linking same-patient episodes across files
4. **Normalize lab data**: map heterogeneous labels (`Tiểu cầu` / `PLT` / `Số lượng tiểu cầu` → `platelet_count_canonical`), normalize units (`K/µL` ↔ `× 10⁹/L`), handle missing reference ranges
5. **Extract treatment events**: parse phrases like `Methylprednisolone liều chuẩn (N1: 6/11/2025)` into structured drug + dose + start-date
6. **Extract bleeding events** from prose: "chấm xuất huyết rải rác" → mucocutaneous bleeding, "Xuất huyết tiêu hóa trên mức độ nặng" → severe GI bleed
7. **Compute reference range flags**: PLT 14 K/µL with reference (151–304) → flagged as critically low
8. **Output a validated JSON record** matching the event-store schema

This is implemented as a Strands agent with:
- A canonical schema (JSON Schema document) defining what valid output looks like
- A retrieval tool over a small reference document (the BV TMHH discharge form template) for handling format variations
- Comprehend Medical as a secondary signal for entity extraction (handles English medical terms well, weaker on Vietnamese but useful)
- A validator that rejects malformed output and asks the agent to retry

This is not a one-prompt job. Phase 0 (§ 6.1) is dedicated to building and validating this agent.

### 5.5 ML model design

**Algorithm**: XGBoost. Justification: dominates tabular medical prediction at this n; same algorithm used by An et al., Shen et al., and Kasser et al. in the related ITP literature.

**Features** (assuming Question 2 default — original 11 + trajectory derivatives):
- Original 11 (from An et al.): infection, uncontrolled diabetes, age, ITP classification, CVD, low lymphocyte, skin/mucosa bleeding, initial PLT, low PLT (<20), disease duration
- Trajectory derivatives: PLT slope over 30 days, PLT minimum in last 60 days, treatment failure count, time since diagnosis, time since last bleeding event, current corticosteroid dose, NLR trend

**Target** (assuming Question 1 default): binary — WHO grade ≥2 bleeding within 30 days of the reference timestamp.

**Training**: SageMaker Training job on the validated extracted dataset. 5-fold stratified cross-validation, SMOTE for class imbalance, GridSearchCV for hyperparameters. SageMaker Clarify for SHAP analysis (satisfies the original proposal's commitment to SHAP).

**Serving**: SageMaker Serverless Inference endpoint. Scales to zero when idle. Exposed via MCP through AgentCore Gateway so the Risk-Reasoner agent can call it.

**Operations**: One model, retrained quarterly or when new validated training data accumulates. No drift monitoring in scope (deferred to post-thesis).

### 5.6 What the Risk-Reasoner does with the ML output

When a clinician submits a patient query, Risk-Reasoner:

1. Calls the trajectory feature computer (Lambda) to derive features from the event store
2. Calls the XGBoost endpoint to get a 30-day bleeding probability
3. Calls Cohort-Lookup for 5 most similar past patients and their outcomes
4. Calls Guidelines for relevant ASH/ISTH passages
5. **Synthesizes**: explains the XGBoost probability in trajectory terms, anchors it to the cohort comparison, cites the guidelines, flags clinically important contradictions (e.g., "XGBoost says low risk but patient just had GI bleed two weeks ago — clinical judgment supersedes")

This synthesis is the agent's contribution. The ML number alone is a 0–1 probability with no explanation; the agent's output is something a clinician can act on.

---

## 6. 11-month timeline (default) and 9-month variant

### 6.1 Phase 0 — Document Understanding (Months 1–2) — NEW IN V0.0.7

This phase did not exist in prior versions. It's now the most important phase.

| Week | Task | Deliverable |
|------|------|-------------|
| 1–2 | Catalog document variations across Nhiên's sample set; design canonical schema | Schema specification |
| 3–4 | AWS environment setup, DynamoDB event store schema, S3 buckets | Infrastructure for Phase 0 |
| 5–6 | Build Intake-Agent v1 (Strands on AgentCore); test on 10 patient documents | Working extractor |
| 7–8 | Validation harness: Nhiên reviews extractions on a 20% sample; iterate on prompts | Quality-validated v2 of agent |

**Decision gate at end of Phase 0**: extraction accuracy ≥ 85% on validated sample. If not met, extend Phase 0 by 2 weeks before proceeding.

### 6.2 Phase 1 — Bulk Data Preparation (Month 3)

| Week | Task | Deliverable |
|------|------|-------------|
| 9–10 | Run Intake-Agent over all ~150 historical patient documents | Raw extracted dataset |
| 11–12 | Nhiên reviews 20% sample; flag errors; agent retries on flagged cases | Validated training dataset |

**Output for thesis**: Mục tiêu 1 — clinical/lab characteristics description.

### 6.3 Phase 2 — ML Training and Evaluation (Month 4)

| Week | Task | Deliverable |
|------|------|-------------|
| 13–14 | Feature engineering (11 original + 7 trajectory features); SageMaker training pipeline | Trained XGBoost model |
| 15–16 | 5-fold CV evaluation, SHAP analysis, hyperparameter tuning | Model performance report |

**Output for thesis**: Mục tiêu 2 — AUC component.

### 6.4 Phase 3 — Agent System Development (Months 5–6) — was Phase 2 in v0.0.6

| Week | Task | Deliverable |
|------|------|-------------|
| 17–18 | Deploy XGBoost to SageMaker Serverless; expose via MCP; wire to Risk-Reasoner | ML-as-tool integration |
| 19–20 | Build Guidelines-Agent (Bedrock KB); build Cohort-Lookup-Agent | Agents 2 and 3 |
| 21–22 | Build Risk-Reasoner-Agent with Code Interpreter and trajectory features | Agent 4 (ML-aware) |
| 23–24 | Configure Supervisor; multi-agent collaboration; Vietnamese prompts; Guardrails | Full system online |

### 6.5 Phase 4 — Application (Month 7)

| Week | Task | Deliverable |
|------|------|-------------|
| 25–26 | React app: Vietnamese UI, JWT auth, SSE streaming, file upload for Word docs | Frontend |
| 27–28 | Clinical UX: risk panel showing both ML and agent reasoning, trajectory visualization, citation panel | Complete clinical UI |

**Output for thesis**: Mục tiêu 3.

### 6.6 Phase 5 — Clinical Evaluation (Months 8–9)

| Week | Task | Deliverable |
|------|------|-------------|
| 29–30 | Internal testing, edge cases, end-to-end accuracy from raw Word doc input | Hardened system |
| 31–32 | Recruit 3 hematologists at BV TMHH; pilot 10 cases | UAT plan and pilot results |
| 33–34 | 50-case prospective evaluation; system vs each clinician | Kappa agreement data |
| 35–36 | Satisfaction survey; manual audit of 30 random explanations | Qualitative data |

**Output for thesis**: Mục tiêu 2 — agent evaluation component.

### 6.7 Phase 6 — Analysis and Writing (Months 10–11)

| Week | Task | Deliverable |
|------|------|-------------|
| 37–40 | Statistical analysis (XGBoost AUC report, kappa, Likert summaries) | Results section |
| 41–44 | Thesis writing support, documentation, final deployment, defense preparation | Production system + thesis draft |

### 6.8 9-Month Variant — Reduced Scope

If 11 months is too long, the 9-month variant compresses by:

- **Reduce evaluation scope**: drop from 50 to 20 prospective cases (saves 2 weeks)
- **Defer trajectory features**: stick with original 11 variables only (saves 1 week in feature engineering, simpler training)
- **Compress Phase 0**: 6 weeks instead of 8 (accept higher extraction error rate, more manual correction)
- **Drop Cohort-Lookup-Agent**: 4-agent system instead of 5 (saves 1 week)

The 9-month variant is achievable but sacrifices either evaluation power (smaller n) or richness (fewer features). My recommendation: go with 11 months if Nhiên's program allows, fall back to 9 with reduced eval scope if not.

---

## 7. Cost analysis

### Option A — Full Pattern A (AgentCore + Strands) with ML

| Service | Monthly | Notes |
|---------|---------|-------|
| AgentCore Runtime (5 agents) | $80–150 | Same as v0.0.6 |
| Bedrock Sonnet (Supervisor, Intake, Risk-Reasoner) | $50–110 | Intake now on Sonnet too |
| Bedrock Haiku (Guidelines, Cohort) | $10–20 | |
| Bedrock Knowledge Bases | $20–30 | |
| AgentCore Memory + Gateway + Observability | $25–45 | |
| OpenSearch Serverless (2 collections) | $350–400 | Floor cost |
| **SageMaker Serverless Inference (XGBoost endpoint)** | **$5–15** | **NEW in v0.0.7** |
| **SageMaker Training (one-off + occasional retrains)** | **$5–10** | **NEW in v0.0.7** |
| **SageMaker Clarify (for SHAP)** | **$5–10** | **NEW in v0.0.7** |
| Comprehend Medical | $20–40 | |
| Aurora Serverless v2 (small, for ops) | $30–50 | |
| Lambda + API Gateway + Cognito + DynamoDB | $10–25 | DynamoDB usage higher with event store |
| CloudFront + S3 + WAF | $5–10 | |
| CloudWatch Logs | $15–25 | |
| KMS | $1.50 | |
| **Monthly total** | **$636–940** | |
| **11-month total** | **$7,000–10,340** | ≈ 178–264 triệu VNĐ |

**vs v0.0.6 Option A** ($540–745/month): adds ~$95 for the ML pieces, but the agent system also got more capable. The total is comparable.

### Option B — Pattern B (Bedrock Multi-Agent Collaboration) with ML

| Service | Monthly | Notes |
|---------|---------|-------|
| Bedrock Multi-Agent (Sonnet + Haiku mix) | $90–155 | |
| Bedrock Knowledge Base | $20–30 | |
| Aurora Serverless v2 with pgvector | $15–30 | Replaces OpenSearch |
| Bedrock Guardrails | $20–35 | |
| AgentCore Code Interpreter (tool only) | $20–40 | |
| **SageMaker Serverless Inference** | **$5–15** | |
| **SageMaker Training** | **$5–10** | One-off mostly |
| Comprehend Medical | $10–25 | |
| Lambda + API GW + Cognito + DynamoDB | $5–15 | |
| S3 + CloudFront | $3–8 | |
| CloudWatch (basic) | $10–20 | |
| **Monthly total** | **$203–383** | |
| **11-month total** | **$2,235–4,215** | ≈ 57–108 triệu VNĐ |

**vs v0.0.6 Option B** ($173–318/month): adds ~$30/month for ML pieces.

### Recommendation

Same staged approach as v0.0.6:
- **Phase 0 + Phase 1 + Phase 2** (Months 1–4): Pattern B for fast iteration. ML training in SageMaker (which works the same regardless of agent pattern).
- **Phase 3 onwards** (Months 5+): migrate to Pattern A if quality and budget allow; stay on Pattern B otherwise.

Staged estimated total: **$3,000–5,500 over 11 months** (~77–141 triệu VNĐ). Still well within AWS Activate research credit range.

---

## 8. Risk register — major changes from v0.0.6

Risks unchanged from v0.0.6:
- Vietnamese clinical terminology gaps (now partially addressed by Intake-Agent being Sonnet)
- Prompt injection
- Hallucinated cohort statistics
- AgentCore region availability

New or elevated risks in v0.0.7:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Intake-Agent extraction accuracy below 85% | Medium | Very high — blocks ML training | Phase 0 decision gate; budget for extension; if irrecoverable, fall back to manual extraction for training data |
| Same-patient linking across documents fails | Medium | High | Use BHYT number + name + DOB as composite key; flag duplicates for Nhiên review |
| Trajectory feature engineering overfits at n=150 | Medium | Medium | Regularization, careful CV, feature selection; Question 2 default mitigates this |
| Nhiên's validation time consumed by data prep | High | Medium | Question 3 default (20% sample) is calibrated to this; revise if Nhiên has more time |
| Word documents from different years use different formats | High | Medium | Catalog variations in Phase 0 week 1–2; build adaptive parsing; not all variants will be supported |
| Encrypted PHI fields complicate dev/test workflow | Medium | Medium | De-identified copies for development; production env separate |
| 11-month timeline conflicts with thesis defense schedule | Unknown | High | Confirm Nhiên's program calendar; 9-month variant available as fallback |

Risks reduced from v0.0.6:
- "LLM accuracy on tabular prediction" — ML is back, so this risk is mitigated by design

---

## 9. What this v0.0.7 plan does NOT include

- **Production deployment to BV TMHH** — Phase 5 uses staging with de-identified data
- **Treatment selection reasoning** (Eltrombopag vs Rituximab from the slide deck) — deferred to post-thesis; would require additional agents and additional evaluation
- **Imaging integration** — CT, X-ray, ultrasound fields in the documents are mentioned but not analyzed
- **Mobile app** — web-only
- **Multi-language support** — Vietnamese only
- **Continuous model retraining** — quarterly manual retraining only
- **Real-time alerts** — system is query-driven, not push

---

## 10. Decision summary

To move forward, Nhiên needs to answer the three questions in § 2, and Huy needs to confirm:

1. **(Nhiên + advisor)** Prediction window, feature scope, validation approach (the three questions)
2. **(Huy)** 11-month vs 9-month timeline
3. **(Huy)** Pattern A target vs staying on Pattern B
4. **(Both)** Acceptance of v0.0.7 architecture before any build work starts

Once these are confirmed, the next concrete deliverable is **Phase 0 week 1–2 work**: catalog document variations across Nhiên's sample set, design the canonical schema, set up the dev AWS account. About 1 week of effort to produce a clear schema specification and an initial dev environment.

---

*v0.0.7 represents the architecture this project should actually have. The lesson across versions: technical decisions follow data realities. Prior versions iterated on agent topologies and ML choices without anchoring to what the input data actually looks like. Once we saw the BV TMHH discharge summary format and learned the prediction target is trajectory-based, the answers fell into place: data preparation is a substantial subsystem, prediction is trajectory-aware, ML returns as a tool (not a core), and the multi-agent design from v0.0.6 stands but with Phase 0 added on the front. This is the version to build.*
