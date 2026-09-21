from pathlib import Path

import pytest

from software_engineering_agent.repository import inspect_repository


def test_inspect_repository_finds_python_and_test_files(tmp_path: Path) -> None:
    src = tmp_path / "src"
    tests = tmp_path / "tests"

    src.mkdir()
    tests.mkdir()

    (src / "app.py").write_text("print('hello')", encoding="utf-8")
    (tests / "test_app.py").write_text("def test_example(): pass", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Example", encoding="utf-8")

    info = inspect_repository(tmp_path)

    assert "src/app.py" in info.python_files
    assert "tests/test_app.py" in info.test_files
    assert "README.md" in info.files


def test_inspect_repository_ignores_virtual_environment(tmp_path: Path) -> None:
    venv = tmp_path / ".venv"
    venv.mkdir()

    (venv / "ignored.py").write_text("secret = True", encoding="utf-8")
    (tmp_path / "main.py").write_text("print('hello')", encoding="utf-8")

    info = inspect_repository(tmp_path)

    assert "main.py" in info.python_files
    assert ".venv/ignored.py" not in info.files


def test_inspect_repository_rejects_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"

    with pytest.raises(FileNotFoundError):
        inspect_repository(missing)