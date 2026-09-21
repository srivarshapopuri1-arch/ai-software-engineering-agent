import pytest

from software_engineering_agent.proposal import (
    FileEditProposal,
    validate_edit_proposal,
)


def test_valid_edit_proposal_is_accepted() -> None:
    proposal = FileEditProposal(
        file_path="src/app.py",
        replacement_content="print('updated')\n",
        reason="Update application behavior",
    )

    result = validate_edit_proposal(
        proposal,
        ["src/app.py", "tests/test_app.py"],
    )

    assert result == proposal


def test_edit_proposal_rejects_unapproved_file() -> None:
    proposal = FileEditProposal(
        file_path="secrets.txt",
        replacement_content="changed",
        reason="Attempt unsafe edit",
    )

    with pytest.raises(ValueError, match="not allowed for editing"):
        validate_edit_proposal(
            proposal,
            ["src/app.py"],
        )


def test_edit_proposal_requires_file_path() -> None:
    with pytest.raises(ValueError):
        FileEditProposal(
            file_path="",
            replacement_content="content",
            reason="Update",
        )


def test_edit_proposal_requires_reason() -> None:
    with pytest.raises(ValueError):
        FileEditProposal(
            file_path="src/app.py",
            replacement_content="content",
            reason="",
        )