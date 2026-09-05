from __future__ import annotations

from datetime import date

from agents import function_tool

from travel_app.models.travel_models import HotelSearchResponse
from travel_app.services.hotel_service import search_hotels_service


@function_tool
async def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    limit: int = 5,
) -> str:
    """
    Search mock hotels for a destination.

    Args:
        destination: Jamaica, Paris, or Hawaii.
        check_in: Check-in date in YYYY-MM-DD format.
        check_out: Check-out date in YYYY-MM-DD format.
        limit: Maximum number of hotels to return.
    """
    try:
        hotels = await search_hotels_service(
            destination=destination,
            check_in=date.fromisoformat(check_in),
            check_out=date.fromisoformat(check_out),
            limit=limit,
        )
        return HotelSearchResponse(
            destination=destination,
            hotels=hotels,
        ).model_dump_json()
    except Exception as exc:
        return HotelSearchResponse(
            destination=destination,
            error=f"{type(exc).__name__}: {exc}",
        ).model_dump_json()
