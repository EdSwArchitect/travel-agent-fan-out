# Parallel Travel Agents Demo

This project implements the requested fan-out/fan-in OpenAI Agents SDK example:

- **Travel Router Agent**
- **Jamaican Agent**
- **Paris Agent**
- **Hawaii Agent**
- one reusable **Hotel Agent**
- `Agent`, `Runner`, and `@function_tool`
- `Agent.as_tool(...)` for the shared Hotel Agent
- guaranteed parallel execution with `asyncio.gather(...)`
- Pydantic structured outputs
- per-destination error isolation
- final data correlated by destination

> The bundled flight and hotel services use deterministic **mock data**.
> They are not real-time schedules, fares, inventory, or availability.

## Why the code is packaged under `travel_app/`

The OpenAI Agents SDK itself is imported as:

```python
from agents import Agent, Runner, function_tool
```

A top-level local directory named `agents/` would shadow that installed package.
Therefore the application agents live under:

```text
travel_app/agents/
```

That avoids an import collision while still keeping the agent definitions grouped
cleanly.

## Architecture

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
  +-- search_flights      +-- search_flights    +-- search_flights
  |                      |                      |
  +-- SAME Hotel Agent    +-- SAME Hotel Agent  +-- SAME Hotel Agent
      via as_tool()           via as_tool()          via as_tool()
  |                      |                      |
  +----------------------+----------------------+
                         |
                         v
                  TravelSearchResult
```

## Why not use handoffs?

A handoff transfers control to the specialist. This workflow needs a manager/router
to collect results from *all* specialists, so agents-as-tools / manager-style
orchestration is a better fit.

The Hotel Agent demonstrates `Agent.as_tool(...)` directly.

For the three destination agents, the requirement says they **must** run in parallel.
The Router therefore calls a deterministic orchestration tool that performs:

```python
jamaica, paris, hawaii = await asyncio.gather(
    jamaica_task,
    paris_task,
    hawaii_task,
)
```

That guarantees concurrency instead of merely allowing the model to emit parallel
tool calls.

## Project layout

```text
travel_agents/
├── main.py
├── single_file_demo.py
├── pyproject.toml
├── .env.example
├── README.md
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

## Run with uv

```bash
cp .env.example .env
# Edit .env and provide OPENAI_API_KEY.

uv sync
uv run python main.py
```

Custom request:

```bash
uv run python main.py \
  "Find flights and hotels between October 10, 2026 and October 17, 2026."
```

Single-file learning version:

```bash
uv run python single_file_demo.py
```

## Replace the mock flight provider

Keep this service contract and replace only its implementation:

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

Then map your provider response into `Flight` objects.

## Replace the mock hotel provider

Keep this contract:

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

Then map provider results into `Hotel` objects.

## Error isolation

`_run_destination(...)` catches an exception from an entire destination Agent run
and converts it into `DestinationResult.agent_error`. The other two agent runs
continue.

Flight and hotel tool results also have separate error fields, so a hotel failure
does not erase successful flight data.

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
