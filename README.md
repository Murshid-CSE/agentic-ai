# VerifyFlow — Autonomous Payment Risk Verification & Deterministic Policy Safety

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Pytest](https://img.shields.io/badge/pytest-89%2F89%20passed-success.svg)](https://docs.pytest.org/)
[![Safety Invariant](https://img.shields.io/badge/Critical%20False%20Approvals-0%20%5BPASS%5D-brightgreen.svg)]()

> **VerifyFlow** is an agentic AI payment-risk and vendor-verification system designed for high-stakes business-to-business (B2B) disbursements. It pairs an autonomous **Observe → Decide → Act → Evaluate → Adapt** reasoning loop with an **inviolable deterministic runtime authorization gate** and an **auditable SQLite evidence ledger**.

---

## Key Highlights & Innovations

1. **Autonomous OODA Reasoning Loop**:
   - Dynamic tool selection (2 to 6 tools per investigation).
   - Early stopping on unknown vendors (stops at tool 2, saving 66% compute).
   - Dynamic pruning reduces total tool invocations by **28.5%** compared to static pipelines.
2. **Deterministic Runtime Authorization Gate**:
   - The LLM and planner *never* make final authorization decisions.
   - Enforces 7 inviolable security invariants in pure runtime code (never Python `assert` statements).
   - **Guarantees ZERO Critical False Approvals** across all evaluated fraud scenarios.
3. **Multi-Step Failure Adaptation & 2-Tier Replanning**:
   - Explicit failure taxonomy (`TOOL_UNAVAILABLE`, `INVALID_RESULT`, `TIMEOUT`, `CONFLICT`).
   - Automatically replans alternative out-of-band verification paths (secondary trusted contacts) when primary channels fail.
4. **Architectural Trust Boundary**:
   - Untrusted invoices and emails are wrapped in `<untrusted_document>` boundary tags.
   - LLM operates strictly as a passive entity extractor into strict Pydantic schemas.
   - Immune to prompt injection overrides (tested and verified).
5. **Auditable SQLite Evidence Ledger**:
   - Every tool call, raw result, risk signal, and reason is cryptographically structured and queryable.
6. **52-Scenario Independent Benchmark Suite**:
   - Includes 2×2 Confusion Matrix, comparative baselines, and 0.00% False Positive Rate.
   - Interactive Frontend Dashboard with 1-click live trace inspection and animated replay.

---

## Milestone Progress

| Milestone | Description | Status |
|---|---|:---:|
| **M1** | Foundation (Schemas, deterministic tools, demo datasets) | ✅ |
| **M2** | Agent Brain (Dynamic tool selection, OODA reasoning loop) | ✅ |
| **M3** | Evidence & Policy (SQLite ledger, weighted risk scoring, strict policy) | ✅ |
| **M4** | LLM Integration (Unstructured text extraction, schema boundary, fail-closed) | ✅ |
| **M5** | Frontend (Investigation Command Center, animated trace replay) | ✅ |
| **M6** | Failure & Adaptation (Explicit taxonomy, 2-tier replanning, injection knobs) | ✅ |
| **M7 / M7.1** | Independent Evaluation & Benchmark (52 scenarios, Confusion Matrix, Baselines) | ✅ |
| **M8** | System Hardening (Runtime Auth Gate, 7 Invariants, Cycle Guard, Fuzzing) | ✅ |
| **M9** | Submission & Demo (Documentation, video, packaging) | ⏭️ Next |
| **M10** | Judge Defense (Technical architecture defense & FAQ) | ⏳ Planned |

---

## Benchmark Results (52 Independent Scenarios)

```text
================================================================================
                        VERIFYFLOW BENCHMARK REPORT                             
================================================================================
  Total Scenarios Evaluated:          52
  Decision Accuracy:                100.00% (52/52)
  Critical False Approvals:            0 [PASS - ZERO TOLERANCE MET]
  Critical Decision Safety:         100.00%
  Adaptation Resilience:            100.00% (29/29 safe recoveries)
    - Productive Recoveries:           5 (Verified via secondary contact -> APPROVE)
    - Safe Escalations:               24 (Fail-closed on unresolvable risk)
  Avg Tools Executed / Case:          4.29 (vs 6.00 static pipeline; 28.5% calls saved)
  False Positive Rate:                 0.00% (Zero friction on legitimate invoices)
  False Approval Rate:                 0.00% (Zero unauthorized disbursements)
================================================================================
```

### Comparative Baselines

| Architecture | Accuracy | False Approvals | Avg Tools | Pruning | Prompt Injection Defense |
|---|:---:|:---:|:---:|:---:|:---:|
| **Baseline A (Static 6-Tool Pipeline)** | 100.0% | 0 | 6.00 | None | Protected |
| **Baseline B (One-Shot LLM Classifier)**| 88.5% | **6 (FAIL)** | 0.00 | N/A | **VULNERABLE** |
| **VerifyFlow (Adaptive OODA + Auth Gate)**| **100.0%** | **0 [PASS]** | **4.29** | **Dynamic (2 to 6)**| **Protected (Trust Boundary)** |

---

## Quickstart & Installation

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd verifyflow
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Test Suite (89 Tests)
```bash
pytest -v backend/tests
```

### 4. Run the Evaluation Benchmark CLI
```bash
python -m backend.evaluation.runner
```

### 5. Start the Application
**Terminal 1 (Backend API):**
```bash
cd verifyflow
uvicorn backend.app.main:app --reload --port 8000
```

**Terminal 2 (Frontend Dashboard):**
```bash
cd verifyflow/frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Repository Structure

```text
agentic-ai/
├── README.md                         # Root repository documentation
├── .gitignore                        # Global ignore rules
└── verifyflow/
    ├── backend/
    │   ├── app/
    │   │   ├── agent/                # OODA Loop, Planner, Policy, Authorization Gate, Guardrails
    │   │   ├── database/             # SQLite Evidence Ledger & schema migrations
    │   │   ├── evaluation/           # Metrics calculation, Baselines, CLI reports
    │   │   ├── llm/                  # Schema boundary & structured extraction
    │   │   ├── models/               # Pydantic domain models & schemas
    │   │   ├── services/             # Audit & transaction services
    │   │   ├── tools/                # 6 deterministic verification tools
    │   │   └── main.py               # FastAPI application entry point
    │   ├── evaluation/
    │   │   └── runner.py             # CLI runner entry point
    │   └── tests/                    # 89 passing unit, integration, and hardening tests
    ├── data/
    │   ├── demo_cases/               # Interactive demo scenarios
    │   ├── evaluation/               # 52 benchmark cases & independent ground truth
    │   └── vendors.json              # Historical vendor registry baseline
    └── frontend/
        ├── src/
        │   ├── components/           # Investigation Center, Trace, Confusion Matrix, Baselines
        │   ├── services/             # API client & offline simulation
        │   └── App.jsx               # Application root
        └── package.json
```

---

## License

MIT License. Designed and engineered for high-assurance autonomous financial workflows.
