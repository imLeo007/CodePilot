from typing import Any, Optional

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class StartRunRequest(BaseModel):
    project_name: str = Field(..., example="calculator")
    prompt: str = Field(..., example="Run the tests and fix all failures.")
    session_id: Optional[str] = None


class ToolApprovalRequest(BaseModel):
    session_id: str
    run_id: str
    approved: bool = Field(..., description="True to confirm, False to reject")


class PendingToolInfo(BaseModel):
    tool_name: str
    tool_args: dict[str, Any]


class AgentRunResponse(BaseModel):
    session_id: str
    run_id: str
    status: str = Field(..., example="completed | paused")
    content: Optional[str] = None
    pending_tool: Optional[PendingToolInfo] = None


class HistoryModel(BaseModel):
    project_name: str = Field(..., example="calculator")
    limit: int | None = 10


class HistoryResponse(BaseModel):
    project_name: str
    file_name: str
    change: str
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)