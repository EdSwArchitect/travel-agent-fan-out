from __future__ import annotations

import asyncio
import json
import os
import sys

from agents import Runner

from travel_app.agents.flight_enrichment_agent import flight_enrichment_agent
from travel_app.models.flight_enrichment_models import FlightInformationSummary


def print_human_readable(result: FlightInformationSummary) -> None:
    print(f"\nFlight: {result.flight_number}")
    print(f"Date: {result.flight_date or 'not provided'}")
    print(f"Airline: {result.airline or 'unverified'}")
    print(
        f"Route: {result.departure_airport or 'unverified'} -> "
        f"{result.arrival_airport or 'unverified'}"
    )
    print(f"Scheduled departure: {result.scheduled_departure or 'unverified'}")
    print(f"Scheduled arrival: {result.scheduled_arrival or 'unverified'}")
    print(f"Current status: {result.current_status or 'unverified'}")
    print(
        f"Gate/terminal: {result.gate or 'unverified'} / "
        f"{result.terminal or 'unverified'}"
    )
    print(f"Aircraft: {result.aircraft_type or 'unverified'}")
    print(f"Real-time status verified: {result.real_time_status_verified}")

    if result.notes:
        print("\nNotes")
        for note in result.notes:
            print(f"- {note}")

    if result.unverified_fields:
        print("\nUnverified fields")
        for field in result.unverified_fields:
            print(f"- {field}")


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and provide your key."
        )

    request = (
        " ".join(sys.argv[1:]).strip()
        if len(sys.argv) > 1
        else "Enrich flight AA1234 for October 10, 2026."
    )

    print(f"Request: {request}")

    run_result = await Runner.run(flight_enrichment_agent, request)
    result = run_result.final_output_as(
        FlightInformationSummary,
        raise_if_incorrect_type=True,
    )

    print_human_readable(result)

    print("\n" + "=" * 72)
    print("JSON RESULT")
    print("=" * 72)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
