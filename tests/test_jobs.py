from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_create_generation_job():
    reset_database()

    payload = {
        "event_name": "Python Backend Workshop",
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

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "QUEUED"
    assert data["total_recipients"] == 2


def test_get_missing_job():
    reset_database()

    response = client.get(
        "/api/v1/jobs/does-not-exist"
    )

    assert response.status_code == 404
