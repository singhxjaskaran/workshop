# Module 3: Frameworks for Agentic AI

> ⏱️ **Duration:** 20 minutes | **Type:** Lecture + Demo

---

## 3.1 Why Use Frameworks?

Building agentic systems from scratch requires handling:

- Tool management and function calling
- Memory persistence
- Agent orchestration and communication
- Error handling and retry logic
- Prompt templating and management

**Frameworks** provide battle-tested abstractions for all of these.

---

## 3.2 Framework Comparison

| Framework | Creator | Language | Multi-Agent | Memory | Best For |
|-----------|---------|----------|-------------|--------|----------|
| **LangChain** | LangChain Inc. | Python, JS | Via LangGraph | ✅ | General-purpose chains & RAG |
| **AutoGen** | Microsoft | Python | ✅ Native | ✅ | Conversational multi-agent |
| **CrewAI** | CrewAI Inc. | Python | ✅ Native | ✅ | Role-based agent crews |
| **OpenDevin** | Community | Python | ✅ | ✅ | Autonomous coding agents |
| **Semantic Kernel** | Microsoft | C#, Python, Java | Via Plugins | ✅ | Enterprise .NET integration |

---

## 3.3 LangChain / LangGraph

### Overview

LangChain is the **most popular** framework for building LLM applications. LangGraph extends it with **graph-based orchestration** for complex agentic workflows.

```
LangChain Ecosystem:
├── langchain-core      → Base abstractions (prompts, LLMs, tools)
├── langchain           → Chains, agents, retrieval
├── langgraph           → Graph-based multi-agent orchestration
├── langsmith           → Observability and tracing
└── langserve           → Deploy as REST APIs
```

### LangGraph Agent Example

```python
from langgraph.graph import StateGraph, MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def search_papers(query: str) -> str:
    """Search for academic papers."""
    return f"Found 5 papers on '{query}'..."

# Define the agent
llm = ChatOpenAI(model="gpt-4").bind_tools([search_papers])

def agent_node(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

def tool_node(state: MessagesState):
    # Execute tool calls from the last message
    ...

# Build the graph
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.add_edge("agent", "tools")
graph.add_edge("tools", "agent")

app = graph.compile()
result = app.invoke({"messages": [("user", "Find papers on RAG")]})
```

### Strengths & Weaknesses

| ✅ Strengths | ❌ Weaknesses |
|-------------|--------------|
| Largest ecosystem & community | Steep learning curve |
| Excellent documentation | Frequent API changes |
| Integrations with 100+ LLMs/tools | Can be over-abstracted |
| LangSmith for tracing | |

---

## 3.4 Microsoft AutoGen

### Overview

AutoGen enables **multi-agent conversations** where agents chat with each other to solve problems.

```
┌──────────────────────────────────────────┐
│           AutoGen Conversation           │
│                                          │
│  User ──► Assistant ──► Critic ──►...   │
│              │              │            │
│         Tool calls    Provides           │
│                      feedback            │
└──────────────────────────────────────────┘
```

### AutoGen Multi-Agent Example

```python
from autogen import AssistantAgent, UserProxyAgent

# Create agents
assistant = AssistantAgent(
    name="Research_Assistant",
    system_message="""You are a research assistant. 
    Search for papers and summarize findings.""",
    llm_config={"model": "gpt-4"}
)

critic = AssistantAgent(
    name="Research_Critic",
    system_message="""You review research summaries for accuracy, 
    completeness, and bias. Provide constructive feedback.""",
    llm_config={"model": "gpt-4"}
)

user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",  # Fully autonomous
    code_execution_config={"work_dir": "output"}
)

# Start a group chat
from autogen import GroupChat, GroupChatManager

group_chat = GroupChat(
    agents=[user_proxy, assistant, critic],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=group_chat)
user_proxy.initiate_chat(
    manager,
    message="Research the latest advances in RAG systems"
)
```

### Strengths & Weaknesses

| ✅ Strengths | ❌ Weaknesses |
|-------------|--------------|
| Natural conversational paradigm | Less structured than CrewAI |
| Code execution built-in | Can be verbose/chatty |
| Microsoft backing & support | Fewer integrations than LangChain |
| Flexible agent topologies | |

---

## 3.5 CrewAI

### Overview

CrewAI uses a **role-based** paradigm inspired by human organizations. You define agents with specific roles, goals, and tools — then assemble them into a "crew."

```
┌─────────────────────────────────────┐
│              CREW                    │
│                                      │
│  ┌──────────┐  ┌──────────────────┐ │
│  │ Agent 1   │  │ Agent 2          │ │
│  │ Role:     │  │ Role:            │ │
│  │ Planner   │  │ Researcher       │ │
│  │ Goal:     │  │ Goal:            │ │
│  │ Plan the  │  │ Find relevant    │ │
│  │ research  │  │ papers           │ │
│  └──────────┘  └──────────────────┘ │
│                                      │
│  Process: Sequential / Hierarchical  │
│  Memory: Shared context              │
└─────────────────────────────────────┘
```

### CrewAI Example

```python
from crewai import Agent, Task, Crew, Process

# Define Agents
planner = Agent(
    role="Research Planner",
    goal="Create a comprehensive research plan",
    backstory="You are an expert academic researcher who excels "
              "at planning systematic literature reviews.",
    verbose=True
)

researcher = Agent(
    role="Literature Researcher",
    goal="Find and analyze relevant academic papers",
    backstory="You are a diligent researcher who thoroughly "
              "searches for and analyzes academic literature.",
    verbose=True
)

writer = Agent(
    role="Summary Writer",
    goal="Write a clear, well-structured literature review",
    backstory="You are a skilled academic writer who synthesizes "
              "complex research into clear narratives.",
    verbose=True
)

# Define Tasks
plan_task = Task(
    description="Create a research plan for: {topic}",
    agent=planner,
    expected_output="A structured research plan with key areas to explore"
)

research_task = Task(
    description="Research papers based on the plan",
    agent=researcher,
    expected_output="Summaries of relevant papers with key findings"
)

write_task = Task(
    description="Write a literature review summary",
    agent=writer,
    expected_output="A comprehensive literature review document"
)

# Create and Run Crew
crew = Crew(
    agents=[planner, researcher, writer],
    tasks=[plan_task, research_task, write_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff(inputs={"topic": "transformer architectures"})
```

### Why We'll Use CrewAI for Hands-On

| Feature | Benefit for Workshop |
|---------|---------------------|
| Intuitive role-based design | Easy to understand conceptually |
| Minimal boilerplate | Get started quickly |
| Sequential + hierarchical processes | Demonstrates coordination patterns |
| Built-in memory | Shows agent memory in action |
| Clean, readable code | Great for teaching |

---

## 3.6 OpenDevin (now OpenHands)

### Overview

OpenDevin is an **open-source autonomous coding agent** — like an open-source version of Devin by Cognition.

### Key Capabilities

- Writes, debugs, and deploys code autonomously
- Uses a sandboxed environment (Docker containers)
- Browses the web for documentation
- Multi-agent architecture internally

### Architecture

```
┌───────────────────────────────────┐
│           OpenDevin               │
├───────────────────────────────────┤
│  Controller Agent                 │
│  ├── CodeAct Agent (writes code)  │
│  ├── Browser Agent (web search)   │
│  └── Planner Agent (task decomp)  │
├───────────────────────────────────┤
│  Sandbox (Docker)                 │
│  ├── Terminal                     │
│  ├── File System                  │
│  └── Browser                     │
└───────────────────────────────────┘
```

### Best For

- Automated software development
- Bug fixing and code migration
- Research prototype implementation

---

## 3.7 Semantic Kernel

### Overview

Microsoft's **Semantic Kernel** is designed for **enterprise applications**, with first-class support for C# and .NET alongside Python and Java.

### Key Concepts

```python
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

kernel = sk.Kernel()

# Add AI service
kernel.add_service(
    OpenAIChatCompletion(service_id="chat", ai_model_id="gpt-4")
)

# Define a "semantic function" (plugin)
summarize = kernel.add_function(
    function_name="summarize",
    plugin_name="TextPlugin",
    prompt="Summarize the following text:\n{{$input}}"
)

# Use it
result = await kernel.invoke(summarize, input="Long text here...")
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Plugins** | Encapsulate AI functions + native code |
| **Planners** | Auto-generate plans from available plugins |
| **Memory** | Built-in vector memory with multiple backends |
| **Enterprise-ready** | Azure integration, security, compliance |

---

## 3.8 Framework Selection Guide

```
Is this a coding/dev task?
  └── YES → OpenDevin
  └── NO ↓

Do you need multi-agent collaboration?
  └── NO → LangChain / Semantic Kernel
  └── YES ↓

Do you prefer role-based or conversational agents?
  ├── Role-based → CrewAI
  └── Conversational → AutoGen

Is it an enterprise .NET app?
  └── YES → Semantic Kernel
```

---

## 🔑 Key Takeaways

1. **LangChain** — the Swiss Army knife; largest ecosystem, best for general-purpose chains
2. **AutoGen** — best for conversational multi-agent systems
3. **CrewAI** — most intuitive for role-based multi-agent collaboration
4. **OpenDevin** — for autonomous coding and software engineering
5. **Semantic Kernel** — enterprise-grade, especially for .NET/Azure ecosystems
6. **No single "best" framework** — choose based on your use case

---

## 💬 Discussion Questions

1. Which framework best fits your current research or industry needs?
2. What's the tradeoff between using a framework vs. building custom?
3. How do you evaluate the maturity and reliability of an open-source AI framework?

---

*← [Module 2](02-prompt-chaining-and-reflection.md) | [Module 4 →](04-multi-agent-coordination.md)*
