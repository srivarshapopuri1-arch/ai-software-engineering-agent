from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from software_engineering_agent.execution import (
    EditExecutionResult,
    execute_edit_proposal,
)
from software_engineering_agent.proposal import FileEditProposal

ProposalFunction = Callable[[int, str | None], FileEditProposal]


@dataclass
class RetryResult:
    attempts: int
    succeeded: bool
    final_result: EditExecutionResult


def execute_with_retries(
    repository: str | Path,
    allowed_files: list[str],
    proposal_function: ProposalFunction,
    max_attempts: int = 2,
) -> RetryResult:
    """Retry controlled edits until tests pass or the attempt limit is reached."""

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    failure_context: str | None = None
    final_result: EditExecutionResult | None = None

    for attempt in range(1, max_attempts + 1):
        proposal = proposal_function(
            attempt,
            failure_context,
        )

        final_result = execute_edit_proposal(
            repository,
            proposal,
            allowed_files,
        )

        if final_result.test_result.succeeded:
            return RetryResult(
                attempts=attempt,
                succeeded=True,
                final_result=final_result,
            )

        failure_context = final_result.analysis.relevant_output

    if final_result is None:
        raise RuntimeError("No edit attempt was executed")

    return RetryResult(
        attempts=max_attempts,
        succeeded=False,
        final_result=final_result,
    )