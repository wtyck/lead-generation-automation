from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response, status

from app.database import Database
from app.schemas import (
    CRMEventList,
    FollowUpList,
    IntakeResult,
    LeadIn,
    LeadList,
)
from app.service import ingest_lead, list_crm_events, list_follow_ups, list_leads


def create_app(database_path: str | Path | None = None) -> FastAPI:
    path = database_path or os.getenv("DATABASE_PATH", "data/leads.db")
    database = Database(path)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        database.initialize()
        yield

    application = FastAPI(
        title="Lead Generation Automation",
        version="1.0.0",
        description="Portfolio API for lead intake, qualification, and outbound queues.",
        lifespan=lifespan,
    )
    application.state.database = database

    @application.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post(
        "/webhooks/leads",
        response_model=IntakeResult,
        status_code=status.HTTP_201_CREATED,
        tags=["leads"],
    )
    def receive_lead(
        payload: LeadIn, request: Request, response: Response
    ) -> IntakeResult:
        created, lead = ingest_lead(request.app.state.database, payload)
        if not created:
            response.status_code = status.HTTP_200_OK
        return IntakeResult(created=created, lead=lead)

    @application.get("/leads", response_model=LeadList, tags=["leads"])
    def get_leads(request: Request) -> LeadList:
        items = list_leads(request.app.state.database)
        return LeadList(total=len(items), items=items)

    @application.get("/follow-ups", response_model=FollowUpList, tags=["queues"])
    def get_follow_ups(request: Request) -> FollowUpList:
        items = list_follow_ups(request.app.state.database)
        return FollowUpList(total=len(items), items=items)

    @application.get("/crm-events", response_model=CRMEventList, tags=["queues"])
    def get_crm_events(request: Request) -> CRMEventList:
        items = list_crm_events(request.app.state.database)
        return CRMEventList(total=len(items), items=items)

    return application


app = create_app()
