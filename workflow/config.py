"""
Configuration for the research workflow.

Modify these values to change the behaviour of the
entire research pipeline.
"""

# ==========================================================
# SEARCH
# ==========================================================

# Number of search results requested from Tavily
SEARCH_RESULTS = 20

# ==========================================================
# SCRAPER
# ==========================================================

# Number of successful webpages to collect
TARGET_SOURCES = 5

# Minimum characters required for a page to be considered useful
MIN_CONTENT_LENGTH = 500

# Maximum characters extracted from each webpage
MAX_CONTENT_LENGTH = 3000

# ==========================================================
# FILTERING
# ==========================================================

# Pages containing these keywords will be ignored
BAD_KEYWORDS = [
    "enable javascript",
    "cookies",
    "access denied",
    "page not found",
    "404",
    "forbidden",
    "captcha",
    "robot check",
    "cloudflare",
    "verification required",
]

# ==========================================================
# READER
# ==========================================================

# Approximate number of words in each source summary
READER_SUMMARY_WORDS = 300

# ==========================================================
# WRITER
# ==========================================================

# Maximum number of sources to cite in the report
MAX_CITATIONS = 5

# ==========================================================
# LOGGING
# ==========================================================

VERBOSE = True