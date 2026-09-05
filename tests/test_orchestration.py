from __future__ import annotations

import asyncio
from datetime import date

import pytest

from destination_stays_app.models.destination_models import PlaceResult
from destination_stays_app.orchestration import destination_orchestrator
from travel_app.models.travel_models import DestinationResult
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
