from langchain_ollama import ChatOllama


def build_planning_prompt(
    task: str,
    repository_files: list[str],
    source_contents: dict[str, str] | None = None,
) -> str:
    files_text = "\n".join(f"- {file}" for file in repository_files)

    source_section = ""

    if source_contents:
        source_parts = []

        for file_name, content in source_contents.items():
            source_parts.append(
                f"File: {file_name}\n"
                f"```text\n{content}\n```"
            )

        source_section = (
            "\n\nRelevant source code:\n\n"
            + "\n\n".join(source_parts)
        )

    return (
        "You are planning a code change for a software repository.\n\n"
        f"Task:\n{task}\n\n"
        f"Repository files:\n{files_text}"
        f"{source_section}\n\n"
        "Create a concise implementation plan based only on the repository "
        "information provided.\n"
        "Do not invent classes, functions, files, or architecture that are not "
        "shown in the repository context.\n"
        "Do not write code yet.\n"
        "Mention the files that likely need to change and the tests that should "
        "verify the work."
    )


def create_plan(
    task: str,
    repository_files: list[str],
    source_contents: dict[str, str] | None = None,
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
) -> str:
    prompt = build_planning_prompt(
        task,
        repository_files,
        source_contents,
    )

    llm = ChatOllama(
        model=model,
        base_url=base_url,
        temperature=0,
    )

    response = llm.invoke(prompt)

    return str(response.content).strip()