from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchState:
    """
    Shared state object for the complete research workflow.

    Every stage (Search, Scraper, Reader, Writer, Critic)
    reads from and updates this object.
    """

    # ==========================================================
    # USER INPUT
    # ==========================================================

    topic: str = ""

    # ==========================================================
    # SEARCH
    # ==========================================================

    tavily_answer: str = ""

    search_results: list[dict[str, Any]] = field(default_factory=list)

    # ==========================================================
    # SCRAPER
    # ==========================================================

    scraped_contents: list[dict[str, Any]] = field(default_factory=list)

    # ==========================================================
    # READER
    # ==========================================================

    summaries: list[dict[str, Any]] = field(default_factory=list)

    # ==========================================================
    # CONTEXT
    # ==========================================================

    research_context: str = ""

    # ==========================================================
    # WRITER
    # ==========================================================

    report: str = ""

    # ==========================================================
    # CRITIC
    # ==========================================================

    feedback: str = ""

    # ==========================================================
    # METRICS
    # ==========================================================

    metrics: dict[str, Any] = field(
        default_factory=lambda: {
            "returned": 0,
            "attempted": 0,
            "accepted": 0,
            "skipped": 0,
            "target": 0,
            "context_chars": 0,
            "report_chars": 0,
            "report_words": 0,
            "feedback_chars": 0,
            "feedback_words": 0,
        }
    )

    # ==========================================================
    # LOGS
    # ==========================================================

    logs: list[str] = field(default_factory=list)

    # ==========================================================
    # HELPER
    # ==========================================================

    def log(self, message: str) -> None:
        """Append a message to the workflow log."""

        self.logs.append(message)