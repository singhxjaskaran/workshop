"""
Crew Orchestrator for the Multi-Agent Research Assistant.

Creates and runs the multi-agent crew using either:
- CrewAI (live mode with API key)
- Demo mode (simulated pipeline without API key)
"""

import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Config
from memory import AgentMemoryManager

console = Console()


def run_crew(topic: str) -> str:
    """
    Run the multi-agent research crew on a given topic.

    Args:
        topic: The research topic to investigate

    Returns:
        The final literature review summary as a string
    """
    if Config.DEMO_MODE:
        return _run_demo_crew(topic)
    else:
        return _run_crewai_crew(topic)


# ============================================================
# CREWAI MODE (Live — requires API key)
# ============================================================

def _run_crewai_crew(topic: str) -> str:
    """Run the research pipeline using CrewAI framework."""
    from crewai import Crew, Process
    from crewai.tools import tool as crewai_tool
    from agents import create_crewai_agents
    from tasks import create_crewai_tasks
    from tools import search_papers, read_paper, save_findings

    console.print(Panel(
        f"[bold cyan]🚀 Starting Multi-Agent Research Crew[/bold cyan]\n"
        f"Topic: [yellow]{topic}[/yellow]\n"
        f"Mode: [green]Live (CrewAI + {Config.OPENAI_MODEL})[/green]",
        title="Research Assistant",
        border_style="cyan"
    ))

    # Wrap tools for CrewAI
    @crewai_tool
    def tool_search_papers(query: str) -> str:
        """Search for academic papers on a given topic. Pass a search query string."""
        return search_papers(query)

    @crewai_tool
    def tool_read_paper(title: str) -> str:
        """Read and extract key information from a paper. Pass the paper title."""
        return read_paper(title)

    @crewai_tool
    def tool_save_findings(topic: str, findings: str) -> str:
        """Save research findings to a file. Pass the topic and findings text."""
        return save_findings(topic, findings)

    # Create agents with tools
    planner, researcher, writer = create_crewai_agents(
        tools_list=[tool_search_papers, tool_read_paper]
    )

    # Create tasks
    tasks = create_crewai_tasks(planner, researcher, writer, topic)

    # Assemble the crew
    crew = Crew(
        agents=[planner, researcher, writer],
        tasks=tasks,
        process=Process.sequential,
        verbose=Config.VERBOSE,
    )

    # Run the crew
    console.print("\n[bold]Starting research pipeline...[/bold]\n")
    result = crew.kickoff(inputs={"topic": topic})

    # Save the final output
    output_text = str(result)
    save_findings(topic, output_text)

    return output_text


# ============================================================
# DEMO MODE (Simulated — no API key required)
# ============================================================

def _run_demo_crew(topic: str) -> str:
    """Run a simulated research pipeline for demonstration."""
    from agents import create_demo_agents
    from tasks import DEMO_TASK_OUTPUTS
    from tools import search_papers, read_paper, save_findings

    # Initialize memory
    memory = AgentMemoryManager(use_vectors=False)

    console.print(Panel(
        f"[bold cyan]🎭 Starting Demo Research Crew[/bold cyan]\n"
        f"Topic: [yellow]{topic}[/yellow]\n"
        f"Mode: [magenta]Demo (simulated, no API needed)[/magenta]",
        title="Research Assistant",
        border_style="magenta"
    ))

    planner, researcher, writer = create_demo_agents()

    # ---- Step 1: Planning ----
    console.print(f"\n{'='*60}")
    console.print(Panel(
        f"[bold blue]📋 STEP 1: Research Planning[/bold blue]\n"
        f"Agent: [cyan]{planner.role}[/cyan]\n"
        f"Goal: {planner.goal[:80]}...",
        border_style="blue"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Planner agent creating research strategy...", total=None)
        time.sleep(1.5)  # Simulate thinking

    plan = DEMO_TASK_OUTPUTS["plan"].format(topic=topic)
    memory.record_plan(planner.role, plan)
    console.print(Markdown(plan))

    # ---- Step 2: Research ----
    console.print(f"\n{'='*60}")
    console.print(Panel(
        f"[bold green]🔍 STEP 2: Literature Research[/bold green]\n"
        f"Agent: [cyan]{researcher.role}[/cyan]\n"
        f"Goal: {researcher.goal[:80]}...",
        border_style="green"
    ))

    # Simulate tool usage
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching for papers...", total=None)
        time.sleep(1.0)
    
    search_results = search_papers(topic, max_results=3)
    console.print(f"\n[dim]📄 Tool call: search_papers(\"{topic}\")[/dim]")
    console.print(f"[dim]   Found papers:[/dim]")

    import json
    papers = json.loads(search_results)
    papers_sections = {}
    for i, paper in enumerate(papers):
        console.print(f"[dim]   {i+1}. {paper['title']} ({paper['year']})[/dim]")
        memory.record_finding(researcher.role, f"Found: {paper['title']}")

        # Read each paper
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Reading: {paper['title'][:50]}...", total=None)
            time.sleep(0.8)
        
        paper_details = read_paper(paper["title"])
        papers_sections[f"papers_section_{i+1}"] = (
            f"**{paper['title']}** ({paper['year']})\n"
            f"- Authors: {paper['authors']}\n"
            f"- Key contribution: Novel approach with significant impact\n"
            f"- Methodology: Systematic empirical evaluation\n"
            f"- Relevance: Directly addresses core aspects of {topic}"
        )

    # Fill in remaining sections if less than 3 papers
    for i in range(len(papers), 3):
        papers_sections[f"papers_section_{i+1}"] = (
            f"**Additional Paper {i+1}** (2023)\n"
            f"- Additional findings related to {topic}"
        )

    research_findings = DEMO_TASK_OUTPUTS["research"].format(
        topic=topic, **papers_sections
    )
    memory.record_action(researcher.role, "Completed research", research_findings[:200])
    console.print(Markdown(research_findings))

    # ---- Step 3: Writing ----
    console.print(f"\n{'='*60}")
    console.print(Panel(
        f"[bold yellow]✍️  STEP 3: Writing Literature Review[/bold yellow]\n"
        f"Agent: [cyan]{writer.role}[/cyan]\n"
        f"Goal: {writer.goal[:80]}...",
        border_style="yellow"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Writer agent synthesizing findings...", total=None)
        time.sleep(2.0)

    summary = DEMO_TASK_OUTPUTS["summary"].format(topic=topic)
    memory.record_action(writer.role, "Wrote literature review", summary[:200])

    console.print(Markdown(summary))

    # ---- Save output ----
    save_result = save_findings(topic, summary)
    console.print(f"\n[green]{save_result}[/green]")

    # ---- Memory Summary ----
    console.print(f"\n{'='*60}")
    console.print(Panel(
        f"[bold]📊 Memory Summary[/bold]\n\n{memory.get_summary()}\n"
        f"[bold]Episodic Timeline:[/bold]\n{memory.episodic.summarize()}",
        title="Agent Memory State",
        border_style="dim"
    ))

    return summary
