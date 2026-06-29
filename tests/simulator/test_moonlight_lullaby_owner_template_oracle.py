from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.MoonlightLullabyAllTeamDmgBonus as moonlight_module


def _make_moonlight_logic() -> SimpleNamespace:
    sim_instance = object()
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index="moonlight-template-index"),
    )
    buff_0 = SimpleNamespace(history=SimpleNamespace(record=None))
    logic = moonlight_module.MoonlightLullabyAllTeamDmgBonus(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
        buff_0=buff_0,
    )


def test_moonlight_lullaby_check_record_module_preserves_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_moonlight_logic()
    owner = "莱卡恩"
    find_equipper_calls: list[tuple[str, object]] = []
    find_exist_calls: list[object] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        find_equipper_calls.append((item_name, sim_instance))
        return owner

    def fake_find_exist_buff_dict(
        *, sim_instance: object
    ) -> dict[str, dict[str, object]]:
        find_exist_calls.append(sim_instance)
        return {owner: {harness.buff_instance.ft.index: harness.buff_0}}

    monkeypatch.setattr(
        moonlight_module.JudgeTools,
        "find_equipper",
        fake_find_equipper,
    )
    monkeypatch.setattr(
        moonlight_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )

    harness.logic.check_record_module()

    assert find_equipper_calls == [("月光骑士颂", harness.sim_instance)]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is harness.buff_0
    assert isinstance(
        harness.buff_0.history.record,
        moonlight_module.MoonlightLullabyAllTeamDmgBonusRecord,
    )
    assert harness.logic.record is harness.buff_0.history.record

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert find_equipper_calls == [("月光骑士颂", harness.sim_instance)]
    assert find_exist_calls == [harness.sim_instance]
    assert harness.logic.buff_0 is harness.buff_0
    assert harness.logic.record is existing_record
    assert harness.buff_0.history.record is existing_record


def test_moonlight_lullaby_special_judge_logic_prepares_cached_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_moonlight_logic()
    owner = "莱卡恩"
    preparation_calls: list[tuple[object, object, dict[str, object]]] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        assert item_name == "月光骑士颂"
        assert sim_instance is harness.sim_instance
        return owner

    def fake_find_exist_buff_dict(
        *, sim_instance: object
    ) -> dict[str, dict[str, object]]:
        assert sim_instance is harness.sim_instance
        return {owner: {harness.buff_instance.ft.index: harness.buff_0}}

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        preparation_calls.append((buff_instance, buff_0, dict(kwargs)))

    monkeypatch.setattr(
        moonlight_module.JudgeTools,
        "find_equipper",
        fake_find_equipper,
    )
    monkeypatch.setattr(
        moonlight_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    monkeypatch.setattr(
        moonlight_module,
        "check_preparation",
        fake_check_preparation,
    )

    harness.logic.special_judge_logic()

    assert preparation_calls == [
        (
            harness.buff_instance,
            harness.buff_0,
            {"equipper": "月光骑士颂"},
        )
    ]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is harness.buff_0
    assert harness.logic.record is harness.buff_0.history.record
