from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.SpectralGazeDefReduce as spectral_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(*, index: str = "spectral-template-index") -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=120)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index),
    )
    logic = spectral_module.SpectralGazeDefReduce(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    skill_tag: str,
    labels: dict[str, object] | None,
    element_type: int,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.skill_tag = skill_tag
    node.skill = SimpleNamespace(labels=labels, element_type=element_type)
    node._element_type_change = None
    return node


def _install_direct_owner_template_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[list[tuple[str, object]], list[object]]:
    owner_calls: list[tuple[str, object]] = []
    template_calls: list[object] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        owner_calls.append((item_name, sim_instance))
        return owner

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        template_calls.append(sim_instance)
        return {owner: {harness.buff_instance.ft.index: buff_0}}

    monkeypatch.setattr(spectral_module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(
        spectral_module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
    )
    return owner_calls, template_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    cid: int,
    buff_0: SimpleNamespace,
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
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(NAME=owner, CID=cid)

    buff_0_ref = buff_0
    monkeypatch.setattr(spectral_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def test_spectral_gaze_check_record_module_preserves_direct_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "扳机"
    buff_0 = _buff_0()
    owner_calls, template_calls = _install_direct_owner_template_lookup(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert owner_calls == [("索魂影眸", harness.sim_instance)]
    assert template_calls == [harness.sim_instance]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(buff_0.history.record, spectral_module.SpectralGazeDefReduceRecord)
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper is None
    assert cast(Any, harness.logic.record).char is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert owner_calls == [("索魂影眸", harness.sim_instance)]
    assert template_calls == [harness.sim_instance]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


def test_spectral_gaze_special_judge_logic_pins_missing_and_type_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "扳机"
    buff_0 = _buff_0()
    _install_direct_owner_template_lookup(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        cid=1311,
        buff_0=buff_0,
    )

    with pytest.raises(ValueError, match="缺少skill_node"):
        harness.logic.special_judge_logic()
    assert preparation_calls == [{"equipper": "索魂影眸"}]

    with pytest.raises(TypeError):
        harness.logic.special_judge_logic(skill_node=object())

    assert preparation_calls == [
        {"equipper": "索魂影眸"},
        {"equipper": "索魂影眸"},
    ]


@pytest.mark.parametrize(
    ("skill_tag", "labels", "element_type", "expected"),
    [
        ("cid-1311-aftershock", {"aftershock_attack": 1}, 3, True),
        ("cid-9999-aftershock", {"aftershock_attack": 1}, 3, False),
        ("cid-1311-aftershock", {}, 3, False),
        ("cid-1311-aftershock", None, 3, False),
        ("cid-1311-aftershock", {"aftershock_attack": 1}, 2, False),
        ("cid-1311-aftershock", {"basic_attack": 1}, 3, False),
    ],
)
def test_spectral_gaze_special_judge_logic_pins_cid_element_and_aftershock_gates(
    monkeypatch: pytest.MonkeyPatch,
    skill_tag: str,
    labels: dict[str, object] | None,
    element_type: int,
    expected: bool,
) -> None:
    harness = _logic_harness()
    owner = "扳机"
    buff_0 = _buff_0()
    owner_calls, template_calls = _install_direct_owner_template_lookup(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        cid=1311,
        buff_0=buff_0,
    )

    result = harness.logic.special_judge_logic(
        skill_node=_skill_node(
            skill_tag=skill_tag,
            labels=labels,
            element_type=element_type,
        )
    )

    assert result is expected
    assert owner_calls == [("索魂影眸", harness.sim_instance)]
    assert template_calls == [harness.sim_instance]
    assert preparation_calls == [{"equipper": "索魂影眸"}]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).equipper == owner
    assert cast(Any, harness.logic.record).char.CID == 1311
