import json
import httpx
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax

console = Console()
API_BASE = "http://localhost:8000/agent"


def display_project_history(client: httpx.Client, project_name: str, limit: int = 3) -> None:
    """Fetch and display recent unified diffs from PostgreSQL audit logs."""
    
    try:
        
        res = client.post(
            f"{API_BASE}/history",
            json={"project_name": project_name, "limit": limit},
        )
        
        if res.status_code == 404:
            console.print(
                f"[yellow] No recorded changes found for '{project_name}'.[/yellow]\n"
            )
            
            return
        
        res.raise_for_status()
        
        records = res.json()

    except httpx.HTTPError as err:
        console.print(f"[red]Failed to fetch audit history:[/red] {err}\n")
        return

    console.print(
        f"\n[bold cyan]─── Recent Audit History ({project_name}) ───[/bold cyan]"
    )

    for idx, entry in enumerate(records, start=1):
        file_name = entry.get("file_name", "unknown")
        reason = entry.get("reason", "No reason recorded.")
        diff_text = entry.get("change", "")

        syntax_diff = (
            Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        )

        console.print(
            Panel(
                syntax_diff,
                title=f"[bold green]Change #{idx}: {file_name}[/bold green]",
                subtitle=f"[dim cyan]Reason:[/dim cyan] {reason}",
                border_style="cyan",
            )
        )
    console.print()


def render_tool_preview(tool_name: str, tool_args: dict) -> None:
    """Render tool arguments as a styled syntax block or diff."""
    file_name = tool_args.get("file_name", "unknown")
    reason = tool_args.get("reason", "No reason provided.")

    if tool_name == "replace_code":
        old_code = tool_args.get("old_code", "")
        new_code = tool_args.get("new_code", "")
        syntax_view = Syntax(
            f"- {old_code}\n+ {new_code}",
            "diff",
            theme="monokai",
            line_numbers=True,
        )
        content = syntax_view

    elif tool_name in ("create_file", "append_code"):
        code = tool_args.get("code", "")
        content = Syntax(code, "python", theme="monokai", line_numbers=True)

    else:
        content = json.dumps(tool_args, indent=2)

    console.print(
        Panel(
            content,
            title=f"[bold yellow] HITL Approval Required: {tool_name}[/bold yellow]",
            subtitle=f"[cyan]{file_name}[/cyan] — {reason}",
            border_style="yellow",
        )
    )


def main() -> None:
    console.clear()
    console.rule("[bold cyan]CodePilot Autonomous Debugging Engine[/bold cyan]")

    client = httpx.Client(timeout=180.0)

    # 1. Select target project
    project_name = Prompt.ask(
        "[bold green]Target Project[/bold green]", default="calculator"
    )

    # 2. Audit check prompt before triggering the agent
    if Confirm.ask(
        f"[bold cyan]View recent audit changes for '{project_name}'?[/bold cyan]",
        default=False,
    ):
        display_project_history(client, project_name, limit=3)

    # 3. Task input
    prompt = Prompt.ask("[bold green]Task Prompt[/bold green]")

    if not prompt.strip():
        console.print("[red]Aborted: Empty prompt provided.[/red]")
    
        return

    # 4. Start run with spinner
    with console.status(
        "[bold green]CodePilot is analyzing workspace & running tests...",
        spinner="dots",
    ):
        try:
            res = client.post(
                f"{API_BASE}/run",
                json={"project_name": project_name, "prompt": prompt},
            )
            
            res.raise_for_status()
            
            data = res.json()
        
        except httpx.HTTPError as err:
            console.print(f"[bold red]API Connection Error:[/bold red] {err}")
            
            return

    session_id = data["session_id"]
    
    run_id = data["run_id"]

    # 5. HITL loop
    while data.get("status") == "paused":
        pending = data.get("pending_tool") or {}
        tool_name = pending.get("tool_name", "unknown")
        tool_args = pending.get("tool_args", {})

        render_tool_preview(tool_name, tool_args)

        approved = Confirm.ask(
            "[bold yellow]Authorize this change to disk?[/bold yellow]",
            default=True,
        )

        with console.status(
            f"[bold cyan]Submitting decision (approved={approved}) & verifying with pytest...",
            spinner="dots",
        ):
            try:
                res = client.post(
                    f"{API_BASE}/approve",
                    json={
                        "session_id": session_id,
                        "run_id": run_id,
                        "approved": approved,
                    },
                )

                res.raise_for_status()
                
                data = res.json()
            
            except httpx.HTTPError as err:
                console.print(f"[bold red]Failed to submit approval:[/bold red] {err}")
                
                return

    # 6. Final report
    console.print()
    console.print(
        Panel(
            Markdown(data.get("content") or "Task completed without summary."),
            title="[bold green]✓ Execution Completed[/bold green]",
            border_style="green",
        )
    )

    console.rule("[bold cyan]Session Finished[/bold cyan]")


if __name__ == "__main__":
    main()