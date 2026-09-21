from pathlib import Path


def write_repository_file(
    repository: str | Path,
    relative_file: str,
    content: str,
) -> Path:
    """Write a text file while preventing writes outside the repository."""

    root = Path(repository).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Repository does not exist: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {root}")

    file_path = (root / relative_file).resolve()

    if not file_path.is_relative_to(root):
        raise ValueError(f"File is outside repository: {relative_file}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")

    return file_path