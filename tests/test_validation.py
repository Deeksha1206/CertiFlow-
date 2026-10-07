from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_invalid_email_is_rejected():
    reset_database()

    payload = {
        "event_name": "Python Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {
                "name": "Deeksha Sharma",
                "email": "not-an-email",
            }
        ],
    }

    response = client.post(
        "/api/v1/jobs",
        json=payload,
    )

    assert response.status_code == 422


def test_empty_recipient_list_is_rejected():
    reset_database()

    payload = {
        "event_name": "Python Workshop",
        "event_date": "2026-10-07",
        "recipients": [],
    }

    response = client.post(
        "/api/v1/jobs",
        json=payload,
    )

    assert response.status_code == 422


def test_short_recipient_name_is_rejected():
    reset_database()

    payload = {
        "event_name": "Python Workshop",
        "event_date": "2026-10-07",
        "recipients": [
            {
                "name": "A",
                "email": "a@example.com",
            }
        ],
    }

    response = client.post(
        "/api/v1/jobs",
        json=payload,
    )

    assert response.status_code == 422
