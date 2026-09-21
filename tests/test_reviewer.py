from software_engineering_agent.git_diff import GitDiffResult
from software_engineering_agent.reviewer import create_final_review


def test_final_review_reports_successful_change() -> None:
    git_diff = GitDiffResult(
        changed_files=["app.py"],
        diff=(
            "-    return a - b\n"
            "+    return a + b\n"
        ),
    )

    review = create_final_review(
        task="Fix the add function",
        implementation_plan="Update app.py and preserve existing behavior.",
        git_diff=git_diff,
        tests_succeeded=True,
        test_output="1 passed",
    )

    assert review.task == "Fix the add function"
    assert review.changed_files == ["app.py"]
    assert review.tests_succeeded is True
    assert "Tests passed successfully." in review.summary
    assert "app.py" in review.summary
    assert "1 passed" in review.summary
    assert "return a + b" in review.summary


def test_final_review_reports_failed_tests() -> None:
    git_diff = GitDiffResult(
        changed_files=["app.py"],
        diff="-old\n+new\n",
    )

    review = create_final_review(
        task="Change app behavior",
        implementation_plan="Update app.py.",
        git_diff=git_diff,
        tests_succeeded=False,
        test_output="FAILED test_app.py::test_behavior",
    )

    assert review.tests_succeeded is False
    assert "Tests failed" in review.summary
    assert "FAILED test_app.py::test_behavior" in review.summary


def test_final_review_handles_no_changes() -> None:
    git_diff = GitDiffResult(
        changed_files=[],
        diff="",
    )

    review = create_final_review(
        task="Inspect repository",
        implementation_plan="Inspect without modifying files.",
        git_diff=git_diff,
        tests_succeeded=True,
        test_output="2 passed",
    )

    assert review.changed_files == []
    assert "No changed files detected." in review.summary
    assert "2 passed" in review.summary