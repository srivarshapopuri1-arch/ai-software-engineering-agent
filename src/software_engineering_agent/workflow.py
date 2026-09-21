from collections.abc import Callable

from langgraph.graph import END, START, StateGraph

from software_engineering_agent.analysis import analyze_test_result
from software_engineering_agent.planner import create_plan
from software_engineering_agent.repository import (
    inspect_repository,
    read_repository_files,
)
from software_engineering_agent.runner import run_pytest
from software_engineering_agent.state import AgentState

PlanFunction = Callable[[str, list[str], dict[str, str] | None], str]


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


def test_node(state: AgentState) -> AgentState:
    result = run_pytest(state["repository_path"])
    analysis = analyze_test_result(result)

    return {
        "tests_succeeded": result.succeeded,
        "test_output": analysis.relevant_output,
        "failure_summary": analysis.summary,
    }


def build_workflow(plan_function: PlanFunction = create_plan):
    graph = StateGraph(AgentState)

    graph.add_node("inspect_repository", inspect_node)
    graph.add_node("plan_change", make_plan_node(plan_function))
    graph.add_node("run_tests", test_node)

    graph.add_edge(START, "inspect_repository")
    graph.add_edge("inspect_repository", "plan_change")
    graph.add_edge("plan_change", "run_tests")
    graph.add_edge("run_tests", END)

    return graph.compile()