from __future__ import annotations

import asyncio
import json
from datetime import date

from agents import Runner, function_tool

from destination_stays_app.agents.dominican_agent import dominican_agent
from destination_stays_app.agents.london_agent import london_agent
from destination_stays_app.agents.us_virgin_islands_agent import (
    us_virgin_islands_agent,
)
from destination_stays_app.models.destination_models import (
    DestinationStaysResult,
    PlaceResult,
)


def _destination_input(
    destination: str,
    start_date: date,
    end_date: date,
) -> str:
    return (
        f"Destination: {destination}\n"
        "Origin: BWI\n"
        f"Start date: {start_date.isoformat()}\n"
        f"End date: {end_date.isoformat()}\n"
        "Return the required ten flights and five stays using your tools."
    )


async def _run_destination(
    agent,
    destination: str,
    start_date: date,
    end_date: date,
) -> PlaceResult:
    try:
        result = await Runner.run(
            agent,
            _destination_input(destination, start_date, end_date),
        )
        return result.final_output_as(
            PlaceResult,
            raise_if_incorrect_type=True,
        )
    except Exception as exc:
        return PlaceResult(
            destination=destination,
            agent_error=f"{type(exc).__name__}: {exc}",
        )


async def run_destination_stays_search_impl(
    start_date: date,
    end_date: date,
) -> DestinationStaysResult:
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    dominican_task = _run_destination(
        dominican_agent, "Dominican Republic", start_date, end_date
    )
    london_task = _run_destination(london_agent, "London", start_date, end_date)
    usvi_task = _run_destination(
        us_virgin_islands_agent, "US Virgin Islands", start_date, end_date
    )

    dominican, london, usvi = await asyncio.gather(
        dominican_task,
        london_task,
        usvi_task,
    )

    return DestinationStaysResult(
        origin="BWI",
        start_date=start_date,
        end_date=end_date,
        places=[dominican, london, usvi],
    )


@function_tool
async def run_destination_stays_search(
    start_date: str,
    end_date: str,
) -> str:
    """
    Run Dominican Republic, London, and US Virgin Islands agents concurrently.

    Args:
        start_date: Inclusive start date in YYYY-MM-DD format.
        end_date: Inclusive end date in YYYY-MM-DD format.

    Returns:
        JSON DestinationStaysResult grouped by destination.
    """
    try:
        result = await run_destination_stays_search_impl(
            date.fromisoformat(start_date),
            date.fromisoformat(end_date),
        )
        return result.model_dump_json()
    except Exception as exc:
        return json.dumps({"error": f"{type(exc).__name__}: {exc}"})
