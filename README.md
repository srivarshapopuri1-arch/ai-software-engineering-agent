# AI Software Engineering Agent

I built this project to explore how an LLM can work through a small software engineering task instead of only generating code from a prompt.

The agent inspects an existing Python repository, builds an implementation plan, proposes a controlled file edit, runs the test suite, analyzes failures, retries when necessary, and reviews the final Git changes.

The workflow is orchestrated with LangGraph and uses a local Ollama model for planning and code-edit proposals.

## How It Works

```text
Task
  ↓
Repository Inspection
  ↓
LLM Planning
  ↓
Structured Edit Proposal
  ↓
Safe File Editing
  ↓
Test Execution
  ↓
Failure Analysis
  ↓
Controlled Retry
  ↓
Final Test Run
  ↓
Git Diff Inspection
  ↓
Final Engineering Review
```

A task begins with the agent inspecting the target repository and reading the relevant Python source files. The planner uses that context to produce an implementation plan.

The editing stage asks the model for a structured proposal rather than unrestricted code execution. The proposed file must be part of the allowed file set before it can be written.

After the edit, the agent runs pytest. If the tests fail, the failure output is analyzed and passed back into the next attempt. The retry loop has a fixed attempt limit so it cannot continue indefinitely.

Once execution is complete, the workflow runs the tests again, inspects the Git diff, and produces a final review containing the task, implementation plan, changed files, test evidence, and resulting diff.

## Safety Boundaries

I intentionally kept the execution surface narrow.

- File writes are restricted to the target repository.
- Proposed edits must target explicitly allowed files.
- The model does not receive arbitrary shell access.
- Test execution uses a predefined pytest command.
- Retry attempts are bounded.
- Git is used for inspecting changes rather than automatically committing them.
- Repository paths are validated before file operations.

The LLM decides what change to propose, while deterministic Python code controls what it is actually allowed to modify and execute.

## Project Structure

```text
src/software_engineering_agent/
├── analysis.py
├── editor.py
├── execution.py
├── git_diff.py
├── llm_editor.py
├── llm_retry.py
├── planner.py
├── proposal.py
├── repository.py
├── retry.py
├── reviewer.py
├── runner.py
├── state.py
└── workflow.py

tests/
├── test_analysis.py
├── test_editor.py
├── test_execution.py
├── test_git_diff.py
├── test_llm_editor.py
├── test_llm_retry.py
├── test_planner.py
├── test_proposal.py
├── test_repository.py
├── test_retry.py
├── test_reviewer.py
├── test_runner.py
└── test_workflow.py
```

## Main Components

**Repository inspection** discovers repository files and safely reads source files while ignoring generated and environment directories.

**Planner** uses the repository context and task description to create an implementation plan with a local LLM.

**Structured edit proposal** uses Pydantic validation so the model returns a defined file edit instead of unrestricted output.

**Safe editor** ensures proposed paths remain inside the repository and only approved files can be modified.

**Test runner** runs the repository's pytest suite through a controlled command.

**Failure analysis and retry** extracts useful failure evidence and feeds it into another edit attempt when needed.

**Git diff inspection** uses Git status and diff information to identify the files changed by the agent.

**Final review** combines the original task, plan, changed files, test result, and Git diff into a final engineering summary.

**LangGraph workflow** connects the individual components into the complete execution flow.

## Tech Stack

- Python
- LangGraph
- LangChain
- Ollama
- Pydantic
- Pytest
- Git
- Ruff

The default local model used during development is `llama3.2:3b`.

## Setup

Python 3.11 or newer is required.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project and development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Install Ollama separately and make sure it is running.

Pull the model:

```powershell
ollama pull llama3.2:3b
```

The example environment configuration is available in `.env.example`.

## Running the Tests

Run the complete test suite:

```powershell
pytest -q
```

Check the code with Ruff:

```powershell
ruff check .
```

At the time of this README update, the project test suite contains 45 passing tests.

## End-to-End Evaluation

I tested the complete workflow against a temporary Git repository containing this intentionally incorrect function:

```python
def multiply(a, b):
    return a + b
```

with an existing test expecting:

```python
assert multiply(4, 5) == 20
```

The agent inspected the repository, generated a plan, proposed an edit, modified only `calculator.py`, ran the tests, and produced this change:

```diff
 def multiply(a, b):
-    return a + b
+    return a * b
```

The workflow reported:

```text
Tests succeeded: True
Changed files: ['calculator.py']
1 passed
```

I then ran pytest independently against the temporary repository and confirmed that the test passed. Git status showed only `calculator.py` as modified.

## Design Notes

One thing I wanted to explore with this project was the boundary between model reasoning and deterministic execution.

The LLM is useful for understanding a task, forming a plan, and proposing a code change. Operations that can affect the repository are deliberately handled by normal Python code with explicit validation.

That separation makes the workflow easier to inspect, test, and reason about than giving the model unrestricted access to the development environment.
