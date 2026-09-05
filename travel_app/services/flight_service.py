from __future__ import annotations

from datetime import date, datetime, time, timedelta
from itertools import cycle

from travel_app.models.travel_models import Flight


AIRPORTS: dict[str, tuple[str, str, str]] = {
    "MBJ": ("Montego Bay", "Jamaica", "Jamaica"),
    "KIN": ("Kingston", "Jamaica", "Jamaica"),
    "CDG": ("Paris", "France", "Paris"),
    "ORY": ("Paris", "France", "Paris"),
    "HNL": ("Honolulu", "Hawaii, USA", "Hawaii"),
    "OGG": ("Kahului / Maui", "Hawaii, USA", "Hawaii"),
    "KOA": ("Kona", "Hawaii, USA", "Hawaii"),
    "LIH": ("Lihue / Kauai", "Hawaii, USA", "Hawaii"),
}

DURATION_MINUTES = {
    "MBJ": 225,
    "KIN": 250,
    "CDG": 480,
    "ORY": 495,
    "HNL": 690,
    "OGG": 735,
    "KOA": 750,
    "LIH": 760,
}

BASE_PRICE = {
    "MBJ": 315.0,
    "KIN": 340.0,
    "CDG": 575.0,
    "ORY": 545.0,
    "HNL": 690.0,
    "OGG": 735.0,
    "KOA": 760.0,
    "LIH": 750.0,
}

AIRLINES = cycle(
    [
        ("AA", "American Airlines"),
        ("DL", "Delta Air Lines"),
        ("UA", "United Airlines"),
        ("WN", "Southwest Airlines"),
        ("B6", "JetBlue"),
    ]
)

DEPARTURE_TIMES = [
    time(6, 10),
    time(8, 45),
    time(11, 30),
    time(15, 20),
    time(19, 5),
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

    This is NOT real-time flight availability. Replace this implementation with
    Amadeus, Duffel, Sabre, Travelport, etc. while keeping the same contract.
    """
    if origin != "BWI":
        raise ValueError("This demo only supports BWI as the origin.")
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    unknown = [airport for airport in destination_airports if airport not in AIRPORTS]
    if unknown:
        raise ValueError(f"Unsupported destination airport(s): {', '.join(unknown)}")

    flights: list[Flight] = []
    sequence = 100
    current = start_date

    while current <= end_date:
        for airport_index, airport in enumerate(destination_airports):
            city, _region, logical_destination = AIRPORTS[airport]
            for departure_index, departure_clock in enumerate(DEPARTURE_TIMES):
                airline_code, airline_name = next(AIRLINES)
                departure = datetime.combine(current, departure_clock)
                duration = DURATION_MINUTES[airport]
                arrival = departure + timedelta(minutes=duration)

                price = (
                    BASE_PRICE[airport]
                    + airport_index * 17.0
                    + departure_index * 23.0
                    + (current - start_date).days * 11.0
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
                        nonstop=(
                            logical_destination == "Jamaica"
                            and departure_index % 2 == 0
                        ),
                        price=round(price, 2),
                        currency="USD",
                    )
                )
                sequence += 1

        current += timedelta(days=1)

    flights.sort(key=lambda flight: flight.departure_time)
    return flights[:limit]
