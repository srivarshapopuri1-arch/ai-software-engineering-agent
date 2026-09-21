from dataclasses import dataclass

from software_engineering_agent.git_diff import GitDiffResult


@dataclass
class FinalReview:
    task: str
    implementation_plan: str
    changed_files: list[str]
    tests_succeeded: bool
    summary: str


def create_final_review(
    task: str,
    implementation_plan: str,
    git_diff: GitDiffResult,
    tests_succeeded: bool,
    test_output: str,
) -> FinalReview:
    """Create a deterministic final review of an engineering change."""

    changed_files = git_diff.changed_files

    if tests_succeeded:
        status_text = "Tests passed successfully."
    else:
        status_text = "Tests failed and the change needs further investigation."

    if changed_files:
        files_text = ", ".join(changed_files)
    else:
        files_text = "No changed files detected."

    summary_parts = [
        f"Task: {task}",
        f"Implementation plan: {implementation_plan}",
        f"Changed files: {files_text}",
        f"Test status: {status_text}",
    ]

    if test_output.strip():
        summary_parts.append(
            f"Test evidence: {test_output.strip()}"
        )

    if git_diff.diff.strip():
        summary_parts.append(
            "Git diff:\n"
            f"{git_diff.diff.strip()}"
        )

    return FinalReview(
        task=task,
        implementation_plan=implementation_plan,
        changed_files=changed_files,
        tests_succeeded=tests_succeeded,
        summary="\n\n".join(summary_parts),
    )