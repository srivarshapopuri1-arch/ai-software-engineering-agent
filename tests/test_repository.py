from pathlib import Path

import pytest

from software_engineering_agent.repository import (
    inspect_repository,
    read_repository_files,
)


def test_inspect_repository_finds_files(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()

    (tmp_path / "src" / "app.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )
    (tmp_path / "tests" / "test_app.py").write_text(
        "def test_example():\n    assert True\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Example",
        encoding="utf-8",
    )

    info = inspect_repository(tmp_path)

    assert "src/app.py" in info.files
    assert "tests/test_app.py" in info.files
    assert "README.md" in info.files
    assert "src/app.py" in info.python_files
    assert "tests/test_app.py" in info.test_files


def test_inspect_repository_ignores_venv(tmp_path: Path) -> None:
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "ignored.py").write_text(
        "print('ignore me')",
        encoding="utf-8",
    )
    (tmp_path / "app.py").write_text(
        "print('keep me')",
        encoding="utf-8",
    )

    info = inspect_repository(tmp_path)

    assert "app.py" in info.files
    assert ".venv/ignored.py" not in info.files


def test_inspect_repository_rejects_missing_path(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        inspect_repository(missing_path)


def test_read_repository_files_reads_selected_file(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )

    contents = read_repository_files(
        tmp_path,
        ["app.py"],
    )

    assert "app.py" in contents
    assert "def add" in contents["app.py"]


def test_read_repository_files_rejects_path_outside_repository(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="outside repository"):
        read_repository_files(
            tmp_path,
            ["../outside.py"],
        )