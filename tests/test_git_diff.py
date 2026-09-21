import subprocess
from pathlib import Path

import pytest

from software_engineering_agent.git_diff import inspect_git_diff


def initialize_git_repository(repository: Path) -> None:
    subprocess.run(
        ["git", "init"],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
    )


def test_inspect_git_diff_detects_modified_file(tmp_path: Path) -> None:
    initialize_git_repository(tmp_path)

    app_file = tmp_path / "app.py"
    app_file.write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )

    subprocess.run(
        ["git", "add", "app.py"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    app_file.write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )

    result = inspect_git_diff(tmp_path)

    assert result.has_changes is True
    assert result.changed_files == ["app.py"]
    assert "return a - b" in result.diff
    assert "return a + b" in result.diff


def test_inspect_git_diff_reports_clean_repository(tmp_path: Path) -> None:
    initialize_git_repository(tmp_path)

    result = inspect_git_diff(tmp_path)

    assert result.has_changes is False
    assert result.changed_files == []
    assert result.diff == ""


def test_inspect_git_diff_rejects_non_git_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(RuntimeError):
        inspect_git_diff(tmp_path)


def test_inspect_git_diff_rejects_missing_repository(
    tmp_path: Path,
) -> None:
    missing_repository = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        inspect_git_diff(missing_repository)