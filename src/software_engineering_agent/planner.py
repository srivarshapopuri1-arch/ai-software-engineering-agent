from langchain_ollama import ChatOllama


def build_planning_prompt(task: str, repository_files: list[str]) -> str:
    files_text = "\n".join(f"- {file}" for file in repository_files)

    return (
        "You are planning a code change for a software repository.\n\n"
        f"Task:\n{task}\n\n"
        f"Repository files:\n{files_text}\n\n"
        "Create a concise implementation plan.\n"
        "Do not write code yet.\n"
        "Mention the files that likely need to change and the tests that should verify the work."
    )


def create_plan(
    task: str,
    repository_files: list[str],
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
) -> str:
    prompt = build_planning_prompt(task, repository_files)

    llm = ChatOllama(
        model=model,
        base_url=base_url,
        temperature=0,
    )

    response = llm.invoke(prompt)

    return str(response.content).strip()