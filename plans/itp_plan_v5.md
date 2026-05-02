# ITP Bleeding Prediction Research Plan — v0.0.5

## Pure Multi-Agent Architecture on AWS

**Project**: Bước đầu đánh giá hiệu quả dự đoán chảy máu của các mô hình học máy ở bệnh nhân người lớn giảm tiểu cầu miễn dịch tại Bệnh viện Truyền máu Huyết học giai đoạn 2022–2026

**Researcher**: Trần Xuân Nhiên (Master's Thesis, 2025–2027)

**Technical Support**: Huy (Software Engineer, AWS DevOps focus)

**Version**: 0.0.5

**Status**: Major architectural shift from v0.0.4 — abandons the hybrid ML+Agent design in favour of a pure multi-agent system.

**Changelog**:
- v0.0.1–0.0.4: Hybrid approach (classical ML core + Agentic AI wrapper)
- **v0.0.5**: Pivot to pure multi-agent orchestration on AWS Bedrock

---

## 1. Why the architectural shift?

The hybrid plan in v0.0.4 used SageMaker-trained ML models (RF, XGBoost, LightGBM, LR) as the prediction core, wrapped by an Agentic AI explanation layer. v0.0.5 removes the ML core entirely and lets a team of specialist agents handle reasoning, prediction, and explanation collaboratively.

**Drivers of the shift:**
- Huy's stack focus is AWS DevOps / cloud — managing SageMaker training pipelines, hyperparameter tuning, and ongoing MLOps is a heavier lift than orchestrating Bedrock agents.
- AWS Bedrock multi-agent collaboration reached general availability in March 2025 with mature CDK/CloudFormation support — the timing is right.
- The Agentic Graph RAG and Dhiman et al. (2026) research lines are now mature reference architectures we can directly model on.
- A pure agent system is more novel for a medical thesis than a replication of An et al.'s ML methodology.

---

## 2. Critical caveat — must be read before proceeding

**LLM agents reasoning over tabular clinical data perform substantially worse than classical ML models on prediction accuracy.** Recent benchmarks make this unambiguous:

- **Liu et al. (2025), Scientific Reports** — On COVID-19 mortality prediction with high-dimensional tabular data (n=9,134), XGBoost reached F1 = 0.87, while GPT-4 zero-shot reached only F1 = 0.43. Fine-tuning Mistral-7b with QLoRA improved it to F1 = 0.74, still below XGBoost.
- **ClinicalBench (Chen et al., 2024)** — Across multiple clinical prediction tasks, no LLM (general-purpose or medical-specialised) matched XGBoost/SVM/RNN. Prompting strategies (CoT, self-reflection, role-playing, in-context learning) gave only marginal lift.
- **TabLLM (Hegselmann et al., 2023)** — LLMs are competitive with XGBoost only in **few-shot regimes (≤16 examples)**; with full datasets, gradient-boosted trees still win.

**What this means for Nhiên's thesis:**
The medical thesis is judged by hematology faculty whose primary evaluation criterion will be predictive performance (AUC, sensitivity, specificity) compared to the An et al. (2023) baseline. A pure multi-agent system **will not match the AUC numbers** that a trained XGBoost model would produce on the same Vietnamese cohort. Aiming the thesis purely at AUC competition is a losing position.

**Two ways forward, both honest:**

### Option 1 — Reframe the thesis contribution (recommended)

Position the work as **building and evaluating a clinical decision support agent system**, not as **a prediction accuracy benchmark**. The contribution becomes:
- A novel multi-agent clinical reasoning system in Vietnamese, the first of its kind for hematology in Vietnam
- Empirical evaluation of agent-generated risk assessment vs. clinician judgment (inter-rater agreement, time-to-decision, perceived utility)
- Qualitative evaluation of explanation quality, guideline adherence, and clinical safety
- The "AUC vs. An et al." comparison is **acknowledged as a limitation**, with future work pointing to agent + ML hybrid

This requires Nhiên to update Mục tiêu 2 in her proposal — moving from "AUC comparison of 4 ML models" to "evaluation of agent-based risk assessment vs. clinician judgment". The thesis committee needs to approve this pivot before serious work starts.

### Option 2 — Keep a small ML model as a tool the agent calls (compromise)

Keep the agent architecture but train a single XGBoost model and expose it as a Lambda-backed action group that the Risk Reasoner agent can call. This isn't the v0.0.4 hybrid (ML as the core); it's a multi-agent system that happens to have ML as one of several tools. The thesis can still report AUC for the XGBoost tool. About 60% of the v0.0.4 SageMaker work is still needed.

### My recommendation

**Discuss with Nhiên and her advisor before committing.** If they agree to reframe the thesis (Option 1), v5 stands as written. If they don't, fall back to Option 2, which is closer to a stripped-down v0.0.4. The rest of this document assumes Option 1; a § 12 addendum sketches the Option 2 deltas.

---

## 3. Research objectives (revised for Option 1)

**Mục tiêu 1** (unchanged) — Mô tả đặc điểm lâm sàng, cận lâm sàng và thực trạng xuất huyết của bệnh nhân GTCMD người lớn tại BV TMHH giai đoạn 2022–2026.

**Mục tiêu 2 (REVISED)** — Xây dựng và đánh giá hệ thống đa tác tử (multi-agent) trên AWS để hỗ trợ ra quyết định lâm sàng về nguy cơ xuất huyết, bao gồm:
- Đánh giá độ phù hợp giữa khuyến nghị của hệ thống và phán đoán bác sĩ (kappa agreement, n=50 ca tiền cứu)
- Đánh giá chất lượng giải thích (clinician satisfaction survey, 5-point Likert)
- Đánh giá độ trung thành với hướng dẫn ASH/ISTH (manual audit của 30 phản hồi ngẫu nhiên)

**Mục tiêu 3** (unchanged) — Xây dựng ứng dụng web tiếng Việt cho bác sĩ tại BV TMHH.

---

## 4. Multi-agent architecture

### 4.1 Topology — supervisor with five specialists

The system uses Amazon Bedrock multi-agent collaboration in **Supervisor with Routing Mode**: simple queries route directly to one specialist, complex ones escalate to full supervisor orchestration.

| Role | Agent name | Backbone | Primary tool |
|------|------------|----------|--------------|
| Supervisor | `IDA-Supervisor` | Claude Sonnet | (no tools — routes & consolidates) |
| Specialist 1 | `Intake-Agent` | Claude Haiku | AWS Comprehend Medical (clinical NER) |
| Specialist 2 | `Risk-Reasoner-Agent` | Claude Sonnet | AgentCore Code Interpreter |
| Specialist 3 | `Guidelines-Agent` | Claude Haiku | Bedrock Knowledge Base (RAG over Aurora pgvector) |
| Specialist 4 | `Cohort-Lookup-Agent` | Claude Haiku | Lambda → DynamoDB query |
| Specialist 5 | `Explanation-Agent` | Claude Sonnet | (no tools — synthesises Vietnamese reply) |

Why these five specialists:
- **Intake** parses unstructured clinical notes and extracts the 11 variables Nhiên defined — separating this from reasoning keeps the input pipeline testable on its own.
- **Risk-Reasoner** uses the AgentCore Code Interpreter to compute risk via **published priors** from An et al. (2023) and Shen et al. (2025). It does not invent a model; it applies literature-derived scoring with code, then reasons about deviations. This is the agent equivalent of "look up which features matter and weight them like the published RF model".
- **Guidelines** retrieves relevant ASH 2019, ISTH 2021, and BV TMHH protocol passages — keeping retrieval separate from reasoning prevents the Risk-Reasoner from hallucinating citations.
- **Cohort-Lookup** finds the 5 most similar past patients from the BV TMHH cohort (by cosine similarity over the 11-feature vector). The Risk-Reasoner uses these as anchors.
- **Explanation** consolidates everything into a Vietnamese clinical reply with citations, structured for clinician readability.

### 4.2 Agent interaction pattern (typical query)

1. Clinician submits a patient case in Vietnamese (free-form text or structured form).
2. **Supervisor (IDA)** receives the request. If it's a straightforward "what's the bleeding risk for this patient" query in routing mode, it goes straight to Risk-Reasoner. If complex (multiple sub-questions, ambiguous input), full supervisor orchestration kicks in.
3. **Intake-Agent** runs first if input is unstructured — extracts the 11 variables via Comprehend Medical + LLM normalization.
4. **Cohort-Lookup-Agent** and **Guidelines-Agent** run in parallel, returning similar past patients and relevant guideline passages.
5. **Risk-Reasoner-Agent** runs the Code Interpreter to compute a literature-anchored risk score, factoring in cohort comparison and guideline thresholds.
6. **Explanation-Agent** receives all sub-agent outputs and produces the Vietnamese clinical reply.
7. **Supervisor** validates the consolidated reply against Bedrock Guardrails (PHI, topic, hallucination filters) and streams it back.

### 4.3 What replaces the SageMaker ML core

The Risk-Reasoner-Agent does **not** train a model. It does the following at inference time:

```python
# Pseudocode the agent would write and execute via AgentCore Code Interpreter
# Coefficients sourced from An et al. (2023) Random Forest feature importance
# (these are literature priors, not local-data fits)

PRIORS = {
    "infection": 0.18,
    "uncontrolled_diabetes": 0.12,
    "age_over_65": 0.09,
    "itp_chronic": 0.08,
    "cvd": 0.10,
    "low_lymphocyte": 0.07,
    "skin_mucosa_bleed": 0.14,
    "low_plt_under_20": 0.16,
    "duration_long": 0.06,
}

def literature_risk(features):
    score = sum(PRIORS[k] for k, v in features.items() if v)
    return min(score, 1.0)
```

The agent then **augments this with cohort similarity** ("of the 5 most similar past patients at BV TMHH, 4 had Grade ≥2 bleeding within 30 days") and **explains the reasoning** with reference to specific ASH/ISTH passages.

This is **honest about its limitations** — the score is not a learned model on the BV TMHH cohort, it's literature priors anchored to local cohort comparison. Nhiên's thesis must state this clearly. The evaluation in Mục tiêu 2 is about agreement with clinicians, not AUC against ground truth.

### 4.4 Bedrock multi-agent specifics

- **Collaboration mode**: Supervisor with Routing Mode (the lightweight router escalates complex queries to full supervisor orchestration).
- **Inline agent support** (GA March 2025) — supervisor can be created at runtime, useful for A/B testing different supervisor prompts.
- **CloudFormation / CDK deployment** — entire agent network as code, reproducible across dev/staging/prod.
- **Conversation history sharing** — supervisor passes session context to specialists when needed (turned off by default to reduce token costs).
- **Payload referencing** — large patient records stay in DynamoDB; agents pass references rather than embedding the full data each turn. Cuts costs ~30% on multi-turn sessions.

### 4.5 Security considerations specific to multi-agent

The Palo Alto Unit 42 research (Sept 2025) identified prompt injection as the primary risk vector for Bedrock multi-agent applications — adversarial inputs could disclose collaborator schemas or trigger unauthorized tool calls. AWS confirmed Bedrock's built-in prompt-attack Guardrail blocks all known attacks. We will:
- Enable Bedrock Guardrails on every agent (not just the supervisor)
- Use parameterised tool inputs (no free-text passthrough to Lambda functions that hit DynamoDB or pgvector)
- Log every agent-to-agent message to CloudWatch for audit

---

## 5. Technical stack

### Compute and AI
- **Amazon Bedrock Agents** (multi-agent collaboration, March 2025 GA)
- **Amazon Bedrock Knowledge Bases** (RAG over Aurora pgvector)
- **Amazon Bedrock Guardrails** (PHI + topic filtering, prompt-attack defence)
- **Amazon Bedrock AgentCore Code Interpreter** (sandboxed Python for risk scoring)
- **Foundation models**: Claude Haiku for cheap specialists, Claude Sonnet for Supervisor, Risk-Reasoner, and Explanation
- **AWS Lambda** for action group functions (DynamoDB queries, Comprehend Medical wrappers)

### Data layer
- **Amazon S3** for raw EHR exports + audit logs
- **Amazon DynamoDB** for patient feature store and cohort similarity index
- **Amazon Aurora Serverless v2 with pgvector** for guideline embeddings
- **AWS Glue** for the one-off ETL of historical hospital data
- **AWS Comprehend Medical** for clinical NER (extracts conditions, medications, anatomy from Vietnamese-translated notes)

### Application
- **Amazon API Gateway + Cognito** for auth
- **AWS Amplify / S3 + CloudFront** for the React app
- **Amazon CloudWatch** for tracing, logging, cost alarms

### What's removed compared to v0.0.4
- ❌ SageMaker Studio
- ❌ SageMaker Training Jobs
- ❌ SageMaker Endpoints (real-time or serverless inference)
- ❌ SageMaker Clarify
- ❌ SageMaker Feature Store
- ❌ SageMaker Model Monitor

This drops 6 SageMaker services from the stack. The total AWS service count goes from 20 → 14 services. Operationally simpler, with no model training/retraining/drift monitoring overhead.

---

## 6. Feasibility assessment

### Technically feasible
- Bedrock multi-agent collaboration is GA, mature, with CDK support and a public AWS workshop (`aws-samples/bedrock-multi-agents-collaboration-workshop`) that we can pattern-match.
- AgentCore Code Interpreter is GA (August 2025), supports Python with 15-minute default execution, S3 file integration, and full CloudTrail logging — exactly what the Risk-Reasoner needs.
- Comprehend Medical supports Vietnamese clinical text (after translation; native Vietnamese is on AWS roadmap but not yet GA).
- Aurora pgvector replaces OpenSearch Serverless's $350/month minimum, scaling to ~$15–30/month at this workload.

### Clinically risky areas
- **Prediction quality** — see § 2. The system's risk score is literature-anchored, not locally-fit. Honest framing required.
- **Hallucination** — the Risk-Reasoner could fabricate cohort statistics if not properly grounded. Mitigation: every cohort claim must come from the Cohort-Lookup-Agent's structured output, not the LLM's own generation.
- **Vietnamese medical language** — Claude handles Vietnamese well at the conversational level, but specific clinical terminology may need few-shot examples. Plan: ~20 hand-curated Vietnamese medical Q&A pairs as in-context examples for the Explanation-Agent.

### Resource feasible
- One software engineer (Huy) can build this in 9 months. The hybrid v0.0.4 plan would have required ML expertise (model training, evaluation, hyperparameter tuning) that Huy doesn't claim. v5 plays to a DevOps/cloud strength.
- No GPU instances required. No SageMaker model training. The build is mostly: write agent prompts, configure CDK, wire up Lambda functions, build the React app.

---

## 7. Revised 9-month timeline

### Phase 1: Foundation and data engineering (Months 1–2) — minor changes from v0.0.4

| Week | Task | Deliverable |
|------|------|-------------|
| 1–2 | AWS account setup, IAM, VPC, HIPAA compliance review | Secure cloud env |
| 3–4 | S3 buckets, Glue ETL for hospital data | Data ingestion pipeline |
| 5–6 | Data cleaning, EDA, **build cohort similarity index in DynamoDB** | Clean dataset + EDA report |
| 7–8 | **Embed ASH/ISTH/BV TMHH guidelines into Aurora pgvector** | RAG knowledge base |

**Output for thesis**: Mục tiêu 1 — clinical/lab characteristics description.

### Phase 2: Multi-agent system development (Months 3–5) — new

| Week | Task | Deliverable |
|------|------|-------------|
| 9–10 | Build Intake-Agent (Lambda + Comprehend Medical) | Agent 1 working |
| 11–12 | Build Guidelines-Agent (Bedrock KB) and Cohort-Lookup-Agent (Lambda + DynamoDB) | Agents 2 & 3 working |
| 13–14 | Build Risk-Reasoner-Agent with AgentCore Code Interpreter — **most complex piece** | Agent 4 working |
| 15–16 | Build Explanation-Agent with Vietnamese few-shot examples | Agent 5 working |
| 17–18 | Configure Supervisor (IDA) and multi-agent collaboration | Full system online |
| 19–20 | Bedrock Guardrails on every agent; CloudWatch tracing; CDK deployment | Production-ready infra |

### Phase 3: Application development (Month 6)

| Week | Task | Deliverable |
|------|------|-------------|
| 21–22 | React web app with Vietnamese UI; API Gateway + Cognito | Frontend |
| 23–24 | Risk gauge, citation panel, conversation history view | Complete clinical UI |

**Output for thesis**: Mục tiêu 3 — online clinical tool.

### Phase 4: Clinical evaluation (Months 7–8) — replaces ML-comparison phase

| Week | Task | Deliverable |
|------|------|-------------|
| 25–26 | Internal testing, agent prompt tuning, edge case handling | Hardened system |
| 27–28 | **Inter-rater study setup** — recruit 3 hematologists at BV TMHH; pilot 10 cases | UAT plan + pilot results |
| 29–30 | **50-case prospective evaluation** — system vs. each of 3 clinicians | Kappa agreement data |
| 31–32 | **Clinician satisfaction survey** + manual audit of 30 random explanations | Qualitative data |

**Output for thesis**: Mục tiêu 2 — agent vs. clinician evaluation results.

### Phase 5: Analysis and writing (Month 9)

| Week | Task | Deliverable |
|------|------|-------------|
| 33–34 | Statistical analysis (kappa, Likert summaries, audit findings) | Results section |
| 35–36 | Thesis writing support, final deployment, documentation | Production system + thesis draft |

---

## 8. Cost analysis — two options

### Option A: Full potential (Sonnet on every agent, OpenSearch Serverless)

| Service | Monthly | Notes |
|---------|---------|-------|
| Bedrock Sonnet (5 agents × heavy use) | $250–400 | ~3K input + 800 output per agent invocation, 200 invocations/day in eval phase |
| Bedrock Agents orchestration overhead | $40–80 | Multi-agent token overhead 3–5× single-agent |
| Bedrock Knowledge Base | $15–25 | Embedding + retrieval |
| Bedrock Guardrails | $20–40 | Per-request filtering across 5 agents |
| AgentCore Code Interpreter | $40–80 | 200 sessions/day × ~30s each |
| OpenSearch Serverless | $350–400 | 0.5 OCU minimum floor |
| Comprehend Medical | $20–40 | $0.01 per 100 chars |
| Aurora Serverless v2 (small) | $30–50 | Backup for OpenSearch metadata |
| Lambda + API Gateway + Cognito + DynamoDB | $15–30 | Mostly free tier |
| CloudFront + S3 hosting | $5–10 | Low traffic |
| CloudWatch | $20–40 | Detailed agent traces |
| **Total / month** | **$805–1,195** | |
| **9-month total** | **$7,250–10,750** | ≈ 185–275 triệu VNĐ |

### Option B: Cost-optimized (Haiku where possible, Aurora pgvector)

| Service | Monthly | Notes |
|---------|---------|-------|
| Bedrock Haiku (3 specialist agents) | $15–25 | Intake, Guidelines, Cohort-Lookup |
| Bedrock Sonnet (Supervisor + Risk-Reasoner + Explanation) | $60–120 | Reasoning-heavy roles |
| Bedrock Agents orchestration | $20–40 | Reduced via prompt caching + payload referencing |
| Bedrock Knowledge Base + Guardrails | $20–35 | Combined |
| AgentCore Code Interpreter | $20–40 | Moderate use |
| Aurora Serverless v2 (pgvector) | $15–30 | Replaces OpenSearch — **saves ~$335/month** |
| Comprehend Medical | $10–20 | Reduced via caching extracted features |
| Lambda + API GW + Cognito + DynamoDB | $5–15 | Free tier covers most |
| S3 + CloudFront | $3–8 | Static hosting |
| CloudWatch (essential metrics) | $10–20 | 7-day log retention |
| **Total / month** | **$178–353** | |
| **9-month total** | **$1,600–3,180** | ≈ 41–81 triệu VNĐ |

### Comparison

| Metric | Option A | Option B |
|--------|----------|----------|
| Monthly cost | $805–1,195 | $178–353 |
| 9-month total | $7,250–10,750 | $1,600–3,180 |
| AWS services used | 14 | 14 |
| LLM quality | Sonnet everywhere | Haiku + Sonnet split |
| Vector store | OpenSearch Serverless | Aurora pgvector |
| Best for | Publication-grade demo | Thesis-grade demo |

**vs v0.0.4 hybrid**: Both options are notably more expensive than the v0.0.4 cost-optimized hybrid (~$65–155/month). Reason: v5 invokes 3–6 LLM calls per user query (one per agent), vs. v0.0.4's single ML inference + 1–2 LLM calls. Multi-agent is **fundamentally more LLM-intensive**.

### Recommendation

**Run Option B during Months 3–8** (development and clinical evaluation). The Sonnet/Haiku split keeps costs reasonable while preserving quality where it matters. **Apply for AWS Activate research credits ($5,000–100,000 range)** before starting — this project is a strong candidate.

---

## 9. Reference implementations

These are the AWS resources to pattern-match against during implementation:

1. **AWS multi-agent workshop** — `github.com/aws-samples/bedrock-multi-agents-collaboration-workshop`. Energy-efficiency management system with 1 supervisor + 3 collaborators. Almost identical topology to ours.
2. **AWS multi-agent GA announcement (March 2025)** — covers CDK deployment, payload referencing, inline agents.
3. **AgentCore Code Interpreter sample** — `github.com/awslabs/amazon-bedrock-agentcore-samples`. Question-answering agent that validates with code.
4. **AWS healthcare reference architecture** — `aws.amazon.com/solutions/guidance/multi-modal-data-analysis-with-health-and-machine-learning-services-on-aws`. Data pipeline pattern (S3 → Glue → Feature store → consumption).
5. **ALMA (CatSalut, Spain, 2025)** — AWS Public Sector blog. Bedrock multi-agent assistant for clinicians with RAG over guidelines. 98% accuracy, 98% satisfaction. Closest to our use case.
6. **NoHarm (Brazil, 2025)** — 200+ hospital deployment of LLM-based clinical decision support. Demonstrates feasibility in developing-country healthcare.

---

## 10. Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Thesis committee rejects Option 1 reframing | Medium | High — forces fallback to Option 2 | Discuss with advisor in Month 1 before serious build |
| Risk-Reasoner gives lower predictive accuracy than An et al. baseline | High (per § 2) | Medium — addressed by reframing | Frame as "agent agreement with clinicians" not "AUC" |
| Multi-agent token cost balloons | Medium | Medium | Aggressive prompt caching, Haiku for cheap specialists, payload referencing |
| Vietnamese clinical terminology gaps in LLM | Medium | Medium | 20+ hand-curated few-shot examples; manual QA pass on 50 outputs |
| Prompt injection attack via clinical note paste | Low | High | Bedrock Guardrails on every agent + parameterised tool inputs |
| Comprehend Medical doesn't natively handle Vietnamese | High | Low | Translate notes to English in Intake-Agent, then NER, then translate back |
| AgentCore Code Interpreter execution timeout (15min default) | Low | Low | Risk-Reasoner code is <1s; configure 5min cap as safety |
| Hallucinated cohort statistics | Medium | High | Cohort-Lookup-Agent returns structured data only; Risk-Reasoner forbidden from inventing numbers |

---

## 11. What this v5 plan does NOT include (deliberately)

- **No SageMaker work** — no model training, no endpoints, no Clarify, no Feature Store. If Option 2 (compromise) is chosen, this comes back.
- **No QuickSight dashboards** — population-level analytics deferred to future work.
- **No model retraining pipeline** — there's no model to retrain.
- **No A/B testing of ML models** — there's only one risk-scoring strategy (literature priors + cohort similarity).
- **No SHAP analysis** — agent reasoning is the explanation; SHAP doesn't apply to LLM outputs.

---

## 12. Addendum — Option 2 (compromise) deltas

If the thesis committee insists on AUC comparison with An et al., add the following to v5:

- **Re-add SageMaker Training** (~$10–20/month) and one **SageMaker Serverless Inference endpoint** (~$5–15/month) for a single XGBoost model.
- **Expose the XGBoost endpoint as a Lambda action group** that the Risk-Reasoner agent can call ("if you want a learned-model second opinion, call `learned_xgb_predict(features)`").
- **Mục tiêu 2 keeps the AUC component** but only for the XGBoost tool, not the agent system as a whole.
- **Total monthly cost increases by ~$15–35** in Option B, ~$60–120 in Option A.
- **Timeline impact**: +2 weeks in Phase 2 for SageMaker training and endpoint deployment.

This is the smallest possible concession that satisfies a traditional medical thesis committee while keeping the multi-agent design intact.

---

*v0.0.5 represents a deliberate architectural shift away from the hybrid ML+Agent design of v0.0.1–0.0.4. The pivot is honest about its trade-offs: lower predictive accuracy on tabular data in exchange for novelty, simpler operations, and a system that plays to Huy's AWS DevOps strengths. The success of this plan depends on Nhiên and her advisor agreeing to reframe the thesis contribution from "AUC competition" to "clinical decision support evaluation".*
