#!/usr/bin/env python3
"""
Multi-Agent Research Assistant — Main Entry Point

A multi-agent system where three specialized AI agents collaboratively
plan, research, and write literature review summaries.

Usage:
    # Live mode (requires OPENAI_API_KEY in .env)
    python main.py "transformer architectures in NLP"

    # Demo mode (no API key needed)
    python main.py --demo "transformer architectures in NLP"

    # Interactive mode (prompts for topic)
    python main.py --demo
"""

import sys
import argparse
from rich.console import Console
from rich.panel import Panel

from config import Config

console = Console()


def main():
    """Main entry point for the research assistant."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research Assistant — "
                    "Collaboratively plan, research, and write literature reviews.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --demo "transformer architectures"
  python main.py "agentic AI systems"
  python main.py --demo --verbose
        """
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="Research topic to investigate"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode (no API key required)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Show detailed agent reasoning (default: True)"
    )

    args = parser.parse_args()

    # ---- Banner ----
    console.print(Panel(
        "[bold cyan]🤖 Multi-Agent Research Assistant[/bold cyan]\n"
        "[dim]Day 3 Workshop — Agentic AI: From LLMs to Autonomous Agents[/dim]\n\n"
        "[dim]Three agents collaborate to produce a literature review:[/dim]\n"
        "  📋 [blue]Planner[/blue]    → Creates research strategy\n"
        "  🔍 [green]Researcher[/green] → Finds and analyzes papers\n"
        "  ✍️  [yellow]Writer[/yellow]     → Synthesizes into a review",
        title="[bold]Workshop Hands-On Project[/bold]",
        border_style="bright_blue",
        padding=(1, 2)
    ))

    # ---- Configuration ----
    if args.demo:
        Config.set_demo_mode(True)
    Config.VERBOSE = args.verbose
    Config.validate()

    # ---- Get topic ----
    topic = args.topic
    if not topic:
        console.print("\n[bold]Enter your research topic:[/bold]")
        topic = input("  > ").strip()
        if not topic:
            topic = "transformer architectures in natural language processing"
            console.print(f"  [dim]Using default topic: {topic}[/dim]")

    console.print(f"\n[bold]Research Topic:[/bold] [cyan]{topic}[/cyan]\n")

    # ---- Run the crew ----
    from crew import run_crew

    try:
        result = run_crew(topic)

        # ---- Final output ----
        console.print(f"\n{'='*60}")
        console.print(Panel(
            "[bold green]✅ Research Complete![/bold green]\n\n"
            "The multi-agent crew has finished their work.\n"
            "Check the [cyan]demo_output/[/cyan] folder for saved results.",
            title="Done",
            border_style="green"
        ))

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        console.print("[dim]Try running with --demo flag for demo mode.[/dim]")
        raise


if __name__ == "__main__":
    main()
