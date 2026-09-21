from dataclasses import dataclass

from software_engineering_agent.runner import CommandResult


@dataclass
class FailureAnalysis:
    failed: bool
    summary: str
    relevant_output: str


def analyze_test_result(result: CommandResult) -> FailureAnalysis:
    """Extract a concise failure summary from a pytest command result."""

    if result.succeeded:
        return FailureAnalysis(
            failed=False,
            summary="Tests passed successfully.",
            relevant_output=result.stdout.strip(),
        )

    combined_output = "\n".join(
        part.strip()
        for part in (result.stdout, result.stderr)
        if part.strip()
    )

    lines = combined_output.splitlines()

    interesting_lines = [
        line
        for line in lines
        if (
            "FAILED" in line
            or "ERROR" in line
            or "AssertionError" in line
            or line.lstrip().startswith("E ")
        )
    ]

    relevant_output = "\n".join(interesting_lines).strip()

    if not relevant_output:
        relevant_output = combined_output.strip()

    return FailureAnalysis(
        failed=True,
        summary="Tests failed and need investigation.",
        relevant_output=relevant_output,
    )