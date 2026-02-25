"""
Configuration loader for the Multi-Agent Research Assistant.

Handles environment variables, demo mode toggle, and model settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Central configuration for the research assistant."""

    # --- API Settings ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # --- Mode ---
    DEMO_MODE: bool = False  # Set via CLI flag --demo

    # --- Agent Settings ---
    VERBOSE: bool = os.getenv("VERBOSE", "true").lower() == "true"
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))

    # --- Memory Settings ---
    MEMORY_COLLECTION: str = "research_memory"
    MAX_SHORT_TERM_MESSAGES: int = 20

    @classmethod
    def is_live_mode(cls) -> bool:
        """Check if we have an API key and are NOT in demo mode."""
        return bool(cls.OPENAI_API_KEY) and not cls.DEMO_MODE

    @classmethod
    def validate(cls):
        """Validate configuration and print status."""
        if cls.DEMO_MODE:
            print("🎭 Running in DEMO mode (mock responses, no API key needed)")
        elif not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY.startswith("sk-your"):
            print("⚠️  No valid OPENAI_API_KEY found.")
            print("   Use --demo flag for demo mode, or set your key in .env")
            print("   Example: python main.py --demo \"your topic\"")
            cls.DEMO_MODE = True
            print("🎭 Auto-switching to DEMO mode.\n")
        else:
            print(f"🟢 Live mode | Model: {cls.OPENAI_MODEL}")

    @classmethod
    def set_demo_mode(cls, enabled: bool = True):
        """Enable or disable demo mode."""
        cls.DEMO_MODE = enabled
