"""
Task definitions for the Multi-Agent Research Assistant.

Each task represents a unit of work assigned to a specific agent.
Tasks are executed sequentially: Plan → Research → Write.
"""

from config import Config


def create_crewai_tasks(planner_agent, researcher_agent, writer_agent, topic: str):
    """
    Create CrewAI Task instances for the research pipeline.

    Args:
        planner_agent: The Planner CrewAI Agent
        researcher_agent: The Researcher CrewAI Agent
        writer_agent: The Writer CrewAI Agent
        topic: The research topic string

    Returns:
        List of [plan_task, research_task, write_task]
    """
    from crewai import Task

    plan_task = Task(
        description=(
            f"Create a detailed research plan for the following topic:\n\n"
            f"**Topic:** {topic}\n\n"
            f"Your plan should include:\n"
            f"1. A clear definition of the research scope\n"
            f"2. 3-5 key sub-topics or research questions to investigate\n"
            f"3. Specific search queries to use for finding papers\n"
            f"4. Criteria for evaluating paper relevance and quality\n"
            f"5. An outline for the final literature review structure\n\n"
            f"Be specific and actionable — the Researcher agent will use "
            f"your plan to guide their paper search."
        ),
        agent=planner_agent,
        expected_output=(
            "A structured research plan in markdown format with: "
            "scope definition, sub-topics list, search queries, "
            "quality criteria, and review outline."
        ),
    )

    research_task = Task(
        description=(
            f"Execute the research plan to find and analyze relevant papers on: "
            f"**{topic}**\n\n"
            f"Based on the Planner's research plan, you should:\n"
            f"1. Use the search_papers tool to find relevant papers\n"
            f"2. Use the read_paper tool to extract details from key papers\n"
            f"3. For each paper, extract:\n"
            f"   - Title, authors, year\n"
            f"   - Key contributions and findings\n"
            f"   - Methodology used\n"
            f"   - Relevance to our topic\n"
            f"4. Organize findings by theme/sub-topic\n"
            f"5. Identify common trends and research gaps\n\n"
            f"Aim to cover at least 3-5 key papers."
        ),
        agent=researcher_agent,
        expected_output=(
            "A detailed research report with summaries of 3-5 key papers, "
            "organized by theme, with key findings and identified gaps."
        ),
    )

    write_task = Task(
        description=(
            f"Write a comprehensive literature review summary on: **{topic}**\n\n"
            f"Using the research findings provided by the Researcher agent, write:\n"
            f"1. **Introduction** — Background and importance of the topic\n"
            f"2. **Key Themes** — Group findings by major themes (2-3 themes)\n"
            f"3. **Methodology Comparison** — How different papers approach the problem\n"
            f"4. **Key Findings** — Most important results and contributions\n"
            f"5. **Research Gaps** — Areas that need more exploration\n"
            f"6. **Conclusion** — Summary of current state and future directions\n\n"
            f"The review should be:\n"
            f"- Well-structured with clear headings\n"
            f"- Written in academic but accessible language\n"
            f"- 500-800 words in length\n"
            f"- Include proper citations for all referenced papers"
        ),
        agent=writer_agent,
        expected_output=(
            "A complete literature review in markdown format, "
            "500-800 words, with introduction, themed sections, "
            "methodology comparison, findings, gaps, and conclusion."
        ),
    )

    return [plan_task, research_task, write_task]


# ============================================================
# DEMO MODE TASK TEMPLATES
# ============================================================

DEMO_TASK_OUTPUTS = {
    "plan": """# Research Plan: {topic}

## 1. Scope Definition
This literature review focuses on **{topic}**, examining the current state of research, 
key methodologies, seminal papers, and emerging trends.

## 2. Key Sub-Topics
1. **Foundational Concepts** — Core principles and early work
2. **Recent Advances** — State-of-the-art methods and breakthroughs
3. **Applications & Impact** — Real-world applications and industry adoption
4. **Challenges & Limitations** — Known issues and open problems
5. **Future Directions** — Emerging trends and research opportunities

## 3. Search Queries
- "{topic} survey"
- "{topic} state of the art 2024"
- "{topic} benchmark comparison"
- "{topic} applications"
- "{topic} challenges limitations"

## 4. Quality Criteria
- Published in top-tier venues (NeurIPS, ICML, ICLR, ACL, CVPR, etc.)
- Minimum 50 citations (unless very recent)
- Clear methodology and reproducible results
- Relevance to the core topic

## 5. Review Outline
1. Introduction & Background
2. Core Methods & Architectures  
3. Applications & Benchmarks
4. Challenges & Limitations
5. Future Directions
6. Conclusion
""",

    "research": """# Research Findings: {topic}

## Papers Analyzed

### Paper 1: Foundational Work
{papers_section_1}

### Paper 2: Methodological Advance
{papers_section_2}

### Paper 3: Recent Breakthrough
{papers_section_3}

## Thematic Analysis

### Theme 1: Architectural Innovation
Multiple papers demonstrate that novel architectural choices significantly impact 
performance. The trend moves from simple to increasingly sophisticated designs.

### Theme 2: Scalability
A recurring theme is the challenge of scaling approaches to handle larger datasets 
and more complex tasks while maintaining efficiency.

### Theme 3: Real-World Application
Recent work focuses on bridging the gap between theoretical advances and practical 
deployment, with emphasis on robustness and reliability.

## Research Gaps
1. Limited evaluation on multilingual/cross-domain settings
2. Computational efficiency for real-time applications
3. Theoretical understanding of why certain approaches work
4. Standardized evaluation benchmarks needed
""",

    "summary": """# Literature Review: {topic}

## 1. Introduction

The field of **{topic}** has experienced remarkable growth in recent years, driven by 
advances in deep learning and the availability of large-scale datasets. This literature 
review examines the current state of research, focusing on key methodologies, significant 
findings, and emerging trends.

## 2. Key Themes

### 2.1 Foundational Concepts and Architectures
The evolution of {topic} can be traced through several architectural innovations. 
Early work established the fundamental principles, while subsequent research introduced 
increasingly sophisticated approaches that achieved state-of-the-art results across 
multiple benchmarks. Notable contributions include novel attention mechanisms, 
pre-training strategies, and multi-task learning frameworks.

### 2.2 Recent Advances and State-of-the-Art
Recent work has pushed the boundaries of what is achievable in this domain. Key advances 
include improved training techniques, better scaling laws, and more efficient architectures. 
Several papers demonstrate that combining multiple approaches — such as retrieval-augmented 
generation and chain-of-thought reasoning — yields significant improvements over 
single-method baselines.

### 2.3 Applications and Practical Impact
The practical applications of {topic} span multiple domains, including natural language 
processing, computer vision, healthcare, and scientific discovery. Industry adoption has 
accelerated, with major technology companies deploying these systems at scale.

## 3. Methodology Comparison

| Approach | Strengths | Limitations |
|----------|-----------|-------------|
| Pre-training + Fine-tuning | Strong transfer learning | Requires task-specific data |
| In-context Learning | No fine-tuning needed | Limited by context window |
| Retrieval-Augmented | Grounded in real data | Retrieval quality is critical |

## 4. Key Findings

1. **Scale matters** — Larger models consistently outperform smaller ones, though with 
   diminishing returns beyond certain thresholds.
2. **Data quality > quantity** — Carefully curated training data produces better results 
   than simply increasing dataset size.
3. **Hybrid approaches** work best — Combining multiple techniques (e.g., retrieval + 
   generation) outperforms single-method systems.
4. **Evaluation challenges** — Standard benchmarks may not fully capture real-world 
   performance and robustness.

## 5. Research Gaps

Several important areas remain under-explored:
- **Multilingual generalization** — Most work focuses on English; cross-lingual 
  capabilities need further investigation.
- **Efficiency and sustainability** — Reducing computational costs while maintaining 
  performance is critical for broader adoption.
- **Theoretical foundations** — A deeper understanding of *why* certain approaches 
  work better than others.
- **Safety and reliability** — Ensuring robust, safe behavior in deployment settings.

## 6. Conclusion

The field of {topic} has made remarkable progress, with state-of-the-art systems achieving 
impressive results across diverse tasks. Key trends include scaling, hybrid approaches, and 
a growing focus on practical deployment. However, significant challenges remain in efficiency, 
multilingual support, and theoretical understanding. Future work should prioritize these 
gaps to enable the next generation of advances in this rapidly evolving field.

---

*Generated by the Multi-Agent Research Assistant — Day 3 Workshop*
"""
}
