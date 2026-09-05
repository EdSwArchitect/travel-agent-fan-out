---
name: python-openai-agents
description: Modify this travel-agents Python demo when work touches OpenAI Agents SDK agents, tools, orchestration, structured outputs, tracing, evals, or SDK configuration.
---

# Python OpenAI Agents Development

Use this skill for changes to this repository's OpenAI Agents SDK code. The project is a Python 3.11+ travel-agents demo with application code under `travel_app/` and a single-file learning version in `single_file_demo.py`.

## Local Architecture

- Import the OpenAI Agents SDK from the installed `agents` package. Do not add a top-level local `agents/` directory because it would shadow the SDK import.
- Keep application agent definitions in `travel_app/agents/`, tool wrappers in `travel_app/tools/`, deterministic mock providers in `travel_app/services/`, Pydantic schemas in `travel_app/models/`, and fan-out/fan-in logic in `travel_app/orchestration/`.
- Preserve the current manager pattern unless the user requests a behavior change: the Travel Router Agent calls `run_parallel_destination_searches`, and the orchestration layer runs the Jamaican, Paris, and Hawaii agents concurrently with `asyncio.gather(...)`.
- Keep the Hotel Agent as one shared `Agent` exposed through `Agent.as_tool(...)` and reused by the destination agents.

## SDK And Agent Guidance

- Prefer the repo's existing SDK idioms: `Agent`, `Runner.run`, `@function_tool`, `Agent.as_tool(...)`, Pydantic `output_type`, and `final_output_as(..., raise_if_incorrect_type=True)`.
- Keep agent instructions explicit about required tool calls, output shape, failure handling, and non-fabrication of flights, hotels, prices, ratings, and availability.
- Use Pydantic models for structured outputs and update schemas before changing agent output contracts.
- Keep API keys and optional model settings in environment variables. Use `.env.example` as documentation, and never hardcode or print secrets.
- Reuse `agent_model_kwargs()` for model configuration unless the user asks for a different configuration approach.

## Changes That Need Extra Care

- If changing orchestration, preserve per-destination error isolation unless the user explicitly asks for all-or-nothing behavior.
- If replacing mock providers with real APIs, keep provider code behind the existing service contracts and map provider responses into the local Pydantic models.
- If adding tracing, evals, or run capture, write outputs to ignored local artifact directories by default. Add committed fixtures only when they are stable, small, and intentionally reviewed.
- If adding tests, focus on service contracts, schema validation, tool behavior, orchestration error mapping, and import safety. Avoid tests that require live OpenAI API calls unless the user asks for integration tests.

## Verification

After edits, run the narrowest useful check. Prefer import, formatting, schema, or service checks when no `OPENAI_API_KEY` is available. Use `uv run python main.py` or `uv run python single_file_demo.py` only when an API key is configured or the user explicitly wants a live smoke test.
