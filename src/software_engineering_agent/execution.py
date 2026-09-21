from dataclasses import dataclass
from pathlib import Path

from software_engineering_agent.analysis import FailureAnalysis, analyze_test_result
from software_engineering_agent.editor import write_repository_file
from software_engineering_agent.proposal import (
    FileEditProposal,
    validate_edit_proposal,
)
from software_engineering_agent.runner import CommandResult, run_pytest


@dataclass
class EditExecutionResult:
    proposal: FileEditProposal
    written_path: Path
    test_result: CommandResult
    analysis: FailureAnalysis


def execute_edit_proposal(
    repository: str | Path,
    proposal: FileEditProposal,
    allowed_files: list[str],
) -> EditExecutionResult:
    """Validate, apply, and test one controlled repository edit."""

    validated_proposal = validate_edit_proposal(
        proposal,
        allowed_files,
    )

    written_path = write_repository_file(
        repository,
        validated_proposal.file_path,
        validated_proposal.replacement_content,
    )

    test_result = run_pytest(repository)
    analysis = analyze_test_result(test_result)

    return EditExecutionResult(
        proposal=validated_proposal,
        written_path=written_path,
        test_result=test_result,
        analysis=analysis,
    )