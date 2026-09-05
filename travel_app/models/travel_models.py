from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class Flight(BaseModel):
    airline: str
    flight_number: str
    origin_airport: str
    destination_airport: str
    destination_city: str | None = None
    departure_time: datetime
    arrival_time: datetime | None = None
    duration: str | None = None
    nonstop: bool | None = None
    price: float | None = None
    currency: str | None = None


class Hotel(BaseModel):
    name: str
    city: str
    country_or_region: str
    check_in: date
    check_out: date
    nightly_rate: float | None = None
    total_price: float | None = None
    currency: str | None = None
    rating: float | None = None
    address: str | None = None


class FlightSearchResponse(BaseModel):
    destination: str
    flights: list[Flight] = Field(default_factory=list)
    error: str | None = None


class HotelSearchResponse(BaseModel):
    destination: str
    hotels: list[Hotel] = Field(default_factory=list)
    error: str | None = None


class DestinationResult(BaseModel):
    destination: str
    flights: list[Flight] = Field(default_factory=list)
    hotels: list[Hotel] = Field(default_factory=list)
    flight_error: str | None = None
    hotel_error: str | None = None
    agent_error: str | None = None


class TravelSearchResult(BaseModel):
    origin: str = "BWI"
    start_date: date
    end_date: date
    destinations: list[DestinationResult] = Field(default_factory=list)
