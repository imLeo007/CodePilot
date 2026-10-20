from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy import select

from agno.agent import RunOutput

from app.agent.instance import agent

from app.agent.state import clear_run, get_run, save_run

from app.core.database import get_db

from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.models.logs import Register

from app.schemas.agent import AgentRunResponse, PendingToolInfo, StartRunRequest, ToolApprovalRequest, HistoryResponse, HistoryModel



router = APIRouter(prefix="/agent", tags=["CodePilot"])


DBSession = Annotated[AsyncSession, Depends(get_db)]


def build_response(session_id: str, run_output: RunOutput) -> AgentRunResponse:
    if run_output.is_paused:
        pending = [
            req for req in (run_output.requirements or [])
            if getattr(req, "needs_confirmation", False)
        ]

        if pending:
            tool = pending[0].tool_execution

            return AgentRunResponse(
                session_id=session_id,
                run_id=run_output.run_id,
                status="paused",
                pending_tool=PendingToolInfo(
                    tool_name=tool.tool_name,
                    tool_args=tool.tool_args or {}
                )
            )

    return AgentRunResponse(
        session_id=session_id,
        run_id=run_output.run_id,
        status="completed",
        content=run_output.content
    )


@router.post("/run", response_model=AgentRunResponse)
async def start_process(request: StartRunRequest):
    if request.session_id is None:
        session_id = f"codepilot-{uuid4().hex[:8]}"
    else:
        session_id = request.session_id

    prompt = f"""
Project Name: {request.project_name}

User Prompt: {request.prompt}
"""

    response: RunOutput = await agent.arun(prompt, session_id=session_id)

    save_run(session_id, response)

    return build_response(session_id, response)


@router.post("/approve", response_model=AgentRunResponse)
async def approve_tool_execution(request: ToolApprovalRequest):
    cached_run = get_run(request.session_id)

    if not cached_run or not cached_run.is_paused:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active paused run found for this session"
        )

    pending = [
        req for req in (cached_run.requirements or [])
        if getattr(req, "needs_confirmation", False)
    ]

    if not pending:
        clear_run(request.session_id)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending tool confirmation found"
        )

    req = pending[0]

    if request.approved:
        req.confirm()

    else:
        req.reject()

    resumed_response: RunOutput = await agent.acontinue_run(
        session_id=request.session_id,
        run_id=request.run_id,
        requirements=pending,
    )

    save_run(request.session_id, resumed_response)

    if not resumed_response.is_paused:
        clear_run(request.session_id)

    return build_response(request.session_id, resumed_response)



@router.post("/history", response_model=list[HistoryResponse])
async def get_changes(entry: HistoryModel, db: DBSession) -> list[HistoryResponse]:
    query = (
        select(Register).where(Register.project_name==entry.project_name).order_by(Register.created_at)
    )

    if entry.limit is not None:
        query = (
            query.limit(entry.limit)
        )

    list_objects = await db.execute(query)

    records = list_objects.scalars().all()

    if not records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This project has no changes")

    return records