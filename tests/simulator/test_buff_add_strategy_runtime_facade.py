from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Iterable, SupportsIndex

from zsim.sim_progress.Buff.BuffAddStrategy import buff_add_strategy
from zsim.sim_progress.Buff.buff_class import Buff


class _BuffAddProbe(Buff):
    def __init__(
        self,
        index: str,
        *,
        operator: str = "Alice",
        add_buff_to: str = "0001",
        count: int | float = 0,
        step: int | float = 1,
        maxcount: int | float = 99,
        maxduration: int = 10,
    ) -> None:
        self.ft = SimpleNamespace(
            index=index,
            operator=operator,
            passively_updating=False,
            beneficiary=operator,
            add_buff_to=add_buff_to,
            simple_start_logic=True,
            simple_effect_logic=True,
            individual_settled=False,
            maxduration=maxduration,
            step=step,
            maxcount=maxcount,
        )
        self.dy = SimpleNamespace(
            active=False,
            ready=True,
            startticks=0,
            endticks=0,
            count=count,
            built_in_buff_box=[],
            is_changed=False,
        )
        self.history = SimpleNamespace(active_times=0)
        self.logic = SimpleNamespace(
            xstart=lambda **kwargs: None,
            xeffect=lambda: None,
        )

    def __deepcopy__(self, memo: dict[int, Any]) -> "_BuffAddProbe":
        copied = _BuffAddProbe(
            self.ft.index,
            operator=self.ft.operator,
            add_buff_to=self.ft.add_buff_to,
            count=self.dy.count,
            step=self.ft.step,
            maxcount=self.ft.maxcount,
            maxduration=self.ft.maxduration,
        )
        copied.ft.passively_updating = self.ft.passively_updating
        copied.ft.beneficiary = self.ft.beneficiary
        copied.dy.active = self.dy.active
        copied.dy.ready = self.dy.ready
        copied.dy.startticks = self.dy.startticks
        copied.dy.endticks = self.dy.endticks
        copied.dy.built_in_buff_box = list(self.dy.built_in_buff_box)
        copied.dy.is_changed = self.dy.is_changed
        copied.history.active_times = self.history.active_times
        return copied


class _FailFastPendingQueue(list[Buff]):
    def append(self, item: Buff) -> None:
        raise AssertionError("buff_add_strategy must not touch pending Buff queues")

    def extend(self, items: Iterable[Any]) -> None:
        raise AssertionError("buff_add_strategy must not touch pending Buff queues")

    def insert(self, index: SupportsIndex, item: Buff) -> None:
        raise AssertionError("buff_add_strategy must not touch pending Buff queues")

    def pop(self, index: SupportsIndex = -1) -> Buff:
        raise AssertionError("buff_add_strategy must not touch pending Buff queues")

    def clear(self) -> None:
        raise AssertionError("buff_add_strategy must not touch pending Buff queues")


class _FailFastEventList(list[object]):
    def append(self, item: object) -> None:
        raise AssertionError("buff_add_strategy must not publish scheduled events")

    def extend(self, items: Iterable[object]) -> None:
        raise AssertionError("buff_add_strategy must not publish scheduled events")

    def insert(self, index: SupportsIndex, item: object) -> None:
        raise AssertionError("buff_add_strategy must not publish scheduled events")


def _fail_listener_broadcast(*args: object, **kwargs: object) -> None:
    raise AssertionError("buff_add_strategy must not broadcast listener events")


def _make_sim_instance(
    *,
    exist_buff_dict: dict[str, dict[str, Buff]],
    loading_buff_dict: dict[str, list[Buff]],
    dynamic_buff_dict: dict[str, list[Buff]],
    enemy_debuff_mirror: list[Buff],
    tick: int = 42,
) -> Any:
    return SimpleNamespace(
        load_data=SimpleNamespace(
            all_name_order_box={"Alice": ["Alice"], "enemy": ["enemy"]},
            exist_buff_dict=exist_buff_dict,
            LOADING_BUFF_DICT=loading_buff_dict,
        ),
        global_stats=SimpleNamespace(DYNAMIC_BUFF_DICT=dynamic_buff_dict),
        schedule_data=SimpleNamespace(
            event_list=_FailFastEventList(),
            enemy=SimpleNamespace(
                dynamic=SimpleNamespace(dynamic_debuff_list=enemy_debuff_mirror)
            )
        ),
        listener_manager=SimpleNamespace(broadcast_event=_fail_listener_broadcast),
        tick=tick,
    )


def _install_recording_runtime_facade(monkeypatch: Any) -> list[tuple[str, str, object]]:
    from zsim.sim_progress.ScheduledEvent import buff_runtime

    calls: list[tuple[str, str, object]] = []

    class _RecordingLegacyBuffRuntimeFacade(buff_runtime.LegacyBuffRuntimeFacade):
        def find_active_buff_by_index(
            self, beneficiary: str, buff_index: str
        ) -> Buff | None:
            calls.append(("find_active_buff_by_index", beneficiary, buff_index))
            return super().find_active_buff_by_index(beneficiary, buff_index)

        def remove_active_buff(self, beneficiary: str, buff: Buff) -> None:
            calls.append(("remove_active_buff", beneficiary, buff))
            super().remove_active_buff(beneficiary, buff)

        def append_active_buff(self, beneficiary: str, buff: Buff) -> None:
            calls.append(("append_active_buff", beneficiary, buff))
            super().append_active_buff(beneficiary, buff)

        def sync_enemy_debuff_mirror(self, buff: Buff) -> None:
            calls.append(("sync_enemy_debuff_mirror", "enemy", buff))
            super().sync_enemy_debuff_mirror(buff)

    monkeypatch.setattr(
        buff_runtime,
        "create_legacy_buff_runtime_facade",
        lambda **kwargs: _RecordingLegacyBuffRuntimeFacade(**kwargs),
    )
    return calls


def _install_runtime_command_creation_guard(monkeypatch: Any) -> None:
    from zsim.sim_progress.ScheduledEvent import runtime_command

    def fail_create_runtime_command_port(*args: object, **kwargs: object) -> None:
        raise AssertionError("buff_add_strategy must not create RuntimeCommandPort")

    monkeypatch.setattr(
        runtime_command,
        "create_runtime_command_port",
        fail_create_runtime_command_port,
    )


def test_buff_add_strategy_replaces_active_store_through_runtime_facade(
    monkeypatch: Any,
) -> None:
    facade_calls = _install_recording_runtime_facade(monkeypatch)
    _install_runtime_command_creation_guard(monkeypatch)
    template_buff = _BuffAddProbe("forced-buff", count=1)
    old_active_buff = _BuffAddProbe("forced-buff", count=9)
    unrelated_active_buff = _BuffAddProbe("other-buff", count=2)
    other_target_active_buff = _BuffAddProbe("forced-buff", count=5)
    active_store = [old_active_buff, unrelated_active_buff]
    other_target_active_store = [other_target_active_buff]
    pending_queue: list[Buff] = _FailFastPendingQueue()
    sim_instance = _make_sim_instance(
        exist_buff_dict={"Alice": {"forced-buff": template_buff}},
        loading_buff_dict={"Alice": pending_queue, "Bob": _FailFastPendingQueue()},
        dynamic_buff_dict={"Alice": active_store, "Bob": other_target_active_store},
        enemy_debuff_mirror=[],
    )

    buff_add_strategy(
        "forced-buff",
        benifit_list=["Alice"],
        specified_count=3,
        sim_instance=sim_instance,
    )

    assert sim_instance.global_stats.DYNAMIC_BUFF_DICT["Alice"] is active_store
    assert active_store[0] is unrelated_active_buff
    assert len(active_store) == 2
    new_active_buff = active_store[1]
    assert new_active_buff is not old_active_buff
    assert new_active_buff is not template_buff
    assert old_active_buff not in active_store
    assert other_target_active_store == [other_target_active_buff]
    assert new_active_buff.ft.index == "forced-buff"
    assert new_active_buff.dy.count == 3
    assert new_active_buff.dy.startticks == 42
    assert new_active_buff.dy.endticks == 52
    assert pending_queue == []
    assert template_buff.history.active_times == 1
    assert facade_calls == [
        ("find_active_buff_by_index", "Alice", "forced-buff"),
        ("remove_active_buff", "Alice", old_active_buff),
        ("append_active_buff", "Alice", new_active_buff),
    ]


def test_buff_add_strategy_syncs_enemy_debuff_mirror_through_runtime_facade(
    monkeypatch: Any,
) -> None:
    facade_calls = _install_recording_runtime_facade(monkeypatch)
    _install_runtime_command_creation_guard(monkeypatch)
    template_debuff = _BuffAddProbe(
        "forced-debuff",
        operator="enemy",
        add_buff_to="0001",
        count=0,
    )
    old_active_debuff = _BuffAddProbe("forced-debuff", operator="enemy")
    unrelated_active_debuff = _BuffAddProbe("other-debuff", operator="enemy")
    old_mirror_debuff = _BuffAddProbe("forced-debuff", operator="enemy")
    other_mirror_debuff = _BuffAddProbe("other-debuff", operator="enemy")
    active_store = [old_active_debuff, unrelated_active_debuff]
    enemy_debuff_mirror = [old_mirror_debuff, other_mirror_debuff]
    sim_instance = _make_sim_instance(
        exist_buff_dict={"enemy": {"forced-debuff": template_debuff}},
        loading_buff_dict={"enemy": _FailFastPendingQueue()},
        dynamic_buff_dict={"enemy": active_store},
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    buff_add_strategy(
        "forced-debuff",
        benifit_list=["enemy"],
        sim_instance=sim_instance,
    )

    assert active_store[0] is unrelated_active_debuff
    assert len(active_store) == 2
    new_debuff = active_store[1]
    assert new_debuff.ft.index == "forced-debuff"
    assert new_debuff is not old_active_debuff
    assert old_active_debuff not in active_store
    assert enemy_debuff_mirror == [other_mirror_debuff, new_debuff]
    assert enemy_debuff_mirror[1] is new_debuff
    assert sim_instance.load_data.LOADING_BUFF_DICT["enemy"] == []
    assert facade_calls == [
        ("find_active_buff_by_index", "enemy", "forced-debuff"),
        ("remove_active_buff", "enemy", old_active_debuff),
        ("append_active_buff", "enemy", new_debuff),
        ("sync_enemy_debuff_mirror", "enemy", new_debuff),
    ]


def test_buff_runtime_read_port_stays_read_only_for_buff_add_strategy() -> None:
    from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort

    write_method_names = {
        "append_active_buff",
        "remove_active_buff",
        "sync_enemy_debuff_mirror",
        "enqueue_pending_buff",
        "drain_pending_buffs",
        "clear_pending_buffs",
        "activate_pending_buffs",
    }

    assert write_method_names.isdisjoint(BuffRuntimeReadPort.__dict__)
