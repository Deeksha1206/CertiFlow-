from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import GENERATED_CERTIFICATES_DIR
from app.database import get_db
from app.models import Certificate, CertificateStatus


router = APIRouter(
    prefix="/api/v1/certificates",
    tags=["Certificates"],
)


@router.get("/{certificate_id}")
def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.certificate_id
            == certificate_id
        )
        .first()
    )

    if certificate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found.",
        )

    return {
        "certificate_id": certificate.certificate_id,
        "recipient_name": certificate.recipient_name,
        "recipient_email": certificate.recipient_email,
        "status": certificate.status.value,
        "file_path": certificate.file_path,
        "error_message": certificate.error_message,
        "generated_at": certificate.generated_at,
    }


@router.get("/{certificate_id}/verify")
def verify_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.certificate_id
            == certificate_id
        )
        .first()
    )

    if certificate is None:
        return {
            "valid": False,
            "certificate_id": certificate_id,
            "message": "Certificate does not exist.",
        }

    if certificate.status != CertificateStatus.SUCCESS:
        return {
            "valid": False,
            "certificate_id": certificate.certificate_id,
            "message": "Certificate has not been successfully generated.",
        }

    job = certificate.job

    return {
        "valid": True,
        "certificate_id": certificate.certificate_id,
        "recipient_name": certificate.recipient_name,
        "event_name": job.event_name,
        "event_date": job.event_date,
        "issued_at": certificate.generated_at,
        "message": "Certificate verified successfully.",
    }


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
):
    certificate = (
        db.query(Certificate)
        .filter(
            Certificate.certificate_id
            == certificate_id
        )
        .first()
    )

    if certificate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found.",
        )

    if (
        certificate.status != CertificateStatus.SUCCESS
        or not certificate.file_path
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Certificate PDF is not available.",
        )

    file_path = (
        GENERATED_CERTIFICATES_DIR
        / certificate.file_path
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate file could not be found.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name,
    )
