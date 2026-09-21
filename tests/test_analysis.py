from software_engineering_agent.analysis import analyze_test_result
from software_engineering_agent.runner import CommandResult


def test_analyze_successful_result() -> None:
    result = CommandResult(
        command=["python", "-m", "pytest", "-q"],
        return_code=0,
        stdout="3 passed in 0.04s",
        stderr="",
    )

    analysis = analyze_test_result(result)

    assert analysis.failed is False
    assert analysis.summary == "Tests passed successfully."
    assert "3 passed" in analysis.relevant_output


def test_analyze_failed_result_extracts_failure_details() -> None:
    result = CommandResult(
        command=["python", "-m", "pytest", "-q"],
        return_code=1,
        stdout=(
            "FAILED tests/test_math.py::test_addition - AssertionError\n"
            "E assert 4 == 5\n"
            "1 failed in 0.10s"
        ),
        stderr="",
    )

    analysis = analyze_test_result(result)

    assert analysis.failed is True
    assert analysis.summary == "Tests failed and need investigation."
    assert "FAILED tests/test_math.py::test_addition" in analysis.relevant_output
    assert "E assert 4 == 5" in analysis.relevant_output


def test_analyze_failure_falls_back_to_full_output() -> None:
    result = CommandResult(
        command=["python", "-m", "pytest", "-q"],
        return_code=2,
        stdout="pytest exited unexpectedly",
        stderr="",
    )

    analysis = analyze_test_result(result)

    assert analysis.failed is True
    assert analysis.relevant_output == "pytest exited unexpectedly"