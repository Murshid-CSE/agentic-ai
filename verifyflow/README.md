# VerifyFlow — Pre-Action Payment Risk Verification Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Pytest](https://img.shields.io/badge/pytest-89%2F89%20passed-success.svg)](https://docs.pytest.org/)
[![Safety Invariant](https://img.shields.io/badge/Unsafe%20Approvals-0%2F29%20%5BPASS%5D-brightgreen.svg)]()
[![Benchmark Accuracy](https://img.shields.io/badge/Benchmark%20Accuracy-100%25%20(52%20cases)-blue.svg)]()

> ### The 30-Second Summary
> **VerifyFlow is a pre-action verification agent, not a phishing classifier.**  
> Rather than guessing whether an inbound email looks malicious, VerifyFlow is a **bounded decision-making agent that determines what must be independently verified across authoritative ledgers before an irreversible payment action can proceed.**

---

## The Comparative Proof (Why VerifyFlow Wins)

Evaluated on an independent, non-circular benchmark of **52 controlled scenarios**:

| System Architecture | Decision Accuracy (52 cases) | Unsafe Approvals (Max 29) | Avg Tools / Case | Dynamic Pruning? | Prompt Injection Defense |
|---|:---:|:---:|:---:|:---:|:---:|
| **Static 6-Tool Rule Pipeline** | 100.0% | 0 | 6.00 (Fixed) | None (Brute force) | Protected |
| **One-Shot LLM Classifier** | 88.5% | **6 [CRITICAL FAIL]** | 0.00 | N/A | **Vulnerable (Overrides decision)** |
| **VerifyFlow (Adaptive OODA Agent)** | **100.0%** | **0 [ZERO TOLERANCE]** | **4.29 (-28.5%)** | **Yes (2 to 6 tools)** | **Protected (Architectural Boundary)** |

---

## System Architecture

```text
                     INBOUND UNTRUSTED INVOICE
                                 │
                                 ▼
                 ARCHITECTURAL TRUST BOUNDARY
                 • <untrusted_document> Tag Isolation
                 • Passive Entity Extraction Only
                 • Strict Pydantic Schema Validation (amount > 0)
                                 │
                                 ▼
                 AUTONOMOUS OODA REASONING LOOP
                 • Observe Claims (Invoice, Vendor, Account)
                 • Decide Next Tool Dynamically
                 • Act (Exception-Wrapped Execution)
                 • Evaluate Evidence (Match vs Conflict)
                 • Adapt on Failures (2-Tier Replanning)
                 • Cycle Detection (Max 2 calls per tool)
                                 │
                                 ▼
                 IMMUTABLE SQLITE EVIDENCE LEDGER
                 • Authoritative Tool Results & Timestamps
                 • Weighted Risk Signal Aggregation (0 to 100)
                                 │
                                 ▼
                 RUNTIME AUTHORIZATION GATE
                 • Pure Runtime Python Code (Never assert statements)
                 • Enforces 7 Inviolable Security Invariants
                 • Zero Unsafe Approvals on Controlled Benchmarks
                                 │
                                 ▼
                     SAFE DISBURSEMENT DECISION
                   [APPROVE / HUMAN_REVIEW / HOLD]
```

---

## Decision Matrix & Operational Performance (52 Scenarios)

| Actual Scenario | Predicted: APPROVE | Predicted: HOLD / REVIEW | Operational Rate |
|---|:---:|:---:|---|
| **Legitimate (23 cases)** | **23** (Approved) | **0** (Unnecessary holds) | **Unnecessary Hold Rate: 0/23 (0.0%)** (Zero supplier friction) |
| **Risky / Fraud (29 cases)** | **0** (Unsafe approvals) | **29** (Safely held/reviewed) | **Unsafe Approval Rate: 0/29 (0.0%)** (**Zero Unsafe Approvals**) |

- **Approval Accuracy:** 23 / 23 (100.0%)
- **Risk-Case Containment:** 29 / 29 (100.0%)
- **Productive Recoveries:** 5 cases verified via secondary out-of-band contact.
- **Safe Escalations:** 24 cases safely held or escalated when risk was unresolvable.

---

## Quickstart: 1-Click Launch (Runs Backend + Frontend)

```bash
# From this directory:
python run_demo.py
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.
- **Frontend Dashboard:** `http://localhost:5173`
- **FastAPI REST API:** `http://127.0.0.1:8000`
- **Swagger Interactive API Docs:** `http://127.0.0.1:8000/docs`

### Run Automated Tests (89 Tests Passing)
```bash
.venv\Scripts\pytest.exe -v backend/tests
```

### Run Benchmark CLI
```bash
.venv\Scripts\python.exe -m backend.evaluation.runner
```

---

## Competition Documentation Links

- [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) — **Official 3 to 5-minute timed presentation script** with screen cues and narration.
- [`docs/SUBMISSION_BRIEF.md`](docs/SUBMISSION_BRIEF.md) — **Round-1 Hackathon submission brief**.
- [`docs/JUDGE_DEFENSE.md`](docs/JUDGE_DEFENSE.md) — **Technical Defense Handbook** answering the 5 critical judge questions.
