from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import (
    Certificate,
    CertificateStatus,
    Job,
    JobStatus,
)
from app.services.certificate_service import (
    generate_certificate_pdf,
)


def utc_now():
    return datetime.now(timezone.utc)


def process_generation_job(job_id: str) -> None:
    """
    Process all pending certificates for a job.

    Each certificate is isolated inside its own try/except block,
    so one failed certificate does not stop the remaining batch.
    """

    db = SessionLocal()

    try:
        job = db.get(Job, job_id)

        if job is None:
            return

        job.status = JobStatus.PROCESSING
        job.started_at = utc_now()

        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(
                Certificate.job_id == job_id,
                Certificate.status == CertificateStatus.PENDING,
            )
            .all()
        )

        for certificate in certificates:
            try:
                certificate.status = (
                    CertificateStatus.PROCESSING
                )

                db.commit()

                relative_path = generate_certificate_pdf(
                    job,
                    certificate,
                )

                certificate.file_path = relative_path
                certificate.status = (
                    CertificateStatus.SUCCESS
                )
                certificate.generated_at = utc_now()
                certificate.error_message = None

                job.successful_count += 1

                db.commit()

            except Exception as exc:
                db.rollback()

                certificate = db.get(
                    Certificate,
                    certificate.id,
                )

                job = db.get(
                    Job,
                    job_id,
                )

                if certificate is not None:
                    certificate.status = (
                        CertificateStatus.FAILED
                    )
                    certificate.error_message = str(exc)

                if job is not None:
                    job.failed_count += 1

                db.commit()

        job = db.get(Job, job_id)

        if job is None:
            return

        if job.failed_count == 0:
            job.status = JobStatus.COMPLETED
        elif job.successful_count > 0:
            job.status = JobStatus.COMPLETED_WITH_ERRORS
        else:
            job.status = JobStatus.FAILED

        job.completed_at = utc_now()

        db.commit()

    finally:
        db.close()
