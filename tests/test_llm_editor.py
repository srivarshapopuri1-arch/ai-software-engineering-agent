from software_engineering_agent.llm_editor import build_edit_prompt


def test_build_edit_prompt_contains_task_and_plan() -> None:
    prompt = build_edit_prompt(
        task="Add validation",
        implementation_plan="Update app.py and add tests.",
        source_contents={
            "src/app.py": "def run():\n    pass\n",
        },
        allowed_files=["src/app.py"],
    )

    assert "Add validation" in prompt
    assert "Update app.py and add tests." in prompt


def test_build_edit_prompt_contains_source_code() -> None:
    prompt = build_edit_prompt(
        task="Improve function",
        implementation_plan="Update the existing function.",
        source_contents={
            "src/app.py": "def run():\n    return True\n",
        },
        allowed_files=["src/app.py"],
    )

    assert "def run()" in prompt
    assert "src/app.py" in prompt


def test_build_edit_prompt_contains_allowed_files() -> None:
    prompt = build_edit_prompt(
        task="Fix bug",
        implementation_plan="Modify the implementation.",
        source_contents={
            "src/app.py": "value = 1\n",
        },
        allowed_files=["src/app.py", "tests/test_app.py"],
    )

    assert "src/app.py" in prompt
    assert "tests/test_app.py" in prompt
    assert "Choose exactly one file from the allowed files." in prompt