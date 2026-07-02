from .state import ResearchState


def build_research_context(state: ResearchState) -> ResearchState:
    """
    Build the complete research context that will be
    supplied to the Writer Agent.

    The context consists of:
    1. Tavily AI answer
    2. Search snippets (only for successfully used sources)
    3. Reader summaries
    """

    state.log("Building research context...")

    sections = []

    # ==========================================================
    # Tavily AI Summary
    # ==========================================================

    if state.tavily_answer:

        sections.append(
            f"""
==================== TAVILY AI SUMMARY ====================

{state.tavily_answer}
"""
        )

    # ==========================================================
    # Only include search results that were actually scraped
    # ==========================================================

    used_urls = {
        page["url"]
        for page in state.scraped_contents
    }

    if state.search_results:

        search_section = [
            "==================== SEARCH RESULTS ====================\n"
        ]

        for i, result in enumerate(state.search_results, start=1):

            if result["url"] not in used_urls:
                continue

            search_section.append(
                f"""
Result {i}

Title:
{result['title']}

URL:
{result['url']}

Snippet:
{result['snippet']}

------------------------------------------------------------
"""
            )

        sections.append("\n".join(search_section))

    # ==========================================================
    # Reader Summaries
    # ==========================================================

    if state.summaries:

        summary_section = [
            "==================== SOURCE SUMMARIES ====================\n"
        ]

        for i, summary in enumerate(state.summaries, start=1):

            if summary.get("error"):
                continue

            summary_section.append(
                f"""
SOURCE {i}

TITLE:
{summary['title']}

URL:
{summary['url']}

SUMMARY:

{summary['summary']}

============================================================
"""
            )

        sections.append("\n".join(summary_section))

    # ==========================================================
    # Final Context
    # ==========================================================

    state.research_context = "\n\n".join(sections)

    state.metrics["context_chars"] = len(
        state.research_context
    )

    state.log(
        f"Research context built "
        f"({state.metrics['context_chars']:,} characters)"
    )

    return state