from __future__ import annotations

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
    assert matrix.json()["data"]["status"] == "not_available"


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
