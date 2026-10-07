from pathlib import Path

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_test_job():
    payload = {
        "event_name": "Aereo Cloud Engineering Workshop",
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
        ],
    }

    response = client.post(
        "/api/v1/jobs",
        json=payload,
    )

    assert response.status_code == 202

    return response.json()["job_id"]


def test_job_reaches_completion():
    reset_database()

    job_id = create_test_job()

    response = client.get(
        f"/api/v1/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["total_recipients"] == 2
    assert data["successful_count"] == 2
    assert data["failed_count"] == 0
    assert data["pending_count"] == 0
    assert data["progress_percent"] == 100.0


def test_certificate_retrieval():
    reset_database()

    create_test_job()

    response = client.get(
        "/api/v1/certificates"
    )

    # The API intentionally does not expose a collection endpoint.
    # Verify retrieval using a certificate ID obtained from the database.
    from app.database import SessionLocal
    from app.models import Certificate

    db = SessionLocal()

    try:
        certificate = db.query(Certificate).first()
        certificate_id = certificate.certificate_id
    finally:
        db.close()

    response = client.get(
        f"/api/v1/certificates/{certificate_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["certificate_id"] == certificate_id
    assert data["recipient_name"] == "Deeksha Sharma"
    assert data["status"] == "SUCCESS"
    assert data["file_path"] is not None


def test_certificate_verification():
    reset_database()

    create_test_job()

    from app.database import SessionLocal
    from app.models import Certificate

    db = SessionLocal()

    try:
        certificate = db.query(Certificate).first()
        certificate_id = certificate.certificate_id
    finally:
        db.close()

    response = client.get(
        f"/api/v1/certificates/{certificate_id}/verify"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["valid"] is True
    assert data["certificate_id"] == certificate_id
    assert data["recipient_name"] == "Deeksha Sharma"
    assert data["event_name"] == "Aereo Cloud Engineering Workshop"
    assert data["message"] == "Certificate verified successfully."


def test_certificate_download():
    reset_database()

    create_test_job()

    from app.database import SessionLocal
    from app.models import Certificate

    db = SessionLocal()

    try:
        certificate = db.query(Certificate).first()
        certificate_id = certificate.certificate_id
        file_path = certificate.file_path
    finally:
        db.close()

    assert file_path is not None
    assert Path("generated_certificates", file_path).exists()

    response = client.get(
        f"/api/v1/certificates/{certificate_id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
