from __future__ import annotations

from datetime import date

from travel_app.models.travel_models import Hotel


HOTEL_CATALOG: dict[str, list[tuple[str, str, str, float, float, str]]] = {
    "Jamaica": [
        ("Mock Montego Bay Harbor Resort", "Montego Bay", "Jamaica", 245.0, 4.4, "1 Demo Bay Rd"),
        ("Mock Kingston Garden Hotel", "Kingston", "Jamaica", 189.0, 4.2, "20 Sample Ave"),
        ("Mock Negril Sunset Inn", "Negril", "Jamaica", 215.0, 4.5, "8 Example Beach Rd"),
        ("Mock Ocho Rios Palm Hotel", "Ocho Rios", "Jamaica", 230.0, 4.3, "15 Test Coast Hwy"),
        ("Mock Blue Mountain Lodge", "Kingston", "Jamaica", 175.0, 4.1, "3 Prototype Ln"),
    ],
    "Paris": [
        ("Mock Rive Gauche Hotel", "Paris", "France", 285.0, 4.5, "10 Rue Exemple"),
        ("Mock Montmartre House", "Paris", "France", 240.0, 4.3, "18 Rue Demo"),
        ("Mock Marais Boutique", "Paris", "France", 315.0, 4.6, "7 Rue Prototype"),
        ("Mock Opera Central", "Paris", "France", 270.0, 4.4, "25 Avenue Exemple"),
        ("Mock Latin Quarter Inn", "Paris", "France", 225.0, 4.2, "4 Rue Test"),
    ],
    "Hawaii": [
        ("Mock Waikiki Shore Hotel", "Honolulu", "Hawaii, USA", 330.0, 4.4, "100 Demo Beach Ave"),
        ("Mock Maui Garden Resort", "Kahului", "Hawaii, USA", 365.0, 4.5, "55 Sample Palm Rd"),
        ("Mock Kona Bay Hotel", "Kona", "Hawaii, USA", 310.0, 4.3, "80 Example Alii Dr"),
        ("Mock Kauai Coast Inn", "Lihue", "Hawaii, USA", 345.0, 4.4, "22 Prototype Coast Rd"),
        ("Mock Honolulu Harbor Hotel", "Honolulu", "Hawaii, USA", 295.0, 4.2, "14 Test Harbor St"),
    ],
}


async def search_hotels_service(
    *,
    destination: str,
    check_in: date,
    check_out: date,
    limit: int = 5,
) -> list[Hotel]:
    """
    Deterministic mock hotel service.

    This is NOT real-time hotel availability. Replace this implementation with
    an authorized hotel provider while keeping the same contract.
    """
    if check_in > check_out:
        raise ValueError("check_in must be on or before check_out")

    catalog = HOTEL_CATALOG.get(destination)
    if catalog is None:
        raise ValueError(f"Unsupported destination: {destination}")

    nights = max((check_out - check_in).days, 1)
    return [
        Hotel(
            name=name,
            city=city,
            country_or_region=region,
            check_in=check_in,
            check_out=check_out,
            nightly_rate=nightly_rate,
            total_price=round(nightly_rate * nights, 2),
            currency="USD",
            rating=rating,
            address=address,
        )
        for name, city, region, nightly_rate, rating, address in catalog[:limit]
    ]
