# VerifyFlow

**Agentic AI security / payment-risk verification workflow**

VerifyFlow investigates vendor payment-change requests and produces one of four constrained actions — `APPROVE`, `HOLD`, `QUARANTINE`, or `HUMAN_REVIEW` — backed by a full evidence trail.

## Architecture

```
Payment Request → Agent Controller → Deterministic Tools → Policy Engine → Decision
```

**Key design:** The LLM does not control authorization. A deterministic policy engine evaluates structured evidence and constrains the final action.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest backend/tests/ -v

# Start API server
uvicorn app.main:app --app-dir backend --reload
```

API docs: http://127.0.0.1:8000/docs

## Project Status

- [x] Milestone 1 — Foundation (project structure, schemas, tools, policy engine)
- [ ] Milestone 2 — Agent Brain (Observe → Decide → Act → Evaluate → Adapt)
- [ ] Milestone 3 — Evidence & Policy
- [ ] Milestone 4 — LLM Integration
- [ ] Milestone 5 — Frontend

## License

MIT
