from .state import ResearchState

from .search import search_sources
from .scraper import scrape_sources
from .reader import summarize_sources
from .context import build_research_context
from .writer import generate_report
from .critic import review_report


def run_research_pipeline(
    topic: str,
    target_sources: int = 5,
) -> ResearchState:
    """
    Execute the complete research workflow.

    Workflow:

    Search
        ↓
    Scrape
        ↓
    Reader
        ↓
    Context Builder
        ↓
    Writer
        ↓
    Critic
    """

    state = ResearchState()

    state.topic = topic

    state.log("=" * 60)
    state.log(f"Research Topic : {topic}")
    state.log("=" * 60)

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    state = search_sources(state)

    # ---------------------------------------------------------
    # Scraper
    # ---------------------------------------------------------

    state = scrape_sources(
        state,
        target_sources=target_sources,
    )

    # ---------------------------------------------------------
    # Reader
    # ---------------------------------------------------------

    state = summarize_sources(state)

    # ---------------------------------------------------------
    # Context Builder
    # ---------------------------------------------------------

    state = build_research_context(state)

    # ---------------------------------------------------------
    # Writer
    # ---------------------------------------------------------

    state = generate_report(state)

    # ---------------------------------------------------------
    # Critic
    # ---------------------------------------------------------

    state = review_report(state)

    state.log("Research workflow completed successfully.")

    return state