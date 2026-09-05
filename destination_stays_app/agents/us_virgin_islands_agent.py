from __future__ import annotations

from agents import Agent

from destination_stays_app.agents.common import agent_model_kwargs
from destination_stays_app.agents.stay_agent import stay_agent_tool
from destination_stays_app.models.destination_models import PlaceResult
from destination_stays_app.tools.flight_tools import search_destination_flights


us_virgin_islands_agent = Agent(
    name="US Virgin Islands Agent",
    instructions=(
        "You are the US Virgin Islands destination specialist. "
        "For the supplied date range you MUST: "
        "1. Call search_destination_flights exactly once using "
        "destination='US Virgin Islands', origin='BWI', "
        "destination_airports=['STT','STX'], and limit=10. "
        "2. Call the shared find_stays Stay Agent exactly once using "
        "destination='US Virgin Islands' and the same dates. "
        "3. Return PlaceResult with destination='US Virgin Islands'. "
        "Copy tool data exactly. Never invent missing data. "
        "Map flight tool error to flight_error and Stay Agent error to stay_error."
    ),
    tools=[search_destination_flights, stay_agent_tool],
    output_type=PlaceResult,
    **agent_model_kwargs(),
)
