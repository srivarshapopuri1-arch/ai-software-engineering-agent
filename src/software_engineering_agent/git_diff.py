import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GitDiffResult:
    changed_files: list[str]
    diff: str

    @property
    def has_changes(self) -> bool:
        return bool(self.changed_files)


def inspect_git_diff(repository: str | Path) -> GitDiffResult:
    """Inspect uncommitted Git changes in a repository."""

    root = Path(repository).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    status_command = [
        "git",
        "status",
        "--short",
    ]

    status_result = subprocess.run(
        status_command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if status_result.returncode != 0:
        raise RuntimeError(
            status_result.stderr.strip()
            or "Unable to inspect Git repository."
        )

    changed_files = []

    for line in status_result.stdout.splitlines():
        if len(line) >= 4:
            changed_files.append(line[3:].strip())

    diff_command = [
        "git",
        "diff",
        "--no-ext-diff",
        "--",
    ]

    diff_result = subprocess.run(
        diff_command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if diff_result.returncode != 0:
        raise RuntimeError(
            diff_result.stderr.strip()
            or "Unable to inspect Git diff."
        )

    return GitDiffResult(
        changed_files=changed_files,
        diff=diff_result.stdout,
    )