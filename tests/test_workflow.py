from pathlib import Path

from software_engineering_agent.analysis import analyze_test_result
from software_engineering_agent.execution import EditExecutionResult
from software_engineering_agent.proposal import FileEditProposal
from software_engineering_agent.retry import RetryResult
from software_engineering_agent.runner import CommandResult
from software_engineering_agent.workflow import build_workflow


def fake_planner(
    task: str,
    repository_files: list[str],
    source_contents: dict[str, str] | None = None,
) -> str:
    source_files = ", ".join(source_contents or {})

    return (
        f"Plan for: {task}. "
        f"Review these repository files: {', '.join(repository_files)}. "
        f"Source files available: {source_files}."
    )


def make_retry_result(
    repository: str,
    succeeded: bool,
) -> RetryResult:
    command_result = CommandResult(
        command=["python", "-m", "pytest", "-q"],
        return_code=0 if succeeded else 1,
        stdout="1 passed" if succeeded else "FAILED test_app.py::test_add",
        stderr="",
    )

    analysis = analyze_test_result(command_result)

    execution_result = EditExecutionResult(
        proposal=FileEditProposal(
            file_path="app.py",
            replacement_content="def add(a, b):\n    return a + b\n",
            reason="Fix addition",
        ),
        written_path=Path(repository) / "app.py",
        test_result=command_result,
        analysis=analysis,
    )

    return RetryResult(
        attempts=1,
        succeeded=succeeded,
        final_result=execution_result,
    )


def test_workflow_runs_edit_and_final_tests(tmp_path: Path) -> None:
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

    received_allowed_files: list[str] = []

    def fake_editor(
        repository: str,
        task: str,
        implementation_plan: str,
        source_contents: dict[str, str],
        allowed_files: list[str],
    ) -> RetryResult:
        received_allowed_files.extend(allowed_files)

        return make_retry_result(
            repository,
            succeeded=True,
        )

    workflow = build_workflow(
        plan_function=fake_planner,
        edit_function=fake_editor,
    )

    result = workflow.invoke(
        {
            "repository_path": str(tmp_path),
            "task": "Fix the add function",
        }
    )

    assert result["tests_succeeded"] is True
    assert "app.py" in received_allowed_files
    assert "test_app.py" not in received_allowed_files
    assert "Plan for: Fix the add function" in result["implementation_plan"]


def test_workflow_reports_final_test_failure(tmp_path: Path) -> None:
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

    def fake_editor(
        repository: str,
        task: str,
        implementation_plan: str,
        source_contents: dict[str, str],
        allowed_files: list[str],
    ) -> RetryResult:
        return make_retry_result(
            repository,
            succeeded=False,
        )

    workflow = build_workflow(
        plan_function=fake_planner,
        edit_function=fake_editor,
    )

    result = workflow.invoke(
        {
            "repository_path": str(tmp_path),
            "task": "Fix the add function",
        }
    )

    assert result["tests_succeeded"] is False
    assert "FAILED" in result["test_output"]