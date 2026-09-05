from __future__ import annotations

from agents import Agent

from destination_stays_app.agents.common import agent_model_kwargs
from destination_stays_app.models.destination_models import StaySearchResponse
from destination_stays_app.tools.stay_tools import search_stays


stay_agent = Agent(
    name="Stay Agent",
    instructions=(
        "You are the single shared Stay Agent for the Dominican Republic, London, "
        "and the US Virgin Islands. You receive a destination plus check-in and "
        "check-out dates. You MUST call search_stays exactly once with limit=5. "
        "Never invent hotels, availability, prices, ratings, or addresses. "
        "Return exactly the tool data as a StaySearchResponse. If the tool reports "
        "an error, preserve that error and return an empty stays list."
    ),
    tools=[search_stays],
    output_type=StaySearchResponse,
    **agent_model_kwargs(),
)


async def extract_stay_tool_output(run_result) -> str:
    output = run_result.final_output_as(
        StaySearchResponse,
        raise_if_incorrect_type=True,
    )
    return output.model_dump_json()


stay_agent_tool = stay_agent.as_tool(
    tool_name="find_stays",
    tool_description=(
        "Call the shared Stay Agent to return exactly five mock hotels "
        "for a destination and date range."
    ),
    custom_output_extractor=extract_stay_tool_output,
)
