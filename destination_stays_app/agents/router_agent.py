from __future__ import annotations

from agents import Agent

from destination_stays_app.agents.common import agent_model_kwargs
from destination_stays_app.models.destination_models import DestinationStaysResult
from destination_stays_app.orchestration.destination_orchestrator import (
    run_destination_stays_search,
)


router_agent = Agent(
    name="Destination Stays Router Agent",
    instructions=(
        "You are the Destination Stays Router Agent. Extract the inclusive "
        "start and end dates from the user's request. Do not search flights or "
        "stays yourself. You MUST call run_destination_stays_search exactly once "
        "with ISO YYYY-MM-DD dates. That orchestration tool validates the range, "
        "launches the Dominican Agent, London Agent, and US Virgin Islands Agent "
        "concurrently, and returns correlated destination data. Preserve every "
        "returned field exactly. Never add or alter flights, stays, prices, "
        "ratings, or availability. Return DestinationStaysResult."
    ),
    tools=[run_destination_stays_search],
    output_type=DestinationStaysResult,
    **agent_model_kwargs(),
)
