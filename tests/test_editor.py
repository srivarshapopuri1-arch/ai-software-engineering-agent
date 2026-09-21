from pathlib import Path

import pytest

from software_engineering_agent.editor import write_repository_file


def test_write_repository_file_updates_existing_file(tmp_path: Path) -> None:
    file_path = tmp_path / "app.py"
    file_path.write_text("old content", encoding="utf-8")

    result = write_repository_file(
        tmp_path,
        "app.py",
        "new content",
    )

    assert result == file_path.resolve()
    assert file_path.read_text(encoding="utf-8") == "new content"


def test_write_repository_file_creates_new_file(tmp_path: Path) -> None:
    result = write_repository_file(
        tmp_path,
        "src/new_file.py",
        "print('hello')\n",
    )

    assert result.exists()
    assert result.read_text(encoding="utf-8") == "print('hello')\n"


def test_write_repository_file_rejects_path_outside_repository(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="outside repository"):
        write_repository_file(
            tmp_path,
            "../outside.py",
            "unsafe",
        )


def test_write_repository_file_rejects_missing_repository(
    tmp_path: Path,
) -> None:
    missing_repository = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        write_repository_file(
            missing_repository,
            "app.py",
            "content",
        )