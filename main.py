from __future__ import annotations

import asyncio
import json
import os
import sys

from agents import Runner

from travel_app.agents.router_agent import router_agent
from travel_app.models.travel_models import TravelSearchResult


def print_human_readable(result: TravelSearchResult) -> None:
    print(f"\nOrigin: {result.origin}")
    print(f"Dates: {result.start_date} through {result.end_date}")

    for destination in result.destinations:
        print("\n" + "=" * 72)
        print(destination.destination.upper())
        print("=" * 72)

        if destination.agent_error:
            print(f"DESTINATION AGENT ERROR: {destination.agent_error}")
            continue

        print("\nFLIGHTS FROM BWI")
        if destination.flight_error:
            print(f"Flight search error: {destination.flight_error}")
        elif not destination.flights:
            print("No flights returned.")
        else:
            for index, flight in enumerate(destination.flights, start=1):
                price = (
                    f"{flight.currency} {flight.price:.2f}"
                    if flight.price is not None and flight.currency
                    else "price unavailable"
                )
                arrival = (
                    flight.arrival_time.isoformat(sep=" ", timespec="minutes")
                    if flight.arrival_time
                    else "arrival unavailable"
                )
                print(
                    f"{index:2d}. {flight.airline} {flight.flight_number} | "
                    f"{flight.origin_airport}->{flight.destination_airport} | "
                    f"{flight.departure_time.isoformat(sep=' ', timespec='minutes')} -> "
                    f"{arrival} | {price}"
                )

        print("\nHOTELS")
        if destination.hotel_error:
            print(f"Hotel search error: {destination.hotel_error}")
        elif not destination.hotels:
            print("No hotels returned.")
        else:
            for index, hotel in enumerate(destination.hotels, start=1):
                rate = (
                    f"{hotel.currency} {hotel.nightly_rate:.2f}/night"
                    if hotel.nightly_rate is not None and hotel.currency
                    else "rate unavailable"
                )
                total = (
                    f"{hotel.currency} {hotel.total_price:.2f} total"
                    if hotel.total_price is not None and hotel.currency
                    else "total unavailable"
                )
                print(
                    f"{index}. {hotel.name} | "
                    f"{hotel.city}, {hotel.country_or_region} | "
                    f"{rate} | {total}"
                )


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and provide your key."
        )

    request = (
        " ".join(sys.argv[1:]).strip()
        if len(sys.argv) > 1
        else "Find flights and hotels between October 10, 2026 and October 17, 2026."
    )

    print(f"Request: {request}")

    run_result = await Runner.run(router_agent, request)
    result = run_result.final_output_as(
        TravelSearchResult,
        raise_if_incorrect_type=True,
    )

    print_human_readable(result)

    print("\n" + "=" * 72)
    print("JSON RESULT")
    print("=" * 72)
    print(json.dumps(result.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
