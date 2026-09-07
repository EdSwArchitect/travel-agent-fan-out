from __future__ import annotations

import re
from datetime import date

from travel_app.models.flight_enrichment_models import FlightInformationSummary


AIRLINE_PREFIXES = {
    "AA": "American Airlines",
    "AAL": "American Airlines",
    "AC": "Air Canada",
    "AS": "Alaska Airlines",
    "BA": "British Airways",
    "BAW": "British Airways",
    "B6": "JetBlue",
    "DL": "Delta Air Lines",
    "DAL": "Delta Air Lines",
    "F9": "Frontier Airlines",
    "JBU": "JetBlue",
    "NK": "Spirit Airlines",
    "SWA": "Southwest Airlines",
    "UA": "United Airlines",
    "UAL": "United Airlines",
    "WN": "Southwest Airlines",
}

UNVERIFIED_LIVE_FIELDS = [
    "departure_airport",
    "arrival_airport",
    "scheduled_departure",
    "scheduled_arrival",
    "current_status",
    "gate",
    "terminal",
    "aircraft_type",
    "delay_details",
    "cancellation_details",
]


def normalize_flight_number(flight_number: str) -> str:
    normalized = flight_number.strip().upper().replace(" ", "")
    if not re.fullmatch(r"[A-Z0-9]{2,3}\d{1,4}[A-Z]?", normalized):
        raise ValueError("flight_number must look like an airline code plus number")
    return normalized


def identify_airline(flight_number: str) -> str | None:
    for prefix_length in (2, 3):
        prefix = flight_number[:prefix_length]
        suffix = flight_number[prefix_length:]
        if prefix in AIRLINE_PREFIXES and re.fullmatch(r"\d{1,4}[A-Z]?", suffix):
            return AIRLINE_PREFIXES[prefix]
    return None


async def enrich_flight_information_service(
    *,
    flight_number: str,
    flight_date: date | None = None,
) -> FlightInformationSummary:
    """
    Conservative local flight information enrichment.

    This does not call a live flight data provider. It identifies common airline
    prefixes and marks schedule/status fields as unverified until a provider or
    web-search implementation is added.
    """
    normalized = normalize_flight_number(flight_number)
    airline = identify_airline(normalized)

    notes = [
        "Local enrichment only; no live flight provider or web lookup was called.",
        "Scheduled route, times, gate, terminal, aircraft, and status need a reliable current source.",
    ]
    if airline is None:
        notes.append("Airline could not be identified from the flight number prefix.")

    requires_date = flight_date is None
    if requires_date:
        notes.append("A flight date is needed before live schedule/status lookup.")

    return FlightInformationSummary(
        flight_number=normalized,
        flight_date=flight_date,
        airline=airline,
        requires_date=requires_date,
        real_time_status_verified=False,
        sources=["local airline-prefix map"],
        unverified_fields=UNVERIFIED_LIVE_FIELDS.copy(),
        notes=notes,
    )
