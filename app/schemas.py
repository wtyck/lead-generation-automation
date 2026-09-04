from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LeadIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: str = Field(min_length=3, max_length=254)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=200)
    job_title: str | None = Field(default=None, max_length=200)
    source: str = Field(default="webhook", max_length=100)
    consent_to_contact: bool = False

    @field_validator("email")
    @classmethod
    def normalize_and_validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
            raise ValueError("must be a valid email address")
        return normalized

    @field_validator("first_name", "last_name", "company", "job_title", "source")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        digits = re.sub(r"\D", "", value)
        if not digits:
            raise ValueError("must contain digits")
        return ("+" if value.strip().startswith("+") else "") + digits


class LeadOut(BaseModel):
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    phone: str | None
    company: str | None
    job_title: str | None
    source: str
    consent_to_contact: bool
    score: int
    segment: str
    created_at: datetime
    updated_at: datetime


class IntakeResult(BaseModel):
    created: bool
    lead: LeadOut


class FollowUpOut(BaseModel):
    id: int
    lead_id: int
    channel: str
    message: str
    status: str
    scheduled_at: datetime
    created_at: datetime


class CRMEventOut(BaseModel):
    id: int
    lead_id: int
    event_type: str
    payload: dict[str, object]
    status: str
    created_at: datetime


class LeadList(BaseModel):
    total: int
    items: list[LeadOut]


class FollowUpList(BaseModel):
    total: int
    items: list[FollowUpOut]


class CRMEventList(BaseModel):
    total: int
    items: list[CRMEventOut]
