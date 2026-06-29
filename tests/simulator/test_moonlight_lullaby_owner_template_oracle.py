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


class _FakeMoonlightPreparationContext:
    def __init__(
        self,
        *,
        owner: str,
        index: str,
        buff_0: object,
        calls: list[tuple[str, object]],
    ) -> None:
        self._owner = owner
        self._index = index
        self._buff_0 = buff_0
        self._calls = calls

    def find_equipper(self, item_name: str) -> str:
        self._calls.append(("find_equipper", item_name))
        return self._owner

    def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
        self._calls.append(("find_sub_exist_buff_dict", owner_name))
        return {self._index: self._buff_0}


def test_moonlight_lullaby_check_record_module_preserves_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_moonlight_logic()
    owner = "莱卡恩"
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeMoonlightPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeMoonlightPreparationContext(
            owner=owner,
            index=harness.buff_instance.ft.index,
            buff_0=harness.buff_0,
            calls=context_calls,
        )

    monkeypatch.setattr(
        moonlight_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )

    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "月光骑士颂"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is harness.buff_0
    assert isinstance(
        harness.buff_0.history.record,
        moonlight_module.MoonlightLullabyAllTeamDmgBonusRecord,
    )
    assert harness.logic.record is harness.buff_0.history.record

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert context_build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "月光骑士颂"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.buff_0 is harness.buff_0
    assert harness.logic.record is existing_record
    assert harness.buff_0.history.record is existing_record


def test_moonlight_lullaby_special_judge_logic_prepares_cached_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _make_moonlight_logic()
    owner = "莱卡恩"
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []
    preparation_calls: list[tuple[object, object, dict[str, object]]] = []

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakeMoonlightPreparationContext:
        context_build_calls.append(buff_instance)
        return _FakeMoonlightPreparationContext(
            owner=owner,
            index=harness.buff_instance.ft.index,
            buff_0=harness.buff_0,
            calls=context_calls,
        )

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        preparation_calls.append(
            (buff_instance, buff_0, {"preparation_context": preparation_context, **kwargs})
        )

    monkeypatch.setattr(
        moonlight_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
    )
    monkeypatch.setattr(
        moonlight_module,
        "check_preparation",
        fake_check_preparation,
    )

    harness.logic.special_judge_logic()

    assert context_build_calls == [harness.buff_instance, harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "月光骑士颂"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert len(preparation_calls) == 1
    prepared_buff_instance, prepared_buff_0, prepared_kwargs = preparation_calls[0]
    assert prepared_buff_instance is harness.buff_instance
    assert prepared_buff_0 is harness.buff_0
    assert isinstance(
        prepared_kwargs["preparation_context"],
        _FakeMoonlightPreparationContext,
    )
    assert prepared_kwargs["equipper"] == "月光骑士颂"
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is harness.buff_0
    assert harness.logic.record is harness.buff_0.history.record
