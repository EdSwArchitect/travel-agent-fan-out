# Repository Guidance

## Project Purpose

This repository is a Python travel-agents demo using the OpenAI Agents SDK. It shows a fan-out/fan-in workflow where a Travel Router Agent calls an orchestration tool, three destination agents run concurrently, and one shared Hotel Agent is exposed with `Agent.as_tool(...)`.

The app uses deterministic mock flight and hotel services. Do not present mock data as live travel schedules, fares, inventory, or availability.

## Python Conventions

- Use Python 3.11+ features and keep `from __future__ import annotations` in Python modules.
- Prefer clear type hints, small focused functions, and explicit return types for shared helpers.
- Use Pydantic models from `travel_app/models/` for structured data and agent outputs.
- Use `python-dotenv` for local configuration. Keep `.env.example` as the documented template.
- Do not create a top-level `agents/` package; it would shadow the installed OpenAI Agents SDK package imported as `agents`.

## OpenAI Agents SDK Conventions

- Follow the existing SDK patterns in the repo: `Agent`, `Runner`, `@function_tool`, `Agent.as_tool(...)`, and `final_output_as(...)`.
- Keep `OPENAI_API_KEY` and optional model overrides in environment variables. Never hardcode keys or commit secrets.
- Preserve `.env.example` when changing configuration, and update it when adding required environment variables.
- Reuse `agent_model_kwargs()` for model configuration so omitted model settings fall back to the SDK default.

## Agent Development Practices

- Keep agent instructions narrow and testable: specify tool boundaries, output type, and what the agent must not fabricate.
- Preserve the manager-style workflow: the Router calls `run_parallel_destination_searches`, and that tool owns concurrent destination execution with `asyncio.gather(...)`.
- Use handoffs only if the product behavior changes to single-specialist transfer of control. This demo intentionally aggregates all destination results.
- Prefer structured outputs backed by Pydantic models. Map tool and agent failures into the existing error fields instead of discarding partial successful results.
- Treat tracing, eval output, generated responses, and run artifacts as local development artifacts unless the user explicitly asks to add maintained fixtures.

## Testing And Verification

- Before editing behavior, inspect the relevant agent, tool, model, orchestration, and service files.
- Run available tests or the closest smoke command after changes. For this repo, useful smoke checks include `uv run python main.py` and `uv run python single_file_demo.py` when an `OPENAI_API_KEY` is configured.
- For changes that do not require a model call, prefer focused import, schema, or service checks that can run without external API access.
- Add focused tests when changing agent logic, Pydantic schemas, tool contracts, error mapping, or orchestration behavior.

## Repo Hygiene

- Do not commit `.env` files, traces, generated run outputs, local caches, virtual environments, or build artifacts.
- Keep changes scoped to the requested behavior. Do not refactor unrelated code or rewrite the demo architecture unless asked.
- When adding files for Codex, keep repo-local skills under `.codex/skills/` and keep runtime Codex state out of Git.
