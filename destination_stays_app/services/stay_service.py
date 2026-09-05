from __future__ import annotations

from datetime import date

from destination_stays_app.models.destination_models import Stay


STAY_CATALOG: dict[str, list[tuple[str, str, str, float, float, str]]] = {
    "Dominican Republic": [
        ("Mock Punta Cana Beach Resort", "Punta Cana", "Dominican Republic", 255.0, 4.5, "1 Demo Playa Rd"),
        ("Mock Santo Domingo Colonial Hotel", "Santo Domingo", "Dominican Republic", 195.0, 4.3, "20 Sample Zona St"),
        ("Mock Bavaro Garden Suites", "Bavaro", "Dominican Republic", 235.0, 4.4, "8 Example Palm Ave"),
        ("Mock La Romana Marina Inn", "La Romana", "Dominican Republic", 220.0, 4.2, "15 Test Marina Dr"),
        ("Mock Samana Bay Lodge", "Samana", "Dominican Republic", 210.0, 4.1, "3 Prototype Bay Ln"),
    ],
    "London": [
        ("Mock South Bank Hotel", "London", "England", 315.0, 4.5, "10 Example Walk"),
        ("Mock Kensington Garden House", "London", "England", 285.0, 4.4, "18 Demo Terrace"),
        ("Mock Shoreditch Rooms", "London", "England", 260.0, 4.2, "7 Prototype Lane"),
        ("Mock Covent Central Hotel", "London", "England", 340.0, 4.6, "25 Sample Street"),
        ("Mock Paddington Station Inn", "London", "England", 245.0, 4.1, "4 Test Mews"),
    ],
    "US Virgin Islands": [
        ("Mock Charlotte Amalie Harbor Stay", "Charlotte Amalie", "U.S. Virgin Islands", 285.0, 4.4, "100 Demo Harbor Rd"),
        ("Mock St. Thomas Beach Hotel", "St. Thomas", "U.S. Virgin Islands", 330.0, 4.5, "55 Sample Beach Ave"),
        ("Mock Christiansted Courtyard", "Christiansted", "U.S. Virgin Islands", 250.0, 4.2, "80 Example King St"),
        ("Mock Cruz Bay View Inn", "Cruz Bay", "U.S. Virgin Islands", 295.0, 4.3, "22 Prototype Hill Rd"),
        ("Mock Frederiksted Sunset Lodge", "Frederiksted", "U.S. Virgin Islands", 240.0, 4.1, "14 Test Shore Dr"),
    ],
}


async def search_stays_service(
    *,
    destination: str,
    check_in: date,
    check_out: date,
    limit: int = 5,
) -> list[Stay]:
    """
    Deterministic mock stay service.

    This is not live hotel availability. Replace this implementation with an
    authorized provider while keeping the same contract.
    """
    if check_in > check_out:
        raise ValueError("check_in must be on or before check_out")

    catalog = STAY_CATALOG.get(destination)
    if catalog is None:
        raise ValueError(f"Unsupported destination: {destination}")

    nights = max((check_out - check_in).days, 1)
    return [
        Stay(
            name=name,
            city=city,
            country_or_region=region,
            check_in=check_in,
            check_out=check_out,
            nightly_rate=nightly_rate,
            total_price=round(nightly_rate * nights, 2),
            rating=rating,
            address=address,
        )
        for name, city, region, nightly_rate, rating, address in catalog[:limit]
    ]
