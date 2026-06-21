from __future__ import annotations

import sys
from collections.abc import Iterable
from types import SimpleNamespace
from typing import Any, SupportsIndex

import pytest
import zsim.define as define_module
import zsim.sim_progress.Character.Seed as seed_character_module
import zsim.sim_progress.ScheduledEvent as scheduled_event_module
import zsim.sim_progress.ScheduledEvent.buff_runtime as buff_runtime_module
import zsim.sim_progress.ScheduledEvent.runtime_command as runtime_command_module
import zsim.sim_progress.data_struct.schedule_dispatch as schedule_dispatch_module

sys.modules.setdefault("define", define_module)

from zsim.sim_progress.Buff import JudgeTools
from zsim.sim_progress.Buff.JudgeTools import CharacterLookup
from zsim.sim_progress.Buff.BuffXLogic.SeedAdditionalAbilityTrigger import (
    SeedAdditionalAbilityTrigger,
    SeedAdditionalAbilityTriggerRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedBesiegeBonus import (
    SeedBesiegeBonus,
    SeedBesiegeBonusRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedBesiegeBonusTrigger import (
    SeedBesiegeBonusTrigger,
    SeedBesiegeBonusTriggerRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedCinema2BesiegeIgnoreDefense import (
    SeedCinema2BesiegeIgnoreDefense,
    SeedCinema2BesiegeIgnoreDefenseRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedCinema2BesiegeIgnoreDefenceTrigger import (
    SeedCinema2BesiegeIgnoreDefenceTrigger,
    SeedCinema2BesiegeIgnoreDefenceTriggerRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedCinema4Trigger import (
    SeedCinema4Trigger,
    SeedCinema4TriggerRecord,
)
from zsim.sim_progress.Buff.BuffXLogic.SeedDirectStrikeTrigger import (
    SeedDirectStrikeTrigger,
    SeedDirectStrikeTriggerRecord,
)


class _FailFastEventList(list[Any]):
    def append(self, item: Any) -> None:
        raise AssertionError("Seed caller should not publish scheduled events")

    def extend(self, items: Iterable[Any]) -> None:
        raise AssertionError("Seed caller should not publish scheduled events")

    def insert(self, index: SupportsIndex, item: Any) -> None:
        raise AssertionError("Seed caller should not publish scheduled events")


class _FailFastLoadingBuffDict(dict[str, list[Any]]):
    def __getitem__(self, key: str) -> list[Any]:
        raise AssertionError("Seed caller should not touch LOADING_BUFF_DICT")

    def get(self, key: str, default: Any = None) -> Any:
        raise AssertionError("Seed caller should not touch LOADING_BUFF_DICT")

    def __setitem__(self, key: str, value: list[Any]) -> None:
        raise AssertionError("Seed caller should not touch LOADING_BUFF_DICT")


class _SeedStub:
    CID = 1461
    NAME = "席德"

    def __init__(
        self,
        *,
        besiege_state: tuple[bool, bool] = (False, False),
        direct_strike_active: bool = False,
        vanguard_name: str | None = "安比",
    ) -> None:
        self._besiege_state = besiege_state
        self._direct_strike_active = direct_strike_active
        self.besiege_calls: list[str] = []
        self.vanguard = (
            None if vanguard_name is None else SimpleNamespace(NAME=vanguard_name)
        )

    @property
    def direct_strike_active(self) -> bool:
        return self._direct_strike_active

    def besiege_active_check(self) -> tuple[bool, bool]:
        self.besiege_calls.append("besiege_active_check")
        return self._besiege_state


def _fail_listener_broadcast(*args: object, **kwargs: object) -> None:
    raise AssertionError("Seed caller should not broadcast listener events")


def _patch_runtime_boundary_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_create_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Seed caller should not create RuntimeCommandPort")

    def fail_create_buff_runtime_read_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Seed caller should not create BuffRuntimeReadPort")

    def fail_create_schedule_dispatch_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("Seed caller should not create ScheduleDispatchPort")

    monkeypatch.setattr(
        runtime_command_module,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
        raising=False,
    )
    monkeypatch.setattr(
        buff_runtime_module,
        "create_buff_runtime_read_port",
        fail_create_buff_runtime_read_port,
    )
    monkeypatch.setattr(
        scheduled_event_module,
        "create_buff_runtime_read_port",
        fail_create_buff_runtime_read_port,
        raising=False,
    )
    monkeypatch.setattr(
        schedule_dispatch_module,
        "create_schedule_dispatch_port",
        fail_create_schedule_dispatch_port,
    )


def _build_seed_harness(
    logic_cls: type[Any],
    record_cls: type[Any],
    seed: _SeedStub,
) -> SimpleNamespace:
    listener_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fail_broadcast_event(*args: object, **kwargs: object) -> None:
        listener_calls.append((args, kwargs))
        _fail_listener_broadcast(*args, **kwargs)

    sim_instance = SimpleNamespace(
        tick=1461,
        schedule_data=SimpleNamespace(event_list=_FailFastEventList()),
        load_data=SimpleNamespace(LOADING_BUFF_DICT=_FailFastLoadingBuffDict()),
        listener_manager=SimpleNamespace(broadcast_event=fail_broadcast_event),
    )
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="seed-trigger"),
    )
    logic = logic_cls(buff_instance)
    record = record_cls()
    record.char = seed

    return SimpleNamespace(
        logic=logic,
        listener_calls=listener_calls,
        record=record,
        sim_instance=sim_instance,
    )


def _build_seed_preparation_sim_instance(
    *,
    buff_index: str,
    buff_0: object,
    seed: object,
) -> SimpleNamespace:
    return SimpleNamespace(
        init_data=SimpleNamespace(Judge_list_set=[]),
        char_data=SimpleNamespace(char_obj_list=[seed]),
        load_data=SimpleNamespace(
            exist_buff_dict={"席德": {buff_index: buff_0}},
            action_stack=object(),
        ),
        global_stats=SimpleNamespace(DYNAMIC_BUFF_DICT={}),
        schedule_data=SimpleNamespace(enemy=object()),
        preload=SimpleNamespace(preload_data=object()),
    )


def _patch_seed_dependencies(
    monkeypatch: pytest.MonkeyPatch,
    harness: SimpleNamespace,
) -> list[tuple[str, dict[str, object]]]:
    _patch_runtime_boundary_guards(monkeypatch)

    def fail_raw_event_list_lookup(*args: object, **kwargs: object) -> None:
        raise AssertionError("Seed caller should not read raw event_list")

    def fail_raw_exist_buff_lookup(*args: object, **kwargs: object) -> None:
        raise AssertionError("Seed caller should use the injected focused record")

    def fake_check_record_module() -> None:
        harness.logic.record = harness.record

    prepared_calls: list[dict[str, object]] = []

    def fake_get_prepared(**kwargs: object) -> None:
        prepared_calls.append(kwargs)

    buff_add_calls: list[tuple[str, dict[str, object]]] = []

    def fake_buff_add_strategy(buff_index: str, **kwargs: object) -> None:
        buff_add_calls.append((buff_index, kwargs))

    monkeypatch.setattr(seed_character_module, "Seed", _SeedStub)
    monkeypatch.setattr(
        JudgeTools,
        "find_event_list",
        fail_raw_event_list_lookup,
        raising=False,
    )
    monkeypatch.setattr(
        JudgeTools,
        "find_exist_buff_dict",
        fail_raw_exist_buff_lookup,
        raising=False,
    )
    monkeypatch.setattr(harness.logic, "check_record_module", fake_check_record_module)
    monkeypatch.setattr(harness.logic, "get_prepared", fake_get_prepared)
    monkeypatch.setattr(
        "zsim.sim_progress.Buff.BuffAddStrategy.buff_add_strategy",
        fake_buff_add_strategy,
    )

    harness.prepared_calls = prepared_calls
    return buff_add_calls


def _assert_no_cross_layer_writes(harness: SimpleNamespace) -> None:
    assert harness.listener_calls == []
    assert harness.sim_instance.schedule_data.event_list == []
    assert isinstance(
        harness.sim_instance.load_data.LOADING_BUFF_DICT,
        _FailFastLoadingBuffDict,
    )


def test_character_lookup_preserves_cid_name_order_and_missing_errors() -> None:
    seed = SimpleNamespace(CID=1461, NAME="席德")
    anby = SimpleNamespace(CID=1381, NAME="零号安比")
    duplicate_cid = SimpleNamespace(CID=1461, NAME="重复席德")
    lookup = CharacterLookup([seed, anby, duplicate_cid])

    assert lookup.by_cid(1461) is seed
    assert lookup.by_name("零号安比") is anby
    with pytest.raises(ValueError, match="CID为9999"):
        lookup.by_cid(9999)
    with pytest.raises(ValueError, match="未找到名为不存在的角色"):
        lookup.by_name("不存在的角色")


@pytest.mark.parametrize(
    ("logic_cls", "record_cls"),
    [
        (SeedAdditionalAbilityTrigger, SeedAdditionalAbilityTriggerRecord),
        (SeedBesiegeBonus, SeedBesiegeBonusRecord),
        (SeedBesiegeBonusTrigger, SeedBesiegeBonusTriggerRecord),
        (
            SeedCinema2BesiegeIgnoreDefenceTrigger,
            SeedCinema2BesiegeIgnoreDefenceTriggerRecord,
        ),
        (SeedCinema2BesiegeIgnoreDefense, SeedCinema2BesiegeIgnoreDefenseRecord),
    ],
)
def test_seed_batch_uses_preparation_context_for_character_lookup(
    logic_cls: type[Any],
    record_cls: type[Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _SeedStub()
    buff_0 = SimpleNamespace(history=SimpleNamespace(record=None))
    sim_instance = _build_seed_preparation_sim_instance(
        buff_index="seed-trigger",
        buff_0=buff_0,
        seed=seed,
    )
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="seed-trigger"),
    )
    logic = logic_cls(buff_instance)

    def fail_legacy_lookup(*args: object, **kwargs: object) -> None:
        raise AssertionError("migrated Seed trigger should use PreparationContext")

    monkeypatch.setattr(JudgeTools, "find_exist_buff_dict", fail_legacy_lookup)
    monkeypatch.setattr(JudgeTools, "find_char_from_CID", fail_legacy_lookup)
    monkeypatch.setattr(JudgeTools, "find_char_from_name", fail_legacy_lookup)

    logic.check_record_module()
    logic.get_prepared(char_CID=1461)

    assert logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, record_cls)
    assert logic.record is buff_0.history.record
    assert logic.record.char is seed


@pytest.mark.parametrize(
    ("logic_cls", "record_cls", "expected_buff_index"),
    [
        (
            SeedBesiegeBonusTrigger,
            SeedBesiegeBonusTriggerRecord,
            "Buff-角色-席德-围杀",
        ),
        (
            SeedCinema2BesiegeIgnoreDefenceTrigger,
            SeedCinema2BesiegeIgnoreDefenceTriggerRecord,
            "Buff-角色-席德-影画-2画-围杀无视防御力",
        ),
        (
            SeedCinema4Trigger,
            SeedCinema4TriggerRecord,
            "Buff-角色-席德-影画-4画-喧响效率与大招增伤",
        ),
    ],
)
def test_seed_besiege_family_uses_explicit_benefit_list_for_active_targets(
    logic_cls: type[Any],
    record_cls: type[Any],
    expected_buff_index: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _SeedStub(besiege_state=(True, True), vanguard_name="安比")
    harness = _build_seed_harness(logic_cls, record_cls, seed)
    buff_add_calls = _patch_seed_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert seed.besiege_calls == ["besiege_active_check"]
    assert harness.prepared_calls == [{"char_CID": 1461}]
    assert buff_add_calls == [
        (
            expected_buff_index,
            {"benifit_list": ["席德", "安比"], "sim_instance": harness.sim_instance},
        )
    ]
    assert "specified_count" not in buff_add_calls[0][1]
    _assert_no_cross_layer_writes(harness)


def test_seed_besiege_family_skips_for_empty_benefit_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _SeedStub(besiege_state=(False, False), vanguard_name="安比")
    harness = _build_seed_harness(
        SeedBesiegeBonusTrigger,
        SeedBesiegeBonusTriggerRecord,
        seed,
    )
    buff_add_calls = _patch_seed_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert seed.besiege_calls == ["besiege_active_check"]
    assert harness.prepared_calls == [{"char_CID": 1461}]
    assert buff_add_calls == []
    _assert_no_cross_layer_writes(harness)


def test_seed_direct_strike_uses_vanguard_target_and_sim_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _SeedStub(direct_strike_active=True, vanguard_name="安比")
    harness = _build_seed_harness(
        SeedDirectStrikeTrigger,
        SeedDirectStrikeTriggerRecord,
        seed,
    )
    buff_add_calls = _patch_seed_dependencies(monkeypatch, harness)

    harness.logic.special_hit_logic()

    assert harness.prepared_calls == [{"char_CID": 1461, "sub_exist_buff_dict": 1}]
    assert buff_add_calls == [
        (
            "Buff-角色-席德-明攻",
            {"benifit_list": ["安比"], "sim_instance": harness.sim_instance},
        )
    ]
    assert "specified_count" not in buff_add_calls[0][1]
    _assert_no_cross_layer_writes(harness)


def test_seed_direct_strike_judge_blocks_without_vanguard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = _SeedStub(direct_strike_active=True, vanguard_name=None)
    harness = _build_seed_harness(
        SeedDirectStrikeTrigger,
        SeedDirectStrikeTriggerRecord,
        seed,
    )
    buff_add_calls = _patch_seed_dependencies(monkeypatch, harness)

    assert harness.logic.special_judge_logic() is False

    assert harness.prepared_calls == [{"char_CID": 1461}]
    assert buff_add_calls == []
    _assert_no_cross_layer_writes(harness)
