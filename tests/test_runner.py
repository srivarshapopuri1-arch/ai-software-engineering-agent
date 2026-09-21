from pathlib import Path

import pytest

from software_engineering_agent.runner import run_pytest


def test_run_pytest_reports_success(tmp_path: Path) -> None:
    (tmp_path / "test_example.py").write_text(
        "def test_example():\n    assert 2 + 2 == 4\n",
        encoding="utf-8",
    )

    result = run_pytest(tmp_path)

    assert result.succeeded is True
    assert result.return_code == 0
    assert "1 passed" in result.stdout


def test_run_pytest_reports_failure(tmp_path: Path) -> None:
    (tmp_path / "test_example.py").write_text(
        "def test_example():\n    assert 2 + 2 == 5\n",
        encoding="utf-8",
    )

    result = run_pytest(tmp_path)

    assert result.succeeded is False
    assert result.return_code != 0
    assert "1 failed" in result.stdout


def test_run_pytest_rejects_missing_repository(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        run_pytest(missing)