from .state import ResearchState
from tools import web_search


def search_sources(state: ResearchState) -> ResearchState:
    """
    Search the web using Tavily and populate the research state.

    Steps:
    1. Search Tavily
    2. Store Tavily AI answer
    3. Remove duplicate URLs
    4. Store cleaned search results
    5. Update metrics
    """

    state.log(f"Searching for: {state.topic}")

    search_response = web_search.invoke(
        {
            "query": state.topic
        }
    )

    if not search_response:
        raise Exception("Search returned no response.")

    # ----------------------------------------------------------
    # Tavily AI Answer
    # ----------------------------------------------------------

    state.tavily_answer = search_response.get("answer", "")

    # ----------------------------------------------------------
    # Raw Search Results
    # ----------------------------------------------------------

    results = search_response.get("results", [])

    if not results:
        raise Exception("No search results found.")
    
    state.log(
        f"Tavily returned {len(results)} results."
    )

    # ----------------------------------------------------------
    # Remove duplicate URLs
    # ----------------------------------------------------------

    unique_results = []
    seen = set()

    for result in results:

        url = result.get("url", "").strip()

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)
        unique_results.append(result)

    state.search_results = unique_results

    # ----------------------------------------------------------
    # Metrics
    # ----------------------------------------------------------

    state.metrics["returned"] = len(unique_results)

    state.log(
        f"Search complete. "
        f"Returned {len(unique_results)} unique results."
    )

    return state