from pydantic import BaseModel, Field


class FileEditProposal(BaseModel):
    file_path: str = Field(min_length=1)
    replacement_content: str
    reason: str = Field(min_length=1)


def validate_edit_proposal(
    proposal: FileEditProposal,
    allowed_files: list[str],
) -> FileEditProposal:
    """Validate that an edit targets an explicitly allowed repository file."""

    if proposal.file_path not in allowed_files:
        raise ValueError(
            f"File is not allowed for editing: {proposal.file_path}"
        )

    return proposal