from collections.abc import Callable

from langgraph.graph import END, START, StateGraph

from software_engineering_agent.analysis import analyze_test_result
from software_engineering_agent.planner import create_plan
from software_engineering_agent.repository import inspect_repository
from software_engineering_agent.runner import run_pytest
from software_engineering_agent.state import AgentState

PlanFunction = Callable[[str, list[str]], str]


def inspect_node(state: AgentState) -> AgentState:
    info = inspect_repository(state["repository_path"])

    return {
        "repository_files": info.files,
        "python_files": info.python_files,
        "test_files": info.test_files,
    }


def make_plan_node(plan_function: PlanFunction):
    def plan_node(state: AgentState) -> AgentState:
        plan = plan_function(
            state["task"],
            state["repository_files"],
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