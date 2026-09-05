from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class Flight(BaseModel):
    airline: str
    flight_number: str
    origin_airport: str
    destination_airport: str
    destination_city: str
    departure_time: datetime
    arrival_time: datetime
    duration: str
    nonstop: bool
    price: float
    currency: str = "USD"


class Stay(BaseModel):
    name: str
    city: str
    country_or_region: str
    check_in: date
    check_out: date
    nightly_rate: float
    total_price: float
    currency: str = "USD"
    rating: float
    address: str


class FlightSearchResponse(BaseModel):
    destination: str
    flights: list[Flight] = Field(default_factory=list)
    error: str | None = None


class StaySearchResponse(BaseModel):
    destination: str
    stays: list[Stay] = Field(default_factory=list)
    error: str | None = None


class PlaceResult(BaseModel):
    destination: str
    flights: list[Flight] = Field(default_factory=list)
    stays: list[Stay] = Field(default_factory=list)
    flight_error: str | None = None
    stay_error: str | None = None
    agent_error: str | None = None


class DestinationStaysResult(BaseModel):
    origin: str = "BWI"
    start_date: date
    end_date: date
    places: list[PlaceResult] = Field(default_factory=list)
