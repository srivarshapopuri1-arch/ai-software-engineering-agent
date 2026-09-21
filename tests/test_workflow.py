from pathlib import Path

from software_engineering_agent.workflow import build_workflow


def fake_planner(task: str, repository_files: list[str]) -> str:
    return (
        f"Plan for: {task}. "
        f"Review these repository files: {', '.join(repository_files)}."
    )


def test_workflow_inspects_repository_plans_and_runs_tests(tmp_path: Path) -> None:
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

    workflow = build_workflow(plan_function=fake_planner)

    result = workflow.invoke(
        {
            "repository_path": str(tmp_path),
            "task": "Improve the add function",
        }
    )

    assert "app.py" in result["python_files"]
    assert "test_app.py" in result["test_files"]
    assert "Improve the add function" in result["implementation_plan"]
    assert result["tests_succeeded"] is True
    assert "1 passed" in result["test_output"]


def test_workflow_captures_test_failure(tmp_path: Path) -> None:
    (tmp_path / "test_failure.py").write_text(
        "def test_failure():\n"
        "    assert 1 == 2\n",
        encoding="utf-8",
    )

    workflow = build_workflow(plan_function=fake_planner)

    result = workflow.invoke(
        {
            "repository_path": str(tmp_path),
            "task": "Fix the failing test",
        }
    )

    assert "Fix the failing test" in result["implementation_plan"]
    assert result["tests_succeeded"] is False
    assert result["failure_summary"] == "Tests failed and need investigation."
    assert "FAILED" in result["test_output"]