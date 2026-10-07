from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200,
    )
    email: EmailStr


class GenerationJobCreate(BaseModel):
    event_name: str = Field(
        min_length=2,
        max_length=200,
    )

    event_date: date

    recipients: list[RecipientCreate] = Field(
        min_length=1,
        max_length=5000,
    )


class JobResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    job_id: str
    event_name: str
    event_date: date
    status: str

    total_recipients: int
    successful_count: int
    failed_count: int
    pending_count: int

    progress_percent: float

    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str
    message: str
    total_recipients: int
    created_at: datetime


class CertificateResponse(BaseModel):
    certificate_id: str
    recipient_name: str
    recipient_email: EmailStr
    status: str
    file_path: str | None = None
    error_message: str | None = None
    generated_at: datetime | None = None


class CertificateVerificationResponse(BaseModel):
    valid: bool
    certificate_id: str
    recipient_name: str | None = None
    event_name: str | None = None
    event_date: date | None = None
    issued_at: datetime | None = None
    message: str
