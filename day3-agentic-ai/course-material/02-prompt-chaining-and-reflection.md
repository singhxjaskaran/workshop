# Module 2: Prompt Chaining & Self-Reflection Mechanisms

> ⏱️ **Duration:** 20 minutes | **Type:** Lecture + Code Examples

---

## 2.1 What is Prompt Chaining?

**Prompt Chaining** is the technique of breaking a complex task into a series of simpler LLM calls, where the output of one call feeds into the next.

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Prompt 1 │────►│ Prompt 2 │────►│ Prompt 3 │────►│  Final  │
│ (Extract)│     │(Analyze) │     │(Generate)│     │ Output  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### Why Chain Prompts?

| Benefit | Explanation |
|---------|-------------|
| **Reduced Complexity** | Each step handles one focused sub-task |
| **Better Quality** | Smaller, clearer instructions → better outputs |
| **Debuggability** | Inspect intermediate results at each step |
| **Controllability** | Add validation, branching, and human review between steps |
| **Reliability** | Retry or fix individual steps without restarting everything |

---

## 2.2 Chaining Patterns

### Pattern 1: Sequential Chain

The simplest pattern — each step feeds into the next linearly.

```python
def sequential_chain(topic):
    # Step 1: Generate an outline
    outline = llm_call(
        f"Create a detailed outline for a research summary on: {topic}"
    )

    # Step 2: Expand each section
    sections = llm_call(
        f"Expand this outline into full paragraphs:\n{outline}"
    )

    # Step 3: Generate an executive summary
    summary = llm_call(
        f"Write a concise executive summary of:\n{sections}"
    )

    return summary
```

**Use when:** Tasks have a clear linear flow (e.g., extract → transform → generate).

---

### Pattern 2: Parallel Chain (Map-Reduce)

Process multiple items independently, then combine results.

```python
import asyncio

async def parallel_chain(papers):
    # MAP: Summarize each paper independently (in parallel)
    tasks = [
        llm_call_async(f"Summarize this paper:\n{paper}")
        for paper in papers
    ]
    summaries = await asyncio.gather(*tasks)

    # REDUCE: Combine all summaries
    combined = llm_call(
        f"Synthesize these summaries into a coherent review:\n"
        + "\n---\n".join(summaries)
    )

    return combined
```

**Use when:** Processing multiple independent items (e.g., analyzing multiple documents).

---

### Pattern 3: Conditional / Branching Chain

Route to different prompts based on intermediate results.

```python
def branching_chain(user_query):
    # Step 1: Classify the query
    classification = llm_call(
        f"Classify this query into one of: [technical, conceptual, comparative]\n"
        f"Query: {user_query}\n"
        f"Output only the category."
    )

    # Step 2: Route to specialized prompt
    if "technical" in classification.lower():
        result = llm_call(
            f"Provide a detailed technical explanation with code: {user_query}"
        )
    elif "comparative" in classification.lower():
        result = llm_call(
            f"Create a comparison table answering: {user_query}"
        )
    else:
        result = llm_call(
            f"Explain conceptually in simple terms: {user_query}"
        )

    return result
```

**Use when:** Different query types need different handling strategies.

---

### Pattern 4: Iterative Refinement Chain

Generate → Critique → Refine, repeated until quality threshold is met.

```python
def iterative_refinement(task, max_iterations=3):
    # Initial generation
    draft = llm_call(f"Write a first draft for: {task}")

    for i in range(max_iterations):
        # Critique the current draft
        critique = llm_call(
            f"Critically evaluate this draft. List specific issues:\n{draft}"
        )

        # Check if quality is good enough
        if "no major issues" in critique.lower():
            break

        # Refine based on critique
        draft = llm_call(
            f"Improve this draft based on the feedback.\n"
            f"Draft:\n{draft}\n\n"
            f"Feedback:\n{critique}"
        )

    return draft
```

**Use when:** Quality matters and you want progressive improvement.

---

## 2.3 Self-Reflection Mechanisms

Self-reflection enables agents to **evaluate their own outputs** and **correct mistakes** autonomously.

### The Reflection Loop

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ GENERATE │────►│ EVALUATE │────►│   GOOD?  │
│          │     │(Self-    │     │          │
│          │     │ Reflect) │     │          │
└──────────┘     └──────────┘     └────┬─────┘
     ▲                                 │
     │              NO                 │ YES
     └─────────────────────────────────┤
                                       ▼
                                 ┌──────────┐
                                 │  OUTPUT  │
                                 └──────────┘
```

### Types of Self-Reflection

| Type | Description | Example |
|------|-------------|---------|
| **Output Verification** | Check if the output meets requirements | "Does this summary cover all 5 papers?" |
| **Fact Checking** | Verify factual accuracy | "Are these citations real and correct?" |
| **Consistency Check** | Ensure internal logical consistency | "Do the conclusions follow from the analysis?" |
| **Quality Assessment** | Rate the quality holistically | "Score this output 1-10 on clarity, depth, accuracy" |
| **Hallucination Detection** | Identify potentially fabricated content | "Which claims lack source attribution?" |

---

## 2.4 Reflexion: A Concrete Framework

**Reflexion** (Shinn et al., 2023) is a framework where agents learn from failures through verbal self-reflection.

```python
class ReflexionAgent:
    def __init__(self):
        self.reflections = []  # Episodic memory of past failures

    def run(self, task, max_attempts=3):
        for attempt in range(max_attempts):
            # Generate action trajectory
            result = self.act(task)

            # Evaluate the result
            evaluation = self.evaluate(task, result)

            if evaluation["success"]:
                return result

            # Reflect on the failure
            reflection = llm_call(
                f"Task: {task}\n"
                f"Your attempt: {result}\n"
                f"Evaluation: {evaluation}\n"
                f"Previous reflections: {self.reflections}\n\n"
                f"Reflect on what went wrong and how to do better next time."
            )

            self.reflections.append(reflection)

        return result  # Return best attempt

    def act(self, task):
        context = "\n".join(self.reflections) if self.reflections else "None"
        return llm_call(
            f"Task: {task}\n"
            f"Lessons from previous attempts:\n{context}\n\n"
            f"Provide your solution:"
        )

    def evaluate(self, task, result):
        eval_result = llm_call(
            f"Task: {task}\n"
            f"Result: {result}\n"
            f"Evaluate: Is this correct and complete? "
            f"Respond as JSON: {{\"success\": true/false, \"reason\": \"...\"}}"
        )
        return json.loads(eval_result)
```

### Key Insight

Agents store **verbal reflections** as memory — not just raw outputs — enabling them to learn from mistakes within a session.

---

## 2.5 Chain-of-Thought (CoT) Prompting

CoT prompting asks the LLM to **show its reasoning step-by-step**, improving accuracy on complex tasks.

### Basic CoT

```
Q: If a research paper has 3 authors and each author has published
   5 papers this year, and each paper has an average of 12 citations,
   how many total citations do all their papers have?

Let me think step by step:
1. Each author published 5 papers this year
2. There are 3 authors, so total papers = 3 × 5 = 15
3. Each paper has an average of 12 citations
4. Total citations = 15 × 12 = 180

Answer: 180 total citations
```

### CoT in Agentic Systems

In agents, CoT becomes the **planning step** — the agent reasons about *what* to do before doing it:

```python
def agent_step(task, available_tools):
    planning_prompt = f"""
    Task: {task}
    Available tools: {available_tools}

    Think step by step:
    1. What information do I need?
    2. Which tool should I use first?
    3. What should I do with the tool's output?
    4. How will I know when I'm done?

    Provide your plan and first action.
    """
    return llm_call(planning_prompt)
```

---

## 2.6 Practical Exercise Preview

In the hands-on session, you'll implement:

1. A **sequential chain** for the Planner Agent (topic → search strategy → plan)
2. A **parallel chain** for the Researcher Agent (search multiple queries simultaneously)
3. A **self-reflection loop** in the Writer Agent (draft → critique → refine)

---

## 🔑 Key Takeaways

1. **Prompt chaining** breaks complex tasks into reliable, debuggable steps
2. Four main patterns: Sequential, Parallel, Branching, and Iterative
3. **Self-reflection** enables agents to evaluate and refine their own outputs
4. **Reflexion** stores verbal lessons from failures as episodic memory
5. **Chain-of-thought** prompting powers the planning module in agents

---

## 💬 Discussion Questions

1. How would you chain prompts for a task in your research domain?
2. What are the trade-offs of adding self-reflection (cost, latency)?
3. When should an agent "give up" vs. continue refining?

---

*← [Module 1](01-passive-llms-to-agents.md) | [Module 3 →](03-agentic-ai-frameworks.md)*
