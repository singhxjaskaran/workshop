"""
Custom tools for the Multi-Agent Research Assistant.

Provides tools that agents can use to search papers, read content,
and save findings. Includes both live (API-based) and mock (demo) modes.
"""

import json
import random
from typing import Optional
from config import Config


# ============================================================
# MOCK DATA — Used in demo mode (no API key required)
# ============================================================

MOCK_PAPERS_DB = {
    "transformer": [
        {
            "title": "Attention Is All You Need",
            "authors": "Vaswani, A., Shazeer, N., Parmar, N., et al.",
            "year": 2017,
            "venue": "NeurIPS 2017",
            "abstract": "We propose a new simple network architecture, the Transformer, "
                        "based solely on attention mechanisms, dispensing with recurrence "
                        "and convolutions entirely. The Transformer allows for significantly "
                        "more parallelization and achieves state-of-the-art results in "
                        "machine translation.",
            "citations": 95000,
            "url": "https://arxiv.org/abs/1706.03762"
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "authors": "Devlin, J., Chang, M., Lee, K., Toutanova, K.",
            "year": 2019,
            "venue": "NAACL 2019",
            "abstract": "We introduce BERT, a new language representation model which stands "
                        "for Bidirectional Encoder Representations from Transformers. BERT is "
                        "designed to pre-train deep bidirectional representations from unlabeled "
                        "text by jointly conditioning on both left and right context.",
            "citations": 75000,
            "url": "https://arxiv.org/abs/1810.04805"
        },
        {
            "title": "GPT-4 Technical Report",
            "authors": "OpenAI",
            "year": 2023,
            "venue": "arXiv",
            "abstract": "We report the development of GPT-4, a large-scale, multimodal model "
                        "which can accept image and text inputs and produce text outputs. GPT-4 "
                        "exhibits human-level performance on various professional and academic "
                        "benchmarks.",
            "citations": 8500,
            "url": "https://arxiv.org/abs/2303.08774"
        },
        {
            "title": "An Image Is Worth 16x16 Words: Transformers for Image Recognition at Scale",
            "authors": "Dosovitskiy, A., Beyer, L., Kolesnikov, A., et al.",
            "year": 2021,
            "venue": "ICLR 2021",
            "abstract": "We show that a pure transformer applied directly to sequences of image "
                        "patches can perform very well on image classification tasks. Vision "
                        "Transformer (ViT) attains excellent results compared to state-of-the-art "
                        "convolutional networks while requiring substantially fewer computational "
                        "resources to train.",
            "citations": 32000,
            "url": "https://arxiv.org/abs/2010.11929"
        },
        {
            "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            "authors": "Lewis, P., Perez, E., Piktus, A., et al.",
            "year": 2020,
            "venue": "NeurIPS 2020",
            "abstract": "We explore a general-purpose fine-tuning recipe for retrieval-augmented "
                        "generation (RAG). RAG models combine pre-trained parametric and non-parametric "
                        "memory for language generation. We find that RAG models generate more specific, "
                        "diverse and factual language than a state-of-the-art parametric-only model.",
            "citations": 4500,
            "url": "https://arxiv.org/abs/2005.11401"
        }
    ],
    "agent": [
        {
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "authors": "Yao, S., Zhao, J., Yu, D., et al.",
            "year": 2023,
            "venue": "ICLR 2023",
            "abstract": "We explore the use of LLMs to generate both reasoning traces and task-specific "
                        "actions in an interleaved manner, allowing for greater synergy between the two: "
                        "reasoning traces help the model induce, track, and update action plans.",
            "citations": 3200,
            "url": "https://arxiv.org/abs/2210.03629"
        },
        {
            "title": "Generative Agents: Interactive Simulacra of Human Behavior",
            "authors": "Park, J.S., O'Brien, J.C., Cai, C.J., et al.",
            "year": 2023,
            "venue": "UIST 2023",
            "abstract": "We introduce generative agents — computational software agents that simulate "
                        "believable human behavior. We describe an architecture for generative agents "
                        "that includes a memory stream, reflection mechanism, and planning module.",
            "citations": 2800,
            "url": "https://arxiv.org/abs/2304.03442"
        },
        {
            "title": "Reflexion: Language Agents with Verbal Reinforcement Learning",
            "authors": "Shinn, N., Cassano, F., Gopinath, A., et al.",
            "year": 2023,
            "venue": "NeurIPS 2023",
            "abstract": "We propose Reflexion, a novel framework to reinforce language agents not "
                        "by updating weights, but through linguistic feedback. Reflexion agents "
                        "verbally reflect on task feedback signals, then maintain their own reflective "
                        "text in an episodic memory buffer.",
            "citations": 1800,
            "url": "https://arxiv.org/abs/2303.11366"
        },
        {
            "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
            "authors": "Schick, T., Dwivedi-Yu, J., Dessì, R., et al.",
            "year": 2023,
            "venue": "NeurIPS 2023",
            "abstract": "We introduce Toolformer, a model trained to decide which APIs to call, "
                        "when to call them, what arguments to pass, and how to best incorporate "
                        "the results into future token prediction.",
            "citations": 2100,
            "url": "https://arxiv.org/abs/2302.04761"
        },
        {
            "title": "AutoGPT: An Autonomous GPT-4 Experiment",
            "authors": "Significant Gravitas",
            "year": 2023,
            "venue": "GitHub",
            "abstract": "AutoGPT is an experimental open-source application showcasing the "
                        "capabilities of the GPT-4 language model. This program, driven by GPT-4, "
                        "chains together LLM 'thoughts' to autonomously achieve whatever goal you set.",
            "citations": 1500,
            "url": "https://github.com/Significant-Gravitas/AutoGPT"
        }
    ],
    "default": [
        {
            "title": "A Survey of Large Language Models",
            "authors": "Zhao, W.X., Zhou, K., Li, J., et al.",
            "year": 2023,
            "venue": "arXiv",
            "abstract": "This survey provides a comprehensive review of recent advances in large "
                        "language models (LLMs). We discuss pre-training, adaptation, utilization, "
                        "and evaluation of LLMs, along with their capabilities and limitations.",
            "citations": 5500,
            "url": "https://arxiv.org/abs/2303.18223"
        },
        {
            "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
            "authors": "Wei, J., Wang, X., Schuurmans, D., et al.",
            "year": 2022,
            "venue": "NeurIPS 2022",
            "abstract": "We explore how generating a chain of thought — a series of intermediate "
                        "reasoning steps — significantly improves the ability of large language "
                        "models to perform complex reasoning.",
            "citations": 7800,
            "url": "https://arxiv.org/abs/2201.11903"
        },
        {
            "title": "LLaMA: Open and Efficient Foundation Language Models",
            "authors": "Touvron, H., Lavril, T., Izacard, G., et al.",
            "year": 2023,
            "venue": "arXiv",
            "abstract": "We introduce LLaMA, a collection of foundation language models ranging "
                        "from 7B to 65B parameters. We show that it is possible to train state-of-the-art "
                        "models using publicly available datasets exclusively.",
            "citations": 9200,
            "url": "https://arxiv.org/abs/2302.13971"
        }
    ]
}


# ============================================================
# TOOL FUNCTIONS
# ============================================================

def search_papers(query: str, max_results: int = 5) -> str:
    """
    Search for academic papers on a given topic.

    Args:
        query: The search query (e.g., "transformer architectures")
        max_results: Maximum number of papers to return (default: 5)

    Returns:
        JSON string with a list of paper metadata.
    """
    if Config.DEMO_MODE:
        return _mock_search(query, max_results)

    # -- Live mode: uses a web search or arXiv API --
    # For workshop purposes, we use mock data even in "live" mode
    # to avoid requiring additional API keys for arXiv/Semantic Scholar.
    # In production, you'd integrate with:
    #   - Semantic Scholar API (api.semanticscholar.org)
    #   - arXiv API (export.arxiv.org/api)
    #   - Google Scholar (via SerpAPI)
    return _mock_search(query, max_results)


def read_paper(title: str) -> str:
    """
    Read and extract key information from a paper.

    Args:
        title: The title of the paper to read.

    Returns:
        Detailed information about the paper including abstract and key findings.
    """
    if Config.DEMO_MODE:
        return _mock_read_paper(title)

    return _mock_read_paper(title)


def save_findings(topic: str, findings: str) -> str:
    """
    Save research findings to a file.

    Args:
        topic: The research topic.
        findings: The findings to save.

    Returns:
        Confirmation message with the file path.
    """
    import os

    output_dir = os.path.join(os.path.dirname(__file__), "demo_output")
    os.makedirs(output_dir, exist_ok=True)

    safe_topic = topic.lower().replace(" ", "_")[:50]
    filepath = os.path.join(output_dir, f"findings_{safe_topic}.md")

    with open(filepath, "w") as f:
        f.write(f"# Research Findings: {topic}\n\n")
        f.write(findings)

    return f"✅ Findings saved to: {filepath}"


# ============================================================
# MOCK IMPLEMENTATIONS (for demo mode)
# ============================================================

def _mock_search(query: str, max_results: int) -> str:
    """Return mock search results based on query keywords."""
    query_lower = query.lower()

    # Match against keyword categories
    if any(kw in query_lower for kw in ["transformer", "attention", "bert", "gpt", "vision"]):
        papers = MOCK_PAPERS_DB["transformer"]
    elif any(kw in query_lower for kw in ["agent", "react", "tool", "autonomous", "autogpt"]):
        papers = MOCK_PAPERS_DB["agent"]
    else:
        papers = MOCK_PAPERS_DB["default"]

    # Shuffle and limit
    selected = random.sample(papers, min(max_results, len(papers)))

    results = []
    for p in selected:
        results.append({
            "title": p["title"],
            "authors": p["authors"],
            "year": p["year"],
            "venue": p["venue"],
            "citations": p["citations"],
            "url": p["url"],
            "abstract_preview": p["abstract"][:150] + "..."
        })

    return json.dumps(results, indent=2)


def _mock_read_paper(title: str) -> str:
    """Return mock paper details."""
    # Search all categories for the title
    for category in MOCK_PAPERS_DB.values():
        for paper in category:
            if title.lower() in paper["title"].lower():
                return json.dumps({
                    "title": paper["title"],
                    "authors": paper["authors"],
                    "year": paper["year"],
                    "venue": paper["venue"],
                    "abstract": paper["abstract"],
                    "citations": paper["citations"],
                    "url": paper["url"],
                    "key_contributions": [
                        f"Novel approach to {paper['title'].split(':')[0].lower()}",
                        "Achieves state-of-the-art performance on multiple benchmarks",
                        "Introduces new methodology that has been widely adopted"
                    ],
                    "methodology": "The paper proposes a systematic approach combining "
                                   "theoretical foundations with empirical evaluation across "
                                   "diverse datasets and tasks.",
                    "limitations": [
                        "Computational cost can be significant for large-scale deployment",
                        "Further evaluation on domain-specific tasks needed"
                    ]
                }, indent=2)

    # If paper not found, return generic info
    return json.dumps({
        "title": title,
        "authors": "Various Authors",
        "year": 2023,
        "abstract": f"This paper presents research related to {title}. "
                    "It introduces novel methods and evaluates them on standard benchmarks.",
        "key_contributions": [
            "Proposes a new approach",
            "Demonstrates improvements over baselines"
        ],
        "status": "Paper found — key details extracted."
    }, indent=2)


# ============================================================
# TOOL DEFINITIONS FOR CREWAI
# ============================================================

def get_tool_definitions():
    """
    Return tool definitions in a format compatible with CrewAI.
    These are used when demo mode is active (without crewai's @tool decorator).
    """
    return {
        "search_papers": {
            "function": search_papers,
            "description": "Search for academic papers on a topic. Input: query string.",
        },
        "read_paper": {
            "function": read_paper,
            "description": "Read a specific paper and get detailed information. Input: paper title.",
        },
        "save_findings": {
            "function": save_findings,
            "description": "Save research findings to a file. Inputs: topic, findings text.",
        }
    }
