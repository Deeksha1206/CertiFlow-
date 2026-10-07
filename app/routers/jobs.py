from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Certificate, CertificateStatus, Job, JobStatus
from app.schemas import GenerationJobCreate
from app.services.job_service import process_generation_job


router = APIRouter(
    prefix="/api/v1/jobs",
    tags=["Jobs"],
)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
)
def create_generation_job(
    payload: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Create a bulk certificate generation job.

    The request is validated first. The job and individual
    certificate records are persisted, then processing is
    delegated to a background task.
    """

    job = Job(
        event_name=payload.event_name,
        event_date=payload.event_date,
        status=JobStatus.QUEUED,
        total_recipients=len(payload.recipients),
        successful_count=0,
        failed_count=0,
    )

    db.add(job)
    db.flush()

    for index, recipient in enumerate(
        payload.recipients,
        start=1,
    ):
        certificate = Certificate(
            job_id=job.id,
            certificate_id=(
                f"CERT-{job.id[:8].upper()}-{index:04d}"
            ),
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status=CertificateStatus.PENDING,
        )

        db.add(certificate)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_generation_job,
        job.id,
    )

    return {
        "job_id": job.id,
        "status": job.status.value,
        "message": "Certificate generation job accepted.",
        "total_recipients": job.total_recipients,
        "created_at": job.created_at,
    }


@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found.",
        )

    pending_count = (
        job.total_recipients
        - job.successful_count
        - job.failed_count
    )

    processed_count = (
        job.successful_count
        + job.failed_count
    )

    if job.total_recipients > 0:
        progress_percent = (
            processed_count
            / job.total_recipients
        ) * 100
    else:
        progress_percent = 0.0

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "event_date": job.event_date,
        "status": job.status.value,
        "total_recipients": job.total_recipients,
        "successful_count": job.successful_count,
        "failed_count": job.failed_count,
        "pending_count": pending_count,
        "progress_percent": round(
            progress_percent,
            2,
        ),
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }
