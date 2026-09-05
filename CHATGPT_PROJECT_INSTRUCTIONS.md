You are helping with a Python travel-agents demo that uses the OpenAI Agents SDK.

Project context:
- This repo demonstrates a fan-out/fan-in travel workflow.
- The Travel Router Agent calls an orchestration tool.
- Jamaican, Paris, and Hawaii destination agents run concurrently.
- One shared Hotel Agent is exposed with Agent.as_tool(...) and reused by the destination agents.
- The flight and hotel providers use deterministic mock data. Do not describe the results as live schedules, fares, inventory, or availability.

Development conventions:
- Use Python 3.11+.
- Prefer type hints, small focused functions, and explicit return types for shared helpers.
- Use Pydantic models for structured data and agent outputs.
- Use python-dotenv for local configuration.
- Keep OPENAI_API_KEY and optional model settings in environment variables only.
- Never hardcode, print, or commit secrets.
- Preserve .env.example as the documented configuration template.
- Do not create a top-level agents/ package because it would shadow the installed OpenAI Agents SDK package imported as agents.

OpenAI Agents SDK conventions:
- Follow the repo’s existing patterns: Agent, Runner.run, @function_tool, Agent.as_tool(...), Pydantic output_type, and final_output_as(..., raise_if_incorrect_type=True).
- Reuse agent_model_kwargs() for model configuration unless explicitly asked to change the approach.
- Keep agent instructions narrow and testable.
- Be explicit about required tool calls, tool boundaries, output shape, failure handling, and non-fabrication.
- Do not invent flights, hotels, prices, ratings, addresses, or availability.

Architecture guidance:
- Keep application agents in travel_app/agents/.
- Keep tool wrappers in travel_app/tools/.
- Keep deterministic mock providers in travel_app/services/.
- Keep Pydantic schemas in travel_app/models/.
- Keep fan-out/fan-in orchestration in travel_app/orchestration/.
- Preserve the manager-style workflow unless explicitly asked to change it.
- Use handoffs only if the requested behavior changes to single-specialist transfer of control.
- Preserve per-destination error isolation unless explicitly asked for all-or-nothing behavior.
- Map tool and agent failures into the existing error fields instead of discarding partial successful results.

Tracing, evals, and generated artifacts:
- Treat traces, eval output, generated responses, and run captures as local development artifacts by default.
- Do not commit .env files, traces, generated run outputs, local caches, virtual environments, or build artifacts.
- Add committed fixtures only when they are stable, small, and intentionally reviewed.

Working style:
- Inspect relevant files before editing.
- Keep changes scoped to the user’s request.
- Do not refactor unrelated code or rewrite the demo architecture unless asked.
- When replacing mock providers with real APIs, keep provider code behind the existing service contracts and map provider responses into the local Pydantic models.
- When changing behavior, add focused tests for agent logic, schema validation, tool behavior, orchestration error mapping, or import safety as appropriate.

Verification:
- Run the narrowest useful check after changes.
- Prefer import, formatting, schema, or service checks when no OPENAI_API_KEY is available.
- Use uv run python main.py or uv run python single_file_demo.py only when an API key is configured or when a live smoke test is explicitly requested.
- Summarize files changed and commands run for verification.
