from __future__ import annotations

from types import SimpleNamespace
from typing import Any

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
            enemy=SimpleNamespace(
                dynamic=SimpleNamespace(dynamic_debuff_list=enemy_debuff_mirror)
            )
        ),
        tick=tick,
    )


def test_buff_add_strategy_replaces_active_store_through_runtime_facade() -> None:
    template_buff = _BuffAddProbe("forced-buff", count=1)
    old_active_buff = _BuffAddProbe("forced-buff", count=9)
    active_store = [old_active_buff]
    pending_queue: list[Buff] = []
    sim_instance = _make_sim_instance(
        exist_buff_dict={"Alice": {"forced-buff": template_buff}},
        loading_buff_dict={"Alice": pending_queue},
        dynamic_buff_dict={"Alice": active_store},
        enemy_debuff_mirror=[],
    )

    buff_add_strategy(
        "forced-buff",
        benifit_list=["Alice"],
        specified_count=3,
        sim_instance=sim_instance,
    )

    assert sim_instance.global_stats.DYNAMIC_BUFF_DICT["Alice"] is active_store
    assert len(active_store) == 1
    new_active_buff = active_store[0]
    assert new_active_buff is not old_active_buff
    assert new_active_buff is not template_buff
    assert new_active_buff.ft.index == "forced-buff"
    assert new_active_buff.dy.count == 3
    assert new_active_buff.dy.startticks == 42
    assert new_active_buff.dy.endticks == 52
    assert pending_queue == []
    assert template_buff.history.active_times == 1


def test_buff_add_strategy_syncs_enemy_debuff_mirror_through_runtime_facade() -> None:
    template_debuff = _BuffAddProbe(
        "forced-debuff",
        operator="enemy",
        add_buff_to="0001",
        count=0,
    )
    old_active_debuff = _BuffAddProbe("forced-debuff", operator="enemy")
    old_mirror_debuff = _BuffAddProbe("forced-debuff", operator="enemy")
    other_mirror_debuff = _BuffAddProbe("other-debuff", operator="enemy")
    active_store = [old_active_debuff]
    enemy_debuff_mirror = [old_mirror_debuff, other_mirror_debuff]
    sim_instance = _make_sim_instance(
        exist_buff_dict={"enemy": {"forced-debuff": template_debuff}},
        loading_buff_dict={"enemy": []},
        dynamic_buff_dict={"enemy": active_store},
        enemy_debuff_mirror=enemy_debuff_mirror,
    )

    buff_add_strategy(
        "forced-debuff",
        benifit_list=["enemy"],
        sim_instance=sim_instance,
    )

    assert len(active_store) == 1
    new_debuff = active_store[0]
    assert new_debuff.ft.index == "forced-debuff"
    assert new_debuff is not old_active_debuff
    assert enemy_debuff_mirror == [other_mirror_debuff, new_debuff]
    assert sim_instance.load_data.LOADING_BUFF_DICT["enemy"] == []
