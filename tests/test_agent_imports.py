from __future__ import annotations


def test_agent_imports_use_sdk_agents_package() -> None:
    import agents
    from destination_stays_app.agents.router_agent import (
        router_agent as destination_stays_router_agent,
    )
    from travel_app.agents.router_agent import router_agent as travel_router_agent

    assert "/travel_agents/agents" not in (agents.__file__ or "")
    assert travel_router_agent.name == "Travel Router Agent"
    assert destination_stays_router_agent.name == "Destination Stays Router Agent"
