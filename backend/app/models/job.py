import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    youtube_url: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    video_title: Mapped[str | None] = mapped_column(String, nullable=True)
    video_thumbnail: Mapped[str | None] = mapped_column(String, nullable=True)
    video_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    result_paths: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    transcript: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
