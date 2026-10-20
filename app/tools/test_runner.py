import subprocess

from agno.tools import tool

@tool(requires_confirmation=False)
async def run_tests(project_name: str) -> str:
    """
    Run pytest inside the isolated project sandbox container and return it's results.

    Args:
        project_name: name of the project that needs test execution.
    """

    SANDBOX_CONTAINER = f"{project_name}_sandbox"
    
    try:
        # Check if the sandbox container is running
        check = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", SANDBOX_CONTAINER],
            capture_output=True,
            text=True,
            check=False,
        )

        if check.stdout.strip() != "true":
            return f"Error: Sandbox container '{SANDBOX_CONTAINER}' is not running."

        # Execute pytest inside the /app directory of the sandbox container
        result = subprocess.run(
            [
                "docker", "exec",
                "-w", "/app",
                SANDBOX_CONTAINER,
                "pytest", "-q", "--tb=short"
            ],
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )
    
    except subprocess.TimeoutExpired:
        return "Error: Test run timed out after 25 seconds in sandbox."
    
    except FileNotFoundError:
        return "Error: Docker CLI is not installed or not available in PATH inside CodePilot."

    output = result.stdout.strip() or result.stderr.strip()

    if len(output) > 2000:
        return output[:1000] + "\n...[truncated]...\n" + output[-1000:]

    return output or "All tests passed."