from zsim.sim_progress.BuffGraph.blocks import build_default_block_registry
from zsim.sim_progress.BuffGraph.migration import classify_xlogic_source, import_xlogic_to_graph
from zsim.sim_progress.BuffGraph.runtime.compiler import compile_buff_graph_spec
from zsim.sim_progress.BuffGraph.spec import OwnerKind, RuntimeStatus, validate_buff_graph_spec


def test_importer_creates_low_risk_buff_graph_spec_without_code_nodes() -> None:
    source = """
class AliceCinema6Trigger:
    def xhit(self, **kwargs):
        if kwargs["skill_tag"] == "basic":
            self.buff.update_count(1)
            self.buff.start()
"""

    result = import_xlogic_to_graph(
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/AliceCinema6Trigger.py",
        source=source,
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index="Buff-角色-爱丽丝-影画6",
    )

    assert result.imported is True
    assert result.spec is not None
    assert result.spec.runtime_status is RuntimeStatus.LEGACY_PYTHON
    assert result.spec.created_from_xlogic.endswith("AliceCinema6Trigger.py")
    assert [node.block_id for node in result.spec.nodes] == [
        "trigger.skill_hit",
        "condition.buff_active",
        "effect.start_buff",
        "effect.update_buff_count",
    ]
    assert validate_buff_graph_spec(result.spec) == ()
    assert compile_buff_graph_spec(result.spec, block_registry=build_default_block_registry()).passed is True


def test_importer_records_unsupported_patterns_instead_of_custom_code_nodes() -> None:
    source = """
class ScheduledProducer:
    def xhit(self, **kwargs):
        self.schedule.event_list.append(kwargs["event"])
        return self.enemy.anomaly_bar
"""

    result = import_xlogic_to_graph(
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/ScheduledProducer.py",
        source=source,
        owner_kind=OwnerKind.CHARACTER,
        owner_name="Alice",
        source_buff_index=None,
    )

    assert result.imported is False
    assert result.spec is None
    assert [pattern.pattern_id for pattern in result.unsupported_patterns] == [
        "runtime_command_or_scheduled_producer",
        "enemy_anomaly_or_dot_read",
    ]


def test_classifier_assigns_record_cooldown_stack_wave() -> None:
    classification = classify_xlogic_source(
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
        source="""
class CannonRotor:
    def xhit(self, **kwargs):
        if self.record.last_tick + self.cooldown <= kwargs["tick"]:
            self.buff.count += 1
""",
    )

    assert classification.migration_wave == "record-cooldown-stack"
    assert "state.cooldown_gate" in classification.state
    assert "state.last_active_tick" in classification.state
    assert "effect.update_buff_count" in classification.effects


def test_importer_keeps_parse_errors_as_unsupported_pattern() -> None:
    result = import_xlogic_to_graph(
        xlogic_path="zsim/sim_progress/Buff/BuffXLogic/Broken.py",
        source="def broken(:",
        owner_kind=OwnerKind.UNKNOWN,
        owner_name="unknown",
        source_buff_index=None,
    )

    assert result.spec is None
    assert [pattern.pattern_id for pattern in result.unsupported_patterns] == ["parse_error"]
