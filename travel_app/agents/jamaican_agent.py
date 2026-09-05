from __future__ import annotations

from agents import Agent

from travel_app.agents.common import agent_model_kwargs
from travel_app.agents.hotel_agent import hotel_agent_tool
from travel_app.models.travel_models import DestinationResult
from travel_app.tools.flight_tools import search_flights


jamaican_agent = Agent(
    name="Jamaican Agent",
    instructions=(
        "You are the Jamaica destination specialist. "
        "For the supplied date range MUST: "
        "1. Call search_flights exactly once using destination='Jamaica', origin='BWI', "
        "destination_airports=['MBJ','KIN'], and limit=10. "
        "2. Call the shared find_hotels Hotel Agent exactly once using destination='Jamaica' "
        "and the same dates. "
        "3. Return DestinationResult with destination='Jamaica'. "
        "Copy tool data exactly. Never invent missing data. "
        "Map flight tool error to flight_error and Hotel Agent error to hotel_error."
    ),
    tools=[search_flights, hotel_agent_tool],
    output_type=DestinationResult,
    **agent_model_kwargs(),
)
