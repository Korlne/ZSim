from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Iterable, NoReturn, SupportsIndex

import pytest

import zsim.sim_progress.Buff.BuffXLogic.AstraYaoCorePassiveAtkBonus as astra_module
import zsim.sim_progress.Character as character_pkg
from zsim.sim_progress.Buff.BuffXLogic.AstraYaoCorePassiveAtkBonus import (
    AstraYaoCorePassiveAtkBonus,
)


class _FailFastEventList(list[object]):
    def _fail(self) -> NoReturn:
        raise AssertionError("Report-state context should not mutate scheduled queues")

    def append(self, item: object) -> None:
        self._fail()

    def extend(self, items: Iterable[object]) -> None:
        self._fail()

    def insert(self, index: SupportsIndex, item: object) -> None:
        self._fail()

    def __setitem__(self, key: SupportsIndex | slice, value: Any) -> None:
        self._fail()

    def __delitem__(self, key: SupportsIndex | slice) -> None:
        self._fail()

    def pop(self, index: SupportsIndex = -1) -> object:
        self._fail()

    def clear(self) -> None:
        self._fail()


class _ScheduleDataReportProbe:
    def __init__(self, *, order_log: list[str]) -> None:
        self.event_list = _FailFastEventList()
        self.change_process_calls = 0
        self.order_log = order_log

    def change_process_state(self) -> None:
        self.change_process_calls += 1
        self.order_log.append("report")


class _CharacterProbe:
    NAME = "耀嘉音"
    CID = 1311

    def __init__(self, *, atk: int = 2000) -> None:
        self.statement = SimpleNamespace(ATK=atk)


class _BuffInstanceProbe:
    def __init__(self, *, sim_instance: SimpleNamespace, order_log: list[str]) -> None:
        self.sim_instance = sim_instance
        self.ft = SimpleNamespace(
            index="Buff-角色-耀嘉音-核心被动攻击力",
            maxcount=999,
            maxduration=2400,
        )
        self.dy = SimpleNamespace(active=False, startticks=0, endticks=0, count=0)
        self.simple_start_calls: list[dict[str, Any]] = []
        self.update_to_buff_0_calls: list[object] = []
        self.order_log = order_log

    def simple_start(
        self,
        timenow: int,
        sub_exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        self.simple_start_calls.append(
            {
                "timenow": timenow,
                "sub_exist_buff_dict": sub_exist_buff_dict,
                "kwargs": kwargs,
            }
        )
        if not kwargs.get("no_start"):
            self.dy.startticks = timenow
        self.order_log.append("simple_start")

    def update_to_buff_0(self, buff_0: object) -> None:
        self.update_to_buff_0_calls.append(buff_0)
        self.order_log.append("update_to_buff_0")


def _fail_listener_broadcast(*args: object, **kwargs: object) -> None:
    raise AssertionError("Report-state context should not broadcast listener events")


def _build_astra_core_harness(
    monkeypatch: pytest.MonkeyPatch,
    *,
    active_buff_0: bool = False,
    same_tick_record: bool = False,
) -> SimpleNamespace:
    order_log: list[str] = []
    sim_instance = SimpleNamespace(
        tick=90,
        schedule_data=_ScheduleDataReportProbe(order_log=order_log),
        listener_manager=SimpleNamespace(broadcast_event=_fail_listener_broadcast),
    )
    buff_instance = _BuffInstanceProbe(
        sim_instance=sim_instance,
        order_log=order_log,
    )
    record = astra_module.AstraYaoCorePassiveAtkBonusRecord()
    record.char = _CharacterProbe()
    buff_0 = SimpleNamespace(
        dy=SimpleNamespace(active=active_buff_0),
        history=SimpleNamespace(record=record),
    )
    record.sub_exist_buff_dict = {buff_instance.ft.index: buff_0}
    if same_tick_record:
        record.update_info_box["苍角"] = {
            "startticks": sim_instance.tick,
            "endticks": sim_instance.tick + record.duration_added_per_active,
            "count": 700.0,
        }

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        return {"耀嘉音": {buff_instance.ft.index: buff_0}}

    monkeypatch.setattr(astra_module, "ASTRAYAO_REPORT", True)
    monkeypatch.setattr(astra_module, "check_preparation", lambda **kwargs: True)
    monkeypatch.setattr(
        astra_module,
        "find_tick",
        lambda *, sim_instance: sim_instance.tick,
    )
    monkeypatch.setattr(
        astra_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(character_pkg, "Character", _CharacterProbe)

    return SimpleNamespace(
        logic=AstraYaoCorePassiveAtkBonus(buff_instance),
        buff_instance=buff_instance,
        buff_0=buff_0,
        record=record,
        schedule_data=sim_instance.schedule_data,
        order_log=order_log,
    )


def test_astra_core_passive_report_state_changes_after_buff_update(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_astra_core_harness(monkeypatch)

    harness.logic.special_start_logic(benifit="苍角")

    assert harness.schedule_data.change_process_calls == 1
    assert harness.order_log == ["simple_start", "update_to_buff_0", "report"]
    assert harness.buff_instance.simple_start_calls == [
        {
            "timenow": 90,
            "sub_exist_buff_dict": harness.record.sub_exist_buff_dict,
            "kwargs": {"no_count": 1, "no_end": 1},
        }
    ]
    assert harness.buff_instance.update_to_buff_0_calls == [harness.buff_0]
    assert harness.buff_instance.dy.count == 700.0
    assert harness.record.update_info_box["苍角"] == {
        "startticks": 90,
        "endticks": 1290,
        "count": 700.0,
    }


def test_astra_core_passive_same_tick_guard_is_report_state_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _build_astra_core_harness(
        monkeypatch,
        active_buff_0=True,
        same_tick_record=True,
    )

    harness.logic.special_start_logic(benifit="苍角")

    assert harness.schedule_data.change_process_calls == 0
    assert harness.order_log == []
    assert harness.buff_instance.simple_start_calls == []
    assert harness.buff_instance.update_to_buff_0_calls == []
    assert harness.record.update_info_box["苍角"] == {
        "startticks": 90,
        "endticks": 1290,
        "count": 700.0,
    }


def test_astra_core_passive_report_state_source_keeps_boundaries() -> None:
    source = inspect.getsource(AstraYaoCorePassiveAtkBonus.special_start_logic)

    assert "change_process_state()" in source
    assert source.index("simple_start") < source.index("update_to_buff_0")
    assert source.index("update_to_buff_0") < source.index("change_process_state")

    forbidden_terms = (
        "publish_scheduled",
        "create_schedule_dispatch_port",
        "broadcast_event",
        "RuntimeCommandPort",
        "create_runtime_command_port",
        "event_list",
        "find_event_list",
        "delete_buff",
        "delete",
    )
    for term in forbidden_terms:
        assert term not in source
