"""
Workflow package.

Contains the complete research workflow.

Modules
-------
state.py
search.py
scraper.py
reader.py
context.py
writer.py
critic.py
orchestrator.py
"""

from .orchestrator import run_research_pipeline

__all__ = [
    "run_research_pipeline",
]