from langchain.tools import tool
from tavily import TavilyClient
import trafilatura
import os
from dotenv import load_dotenv
from workflow.config import SEARCH_RESULTS, MAX_CONTENT_LENGTH

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ==========================================================
# WEB SEARCH TOOL
# ==========================================================

@tool
def web_search(query: str) -> list:
    """
    Search the web and return structured search results.

    Returns:
    [
        {
            "title": "...",
            "url": "...",
            "snippet": "..."
        }
    ]
    """

    try:

        response = tavily.search(
            query=query,
            max_results=SEARCH_RESULTS,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
        )

        results = []

        for item in response.get("results", []):

            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                }
            )

        return {
        "answer": response.get("answer", ""),
        "results": results,
    }

    except Exception as e:

        print(f"Search Error : {e}")
        return []


# ==========================================================
# URL SCRAPER TOOL
# ==========================================================

@tool
def scrape_url(url: str) -> str:
    """
    Scrape a webpage and return the cleaned textual content.
    """

    try:

        print(f"\nScraping: {url}")

        downloaded = trafilatura.fetch_url(
        url,
        no_ssl=False
    )

        if downloaded is None:
            return "Scraping failed."

        extracted_text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_links=False,
            include_images=False,
            favor_precision=True,
            deduplicate=True,
        )

        if extracted_text is None:
            return "Scraping failed."

        extracted_text = extracted_text.strip()

        if len(extracted_text) < 500:
            return "Scraping failed."

        return extracted_text[:MAX_CONTENT_LENGTH]

    except Exception as e:

        print(f"Scraping Error : {e}")

        return "Scraping failed."