from pathlib import Path

from agno.tools import tool

from app.tools.logs_service import register_logs

import difflib

DIR = Path("projects").resolve()

def safe_path(file_name: str, project_name: str) -> Path:
    path = (DIR/project_name/file_name).resolve()

    if not path.is_relative_to(DIR/project_name):
        raise ValueError("Security error: File must stay inside the project directory.")
    
    return path


def compute_diff(old: str, new: str, file_name: str):
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{file_name}",
        tofile=f"b/{file_name}",
        n=2,
    )

    return "".join(diff)


@tool
async def list_files(project_name: str) -> str:
    """List all Python files in the project folder."""

    dir = DIR/project_name
    
    files = [
        str(file.relative_to(dir))
        for file in dir.rglob("*.py")
        if not file.name.startswith((".", "__pycache__"))
    ]

    return "\n".join(files) if files else "No python files found."


@tool
async def read_file(file_name: str, project_name: str) -> str:
    """Read full text of a project file.
    
    Args:
        file_name: Name of file to read (e.g. 'calculator.py').
    """

    path = safe_path(file_name, project_name)

    if not path.is_file():
        return f"Error: File '{file_name}' does not exist."
    
    return path.read_text(encoding="utf-8")


@tool(requires_confirmation=True)
async def append_code(file_name: str, code: str, project_name: str, reason: str) -> str:
    """Append new code to the very end of an existing file and log the audit entry.

    Args:
        project_name: Name of the project directory.
        file_name: Name of the file.
        code: The block of code to append at the end of the file.
        reason: Technical reason for adding this code.
    """
    
    path = safe_path(file_name, project_name)
    
    if not path.exists():
        return f"Error: '{file_name}' does not exist."


    old = path.read_text(encoding="utf-8")

    with path.open("a", encoding="utf-8") as file:
        file.write("\n\n" + code.rstrip())

    new = path.read_text(encoding="utf-8")

    diff = compute_diff(
        old,
        new,
        file_name
    )

    await register_logs(
        project_name,
        file_name,
        reason,
        change=diff,
    )

    return f"Success: Appended code in {file_name}.\n\nApplied Diff:\n{diff}\nRun `run_tests` now."


@tool(requires_confirmation=True)
async def create_file(file_name: str, content: str, project_name: str, reason: str) -> str:
    """Create new file in the relative project directory and log the audit entry.

    Args:
        project_name: Name of the project directory.
        file_name: Name of the file.
        code: The block of code to append at the end of the file.
        reason: Technical reason for creating this file.
    """
    
    path = safe_path(file_name, project_name)
    
    if path.exists():
        return f"Error: File '{file_name}' already exists."

    path.parent.mkdir(parents=True, exist_ok=True)
    
    path.write_text(content, encoding="utf-8")

    new = path.read_text(encoding="utf-8")

    diff = compute_diff(
        "",
        new,
        file_name
    )

    await register_logs(
        project_name,
        file_name,
        reason,
        change=diff,
    
    )
    
    return f"Success: Created {file_name}."


@tool(requires_confirmation=True)
async def replace_code(file_name: str, project_name: str, old_code: str, new_code: str, reason: str) -> str:
    """Surgically replace an exact code snippet in a file with new code and log the unified diff.

    Important: `old_code` must match the file content exactly, including
    indentation and whitespace. Always read the file with `read_file` first.

    Args:
        project_name: Name of the project directory.
        file_name: Name of the file to modify.
        old_code: The exact snippet currently in the file to be replaced.
        new_code: The replacement snippet.
        reason: A concise 1-sentence technical explanation of why this fix is being applied.
    """
    
    if not old_code:
        return "Error: old_code cannot be empty."

    if old_code.strip() == new_code.strip():
        return "Error: new_code is identical to old_code."

    path = safe_path(file_name, project_name)
    
    if not path.is_file():
        return f"Error: File '{file_name}' does not exist."

    content = path.read_text(encoding="utf-8")
    
    match_count = content.count(old_code)

    if match_count == 0:
        return (
            f"Error: `old_code` not found in {file_name}. "
            "Call `read_file` to verify indentation and text."
        )

    if match_count > 1:
        return (
            f"Error: Found {match_count} occurrences. "
            "Include more surrounding code to make the block unique."
        )

    updated = content.replace(old_code, new_code, 1)

    path.write_text(updated, encoding="utf-8")

    diff = compute_diff(content, updated, file_name)

    await register_logs(
        project_name,
        file_name,
        reason,
        change=diff,
    )
    
    return f"Success: Replaced code in {file_name}.\n\nApplied Diff:\n{diff}\nRun `run_tests` now."