from software_engineering_agent.planner import build_planning_prompt


def test_build_planning_prompt_contains_task() -> None:
    prompt = build_planning_prompt(
        task="Add input validation",
        repository_files=["src/app.py", "tests/test_app.py"],
    )

    assert "Add input validation" in prompt


def test_build_planning_prompt_contains_repository_files() -> None:
    prompt = build_planning_prompt(
        task="Fix failing tests",
        repository_files=["src/app.py", "tests/test_app.py"],
    )

    assert "src/app.py" in prompt
    assert "tests/test_app.py" in prompt


def test_build_planning_prompt_prevents_immediate_code_generation() -> None:
    prompt = build_planning_prompt(
        task="Add a new API endpoint",
        repository_files=["src/api.py"],
    )

    assert "Do not write code yet." in prompt


def test_build_planning_prompt_includes_source_code() -> None:
    prompt = build_planning_prompt(
        task="Add input validation",
        repository_files=["src/repository.py"],
        source_contents={
            "src/repository.py": "def inspect_repository(path):\n    return path\n",
        },
    )

    assert "Relevant source code:" in prompt
    assert "def inspect_repository(path)" in prompt
    assert "src/repository.py" in prompt


def test_build_planning_prompt_warns_against_inventing_code() -> None:
    prompt = build_planning_prompt(
        task="Improve repository inspection",
        repository_files=["src/repository.py"],
        source_contents={
            "src/repository.py": "def inspect_repository(path):\n    return path\n",
        },
    )

    assert "Do not invent classes, functions, files, or architecture" in prompt