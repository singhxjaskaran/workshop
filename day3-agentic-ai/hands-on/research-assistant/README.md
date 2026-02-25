# Multi-Agent Research Assistant — Hands-On Workshop

> 🛠️ **Duration:** 25 minutes | **Level:** Intermediate

Build a multi-agent system where three AI agents collaboratively plan, research, and write a literature review summary.

---

## 🏗️ Architecture

```
                    ┌──────────────┐
                    │    main.py   │
                    │  (Entry Pt)  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   crew.py    │
                    │ (Orchestrator│
                    │  Pipeline)   │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
     ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
     │   PLANNER   │ │RESEARCHER│ │   WRITER    │
     │   Agent     │ │  Agent   │ │   Agent     │
     │             │ │          │ │             │
     │ Plans the   │ │ Searches │ │ Synthesizes │
     │ research    │ │ & reads  │ │ final       │
     │ strategy    │ │ papers   │ │ review      │
     └──────┬──────┘ └────┬─────┘ └──────┬──────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                    ┌──────▼───────┐
                    │  tools.py    │──── search_papers()
                    │  (Tools)     │──── read_paper()
                    └──────────────┘
                           │
                    ┌──────▼───────┐
                    │  memory.py   │──── EpisodicMemory
                    │  (Memory)    │──── SemanticMemory
                    └──────────────┘
```

---

## 📦 Files Overview

| File | Purpose |
|------|---------|
| `main.py` | Entry point — run with `python main.py` |
| `crew.py` | Creates and runs the multi-agent crew |
| `agents.py` | Defines the 3 agents (Planner, Researcher, Writer) |
| `tasks.py` | Defines CrewAI tasks for each agent |
| `tools.py` | Custom research tools (search, read, save) |
| `memory.py` | Episodic + semantic memory system |
| `config.py` | Configuration and environment loading |
| `.env.example` | Template for API keys |
| `requirements.txt` | Python dependencies |

---

## 🚀 Setup Instructions

### Step 1: Install Python Dependencies

```bash
cd hands-on/research-assistant
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

> **💡 No API key?** Use demo mode: `python main.py --demo "your topic"`

### Step 3: Run the Research Assistant

```bash
# With API key (live mode)
python main.py "transformer architectures in NLP"

# Without API key (demo mode with mock responses)
python main.py --demo "transformer architectures in NLP"
```

---

## 🎓 Workshop Steps (Follow Along)

### Step 1: Understand the Tools (5 min)
Open `tools.py` — see how agents interact with external systems.

### Step 2: Explore the Memory System (5 min)
Open `memory.py` — see episodic and semantic memory in action.

### Step 3: Define the Agents (5 min)
Open `agents.py` — understand role, goal, backstory, and tool assignment.

### Step 4: Set Up Tasks (5 min)
Open `tasks.py` — see how tasks chain agents together.

### Step 5: Run the Crew (5 min)
Open `crew.py` and `main.py` — run the multi-agent system and observe the output.

---

## 🔧 Exercises (Try These!)

1. **Add a Reviewer Agent** — Add a 4th agent that critiques the Writer's output
2. **Switch to Hierarchical Process** — Change `Process.sequential` to `Process.hierarchical`
3. **Add a New Tool** — Create a `cite_paper()` tool that generates citations
4. **Enhance Memory** — Store research findings persistently using ChromaDB

---

## 📤 Sample Output

See `demo_output/sample_research_summary.md` for an example of what the system produces.
