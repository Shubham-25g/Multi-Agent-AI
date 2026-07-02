from .state import ResearchState
from tools import scrape_url
from .config import (
    TARGET_SOURCES,
    MIN_CONTENT_LENGTH,
    BAD_KEYWORDS,
)


def scrape_sources(state: ResearchState,target_sources: int = TARGET_SOURCES,) -> ResearchState:
    """
    Scrape webpages until TARGET_SOURCES successful pages
    have been collected.
    """

    state.log("Starting webpage scraping...")
    state.log(
        f"Target sources: {target_sources}"
    )

    attempted = 0
    accepted = 0
    skipped = 0

    scraped_contents = []

    for result in state.search_results:

        # Stop after collecting enough successful sources
        if accepted >= target_sources:
            break

        attempted += 1

        url = result["url"]

        state.log(f"Scraping: {url}")

        try:

            content = scrape_url.invoke(
                {
                    "url": url
                }
            )

        except Exception as e:

            skipped += 1

            state.log(f"Failed: {url}")

            continue

        # --------------------------------------------------
        # Validate page
        # --------------------------------------------------

        reason = None

        if not content:
            reason = "No content"

        elif content.startswith("Scraping failed"):
            reason = "Scraping failed"

        elif len(content) < MIN_CONTENT_LENGTH:
            reason = "Too short"

        elif any(
            keyword in content.lower()
            for keyword in BAD_KEYWORDS
        ):
            reason = "Blocked page"

        if reason:

            skipped += 1

            state.log(
                f"Skipped ({reason}) : {url}"
            )

            continue

        scraped_contents.append(
            {
                "title": result["title"],
                "url": url,
                "snippet": result["snippet"],
                "content": content,
            }
        )

        accepted += 1

        state.log(
            f"Accepted ({accepted}/{target_sources})"
        )

    # ------------------------------------------------------
    # Save state
    # ------------------------------------------------------

    state.scraped_contents = scraped_contents

    state.metrics["attempted"] = attempted
    state.metrics["accepted"] = accepted
    state.metrics["target"] = target_sources
    state.metrics["skipped"] = skipped

    if accepted == 0:

        raise Exception(
            "No webpages could be scraped successfully."
        )

    state.log(
        f"Scraping complete. "
        f"{accepted} accepted, "
        f"{skipped} skipped."
    )

    return state