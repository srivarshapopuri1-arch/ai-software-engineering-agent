from collections.abc import Callable

from langgraph.graph import END, START, StateGraph

from software_engineering_agent.analysis import analyze_test_result
from software_engineering_agent.llm_retry import execute_llm_edit_with_retries
from software_engineering_agent.planner import create_plan
from software_engineering_agent.repository import (
    inspect_repository,
    read_repository_files,
)
from software_engineering_agent.retry import RetryResult
from software_engineering_agent.runner import run_pytest
from software_engineering_agent.state import AgentState

PlanFunction = Callable[[str, list[str], dict[str, str] | None], str]

EditFunction = Callable[
    [
        str,
        str,
        str,
        dict[str, str],
        list[str],
    ],
    RetryResult,
]


def inspect_node(state: AgentState) -> AgentState:
    info = inspect_repository(state["repository_path"])

    source_contents = read_repository_files(
        state["repository_path"],
        info.python_files,
    )

    return {
        "repository_files": info.files,
        "python_files": info.python_files,
        "test_files": info.test_files,
        "source_contents": source_contents,
    }


def make_plan_node(plan_function: PlanFunction):
    def plan_node(state: AgentState) -> AgentState:
        plan = plan_function(
            state["task"],
            state["repository_files"],
            state["source_contents"],
        )

        return {"implementation_plan": plan}

    return plan_node


def make_edit_node(edit_function: EditFunction):
    def edit_node(state: AgentState) -> AgentState:
        allowed_files = [
            file_name
            for file_name in state["python_files"]
            if file_name not in state["test_files"]
        ]

        if not allowed_files:
            return {
                "tests_succeeded": False,
                "test_output": "",
                "failure_summary": "No editable Python source files were found.",
            }

        result = edit_function(
            state["repository_path"],
            state["task"],
            state["implementation_plan"],
            state["source_contents"],
            allowed_files,
        )

        return {
            "tests_succeeded": result.succeeded,
            "test_output": result.final_result.analysis.relevant_output,
            "failure_summary": result.final_result.analysis.summary,
        }

    return edit_node


def test_node(state: AgentState) -> AgentState:
    result = run_pytest(state["repository_path"])
    analysis = analyze_test_result(result)

    return {
        "tests_succeeded": result.succeeded,
        "test_output": analysis.relevant_output,
        "failure_summary": analysis.summary,
    }


def build_workflow(
    plan_function: PlanFunction = create_plan,
    edit_function: EditFunction = execute_llm_edit_with_retries,
):
    graph = StateGraph(AgentState)

    graph.add_node("inspect_repository", inspect_node)
    graph.add_node("plan_change", make_plan_node(plan_function))
    graph.add_node("edit_and_verify", make_edit_node(edit_function))
    graph.add_node("run_final_tests", test_node)

    graph.add_edge(START, "inspect_repository")
    graph.add_edge("inspect_repository", "plan_change")
    graph.add_edge("plan_change", "edit_and_verify")
    graph.add_edge("edit_and_verify", "run_final_tests")
    graph.add_edge("run_final_tests", END)

    return graph.compile()