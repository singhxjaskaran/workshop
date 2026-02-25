# Module 6 — Safety, Alignment & Interpretability Demo

Live demo using OpenAI API — 5 interpretability and safety strategies.

## Quick Start

```bash
cd interpretability-demos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python interpretability_demo.py
```

## What It Shows

| # | Demo | Strategy |
|---|------|----------|
| 1 | 🛡️ Prompt Injection | Regex scanner blocks malicious inputs before LLM sees them |
| 2 | 🔍 Chain-of-Thought | Opaque vs transparent reasoning — same question, different visibility |
| 3 | 📋 Audit Trail | Every decision logged with timestamp, reasoning, and LLM confidence |
| 4 | 🚧 Guardrails | Action allowlists + output filtering (redacts emails, IPs, API keys) |
| 5 | 🧑‍💻 HITL | Agent pauses for human approval on high-risk actions |

Requires `OPENAI_API_KEY` in `.env` file.
