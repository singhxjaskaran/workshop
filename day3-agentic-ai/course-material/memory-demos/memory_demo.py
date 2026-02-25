#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   AGENT MEMORY ARCHITECTURE DEMO — Module 5 Live Showcase   ║
╚══════════════════════════════════════════════════════════════╝

Demonstrates all three memory types using real OpenAI API calls:

  1. SHORT-TERM MEMORY  — Sliding conversation window
  2. EPISODIC MEMORY    — Timestamped event log with recall
  3. SEMANTIC MEMORY    — Vector embeddings (ChromaDB) with retrieval

Each section shows how memory impacts agent behavior in real-time.

Usage:
    python memory_demo.py
"""

import os
import time
import json
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich import box

load_dotenv()

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def llm_call(messages: list, temperature: float = 0.7, max_tokens: int = 300) -> str:
    """Make a real OpenAI API call."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


# ============================================================
# 1. SHORT-TERM MEMORY (Sliding Window)
# ============================================================

class ShortTermMemory:
    """
    Sliding-window memory that keeps only the last N messages.
    This simulates a context window — oldest messages get dropped.
    """

    def __init__(self, max_messages: int = 6):
        self.messages: list[dict] = []
        self.max_messages = max_messages
        self.dropped_count = 0

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Enforce sliding window
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)
            self.dropped_count += 1

    def get_messages(self) -> list[dict]:
        return list(self.messages)

    def stats(self) -> str:
        return f"{len(self.messages)}/{self.max_messages} messages (dropped: {self.dropped_count})"


def demo_short_term_memory():
    """Demonstrate how short-term memory affects conversation continuity."""
    console.print(Panel(
        "[bold blue]🧠 DEMO 1: Short-Term Memory (Sliding Window)[/bold blue]\n\n"
        "[dim]The agent remembers only the last 6 messages.\n"
        "Watch what happens when early context gets dropped![/dim]",
        title="Module 5 — Memory Type 1/3",
        border_style="blue",
        padding=(1, 2),
    ))
    time.sleep(1)

    stm = ShortTermMemory(max_messages=6)
    system_msg = {
        "role": "system",
        "content": (
            "You are a helpful AI assistant. Answer concisely in 1-2 sentences. "
            "If you don't remember something from earlier in the conversation, say so honestly."
        )
    }

    # Conversation sequence designed to show memory loss
    questions = [
        "My name is Dr. Sarah Chen and I'm a professor at MIT.",
        "I'm researching transformer architectures for protein folding.",
        "My latest paper was published in Nature last month.",
        "What programming languages are best for deep learning?",
        "Can you recommend some datasets for protein structure prediction?",
        "What was my name and what university am I from?",  # Tests if early context survived
    ]

    console.print("\n[bold]Conversation with a 6-message sliding window:[/bold]\n")

    for i, question in enumerate(questions):
        # Show what we're sending
        console.print(f"[bold cyan]👤 User (Turn {i+1}):[/bold cyan] {question}")
        stm.add("user", question)

        # Build messages for API call
        api_messages = [system_msg] + stm.get_messages()

        # Call OpenAI
        console.print("[dim]   ⏳ Thinking...[/dim]", end="")
        response = llm_call(api_messages)
        console.print(" [green]done[/green]")

        stm.add("assistant", response)
        console.print(f"[bold green]🤖 Agent:[/bold green] {response}")

        # Show memory state
        console.print(f"[dim]   📊 Memory: {stm.stats()}[/dim]\n")
        time.sleep(0.5)

    # Show the memory window contents
    console.print(Panel(
        "\n".join([
            f"[{'cyan' if m['role']=='user' else 'green'}]"
            f"{'👤' if m['role']=='user' else '🤖'} {m['role']}: "
            f"{m['content'][:80]}{'...' if len(m['content'])>80 else ''}[/]"
            for m in stm.get_messages()
        ]),
        title="📦 Final Memory Window Contents",
        border_style="dim",
    ))

    console.print(Panel(
        "[bold]Key Takeaway:[/bold]\n"
        "Short-term memory is like a human's working memory — limited capacity.\n"
        "Early context (name, affiliation) may be lost once the window slides.\n"
        "This is why agents need EPISODIC and SEMANTIC memory for persistence!",
        border_style="blue",
    ))


# ============================================================
# 2. EPISODIC MEMORY (Event Log)
# ============================================================

class EpisodicMemory:
    """
    Stores timestamped events — an agent's 'autobiography'.
    Supports filtering by type and time-based recall.
    """

    def __init__(self):
        self.episodes: list[dict] = []

    def record(self, event_type: str, agent: str, content: str, metadata: dict = None):
        self.episodes.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "agent": agent,
            "content": content,
            "metadata": metadata or {},
        })

    def recall(self, event_type: str = None, last_n: int = None) -> list[dict]:
        results = self.episodes
        if event_type:
            results = [e for e in results if e["type"] == event_type]
        if last_n:
            results = results[-last_n:]
        return results

    def summarize_for_llm(self) -> str:
        """Format episodes as context for an LLM."""
        lines = []
        for ep in self.episodes:
            ts = ep["timestamp"].split("T")[1][:8]
            lines.append(f"[{ts}] {ep['type'].upper()} ({ep['agent']}): {ep['content'][:100]}")
        return "\n".join(lines)

    def stats(self) -> str:
        types = {}
        for ep in self.episodes:
            types[ep["type"]] = types.get(ep["type"], 0) + 1
        parts = [f"{t}: {c}" for t, c in types.items()]
        return f"{len(self.episodes)} episodes ({', '.join(parts)})"


def demo_episodic_memory():
    """Demonstrate episodic memory — agent reflects on its own history."""
    console.print(Panel(
        "[bold magenta]📓 DEMO 2: Episodic Memory (Event Log)[/bold magenta]\n\n"
        "[dim]The agent records every action it takes as timestamped events.\n"
        "Then it uses this 'autobiography' to reflect on its behavior![/dim]",
        title="Module 5 — Memory Type 2/3",
        border_style="magenta",
        padding=(1, 2),
    ))
    time.sleep(1)

    em = EpisodicMemory()

    # Simulate a research task with episodic logging
    console.print("\n[bold]Simulating a research agent with episodic memory...[/bold]\n")

    # Step 1: Planning
    console.print("[bold blue]📋 Step 1: Planning[/bold blue]")
    em.record("plan", "Planner", "Research plan created for 'AI agents in healthcare'")
    console.print("[dim]   → Recorded: PLAN event[/dim]")

    plan_prompt = [
        {"role": "system", "content": "You are a research planner. Create 3 specific search queries for the topic. Be concise."},
        {"role": "user", "content": "Create search queries for: AI agents in healthcare"}
    ]
    console.print("[dim]   ⏳ LLM generating plan...[/dim]", end="")
    plan = llm_call(plan_prompt)
    console.print(" [green]done[/green]")
    em.record("action", "Planner", f"Generated queries: {plan[:100]}")
    console.print(f"[green]   Plan: {plan[:120]}...[/green]\n")
    time.sleep(0.5)

    # Step 2: Research
    console.print("[bold green]🔍 Step 2: Research[/bold green]")
    topics_found = ["diagnostic AI agents", "drug discovery agents", "clinical trial optimization"]
    for topic in topics_found:
        em.record("observation", "Researcher", f"Found relevant area: {topic}")
        console.print(f"[dim]   → Recorded: OBSERVATION — {topic}[/dim]")
        time.sleep(0.3)

    em.record("action", "Researcher", "Analyzed 3 research areas with key findings")
    console.print()

    # Step 3: Error & Recovery
    console.print("[bold red]⚠️ Step 3: Error Encountered[/bold red]")
    em.record("error", "Researcher", "API rate limit hit — retrying after 2s delay")
    console.print("[dim]   → Recorded: ERROR event[/dim]")
    em.record("action", "Researcher", "Successfully retried after rate limit — results obtained")
    console.print("[dim]   → Recorded: RECOVERY action[/dim]\n")

    # Step 4: Writing
    console.print("[bold yellow]✍️ Step 4: Writing[/bold yellow]")
    em.record("action", "Writer", "Synthesized findings into summary")
    em.record("observation", "Writer", "Summary covers 3 areas with methodology comparison")
    console.print("[dim]   → Recorded: ACTION + OBSERVATION events[/dim]\n")

    # Show the episode log
    ep_table = Table(title="📓 Episodic Memory Log", box=box.ROUNDED, border_style="magenta")
    ep_table.add_column("Time", style="dim", width=10)
    ep_table.add_column("Type", width=12)
    ep_table.add_column("Agent", style="cyan", width=12)
    ep_table.add_column("Content", max_width=50)

    type_colors = {"plan": "blue", "action": "green", "observation": "yellow", "error": "red"}
    for ep in em.episodes:
        ts = ep["timestamp"].split("T")[1][:8]
        tcolor = type_colors.get(ep["type"], "white")
        ep_table.add_row(
            ts,
            f"[{tcolor}]{ep['type'].upper()}[/{tcolor}]",
            ep["agent"],
            ep["content"][:50] + ("..." if len(ep["content"]) > 50 else "")
        )
    console.print(ep_table)
    console.print(f"\n[dim]📊 Stats: {em.stats()}[/dim]\n")

    # Now ask the LLM to REFLECT on its own episodic memory
    console.print("[bold]🪞 Agent Self-Reflection (LLM reads its own episodic log):[/bold]\n")

    reflection_prompt = [
        {"role": "system", "content": (
            "You are an AI agent reviewing your own episodic memory log. "
            "Analyze what happened, what went well, what could be improved, "
            "and what you learned. Be specific and concise (3-4 sentences)."
        )},
        {"role": "user", "content": f"Here is your episodic memory:\n\n{em.summarize_for_llm()}\n\nReflect on your performance."}
    ]
    console.print("[dim]   ⏳ LLM reflecting on its own memory...[/dim]", end="")
    reflection = llm_call(reflection_prompt, max_tokens=200)
    console.print(" [green]done[/green]\n")

    console.print(Panel(
        Markdown(reflection),
        title="🪞 Agent Self-Reflection",
        border_style="magenta",
    ))

    console.print(Panel(
        "[bold]Key Takeaway:[/bold]\n"
        "Episodic memory gives agents an 'autobiography' — they can recall WHAT happened,\n"
        "WHEN it happened, and WHO did it. This enables self-reflection, error recovery,\n"
        "and learning from past mistakes. Unlike short-term memory, nothing is ever lost!",
        border_style="magenta",
    ))


# ============================================================
# 3. SEMANTIC MEMORY (Vector Embeddings + Retrieval)
# ============================================================

class SemanticMemory:
    """
    Stores knowledge as vector embeddings using ChromaDB.
    Supports similarity-based retrieval — finds related knowledge
    even when the exact words don't match.
    """

    def __init__(self, collection_name: str = "agent_knowledge"):
        import chromadb
        self.chroma = chromadb.Client()
        # Delete if exists for clean demo
        try:
            self.chroma.delete_collection(collection_name)
        except Exception:
            pass
        self.collection = self.chroma.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.doc_count = 0

    def store(self, text: str, metadata: dict = None):
        """Store a piece of knowledge as a vector embedding."""
        self.doc_count += 1
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"source": "agent"}],
            ids=[f"doc_{self.doc_count}"],
        )

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve the most similar stored knowledge."""
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.doc_count),
        )
        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "text": doc,
                "distance": results["distances"][0][i] if results["distances"] else None,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            })
        return output

    def stats(self) -> str:
        return f"{self.doc_count} documents stored"


def demo_semantic_memory():
    """Demonstrate semantic memory with real vector embeddings."""
    console.print(Panel(
        "[bold green]🧬 DEMO 3: Semantic Memory (Vector Embeddings)[/bold green]\n\n"
        "[dim]The agent stores knowledge as vector embeddings in ChromaDB.\n"
        "It can retrieve related information even with different wording![/dim]",
        title="Module 5 — Memory Type 3/3",
        border_style="green",
        padding=(1, 2),
    ))
    time.sleep(1)

    sm = SemanticMemory()

    # Store diverse knowledge pieces
    knowledge_base = [
        {"text": "Transformers use self-attention mechanisms to process sequences in parallel, unlike RNNs which process sequentially.", "source": "architecture"},
        {"text": "BERT uses bidirectional pre-training to understand context from both left and right sides of a token.", "source": "models"},
        {"text": "GPT-4 demonstrates emergent abilities like chain-of-thought reasoning that smaller models lack.", "source": "models"},
        {"text": "Retrieval-Augmented Generation (RAG) combines LLMs with external document retrieval for more factual outputs.", "source": "techniques"},
        {"text": "Fine-tuning adapts a pre-trained model to a specific task using a smaller, task-specific dataset.", "source": "training"},
        {"text": "LoRA (Low-Rank Adaptation) reduces the number of trainable parameters during fine-tuning by up to 10,000x.", "source": "efficiency"},
        {"text": "Prompt injection is a security vulnerability where malicious inputs trick an LLM into ignoring its system instructions.", "source": "safety"},
        {"text": "Constitutional AI trains models using a set of principles to self-critique and revise their own outputs.", "source": "alignment"},
        {"text": "Multi-agent systems coordinate multiple specialized AI agents to solve complex tasks collaboratively.", "source": "architecture"},
        {"text": "Vector databases like ChromaDB, Pinecone, and Weaviate store embeddings for fast similarity search.", "source": "infrastructure"},
    ]

    console.print("\n[bold]📥 Storing 10 knowledge fragments as vectors...[/bold]\n")
    for i, item in enumerate(knowledge_base):
        sm.store(item["text"], {"source": item["source"]})
        console.print(f"  [dim]{i+1}. [{item['source']}] {item['text'][:70]}...[/dim]")
        time.sleep(0.15)

    console.print(f"\n[green]✅ {sm.stats()}[/green]\n")
    time.sleep(0.5)

    # Now query with different phrasings — shows semantic similarity
    queries = [
        "How do attention mechanisms work in neural networks?",
        "What are the risks of AI language models?",
        "How can I make fine-tuning cheaper and faster?",
    ]

    for q_idx, query in enumerate(queries):
        console.print(f"[bold cyan]🔍 Query {q_idx+1}:[/bold cyan] \"{query}\"")
        console.print("[dim]   ⏳ Searching vector space...[/dim]", end="")
        results = sm.retrieve(query, top_k=3)
        console.print(" [green]done[/green]")

        result_table = Table(box=box.SIMPLE, border_style="dim", show_header=True)
        result_table.add_column("#", width=3)
        result_table.add_column("Similarity", width=10, style="green")
        result_table.add_column("Source", width=12, style="cyan")
        result_table.add_column("Retrieved Knowledge", max_width=60)

        for i, r in enumerate(results):
            similarity = f"{(1 - r['distance'])*100:.1f}%" if r["distance"] is not None else "—"
            result_table.add_row(
                str(i+1), similarity, r["metadata"].get("source", ""),
                r["text"][:80] + ("..." if len(r["text"]) > 80 else "")
            )

        console.print(result_table)

        # Ask LLM to answer using retrieved context
        context = "\n".join([f"- {r['text']}" for r in results])
        rag_prompt = [
            {"role": "system", "content": "Answer the question using ONLY the provided context. Be concise (2 sentences max). Cite which fact you used."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        console.print("[dim]   ⏳ LLM answering with retrieved context...[/dim]", end="")
        answer = llm_call(rag_prompt, max_tokens=150)
        console.print(" [green]done[/green]")
        console.print(f"  [bold green]🤖 Answer:[/bold green] {answer}\n")
        time.sleep(0.5)

    console.print(Panel(
        "[bold]Key Takeaway:[/bold]\n"
        "Semantic memory stores knowledge as vectors, enabling retrieval by MEANING,\n"
        "not just keywords. 'How do attention mechanisms work?' matches content about\n"
        "'self-attention' even without the exact words. This is the foundation of RAG!\n\n"
        "Combined with episodic + short-term memory, agents get a complete memory system.",
        border_style="green",
    ))


# ============================================================
# ARCHITECTURE VISUALIZATION
# ============================================================

def print_unified_architecture():
    """Show how all three memory types work together."""
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]Unified Agent Memory Architecture[/bold cyan]\n\n"
            "  ┌─────────────────────────────────────────────────────────────┐\n"
            "  │                     [bold white]AI AGENT[/bold white]                              │\n"
            "  │                                                             │\n"
            "  │   ┌───────────────────────────────────────────────────┐     │\n"
            "  │   │              [bold blue]SHORT-TERM MEMORY[/bold blue]                  │     │\n"
            "  │   │  Sliding window · Last N messages · Fast access   │     │\n"
            "  │   │  [dim]Like human working memory — limited capacity[/dim]    │     │\n"
            "  │   └───────────────────────────────────────────────────┘     │\n"
            "  │                         │                                   │\n"
            "  │   ┌───────────────────────────────────────────────────┐     │\n"
            "  │   │              [bold magenta]EPISODIC MEMORY[/bold magenta]                   │     │\n"
            "  │   │  Event log · Timestamped · Self-reflection       │     │\n"
            "  │   │  [dim]Like human autobiographical memory[/dim]             │     │\n"
            "  │   └───────────────────────────────────────────────────┘     │\n"
            "  │                         │                                   │\n"
            "  │   ┌───────────────────────────────────────────────────┐     │\n"
            "  │   │              [bold green]SEMANTIC MEMORY[/bold green]                    │     │\n"
            "  │   │  Vector DB · Similarity search · Persistent      │     │\n"
            "  │   │  [dim]Like human long-term knowledge store[/dim]           │     │\n"
            "  │   └──────────────────────┬────────────────────────────┘     │\n"
            "  │                          │                                  │\n"
            "  └──────────────────────────┼──────────────────────────────────┘\n"
            "                             │\n"
            "                    ┌────────┴────────┐\n"
            "                    │  [green]ChromaDB /[/green]      │\n"
            "                    │  [green]Pinecone /[/green]      │\n"
            "                    │  [green]Weaviate[/green]        │\n"
            "                    └─────────────────┘\n"
        ),
        title="[bold]🏗️  Memory Architecture Overview[/bold]",
        border_style="cyan",
        padding=(1, 2),
    ))


# ============================================================
# MAIN
# ============================================================

def main():
    console.print(Panel(
        "[bold cyan]🧠 Agent Memory Architecture — Live Demo[/bold cyan]\n\n"
        "[dim]Module 5: Three types of memory that make agents intelligent[/dim]\n\n"
        f"[dim]Using model: [cyan]{MODEL}[/cyan] | Mode: [green]Live (OpenAI API)[/green][/dim]",
        title="[bold]Workshop Hands-On — Module 5[/bold]",
        border_style="bright_cyan",
        padding=(1, 2),
    ))

    # Architecture overview
    print_unified_architecture()
    time.sleep(1)

    # Demo 1: Short-term memory
    console.print(f"\n{'='*60}\n")
    demo_short_term_memory()

    console.print(f"\n{'='*60}\n")
    input("[dim]Press Enter to continue to Episodic Memory demo...[/dim]")

    # Demo 2: Episodic memory
    console.print(f"\n{'='*60}\n")
    demo_episodic_memory()

    console.print(f"\n{'='*60}\n")
    input("[dim]Press Enter to continue to Semantic Memory demo...[/dim]")

    # Demo 3: Semantic memory
    console.print(f"\n{'='*60}\n")
    demo_semantic_memory()

    # Final summary
    console.print(f"\n{'='*60}\n")
    summary = Table(title="📊 Memory Types Summary", box=box.DOUBLE, border_style="cyan")
    summary.add_column("Memory Type", style="bold")
    summary.add_column("Capacity", width=15)
    summary.add_column("Persistence", width=15)
    summary.add_column("Retrieval", width=20)
    summary.add_column("Human Analogy", width=20)

    summary.add_row("[blue]Short-Term[/blue]", "Limited (N msgs)", "Session only", "Sequential", "Working memory")
    summary.add_row("[magenta]Episodic[/magenta]", "Unlimited", "Persistent", "By time/type", "Autobiographical")
    summary.add_row("[green]Semantic[/green]", "Unlimited", "Persistent", "By similarity", "Long-term knowledge")

    console.print(summary)

    console.print(Panel(
        "[bold green]✅ All three memory demos complete![/bold green]\n\n"
        "In production agents, these three systems work together:\n"
        "• [blue]Short-term[/blue] provides immediate context\n"
        "• [magenta]Episodic[/magenta] enables learning from experience\n"
        "• [green]Semantic[/green] provides persistent knowledge retrieval",
        title="Done",
        border_style="green",
    ))


if __name__ == "__main__":
    main()
