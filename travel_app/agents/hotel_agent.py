from __future__ import annotations

from agents import Agent

from travel_app.agents.common import agent_model_kwargs
from travel_app.models.travel_models import HotelSearchResponse
from travel_app.tools.hotel_tools import search_hotels


hotel_agent = Agent(
    name="Hotel Agent",
    instructions=(
        "You are the single shared Hotel Agent for Jamaica, Paris, and Hawaii. "
        "You receive a destination plus check-in/check-out dates. "
        "You MUST call search_hotels exactly once with limit=5. "
        "Never invent hotels, availability, prices, ratings, or addresses. "
        "Return exactly the tool data as a HotelSearchResponse. "
        "If the tool reports an error, preserve that error and return an empty hotel list."
    ),
    tools=[search_hotels],
    output_type=HotelSearchResponse,
    **agent_model_kwargs(),
)


async def extract_hotel_tool_output(run_result) -> str:
    output = run_result.final_output_as(
        HotelSearchResponse,
        raise_if_incorrect_type=True,
    )
    return output.model_dump_json()


# ONE tool wrapping ONE shared Hotel Agent. The same object is reused by all
# three destination agents.
hotel_agent_tool = hotel_agent.as_tool(
    tool_name="find_hotels",
    tool_description=(
        "Call the shared Hotel Agent to return exactly five mock hotels "
        "for a destination and date range."
    ),
    custom_output_extractor=extract_hotel_tool_output,
)
