# Module 5 — Agent Memory Architecture Demo

Live demo using OpenAI API — no demo mode, real LLM calls.

## Quick Start

```bash
cd memory-demos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python memory_demo.py
```

## What It Shows

| Demo | Memory Type | Key Concept |
|------|------------|-------------|
| 1 | **Short-Term** | Sliding window — early context gets lost |
| 2 | **Episodic** | Event log + LLM self-reflection on its own history |
| 3 | **Semantic** | ChromaDB vectors + RAG-style retrieval by meaning |

Requires `OPENAI_API_KEY` in `.env` file.
