import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    FAILED = "FAILED"


class CertificateStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    event_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    event_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.QUEUED,
        nullable=False,
    )

    total_recipients: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    successful_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    failed_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    certificates: Mapped[list["Certificate"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_id,
    )

    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    certificate_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    recipient_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    recipient_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    status: Mapped[CertificateStatus] = mapped_column(
        Enum(CertificateStatus),
        default=CertificateStatus.PENDING,
        nullable=False,
    )

    file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    job: Mapped["Job"] = relationship(
        back_populates="certificates",
    )
