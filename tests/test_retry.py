from pathlib import Path

from software_engineering_agent.proposal import FileEditProposal
from software_engineering_agent.retry import execute_with_retries


def test_retry_succeeds_on_second_attempt(tmp_path: Path) -> None:
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

    received_contexts: list[str | None] = []

    def proposal_function(
        attempt: int,
        failure_context: str | None,
    ) -> FileEditProposal:
        received_contexts.append(failure_context)

        if attempt == 1:
            return FileEditProposal(
                file_path="app.py",
                replacement_content=(
                    "def add(a, b):\n"
                    "    return a * b\n"
                ),
                reason="First attempt",
            )

        return FileEditProposal(
            file_path="app.py",
            replacement_content=(
                "def add(a, b):\n"
                "    return a + b\n"
            ),
            reason="Correct the failed implementation",
        )

    result = execute_with_retries(
        tmp_path,
        ["app.py"],
        proposal_function,
        max_attempts=2,
    )

    assert result.succeeded is True
    assert result.attempts == 2
    assert received_contexts[0] is None
    assert received_contexts[1] is not None
    assert "FAILED" in received_contexts[1]


def test_retry_stops_after_success(tmp_path: Path) -> None:
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

    calls = 0

    def proposal_function(
        attempt: int,
        failure_context: str | None,
    ) -> FileEditProposal:
        nonlocal calls
        calls += 1

        return FileEditProposal(
            file_path="app.py",
            replacement_content=(
                "def add(a, b):\n"
                "    return a + b\n"
            ),
            reason="Fix addition",
        )

    result = execute_with_retries(
        tmp_path,
        ["app.py"],
        proposal_function,
        max_attempts=3,
    )

    assert result.succeeded is True
    assert result.attempts == 1
    assert calls == 1


def test_retry_stops_at_max_attempts(tmp_path: Path) -> None:
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

    def proposal_function(
        attempt: int,
        failure_context: str | None,
    ) -> FileEditProposal:
        return FileEditProposal(
            file_path="app.py",
            replacement_content=(
                "def add(a, b):\n"
                "    return a - b\n"
            ),
            reason=f"Attempt {attempt}",
        )

    result = execute_with_retries(
        tmp_path,
        ["app.py"],
        proposal_function,
        max_attempts=2,
    )

    assert result.succeeded is False
    assert result.attempts == 2
    assert result.final_result.analysis.failed is True