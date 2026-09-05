from __future__ import annotations

from datetime import date

from agents import function_tool

from destination_stays_app.models.destination_models import StaySearchResponse
from destination_stays_app.services.stay_service import search_stays_service


@function_tool
async def search_stays(
    destination: str,
    check_in: str,
    check_out: str,
    limit: int = 5,
) -> str:
    """
    Search mock stays for a destination.

    Args:
        destination: Dominican Republic, London, or US Virgin Islands.
        check_in: Check-in date in YYYY-MM-DD format.
        check_out: Check-out date in YYYY-MM-DD format.
        limit: Maximum number of stays to return.
    """
    try:
        stays = await search_stays_service(
            destination=destination,
            check_in=date.fromisoformat(check_in),
            check_out=date.fromisoformat(check_out),
            limit=limit,
        )
        return StaySearchResponse(
            destination=destination,
            stays=stays,
        ).model_dump_json()
    except Exception as exc:
        return StaySearchResponse(
            destination=destination,
            error=f"{type(exc).__name__}: {exc}",
        ).model_dump_json()
