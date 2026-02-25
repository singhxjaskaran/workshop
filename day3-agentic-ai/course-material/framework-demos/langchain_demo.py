#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║   LANGCHAIN ReAct AGENT DEMO — Module 3 Framework Showcase  ║
╚══════════════════════════════════════════════════════════════╝

Demonstrates the LangChain / ReAct agent pattern:
  - An LLM-powered agent that REASONS about what to do, then ACTS using tools
  - The Thought → Action → Observation loop repeats until the task is solved

This demo simulates the full ReAct loop without requiring an API key,
so you can see exactly how LangChain agents work under the hood.

Usage:
    python langchain_demo.py
"""

import time
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.tree import Tree
from rich import box

console = Console()

# ============================================================
# SIMULATED TOOLS (what a LangChain agent would use)
# ============================================================

TOOLS = {
    "search": {
        "name": "search",
        "description": "Search the web for information on a topic",
    },
    "calculator": {
        "name": "calculator",
        "description": "Perform mathematical calculations",
    },
    "wikipedia": {
        "name": "wikipedia",
        "description": "Look up information on Wikipedia",
    },
}

# Pre-scripted ReAct trace for the demo
REACT_TRACE = [
    {
        "step": 1,
        "thought": "I need to find out which country has the tallest building in the world in 2024. Let me search for this information.",
        "action": "search",
        "action_input": "tallest building in the world 2024",
        "observation": "The Burj Khalifa in Dubai, United Arab Emirates (UAE) remains the tallest building in the world at 828 meters (2,717 feet). It was completed in 2010.",
    },
    {
        "step": 2,
        "thought": "Now I know the tallest building is the Burj Khalifa in the UAE. I need to find the GDP of the UAE in 2024.",
        "action": "search",
        "action_input": "UAE GDP 2024",
        "observation": "The UAE's GDP in 2024 is approximately $509 billion USD, making it the 35th largest economy in the world. The GDP per capita is approximately $53,708 USD.",
    },
    {
        "step": 3,
        "thought": "Now let me calculate the GDP per capita as a percentage of the US GDP per capita for comparison.",
        "action": "calculator",
        "action_input": "(53708 / 80035) * 100",
        "observation": "67.1% — UAE's GDP per capita is about 67.1% of the US GDP per capita.",
    },
    {
        "step": 4,
        "thought": "I now have all the information needed to provide a comprehensive answer. The Burj Khalifa is in the UAE, which has a GDP of ~$509 billion.",
        "action": None,
        "action_input": None,
        "observation": None,
        "final_answer": (
            "The country with the tallest building in the world is the **United Arab Emirates (UAE)**, "
            "home to the **Burj Khalifa** (828m). The UAE's GDP in 2024 is approximately **$509 billion USD**, "
            "ranking 35th globally, with a GDP per capita of ~$53,708 (about 67.1% of the US GDP per capita)."
        ),
    },
]


def print_architecture():
    """Print the LangChain ReAct agent architecture visually."""
    console.print()
    console.print(Panel(
        Text.from_markup(
            "[bold cyan]LangChain ReAct Agent Architecture[/bold cyan]\n\n"
            "  ┌─────────────────────────────────────────────────────┐\n"
            "  │                  [bold yellow]USER QUERY[/bold yellow]                       │\n"
            "  │   \"What is the GDP of the country with the          │\n"
            "  │    tallest building?\"                               │\n"
            "  └────────────────────┬────────────────────────────────┘\n"
            "                       │\n"
            "                       ▼\n"
            "  ┌─────────────────────────────────────────────────────┐\n"
            "  │              [bold green]LLM (ReAct Agent)[/bold green]                    │\n"
            "  │                                                     │\n"
            "  │   ┌───────────┐    ┌───────────┐    ┌───────────┐  │\n"
            "  │   │ [blue]THOUGHT[/blue]   │───►│  [yellow]ACTION[/yellow]   │───►│[magenta]OBSERVATION[/magenta]│  │\n"
            "  │   │(Reasoning)│    │(Tool Call)│    │ (Result)  │  │\n"
            "  │   └───────────┘    └─────┬─────┘    └─────┬─────┘  │\n"
            "  │         ▲                │                │        │\n"
            "  │         └────────────────┼────────────────┘        │\n"
            "  │              Loop until done                       │\n"
            "  └──────────────────────┬──────────────────────────────┘\n"
            "                        │\n"
            "         ┌──────────────┼──────────────┐\n"
            "         ▼              ▼              ▼\n"
            "  ┌────────────┐ ┌────────────┐ ┌────────────┐\n"
            "  │  [green]🔍 Search[/green] │ │ [green]🔢 Calc[/green]    │ │ [green]📚 Wiki[/green]   │\n"
            "  │   Tool     │ │   Tool     │ │   Tool     │\n"
            "  └────────────┘ └────────────┘ └────────────┘\n"
        ),
        title="[bold]🏗️  Architecture Diagram[/bold]",
        border_style="cyan",
        padding=(1, 2),
    ))


def print_tools():
    """Print available tools in a table."""
    table = Table(title="🔧 Available Tools", box=box.ROUNDED, border_style="green")
    table.add_column("#", style="dim", width=3)
    table.add_column("Tool", style="cyan bold")
    table.add_column("Description", style="white")

    for i, (name, tool) in enumerate(TOOLS.items(), 1):
        table.add_row(str(i), name, tool["description"])

    console.print(table)


def run_react_demo():
    """Run the full ReAct demo with animated output."""

    # Banner
    console.print(Panel(
        "[bold cyan]🔗 LangChain ReAct Agent Demo[/bold cyan]\n\n"
        "[dim]This demo simulates a LangChain agent using the ReAct pattern.[/dim]\n"
        "[dim]The agent THINKS, ACTS (uses tools), and OBSERVES in a loop.[/dim]",
        title="[bold]Module 3 — Framework Demo 1/2[/bold]",
        border_style="bright_cyan",
        padding=(1, 2),
    ))

    # Show architecture
    print_architecture()
    time.sleep(1)

    # Show tools
    print_tools()
    console.print()
    time.sleep(0.5)

    # Show the question
    question = "What is the GDP of the country with the tallest building in the world?"
    console.print(Panel(
        f"[bold white]{question}[/bold white]",
        title="❓ User Question",
        border_style="yellow",
    ))
    console.print()
    time.sleep(1)

    # Run the ReAct loop
    console.print("[bold]━━━ ReAct Loop Begins ━━━[/bold]\n")

    for step in REACT_TRACE:
        step_num = step["step"]

        # --- THOUGHT ---
        console.print(f"[bold blue]💭 Thought {step_num}:[/bold blue]")
        # Simulate typing
        for char in step["thought"]:
            console.print(char, end="", highlight=False)
            time.sleep(0.008)
        console.print("\n")
        time.sleep(0.5)

        if step["action"] is None:
            # Final answer
            console.print("[bold green]✅ Final Answer:[/bold green]")
            console.print(Panel(
                Markdown(step["final_answer"]),
                border_style="green",
            ))
            break

        # --- ACTION ---
        console.print(
            f"[bold yellow]⚡ Action {step_num}:[/bold yellow] "
            f"[cyan]{step['action']}[/cyan](\"{step['action_input']}\")"
        )
        time.sleep(0.3)

        # Simulate tool execution
        console.print("[dim]   ⏳ Executing tool...[/dim]", end="")
        time.sleep(1.0)
        console.print(" [green]done[/green]")

        # --- OBSERVATION ---
        console.print(f"[bold magenta]👁️  Observation {step_num}:[/bold magenta]")
        console.print(f"   [dim]{step['observation']}[/dim]")
        console.print()
        time.sleep(0.8)

        # Visual separator
        console.print(f"[dim]{'─' * 60}[/dim]")
        console.print()

    # Summary
    console.print()
    console.print("[bold]━━━ ReAct Loop Complete ━━━[/bold]\n")

    # Show the trace summary
    trace_table = Table(title="📊 Agent Trace Summary", box=box.ROUNDED)
    trace_table.add_column("Step", style="bold", width=5)
    trace_table.add_column("Type", width=12)
    trace_table.add_column("Detail", max_width=50)

    for step in REACT_TRACE:
        n = str(step["step"])
        trace_table.add_row(n, "[blue]Thought[/blue]", step["thought"][:50] + "...")
        if step["action"]:
            trace_table.add_row(
                "", "[yellow]Action[/yellow]",
                f"{step['action']}(\"{step['action_input']}\")"
            )
            trace_table.add_row(
                "", "[magenta]Observation[/magenta]",
                step["observation"][:50] + "..."
            )
        else:
            trace_table.add_row("", "[green]Answer[/green]", step["final_answer"][:50] + "...")

    console.print(trace_table)

    # Show equivalent LangChain code
    console.print()
    console.print(Panel(
        Text.from_markup(
            "[bold]Equivalent LangChain Code:[/bold]\n\n"
            "[green]from[/green] langchain.agents [green]import[/green] create_react_agent, AgentExecutor\n"
            "[green]from[/green] langchain_openai [green]import[/green] ChatOpenAI\n"
            "[green]from[/green] langchain.tools [green]import[/green] Tool\n\n"
            "[dim]# Define tools[/dim]\n"
            "tools = [search_tool, calculator_tool, wiki_tool]\n\n"
            "[dim]# Create the ReAct agent[/dim]\n"
            "llm = ChatOpenAI(model=[cyan]\"gpt-4\"[/cyan])\n"
            "agent = create_react_agent(llm, tools, prompt)\n"
            "executor = AgentExecutor(agent=agent, tools=tools, verbose=[cyan]True[/cyan])\n\n"
            "[dim]# Run it[/dim]\n"
            "result = executor.invoke({[cyan]\"input\"[/cyan]: question})\n"
        ),
        title="💻 LangChain Implementation",
        border_style="green",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    run_react_demo()
