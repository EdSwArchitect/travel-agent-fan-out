from __future__ import annotations

import asyncio
import json
from datetime import date

from agents import Runner, function_tool

from travel_app.agents.hawaii_agent import hawaii_agent
from travel_app.agents.jamaican_agent import jamaican_agent
from travel_app.agents.paris_agent import paris_agent
from travel_app.models.travel_models import DestinationResult, TravelSearchResult


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
        "Return the required ten flights and five hotels using your tools."
    )


async def _run_destination(
    agent,
    destination: str,
    start_date: date,
    end_date: date,
) -> DestinationResult:
    try:
        result = await Runner.run(
            agent,
            _destination_input(destination, start_date, end_date),
        )
        return result.final_output_as(
            DestinationResult,
            raise_if_incorrect_type=True,
        )
    except Exception as exc:
        # Failure isolation: one agent failure does not cancel the other results.
        return DestinationResult(
            destination=destination,
            agent_error=f"{type(exc).__name__}: {exc}",
        )


async def run_parallel_destination_searches_impl(
    start_date: date,
    end_date: date,
) -> TravelSearchResult:
    if start_date > end_date:
        raise ValueError("start_date must be on or before end_date")

    # FAN OUT -- these are three separate Runner.run(...) calls.
    jamaica_task = _run_destination(
        jamaican_agent, "Jamaica", start_date, end_date
    )
    paris_task = _run_destination(
        paris_agent, "Paris", start_date, end_date
    )
    hawaii_task = _run_destination(
        hawaii_agent, "Hawaii", start_date, end_date
    )

    # Guaranteed concurrency at the application layer.
    jamaica, paris, hawaii = await asyncio.gather(
        jamaica_task,
        paris_task,
        hawaii_task,
    )

    # FAN IN -- destination-correlated typed output.
    return TravelSearchResult(
        origin="BWI",
        start_date=start_date,
        end_date=end_date,
        destinations=[jamaica, paris, hawaii],
    )


@function_tool
async def run_parallel_destination_searches(
    start_date: str,
    end_date: str,
) -> str:
    """
    Run Jamaican, Paris, and Hawaii agents concurrently.

    Args:
        start_date: Inclusive start date in YYYY-MM-DD format.
        end_date: Inclusive end date in YYYY-MM-DD format.

    Returns:
        JSON TravelSearchResult grouped by destination.
    """
    try:
        result = await run_parallel_destination_searches_impl(
            date.fromisoformat(start_date),
            date.fromisoformat(end_date),
        )
        return result.model_dump_json()
    except Exception as exc:
        # A Router-visible validation/runtime error. The Router is instructed
        # not to fabricate a TravelSearchResult in this case.
        return json.dumps(
            {"error": f"{type(exc).__name__}: {exc}"}
        )
