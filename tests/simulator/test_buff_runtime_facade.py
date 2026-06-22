from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from zsim.sim_progress.Buff.BuffLoad import (
    EXIST_FILE,
    JUDGE_FILE,
    BuffInitCache,
    BuffInitialize,
    BuffJudge,
    BuffJudgeCache,
)
from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.ScheduledEvent.buff_runtime import (
    ActiveBuffStore,
    BuffTemplateRegistry,
    BuffRuntimeFacade,
    BuffRuntimeState,
    EnemyDebuffMirror,
    LegacyBuffRuntimeFacade,
    PendingBuffQueue,
    create_legacy_buff_runtime_facade,
)


class _BuffProbe(Buff):
    def __init__(
        self,
        index: str,
        *,
        active: bool = True,
        startticks: int = 1,
        endticks: int = 2,
        count: int = 1,
        alltime: bool = False,
        simple_exit_logic: bool = True,
        simple_judge_logic: bool = True,
        simple_start_logic: bool = True,
        simple_hit_logic: bool = True,
        simple_end_logic: bool = True,
        simple_effect_logic: bool = True,
        individual_settled: bool = False,
        is_debuff: bool = False,
        built_in_buff_box: list[tuple[str, int]] | None = None,
        xexit_result: bool | None = None,
        events: list[str] | None = None,
    ) -> None:
        self.ft = SimpleNamespace(
            index=index,
            alltime=alltime,
            simple_exit_logic=simple_exit_logic,
            simple_judge_logic=simple_judge_logic,
            simple_start_logic=simple_start_logic,
            simple_hit_logic=simple_hit_logic,
            simple_end_logic=simple_end_logic,
            simple_effect_logic=simple_effect_logic,
            individual_settled=individual_settled,
            is_debuff=is_debuff,
        )
        self.dy = SimpleNamespace(
            active=active,
            startticks=startticks,
            endticks=endticks,
            count=count,
            built_in_buff_box=list(built_in_buff_box or []),
        )
        self.history = SimpleNamespace()
        self.logic = SimpleNamespace(xexit=self._xexit)
        self._xexit_result = xexit_result
        self.xexit_calls: list[str] = []
        self.end_calls: list[tuple[int, dict[str, Any]]] = []
        self._events = events

    def _xexit(self, *, beneficiary: str) -> bool:
        self.xexit_calls.append(beneficiary)
        return bool(self._xexit_result)

    def end(self, timenow: int, exist_buff_dict: dict[str, Any]) -> None:
        self.end_calls.append((timenow, exist_buff_dict))
        if self._events is not None:
            self._events.append(f"end:{self.ft.index}:{timenow}")
        self.dy.active = False
        self.dy.count = 0
        self.dy.built_in_buff_box = []


class _TrackingList(list[Any]):
    def __init__(self, values: list[Any], events: list[str], label: str) -> None:
        super().__init__(values)
        self._events = events
        self._label = label

    def remove(self, value: Any) -> None:
        self._events.append(f"{self._label}.remove:{value.ft.index}")
        super().remove(value)


def _capture_update_reports(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[list[tuple[tuple[Any, ...], dict[str, Any]]], list[tuple[str, int]]]:
    from zsim.sim_progress.ScheduledEvent import buff_runtime
    from zsim.sim_progress.Update import Update_Buff

    buff_reports: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    log_reports: list[tuple[str, int]] = []

    def fake_report_buff_to_queue(*args: Any, **kwargs: Any) -> None:
        buff_reports.append((args, kwargs))

    def fake_report_to_log(message: str, *, level: int) -> None:
        log_reports.append((message, level))

    monkeypatch.setattr(Update_Buff, "report_buff_to_queue", fake_report_buff_to_queue)
    monkeypatch.setattr(buff_runtime, "report_to_log", fake_report_to_log)
    return buff_reports, log_reports


def _create_facade(
    *,
    exist_buff_dict: dict[str, dict[str, Any]] | None = None,
    loading_buff_dict: dict[str, list[Any]] | None = None,
    dynamic_buff_dict: dict[str, list[Any]] | None = None,
    enemy_debuff_mirror: list[Any] | None = None,
) -> BuffRuntimeFacade:
    return create_legacy_buff_runtime_facade(
        exist_buff_dict=exist_buff_dict if exist_buff_dict is not None else {},
        loading_buff_dict=loading_buff_dict if loading_buff_dict is not None else {},
        dynamic_buff_dict=dynamic_buff_dict if dynamic_buff_dict is not None else {},
        enemy_debuff_mirror=enemy_debuff_mirror if enemy_debuff_mirror is not None else [],
    )


def _first_loaded_buff_name() -> str:
    for index in JUDGE_FILE.index:
        if index in EXIST_FILE.index:
            return cast(str, index)
    raise AssertionError("No Buff index is shared by JUDGE_FILE and EXIST_FILE")


def test_buff_initialize_default_cache_retains_registry_identity_without_invalidation() -> None:
    default_cache = BuffInitialize.__kwdefaults__["cache"]
    assert isinstance(default_cache, BuffInitCache)

    cache = BuffInitCache()
    buff_name = _first_loaded_buff_name()
    registered_buff = _BuffProbe(buff_name)
    registry = {buff_name: registered_buff}

    result = BuffInitialize(buff_name, registry, cache=cache)
    cache_key = (buff_name, tuple(registry.items()))

    assert cache.get(cache_key) is result
    assert cache_key[1][0][1] is registered_buff

    registry.clear()
    assert cache.get(cache_key) is result


def test_buff_init_cache_keeps_first_128_entries_after_overflow() -> None:
    cache = BuffInitCache()
    keys = [(f"buff-{index}", index) for index in range(129)]

    for index, key in enumerate(keys):
        cache.add(key, index)

    assert len(cache.cache) == 128
    assert keys[0] in cache.cache
    assert keys[127] in cache.cache
    assert keys[128] not in cache.cache


def test_buff_judge_default_cache_is_identity_keyed_without_lifecycle_invalidation() -> None:
    default_cache = BuffJudge.__kwdefaults__["cache"]
    assert isinstance(default_cache, BuffJudgeCache)

    cache = BuffJudgeCache()
    buff = _BuffProbe("identity-cache", alltime=True)
    mission = SimpleNamespace()
    judge_conditions: dict[str, Any] = {}

    assert BuffJudge(buff, judge_conditions, cast(Any, mission), cache=cache) is True
    expected_key = hash((id(buff), tuple(judge_conditions.items()), id(mission)))
    assert cache.cache == {expected_key: True}

    buff.ft.alltime = False
    assert BuffJudge(buff, judge_conditions, cast(Any, mission), cache=cache) is True
    assert BuffJudge(buff, judge_conditions, cast(Any, SimpleNamespace()), cache=cache) is False


def test_legacy_buff_runtime_facade_preserves_old_container_identity() -> None:
    registered_buff = _BuffProbe("registered")
    pending_buff = _BuffProbe("pending")
    active_buff = _BuffProbe("active")
    enemy_debuff = _BuffProbe("enemy-debuff")
    exist_buff_dict: dict[str, dict[str, Any]] = {
        "alpha": {"registered": registered_buff},
        "enemy": {},
    }
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [], "enemy": []}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [], "enemy": []}
    enemy_debuff_mirror: list[Any] = [enemy_debuff]

    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    assert isinstance(facade, LegacyBuffRuntimeFacade)
    assert facade.get_registered_buff("alpha", "registered") is registered_buff
    assert facade.get_pending_queue_for_compat("alpha") is loading_buff_dict["alpha"]
    assert facade.get_active_buffs_for_compat("alpha") is dynamic_buff_dict["alpha"]
    assert facade.get_enemy_debuff_mirror_for_compat() is enemy_debuff_mirror
    assert dynamic_buff_dict["enemy"] is enemy_debuff_mirror

    facade.enqueue_pending_buff("alpha", pending_buff)
    facade.append_active_buff("alpha", active_buff)

    assert loading_buff_dict["alpha"] == [pending_buff]
    assert dynamic_buff_dict["alpha"] == [active_buff]
    assert enemy_debuff_mirror == [enemy_debuff]


def test_buff_runtime_state_exposes_active_store_owner_with_compat_identity() -> None:
    active_buff = _BuffProbe("active")
    replacement = _BuffProbe("replacement")
    active_store: dict[str, list[Any]] = {"alpha": [active_buff], "enemy": []}
    pending_queue: dict[str, list[Any]] = {"alpha": [], "enemy": []}
    enemy_mirror: list[Any] = []

    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue=pending_queue,
        active_store=active_store,
        enemy_mirror=enemy_mirror,
    )

    active_owner = runtime_state.active_store_owner()

    assert isinstance(active_owner, ActiveBuffStore)
    assert active_owner.as_compat_dict() is active_store
    assert runtime_state.active_store_for_compat() is active_store
    assert active_owner.active_buffs_for_compat("alpha") is active_store["alpha"]
    assert active_owner.find_by_index("alpha", "active") is active_buff

    active_owner.append("alpha", replacement)
    active_owner.remove("alpha", active_buff)

    assert active_store["alpha"] == [replacement]
    assert active_owner.find_by_index("alpha", "active") is None
    assert active_owner.find_by_index("alpha", "replacement") is replacement
    assert active_owner.count() == 1
    assert active_owner.ensure_beneficiary("beta") is active_store["beta"]
    assert active_owner.beneficiaries() == ("alpha", "enemy", "beta")


def test_buff_runtime_state_exposes_template_registry_owner_with_compat_identity() -> None:
    registered_buff = _BuffProbe("registered")
    replacement_buff = _BuffProbe("replacement")
    registry: dict[str, dict[str, Any]] = {
        "alpha": {"registered": registered_buff},
        "enemy": {},
    }
    runtime_state = BuffRuntimeState(
        template_registry=registry,
        pending_queue={"alpha": [], "enemy": []},
        active_store={"alpha": [], "enemy": []},
        enemy_mirror=[],
    )

    template_owner = runtime_state.template_registry_owner()

    assert isinstance(template_owner, BuffTemplateRegistry)
    assert template_owner.as_compat_dict() is registry
    assert runtime_state.template_registry_for_compat() is registry
    assert template_owner.for_owner("alpha") is registry["alpha"]
    assert template_owner.get_registered_buff("alpha", "registered") is registered_buff

    owner_snapshot = template_owner.owner_snapshot("alpha")
    registry_snapshot = template_owner.registry_snapshot()
    registry["alpha"]["replacement"] = replacement_buff

    assert dict(owner_snapshot) == {"registered": registered_buff}
    assert dict(registry_snapshot["alpha"]) == {"registered": registered_buff}
    with pytest.raises(TypeError):
        cast(Any, owner_snapshot)["mutated"] = replacement_buff
    with pytest.raises(TypeError):
        cast(Any, registry_snapshot)["bravo"] = {}


def test_buff_runtime_read_port_reads_active_view_through_active_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active_buff = _BuffProbe("active")
    enemy_buff = _BuffProbe("enemy", is_debuff=True)
    active_store: dict[str, list[Any]] = {
        "alpha": [active_buff],
        "enemy": [enemy_buff],
    }
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue={"alpha": [], "enemy": []},
        active_store=active_store,
        enemy_mirror=active_store["enemy"],
    )
    active_owner = runtime_state.active_store_owner()
    read_port = runtime_state.create_read_port()
    calls: list[tuple[str, str | None]] = []
    original_active_buffs_snapshot = active_owner.active_buffs_snapshot
    original_active_buff_view_snapshot = active_owner.active_buff_view_snapshot

    def recording_active_buffs_snapshot(beneficiary: str) -> tuple[Any, ...]:
        calls.append(("single", beneficiary))
        return original_active_buffs_snapshot(beneficiary)

    def recording_active_buff_view_snapshot() -> Any:
        calls.append(("view", None))
        return original_active_buff_view_snapshot()

    def fail_compat_access() -> dict[str, list[Any]]:
        raise AssertionError("read port must read active view through ActiveBuffStore")

    monkeypatch.setattr(
        active_owner,
        "active_buffs_snapshot",
        recording_active_buffs_snapshot,
    )
    monkeypatch.setattr(
        active_owner,
        "active_buff_view_snapshot",
        recording_active_buff_view_snapshot,
    )
    monkeypatch.setattr(runtime_state, "active_store_for_compat", fail_compat_access)

    assert read_port.get_active_buffs("alpha") == (active_buff,)
    assert read_port.get_active_buffs("missing") == ()
    active_view = read_port.get_active_buff_view()
    assert active_view["alpha"] == (active_buff,)
    assert active_view["enemy"] == (enemy_buff,)
    with pytest.raises(TypeError):
        cast(Any, active_view)["alpha"] = ()
    assert calls == [
        ("single", "alpha"),
        ("single", "missing"),
        ("view", None),
    ]


def test_buff_runtime_read_ports_do_not_retain_stale_active_store_between_states() -> None:
    first_buff = _BuffProbe("first")
    second_buff = _BuffProbe("second")
    first_late_buff = _BuffProbe("first-late")
    second_late_buff = _BuffProbe("second-late")
    first_store: dict[str, list[Any]] = {"alpha": [first_buff], "enemy": []}
    second_store: dict[str, list[Any]] = {"alpha": [second_buff], "enemy": []}

    first_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue={"alpha": [], "enemy": []},
        active_store=first_store,
        enemy_mirror=first_store["enemy"],
    )
    second_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue={"alpha": [], "enemy": []},
        active_store=second_store,
        enemy_mirror=second_store["enemy"],
    )
    first_read_port = first_state.create_read_port()
    second_read_port = second_state.create_read_port()

    first_state.active_store_owner().append("alpha", first_late_buff)
    second_state.active_store_owner().append("alpha", second_late_buff)

    assert first_read_port.get_active_buffs("alpha") == (
        first_buff,
        first_late_buff,
    )
    assert second_read_port.get_active_buffs("alpha") == (
        second_buff,
        second_late_buff,
    )
    assert first_read_port.get_active_buff_view()["alpha"] == (
        first_buff,
        first_late_buff,
    )
    assert second_read_port.get_active_buff_view()["alpha"] == (
        second_buff,
        second_late_buff,
    )


def test_buff_runtime_read_ports_do_not_retain_stale_template_registry_between_states() -> None:
    first_buff = _BuffProbe("first-template")
    second_buff = _BuffProbe("second-template")
    first_late_buff = _BuffProbe("first-late-template")
    second_late_buff = _BuffProbe("second-late-template")
    first_registry: dict[str, dict[str, Any]] = {
        "alpha": {"first-template": first_buff},
        "enemy": {},
    }
    second_registry: dict[str, dict[str, Any]] = {
        "alpha": {"second-template": second_buff},
        "enemy": {},
    }
    first_state = BuffRuntimeState(
        template_registry=first_registry,
        pending_queue={"alpha": [], "enemy": []},
        active_store={"alpha": [], "enemy": []},
        enemy_mirror=[],
    )
    second_state = BuffRuntimeState(
        template_registry=second_registry,
        pending_queue={"alpha": [], "enemy": []},
        active_store={"alpha": [], "enemy": []},
        enemy_mirror=[],
    )
    first_read_port = first_state.create_read_port()
    second_read_port = second_state.create_read_port()

    first_registry["alpha"]["first-late-template"] = first_late_buff
    second_registry["alpha"]["second-late-template"] = second_late_buff

    assert dict(first_read_port.get_exist_buff_snapshot("alpha")) == {
        "first-template": first_buff,
        "first-late-template": first_late_buff,
    }
    assert dict(second_read_port.get_exist_buff_snapshot("alpha")) == {
        "second-template": second_buff,
        "second-late-template": second_late_buff,
    }
    assert dict(first_read_port.get_exist_buff_snapshot_view()["alpha"]) == {
        "first-template": first_buff,
        "first-late-template": first_late_buff,
    }
    assert dict(second_read_port.get_exist_buff_snapshot_view()["alpha"]) == {
        "second-template": second_buff,
        "second-late-template": second_late_buff,
    }
    with pytest.raises(TypeError):
        cast(Any, first_read_port.get_exist_buff_snapshot("alpha"))[
            "mutated"
        ] = first_late_buff


def test_buff_runtime_state_exposes_enemy_mirror_owner_with_active_identity() -> None:
    active_debuff = _BuffProbe("debuff", is_debuff=True)
    replacement_debuff = _BuffProbe("debuff", is_debuff=True)
    other_debuff = _BuffProbe("other", is_debuff=True)
    dynamic_buff_dict: dict[str, list[Any]] = {"enemy": [active_debuff, other_debuff]}
    enemy_debuff_mirror: list[Any] = []
    runtime_state = BuffRuntimeState(
        template_registry={"enemy": {}},
        pending_queue={"enemy": []},
        active_store=dynamic_buff_dict,
        enemy_mirror=enemy_debuff_mirror,
    )

    active_owner = runtime_state.active_store_owner()
    mirror_owner = runtime_state.enemy_mirror_owner()

    assert isinstance(mirror_owner, EnemyDebuffMirror)
    assert mirror_owner.as_compat_list() is enemy_debuff_mirror
    assert runtime_state.enemy_mirror_for_compat() is enemy_debuff_mirror
    assert active_owner.active_buffs_for_compat("enemy") is enemy_debuff_mirror
    assert dynamic_buff_dict["enemy"] is enemy_debuff_mirror
    assert mirror_owner.find_by_index("debuff") is active_debuff

    mirror_owner.sync(replacement_debuff)
    assert enemy_debuff_mirror == [other_debuff, replacement_debuff]
    assert active_owner.active_buffs_for_compat("enemy") == [
        other_debuff,
        replacement_debuff,
    ]

    mirror_owner.remove(replacement_debuff)
    assert enemy_debuff_mirror == [other_debuff]
    assert active_owner.find_by_index("enemy", "debuff") is None


def test_legacy_facade_active_helpers_route_through_active_store_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    active_buff = _BuffProbe("active")
    replacement = _BuffProbe("replacement")
    active_store: dict[str, list[Any]] = {"alpha": [active_buff], "enemy": []}
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue={"alpha": [], "enemy": []},
        active_store=active_store,
        enemy_mirror=active_store["enemy"],
    )
    active_owner = runtime_state.active_store_owner()
    facade = runtime_state.create_facade()
    calls: list[tuple[str, str, str | None]] = []

    def fake_append(beneficiary: str, buff: Any) -> None:
        calls.append(("append", beneficiary, buff.ft.index))
        active_store[beneficiary].append(buff)

    def fake_remove(beneficiary: str, buff: Any) -> None:
        calls.append(("remove", beneficiary, buff.ft.index))
        active_store[beneficiary].remove(buff)

    def fake_find_by_index(beneficiary: str, buff_index: str) -> Any:
        calls.append(("find", beneficiary, buff_index))
        return replacement

    def fake_active_buffs_for_compat(beneficiary: str) -> list[Any]:
        calls.append(("compat", beneficiary, None))
        return active_store[beneficiary]

    monkeypatch.setattr(active_owner, "append", fake_append)
    monkeypatch.setattr(active_owner, "remove", fake_remove)
    monkeypatch.setattr(active_owner, "find_by_index", fake_find_by_index)
    monkeypatch.setattr(
        active_owner,
        "active_buffs_for_compat",
        fake_active_buffs_for_compat,
    )

    facade.append_active_buff("alpha", replacement)
    facade.remove_active_buff("alpha", active_buff)

    assert facade.find_active_buff_by_index("alpha", "replacement") is replacement
    assert facade.get_active_buffs_for_compat("alpha") == [replacement]
    assert calls == [
        ("append", "alpha", "replacement"),
        ("remove", "alpha", "active"),
        ("find", "alpha", "replacement"),
        ("compat", "alpha", None),
    ]


def test_legacy_buff_runtime_facade_keeps_pending_and_active_store_semantics_separate() -> None:
    first_pending = _BuffProbe("first-pending")
    second_pending = _BuffProbe("second-pending")
    active_buff = _BuffProbe("active")
    replacement = _BuffProbe("active")
    loading_buff_dict: dict[str, list[Any]] = {
        "alpha": [first_pending, second_pending],
        "enemy": [],
    }
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [active_buff], "enemy": []}
    enemy_pending_list = loading_buff_dict["enemy"]
    enemy_active_list = dynamic_buff_dict["enemy"]
    before_loading_keys = set(loading_buff_dict)
    before_dynamic_keys = set(dynamic_buff_dict)
    facade = _create_facade(
        exist_buff_dict={"alpha": {}, "enemy": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=enemy_active_list,
    )

    drained = facade.drain_pending_buffs("alpha")
    facade.append_active_buff("alpha", replacement)
    facade.remove_active_buff("alpha", active_buff)

    assert drained == [second_pending, first_pending]
    assert loading_buff_dict["alpha"] == []
    assert dynamic_buff_dict["alpha"] == [replacement]
    assert facade.find_active_buff_by_index("alpha", "active") is replacement
    assert set(loading_buff_dict) == before_loading_keys
    assert set(dynamic_buff_dict) == before_dynamic_keys
    assert loading_buff_dict["enemy"] is enemy_pending_list
    assert dynamic_buff_dict["enemy"] is enemy_active_list

    with pytest.raises(KeyError):
        facade.enqueue_pending_buff("missing", _BuffProbe("missing"))
    assert set(loading_buff_dict) == before_loading_keys
    assert set(dynamic_buff_dict) == before_dynamic_keys


def test_legacy_buff_runtime_facade_syncs_enemy_debuff_mirror_by_index(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    old_debuff = _BuffProbe("debuff")
    other_debuff = _BuffProbe("other")
    replacement_debuff = _BuffProbe("debuff")
    enemy_debuff_mirror: list[Any] = [old_debuff, other_debuff]
    dynamic_buff_dict: dict[str, list[Any]] = {"enemy": []}
    runtime_state = BuffRuntimeState(
        template_registry={"enemy": {}},
        pending_queue={"enemy": []},
        active_store=dynamic_buff_dict,
        enemy_mirror=enemy_debuff_mirror,
    )
    mirror_owner = runtime_state.enemy_mirror_owner()
    facade = runtime_state.create_facade()
    calls: list[tuple[str, str]] = []
    original_sync = mirror_owner.sync
    original_remove = mirror_owner.remove

    def recording_sync(buff: Any) -> None:
        calls.append(("sync", buff.ft.index))
        original_sync(buff)

    def recording_remove(buff: Any) -> None:
        calls.append(("remove", buff.ft.index))
        original_remove(buff)

    def fail_compat_access() -> list[Any]:
        raise AssertionError("facade mirror writes must use EnemyDebuffMirror")

    monkeypatch.setattr(mirror_owner, "sync", recording_sync)
    monkeypatch.setattr(mirror_owner, "remove", recording_remove)
    monkeypatch.setattr(runtime_state, "enemy_mirror_for_compat", fail_compat_access)

    facade.sync_enemy_debuff_mirror(replacement_debuff)
    assert enemy_debuff_mirror == [other_debuff, replacement_debuff]
    assert facade.get_active_buffs_for_compat("enemy") is enemy_debuff_mirror

    facade.remove_enemy_debuff_mirror(replacement_debuff)
    assert enemy_debuff_mirror == [other_debuff]
    assert calls == [
        ("sync", "debuff"),
        ("remove", "debuff"),
    ]


def test_buff_runtime_state_collapses_enemy_active_store_into_dynamic_debuff_list() -> None:
    active_debuff = _BuffProbe("active-debuff", is_debuff=True)
    stale_mirror_debuff = _BuffProbe("stale-debuff", is_debuff=True)
    dynamic_buff_dict: dict[str, list[Any]] = {"enemy": [active_debuff]}
    enemy_debuff_mirror: list[Any] = [stale_mirror_debuff]

    runtime_state = BuffRuntimeState(
        template_registry={"enemy": {}},
        pending_queue={"enemy": []},
        active_store=dynamic_buff_dict,
        enemy_mirror=enemy_debuff_mirror,
    )

    assert dynamic_buff_dict["enemy"] is enemy_debuff_mirror
    assert runtime_state.active_store_for_compat()["enemy"] is enemy_debuff_mirror
    assert runtime_state.enemy_mirror_for_compat() is enemy_debuff_mirror
    assert enemy_debuff_mirror == [active_debuff]


def test_legacy_buff_runtime_facade_registry_view_is_read_only_snapshot() -> None:
    registered_buff = _BuffProbe("registered")
    exist_buff_dict: dict[str, dict[str, Any]] = {
        "alpha": {"registered": registered_buff},
    }
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict={"alpha": []},
        dynamic_buff_dict={"alpha": []},
        enemy_debuff_mirror=[],
    )

    registered_view = facade.get_registered_buff_view("alpha")
    exist_buff_dict["alpha"]["new"] = _BuffProbe("new")

    assert dict(registered_view) == {"registered": registered_buff}
    with pytest.raises(TypeError):
        cast(Any, registered_view)["another"] = _BuffProbe("another")


def test_legacy_buff_runtime_facade_registry_reads_use_template_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registered_buff = _BuffProbe("registered")
    other_buff = _BuffProbe("other")
    registry: dict[str, dict[str, Any]] = {
        "alpha": {"registered": registered_buff},
        "bravo": {"other": other_buff},
    }
    runtime_state = BuffRuntimeState(
        template_registry=registry,
        pending_queue={"alpha": [], "bravo": []},
        active_store={"alpha": [], "bravo": []},
        enemy_mirror=[],
    )
    template_owner = runtime_state.template_registry_owner()
    calls: list[tuple[str, str | None, str | None]] = []
    original_get_registered_buff = template_owner.get_registered_buff
    original_owner_snapshot = template_owner.owner_snapshot
    original_items = template_owner.items

    def recording_get_registered_buff(owner: str, buff_index: str) -> Any:
        calls.append(("get", owner, buff_index))
        return original_get_registered_buff(owner, buff_index)

    def recording_owner_snapshot(owner: str) -> Any:
        calls.append(("snapshot", owner, None))
        return original_owner_snapshot(owner)

    def recording_items() -> Any:
        calls.append(("items", None, None))
        return original_items()

    def fail_compat_access() -> dict[str, dict[str, Any]]:
        raise AssertionError("facade registry reads must use BuffTemplateRegistry")

    monkeypatch.setattr(
        template_owner,
        "get_registered_buff",
        recording_get_registered_buff,
    )
    monkeypatch.setattr(template_owner, "owner_snapshot", recording_owner_snapshot)
    monkeypatch.setattr(template_owner, "items", recording_items)
    monkeypatch.setattr(runtime_state, "template_registry_for_compat", fail_compat_access)
    facade = runtime_state.create_facade()

    assert facade.get_registered_buff("alpha", "registered") is registered_buff
    assert dict(facade.get_registered_buff_view("alpha")) == {
        "registered": registered_buff
    }
    assert facade.find_registered_buff_source("other") == ("bravo", other_buff)
    assert calls == [
        ("get", "alpha", "registered"),
        ("snapshot", "alpha", None),
        ("items", None, None),
    ]


def test_legacy_buff_runtime_facade_tick_sweep_uses_wrapped_legacy_containers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    loading_buff_dict: dict[str, list[Any]] = {"alpha": []}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": []}
    enemy = SimpleNamespace()
    calls: list[tuple[int, Any, BuffRuntimeFacade]] = []

    def fake_update_time_related_effect(
        *,
        timetick: int,
        enemy: Any,
        runtime_facade: BuffRuntimeFacade | None = None,
    ) -> dict[str, list[Any]]:
        assert runtime_facade is not None
        calls.append((timetick, enemy, runtime_facade))
        return dynamic_buff_dict

    monkeypatch.setattr(
        Update_Buff,
        "update_time_related_effect",
        fake_update_time_related_effect,
    )
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    result = facade.update_time_related_effects(tick=77, enemy=cast(Any, enemy))

    assert result is dynamic_buff_dict
    assert calls == [(77, enemy, facade)]


def test_sweep_active_buffs_iterates_active_store_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    buff_reports, log_reports = _capture_update_reports(monkeypatch)
    active = _BuffProbe("active", endticks=10)
    alltime = _BuffProbe("alltime", alltime=True, endticks=1)
    active_store: dict[str, list[Any]] = {"alpha": [active, alltime], "enemy": []}
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue={"alpha": [], "enemy": []},
        active_store=active_store,
        enemy_mirror=active_store["enemy"],
    )
    active_owner = runtime_state.active_store_owner()
    facade = runtime_state.create_facade()
    iter_calls: list[str] = []
    original_items = active_owner.items

    def recording_items() -> Any:
        iter_calls.append("items")
        return original_items()

    def fail_compat_access() -> dict[str, list[Any]]:
        raise AssertionError("sweep_active_buffs must iterate through ActiveBuffStore")

    monkeypatch.setattr(active_owner, "items", recording_items)
    monkeypatch.setattr(runtime_state, "active_store_for_compat", fail_compat_access)

    result = facade.sweep_active_buffs(tick=5)

    assert result is active_store
    assert iter_calls == ["items"]
    assert active_store["alpha"] == [active, alltime]
    assert buff_reports == [
        (("alpha", 5, "active", 1, True), {"level": 4}),
        (("alpha", 5, "alltime", 1, True), {"level": 4}),
    ]
    assert log_reports == []


def test_end_active_buff_removes_through_active_store_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, log_reports = _capture_update_reports(monkeypatch)
    events: list[str] = []
    expired = _BuffProbe("expired", endticks=5, events=events)
    active_store: dict[str, list[Any]] = {"alpha": [expired], "enemy": []}
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {"expired": _BuffProbe("expired")}, "enemy": {}},
        pending_queue={"alpha": [], "enemy": []},
        active_store=active_store,
        enemy_mirror=active_store["enemy"],
    )
    active_owner = runtime_state.active_store_owner()
    facade = runtime_state.create_facade()
    remove_calls: list[tuple[str, str]] = []
    original_remove = active_owner.remove

    def recording_remove(beneficiary: str, buff: Any) -> None:
        remove_calls.append((beneficiary, buff.ft.index))
        original_remove(beneficiary, buff)

    monkeypatch.setattr(active_owner, "remove", recording_remove)

    facade.end_active_buff("alpha", expired, tick=6)

    assert remove_calls == [("alpha", "expired")]
    assert active_store["alpha"] == []
    assert expired.end_calls == [(6, runtime_state.template_registry_for_compat()["alpha"])]
    assert events == ["end:expired:6"]
    assert log_reports == [
        ("[Buff END]:6:alpha 的 expired 结束，已从动态列表移除", 4),
    ]


def test_update_buff_expired_simple_buff_uses_facade_active_removal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    _, log_reports = _capture_update_reports(monkeypatch)
    events: list[str] = []
    expired = _BuffProbe("expired", endticks=5, events=events)
    active_buffs = _TrackingList([expired], events, "active")
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {"expired": _BuffProbe("expired")}}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": active_buffs}
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict={"alpha": []},
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    Update_Buff.update_buff(
        6,
        runtime_facade=facade,
    )

    assert expired.end_calls == [(6, exist_buff_dict["alpha"])]
    assert active_buffs == []
    assert events == ["end:expired:6", "active.remove:expired"]
    assert log_reports == [
        ("[Buff END]:6:alpha 的 expired 结束，已从动态列表移除", 4),
    ]


def test_update_buff_reports_non_expired_and_alltime_buffs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    buff_reports, log_reports = _capture_update_reports(monkeypatch)
    active = _BuffProbe("active", endticks=10)
    alltime = _BuffProbe("alltime", alltime=True, endticks=1)
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [active, alltime]}
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict={"alpha": []},
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    Update_Buff.update_buff(
        5,
        runtime_facade=facade,
    )

    assert dynamic_buff_dict["alpha"] == [active, alltime]
    assert buff_reports == [
        (("alpha", 5, "active", 1, True), {"level": 4}),
        (("alpha", 5, "alltime", 1, True), {"level": 4}),
    ]
    assert log_reports == []


def test_update_buff_preserves_individual_settled_stack_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    buff_reports, log_reports = _capture_update_reports(monkeypatch)
    stacked = _BuffProbe(
        "stacked",
        count=2,
        individual_settled=True,
        built_in_buff_box=[("expired", 4), ("live", 8)],
    )
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [stacked]}
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict={"alpha": []},
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )
    settle_calls: list[tuple[Any, int]] = []
    original_settle = facade.settle_individual_buff_stack

    def recording_settle(buff: Any, *, tick: int) -> None:
        settle_calls.append((buff, tick))
        original_settle(buff, tick=tick)

    monkeypatch.setattr(facade, "settle_individual_buff_stack", recording_settle)

    Update_Buff.update_buff(
        5,
        runtime_facade=facade,
    )

    assert settle_calls == [(stacked, 5)]
    assert dynamic_buff_dict["alpha"] == [stacked]
    assert stacked.dy.built_in_buff_box == [("live", 8)]
    assert stacked.dy.count == 1
    assert buff_reports == [(("alpha", 5, "stacked", 1, True), {"level": 4})]
    assert log_reports == []


def test_update_buff_preserves_complex_xexit_true_and_false_branches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    buff_reports, log_reports = _capture_update_reports(monkeypatch)
    events: list[str] = []
    stay = _BuffProbe("stay", simple_exit_logic=False, xexit_result=False)
    leave = _BuffProbe("leave", simple_exit_logic=False, xexit_result=True, events=events)
    active_buffs = _TrackingList([stay, leave], events, "active")
    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {"leave": _BuffProbe("leave")}}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": active_buffs}
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict={"alpha": []},
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    Update_Buff.update_buff(
        9,
        runtime_facade=facade,
    )

    assert stay.xexit_calls == ["alpha"]
    assert leave.xexit_calls == ["alpha"]
    assert active_buffs == [stay]
    assert leave.end_calls == [(9, exist_buff_dict["alpha"])]
    assert buff_reports == [(("alpha", 9, "stay", 1, True), {"level": 4})]
    assert log_reports == [
        ("[Buff END]:9:alpha 的 leave 结束，已从动态列表移除", 4),
    ]


def test_update_buff_removes_enemy_debuff_mirror_through_facade(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    _, log_reports = _capture_update_reports(monkeypatch)
    events: list[str] = []
    expired_debuff = _BuffProbe("debuff", endticks=2, is_debuff=True, events=events)
    other_debuff = _BuffProbe("other", endticks=10, is_debuff=True)
    active_buffs = _TrackingList([expired_debuff, other_debuff], events, "active-source")
    enemy_debuff_mirror = _TrackingList([], events, "mirror")
    exist_buff_dict: dict[str, dict[str, Any]] = {"enemy": {"debuff": _BuffProbe("debuff")}}
    dynamic_buff_dict: dict[str, list[Any]] = {"enemy": active_buffs}
    facade = _create_facade(
        exist_buff_dict=exist_buff_dict,
        loading_buff_dict={"enemy": []},
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    Update_Buff.update_buff(
        3,
        runtime_facade=facade,
    )

    assert dynamic_buff_dict["enemy"] is enemy_debuff_mirror
    assert active_buffs == [expired_debuff, other_debuff]
    assert enemy_debuff_mirror == [other_debuff]
    assert events == ["end:debuff:3", "mirror.remove:debuff"]
    assert log_reports == [
        ("[Buff END]:3:enemy 的 debuff 结束，已从动态列表移除", 4),
    ]


def test_legacy_buff_runtime_facade_activates_pending_buffs_in_old_pop_order() -> None:
    first_pending = _BuffProbe("first")
    second_pending = _BuffProbe("second")
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [first_pending, second_pending]}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": []}
    facade = _create_facade(
        exist_buff_dict={"alpha": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    result = facade.activate_pending_buffs(timenow=10)

    assert result is dynamic_buff_dict
    assert loading_buff_dict["alpha"] == []
    assert dynamic_buff_dict["alpha"] == [second_pending, first_pending]


def test_legacy_buff_runtime_facade_activation_drains_pending_owner() -> None:
    class TrackingPendingBuffQueue(PendingBuffQueue):
        def __init__(self, queues: dict[str, list[Any]]) -> None:
            super().__init__(queues)
            self.beneficiary_calls = 0
            self.drain_calls: list[str] = []

        def beneficiaries(self) -> tuple[str, ...]:
            self.beneficiary_calls += 1
            return super().beneficiaries()

        def drain(self, beneficiary: str) -> list[Any]:
            self.drain_calls.append(beneficiary)
            return super().drain(beneficiary)

    first_pending = _BuffProbe("first")
    second_pending = _BuffProbe("second")
    loading_buff_dict: dict[str, list[Any]] = {
        "alpha": [first_pending],
        "bravo": [second_pending],
    }
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [], "bravo": []}
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "bravo": {}},
        pending_queue=loading_buff_dict,
        active_store=dynamic_buff_dict,
        enemy_mirror=[],
    )
    pending_owner = TrackingPendingBuffQueue(loading_buff_dict)
    runtime_state._pending_queue = pending_owner
    facade = runtime_state.create_facade()

    result = facade.activate_pending_buffs(timenow=10)

    assert result is dynamic_buff_dict
    assert pending_owner.beneficiary_calls == 1
    assert pending_owner.drain_calls == ["alpha", "bravo"]
    assert loading_buff_dict == {"alpha": [], "bravo": []}
    assert dynamic_buff_dict == {
        "alpha": [first_pending],
        "bravo": [second_pending],
        "enemy": [],
    }


def test_legacy_buff_runtime_facade_activation_uses_active_owner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_buff = _BuffProbe("same")
    replacement_buff = _BuffProbe("same")
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [replacement_buff], "enemy": []}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [existing_buff], "enemy": []}
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue=loading_buff_dict,
        active_store=dynamic_buff_dict,
        enemy_mirror=dynamic_buff_dict["enemy"],
    )
    active_owner = runtime_state.active_store_owner()
    facade = runtime_state.create_facade()
    calls: list[tuple[str, str | None, str | None]] = []
    original_find_by_index = active_owner.find_by_index
    original_remove = active_owner.remove
    original_append = active_owner.append
    original_as_compat_dict = active_owner.as_compat_dict

    def recording_find_by_index(beneficiary: str, buff_index: str) -> Any:
        calls.append(("find", beneficiary, buff_index))
        return original_find_by_index(beneficiary, buff_index)

    def recording_remove(beneficiary: str, buff: Any) -> None:
        calls.append(("remove", beneficiary, buff.ft.index))
        original_remove(beneficiary, buff)

    def recording_append(beneficiary: str, buff: Any) -> None:
        calls.append(("append", beneficiary, buff.ft.index))
        original_append(beneficiary, buff)

    def recording_as_compat_dict() -> dict[str, list[Any]]:
        calls.append(("result", None, None))
        return original_as_compat_dict()

    def fail_compat_access() -> dict[str, list[Any]]:
        raise AssertionError("activation must return through ActiveBuffStore")

    monkeypatch.setattr(active_owner, "find_by_index", recording_find_by_index)
    monkeypatch.setattr(active_owner, "remove", recording_remove)
    monkeypatch.setattr(active_owner, "append", recording_append)
    monkeypatch.setattr(active_owner, "as_compat_dict", recording_as_compat_dict)
    monkeypatch.setattr(runtime_state, "active_store_for_compat", fail_compat_access)

    result = facade.activate_pending_buffs(timenow=10)

    assert result is dynamic_buff_dict
    assert loading_buff_dict == {"alpha": [], "enemy": []}
    assert dynamic_buff_dict["alpha"] == [replacement_buff]
    assert calls == [
        ("find", "alpha", "same"),
        ("remove", "alpha", "same"),
        ("append", "alpha", "same"),
        ("result", None, None),
    ]


def test_activation_drains_pending_and_writes_active_owner_on_same_runtime_state() -> None:
    pending_buff = _BuffProbe("pending")
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [pending_buff], "enemy": []}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [], "enemy": []}
    runtime_state = BuffRuntimeState(
        template_registry={"alpha": {}, "enemy": {}},
        pending_queue=loading_buff_dict,
        active_store=dynamic_buff_dict,
        enemy_mirror=dynamic_buff_dict["enemy"],
    )
    pending_owner = runtime_state.pending_queue_owner()
    active_owner = runtime_state.active_store_owner()
    facade = runtime_state.create_facade()

    assert pending_owner.as_compat_dict() is loading_buff_dict
    assert active_owner.as_compat_dict() is dynamic_buff_dict

    result = facade.activate_pending_buffs(timenow=10)

    assert result is active_owner.as_compat_dict()
    assert pending_owner.as_compat_dict() == {"alpha": [], "enemy": []}
    assert active_owner.active_buffs_for_compat("alpha") == [pending_buff]


def test_legacy_buff_runtime_facade_skips_invalid_pending_buffs() -> None:
    inactive = _BuffProbe("inactive", active=False)
    zero_ticks = _BuffProbe("zero-ticks", startticks=0, endticks=0)
    zero_count = _BuffProbe("zero-count", count=0)
    valid = _BuffProbe("valid")
    loading_buff_dict: dict[str, list[Any]] = {
        "alpha": [inactive, zero_ticks, zero_count, valid],
    }
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": []}
    facade = _create_facade(
        exist_buff_dict={"alpha": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    facade.activate_pending_buffs(timenow=10)

    assert loading_buff_dict["alpha"] == []
    assert dynamic_buff_dict["alpha"] == [valid]


def test_legacy_buff_runtime_facade_replaces_non_alltime_active_buff_by_index() -> None:
    existing_buff = _BuffProbe("same")
    replacement_buff = _BuffProbe("same")
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [replacement_buff]}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [existing_buff]}
    facade = _create_facade(
        exist_buff_dict={"alpha": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    facade.activate_pending_buffs(timenow=10)

    assert loading_buff_dict["alpha"] == []
    assert dynamic_buff_dict["alpha"] == [replacement_buff]


def test_legacy_buff_runtime_facade_skips_alltime_duplicate_without_removing_existing() -> None:
    existing_buff = _BuffProbe("same")
    alltime_duplicate = _BuffProbe("same", alltime=True)
    loading_buff_dict: dict[str, list[Any]] = {"alpha": [alltime_duplicate]}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": [existing_buff]}
    facade = _create_facade(
        exist_buff_dict={"alpha": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=[],
    )

    facade.activate_pending_buffs(timenow=10)

    assert loading_buff_dict["alpha"] == []
    assert dynamic_buff_dict["alpha"] == [existing_buff]


def test_legacy_buff_runtime_facade_replaces_enemy_debuff_mirror_on_activation() -> None:
    old_enemy_buff = _BuffProbe("enemy-buff")
    other_enemy_buff = _BuffProbe("other")
    replacement_enemy_buff = _BuffProbe("enemy-buff")
    loading_buff_dict: dict[str, list[Any]] = {"enemy": [replacement_enemy_buff]}
    dynamic_buff_dict: dict[str, list[Any]] = {"enemy": [old_enemy_buff, other_enemy_buff]}
    enemy_debuff_mirror: list[Any] = []
    facade = _create_facade(
        exist_buff_dict={"enemy": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    facade.activate_pending_buffs(timenow=10)

    assert loading_buff_dict["enemy"] == []
    assert dynamic_buff_dict["enemy"] is enemy_debuff_mirror
    assert dynamic_buff_dict["enemy"] == [other_enemy_buff, replacement_enemy_buff]
    assert enemy_debuff_mirror == [other_enemy_buff, replacement_enemy_buff]
