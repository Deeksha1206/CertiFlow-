from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.models import Certificate, CertificateStatus


client = TestClient(app)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_individual_certificate_failure_does_not_stop_batch():
    reset_database()

    payload = {
        "event_name": "Aereo Backend Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {
                "name": "Deeksha Sharma",
                "email": "deeksha@example.com",
            },
            {
                "name": "Rahul Kumar",
                "email": "rahul@example.com",
            },
            {
                "name": "Ananya Rao",
                "email": "ananya@example.com",
            },
        ],
    }

    original_generator = (
        "app.services.job_service.generate_certificate_pdf"
    )

    call_count = {"value": 0}

    def failing_generator(job, certificate):
        call_count["value"] += 1

        if call_count["value"] == 2:
            raise RuntimeError(
                "Simulated certificate generation failure"
            )

        from app.services.certificate_service import (
            generate_certificate_pdf,
        )

        return generate_certificate_pdf(
            job,
            certificate,
        )

    with patch(
        original_generator,
        side_effect=failing_generator,
    ):
        response = client.post(
            "/api/v1/jobs",
            json=payload,
        )

    assert response.status_code == 202

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/v1/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["status"] == "COMPLETED_WITH_ERRORS"
    assert data["total_recipients"] == 3
    assert data["successful_count"] == 2
    assert data["failed_count"] == 1
    assert data["pending_count"] == 0
    assert data["progress_percent"] == 100.0

    db = SessionLocal()

    try:
        certificates = (
            db.query(Certificate)
            .filter(
                Certificate.job_id == job_id
            )
            .order_by(Certificate.certificate_id)
            .all()
        )

        assert len(certificates) == 3

        statuses = [
            certificate.status
            for certificate in certificates
        ]

        assert statuses.count(
            CertificateStatus.SUCCESS
        ) == 2

        assert statuses.count(
            CertificateStatus.FAILED
        ) == 1

        failed_certificate = next(
            certificate
            for certificate in certificates
            if certificate.status
            == CertificateStatus.FAILED
        )

        assert (
            failed_certificate.error_message
            == "Simulated certificate generation failure"
        )

    finally:
        db.close()
