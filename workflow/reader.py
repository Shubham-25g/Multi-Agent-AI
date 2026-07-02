from .state import ResearchState
from agents import reader_chain


def summarize_sources(state: ResearchState) -> ResearchState:
    """
    Summarize every successfully scraped webpage.

    Each webpage is summarized independently by the Reader Agent.
    """

    state.log("Starting Reader Agent...")

    summaries = []

    total_sources = len(state.scraped_contents)

    for index, page in enumerate(state.scraped_contents, start=1):

        state.log(
            f"Summarizing source {index}/{total_sources}"
        )

        try:

            summary = reader_chain.invoke(
                {
                    "title": page["title"],
                    "url": page["url"],
                    "content": page["content"],
                }
            )

        except Exception as e:

            summaries.append(
                {
                    "title": page["title"],
                    "url": page["url"],
                    "summary": "",
                    "error": str(e),
                }
            )

            state.log(
                f"Reader failed for {page['url']}: {e}"
            )

            continue

        summaries.append(
            {
                "title": page["title"],
                "url": page["url"],
                "summary": summary,
            }
        )

    state.summaries = summaries

    state.log(
        f"Reader completed. "
        f"Generated {len(summaries)} summaries."
    )

    return state