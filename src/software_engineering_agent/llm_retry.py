from pathlib import Path

from software_engineering_agent.llm_editor import create_edit_proposal
from software_engineering_agent.proposal import FileEditProposal
from software_engineering_agent.retry import RetryResult, execute_with_retries


def execute_llm_edit_with_retries(
    repository: str | Path,
    task: str,
    implementation_plan: str,
    source_contents: dict[str, str],
    allowed_files: list[str],
    max_attempts: int = 2,
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
) -> RetryResult:
    """Use Ollama to propose controlled edits and retry after test failures."""

    def proposal_function(
        attempt: int,
        failure_context: str | None,
    ) -> FileEditProposal:
        retry_context = ""

        if failure_context:
            retry_context = (
                "\n\nPrevious test failure:\n"
                f"{failure_context}\n\n"
                "Correct the previous edit based on this failure evidence."
            )

        plan_with_context = (
            f"{implementation_plan}"
            f"{retry_context}"
        )

        return create_edit_proposal(
            task=task,
            implementation_plan=plan_with_context,
            source_contents=source_contents,
            allowed_files=allowed_files,
            model=model,
            base_url=base_url,
        )

    return execute_with_retries(
        repository=repository,
        allowed_files=allowed_files,
        proposal_function=proposal_function,
        max_attempts=max_attempts,
    )