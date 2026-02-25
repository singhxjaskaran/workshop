"""
Memory systems for the Multi-Agent Research Assistant.

Implements three types of agent memory:
1. ShortTermMemory  — sliding-window context (recent messages)
2. EpisodicMemory   — timestamped event log (what happened)
3. SemanticMemory   — vector-based retrieval (what the agent knows)
"""

import json
from datetime import datetime
from typing import Optional


# ============================================================
# SHORT-TERM MEMORY
# ============================================================

class ShortTermMemory:
    """
    Maintains recent messages/context within a fixed window.

    This mirrors the LLM's context window — oldest messages are
    dropped when the buffer is full.
    """

    def __init__(self, max_messages: int = 20):
        self.messages: list[dict] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        """Add a message to short-term memory."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Sliding window: keep only the most recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> list[dict]:
        """Get all messages in the current context window."""
        return self.messages

    def get_formatted(self) -> str:
        """Get messages formatted as a string for prompts."""
        lines = []
        for msg in self.messages:
            lines.append(f"[{msg['role']}]: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        """Clear all short-term memory."""
        self.messages = []

    def __len__(self):
        return len(self.messages)

    def __repr__(self):
        return f"ShortTermMemory({len(self.messages)}/{self.max_messages} messages)"


# ============================================================
# EPISODIC MEMORY
# ============================================================

class EpisodicMemory:
    """
    Stores timestamped events and interactions — like a diary.

    Each episode records what the agent did, what it observed,
    and what it learned (reflections).
    """

    def __init__(self):
        self.episodes: list[dict] = []

    def record(self, event_type: str, content: str,
               agent_name: str = "", metadata: Optional[dict] = None):
        """
        Record an event in episodic memory.

        Args:
            event_type: One of "action", "observation", "reflection", "plan"
            content: Description of the event
            agent_name: Name of the agent that created this episode
            metadata: Additional structured data
        """
        episode = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "agent": agent_name,
            "content": content,
            "metadata": metadata or {}
        }
        self.episodes.append(episode)

    def get_recent(self, n: int = 10) -> list[dict]:
        """Get the N most recent episodes."""
        return self.episodes[-n:]

    def get_by_agent(self, agent_name: str) -> list[dict]:
        """Get all episodes from a specific agent."""
        return [e for e in self.episodes if e["agent"] == agent_name]

    def get_by_type(self, event_type: str) -> list[dict]:
        """Get all episodes of a specific type."""
        return [e for e in self.episodes if e["type"] == event_type]

    def get_reflections(self) -> list[dict]:
        """Get all reflection episodes (lessons learned)."""
        return self.get_by_type("reflection")

    def get_plans(self) -> list[dict]:
        """Get all planning episodes."""
        return self.get_by_type("plan")

    def summarize(self, max_episodes: int = 20) -> str:
        """Generate a human-readable summary of recent episodes."""
        if not self.episodes:
            return "No episodes recorded yet."

        recent = self.episodes[-max_episodes:]
        lines = []
        for ep in recent:
            agent_tag = f" ({ep['agent']})" if ep['agent'] else ""
            content_preview = ep['content'][:120]
            lines.append(
                f"  [{ep['timestamp'][:16]}] "
                f"{ep['type'].upper()}{agent_tag}: {content_preview}"
            )
        return "\n".join(lines)

    def to_json(self) -> str:
        """Export all episodes as JSON."""
        return json.dumps(self.episodes, indent=2)

    def __len__(self):
        return len(self.episodes)

    def __repr__(self):
        return f"EpisodicMemory({len(self.episodes)} episodes)"


# ============================================================
# SEMANTIC MEMORY (Vector-Based Retrieval)
# ============================================================

class SemanticMemory:
    """
    Vector-based semantic memory for similarity-based retrieval.

    In live mode, uses ChromaDB with sentence transformers.
    In demo mode, uses a simple keyword-based fallback.
    """

    def __init__(self, collection_name: str = "research_memory",
                 use_vectors: bool = False):
        """
        Initialize semantic memory.

        Args:
            collection_name: Name for the ChromaDB collection
            use_vectors: If True, use ChromaDB. If False, use simple keyword search.
        """
        self.collection_name = collection_name
        self.use_vectors = use_vectors
        self._documents: list[dict] = []  # Fallback storage
        self._collection = None

        if use_vectors:
            try:
                import chromadb
                self._client = chromadb.Client()
                self._collection = self._client.get_or_create_collection(
                    name=collection_name
                )
                print(f"  📦 Semantic memory initialized (ChromaDB: {collection_name})")
            except ImportError:
                print("  ⚠️ ChromaDB not installed. Using keyword-based fallback.")
                self.use_vectors = False
        else:
            print(f"  📦 Semantic memory initialized (keyword-based)")

    def store(self, text: str, metadata: Optional[dict] = None,
              doc_id: Optional[str] = None):
        """
        Store a piece of knowledge in semantic memory.

        Args:
            text: The text/knowledge to store
            metadata: Optional metadata dict
            doc_id: Optional unique identifier
        """
        doc_id = doc_id or f"doc_{len(self._documents)}"

        if self.use_vectors and self._collection is not None:
            self._collection.add(
                documents=[text],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
        else:
            self._documents.append({
                "id": doc_id,
                "text": text,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            })

    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """
        Retrieve the most relevant documents for a query.

        Args:
            query: The search query
            top_k: Number of results to return

        Returns:
            List of relevant document strings
        """
        if self.use_vectors and self._collection is not None:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(top_k, self._collection.count() or 1)
            )
            return results["documents"][0] if results["documents"] else []
        else:
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> list[str]:
        """Simple keyword-based fallback search."""
        if not self._documents:
            return []

        query_words = set(query.lower().split())
        scored = []

        for doc in self._documents:
            doc_words = set(doc["text"].lower().split())
            overlap = len(query_words & doc_words)
            scored.append((overlap, doc["text"]))

        # Sort by relevance (overlap count), descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored[:top_k]]

    def get_all(self) -> list[str]:
        """Get all stored documents."""
        if self.use_vectors and self._collection is not None:
            results = self._collection.get()
            return results["documents"] if results["documents"] else []
        return [doc["text"] for doc in self._documents]

    def count(self) -> int:
        """Get the number of stored documents."""
        if self.use_vectors and self._collection is not None:
            return self._collection.count()
        return len(self._documents)

    def __repr__(self):
        mode = "vector" if self.use_vectors else "keyword"
        return f"SemanticMemory({self.count()} docs, mode={mode})"


# ============================================================
# UNIFIED MEMORY MANAGER
# ============================================================

class AgentMemoryManager:
    """
    Unified memory manager that coordinates all three memory types.

    This is the main interface agents use to interact with memory.
    """

    def __init__(self, use_vectors: bool = False):
        self.short_term = ShortTermMemory(max_messages=20)
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory(use_vectors=use_vectors)

    def record_action(self, agent: str, action: str, result: str):
        """Record an agent action and its result."""
        self.short_term.add(agent, f"{action} → {result[:200]}")
        self.episodic.record("action", action, agent_name=agent)
        self.episodic.record("observation", result[:500], agent_name=agent)

    def record_finding(self, agent: str, finding: str):
        """Store a research finding in semantic memory."""
        self.semantic.store(finding, metadata={"agent": agent})
        self.episodic.record("observation", finding[:200], agent_name=agent)

    def record_reflection(self, agent: str, reflection: str):
        """Store a reflection / lesson learned."""
        self.episodic.record("reflection", reflection, agent_name=agent)

    def record_plan(self, agent: str, plan: str):
        """Store a plan."""
        self.episodic.record("plan", plan, agent_name=agent)

    def get_context_for_agent(self, query: str = "") -> str:
        """
        Build a context string for an agent, combining all memory types.
        """
        parts = []

        # Recent activity
        recent = self.episodic.get_recent(5)
        if recent:
            parts.append("## Recent Activity")
            for ep in recent:
                parts.append(f"- [{ep['type']}] {ep['content'][:100]}")

        # Relevant knowledge
        if query:
            relevant = self.semantic.retrieve(query, top_k=3)
            if relevant:
                parts.append("\n## Relevant Knowledge")
                for doc in relevant:
                    parts.append(f"- {doc[:150]}")

        return "\n".join(parts) if parts else "No prior context available."

    def get_summary(self) -> str:
        """Get a summary of all memory contents."""
        return (
            f"Memory Status:\n"
            f"  Short-term: {self.short_term}\n"
            f"  Episodic: {self.episodic}\n"
            f"  Semantic: {self.semantic}\n"
        )
