from workflow import run_research_pipeline


def print_separator(title: str):
    """Print a formatted section separator."""

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_logs(state):
    """Print workflow execution logs."""

    print_separator("WORKFLOW LOGS")

    for log in state.logs:
        print(log)


def print_metrics(state):
    """Print workflow metrics."""

    print_separator("WORKFLOW METRICS")

    metrics = state.metrics

    print(f"Search Results Returned : {metrics['returned']}")
    print(f"Search Results Attempted: {metrics['attempted']}")
    print(f"Target Sources          : {metrics['target']}")
    print(f"Accepted Sources        : {metrics['accepted']}")
    print(f"Skipped Sources         : {metrics['skipped']}")
    print(f"Context Size            : {metrics['context_chars']:,} chars")
    print(f"Report Size             : {metrics['report_chars']:,} chars")
    print(f"Report Words            : {metrics['report_words']:,}")
    print(f"Feedback Words          : {metrics['feedback_words']:,}")


def print_report(state):
    """Print the generated report."""

    print_separator("FINAL REPORT")

    print(state.report)


def print_feedback(state):
    """Print critic feedback."""

    print_separator("CRITIC FEEDBACK")

    print(state.feedback)


def main():

    print("=" * 80)
    print("MULTI-AGENT RESEARCH SYSTEM")
    print("=" * 80)

    topic = input("\nEnter Research Topic : ").strip()

    if not topic:
        print("\nPlease enter a valid topic.")
        return

    try:

        state = run_research_pipeline(topic)

    except Exception as e:

        print_separator("ERROR")

        print(e)

        return

    print_logs(state)

    print_metrics(state)

    print_report(state)

    print_feedback(state)


if __name__ == "__main__":
    main()