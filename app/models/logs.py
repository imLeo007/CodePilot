from datetime import datetime

from sqlalchemy import Integer, String, Text, DateTime, func

from sqlalchemy.orm import mapped_column, Mapped

from app.core.database import Base


class Register(Base):

    __tablename__ = "register_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    file_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    change: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
    )