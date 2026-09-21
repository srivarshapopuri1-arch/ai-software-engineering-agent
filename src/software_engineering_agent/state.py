from typing import TypedDict


class AgentState(TypedDict, total=False):
    repository_path: str
    task: str
    repository_files: list[str]
    python_files: list[str]
    test_files: list[str]
    source_contents: dict[str, str]
    implementation_plan: str
    tests_succeeded: bool
    test_output: str
    failure_summary: str