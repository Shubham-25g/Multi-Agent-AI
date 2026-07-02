from .state import ResearchState
from agents import critic_chain


def review_report(state: ResearchState) -> ResearchState:
    """
    Review the generated report using the Critic Agent.
    """

    state.log("Starting Critic Agent...")

    if not state.report.strip():
        raise Exception(
            "Cannot review an empty report."
        )

    try:

        feedback = critic_chain.invoke(
            {
                "report": state.report,
            }
        )

    except Exception as e:

        state.log(
            f"Critic Agent failed: {e}"
        )

        raise

    state.feedback = feedback

    state.metrics["feedback_chars"] = len(feedback)
    state.metrics["feedback_words"] = len(feedback.split())

    state.log(
        "Critic Agent completed successfully."
    )

    return state