from .state import ResearchState
from agents import writer_chain


def generate_report(state: ResearchState) -> ResearchState:
    """
    Generate the final research report using the
    Writer Agent.
    """

    state.log("Starting Writer Agent...")

    if not state.research_context.strip():
        raise Exception(
            "Research context is empty."
        )

    try:

        report = writer_chain.invoke(
            {
                "topic": state.topic,
                "research": state.research_context,
            }
        )

    except Exception as e:

        state.log(
            f"Writer Agent failed: {e}"
        )

        raise

    state.report = report

    state.metrics["report_chars"] = len(report)
    state.metrics["report_words"] = len(report.split())

    state.log(
        "Writer Agent completed successfully."
    )

    state.log(
        f"Report length: {len(report):,} characters"
    )

    return state