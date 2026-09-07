from __future__ import annotations

from destination_stays_app.models.destination_models import (
    DestinationStaysResult,
    PlaceResult,
)
from travel_app.models.flight_enrichment_models import FlightInformationSummary
from travel_app.models.travel_models import DestinationResult, Flight, TravelSearchResult


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


def test_flight_enrichment_summary_serializes_date_as_json_string() -> None:
    summary = FlightInformationSummary(
        flight_number="AA1234",
        flight_date="2026-10-10",
        airline="American Airlines",
    )

    dumped = summary.model_dump(mode="json")

    assert dumped["flight_number"] == "AA1234"
    assert dumped["flight_date"] == "2026-10-10"
    assert dumped["airline"] == "American Airlines"


def test_flight_serializes_optional_enrichment_only_when_present() -> None:
    flight = Flight(
        airline="American Airlines",
        flight_number="AA1234",
        origin_airport="BWI",
        destination_airport="MBJ",
        departure_time="2026-10-10T06:10:00",
    )

    assert "enrichment" not in flight.model_dump(mode="json")

    flight.enrichment = FlightInformationSummary(
        flight_number="AA1234",
        flight_date="2026-10-10",
        airline="American Airlines",
    )

    dumped = flight.model_dump(mode="json")

    assert dumped["enrichment"]["flight_number"] == "AA1234"
    assert dumped["enrichment"]["flight_date"] == "2026-10-10"
