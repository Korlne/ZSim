from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from zsim.api import app
from zsim.api_src.routes import buff_graph as buff_graph_routes
from zsim.api_src.services.buff_graph_service import BuffGraphService
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.spec import BuffGraphEdge, BuffGraphSpec, OwnerKind


def test_buff_graph_api_registers_prd_endpoint_contract():
    routes = {
        (method, route.path)
        for route in app.routes
        for method in getattr(route, "methods", set())
    }

    expected_routes = {
        ("GET", "/api/buff-graphs"),
        ("GET", "/api/buff-graphs/{graph_id}"),
        ("POST", "/api/buff-graphs"),
        ("PUT", "/api/buff-graphs/{graph_id}"),
        ("POST", "/api/buff-graphs/{graph_id}/validate"),
        ("POST", "/api/buff-graphs/{graph_id}/compile"),
        ("POST", "/api/buff-graphs/{graph_id}/parity"),
        ("POST", "/api/buff-graphs/{graph_id}/status"),
        ("GET", "/api/buff-graphs/migration/catalog"),
        ("POST", "/api/buff-graphs/migration/census"),
        ("POST", "/api/buff-graphs/migration/import-xlogic"),
        ("GET", "/api/buff-graphs/parity/matrix"),
        ("POST", "/api/buff-graphs/parity/matrix/run"),
    }

    assert expected_routes <= routes


def test_buff_graph_crud_validate_compile_and_parity(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    spec = _graph_payload()

    created = client.post("/api/buff-graphs", json={"spec": spec})
    listed = client.get("/api/buff-graphs")
    fetched = client.get("/api/buff-graphs/alice-cinema6")
    validated = client.post("/api/buff-graphs/alice-cinema6/validate")
    compiled = client.post("/api/buff-graphs/alice-cinema6/compile")
    parity = client.post("/api/buff-graphs/alice-cinema6/parity")

    assert created.status_code == 200
    assert created.json()["data"]["graph_id"] == "alice-cinema6"
    assert listed.status_code == 200
    assert [item["graph_id"] for item in listed.json()["data"]] == ["alice-cinema6"]
    assert fetched.status_code == 200
    assert fetched.json()["data"]["runtime_status"] == "legacy_python"
    assert validated.status_code == 200
    assert validated.json()["data"] == {"valid": True, "errors": []}
    assert compiled.status_code == 200
    assert compiled.json()["data"]["compiled"] is True
    assert compiled.json()["data"]["execution_order"] == ["trigger", "effect"]
    assert parity.status_code == 200
    assert parity.json()["data"]["status"] == "ready_for_oracle"


def test_buff_graph_api_rejects_bad_status_transition(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    client.post("/api/buff-graphs", json={"spec": _graph_payload()})

    response = client.post(
        "/api/buff-graphs/alice-cinema6/status",
        json={"runtime_status": "visual_graph_default"},
    )

    assert response.status_code == 400
    assert "default_requires_verification" in response.text


def test_buff_graph_api_runs_low_risk_candidate_harness_when_metadata_is_present(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    spec = _graph_payload()
    spec["parity_metadata"] = {
        "candidate_harness": {
            "enabled": True,
            "case_id": "alice-cinema6-api-candidate-harness",
            "legacy_oracle": "legacy_python_fixture",
            "tick": 600,
            "prepared_context": {
                "event": {
                    "kind": "skill_hit",
                    "skill_tag": "basic",
                }
            },
            "expected_final_output": {
                "command": {
                    "type": "start_buff",
                    "buff_index": "Buff-角色-爱丽丝-影画6",
                    "count": 1,
                    "duration_ticks": None,
                }
            },
            "expected_trace_kind_checkpoint": [
                ["graph_started", ""],
                ["node_evaluated", "node_ready"],
                ["adapter_executed", "adapter_executed"],
                ["node_evaluated", "node_ready"],
                ["adapter_executed", "adapter_executed"],
                ["effect_requested", "effect_requested"],
                ["graph_finished", "graph_finished"],
            ],
        }
    }

    created = client.post("/api/buff-graphs", json={"spec": spec})
    parity = client.post("/api/buff-graphs/alice-cinema6/parity")
    fetched = client.get("/api/buff-graphs/alice-cinema6")

    assert created.status_code == 200
    assert parity.status_code == 200
    payload = parity.json()["data"]
    assert payload["status"] == "candidate_harness_passed"
    assert payload["candidate_harness_id"] == "alice-cinema6-api-candidate-harness"
    assert payload["candidate_runtime_status"] == "visual_graph_candidate"
    assert payload["candidate_parity_passed"] is True
    assert payload["full_parity_verified"] is False
    assert payload["evidence"]["output_passed"] is True
    assert payload["evidence"]["trace_checkpoint_passed"] is True
    assert fetched.json()["data"]["runtime_status"] == "legacy_python"


def test_buff_graph_api_runs_pure_low_risk_candidate_harness_wave_case(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    case = _read_json(
        Path(
            "tests/fixtures/buff_graph/runtime-candidate-harness/pure-low-risk/"
            "rainforest-gourmet-atk-bonus-candidate.json"
        )
    )
    wrapper = _read_json(Path(case["source_generated_spec"]))
    spec = wrapper["spec"]
    spec["parity_metadata"] = {
        "candidate_harness": {
            "enabled": True,
            "case_id": case["case_id"],
            "legacy_oracle": case["legacy_oracle"],
            "tick": case["tick"],
            "prepared_context": case["prepared_context"],
            "expected_final_output": case["expected_final_output"],
            "expected_trace_kind_checkpoint": case["expected_trace_kind_checkpoint"],
        }
    }

    created = client.post("/api/buff-graphs", json={"spec": spec})
    parity = client.post("/api/buff-graphs/rainforest-gourmet-atk-bonus/parity")
    fetched = client.get("/api/buff-graphs/rainforest-gourmet-atk-bonus")

    assert created.status_code == 200
    assert parity.status_code == 200
    payload = parity.json()["data"]
    assert payload["status"] == "candidate_harness_passed"
    assert payload["candidate_harness_id"] == "rainforest-gourmet-atk-bonus-candidate"
    assert payload["candidate_runtime_status"] == "visual_graph_candidate"
    assert payload["candidate_parity_passed"] is True
    assert payload["full_parity_verified"] is False
    assert payload["evidence"]["legacy_oracle"] == (
        "generated_spec_fixture_pending_legacy_python_oracle"
    )
    assert payload["evidence"]["output_passed"] is True
    assert payload["evidence"]["trace_checkpoint_passed"] is True
    assert fetched.json()["data"]["runtime_status"] == "legacy_python"


def test_buff_graph_api_runs_enemy_state_candidate_harness_wave_case(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    case = _read_json(
        Path(
            "tests/fixtures/buff_graph/runtime-candidate-harness/enemy-state/"
            "miyabi-core-skill-frost-burn-candidate.json"
        )
    )
    wrapper = _read_json(Path(case["source_generated_spec"]))
    spec = wrapper["spec"]
    spec["parity_metadata"] = {
        "candidate_harness": {
            "enabled": True,
            "case_id": case["case_id"],
            "legacy_oracle": case["legacy_oracle"],
            "tick": case["tick"],
            "prepared_context": case["prepared_context"],
            "expected_final_output": case["expected_final_output"],
            "expected_trace_kind_checkpoint": case["expected_trace_kind_checkpoint"],
        }
    }

    created = client.post("/api/buff-graphs", json={"spec": spec})
    parity = client.post("/api/buff-graphs/miyabi-core-skill-frost-burn/parity")
    fetched = client.get("/api/buff-graphs/miyabi-core-skill-frost-burn")

    assert created.status_code == 200
    assert parity.status_code == 200
    payload = parity.json()["data"]
    assert payload["status"] == "candidate_harness_passed"
    assert payload["candidate_harness_id"] == "miyabi-core-skill-frost-burn-candidate"
    assert payload["candidate_runtime_status"] == "visual_graph_candidate"
    assert payload["candidate_parity_passed"] is True
    assert payload["full_parity_verified"] is False
    assert payload["evidence"]["legacy_oracle"] == (
        "generated_spec_fixture_pending_legacy_python_oracle"
    )
    assert payload["evidence"]["output_passed"] is True
    assert payload["evidence"]["trace_checkpoint_passed"] is True
    assert fetched.json()["data"]["runtime_status"] == "legacy_python"


def test_buff_graph_api_runs_dynamic_owner_candidate_harness_wave_case(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)
    case = _read_json(
        Path(
            "tests/fixtures/buff_graph/runtime-candidate-harness/dynamic-owner/"
            "zanshin-herb-case-candidate.json"
        )
    )
    wrapper = _read_json(Path(case["source_generated_spec"]))
    spec = wrapper["spec"]
    spec["parity_metadata"] = {
        "candidate_harness": {
            "enabled": True,
            "case_id": case["case_id"],
            "legacy_oracle": case["legacy_oracle"],
            "tick": case["tick"],
            "prepared_context": case["prepared_context"],
            "expected_final_output": case["expected_final_output"],
            "expected_trace_kind_checkpoint": _expected_trace(
                node_count=case["expected_trace_node_count"],
                effect_node_indexes=case["expected_trace_effect_node_indexes"],
            ),
        }
    }

    created = client.post("/api/buff-graphs", json={"spec": spec})
    parity = client.post("/api/buff-graphs/zanshin-herb-case/parity")
    fetched = client.get("/api/buff-graphs/zanshin-herb-case")

    assert created.status_code == 200
    assert parity.status_code == 200
    payload = parity.json()["data"]
    assert payload["status"] == "candidate_harness_passed"
    assert payload["candidate_harness_id"] == "dynamic-owner-zanshin-herb-case-candidate"
    assert payload["candidate_runtime_status"] == "visual_graph_candidate"
    assert payload["candidate_parity_passed"] is True
    assert payload["full_parity_verified"] is False
    assert payload["evidence"]["legacy_oracle"] == (
        "generated_spec_fixture_pending_legacy_python_oracle"
    )
    assert payload["evidence"]["output_passed"] is True
    assert payload["evidence"]["trace_checkpoint_passed"] is True
    assert fetched.json()["data"]["runtime_status"] == "legacy_python"


def test_buff_graph_migration_endpoints_keep_unsupported_patterns_explicit(monkeypatch):
    service = BuffGraphService()
    monkeypatch.setattr(buff_graph_routes, "buff_graph_service", service)
    client = TestClient(app)

    catalog = client.get("/api/buff-graphs/migration/catalog")
    census = client.post(
        "/api/buff-graphs/migration/census",
        json={
            "sources": {
                "zsim/sim_progress/Buff/BuffXLogic/Scheduled.py": (
                    "class Scheduled:\n"
                    "    def xhit(self, **kwargs):\n"
                    "        self.schedule.event_list.append(kwargs['event'])\n"
                    "        return self.enemy.anomaly_bar\n"
                )
            }
        },
    )
    imported = client.post(
        "/api/buff-graphs/migration/import-xlogic",
        json={
            "xlogic_path": "zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
            "source": (
                "class AliceCinema6Trigger:\n"
                "    def xhit(self, **kwargs):\n"
                "        if kwargs['skill_tag'] == 'basic':\n"
                "            self.buff.update_count(1)\n"
                "            self.buff.start()\n"
            ),
            "owner_kind": "character",
            "owner_name": "Alice",
            "source_buff_index": "Buff-角色-爱丽丝-影画6",
        },
    )
    matrix = client.get("/api/buff-graphs/parity/matrix")
    matrix_run = client.post("/api/buff-graphs/parity/matrix/run")

    assert catalog.status_code == 200
    assert catalog.json()["data"]["custom_python_nodes_allowed"] is False
    assert "effect" in catalog.json()["data"]["block_families"]
    assert census.status_code == 200
    unsupported = census.json()["data"][0]["unsupported_patterns"]
    assert [item["pattern_id"] for item in unsupported] == [
        "runtime_command_or_scheduled_producer",
        "enemy_anomaly_or_dot_read",
    ]
    assert imported.status_code == 200
    payload = imported.json()["data"]
    assert payload["imported"] is True
    assert payload["spec"]["runtime_status"] == "legacy_python"
    assert matrix.status_code == 200
    matrix_payload = matrix.json()["data"]
    assert matrix_payload["status"] == "not_available"
    assert matrix_payload["command_status"] == "runner_required"
    assert (
        matrix_payload["required_command"]
        == "cd electron-app; pnpm smoke:buff-graph:electron -- --run-parity-matrix"
    )
    assert matrix_payload["evidence_path"].endswith("ui-driven-full-simulation-matrix.json")
    assert matrix_payload["ui_driven"] is True
    assert matrix_payload["full_simulation_matrix"] is True
    assert matrix_payload["full_parity_verified"] is False
    assert "all-runnable-apl-config-matrix" in matrix_payload["matrix_scope"]
    wave_evidence = matrix_payload["candidate_wave_evidence"]
    assert [item["wave_id"] for item in wave_evidence] == [
        "pure-and-low-risk-stateless",
        "enemy-state-edge-triggers",
        "dynamic-owner-equipper",
    ]
    assert wave_evidence[0]["candidate_parity_passed"] is True
    assert wave_evidence[0]["full_parity_verified"] is False
    assert "rainforest-gourmet-atk-bonus-candidate" in wave_evidence[0]["case_ids"]
    assert wave_evidence[1]["candidate_parity_passed"] is True
    assert wave_evidence[1]["full_parity_verified"] is False
    assert "miyabi-core-skill-frost-burn-candidate" in wave_evidence[1]["case_ids"]
    assert wave_evidence[2]["candidate_parity_passed"] is True
    assert wave_evidence[2]["full_parity_verified"] is False
    assert "dynamic-owner-zanshin-herb-case-candidate" in wave_evidence[2]["case_ids"]

    assert matrix_run.status_code == 200
    run_payload = matrix_run.json()["data"]
    assert run_payload["status"] == "run_requested"
    assert run_payload["command_status"] == "request_recorded"
    assert run_payload["required_command"] == matrix_payload["required_command"]
    assert run_payload["evidence_path"] == matrix_payload["evidence_path"]
    assert run_payload["run_id"] == (
        "buff-20260702-buffxlogic-react-flow-visual-authoring:"
        "ui-driven-full-simulation-matrix"
    )
    assert run_payload["full_parity_verified"] is False
    assert run_payload["candidate_wave_evidence"] == wave_evidence


def _graph_payload() -> dict:
    registry = build_default_block_registry()
    trigger = registry.get("trigger.skill_hit").create_node(
        node_id="trigger",
        params={"skill_tag": "basic"},
    )
    effect = registry.get("effect.start_buff").create_node(
        node_id="effect",
        params={"buff_index": "Buff-角色-爱丽丝-影画6"},
    )
    spec = BuffGraphSpec.draft_from_xlogic(
        graph_id="alice-cinema6",
        display_name="Alice Cinema 6",
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        nodes=(trigger, effect),
        edges=(BuffGraphEdge("edge-1", "trigger", "effect"),),
    )
    return {
        "schema_version": spec.schema_version,
        "node_library_version": spec.node_library_version,
        "adapter_contract_version": spec.adapter_contract_version,
        "graph_id": spec.graph_id,
        "display_name": spec.display_name,
        "owner_kind": spec.owner_kind.value,
        "owner_name": spec.owner_name,
        "source_buff_index": spec.source_buff_index,
        "created_from_xlogic": spec.created_from_xlogic,
        "runtime_status": spec.runtime_status.value,
        "nodes": [
            {
                "node_id": node.node_id,
                "family": node.family.value,
                "block_id": node.block_id,
                "adapter_id": node.adapter_id,
                "params": dict(node.params),
                "display_name": node.display_name,
            }
            for node in spec.nodes
        ],
        "edges": [
            {
                "edge_id": edge.edge_id,
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "source_port": edge.source_port,
                "target_port": edge.target_port,
            }
            for edge in spec.edges
        ],
        "params": {},
        "parity_metadata": {},
        "last_parity_baseline": None,
        "last_verified_at": None,
    }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _expected_trace(
    *,
    node_count: int,
    effect_node_indexes: list[int],
) -> list[list[str]]:
    events: list[list[str]] = [["graph_started", ""]]
    effect_slots = set(effect_node_indexes)
    for index in range(node_count):
        events.append(["node_evaluated", "node_ready"])
        events.append(["adapter_executed", "adapter_executed"])
        if index in effect_slots:
            events.append(["effect_requested", "effect_requested"])
    events.append(["graph_finished", "graph_finished"])
    return events
