from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


def _readme_text() -> str:
    return README.read_text()


def test_readme_documents_architecture_with_mermaid() -> None:
    readme = _readme_text()

    assert "## Architecture" in readme
    assert "```mermaid" in readme
    assert "flowchart TD" in readme
    assert "User CLI input" in readme
    assert "OpenAI Agents SDK" in readme
    assert "deterministic mock flight service" in readme
    assert "local airline-prefix enrichment service" in readme


def test_readme_documents_agent_contracts_and_handoffs() -> None:
    readme = _readme_text()

    for expected in (
        "Travel Router Agent",
        "Jamaican Agent",
        "Paris Agent",
        "Hawaii Agent",
        "Hotel Agent",
        "Destination Stays Router Agent",
        "Dominican Agent",
        "London Agent",
        "US Virgin Islands Agent",
        "Stay Agent",
        "Flight Information Enrichment Agent",
        "These examples do not use SDK handoffs.",
        "OPENAI_API_KEY required for live agent runs",
        "OPENAI_MODEL optional",
        "--include-flight-enrichment",
        "top five flights per destination",
        "real-time status remains unverified",
    ):
        assert expected in readme


def test_readme_documented_entrypoints_exist() -> None:
    readme = _readme_text()

    for relative_path in (
        "main.py",
        "multi_destination_demo.py",
        "flight_enrichment_demo.py",
        "single_file_demo.py",
        "travel_app/agents/router_agent.py",
        "travel_app/agents/flight_enrichment_agent.py",
        "destination_stays_app/agents/router_agent.py",
        "tests/test_readme.py",
    ):
        assert relative_path in readme
        assert (REPO_ROOT / relative_path).exists()
