from langchain_ollama import ChatOllama

from software_engineering_agent.proposal import FileEditProposal


def build_edit_prompt(
    task: str,
    implementation_plan: str,
    source_contents: dict[str, str],
    allowed_files: list[str],
) -> str:
    source_sections = []

    for file_name, content in source_contents.items():
        source_sections.append(
            f"File: {file_name}\n"
            f"```text\n{content}\n```"
        )

    source_text = "\n\n".join(source_sections)
    allowed_text = "\n".join(f"- {file}" for file in allowed_files)

    return (
        "You are proposing one controlled code edit.\n\n"
        f"Task:\n{task}\n\n"
        f"Implementation plan:\n{implementation_plan}\n\n"
        f"Allowed files:\n{allowed_text}\n\n"
        f"Repository source:\n\n{source_text}\n\n"
        "Choose exactly one file from the allowed files.\n"
        "Return the complete replacement content for that file.\n"
        "Do not modify or reference files outside the allowed list.\n"
        "Preserve existing behavior unless the task requires a change.\n"
    )


def create_edit_proposal(
    task: str,
    implementation_plan: str,
    source_contents: dict[str, str],
    allowed_files: list[str],
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
) -> FileEditProposal:
    prompt = build_edit_prompt(
        task,
        implementation_plan,
        source_contents,
        allowed_files,
    )

    llm = ChatOllama(
        model=model,
        base_url=base_url,
        temperature=0,
    )

    structured_llm = llm.with_structured_output(FileEditProposal)
    proposal = structured_llm.invoke(prompt)

    return FileEditProposal.model_validate(proposal)