from __future__ import annotations

from destination_stays_app.models.destination_models import (
    DestinationStaysResult,
    PlaceResult,
)
from travel_app.models.travel_models import DestinationResult, TravelSearchResult


def test_travel_search_result_serializes_dates_as_json_strings() -> None:
    result = TravelSearchResult(
        start_date="2026-10-10",
        end_date="2026-10-17",
        destinations=[DestinationResult(destination="Paris")],
    )

    dumped = result.model_dump(mode="json")

    assert dumped["origin"] == "BWI"
    assert dumped["start_date"] == "2026-10-10"
    assert dumped["end_date"] == "2026-10-17"
    assert dumped["destinations"][0]["destination"] == "Paris"


def test_destination_stays_result_serializes_dates_as_json_strings() -> None:
    result = DestinationStaysResult(
        start_date="2026-10-10",
        end_date="2026-10-17",
        places=[PlaceResult(destination="London")],
    )

    dumped = result.model_dump(mode="json")

    assert dumped["origin"] == "BWI"
    assert dumped["start_date"] == "2026-10-10"
    assert dumped["end_date"] == "2026-10-17"
    assert dumped["places"][0]["destination"] == "London"
