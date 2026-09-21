from typing import TypedDict


class AgentState(TypedDict, total=False):
    repository_path: str
    repository_files: list[str]
    python_files: list[str]
    test_files: list[str]
    tests_succeeded: bool
    test_output: str
    failure_summary: str