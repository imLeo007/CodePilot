from app.core.database import AsyncSessionLocal

from app.models.logs import Register


async def register_logs(
    project_name: str,
    file_name: str,
    reason: str,
    change: str,
) -> None:
    async with AsyncSessionLocal() as db:
        new_register = Register(
            file_name=file_name,
            project_name=project_name,
            reason=reason,
            change=change,
        )

        db.add(new_register)

        await db.commit()