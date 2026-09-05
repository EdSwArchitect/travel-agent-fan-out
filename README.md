# Parallel Travel Agents Demo

This repository contains OpenAI Agents SDK examples for fan-out/fan-in travel
planning workflows.

The examples use:

- `Agent`, `Runner`, and `@function_tool`
- shared specialist agents exposed with `Agent.as_tool(...)`
- guaranteed parallel execution with `asyncio.gather(...)`
- Pydantic structured outputs
- per-destination error isolation
- final data correlated by destination/place

> The bundled flight, hotel, and stay services use deterministic **mock data**.
> They are not real-time schedules, fares, inventory, or availability.

## Examples

### Original Travel Demo

Entry point:

```bash
uv run python main.py
```

Package:

```text
travel_app/
```

Workflow:

- **Travel Router Agent**
- **Jamaican Agent**
- **Paris Agent**
- **Hawaii Agent**
- one reusable **Hotel Agent**
- final output: `TravelSearchResult`

Custom request:

```bash
uv run python main.py \
  "Find flights and hotels between October 10, 2026 and October 17, 2026."
```

Single-file learning version:

```bash
uv run python single_file_demo.py
```

### Destination Stays Demo

Entry point:

```bash
uv run python multi_destination_demo.py
```

Package:

```text
destination_stays_app/
```

Workflow:

- **Destination Stays Router Agent**
- **Dominican Agent**
- **London Agent**
- **US Virgin Islands Agent**
- one reusable **Stay Agent**
- final output: `DestinationStaysResult`

Custom request:

```bash
uv run python multi_destination_demo.py \
  "Find flights and stays between October 10, 2026 and October 17, 2026."
```

## Setup

```bash
cp .env.example .env
# Edit .env and provide OPENAI_API_KEY.

uv sync
```

Optional model override:

```bash
OPENAI_MODEL=<model-name-you-have-access-to>
```

## Why packages avoid top-level `agents/`

The OpenAI Agents SDK itself is imported as:

```python
from agents import Agent, Runner, function_tool
```

A top-level local directory named `agents/` would shadow that installed package.
Therefore application agents live inside example-specific packages:

```text
travel_app/agents/
destination_stays_app/agents/
```

That avoids an import collision while still keeping the agent definitions grouped
cleanly.

## Original Demo Architecture

```text
User
  |
  v
Travel Router Agent
  |
  v
run_parallel_destination_searches (@function_tool)
  |
  +----------------------+----------------------+
  |                      |                      |
  v                      v                      v
Jamaican Agent        Paris Agent           Hawaii Agent
  |                      |                      |
  +-- search_flights     +-- search_flights    +-- search_flights
  |                      |                      |
  +-- SAME Hotel Agent   +-- SAME Hotel Agent  +-- SAME Hotel Agent
      via as_tool()          via as_tool()         via as_tool()
  |                      |                      |
  +----------------------+----------------------+
                         |
                         v
                  TravelSearchResult
```

## Destination Stays Architecture

```text
User
  |
  v
Destination Stays Router Agent
  |
  v
run_destination_stays_search (@function_tool)
  |
  +-------------------------+-------------------------+
  |                         |                         |
  v                         v                         v
Dominican Agent          London Agent              US Virgin Islands Agent
  |                         |                         |
  +-- search_destination_flights                     |
  +-- SAME Stay Agent via as_tool()                  |
  |                         |                         |
  |                         +-- search_destination_flights
  |                         +-- SAME Stay Agent via as_tool()
  |                         |                         |
  |                         |                         +-- search_destination_flights
  |                         |                         +-- SAME Stay Agent via as_tool()
  |                         |                         |
  +-------------------------+-------------------------+
                            |
                            v
                   DestinationStaysResult
```

## Why not use handoffs?

A handoff transfers control to one specialist. These workflows need a
manager/router to collect results from *all* specialists, so agents-as-tools and
manager-style orchestration are a better fit.

The shared Hotel Agent and Stay Agent demonstrate `Agent.as_tool(...)` directly.
The router agents call deterministic orchestration tools that perform concurrent
destination runs with `asyncio.gather(...)`. That guarantees concurrency at the
application layer instead of merely allowing the model to emit parallel tool
calls.

## Project layout

```text
travel_agents/
├── AGENTS.md
├── README.md
├── main.py
├── multi_destination_demo.py
├── single_file_demo.py
├── pyproject.toml
├── .env.example
├── .codex/
│   └── skills/
│       └── python-openai-agents/
│           └── SKILL.md
├── destination_stays_app/
│   ├── agents/
│   │   ├── common.py
│   │   ├── router_agent.py
│   │   ├── dominican_agent.py
│   │   ├── london_agent.py
│   │   ├── us_virgin_islands_agent.py
│   │   └── stay_agent.py
│   ├── models/
│   │   └── destination_models.py
│   ├── orchestration/
│   │   └── destination_orchestrator.py
│   ├── services/
│   │   ├── flight_service.py
│   │   └── stay_service.py
│   └── tools/
│       ├── flight_tools.py
│       └── stay_tools.py
└── travel_app/
    ├── agents/
    │   ├── common.py
    │   ├── router_agent.py
    │   ├── jamaican_agent.py
    │   ├── paris_agent.py
    │   ├── hawaii_agent.py
    │   └── hotel_agent.py
    ├── models/
    │   └── travel_models.py
    ├── orchestration/
    │   └── travel_orchestrator.py
    ├── services/
    │   ├── flight_service.py
    │   └── hotel_service.py
    └── tools/
        ├── flight_tools.py
        └── hotel_tools.py
```

## Replace mock providers

For flights, keep this service shape and replace only the implementation:

```python
async def search_flights_service(
    *,
    origin: str,
    destination_airports: list[str],
    start_date: date,
    end_date: date,
    limit: int = 10,
) -> list[Flight]:
    ...
```

For hotels or stays, keep these shapes:

```python
async def search_hotels_service(
    *,
    destination: str,
    check_in: date,
    check_out: date,
    limit: int = 5,
) -> list[Hotel]:
    ...
```

```python
async def search_stays_service(
    *,
    destination: str,
    check_in: date,
    check_out: date,
    limit: int = 5,
) -> list[Stay]:
    ...
```

Then map provider responses into the relevant Pydantic models.

## Error isolation

Each orchestration layer catches an exception from an entire destination Agent
run and converts it into that destination's `agent_error`. The other destination
runs continue.

Flight and hotel/stay tool results also have separate error fields, so one tool
failure does not erase successful data from the same destination.

## Production additions

For real travel data, add:

- authorized flight/hotel provider APIs
- provider offer IDs and expiry timestamps
- API timeouts and retry/backoff
- rate limiting
- structured logging and tracing
- cache policy for time-sensitive availability
- secrets management
- provider-specific error mapping
