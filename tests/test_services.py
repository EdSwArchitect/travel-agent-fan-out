from __future__ import annotations

import asyncio
from datetime import date

import pytest

from destination_stays_app.services.flight_service import (
    search_flights_service as search_destination_flights_service,
)
from destination_stays_app.services.stay_service import search_stays_service
from travel_app.services.flight_service import search_flights_service
from travel_app.services.flight_enrichment_service import (
    enrich_flight_information_service,
)
from travel_app.services.hotel_service import search_hotels_service


def test_travel_app_services_return_requested_limits() -> None:
    async def run() -> None:
        flights = await search_flights_service(
            origin="BWI",
            destination_airports=["MBJ", "KIN"],
            start_date=date(2026, 10, 10),
            end_date=date(2026, 10, 17),
            limit=10,
        )
        hotels = await search_hotels_service(
            destination="Jamaica",
            check_in=date(2026, 10, 10),
            check_out=date(2026, 10, 17),
            limit=5,
        )

        assert len(flights) == 10
        assert len(hotels) == 5
        assert all(flight.origin_airport == "BWI" for flight in flights)
        assert all(hotel.check_in == date(2026, 10, 10) for hotel in hotels)

    asyncio.run(run())


def test_destination_stays_services_return_requested_limits() -> None:
    async def run() -> None:
        flights = await search_destination_flights_service(
            origin="BWI",
            destination_airports=["LHR", "LGW"],
            start_date=date(2026, 10, 10),
            end_date=date(2026, 10, 17),
            limit=10,
        )
        stays = await search_stays_service(
            destination="London",
            check_in=date(2026, 10, 10),
            check_out=date(2026, 10, 17),
            limit=5,
        )

        assert len(flights) == 10
        assert len(stays) == 5
        assert all(flight.origin_airport == "BWI" for flight in flights)
        assert all(stay.city == "London" for stay in stays)

    asyncio.run(run())


def test_services_reject_invalid_inputs() -> None:
    async def run() -> None:
        with pytest.raises(ValueError, match="BWI"):
            await search_flights_service(
                origin="DCA",
                destination_airports=["MBJ"],
                start_date=date(2026, 10, 10),
                end_date=date(2026, 10, 17),
            )

        with pytest.raises(ValueError, match="Unsupported destination airport"):
            await search_destination_flights_service(
                origin="BWI",
                destination_airports=["XXX"],
                start_date=date(2026, 10, 10),
                end_date=date(2026, 10, 17),
            )

        with pytest.raises(ValueError, match="on or before"):
            await search_hotels_service(
                destination="Jamaica",
                check_in=date(2026, 10, 17),
                check_out=date(2026, 10, 10),
            )

        with pytest.raises(ValueError, match="Unsupported destination"):
            await search_stays_service(
                destination="Atlantis",
                check_in=date(2026, 10, 10),
                check_out=date(2026, 10, 17),
            )

    asyncio.run(run())


def test_flight_enrichment_service_identifies_airline_without_live_status() -> None:
    async def run() -> None:
        summary = await enrich_flight_information_service(
            flight_number="aa 1234",
            flight_date=date(2026, 10, 10),
        )

        assert summary.flight_number == "AA1234"
        assert summary.flight_date == date(2026, 10, 10)
        assert summary.airline == "American Airlines"
        assert summary.requires_date is False
        assert summary.real_time_status_verified is False
        assert "current_status" in summary.unverified_fields

    asyncio.run(run())


def test_flight_enrichment_service_identifies_three_letter_prefix() -> None:
    async def run() -> None:
        summary = await enrich_flight_information_service(flight_number="AAL123")

        assert summary.flight_number == "AAL123"
        assert summary.airline == "American Airlines"

    asyncio.run(run())


def test_flight_enrichment_service_requires_date_for_live_lookup() -> None:
    async def run() -> None:
        summary = await enrich_flight_information_service(flight_number="DL42")

        assert summary.airline == "Delta Air Lines"
        assert summary.requires_date is True
        assert any("flight date" in note for note in summary.notes)

    asyncio.run(run())
