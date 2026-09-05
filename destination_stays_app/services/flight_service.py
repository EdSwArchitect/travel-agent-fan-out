from __future__ import annotations

from datetime import date, datetime, time, timedelta

from destination_stays_app.models.destination_models import Flight


AIRPORTS: dict[str, tuple[str, str, str]] = {
    "PUJ": ("Punta Cana", "Dominican Republic", "Dominican Republic"),
    "SDQ": ("Santo Domingo", "Dominican Republic", "Dominican Republic"),
    "LHR": ("London", "England", "London"),
    "LGW": ("London", "England", "London"),
    "STT": ("Charlotte Amalie", "U.S. Virgin Islands", "US Virgin Islands"),
    "STX": ("Christiansted", "U.S. Virgin Islands", "US Virgin Islands"),
}

DURATION_MINUTES = {
    "PUJ": 220,
    "SDQ": 230,
    "LHR": 450,
    "LGW": 465,
    "STT": 250,
    "STX": 265,
}

BASE_PRICE = {
    "PUJ": 335.0,
    "SDQ": 350.0,
    "LHR": 610.0,
    "LGW": 585.0,
    "STT": 390.0,
    "STX": 410.0,
}

AIRLINES = [
    ("AA", "American Airlines"),
    ("DL", "Delta Air Lines"),
    ("UA", "United Airlines"),
    ("B6", "JetBlue"),
    ("BA", "British Airways"),
]

DEPARTURE_TIMES = [
    time(6, 15),
    time(9, 30),
    time(12, 40),
    time(16, 25),
    time(20, 5),
]


async def search_flights_service(
    *,
    origin: str,
    destination_airports: list[str],
    start_date: date,
    end_date: date,
    limit: int = 10,
) -> list[Flight]:
    """
    Deterministic mock flight service.

    This is not live flight availability. Replace this implementation with an
    authorized provider while keeping the same contract.
    """
    if origin != "BWI":
        raise ValueError("This demo only supports BWI as the origin.")
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    unknown = [airport for airport in destination_airports if airport not in AIRPORTS]
    if unknown:
        raise ValueError(f"Unsupported destination airport(s): {', '.join(unknown)}")

    flights: list[Flight] = []
    sequence = 300
    current = start_date

    while current <= end_date:
        for airport_index, airport in enumerate(destination_airports):
            city, _region, logical_destination = AIRPORTS[airport]
            for departure_index, departure_clock in enumerate(DEPARTURE_TIMES):
                airline_code, airline_name = AIRLINES[
                    (airport_index + departure_index + current.day) % len(AIRLINES)
                ]
                departure = datetime.combine(current, departure_clock)
                duration = DURATION_MINUTES[airport]
                arrival = departure + timedelta(minutes=duration)
                price = (
                    BASE_PRICE[airport]
                    + airport_index * 19.0
                    + departure_index * 21.0
                    + (current - start_date).days * 13.0
                )

                flights.append(
                    Flight(
                        airline=airline_name,
                        flight_number=f"{airline_code}{sequence}",
                        origin_airport=origin,
                        destination_airport=airport,
                        destination_city=city,
                        departure_time=departure,
                        arrival_time=arrival,
                        duration=f"{duration // 60}h {duration % 60:02d}m",
                        nonstop=logical_destination != "London",
                        price=round(price, 2),
                    )
                )
                sequence += 1

        current += timedelta(days=1)

    flights.sort(key=lambda flight: flight.departure_time)
    return flights[:limit]
