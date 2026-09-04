from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from app.database import Database
from app.schemas import LeadIn


def calculate_score(lead: LeadIn) -> int:
    return min(
        100,
        40
        + (25 if lead.phone else 0)
        + (20 if lead.company else 0)
        + (10 if lead.job_title else 0)
        + (5 if lead.consent_to_contact else 0),
    )


def segment_for_score(score: int) -> str:
    if score >= 80:
        return "high_intent"
    if score >= 60:
        return "qualified"
    return "nurture"


def follow_up_message(lead: LeadIn, segment: str) -> str:
    name = lead.first_name or "there"
    if segment == "high_intent":
        return f"Hi {name}, thanks for your interest. Would you like to schedule a short discovery call?"
    if segment == "qualified":
        return f"Hi {name}, thanks for connecting. Here is a quick overview of how we can help."
    return f"Hi {name}, thanks for joining us. We will share useful updates from time to time."


def serialize_lead(row: sqlite3.Row) -> dict[str, object]:
    result = dict(row)
    result["consent_to_contact"] = bool(result["consent_to_contact"])
    return result


def ingest_lead(database: Database, lead: LeadIn) -> tuple[bool, dict[str, object]]:
    score = calculate_score(lead)
    segment = segment_for_score(score)
    now = datetime.now(timezone.utc).isoformat()

    with database.connect() as connection:
        existing = connection.execute(
            "SELECT * FROM leads WHERE email = ?", (lead.email,)
        ).fetchone()
        if existing is not None:
            return False, serialize_lead(existing)

        cursor = connection.execute(
            """
            INSERT INTO leads (
                email, first_name, last_name, phone, company, job_title, source,
                consent_to_contact, score, segment, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lead.email,
                lead.first_name,
                lead.last_name,
                lead.phone,
                lead.company,
                lead.job_title,
                lead.source,
                int(lead.consent_to_contact),
                score,
                segment,
                now,
                now,
            ),
        )
        lead_id = int(cursor.lastrowid)
        if lead.consent_to_contact:
            connection.execute(
                """
                INSERT INTO follow_up_queue (
                    lead_id, channel, message, status, scheduled_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    lead_id,
                    "email",
                    follow_up_message(lead, segment),
                    "pending",
                    now,
                    now,
                ),
            )
        event_payload = {
            "lead_id": lead_id,
            "email": lead.email,
            "score": score,
            "segment": segment,
            "source": lead.source,
        }
        connection.execute(
            """
            INSERT INTO crm_event_log (
                lead_id, event_type, payload, status, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (lead_id, "lead.created", json.dumps(event_payload), "pending", now),
        )
        created = connection.execute(
            "SELECT * FROM leads WHERE id = ?", (lead_id,)
        ).fetchone()

    if created is None:
        raise RuntimeError("lead was not persisted")
    return True, serialize_lead(created)


def list_leads(database: Database) -> list[dict[str, object]]:
    with database.connect() as connection:
        rows = connection.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    return [serialize_lead(row) for row in rows]


def list_follow_ups(database: Database) -> list[dict[str, object]]:
    with database.connect() as connection:
        rows = connection.execute(
            "SELECT * FROM follow_up_queue ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def list_crm_events(database: Database) -> list[dict[str, object]]:
    with database.connect() as connection:
        rows = connection.execute(
            "SELECT * FROM crm_event_log ORDER BY id DESC"
        ).fetchall()
    return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]
