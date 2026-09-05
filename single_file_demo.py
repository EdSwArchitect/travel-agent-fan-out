"""
Single-file learning version.

The flight and hotel data are deterministic MOCK DATA and are not real-time availability.

Flow:
    Travel Router Agent
      -> run_parallel_destination_searches tool
          -> asyncio.gather(Jamaican Agent, Paris Agent, Hawaii Agent)
              -> flight tool
              -> SAME Hotel Agent exposed with Agent.as_tool()
          -> TravelSearchResult
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import date, datetime, time, timedelta
from itertools import cycle

from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")


def model_kwargs() -> dict[str, str]:
    return {"model": MODEL} if MODEL else {}


class Flight(BaseModel):
    airline: str
    flight_number: str
    origin_airport: str
    destination_airport: str
    destination_city: str | None = None
    departure_time: datetime
    arrival_time: datetime | None = None
    duration: str | None = None
    nonstop: bool | None = None
    price: float | None = None
    currency: str | None = None


class Hotel(BaseModel):
    name: str
    city: str
    country_or_region: str
    check_in: date
    check_out: date
    nightly_rate: float | None = None
    total_price: float | None = None
    currency: str | None = None
    rating: float | None = None
    address: str | None = None


class FlightSearchResponse(BaseModel):
    destination: str
    flights: list[Flight] = Field(default_factory=list)
    error: str | None = None


class HotelSearchResponse(BaseModel):
    destination: str
    hotels: list[Hotel] = Field(default_factory=list)
    error: str | None = None


class DestinationResult(BaseModel):
    destination: str
    flights: list[Flight] = Field(default_factory=list)
    hotels: list[Hotel] = Field(default_factory=list)
    flight_error: str | None = None
    hotel_error: str | None = None
    agent_error: str | None = None


class TravelSearchResult(BaseModel):
    origin: str = "BWI"
    start_date: date
    end_date: date
    destinations: list[DestinationResult] = Field(default_factory=list)


AIRPORTS = {
    "MBJ": ("Montego Bay", 225, 315.0),
    "KIN": ("Kingston", 250, 340.0),
    "CDG": ("Paris", 480, 575.0),
    "ORY": ("Paris", 495, 545.0),
    "HNL": ("Honolulu", 690, 690.0),
    "OGG": ("Kahului / Maui", 735, 735.0),
    "KOA": ("Kona", 750, 760.0),
    "LIH": ("Lihue / Kauai", 760, 750.0),
}

HOTELS = {
    "Jamaica": [
        ("Mock Montego Bay Harbor Resort", "Montego Bay", "Jamaica", 245.0, 4.4),
        ("Mock Kingston Garden Hotel", "Kingston", "Jamaica", 189.0, 4.2),
        ("Mock Negril Sunset Inn", "Negril", "Jamaica", 215.0, 4.5),
        ("Mock Ocho Rios Palm Hotel", "Ocho Rios", "Jamaica", 230.0, 4.3),
        ("Mock Blue Mountain Lodge", "Kingston", "Jamaica", 175.0, 4.1),
    ],
    "Paris": [
        ("Mock Rive Gauche Hotel", "Paris", "France", 285.0, 4.5),
        ("Mock Montmartre House", "Paris", "France", 240.0, 4.3),
        ("Mock Marais Boutique", "Paris", "France", 315.0, 4.6),
        ("Mock Opera Central", "Paris", "France", 270.0, 4.4),
        ("Mock Latin Quarter Inn", "Paris", "France", 225.0, 4.2),
    ],
    "Hawaii": [
        ("Mock Waikiki Shore Hotel", "Honolulu", "Hawaii, USA", 330.0, 4.4),
        ("Mock Maui Garden Resort", "Kahului", "Hawaii, USA", 365.0, 4.5),
        ("Mock Kona Bay Hotel", "Kona", "Hawaii, USA", 310.0, 4.3),
        ("Mock Kauai Coast Inn", "Lihue", "Hawaii, USA", 345.0, 4.4),
        ("Mock Honolulu Harbor Hotel", "Honolulu", "Hawaii, USA", 295.0, 4.2),
    ],
}


@function_tool
async def search_flights(
    destination: str,
    origin: str,
    destination_airports: list[str],
    start_date: str,
    end_date: str,
    limit: int = 10,
) -> str:
    """Return deterministic mock flights; not real-time availability."""
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        if start > end:
            raise ValueError("start_date must be on or before end_date")

        airline_cycle = cycle(
            [
                ("AA", "American Airlines"),
                ("DL", "Delta Air Lines"),
                ("UA", "United Airlines"),
                ("WN", "Southwest Airlines"),
                ("B6", "JetBlue"),
            ]
        )
        departure_times = [
            time(6, 10),
            time(8, 45),
            time(11, 30),
            time(15, 20),
            time(19, 5),
        ]
        flights: list[Flight] = []
        seq = 100
        current = start

        while current <= end:
            for airport_index, airport in enumerate(destination_airports):
                city, duration, base_price = AIRPORTS[airport]
                for departure_index, clock in enumerate(departure_times):
                    code, airline = next(airline_cycle)
                    departure = datetime.combine(current, clock)
                    arrival = departure + timedelta(minutes=duration)
                    flights.append(
                        Flight(
                            airline=airline,
                            flight_number=f"{code}{seq}",
                            origin_airport=origin,
                            destination_airport=airport,
                            destination_city=city,
                            departure_time=departure,
                            arrival_time=arrival,
                            duration=f"{duration // 60}h {duration % 60:02d}m",
                            nonstop=(
                                destination == "Jamaica"
                                and departure_index % 2 == 0
                            ),
                            price=round(
                                base_price
                                + airport_index * 17
                                + departure_index * 23
                                + (current - start).days * 11,
                                2,
                            ),
                            currency="USD",
                        )
                    )
                    seq += 1
            current += timedelta(days=1)

        flights.sort(key=lambda flight: flight.departure_time)
        return FlightSearchResponse(
            destination=destination,
            flights=flights[:limit],
        ).model_dump_json()
    except Exception as exc:
        return FlightSearchResponse(
            destination=destination,
            error=f"{type(exc).__name__}: {exc}",
        ).model_dump_json()


@function_tool
async def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    limit: int = 5,
) -> str:
    """Return deterministic mock hotels; not real-time availability."""
    try:
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
        if start > end:
            raise ValueError("check_in must be on or before check_out")

        nights = max((end - start).days, 1)
        hotels = [
            Hotel(
                name=name,
                city=city,
                country_or_region=region,
                check_in=start,
                check_out=end,
                nightly_rate=rate,
                total_price=round(rate * nights, 2),
                currency="USD",
                rating=rating,
                address=None,
            )
            for name, city, region, rate, rating in HOTELS[destination][:limit]
        ]
        return HotelSearchResponse(
            destination=destination,
            hotels=hotels,
        ).model_dump_json()
    except Exception as exc:
        return HotelSearchResponse(
            destination=destination,
            error=f"{type(exc).__name__}: {exc}",
        ).model_dump_json()


hotel_agent = Agent(
    name="Hotel Agent",
    instructions=(
        "You are the ONE shared Hotel Agent. "
        "Call search_hotels exactly once with limit=5. "
        "Never invent hotel data. Return HotelSearchResponse."
    ),
    tools=[search_hotels],
    output_type=HotelSearchResponse,
    **model_kwargs(),
)


async def extract_hotel_output(run_result) -> str:
    return run_result.final_output_as(
        HotelSearchResponse,
        raise_if_incorrect_type=True,
    ).model_dump_json()


hotel_tool = hotel_agent.as_tool(
    tool_name="find_hotels",
    tool_description="Use the shared Hotel Agent to find five mock hotels.",
    custom_output_extractor=extract_hotel_output,
)


def make_destination_agent(
    name: str,
    destination: str,
    airports: list[str],
) -> Agent:
    return Agent(
        name=name,
        instructions=(
            f"You are the {destination} specialist. "
            f"Call search_flights exactly once with origin='BWI', "
            f"destination='{destination}', destination_airports={airports!r}, limit=10, "
            "and the supplied dates. "
            f"Call the shared find_hotels tool exactly once for destination='{destination}' "
            "using the same dates. "
            "Return DestinationResult. Copy tool data exactly and never invent missing data."
        ),
        tools=[search_flights, hotel_tool],
        output_type=DestinationResult,
        **model_kwargs(),
    )


jamaican_agent = make_destination_agent(
    "Jamaican Agent", "Jamaica", ["MBJ", "KIN"]
)
paris_agent = make_destination_agent(
    "Paris Agent", "Paris", ["CDG", "ORY"]
)
hawaii_agent = make_destination_agent(
    "Hawaii Agent", "Hawaii", ["HNL", "OGG", "KOA", "LIH"]
)


async def run_destination(
    agent: Agent,
    destination: str,
    start: date,
    end: date,
) -> DestinationResult:
    try:
        run_result = await Runner.run(
            agent,
            f"Destination: {destination}\nStart date: {start}\nEnd date: {end}",
        )
        return run_result.final_output_as(
            DestinationResult,
            raise_if_incorrect_type=True,
        )
    except Exception as exc:
        return DestinationResult(
            destination=destination,
            agent_error=f"{type(exc).__name__}: {exc}",
        )


@function_tool
async def run_parallel_destination_searches(
    start_date: str,
    end_date: str,
) -> str:
    """Run the three destination agents concurrently and return correlated JSON."""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    if start > end:
        raise ValueError("start_date must be on or before end_date")

    # GUARANTEED PARALLEL FAN-OUT:
    jamaica_task = run_destination(jamaican_agent, "Jamaica", start, end)
    paris_task = run_destination(paris_agent, "Paris", start, end)
    hawaii_task = run_destination(hawaii_agent, "Hawaii", start, end)

    jamaica, paris, hawaii = await asyncio.gather(
        jamaica_task,
        paris_task,
        hawaii_task,
    )

    # FAN-IN:
    return TravelSearchResult(
        origin="BWI",
        start_date=start,
        end_date=end,
        destinations=[jamaica, paris, hawaii],
    ).model_dump_json()


router_agent = Agent(
    name="Travel Router Agent",
    instructions=(
        "Extract start/end dates from the user request. "
        "Do not search flights or hotels yourself. "
        "Call run_parallel_destination_searches exactly once using ISO dates. "
        "Preserve its returned data exactly and return TravelSearchResult."
    ),
    tools=[run_parallel_destination_searches],
    output_type=TravelSearchResult,
    **model_kwargs(),
)


async def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required.")

    prompt = (
        "Find flights and hotels between "
        "October 10, 2026 and October 17, 2026."
    )

    run_result = await Runner.run(router_agent, prompt)
    travel = run_result.final_output_as(
        TravelSearchResult,
        raise_if_incorrect_type=True,
    )
    print(json.dumps(travel.model_dump(mode="json"), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
