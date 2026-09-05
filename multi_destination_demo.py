from __future__ import annotations

import asyncio
import json
import os
import sys

from agents import Runner

from destination_stays_app.agents.router_agent import router_agent
from destination_stays_app.models.destination_models import DestinationStaysResult


def print_human_readable(result: DestinationStaysResult) -> None:
    print(f"\nOrigin: {result.origin}")
    print(f"Dates: {result.start_date} through {result.end_date}")

    for place in result.places:
        print("\n" + "=" * 72)
        print(place.destination.upper())
        print("=" * 72)

        if place.agent_error:
            print(f"DESTINATION AGENT ERROR: {place.agent_error}")
            continue

        print("\nFLIGHTS FROM BWI")
        if place.flight_error:
            print(f"Flight search error: {place.flight_error}")
        elif not place.flights:
            print("No flights returned.")
        else:
            for index, flight in enumerate(place.flights, start=1):
                print(
                    f"{index:2d}. {flight.airline} {flight.flight_number} | "
                    f"{flight.origin_airport}->{flight.destination_airport} | "
                    f"{flight.departure_time.isoformat(sep=' ', timespec='minutes')} -> "
                    f"{flight.arrival_time.isoformat(sep=' ', timespec='minutes')} | "
                    f"{flight.duration} | {flight.currency} {flight.price:.2f}"
                )

        print("\nSTAYS")
        if place.stay_error:
            print(f"Stay search error: {place.stay_error}")
        elif not place.stays:
            print("No stays returned.")
        else:
            for index, stay in enumerate(place.stays, start=1):
                print(
                    f"{index}. {stay.name} | "
                    f"{stay.city}, {stay.country_or_region} | "
                    f"{stay.currency} {stay.nightly_rate:.2f}/night | "
                    f"{stay.currency} {stay.total_price:.2f} total"
                )


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and provide your key."
        )

    request = (
        " ".join(sys.argv[1:]).strip()
        if len(sys.argv) > 1
        else "Find flights and stays between October 10, 2026 and October 17, 2026."
    )

    print(f"Request: {request}")

    run_result = await Runner.run(router_agent, request)
    result = run_result.final_output_as(
        DestinationStaysResult,
        raise_if_incorrect_type=True,
    )

    print_human_readable(result)

    print("\n" + "=" * 72)
    print("JSON RESULT")
    print("=" * 72)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
