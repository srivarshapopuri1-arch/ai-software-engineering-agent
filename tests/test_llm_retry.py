from pathlib import Path

from software_engineering_agent.proposal import FileEditProposal


def test_llm_retry_module_imports() -> None:
    from software_engineering_agent.llm_retry import execute_llm_edit_with_retries

    assert callable(execute_llm_edit_with_retries)


def test_llm_retry_passes_failure_context(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from software_engineering_agent import llm_retry

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

    received_plans: list[str] = []
    calls = 0

    def fake_create_edit_proposal(
        task: str,
        implementation_plan: str,
        source_contents: dict[str, str],
        allowed_files: list[str],
        model: str,
        base_url: str,
    ) -> FileEditProposal:
        nonlocal calls
        calls += 1
        received_plans.append(implementation_plan)

        if calls == 1:
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
            reason="Correct failed implementation",
        )

    monkeypatch.setattr(
        llm_retry,
        "create_edit_proposal",
        fake_create_edit_proposal,
    )

    result = llm_retry.execute_llm_edit_with_retries(
        repository=tmp_path,
        task="Fix the add function",
        implementation_plan="Update app.py without changing unrelated behavior.",
        source_contents={
            "app.py": "def add(a, b):\n    return a - b\n"
        },
        allowed_files=["app.py"],
        max_attempts=2,
    )

    assert result.succeeded is True
    assert result.attempts == 2
    assert "Previous test failure:" not in received_plans[0]
    assert "Previous test failure:" in received_plans[1]
    assert "FAILED" in received_plans[1]