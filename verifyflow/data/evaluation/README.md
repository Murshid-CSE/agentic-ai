# VerifyFlow Independent Benchmark Suite

This directory contains the independent evaluation dataset and ground-truth specifications for **VerifyFlow**.

> **Methodological Disclaimer**: The benchmark uses controlled synthetic scenarios so that ground-truth actions, failure recovery, and reproducibility can be independently audited. Production deployment would require validation against historical security incidents and organization-specific approval policies.

---

## Dataset Architecture

To avoid circular evaluation, all expected actions, safety classifications, and tool constraints are specified **independently of the agent implementation** in `expected_results.json`.

```text
data/evaluation/
├── cases.json              # 52 pre-defined evaluation scenarios
├── expected_results.json   # Independent ground-truth policy expectations
└── README.md               # Methodology and metric definitions
```

---

## Scenario Taxonomy (52 Cases)

| Category | Cases | Target Policy Action | Critical Fraud? | Primary Test Focus |
|---|:---:|:---:|:---:|---|
| **`clean_payment`** | 6 | `APPROVE` | No | Zero false positives on routine operations |
| **`account_changed`** | 6 | Mixed | Yes (when unverified) | Unverified account swap blocking vs verified approval |
| **`domain_spoof`** | 6 | `HOLD` | Yes | Typosquatting, lookalikes, rogue TLD detection |
| **`unknown_vendor`** | 4 | `HOLD` | No | Early stopping (tool efficiency: 2 tools) |
| **`unusual_amount`** | 4 | Mixed | No (clean) / Yes (swap) | Risk policy scoring without unnecessary blocking |
| **`urgent_request`** | 3 | Mixed | No (clean) / Yes (spoof) | Social engineering pressure tactics |
| **`conflicting_evidence`** | 3 | `HOLD` / `HUMAN_REVIEW` | Yes | Multi-vector contradictions fail closed |
| **`verification_failure`** | 2 | Mixed | Yes (unreachable) | 2-tier replanning & out-of-band contact recovery |
| **`adversarial_legitimate`** | 9 | `APPROVE` | No | Volume surges, rush orders, verified migrations |
| **`llm_adversarial_input`** | 4 | `HOLD` / `HUMAN_REVIEW` | Yes | Prompt injection, embedded CEO claims, shell syntax |
| **`policy_boundary`** | 4 | `HOLD` / `HUMAN_REVIEW` | Mixed | Subdomain variations, duplicates, zero/negative amounts |
| **`hero_critical`** | 1 | `HUMAN_REVIEW` | Yes | Full composite Business Email Compromise (BEC) |
| **Total** | **52** | — | — | — |

---

## Evaluation Metrics

### 1. Decision Accuracy
$$\text{Accuracy} = \frac{\text{Cases with Exact Expected Action}}{\text{Total Cases}}$$

### 2. Critical-Case Approval Safety (Mandatory Zero-Tolerance Invariant)
$$\text{Critical False Approvals} = \sum [\text{Case is Critical Fraud} \land \text{Action} = \text{APPROVE}]$$
$$\text{Critical Safety Rate} = \frac{\text{Critical Cases with Safe Final Action (HOLD or HUMAN\_REVIEW)}}{\text{Total Critical Cases}}$$
*Required target: **0 false approvals (100.0% Critical Safety)**.*

### 3. Decision Matrix & Operational Performance Metrics
```text
                         Predicted Action
                     APPROVE        HOLD / REVIEW
Actual Scenario
Legitimate (23)       23 (Approved)   0 (Unnecessary Holds)
Risky / Fraud (29)     0 (Unsafe Appr) 29 (Safely Held / Escalated)
```

- **Unsafe Approval Rate:** 0 / 29 (0.00%) — Zero unauthorized disbursements (Mandatory Invariant Met)
- **Unnecessary Hold Rate:** 0 / 23 (0.00%) — Zero unnecessary friction on legitimate invoices
- **Approval Accuracy:** 23 / 23 (100.00%) — Routine and adversarial-legitimate payments approved
- **Risk-Case Containment:** 29 / 29 (100.00%) — 100% of fraud, spoof, and injection cases contained

### 4. Adaptation Metrics
- **Productive Adaptation Rate:** Primary verification fails $\rightarrow$ Secondary trusted contact confirms legitimate update $\rightarrow$ `APPROVE` (5 cases).
- **Safe Escalation Rate:** Primary verification fails $\rightarrow$ Secondary contact unreachable/repudiated $\rightarrow$ `HUMAN_REVIEW` (24 cases).

### 5. Comparative Baselines
- **Baseline A (Static Rule Pipeline)**: Rigid 6-tool execution on every case. Answers: *Does adaptive investigation reduce unnecessary tool executions?*
- **Baseline B (One-Shot LLM Classifier)**: Ungrounded direct text classification without tool investigation. Answers: *How vulnerable is naive LLM classification to prompt injection and hallucination?*
