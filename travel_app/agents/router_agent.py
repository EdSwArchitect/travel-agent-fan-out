from __future__ import annotations

from agents import Agent

from travel_app.agents.common import agent_model_kwargs
from travel_app.models.travel_models import TravelSearchResult
from travel_app.orchestration.travel_orchestrator import (
    run_parallel_destination_searches,
)


router_agent = Agent(
    name="Travel Router Agent",
    instructions=(
        "You are the Travel Router Agent. "
        "Extract the inclusive start and end dates from the user's request. "
        "Do not search flights or hotels yourself. "
        "You MUST call run_parallel_destination_searches exactly once with ISO YYYY-MM-DD dates. "
        "That orchestration tool validates the range, launches the Jamaican Agent, Paris Agent, "
        "and Hawaii Agent concurrently, and returns correlated destination data. "
        "Preserve every returned field exactly. "
        "Never add or alter flights, hotels, prices, ratings, or availability. "
        "Return TravelSearchResult."
    ),
    tools=[run_parallel_destination_searches],
    output_type=TravelSearchResult,
    **agent_model_kwargs(),
)
