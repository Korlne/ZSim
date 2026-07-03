from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any, Mapping

from zsim.api_src.models.buff_graph import (
    BuffGraphCompilePayload,
    BuffGraphMatrixPayload,
    BuffGraphParityPayload,
    BuffGraphSpecModel,
    BuffGraphValidationPayload,
)
from zsim.sim_progress.BuffGraph.adapters.compose_adapters import build_low_risk_compose_adapters
from zsim.sim_progress.BuffGraph.adapters.condition_adapters import (
    build_enemy_anomaly_state_condition_adapters,
    build_low_risk_condition_adapters,
    build_prepared_context_condition_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.effect_adapters import (
    build_low_risk_effect_adapters,
    build_prepared_context_effect_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.read_adapters import (
    build_enemy_anomaly_state_read_adapters,
    build_low_risk_read_adapters,
    build_prepared_context_read_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.state_adapters import (
    build_enemy_anomaly_state_state_adapters,
    build_low_risk_state_adapters,
)
from zsim.sim_progress.BuffGraph.adapters.trigger_adapters import build_low_risk_trigger_adapters
from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import classify_xlogic_source, import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.runtime.parity import (
    BuffGraphCandidateParityOracle,
    run_buff_graph_candidate_parity,
)
from zsim.sim_progress.BuffGraph.spec import BuffGraphSpec, RuntimeStatus, validate_buff_graph_spec


CAMPAIGN_ID = "buff-20260702-buffxlogic-react-flow-visual-authoring"
BUFF_GRAPH_MATRIX_COMMAND = "cd electron-app; pnpm smoke:buff-graph:electron -- --run-parity-matrix"
BUFF_GRAPH_MATRIX_EVIDENCE_PATH = (
    f"scripts/buff_agents/evidence/{CAMPAIGN_ID}/ui-driven-full-simulation-matrix.json"
)
BUFF_GRAPH_MATRIX_RUN_ID = f"{CAMPAIGN_ID}:ui-driven-full-simulation-matrix"
BUFF_GRAPH_MATRIX_SCOPE = [
    "react-flow-ui-open-edit-save-validate",
    "react-flow-ui-initiated-parity",
    "all-runnable-apl-config-matrix",
    "gap-dedicated-trigger-scenarios",
    "legacy-python-xlogic-vs-graph-runtime",
]
PURE_LOW_RISK_CANDIDATE_WAVE_EVIDENCE = [
    {
        "wave_id": "pure-and-low-risk-stateless",
        "candidate_harness_id": "pure-low-risk-generated-spec-candidate-harness",
        "status": "candidate_harness_wave_available",
        "case_ids": [
            "cordis-germina-crit-rate-bonus-candidate",
            "rainforest-gourmet-atk-bonus-candidate",
            "astra-yao-idyllic-cadenza-candidate",
        ],
        "sampled_generated_spec_dirs": [
            "pure-condition-passive-buffs",
            "record-cooldown-stack-buffs",
            "low-risk-remaining-generated-specs",
        ],
        "candidate_runtime_status": RuntimeStatus.VISUAL_GRAPH_CANDIDATE.value,
        "candidate_parity_passed": True,
        "full_parity_verified": False,
        "evidence_path": (
            f"scripts/buff_agents/evidence/{CAMPAIGN_ID}/"
            "oracle-graph-runtime-candidate-harness-pure-low-risk.json"
        ),
        "scope": (
            "Fixture-backed candidate harness mechanism evidence for three "
            "pure/low-risk generated specs; not final legacy parity for the full wave."
        ),
    }
]
ENEMY_STATE_CANDIDATE_WAVE_EVIDENCE = [
    {
        "wave_id": "enemy-state-edge-triggers",
        "candidate_harness_id": "enemy-state-generated-spec-candidate-harness",
        "status": "candidate_harness_wave_available",
        "case_ids": [
            "anomaly-debuff-exit-judge-candidate",
            "miyabi-core-skill-frost-burn-candidate",
            "branch-blade-song-crit-rate-bonus-candidate",
        ],
        "sampled_generated_spec_dirs": [
            "enemy-state-edge-triggers",
        ],
        "candidate_runtime_status": RuntimeStatus.VISUAL_GRAPH_CANDIDATE.value,
        "candidate_parity_passed": True,
        "full_parity_verified": False,
        "evidence_path": (
            f"scripts/buff_agents/evidence/{CAMPAIGN_ID}/"
            "oracle-graph-runtime-candidate-harness-enemy-state.json"
        ),
        "scope": (
            "Fixture-backed candidate harness mechanism evidence for three "
            "enemy-state generated specs; not final legacy parity for the full wave."
        ),
    }
]
DYNAMIC_OWNER_CANDIDATE_WAVE_EVIDENCE = [
    {
        "wave_id": "dynamic-owner-equipper",
        "candidate_harness_id": "dynamic-owner-generated-spec-candidate-harness",
        "status": "candidate_harness_wave_available",
        "case_ids": [
            "dynamic-owner-astral-voice-candidate",
            "dynamic-owner-hellfire-gears-sp-r-bonus-candidate",
            "dynamic-owner-ice-jade-teapot-extra-dmg-bonus-candidate",
            "dynamic-owner-zanshin-herb-case-candidate",
        ],
        "sampled_generated_spec_dirs": [
            "dynamic-owner-equipper-cases",
        ],
        "candidate_runtime_status": RuntimeStatus.VISUAL_GRAPH_CANDIDATE.value,
        "candidate_parity_passed": True,
        "full_parity_verified": False,
        "evidence_path": (
            f"scripts/buff_agents/evidence/{CAMPAIGN_ID}/"
            "oracle-graph-runtime-candidate-harness-dynamic-owner.json"
        ),
        "scope": (
            "Fixture-backed candidate harness mechanism evidence for four "
            "dynamic-owner/equipper generated specs; not final legacy parity for the full wave."
        ),
    }
]
CANDIDATE_WAVE_EVIDENCE = (
    PURE_LOW_RISK_CANDIDATE_WAVE_EVIDENCE
    + ENEMY_STATE_CANDIDATE_WAVE_EVIDENCE
    + DYNAMIC_OWNER_CANDIDATE_WAVE_EVIDENCE
)


class BuffGraphService:
    def __init__(self) -> None:
        self._graphs: dict[str, BuffGraphSpec] = {}
        self._block_registry = build_default_block_registry()

    def list_graphs(self) -> list[BuffGraphSpecModel]:
        return [BuffGraphSpecModel.from_domain(spec) for spec in self._graphs.values()]

    def get_graph(self, graph_id: str) -> BuffGraphSpecModel:
        return BuffGraphSpecModel.from_domain(self._require_graph(graph_id))

    def save_graph(self, spec_model: BuffGraphSpecModel) -> BuffGraphSpecModel:
        spec = spec_model.to_domain()
        self._graphs[spec.graph_id] = spec
        return BuffGraphSpecModel.from_domain(spec)

    def validate_graph(self, graph_id: str) -> BuffGraphValidationPayload:
        return self.validate_spec(self._require_graph(graph_id))

    def validate_spec(self, spec: BuffGraphSpec) -> BuffGraphValidationPayload:
        errors = validate_buff_graph_spec(spec)
        return BuffGraphValidationPayload(
            valid=not errors,
            errors=[asdict(error) for error in errors],
        )

    def compile_graph(self, graph_id: str) -> BuffGraphCompilePayload:
        result = compile_buff_graph_spec(
            self._require_graph(graph_id),
            block_registry=self._block_registry,
        )
        return BuffGraphCompilePayload(
            compiled=result.passed,
            errors=[asdict(error) for error in result.errors],
            execution_order=[] if result.compiled is None else list(result.compiled.execution_order),
        )

    def request_parity(self, graph_id: str) -> BuffGraphParityPayload:
        spec = self._require_graph(graph_id)
        compile_result = self.compile_graph(graph_id)
        if compile_result.compiled:
            candidate_harness = _candidate_harness_metadata(spec.parity_metadata)
            if candidate_harness is not None:
                result = run_buff_graph_candidate_parity(
                    replace(
                        spec,
                        runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
                    ),
                    block_registry=self._block_registry,
                    adapters=_candidate_harness_adapters(),
                    tick=int(candidate_harness.get("tick", 0)),
                    prepared_context=_mapping(candidate_harness.get("prepared_context")),
                    oracle=BuffGraphCandidateParityOracle(
                        case_id=str(candidate_harness.get("case_id", spec.graph_id)),
                        expected_final_output=_mapping(
                            candidate_harness.get("expected_final_output")
                        ),
                        expected_trace_kind_checkpoint=tuple(
                            candidate_harness.get("expected_trace_kind_checkpoint", ())
                        ),
                        legacy_oracle=str(
                            candidate_harness.get("legacy_oracle", "legacy_python_fixture")
                        ),
                    ),
                )
                return BuffGraphParityPayload(
                    status=(
                        "candidate_harness_passed"
                        if result.passed
                        else "candidate_harness_failed"
                    ),
                    graph_id=spec.graph_id,
                    reason=(
                        "Graph candidate harness executed without live Buff runtime cutover."
                    ),
                    candidate_harness_id=result.case_id,
                    candidate_runtime_status=RuntimeStatus.VISUAL_GRAPH_CANDIDATE,
                    candidate_parity_passed=result.passed,
                    full_parity_verified=False,
                    evidence=result.to_evidence(),
                )
            return BuffGraphParityPayload(
                status="ready_for_oracle",
                graph_id=spec.graph_id,
                reason="Graph compiles; legacy-vs-graph parity execution is provided by later oracle/UI matrix packs.",
            )
        return BuffGraphParityPayload(
            status="not_available",
            graph_id=spec.graph_id,
            reason="Graph must compile before parity can run.",
        )

    def update_status(
        self,
        graph_id: str,
        *,
        runtime_status: RuntimeStatus,
        last_verified_at: str | None,
    ) -> BuffGraphSpecModel:
        spec = self._require_graph(graph_id)
        updated = BuffGraphSpec(
            schema_version=spec.schema_version,
            node_library_version=spec.node_library_version,
            adapter_contract_version=spec.adapter_contract_version,
            graph_id=spec.graph_id,
            display_name=spec.display_name,
            owner_kind=spec.owner_kind,
            owner_name=spec.owner_name,
            source_buff_index=spec.source_buff_index,
            created_from_xlogic=spec.created_from_xlogic,
            runtime_status=runtime_status,
            nodes=spec.nodes,
            edges=spec.edges,
            params=spec.params,
            parity_metadata=spec.parity_metadata,
            last_parity_baseline=spec.last_parity_baseline,
            last_verified_at=last_verified_at,
        )
        validation = self.validate_spec(updated)
        if not validation.valid:
            raise ValueError(f"Invalid graph status transition: {validation.errors}")
        self._graphs[graph_id] = updated
        return BuffGraphSpecModel.from_domain(updated)

    def migration_catalog(self) -> dict[str, Any]:
        return {
            "block_families": sorted(
                {block.family.value for block in self._block_registry.all()}
            ),
            "blocks": [
                {
                    "block_id": block.block_id,
                    "family": block.family.value,
                    "display_name": block.display_name,
                    "adapter_id": block.adapter_id,
                }
                for block in self._block_registry.all()
            ],
            "custom_python_nodes_allowed": False,
        }

    def census_sources(self, sources: dict[str, str]) -> list[dict[str, Any]]:
        return [
            {
                "xlogic_path": classification.xlogic_path,
                "triggers": list(classification.triggers),
                "conditions": list(classification.conditions),
                "reads": list(classification.reads),
                "effects": list(classification.effects),
                "state": list(classification.state),
                "migration_wave": classification.migration_wave,
                "unsupported_patterns": [
                    asdict(pattern) for pattern in classification.unsupported_patterns
                ],
            }
            for path, source in sources.items()
            for classification in (classify_xlogic_source(xlogic_path=path, source=source),)
        ]

    def import_xlogic(
        self,
        *,
        xlogic_path: str,
        source: str,
        owner_kind,
        owner_name: str,
        source_buff_index: str | None,
        graph_id: str | None,
        display_name: str | None,
    ) -> dict[str, Any]:
        result = import_xlogic_to_graph(
            xlogic_path=xlogic_path,
            source=source,
            owner_kind=owner_kind,
            owner_name=owner_name,
            source_buff_index=source_buff_index,
            graph_id=graph_id,
            display_name=display_name,
            block_registry=self._block_registry,
        )
        spec_model = None
        if result.spec is not None:
            self._graphs[result.spec.graph_id] = result.spec
            spec_model = BuffGraphSpecModel.from_domain(result.spec).model_dump(mode="json")
        return {
            "imported": result.imported,
            "spec": spec_model,
            "unsupported_patterns": [asdict(pattern) for pattern in result.unsupported_patterns],
            "validation_errors": [
                asdict(error) if hasattr(error, "__dataclass_fields__") else str(error)
                for error in result.validation_errors
            ],
        }

    def parity_matrix(self) -> BuffGraphMatrixPayload:
        return BuffGraphMatrixPayload(
            status="not_available",
            reason=(
                "UI-driven full simulation matrix evidence is still required. "
                "The returned command is the stable Electron entrypoint that a later UI runner pack "
                "must implement before parity can be accepted."
            ),
            required_command=BUFF_GRAPH_MATRIX_COMMAND,
            evidence_path=BUFF_GRAPH_MATRIX_EVIDENCE_PATH,
            command_status="runner_required",
            run_id=None,
            candidate_wave_evidence=list(CANDIDATE_WAVE_EVIDENCE),
            matrix_scope=list(BUFF_GRAPH_MATRIX_SCOPE),
        )

    def request_parity_matrix_run(self) -> BuffGraphMatrixPayload:
        return BuffGraphMatrixPayload(
            status="run_requested",
            reason=(
                "Matrix run request recorded as an auditable backend contract only. "
                "This API pack does not execute the Electron UI runner and does not prove full parity."
            ),
            required_command=BUFF_GRAPH_MATRIX_COMMAND,
            evidence_path=BUFF_GRAPH_MATRIX_EVIDENCE_PATH,
            command_status="request_recorded",
            run_id=BUFF_GRAPH_MATRIX_RUN_ID,
            candidate_wave_evidence=list(CANDIDATE_WAVE_EVIDENCE),
            matrix_scope=list(BUFF_GRAPH_MATRIX_SCOPE),
        )

    def _require_graph(self, graph_id: str) -> BuffGraphSpec:
        try:
            return self._graphs[graph_id]
        except KeyError as exc:
            raise KeyError(f"Buff graph not found: {graph_id}") from exc


def _candidate_harness_metadata(parity_metadata: Mapping[str, Any]) -> Mapping[str, Any] | None:
    value = parity_metadata.get("candidate_harness")
    return value if isinstance(value, Mapping) and value.get("enabled") else None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _candidate_harness_adapters() -> dict[str, object]:
    adapters: dict[str, object] = {}
    for group in (
        build_low_risk_trigger_adapters(),
        build_low_risk_condition_adapters(),
        build_prepared_context_condition_adapters(),
        build_enemy_anomaly_state_condition_adapters(),
        build_low_risk_read_adapters(),
        build_prepared_context_read_adapters(),
        build_enemy_anomaly_state_read_adapters(),
        build_low_risk_effect_adapters(),
        build_prepared_context_effect_adapters(),
        build_low_risk_state_adapters(),
        build_enemy_anomaly_state_state_adapters(),
        build_low_risk_compose_adapters(),
    ):
        adapters.update(group)
    return adapters
