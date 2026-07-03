from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from zsim.api import app
from zsim.api_src.routes import buff_graph as buff_graph_routes
from zsim.api_src.services.buff_graph_service import BuffGraphService


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


GENERATED_SPEC_LEGACY_ORACLE_ROOT = Path(
    "tests/fixtures/buff_graph/generated-spec-legacy-oracles"
)

ORACLE_FIXTURES = [
    Path(
        "tests/fixtures/buff_graph/generated-spec-legacy-oracles/"
        "alice-cinema-6-trigger-legacy-oracle.json"
    ),
    Path(
        "tests/fixtures/buff_graph/generated-spec-legacy-oracles/"
        "astra-yao-idyllic-cadenza-legacy-oracle.json"
    ),
    Path(
        "tests/fixtures/buff_graph/generated-spec-legacy-oracles/"
        "cordis-germina-crit-rate-bonus-legacy-oracle.json"
    ),
]

PREPARED_CONTEXT_BY_GRAPH = {
    "alice-cinema-6-trigger": _read_json(
        Path(
            "tests/fixtures/buff_graph/runtime-candidate-harness/character-manager/"
            "alice-cinema-6-trigger-candidate.json"
        )
    )["prepared_context"],
}


def _spec_with_oracle_metadata(fixture_path: Path) -> tuple[dict, dict, dict]:
    oracle_fixture = _read_json(fixture_path)
    wrapper = _read_json(Path(oracle_fixture["source_generated_spec"]))
    graph_id = oracle_fixture["graph_id"]
    original_spec = wrapper["spec"]
    spec = json.loads(json.dumps(original_spec))
    spec["parity_metadata"] = {
        "generated_spec_legacy_oracle": {
            "enabled": True,
            "fixture_path": fixture_path.as_posix(),
            "prepared_context": PREPARED_CONTEXT_BY_GRAPH.get(graph_id, {}),
        }
    }
    return oracle_fixture, original_spec, spec


@pytest.mark.parametrize("fixture_path", ORACLE_FIXTURES)
def test_materialized_generated_spec_legacy_oracles_execute_without_runtime_promotion(
    monkeypatch,
    fixture_path: Path,
):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)

    oracle_fixture, original_spec, spec = _spec_with_oracle_metadata(fixture_path)
    graph_id = oracle_fixture["graph_id"]

    created = client.post("/api/buff-graphs", json={"spec": spec})
    parity = client.post(f"/api/buff-graphs/{graph_id}/parity")
    fetched = client.get(f"/api/buff-graphs/{graph_id}")
    matrix = client.get("/api/buff-graphs/parity/matrix")

    assert created.status_code == 200
    assert parity.status_code == 200
    payload = parity.json()["data"]
    assert payload["status"] == "generated_spec_legacy_oracle_passed"
    assert payload["candidate_harness_id"] == oracle_fixture["case_id"]
    assert payload["candidate_runtime_status"] == "visual_graph_candidate"
    assert payload["candidate_parity_passed"] is True
    assert payload["full_parity_verified"] is False
    assert payload["evidence"]["case_id"] == oracle_fixture["case_id"]
    assert payload["evidence"]["legacy_oracle"] == "legacy_python_collected"
    assert payload["evidence"]["output_passed"] is True
    assert payload["evidence"]["trace_checkpoint_passed"] is True
    assert payload["evidence"]["oracle_fixture_path"] == fixture_path.as_posix()
    assert payload["evidence"]["oracle_fixture_parity_status"] == (
        "legacy_oracle_materialized_only"
    )
    assert payload["evidence"]["oracle_fixture_full_parity_verified"] is False

    fetched_payload = fetched.json()["data"]
    assert fetched_payload["runtime_status"] == "visual_graph_candidate"
    assert fetched_payload["last_verified_at"] is None
    assert original_spec["runtime_status"] == "visual_graph_candidate"
    assert (
        original_spec["parity_metadata"]["parity_status"]
        == "generated_spec_legacy_oracle_passed"
    )
    assert oracle_fixture["full_parity_verified"] is False

    readiness = matrix.json()["data"]["generated_spec_readiness"]
    ready_items = {
        item["graph_id"]: item
        for item in readiness["items"]
        if item["candidate_execution_available"]
    }
    assert len(ready_items) == 150
    assert readiness["materialized_legacy_oracle_count"] == 150
    assert readiness["missing_legacy_oracle_count"] == 0
    assert readiness["ready_for_execution_count"] == 150
    assert readiness["readiness_status_counts"] == {
        "ready_for_generated_spec_legacy_oracle_execution": 150
    }
    assert ready_items[graph_id]["readiness_status"] == (
        "ready_for_generated_spec_legacy_oracle_execution"
    )
    assert ready_items[graph_id]["full_parity_verified"] is False
    assert readiness["full_parity_verified_count"] == 0


def test_all_materialized_generated_spec_legacy_oracles_execute_without_runtime_promotion(
    monkeypatch,
):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    fixture_paths = sorted(GENERATED_SPEC_LEGACY_ORACLE_ROOT.glob("*.json"))

    failures: list[dict[str, object]] = []
    for fixture_path in fixture_paths:
        oracle_fixture, original_spec, spec = _spec_with_oracle_metadata(fixture_path)
        graph_id = oracle_fixture["graph_id"]

        created = client.post("/api/buff-graphs", json={"spec": spec})
        parity = client.post(f"/api/buff-graphs/{graph_id}/parity")
        fetched = client.get(f"/api/buff-graphs/{graph_id}")
        parity_payload = parity.json().get("data", {}) if parity.status_code == 200 else {}
        fetched_payload = fetched.json().get("data", {}) if fetched.status_code == 200 else {}

        if (
            created.status_code != 200
            or parity.status_code != 200
            or parity_payload.get("status") != "generated_spec_legacy_oracle_passed"
            or parity_payload.get("candidate_parity_passed") is not True
            or parity_payload.get("full_parity_verified") is not False
            or fetched_payload.get("runtime_status") != "visual_graph_candidate"
            or original_spec["runtime_status"] != "visual_graph_candidate"
            or original_spec["parity_metadata"]["parity_status"]
            != "generated_spec_legacy_oracle_passed"
        ):
            failures.append(
                {
                    "fixture": fixture_path.as_posix(),
                    "created_status": created.status_code,
                    "parity_status_code": parity.status_code,
                    "parity_status": parity_payload.get("status"),
                    "candidate_parity_passed": parity_payload.get(
                        "candidate_parity_passed"
                    ),
                    "full_parity_verified": parity_payload.get("full_parity_verified"),
                    "fetched_runtime_status": fetched_payload.get("runtime_status"),
                }
            )

    matrix = client.get("/api/buff-graphs/parity/matrix")
    readiness = matrix.json()["data"]["generated_spec_readiness"]

    assert len(fixture_paths) == 150
    assert failures == []
    assert readiness["total_generated_specs"] == 150
    assert readiness["materialized_legacy_oracle_count"] == 150
    assert readiness["missing_legacy_oracle_count"] == 0
    assert readiness["ready_for_execution_count"] == 150
    assert readiness["full_parity_verified_count"] == 0
    assert readiness["runtime_status_counts"] == {"visual_graph_candidate": 150}
    assert readiness["parity_status_counts"] == {
        "generated_spec_legacy_oracle_passed": 150
    }
