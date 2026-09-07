from __future__ import annotations

import asyncio
from datetime import date
from datetime import datetime

import pytest

from destination_stays_app.models.destination_models import PlaceResult
from destination_stays_app.orchestration import destination_orchestrator
from travel_app.models.flight_enrichment_models import FlightInformationSummary
from travel_app.models.travel_models import DestinationResult, Flight
from travel_app.orchestration import travel_orchestrator


def test_travel_orchestrator_correlates_destinations(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run_destination(
        agent,
        destination: str,
        start_date: date,
        end_date: date,
    ) -> DestinationResult:
        return DestinationResult(destination=destination)

    monkeypatch.setattr(
        travel_orchestrator,
        "_run_destination",
        fake_run_destination,
    )

    result = asyncio.run(
        travel_orchestrator.run_parallel_destination_searches_impl(
            date(2026, 10, 10),
            date(2026, 10, 17),
        )
    )

    assert result.origin == "BWI"
    assert [item.destination for item in result.destinations] == [
        "Jamaica",
        "Paris",
        "Hawaii",
    ]
    assert all(
        flight.enrichment is None
        for destination in result.destinations
        for flight in destination.flights
    )


def _mock_flights(count: int) -> list[Flight]:
    return [
        Flight(
            airline="American Airlines",
            flight_number=f"AA{100 + index}",
            origin_airport="BWI",
            destination_airport="MBJ",
            departure_time=datetime(2026, 10, 10, 6 + index, 10),
        )
        for index in range(count)
    ]


def test_travel_orchestrator_skips_enrichment_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    async def fake_run_destination(
        agent,
        destination: str,
        start_date: date,
        end_date: date,
    ) -> DestinationResult:
        return DestinationResult(destination=destination, flights=_mock_flights(2))

    async def fake_enrich_flight_information_service(**kwargs):
        calls.append(kwargs["flight_number"])
        return FlightInformationSummary(flight_number=kwargs["flight_number"])

    monkeypatch.setattr(travel_orchestrator, "_run_destination", fake_run_destination)
    monkeypatch.setattr(
        travel_orchestrator,
        "enrich_flight_information_service",
        fake_enrich_flight_information_service,
    )

    result = asyncio.run(
        travel_orchestrator.run_parallel_destination_searches_impl(
            date(2026, 10, 10),
            date(2026, 10, 17),
        )
    )

    assert calls == []
    assert all(
        flight.enrichment is None
        for destination in result.destinations
        for flight in destination.flights
    )


def test_travel_orchestrator_enriches_first_five_flights_per_destination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    async def fake_run_destination(
        agent,
        destination: str,
        start_date: date,
        end_date: date,
    ) -> DestinationResult:
        return DestinationResult(destination=destination, flights=_mock_flights(7))

    async def fake_enrich_flight_information_service(**kwargs):
        calls.append(kwargs["flight_number"])
        return FlightInformationSummary(
            flight_number=kwargs["flight_number"],
            flight_date=kwargs["flight_date"],
            airline="American Airlines",
        )

    monkeypatch.setattr(travel_orchestrator, "_run_destination", fake_run_destination)
    monkeypatch.setattr(
        travel_orchestrator,
        "enrich_flight_information_service",
        fake_enrich_flight_information_service,
    )

    result = asyncio.run(
        travel_orchestrator.run_parallel_destination_searches_impl(
            date(2026, 10, 10),
            date(2026, 10, 17),
            include_flight_enrichment=True,
            enrichment_limit=5,
        )
    )

    assert len(calls) == 15
    for destination in result.destinations:
        assert [flight.enrichment is not None for flight in destination.flights] == [
            True,
            True,
            True,
            True,
            True,
            False,
            False,
        ]


def test_travel_orchestrator_preserves_results_when_enrichment_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_run_destination(
        agent,
        destination: str,
        start_date: date,
        end_date: date,
    ) -> DestinationResult:
        return DestinationResult(destination=destination, flights=_mock_flights(1))

    async def fake_enrich_flight_information_service(**kwargs):
        raise RuntimeError("simulated enrichment failure")

    monkeypatch.setattr(travel_orchestrator, "_run_destination", fake_run_destination)
    monkeypatch.setattr(
        travel_orchestrator,
        "enrich_flight_information_service",
        fake_enrich_flight_information_service,
    )

    result = asyncio.run(
        travel_orchestrator.run_parallel_destination_searches_impl(
            date(2026, 10, 10),
            date(2026, 10, 17),
            include_flight_enrichment=True,
        )
    )

    for destination in result.destinations:
        flight = destination.flights[0]
        assert flight.flight_number == "AA100"
        assert flight.enrichment is not None
        assert flight.enrichment.real_time_status_verified is False
        assert any("simulated enrichment failure" in note for note in flight.enrichment.notes)


def test_destination_stays_orchestrator_preserves_agent_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_run_destination(
        agent,
        destination: str,
        start_date: date,
        end_date: date,
    ) -> PlaceResult:
        if destination == "London":
            return PlaceResult(
                destination=destination,
                agent_error="RuntimeError: simulated failure",
            )
        return PlaceResult(destination=destination)

    monkeypatch.setattr(
        destination_orchestrator,
        "_run_destination",
        fake_run_destination,
    )

    result = asyncio.run(
        destination_orchestrator.run_destination_stays_search_impl(
            date(2026, 10, 10),
            date(2026, 10, 17),
        )
    )

    assert [item.destination for item in result.places] == [
        "Dominican Republic",
        "London",
        "US Virgin Islands",
    ]
    assert result.places[1].agent_error == "RuntimeError: simulated failure"
    assert result.places[0].agent_error is None
    assert result.places[2].agent_error is None


def test_orchestrators_reject_invalid_date_ranges() -> None:
    with pytest.raises(ValueError, match="on or before"):
        asyncio.run(
            travel_orchestrator.run_parallel_destination_searches_impl(
                date(2026, 10, 17),
                date(2026, 10, 10),
            )
        )

    with pytest.raises(ValueError, match="on or before"):
        asyncio.run(
            destination_orchestrator.run_destination_stays_search_impl(
                date(2026, 10, 17),
                date(2026, 10, 10),
            )
        )
