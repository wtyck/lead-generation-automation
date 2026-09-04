from fastapi.testclient import TestClient

from app.main import create_app


def test_webhook_creates_normalized_scored_lead_and_queues_outputs(tmp_path):
    app = create_app(tmp_path / "leads.db")

    with TestClient(app) as client:
        response = client.post(
            "/webhooks/leads",
            json={
                "email": "  Ada.Lovelace@Example.COM ",
                "first_name": "  Ada ",
                "last_name": " Lovelace  ",
                "phone": "+1 (555) 010-2020",
                "company": "  Analytical Engines  ",
                "job_title": " Founder ",
                "source": "portfolio-demo",
                "consent_to_contact": True,
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["created"] is True
        assert body["lead"]["email"] == "ada.lovelace@example.com"
        assert body["lead"]["phone"] == "+15550102020"
        assert body["lead"]["company"] == "Analytical Engines"
        assert body["lead"]["score"] == 100
        assert body["lead"]["segment"] == "high_intent"

        assert client.get("/leads").json()["total"] == 1
        follow_ups = client.get("/follow-ups").json()
        assert follow_ups["total"] == 1
        assert follow_ups["items"][0]["status"] == "pending"
        assert "Ada" in follow_ups["items"][0]["message"]

        events = client.get("/crm-events").json()
        assert events["total"] == 1
        assert events["items"][0]["event_type"] == "lead.created"
        assert events["items"][0]["status"] == "pending"


def test_duplicate_email_is_idempotent_and_does_not_repeat_queued_work(tmp_path):
    app = create_app(tmp_path / "leads.db")
    first = {
        "email": "duplicate@example.com",
        "first_name": "First",
        "consent_to_contact": True,
    }
    duplicate = {"email": " DUPLICATE@example.com ", "first_name": "Second"}

    with TestClient(app) as client:
        assert client.post("/webhooks/leads", json=first).status_code == 201
        response = client.post("/webhooks/leads", json=duplicate)

        assert response.status_code == 200
        assert response.json()["created"] is False
        assert response.json()["lead"]["first_name"] == "First"
        assert client.get("/leads").json()["total"] == 1
        assert client.get("/follow-ups").json()["total"] == 1
        assert client.get("/crm-events").json()["total"] == 1


def test_lead_without_contact_consent_is_not_queued_for_follow_up(tmp_path):
    app = create_app(tmp_path / "leads.db")

    with TestClient(app) as client:
        response = client.post(
            "/webhooks/leads",
            json={"email": "privacy@example.com", "consent_to_contact": False},
        )

        assert response.status_code == 201
        assert response.json()["lead"]["score"] == 40
        assert response.json()["lead"]["segment"] == "nurture"
        assert client.get("/follow-ups").json()["total"] == 0
        assert client.get("/crm-events").json()["total"] == 1


def test_webhook_rejects_unknown_fields(tmp_path):
    app = create_app(tmp_path / "leads.db")

    with TestClient(app) as client:
        response = client.post(
            "/webhooks/leads",
            json={"email": "valid@example.com", "unexpected": "not accepted"},
        )

    assert response.status_code == 422
