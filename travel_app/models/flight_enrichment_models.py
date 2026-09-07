from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class FlightInformationSummary(BaseModel):
    flight_number: str
    flight_date: date | None = None
    airline: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    scheduled_departure: datetime | None = None
    scheduled_arrival: datetime | None = None
    current_status: str | None = None
    gate: str | None = None
    terminal: str | None = None
    aircraft_type: str | None = None
    delay_details: str | None = None
    cancellation_details: str | None = None
    requires_date: bool = False
    real_time_status_verified: bool = False
    sources: list[str] = Field(default_factory=list)
    unverified_fields: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
