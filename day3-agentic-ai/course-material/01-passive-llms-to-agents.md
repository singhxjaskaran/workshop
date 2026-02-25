# Module 1: From Passive LLMs to Agentic Behavior

> ⏱️ **Duration:** 25 minutes | **Type:** Lecture + Discussion

---

## 1.1 The Limitations of Passive LLMs

Traditional LLMs operate in a **request-response** paradigm:

```
User Prompt → LLM → Single Response
```

### Key Limitations

| Limitation | Description |
|-----------|-------------|
| **No Memory** | Each call is stateless; no recall of previous conversations |
| **No Planning** | Cannot break complex tasks into sub-steps autonomously |
| **No Tool Use** | Cannot browse the web, run code, or query databases |
| **No Self-Correction** | Cannot verify or refine its own outputs |
| **Knowledge Cutoff** | Training data has a fixed date; cannot access real-time info |
| **Hallucination** | Generates plausible but factually incorrect information |

### Illustrative Example

**Task:** "Find the latest 5 papers on transformer architectures, summarize them, and create a comparison table."

- **Passive LLM:** Generates a *plausible-looking* but potentially hallucinated list from training data
- **Agentic System:** Actually searches arXiv → reads papers → extracts key points → generates verified summary

---

## 1.2 What Makes an Agent "Agentic"?

An **AI agent** is a system that can:

1. **Perceive** its environment (receive inputs, read data)
2. **Plan** a sequence of actions toward a goal
3. **Act** using tools and APIs
4. **Reflect** on the outcomes and adjust

### The Agent Loop

```
                  ┌──────────────┐
                  │   PERCEIVE   │
                  │  (Observe)   │
                  └──────┬───────┘
                         │
                         ▼
┌──────────┐     ┌──────────────┐
│  REFLECT │◄────│    PLAN      │
│(Evaluate)│     │  (Reason)    │
└────┬─────┘     └──────┬───────┘
     │                   │
     │                   ▼
     │           ┌──────────────┐
     └──────────►│     ACT      │
                 │  (Execute)   │
                 └──────────────┘
```

---

## 1.3 Anatomy of an AI Agent

```
┌─────────────────────────────────────────────────┐
│                   AI AGENT                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────────┐  ┌─────────────┐               │
│  │   LLM Core  │  │   Memory    │               │
│  │  (Brain)    │  │  System     │               │
│  └──────┬──────┘  └──────┬──────┘               │
│         │                │                       │
│  ┌──────┴──────┐  ┌──────┴──────┐               │
│  │  Planning   │  │   Tools     │               │
│  │  Module     │  │  Interface  │               │
│  └─────────────┘  └──────┬──────┘               │
│                          │                       │
│         ┌────────────────┼────────────┐          │
│         ▼                ▼            ▼          │
│   ┌──────────┐   ┌──────────┐  ┌──────────┐    │
│   │  Search  │   │  Code    │  │ Database │    │
│   │  API     │   │  Exec    │  │  Query   │    │
│   └──────────┘   └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────┘
```

### Core Components

| Component | Role | Example |
|-----------|------|---------|
| **LLM Core** | Reasoning engine; decides what to do next | GPT-4, Claude, Gemini |
| **Memory** | Stores context, past actions, and knowledge | Vector DB, conversation buffer |
| **Planning** | Breaks goals into action sequences | Chain-of-thought, task decomposition |
| **Tools** | Interfaces to external systems | Web search, code execution, APIs |

---

## 1.4 The ReAct Pattern

**ReAct** (Reasoning + Acting) is the foundational pattern for agentic behavior, introduced by Yao et al. (2023).

### How It Works

```
Question: What is the GDP of the country with the tallest building in 2024?

Thought 1: I need to find the tallest building in 2024.
Action 1: search("tallest building in the world 2024")
Observation 1: The Burj Khalifa in Dubai, UAE (828m)...

Thought 2: Now I need the GDP of the UAE.
Action 2: search("UAE GDP 2024")
Observation 2: UAE GDP in 2024 is approximately $509 billion...

Thought 3: I have enough information to answer.
Answer: The country with the tallest building (Burj Khalifa, UAE)
         has a GDP of approximately $509 billion (2024).
```

### Key Insight

The LLM **interleaves reasoning** (Thought) with **tool use** (Action) and **observation**, enabling it to ground its responses in real data.

### ReAct vs. Other Approaches

| Approach | Reasoning | Acting | Grounded |
|----------|-----------|--------|----------|
| Standard Prompting | ✅ | ❌ | ❌ |
| Chain-of-Thought | ✅ | ❌ | ❌ |
| Action-only | ❌ | ✅ | ✅ |
| **ReAct** | **✅** | **✅** | **✅** |

---

## 1.5 Function Calling / Tool Use

Modern LLMs support **function calling** — the model outputs structured JSON indicating which function to call and with what arguments.

### OpenAI Function Calling Example

```python
import openai

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search academic papers on a given topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Find papers on attention mechanisms"}
    ],
    tools=tools,
    tool_choice="auto"
)

# The model responds with a function call:
# {
#   "name": "search_papers",
#   "arguments": {"query": "attention mechanisms", "max_results": 5}
# }
```

---

## 1.6 From LLM to Agent: The Evolution

```
Level 0: Chat        → Simple Q&A (ChatGPT, basic mode)
Level 1: Tools       → LLM + function calling (single step)
Level 2: ReAct       → Reasoning + Acting loop (multi-step)
Level 3: Planning    → Goal decomposition + execution
Level 4: Multi-Agent → Multiple specialized agents collaborating
Level 5: Autonomous  → Self-directed, long-running agents (AutoGPT)
```

### Real-World Agentic Systems

| System | Level | Description |
|--------|-------|-------------|
| ChatGPT Plugins | 1–2 | LLM with tool access |
| GitHub Copilot Workspace | 3 | Plans and implements code changes |
| Devin (Cognition) | 4–5 | Autonomous software engineer |
| AutoGPT | 5 | Self-directed task completion |
| CrewAI | 4 | Multi-agent collaboration framework |

---

## 🔑 Key Takeaways

1. **Passive LLMs** are limited to single-turn, stateless text generation
2. **Agents** add memory, planning, tools, and reflection loops
3. The **ReAct pattern** is foundational — interleave reasoning with action
4. **Function calling** makes tool use structured and reliable
5. Agentic systems exist on a **spectrum** from simple tool use to full autonomy

---

## 💬 Discussion Questions

1. Where does your current use of LLMs fall on the agentic spectrum?
2. What tasks in your domain would benefit most from agentic behavior?
3. What are the risks of giving LLMs autonomous tool access?

---

*Next: [Module 2 — Prompt Chaining & Self-Reflection →](02-prompt-chaining-and-reflection.md)*
