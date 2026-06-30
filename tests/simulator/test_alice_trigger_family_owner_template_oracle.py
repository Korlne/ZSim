from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any, cast

import pytest
import zsim.define as define_module

sys.modules.setdefault("define", define_module)

import zsim.sim_progress.Buff.BuffXLogic.AliceCinema6Trigger as cinema_module
import zsim.sim_progress.Buff.BuffXLogic.AlicePolarizedAssaultTrigger as polarized_module
import zsim.sim_progress.Character.Alice as alice_character_module
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.data_struct import PolarizedAssaultEvent
from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduleDispatchPort,
    ScheduledEventEmitterProvider,
)


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(
    module: Any,
    logic_cls: type[Any],
    *,
    index: str = "alice-template-index",
    tick: int = 300,
    scheduled_event_emitter_provider: ScheduledEventEmitterProvider | None = None,
) -> SimpleNamespace:
    schedule_data = SimpleNamespace(
        enemy=SimpleNamespace(anomaly_bars_dict={0: _FakeAnomalyBar(marker="source")}),
        change_process_state=lambda: None,
    )
    sim_instance = SimpleNamespace(tick=tick, schedule_data=schedule_data)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    if scheduled_event_emitter_provider is None:
        logic = logic_cls(cast(Any, buff_instance))
    else:
        logic = logic_cls(
            cast(Any, buff_instance),
            scheduled_event_emitter_provider=scheduled_event_emitter_provider,
        )
    return SimpleNamespace(
        module=module,
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    char_name: str = "安比",
    skill_tag: str = "1401_SNA_3",
    tick_list: list[int] | None = None,
    skill_text: str = "test skill",
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.skill_tag = skill_tag
    node.tick_list = tick_list if tick_list is not None else [300]
    node.skill = SimpleNamespace(skill_text=skill_text)
    return node


def _install_direct_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: SimpleNamespace,
    buff_0: SimpleNamespace,
    registry: dict[str, dict[str, object]] | None = None,
) -> list[object]:
    lookup_calls: list[object] = []
    lookup_registry = registry if registry is not None else {"爱丽丝": {harness.buff_instance.ft.index: buff_0}}

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        lookup_calls.append(sim_instance)
        return lookup_registry

    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    return lookup_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: SimpleNamespace,
    buff_0: SimpleNamespace,
    char: object,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        preparation_calls.append(dict(kwargs))
        cast(Any, buff_0_ref.history.record).char = char_ref

    buff_0_ref = buff_0
    char_ref = char
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _prepared_logic(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    logic_cls: type[Any],
    char: object,
    tick: int = 300,
    scheduled_event_emitter_provider: ScheduledEventEmitterProvider | None = None,
) -> tuple[SimpleNamespace, SimpleNamespace, list[object], list[dict[str, object]]]:
    harness = _logic_harness(
        module,
        logic_cls,
        tick=tick,
        scheduled_event_emitter_provider=scheduled_event_emitter_provider,
    )
    buff_0 = _buff_0()
    lookup_calls = _install_direct_lookup(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        char=char,
    )
    return harness, buff_0, lookup_calls, preparation_calls


class _FakeAlice:
    NAME = "爱丽丝"

    def __init__(
        self,
        *,
        cinema: int = 6,
        victory_state: bool = True,
    ) -> None:
        self.cinema = cinema
        self.victory_state = victory_state
        self.spawn_calls = 0

    def spawn_extra_attack(self) -> None:
        self.spawn_calls += 1


class _RecordingDispatchPort(ScheduleDispatchPort):
    def __init__(self) -> None:
        self.events: list[object] = []

    def publish_scheduled(self, event: object) -> None:
        self.events.append(event)


class _FakeAnomalyBar:
    def __init__(
        self,
        *,
        marker: str,
        sim_instance: object | None = None,
        activated_by: object | None = None,
        settled: bool = False,
    ) -> None:
        self.marker = marker
        self.sim_instance = sim_instance
        self.activated_by = activated_by
        self.settled = settled
        self.element_type = 0
        self.rename_tag = None

    def anomaly_settled(self) -> None:
        self.settled = True

    def __deepcopy__(self, memo: dict[int, object]) -> "_FakeAnomalyBar":
        return type(self)(
            marker=f"{self.marker}-copy",
            sim_instance=self.sim_instance,
            activated_by=self.activated_by,
            settled=self.settled,
        )


@pytest.mark.parametrize(
    ("module", "logic_cls", "record_cls"),
    [
        (
            cinema_module,
            cinema_module.AliceCinema6Trigger,
            cinema_module.AliceCinema6TriggerRecord,
        ),
        (
            polarized_module,
            polarized_module.AlicePolarizedAssaultTrigger,
            polarized_module.AlicePolarizedAssaultTriggerRecord,
        ),
    ],
)
def test_alice_trigger_family_check_record_module_pins_direct_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
    record_cls: type[Any],
) -> None:
    harness = _logic_harness(module, logic_cls, index="alice-template-index")
    buff_0 = _buff_0()
    lookup_calls = _install_direct_lookup(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, record_cls)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char is None

    if record_cls is cinema_module.AliceCinema6TriggerRecord:
        assert cast(Any, harness.logic.record).additional_attack_skill_tag == "1401_Cinema_6"
        assert cast(Any, harness.logic.record).cd == 60
    else:
        assert cast(Any, harness.logic.record).allowed_skill_tag_list == ["1401_SNA_3", "1401_Q"]
        assert cast(Any, harness.logic.record).trigger_origin is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


@pytest.mark.parametrize(
    ("module", "logic_cls", "registry"),
    [
        (cinema_module, cinema_module.AliceCinema6Trigger, {}),
        (cinema_module, cinema_module.AliceCinema6Trigger, {"爱丽丝": {}}),
        (polarized_module, polarized_module.AlicePolarizedAssaultTrigger, {}),
        (polarized_module, polarized_module.AlicePolarizedAssaultTrigger, {"爱丽丝": {}}),
    ],
)
def test_alice_trigger_family_check_record_module_pins_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    logic_cls: type[Any],
    registry: dict[str, dict[str, object]],
) -> None:
    harness = _logic_harness(module, logic_cls, index="missing-template-index")
    _install_direct_lookup(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=_buff_0(),
        registry=registry,
    )

    with pytest.raises(KeyError):
        harness.logic.check_record_module()


def test_alice_cinema6_special_judge_logic_pins_char_preparation_and_missing_type_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(alice_character_module, "Alice", _FakeAlice)
    char = _FakeAlice()
    harness, _, lookup_calls, preparation_calls = _prepared_logic(
        monkeypatch,
        module=cinema_module,
        logic_cls=cinema_module.AliceCinema6Trigger,
        char=char,
    )

    assert harness.logic.special_judge_logic() is False

    with pytest.raises(AssertionError, match="skill_node"):
        harness.logic.special_judge_logic(skill_node=object())

    assert lookup_calls == [harness.sim_instance]
    assert preparation_calls == [
        {"char_CID": 1401},
        {"char_CID": 1401},
    ]


@pytest.mark.parametrize(
    (
        "skill_char_name",
        "victory_state",
        "tick_list",
        "last_active_tick",
        "expected",
    ),
    [
        ("爱丽丝", True, [300], 0, False),
        ("安比", False, [300], 0, False),
        ("安比", True, [299], 0, False),
        ("安比", True, [300], 250, False),
        ("安比", True, [300], 0, True),
    ],
)
def test_alice_cinema6_special_judge_logic_pins_owner_victory_hit_and_cooldown_gates(
    monkeypatch: pytest.MonkeyPatch,
    skill_char_name: str,
    victory_state: bool,
    tick_list: list[int],
    last_active_tick: int,
    expected: bool,
) -> None:
    monkeypatch.setattr(alice_character_module, "Alice", _FakeAlice)
    char = _FakeAlice(victory_state=victory_state)
    harness, buff_0, lookup_calls, preparation_calls = _prepared_logic(
        monkeypatch,
        module=cinema_module,
        logic_cls=cinema_module.AliceCinema6Trigger,
        char=char,
        tick=300,
    )
    harness.logic.check_record_module()
    cast(Any, buff_0.history.record).last_active_tick = last_active_tick

    result = harness.logic.special_judge_logic(
        skill_node=_skill_node(char_name=skill_char_name, tick_list=tick_list)
    )

    assert result is expected
    assert lookup_calls == [harness.sim_instance]
    assert preparation_calls == [{"char_CID": 1401}]


def test_alice_cinema6_special_hit_logic_pins_extra_attack_and_last_active_tick(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(alice_character_module, "Alice", _FakeAlice)
    char = _FakeAlice()
    harness, _, _, preparation_calls = _prepared_logic(
        monkeypatch,
        module=cinema_module,
        logic_cls=cinema_module.AliceCinema6Trigger,
        char=char,
        tick=360,
    )

    harness.logic.special_hit_logic()

    assert char.spawn_calls == 1
    assert cast(Any, harness.logic.record).last_active_tick == 360
    assert preparation_calls == [{"char_CID": 1401}]


def test_alice_cinema6_special_logic_pins_non_alice_prepared_char_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(alice_character_module, "Alice", _FakeAlice)
    harness, _, _, _ = _prepared_logic(
        monkeypatch,
        module=cinema_module,
        logic_cls=cinema_module.AliceCinema6Trigger,
        char=SimpleNamespace(NAME="not Alice", victory_state=True),
    )

    with pytest.raises(TypeError, match="并非爱丽丝"):
        harness.logic.special_judge_logic(
            skill_node=_skill_node(char_name="安比", tick_list=[300])
        )


def test_alice_polarized_special_judge_logic_pins_missing_type_and_allowed_tag_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    char = _FakeAlice(cinema=2)
    harness, _, lookup_calls, preparation_calls = _prepared_logic(
        monkeypatch,
        module=polarized_module,
        logic_cls=polarized_module.AlicePolarizedAssaultTrigger,
        char=char,
    )

    assert harness.logic.special_judge_logic() is False
    assert harness.logic.special_judge_logic(skill_node=object()) is False
    assert harness.logic.special_judge_logic(
        skill_node=_skill_node(skill_tag="1401_BAD", tick_list=[300])
    ) is False

    assert lookup_calls == [harness.sim_instance]
    assert preparation_calls == [
        {"char_CID": 1401},
        {"char_CID": 1401},
        {"char_CID": 1401},
    ]


@pytest.mark.parametrize(
    ("skill_tag", "tick_list", "cinema", "expected"),
    [
        ("1401_SNA_3", [299], 6, False),
        ("1401_Q", [300], 1, False),
        ("1401_SNA_3", [300], 0, True),
        ("1401_Q", [300], 2, True),
    ],
)
def test_alice_polarized_special_judge_logic_pins_last_hit_cinema_and_trigger_origin_gates(
    monkeypatch: pytest.MonkeyPatch,
    skill_tag: str,
    tick_list: list[int],
    cinema: int,
    expected: bool,
) -> None:
    char = _FakeAlice(cinema=cinema)
    harness, buff_0, _, preparation_calls = _prepared_logic(
        monkeypatch,
        module=polarized_module,
        logic_cls=polarized_module.AlicePolarizedAssaultTrigger,
        char=char,
        tick=300,
    )
    skill_node = _skill_node(skill_tag=skill_tag, tick_list=tick_list)

    result = harness.logic.special_judge_logic(skill_node=skill_node)

    assert result is expected
    expected_origin = skill_node if expected else None
    assert cast(Any, buff_0.history.record).trigger_origin is expected_origin
    assert preparation_calls == [{"char_CID": 1401}]


def test_alice_polarized_special_judge_logic_pins_pending_trigger_origin_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    char = _FakeAlice(cinema=6)
    harness, buff_0, _, _ = _prepared_logic(
        monkeypatch,
        module=polarized_module,
        logic_cls=polarized_module.AlicePolarizedAssaultTrigger,
        char=char,
        tick=300,
    )
    harness.logic.check_record_module()
    pending = _skill_node(skill_tag="1401_Q", skill_text="pending")
    cast(Any, buff_0.history.record).trigger_origin = pending

    with pytest.raises(ValueError, match="尚未处理"):
        harness.logic.special_judge_logic(
            skill_node=_skill_node(skill_tag="1401_SNA_3", tick_list=[300])
        )

    assert cast(Any, buff_0.history.record).trigger_origin is pending


def test_alice_polarized_special_effect_logic_pins_scheduled_event_emission_and_origin_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dispatch_port = _RecordingDispatchPort()
    trigger_origin = _skill_node(skill_tag="1401_Q", tick_list=[420], skill_text="ultimate")
    char = _FakeAlice(cinema=6)
    harness, buff_0, lookup_calls, preparation_calls = _prepared_logic(
        monkeypatch,
        module=polarized_module,
        logic_cls=polarized_module.AlicePolarizedAssaultTrigger,
        char=char,
        tick=420,
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: cast(ScheduleDispatchPort, dispatch_port)
        ),
    )
    harness.logic.check_record_module()
    source_anomaly = _FakeAnomalyBar(marker="source", sim_instance=harness.sim_instance)
    harness.sim_instance.schedule_data.enemy.anomaly_bars_dict[0] = source_anomaly
    cast(Any, buff_0.history.record).trigger_origin = trigger_origin

    harness.logic.special_effect_logic()

    assert lookup_calls == [harness.sim_instance]
    assert preparation_calls == [{"char_CID": 1401}]
    assert len(dispatch_port.events) == 1
    event = dispatch_port.events[0]
    assert isinstance(event, PolarizedAssaultEvent)
    assert event.execute_tick == 420
    assert event.char is char
    assert event.skill_node is trigger_origin
    assert event.anomaly_bar is not source_anomaly
    assert event.anomaly_bar.marker == "source-copy"
    assert event.anomaly_bar.activated_by is trigger_origin
    assert event.anomaly_bar.settled is True
    assert source_anomaly.activated_by is None
    assert source_anomaly.settled is False
    assert cast(Any, buff_0.history.record).trigger_origin is None


def test_alice_polarized_special_effect_logic_pins_current_missing_origin_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dispatch_port = _RecordingDispatchPort()
    char = _FakeAlice(cinema=6)
    harness, buff_0, _, _ = _prepared_logic(
        monkeypatch,
        module=polarized_module,
        logic_cls=polarized_module.AlicePolarizedAssaultTrigger,
        char=char,
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: cast(ScheduleDispatchPort, dispatch_port)
        ),
    )
    harness.logic.check_record_module()
    cast(Any, buff_0.history.record).trigger_origin = None

    with pytest.raises(AttributeError, match="skill_tag"):
        harness.logic.special_effect_logic()

    assert dispatch_port.events == []
    assert cast(Any, buff_0.history.record).trigger_origin is None
