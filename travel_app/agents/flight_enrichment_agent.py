from __future__ import annotations

from agents import Agent

from travel_app.agents.common import agent_model_kwargs
from travel_app.models.flight_enrichment_models import FlightInformationSummary
from travel_app.tools.flight_enrichment_tools import lookup_flight_information


flight_enrichment_agent = Agent(
    name="Flight Information Enrichment Agent",
    instructions=(
        "You are a flight information enrichment agent. Given a flight number, "
        "identify the airline, route, scheduled departure and arrival airports, "
        "scheduled times, current status, gate or terminal when available, "
        "aircraft type when available, and any delay or cancellation details. "
        "If the flight number alone is ambiguous or the date is missing, ask for "
        "the flight date instead of guessing real-time status. You MUST call "
        "lookup_flight_information before returning a summary when a flight "
        "number is present. Clearly distinguish scheduled information from "
        "real-time status. Do not guess route, gate, aircraft, delay, or "
        "cancellation details. Return FlightInformationSummary and preserve any "
        "unverified fields reported by the tool."
    ),
    tools=[lookup_flight_information],
    output_type=FlightInformationSummary,
    **agent_model_kwargs(),
)
