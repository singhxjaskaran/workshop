# Module 5: Agent Memory Architectures

> ⏱️ **Duration:** 20 minutes | **Type:** Lecture + Code Walkthrough

---

## 5.1 Why Agents Need Memory

Without memory, agents:
- Forget what they've already done (repeat work)
- Can't build on previous findings
- Lose context in long-running tasks
- Can't learn from past mistakes

### Human Memory vs. Agent Memory

| Human Memory | Agent Equivalent | Purpose |
|-------------|------------------|---------|
| **Working Memory** | Context window / Short-term buffer | Current task context |
| **Episodic Memory** | Conversation history / Event logs | "What happened" |
| **Semantic Memory** | Vector database / Knowledge base | "What I know" |
| **Procedural Memory** | Learned tool-use patterns / Fine-tuning | "How to do things" |

---

## 5.2 Short-Term Memory (Context Window)

The simplest form of memory: **the LLM's context window** itself.

```python
class ShortTermMemory:
    """Maintains recent messages within the context window."""

    def __init__(self, max_messages=20):
        self.messages = []
        self.max_messages = max_messages

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        # Sliding window: remove oldest if too many
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self):
        return self.messages
```

### Limitations

- **Fixed size** — context windows are finite (4K – 128K tokens)
- **No prioritization** — old messages pushed out regardless of importance
- **No retrieval** — can't search across sessions

---

## 5.3 Episodic Memory

Stores **specific events and interactions** — like a diary of what the agent has done.

```python
import json
from datetime import datetime

class EpisodicMemory:
    """Stores timestamped events and interactions."""

    def __init__(self):
        self.episodes = []

    def record(self, event_type, content, metadata=None):
        episode = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,      # "action", "observation", "reflection"
            "content": content,
            "metadata": metadata or {}
        }
        self.episodes.append(episode)

    def get_recent(self, n=10):
        """Get the N most recent episodes."""
        return self.episodes[-n:]

    def search_by_type(self, event_type):
        """Get all episodes of a specific type."""
        return [e for e in self.episodes if e["type"] == event_type]

    def get_reflections(self):
        """Get all reflection episodes (lessons learned)."""
        return self.search_by_type("reflection")

    def summarize(self):
        """Generate a summary of all episodes."""
        if not self.episodes:
            return "No episodes recorded yet."
        
        summary_lines = []
        for ep in self.episodes:
            summary_lines.append(
                f"[{ep['timestamp'][:16]}] {ep['type'].upper()}: "
                f"{ep['content'][:100]}"
            )
        return "\n".join(summary_lines)
```

### Use Cases

- **Research agents:** Remember which papers were already read
- **Coding agents:** Track which files were modified and why
- **Reflexion pattern:** Store verbal reflections on past failures

---

## 5.4 Semantic Memory (Vector-Based Retrieval)

Stores **knowledge and facts** as vector embeddings for similarity-based retrieval.

### How Vector-Based Retrieval Works

```
1. STORE                          2. RETRIEVE
   Text → Embedding Model →         Query → Embedding Model →
   → Vector [0.1, 0.3, ...]        → Vector [0.2, 0.3, ...]
   → Store in Vector DB              → Similarity Search
                                      → Top-K Results
```

### Implementation with ChromaDB

```python
import chromadb
from chromadb.utils import embedding_functions

class SemanticMemory:
    """Vector-based semantic memory using ChromaDB."""

    def __init__(self, collection_name="agent_memory"):
        self.client = chromadb.Client()

        # Use a sentence transformer for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def store(self, text, metadata=None, doc_id=None):
        """Store a piece of knowledge."""
        doc_id = doc_id or f"doc_{self.collection.count()}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )

    def retrieve(self, query, top_k=5):
        """Retrieve the most relevant memories for a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results["documents"][0]  # List of relevant texts

    def retrieve_with_scores(self, query, top_k=5):
        """Retrieve with similarity scores."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "distances", "metadatas"]
        )
        return [
            {
                "text": doc,
                "distance": dist,
                "metadata": meta
            }
            for doc, dist, meta in zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0]
            )
        ]
```

### Embedding Models Comparison

| Model | Dimensions | Speed | Quality | Free? |
|-------|-----------|-------|---------|-------|
| `all-MiniLM-L6-v2` | 384 | ⚡ Fast | Good | ✅ Yes |
| `text-embedding-3-small` | 1536 | Medium | Very Good | 💰 Paid |
| `text-embedding-3-large` | 3072 | Slow | Excellent | 💰 Paid |
| `nomic-embed-text-v1.5` | 768 | Fast | Very Good | ✅ Yes |

---

## 5.5 RAG: Memory Meets Generation

**Retrieval-Augmented Generation (RAG)** combines vector retrieval with LLM generation.

```
User Query
    │
    ▼
┌──────────────┐     ┌──────────────┐
│  Retrieve    │────►│   Generate   │
│  Relevant    │     │   Response   │
│  Documents   │     │   with       │
│  from Vector │     │   Context    │
│  Store       │     │              │
└──────────────┘     └──────────────┘
```

### RAG for Agent Memory

```python
def agent_with_rag_memory(query, semantic_memory, episodic_memory):
    # 1. Retrieve relevant knowledge
    relevant_docs = semantic_memory.retrieve(query, top_k=3)

    # 2. Get recent episode context
    recent_episodes = episodic_memory.get_recent(n=5)

    # 3. Generate response with full context
    prompt = f"""
    Question: {query}

    Relevant Knowledge (from your memory):
    {chr(10).join(f'- {doc}' for doc in relevant_docs)}

    Recent Activity:
    {episodic_memory.summarize()}

    Based on your memory and recent activity, provide a comprehensive answer.
    """

    response = llm_call(prompt)

    # 4. Store this interaction in memory
    episodic_memory.record("action", f"Answered query: {query}")
    semantic_memory.store(response, metadata={"type": "generated_answer"})

    return response
```

---

## 5.6 Advanced Memory Patterns

### Memory Consolidation

Like human sleep, agents can periodically summarize and consolidate memories:

```python
def consolidate_memories(episodic_memory, semantic_memory):
    """Consolidate episodic memories into semantic knowledge."""
    recent = episodic_memory.get_recent(n=50)

    # Use LLM to extract key insights
    consolidation_prompt = f"""
    Review these recent experiences and extract key insights,
    patterns, and learnings that would be valuable to remember
    long-term:

    {json.dumps(recent, indent=2)}

    Format as a list of key insights.
    """

    insights = llm_call(consolidation_prompt)

    # Store consolidated insights in semantic memory
    for i, insight in enumerate(insights.split("\n")):
        if insight.strip():
            semantic_memory.store(
                insight.strip(),
                metadata={"type": "consolidated_insight"}
            )
```

### Memory Importance Scoring

Not all memories are equally important. Score and prioritize:

```python
def score_importance(memory_content):
    """Score a memory's importance from 1-10."""
    score_prompt = f"""
    Rate the importance of this memory on a scale of 1-10.
    Consider: Is this a key finding? A critical decision?
    A routine action?

    Memory: {memory_content}

    Respond with just a number (1-10).
    """
    score = int(llm_call(score_prompt).strip())
    return score
```

---

## 5.7 Memory in Multi-Agent Systems

In multi-agent systems, memory can be:

| Type | Description | Use Case |
|------|-------------|----------|
| **Private** | Each agent has its own memory | Personal reflections |
| **Shared** | All agents access the same memory | Collaborative research |
| **Selective** | Agents share specific memories | Need-to-know basis |

### In our Hands-On Project

```
┌──────────────────────────────────────┐
│          SHARED MEMORY               │
│  ┌─────────────┐ ┌────────────────┐ │
│  │  Semantic    │ │   Episodic     │ │
│  │  (Papers &   │ │   (Interaction │ │
│  │   Findings)  │ │    History)    │ │
│  └──────┬───────┘ └───────┬────────┘ │
│         │                 │          │
└─────────┼─────────────────┼──────────┘
     ┌────┴────┐       ┌────┴────┐
     │Researcher│       │ Writer  │
     │  Agent   │       │ Agent   │
     └─────────┘       └─────────┘
     
Researcher stores papers → Writer retrieves to write summaries
```

---

## 🔑 Key Takeaways

1. Agents need **multiple types** of memory, just like humans
2. **Short-term memory** = context window (simple but limited)
3. **Episodic memory** = event log (what happened, what was learned)
4. **Semantic memory** = vector-based retrieval (what the agent knows)
5. **RAG** bridges retrieval and generation for grounded responses
6. Memory can be **private, shared, or selective** in multi-agent systems

---

*← [Module 4](04-multi-agent-coordination.md) | [Module 6 →](06-safety-alignment-interpretability.md)*
