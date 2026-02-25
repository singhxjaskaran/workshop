"""
Agent definitions for the Multi-Agent Research Assistant.

Defines three specialized agents:
1. Planner Agent  — Plans the literature review strategy
2. Researcher Agent — Searches for and analyzes papers
3. Writer Agent   — Synthesizes findings into a summary
"""

from config import Config


# ============================================================
# AGENT DEFINITIONS (used by both CrewAI and demo modes)
# ============================================================

AGENT_DEFINITIONS = {
    "planner": {
        "role": "Research Planner",
        "goal": (
            "Create a comprehensive, structured research plan that identifies "
            "key sub-topics, relevant search queries, and a systematic approach "
            "to reviewing the literature on the given topic."
        ),
        "backstory": (
            "You are a senior academic researcher with 15+ years of experience "
            "in conducting systematic literature reviews. You excel at breaking "
            "down broad research topics into focused, searchable sub-topics. "
            "You understand how to identify seminal papers, current trends, "
            "and research gaps. Your plans are thorough yet focused."
        ),
    },
    "researcher": {
        "role": "Literature Researcher",
        "goal": (
            "Execute the research plan by searching for and analyzing relevant "
            "academic papers. Extract key findings, methodologies, and contributions "
            "from each paper. Organize findings by theme."
        ),
        "backstory": (
            "You are a meticulous research analyst who specializes in finding "
            "and extracting information from academic papers. You have experience "
            "with major academic databases and know how to evaluate paper quality, "
            "identify key contributions, and cross-reference findings. You always "
            "cite your sources accurately."
        ),
    },
    "writer": {
        "role": "Research Summary Writer",
        "goal": (
            "Synthesize the research findings into a clear, well-structured "
            "literature review summary. The summary should be comprehensive "
            "yet accessible, highlighting key themes, methodologies, findings, "
            "and research gaps."
        ),
        "backstory": (
            "You are a skilled academic writer who transforms complex research "
            "findings into clear, engaging narratives. You have written numerous "
            "literature reviews and survey papers. You excel at identifying "
            "common threads, contrasting different approaches, and providing "
            "a balanced synthesis of the current state of research."
        ),
    }
}


def create_crewai_agents(tools_list=None):
    """
    Create CrewAI Agent instances.

    Args:
        tools_list: Optional list of CrewAI tool objects

    Returns:
        Tuple of (planner, researcher, writer) Agent instances
    """
    from crewai import Agent

    planner = Agent(
        role=AGENT_DEFINITIONS["planner"]["role"],
        goal=AGENT_DEFINITIONS["planner"]["goal"],
        backstory=AGENT_DEFINITIONS["planner"]["backstory"],
        verbose=Config.VERBOSE,
        allow_delegation=False,
        max_iter=Config.MAX_ITERATIONS,
    )

    researcher = Agent(
        role=AGENT_DEFINITIONS["researcher"]["role"],
        goal=AGENT_DEFINITIONS["researcher"]["goal"],
        backstory=AGENT_DEFINITIONS["researcher"]["backstory"],
        verbose=Config.VERBOSE,
        tools=tools_list or [],
        allow_delegation=False,
        max_iter=Config.MAX_ITERATIONS,
    )

    writer = Agent(
        role=AGENT_DEFINITIONS["writer"]["role"],
        goal=AGENT_DEFINITIONS["writer"]["goal"],
        backstory=AGENT_DEFINITIONS["writer"]["backstory"],
        verbose=Config.VERBOSE,
        allow_delegation=False,
        max_iter=Config.MAX_ITERATIONS,
    )

    return planner, researcher, writer


def create_demo_agents():
    """
    Create lightweight agent wrappers for demo mode (no CrewAI needed).

    Returns:
        Tuple of (planner, researcher, writer) DemoAgent instances
    """
    return (
        DemoAgent(**AGENT_DEFINITIONS["planner"]),
        DemoAgent(**AGENT_DEFINITIONS["researcher"]),
        DemoAgent(**AGENT_DEFINITIONS["writer"]),
    )


class DemoAgent:
    """
    Lightweight agent for demo mode — simulates agent behavior
    without requiring an LLM API.
    """

    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory

    def __repr__(self):
        return f"DemoAgent(role='{self.role}')"
