from __future__ import annotations

from datetime import date

from agents import function_tool

from travel_app.models.travel_models import FlightSearchResponse
from travel_app.services.flight_service import search_flights_service


@function_tool
async def search_flights(
    destination: str,
    origin: str,
    destination_airports: list[str],
    start_date: str,
    end_date: str,
    limit: int = 10,
) -> str:
    """
    Search mock flights from an origin to one or more destination airports.

    Args:
        destination: Jamaica, Paris, or Hawaii.
        origin: Origin IATA code; this demo expects BWI.
        destination_airports: Destination IATA airport codes.
        start_date: Inclusive start date in YYYY-MM-DD format.
        end_date: Inclusive end date in YYYY-MM-DD format.
        limit: Maximum number of flights to return.
    """
    try:
        flights = await search_flights_service(
            origin=origin,
            destination_airports=destination_airports,
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            limit=limit,
        )
        return FlightSearchResponse(
            destination=destination,
            flights=flights,
        ).model_dump_json()
    except Exception as exc:
        return FlightSearchResponse(
            destination=destination,
            error=f"{type(exc).__name__}: {exc}",
        ).model_dump_json()
