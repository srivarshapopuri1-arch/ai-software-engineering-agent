from pathlib import Path

import pytest

from software_engineering_agent.execution import execute_edit_proposal
from software_engineering_agent.proposal import FileEditProposal


def test_execute_edit_proposal_applies_change_and_runs_tests(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )

    (tmp_path / "test_app.py").write_text(
        "from app import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    proposal = FileEditProposal(
        file_path="app.py",
        replacement_content=(
            "def add(a, b):\n"
            "    return a + b\n"
        ),
        reason="Fix addition behavior",
    )

    result = execute_edit_proposal(
        tmp_path,
        proposal,
        ["app.py"],
    )

    assert result.written_path == (tmp_path / "app.py").resolve()
    assert result.test_result.succeeded is True
    assert result.analysis.failed is False


def test_execute_edit_proposal_reports_failed_tests(
    tmp_path: Path,
) -> None:
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )

    (tmp_path / "test_app.py").write_text(
        "from app import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    proposal = FileEditProposal(
        file_path="app.py",
        replacement_content=(
            "def add(a, b):\n"
            "    return a - b\n"
        ),
        reason="Introduce failing behavior for test",
    )

    result = execute_edit_proposal(
        tmp_path,
        proposal,
        ["app.py"],
    )

    assert result.test_result.succeeded is False
    assert result.analysis.failed is True
    assert "FAILED" in result.analysis.relevant_output


def test_execute_edit_proposal_rejects_unapproved_file(
    tmp_path: Path,
) -> None:
    proposal = FileEditProposal(
        file_path="unsafe.py",
        replacement_content="print('unsafe')\n",
        reason="Unsafe target",
    )

    with pytest.raises(ValueError, match="not allowed for editing"):
        execute_edit_proposal(
            tmp_path,
            proposal,
            ["app.py"],
        )