# Module 4: Multi-Agent Coordination & Emergent Behavior

> ⏱️ **Duration:** 15 minutes | **Type:** Lecture + Case Studies

---

## 4.1 Why Multi-Agent Systems?

A single agent has limitations:
- **Cognitive overload** — one LLM handling planning, research, writing, and review
- **Role confusion** — switching between personas degrades quality
- **No checks and balances** — no one to review the agent's work

**Multi-agent systems** mirror how human organizations work — specialized roles, division of labor, and collaborative review.

---

## 4.2 Coordination Patterns

### Pattern 1: Sequential Pipeline

Agents pass work product to the next agent in a fixed order.

```
Planner → Researcher → Writer → Reviewer → Final Output
```

```python
# CrewAI Sequential Process
crew = Crew(
    agents=[planner, researcher, writer, reviewer],
    tasks=[plan_task, research_task, write_task, review_task],
    process=Process.sequential  # Fixed order
)
```

**Pros:** Simple, predictable, easy to debug  
**Cons:** No parallelism, rigid flow

---

### Pattern 2: Hierarchical (Manager-Worker)

A **manager agent** delegates tasks to worker agents and reviews their output.

```
            ┌──────────┐
            │ MANAGER  │
            │ (GPT-4)  │
            └────┬─────┘
         ┌───────┼───────┐
         ▼       ▼       ▼
    ┌────────┐ ┌────────┐ ┌────────┐
    │Worker 1│ │Worker 2│ │Worker 3│
    │Planner │ │Search  │ │Writer  │
    └────────┘ └────────┘ └────────┘
```

```python
# CrewAI Hierarchical Process
crew = Crew(
    agents=[planner, researcher, writer],
    tasks=[plan_task, research_task, write_task],
    process=Process.hierarchical,
    manager_llm=ChatOpenAI(model="gpt-4")  # Manager decides who works on what
)
```

**Pros:** Dynamic task allocation, manager reviews quality  
**Cons:** Manager is a bottleneck, higher cost

---

### Pattern 3: Debate / Adversarial

Multiple agents argue different positions to arrive at a better answer.

```
┌──────────┐     ┌──────────┐
│ Agent A   │◄───►│ Agent B   │
│ (For)     │     │ (Against) │
└──────┬────┘     └────┬──────┘
       │               │
       └───────┬───────┘
               ▼
        ┌──────────┐
        │  Judge   │
        │  Agent   │
        └──────────┘
```

**Use case:** Fact-checking, policy analysis, risk assessment

---

### Pattern 4: Blackboard / Shared Memory

All agents read from and write to a shared workspace.

```
┌─────────────────────────────────────┐
│         SHARED BLACKBOARD           │
│                                      │
│  Research Plan: ✅                   │
│  Papers Found: ["paper1", "paper2"] │
│  Summaries: ["summary1"]            │
│  Review Status: In Progress          │
└──────────┬──────┬──────┬────────────┘
           │      │      │
      ┌────┴┐  ┌──┴──┐  ┌┴─────┐
      │Plan │  │Search│  │Write │
      │Agent│  │Agent │  │Agent │
      └─────┘  └─────┘  └──────┘
```

**Pros:** Flexible, agents can work asynchronously  
**Cons:** Potential conflicts, needs coordination rules

---

## 4.3 Communication Protocols

### How Do Agents Talk to Each Other?

| Protocol | Description | Example |
|----------|-------------|---------|
| **Message Passing** | Direct agent-to-agent messages | AutoGen conversations |
| **Shared State** | Agents read/write shared memory | CrewAI context sharing |
| **Event-Driven** | Agents react to events/triggers | LangGraph state transitions |
| **Publish-Subscribe** | Agents subscribe to topics | Kafka-like agent bus |

### AutoGen Conversational Protocol

```python
# Agents have a natural conversation
User: "Research transformer architectures"
Assistant: "I'll start by searching for recent papers..."
  → [calls search tool]
  → "I found 5 papers. Here are the key findings..."
Critic: "The summary misses attention mechanism variants.
         Please expand on multi-head attention."
Assistant: "Good point. Let me elaborate..."
  → [refined output]
Critic: "This looks comprehensive now. APPROVE."
```

---

## 4.4 Emergent Behavior

When agents interact, **emergent behaviors** can arise that were not explicitly programmed.

### Positive Emergent Behavior

| Behavior | Example |
|----------|---------|
| **Self-organization** | Agents naturally specialize further based on successful outcomes |
| **Quality improvement** | Critic agents push other agents to produce better output |
| **Creative solutions** | Debate between agents surfaces novel approaches |
| **Error correction** | One agent catches another's mistakes |

### Negative Emergent Behavior (Risks!)

| Risk | Description |
|------|-------------|
| **Infinite loops** | Agents keep critiquing each other without convergence |
| **Sycophancy** | Agents agree with each other to avoid conflict |
| **Hallucination amplification** | One agent's hallucination gets reinforced by others |
| **Goal drift** | Agents collectively drift away from the original objective |

### Mitigation Strategies

```python
# 1. Set maximum interaction rounds
crew = Crew(max_iterations=10)

# 2. Use a judge/arbiter agent
judge = Agent(
    role="Quality Arbiter",
    goal="Ensure the final output meets quality standards",
    backstory="You are a strict but fair academic reviewer."
)

# 3. Ground agents with tool outputs (not just opinons)
researcher = Agent(
    tools=[search_tool, paper_reader_tool],  # Grounded in real data
)

# 4. Add explicit stopping criteria
review_task = Task(
    description="Review the summary. If quality score >= 8/10, "
                "APPROVE. Otherwise, list specific improvements needed.",
)
```

---

## 4.5 Case Study: Generative Agents (Stanford, 2023)

Park et al. created a **virtual town** with 25 AI agents that:
- Had persistent memories and relationships
- Planned daily schedules autonomously
- Formed opinions and relationships
- Organized social events (e.g., a Valentine's Day party)

### Key Architecture

```
Each Agent:
├── Memory Stream (episodic memory of all observations)
├── Reflection Module (generates higher-level insights)
├── Planning Module (creates daily/hourly plans)
└── Action Module (executes plans in the virtual world)
```

### Emergent Behaviors Observed
- Agents **spread information** through natural conversation
- They **formed relationships** based on shared interests
- One agent **organized a party** and invited others
- Agents showed **personality consistency** over time

---

## 🔑 Key Takeaways

1. **Multi-agent systems** mirror human organizations for better quality & specialization
2. Four main patterns: Sequential, Hierarchical, Debate, and Blackboard
3. **Emergent behavior** can be both powerful and dangerous
4. Always include **stopping criteria**, **grounding**, and **quality checks**
5. Real-world examples (Stanford's Generative Agents) show remarkable emergent properties

---

*← [Module 3](03-agentic-ai-frameworks.md) | [Module 5 →](05-agent-memory-architectures.md)*
