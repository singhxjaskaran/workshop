# Day 3: Agentic AI – From LLMs to Autonomous Agents

> **Duration:** 2.5 Hours | **Level:** Intermediate–Advanced | **Speaker:** Industry/Startup Expert

---

## 🎯 Learning Objectives

By the end of this session, participants will be able to:

1. Differentiate between passive LLMs and agentic AI systems
2. Design prompt chains with self-reflection mechanisms
3. Compare and select appropriate agentic AI frameworks
4. Understand multi-agent coordination and emergent behavior
5. Implement agent memory architectures (episodic, semantic, vector-based)
6. Address safety, alignment, and interpretability challenges
7. **Build a multi-agent research assistant system (hands-on)**

---

## 📋 Prerequisites

- Python 3.10+ installed
- Basic understanding of LLMs and prompt engineering (Day 1 & 2)
- Familiarity with APIs and JSON
- A code editor (VS Code recommended)
- (Optional) OpenAI API key for live mode

---

## ⏱️ Session Schedule

| Time | Module | Duration |
|------|--------|----------|
| 0:00 – 0:25 | **Module 1:** From Passive LLMs to Agentic Behavior | 25 min |
| 0:25 – 0:45 | **Module 2:** Prompt Chaining & Self-Reflection | 20 min |
| 0:45 – 1:05 | **Module 3:** Frameworks for Agentic AI | 20 min |
| 1:05 – 1:15 | ☕ **Break** | 10 min |
| 1:15 – 1:30 | **Module 4:** Multi-Agent Coordination | 15 min |
| 1:30 – 1:50 | **Module 5:** Agent Memory Architectures | 20 min |
| 1:50 – 2:05 | **Module 6:** Safety, Alignment & Interpretability | 15 min |
| 2:05 – 2:30 | 🛠️ **Hands-On:** Multi-Agent Research Assistant | 25 min |

---

## 📚 Course Material

| # | Module | File |
|---|--------|------|
| 1 | From Passive LLMs to Agentic Behavior | [01-passive-llms-to-agents.md](course-material/01-passive-llms-to-agents.md) |
| 2 | Prompt Chaining & Self-Reflection | [02-prompt-chaining-and-reflection.md](course-material/02-prompt-chaining-and-reflection.md) |
| 3 | Frameworks for Agentic AI | [03-agentic-ai-frameworks.md](course-material/03-agentic-ai-frameworks.md) |
| 4 | Multi-Agent Coordination | [04-multi-agent-coordination.md](course-material/04-multi-agent-coordination.md) |
| 5 | Agent Memory Architectures | [05-agent-memory-architectures.md](course-material/05-agent-memory-architectures.md) |
| 6 | Safety, Alignment & Interpretability | [06-safety-alignment-interpretability.md](course-material/06-safety-alignment-interpretability.md) |

---

## 🛠️ Hands-On Project

**Build a Multi-Agent Research Assistant** — a system where multiple AI agents collaboratively plan literature reviews and write summaries.

👉 [Go to Hands-On Project](hands-on/research-assistant/README.md)

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                  ORCHESTRATOR                    │
│            (Sequential Pipeline)                 │
├─────────────────────────────────────────────────┤
│                                                  │
│   ┌───────────┐  ┌────────────┐  ┌───────────┐ │
│   │  PLANNER  │→ │ RESEARCHER │→ │  WRITER   │ │
│   │   Agent   │  │   Agent    │  │  Agent    │ │
│   └─────┬─────┘  └─────┬──────┘  └─────┬─────┘ │
│         │              │              │         │
│   Plans review    Searches &      Synthesizes   │
│   strategy        retrieves       & writes      │
│                   papers          summary        │
│                                                  │
├─────────────────────────────────────────────────┤
│              SHARED MEMORY SYSTEM                │
│   (Episodic + Semantic + Short-term)             │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Hands-On)

```bash
cd hands-on/research-assistant
pip install -r requirements.txt
cp .env.example .env          # Add your API key (or use demo mode)
python main.py --demo "transformer architectures in NLP"
```

---

## 📖 References

- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2023)
- Park et al., "Generative Agents: Interactive Simulacra of Human Behavior" (2023)
- Significant Gravitas, "AutoGPT" — github.com/Significant-Gravitas/AutoGPT
- CrewAI Documentation — docs.crewai.com
- LangChain Documentation — python.langchain.com
- Microsoft AutoGen — microsoft.github.io/autogen
