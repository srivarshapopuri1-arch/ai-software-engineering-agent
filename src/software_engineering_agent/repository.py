from dataclasses import dataclass
from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
}


@dataclass
class RepositoryInfo:
    root: Path
    files: list[str]
    python_files: list[str]
    test_files: list[str]


def inspect_repository(path: str | Path) -> RepositoryInfo:
    """Inspect a repository and return a lightweight view of its files."""

    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    files: list[str] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(root)

        if any(part in IGNORED_DIRECTORIES for part in relative_path.parts):
            continue

        files.append(relative_path.as_posix())

    files.sort()

    python_files = [file for file in files if file.endswith(".py")]
    test_files = [
        file
        for file in python_files
        if Path(file).name.startswith("test_") or "tests" in Path(file).parts
    ]

    return RepositoryInfo(
        root=root,
        files=files,
        python_files=python_files,
        test_files=test_files,
    )


def read_repository_files(
    repository: str | Path,
    files: list[str],
    max_characters_per_file: int = 6000,
) -> dict[str, str]:
    """Read selected text files while keeping access inside the repository."""

    root = Path(repository).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    contents: dict[str, str] = {}

    for relative_file in files:
        file_path = (root / relative_file).resolve()

        if not file_path.is_relative_to(root):
            raise ValueError(f"File is outside repository: {relative_file}")

        if not file_path.is_file():
            continue

        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        contents[relative_file] = text[:max_characters_per_file]

    return contents