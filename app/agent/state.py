from typing import Optional
from agno.agent import RunOutput

active_runs: dict[str, RunOutput] = {}

def save_run(session_id: str, run_output: RunOutput) -> None:
    active_runs[session_id] = run_output

def get_run(session_id: str) -> Optional[RunOutput]:
    return active_runs.get(session_id)

def clear_run(session_id: str) -> None:
    active_runs.pop(session_id, None)