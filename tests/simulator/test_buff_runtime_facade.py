from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from zsim.sim_progress.Buff.buff_class import Buff
from zsim.sim_progress.ScheduledEvent.buff_runtime import (
    BuffRuntimeFacade,
    LegacyBuffRuntimeFacade,
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
    ) -> None:
        self.ft = SimpleNamespace(index=index, alltime=alltime)
        self.dy = SimpleNamespace(
            active=active,
            startticks=startticks,
            endticks=endticks,
            count=count,
        )


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

    facade.enqueue_pending_buff("alpha", pending_buff)
    facade.append_active_buff("alpha", active_buff)

    assert loading_buff_dict["alpha"] == [pending_buff]
    assert dynamic_buff_dict["alpha"] == [active_buff]
    assert enemy_debuff_mirror == [enemy_debuff]


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
        enemy_debuff_mirror=[],
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


def test_legacy_buff_runtime_facade_syncs_enemy_debuff_mirror_by_index() -> None:
    old_debuff = _BuffProbe("debuff")
    other_debuff = _BuffProbe("other")
    replacement_debuff = _BuffProbe("debuff")
    enemy_debuff_mirror: list[Any] = [old_debuff, other_debuff]
    facade = _create_facade(
        exist_buff_dict={"enemy": {}},
        loading_buff_dict={"enemy": []},
        dynamic_buff_dict={"enemy": []},
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    facade.sync_enemy_debuff_mirror(replacement_debuff)
    assert enemy_debuff_mirror == [other_debuff, replacement_debuff]
    assert facade.get_enemy_debuff_mirror_for_compat() is enemy_debuff_mirror

    facade.remove_enemy_debuff_mirror(replacement_debuff)
    assert enemy_debuff_mirror == [other_debuff]


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


def test_legacy_buff_runtime_facade_tick_sweep_uses_wrapped_legacy_containers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from zsim.sim_progress.Update import Update_Buff

    exist_buff_dict: dict[str, dict[str, Any]] = {"alpha": {}}
    loading_buff_dict: dict[str, list[Any]] = {"alpha": []}
    dynamic_buff_dict: dict[str, list[Any]] = {"alpha": []}
    enemy = SimpleNamespace()
    calls: list[tuple[dict[str, list[Any]], int, dict[str, dict[str, Any]], Any]] = []

    def fake_update_time_related_effect(
        dynamic_buff: dict[str, list[Any]],
        tick: int,
        exist_buff: dict[str, dict[str, Any]],
        received_enemy: Any,
    ) -> dict[str, list[Any]]:
        calls.append((dynamic_buff, tick, exist_buff, received_enemy))
        return dynamic_buff

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
    assert calls == [(dynamic_buff_dict, 77, exist_buff_dict, enemy)]


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
    dynamic_buff_dict: dict[str, list[Any]] = {"enemy": [old_enemy_buff]}
    enemy_debuff_mirror: list[Any] = [old_enemy_buff, other_enemy_buff]
    facade = _create_facade(
        exist_buff_dict={"enemy": {}},
        loading_buff_dict=loading_buff_dict,
        dynamic_buff_dict=dynamic_buff_dict,
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    facade.activate_pending_buffs(timenow=10)

    assert loading_buff_dict["enemy"] == []
    assert dynamic_buff_dict["enemy"] == [replacement_enemy_buff]
    assert enemy_debuff_mirror == [other_enemy_buff, replacement_enemy_buff]
