from __future__ import annotations

from datetime import date

from agents import function_tool

from travel_app.models.flight_enrichment_models import FlightInformationSummary
from travel_app.services.flight_enrichment_service import (
    enrich_flight_information_service,
)


@function_tool
async def lookup_flight_information(
    flight_number: str,
    flight_date: str | None = None,
) -> str:
    """
    Enrich a flight number with conservative locally verifiable information.

    Args:
        flight_number: Airline code and flight number, such as AA1234.
        flight_date: Optional flight date in YYYY-MM-DD format.
    """
    try:
        parsed_date = date.fromisoformat(flight_date) if flight_date else None
        result = await enrich_flight_information_service(
            flight_number=flight_number,
            flight_date=parsed_date,
        )
        return result.model_dump_json()
    except Exception as exc:
        return FlightInformationSummary(
            flight_number=flight_number.strip().upper(),
            notes=[f"{type(exc).__name__}: {exc}"],
            unverified_fields=[
                "airline",
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
            ],
        ).model_dump_json()
