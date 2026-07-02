from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from zsim.sim_progress.BuffGraph.adapters import BuffGraphAdapter
from zsim.sim_progress.BuffGraph.blocks import BuffGraphBlockRegistry
from zsim.sim_progress.BuffGraph.spec import BuffGraphSpec, RuntimeStatus

from .compiler import compile_buff_graph_spec
from .executor import execute_compiled_buff_graph
from .trace import validate_buff_graph_trace


@dataclass(frozen=True, slots=True)
class BuffGraphCandidateParityOracle:
    case_id: str
    expected_final_output: Mapping[str, Any]
    expected_trace_kind_checkpoint: Sequence[Sequence[str]]
    legacy_oracle: str = "legacy_python_fixture"


@dataclass(frozen=True, slots=True)
class BuffGraphCandidateParityResult:
    case_id: str
    graph_id: str
    runtime_status: str
    legacy_oracle: str
    passed: bool
    compile_passed: bool
    execution_passed: bool
    output_passed: bool
    trace_valid: bool
    trace_checkpoint_passed: bool
    errors: tuple[str, ...]
    expected_final_output: Mapping[str, Any]
    actual_final_output: Mapping[str, Any]
    expected_trace_kind_checkpoint: tuple[tuple[str, str], ...]
    actual_trace_kind_checkpoint: tuple[tuple[str, str], ...]

    def to_evidence(self) -> dict[str, Any]:
        return asdict(self)


def run_buff_graph_candidate_parity(
    spec: BuffGraphSpec,
    *,
    block_registry: BuffGraphBlockRegistry,
    adapters: Mapping[str, BuffGraphAdapter],
    tick: int,
    prepared_context: Mapping[str, Any],
    oracle: BuffGraphCandidateParityOracle,
) -> BuffGraphCandidateParityResult:
    errors: list[str] = []
    if spec.runtime_status == RuntimeStatus.VISUAL_GRAPH_DEFAULT:
        errors.append("visual_graph_default is not allowed in candidate parity harness")

    compile_result = compile_buff_graph_spec(spec, block_registry=block_registry)
    if not compile_result.passed:
        errors.extend(f"compile:{error.code}:{error.path}" for error in compile_result.errors)
        return BuffGraphCandidateParityResult(
            case_id=oracle.case_id,
            graph_id=spec.graph_id,
            runtime_status=spec.runtime_status.value,
            legacy_oracle=oracle.legacy_oracle,
            passed=False,
            compile_passed=False,
            execution_passed=False,
            output_passed=False,
            trace_valid=False,
            trace_checkpoint_passed=False,
            errors=tuple(errors),
            expected_final_output=dict(oracle.expected_final_output),
            actual_final_output={},
            expected_trace_kind_checkpoint=_trace_checkpoint_tuple(
                oracle.expected_trace_kind_checkpoint
            ),
            actual_trace_kind_checkpoint=(),
        )

    assert compile_result.compiled is not None
    execution = execute_compiled_buff_graph(
        compile_result.compiled,
        adapters=adapters,
        tick=tick,
        prepared_context=prepared_context,
    )
    if not execution.passed:
        errors.extend(f"execute:{error.code}:{error.path}" for error in execution.errors)

    expected_output = _normalize(dict(oracle.expected_final_output))
    actual_output = _normalize(dict(execution.outputs))
    output_passed = actual_output == expected_output
    if not output_passed:
        errors.append("output_mismatch")

    trace_errors = validate_buff_graph_trace(execution.trace)
    trace_valid = not trace_errors
    if trace_errors:
        errors.extend(f"trace:{error.code}:{error.path}" for error in trace_errors)

    expected_trace = _trace_checkpoint_tuple(oracle.expected_trace_kind_checkpoint)
    actual_trace = tuple((event.kind.value, event.checkpoint) for event in execution.trace.events)
    trace_checkpoint_passed = actual_trace == expected_trace
    if not trace_checkpoint_passed:
        errors.append("trace_checkpoint_mismatch")

    return BuffGraphCandidateParityResult(
        case_id=oracle.case_id,
        graph_id=spec.graph_id,
        runtime_status=spec.runtime_status.value,
        legacy_oracle=oracle.legacy_oracle,
        passed=not errors,
        compile_passed=True,
        execution_passed=execution.passed,
        output_passed=output_passed,
        trace_valid=trace_valid,
        trace_checkpoint_passed=trace_checkpoint_passed,
        errors=tuple(errors),
        expected_final_output=dict(oracle.expected_final_output),
        actual_final_output=dict(execution.outputs),
        expected_trace_kind_checkpoint=expected_trace,
        actual_trace_kind_checkpoint=actual_trace,
    )


def _trace_checkpoint_tuple(rows: Sequence[Sequence[str]]) -> tuple[tuple[str, str], ...]:
    return tuple((str(row[0]), str(row[1])) for row in rows)


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _normalize(value[key]) for key in sorted(value)}
    if isinstance(value, list | tuple):
        return tuple(_normalize(item) for item in value)
    return value
