from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

from destination_stays_app.models.destination_models import (
    FlightSearchResponse as DestinationFlightSearchResponse,
    StaySearchResponse,
)
from destination_stays_app.tools.flight_tools import search_destination_flights
from destination_stays_app.tools.stay_tools import search_stays
from travel_app.models.travel_models import FlightSearchResponse, HotelSearchResponse
from travel_app.models.flight_enrichment_models import FlightInformationSummary
from travel_app.tools.flight_enrichment_tools import lookup_flight_information
from travel_app.tools.flight_tools import search_flights
from travel_app.tools.hotel_tools import search_hotels


def _tool_context(tool_name: str) -> SimpleNamespace:
    return SimpleNamespace(tool_name=tool_name, run_config=None)


def test_travel_app_tool_wrappers_map_service_errors() -> None:
    async def run() -> None:
        flight_json = await search_flights.on_invoke_tool(
            _tool_context("search_flights"),
            json.dumps(
                {
                    "destination": "Jamaica",
                    "origin": "DCA",
                    "destination_airports": ["MBJ"],
                    "start_date": "2026-10-10",
                    "end_date": "2026-10-17",
                    "limit": 10,
                }
            ),
        )
        hotel_json = await search_hotels.on_invoke_tool(
            _tool_context("search_hotels"),
            json.dumps(
                {
                    "destination": "Atlantis",
                    "check_in": "2026-10-10",
                    "check_out": "2026-10-17",
                    "limit": 5,
                }
            ),
        )

        flight_response = FlightSearchResponse.model_validate_json(flight_json)
        hotel_response = HotelSearchResponse.model_validate_json(hotel_json)

        assert flight_response.flights == []
        assert flight_response.error
        assert "BWI" in flight_response.error
        assert hotel_response.hotels == []
        assert hotel_response.error
        assert "Unsupported destination" in hotel_response.error

    asyncio.run(run())


def test_destination_stays_tool_wrappers_map_service_errors() -> None:
    async def run() -> None:
        flight_json = await search_destination_flights.on_invoke_tool(
            _tool_context("search_destination_flights"),
            json.dumps(
                {
                    "destination": "London",
                    "origin": "BWI",
                    "destination_airports": ["XXX"],
                    "start_date": "2026-10-10",
                    "end_date": "2026-10-17",
                    "limit": 10,
                }
            ),
        )
        stay_json = await search_stays.on_invoke_tool(
            _tool_context("search_stays"),
            json.dumps(
                {
                    "destination": "Atlantis",
                    "check_in": "2026-10-10",
                    "check_out": "2026-10-17",
                    "limit": 5,
                }
            ),
        )

        flight_response = DestinationFlightSearchResponse.model_validate_json(
            flight_json
        )
        stay_response = StaySearchResponse.model_validate_json(stay_json)

        assert flight_response.flights == []
        assert flight_response.error
        assert "Unsupported destination airport" in flight_response.error
        assert stay_response.stays == []
        assert stay_response.error
        assert "Unsupported destination" in stay_response.error

    asyncio.run(run())


def test_flight_enrichment_tool_returns_structured_unverified_summary() -> None:
    async def run() -> None:
        summary_json = await lookup_flight_information.on_invoke_tool(
            _tool_context("lookup_flight_information"),
            json.dumps(
                {
                    "flight_number": "UA 100",
                    "flight_date": "2026-10-10",
                }
            ),
        )

        summary = FlightInformationSummary.model_validate_json(summary_json)

        assert summary.flight_number == "UA100"
        assert summary.airline == "United Airlines"
        assert summary.real_time_status_verified is False
        assert "gate" in summary.unverified_fields

    asyncio.run(run())
