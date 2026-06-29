from types import SimpleNamespace
from typing import Any, cast

import pytest

import zsim.sim_progress.Buff.BuffXLogic.SeveredInnocenceCritDMGBonus as severed_module
from zsim.sim_progress.Preload import SkillNode


def _buff_0() -> SimpleNamespace:
    return SimpleNamespace(history=SimpleNamespace(record=None))


def _logic_harness(
    *,
    index: str = "severed-template-index",
    tick: int = 180,
    maxduration: int = 60,
) -> SimpleNamespace:
    sim_instance = SimpleNamespace(tick=tick)
    buff_instance = SimpleNamespace(
        sim_instance=sim_instance,
        ft=SimpleNamespace(index=index, maxduration=maxduration),
        dy=SimpleNamespace(built_in_buff_box=[["stale", 1]], count=9),
    )
    logic = severed_module.SeveredInnocenceCritDMGBonus(cast(Any, buff_instance))
    return SimpleNamespace(
        logic=logic,
        buff_instance=buff_instance,
        sim_instance=sim_instance,
    )


def _skill_node(
    *,
    skill_tag: list[str] | None = None,
    preload_tick: int = 180,
    labels: dict[str, object] | None = None,
    trigger_buff_level: int = 0,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.skill_tag = skill_tag if skill_tag is not None else ["1381"]
    node.preload_tick = preload_tick
    node.skill = SimpleNamespace(
        labels=labels,
        trigger_buff_level=trigger_buff_level,
    )
    return node


def _install_preparation_context(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
) -> tuple[SimpleNamespace, list[object], list[tuple[str, object]]]:
    build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_find_equipper(item_name: str) -> str:
        context_calls.append(("find_equipper", item_name))
        return owner

    def fake_find_sub_exist_buff_dict(owner_name: str) -> dict[str, object]:
        context_calls.append(("find_sub_exist_buff_dict", owner_name))
        assert owner_name == owner
        return {harness.buff_instance.ft.index: buff_0}

    preparation_context = SimpleNamespace(
        find_equipper=fake_find_equipper,
        find_sub_exist_buff_dict=fake_find_sub_exist_buff_dict,
    )

    def fake_build_preparation_context(buff_instance: object) -> SimpleNamespace:
        build_calls.append(buff_instance)
        assert buff_instance is harness.buff_instance
        return preparation_context

    if hasattr(severed_module, "JudgeTools"):
        monkeypatch.setattr(
            severed_module.JudgeTools,
            "find_equipper",
            lambda *args, **kwargs: pytest.fail("Severed must use PreparationContext"),
        )
        monkeypatch.setattr(
            severed_module.JudgeTools,
            "find_exist_buff_dict",
            lambda *args, **kwargs: pytest.fail("Severed must use PreparationContext"),
        )
    monkeypatch.setattr(
        severed_module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context,
    )
    return preparation_context, build_calls, context_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    harness: SimpleNamespace,
    owner: str,
    buff_0: SimpleNamespace,
    preparation_context: SimpleNamespace,
    sub_exist_buff_dict: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        preparation_context: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness.buff_instance
        assert buff_0 is buff_0_ref
        assert preparation_context is preparation_context_ref
        preparation_calls.append(dict(kwargs))
        record = cast(Any, buff_0_ref.history.record)
        record.equipper = owner
        record.char = SimpleNamespace(CID=1381, NAME=owner)
        if kwargs.get("sub_exist_buff_dict") == 1:
            record.sub_exist_buff_dict = sub_exist_buff_dict_ref

    buff_0_ref = buff_0
    preparation_context_ref = preparation_context
    sub_exist_buff_dict_ref = (
        sub_exist_buff_dict
        if sub_exist_buff_dict is not None
        else {harness.buff_instance.ft.index: buff_0}
    )
    monkeypatch.setattr(severed_module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, *, harness: SimpleNamespace) -> list[object]:
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return harness.sim_instance.tick

    monkeypatch.setattr(severed_module, "find_tick", fake_find_tick)
    return tick_calls


def _prepared_logic(
    monkeypatch: pytest.MonkeyPatch,
    *,
    tick: int = 180,
    owner: str = "安比",
) -> tuple[SimpleNamespace, SimpleNamespace, list[dict[str, object]]]:
    harness = _logic_harness(tick=tick)
    buff_0 = _buff_0()
    preparation_context, _, _ = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
        preparation_context=preparation_context,
    )
    return harness, buff_0, preparation_calls


def test_severed_check_record_module_pins_preparation_context_owner_template_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness()
    owner = "安比"
    buff_0 = _buff_0()
    _, build_calls, context_calls = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )

    harness.logic.check_record_module()

    assert build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "牺牲洁纯"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.equipper == owner
    assert harness.logic.buff_0 is buff_0
    assert isinstance(
        buff_0.history.record,
        severed_module.SeveredInnocenceCritDMGBonusRecord,
    )
    assert harness.logic.record is buff_0.history.record
    assert cast(Any, harness.logic.record).char is None
    assert cast(Any, harness.logic.record).equipper is None
    assert cast(Any, harness.logic.record).update_signal == []
    assert cast(Any, harness.logic.record).active_tick_box == {
        0: {"start": 0, "end": 0},
        1: {"start": 0, "end": 0},
        2: {"start": 0, "end": 0},
    }
    assert cast(Any, harness.logic.record).sub_exist_buff_dict is None

    existing_record = harness.logic.record
    harness.logic.check_record_module()

    assert build_calls == [harness.buff_instance]
    assert context_calls == [
        ("find_equipper", "牺牲洁纯"),
        ("find_sub_exist_buff_dict", owner),
    ]
    assert harness.logic.record is existing_record
    assert buff_0.history.record is existing_record


def test_severed_special_judge_logic_pins_required_argument_and_type_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, _, preparation_calls = _prepared_logic(monkeypatch)

    with pytest.raises(ValueError, match="skill_node"):
        harness.logic.special_judge_logic(loading_mission=object())

    with pytest.raises(ValueError, match="loading_mission"):
        harness.logic.special_judge_logic(skill_node=_skill_node())

    with pytest.raises(TypeError, match="SkillNode"):
        harness.logic.special_judge_logic(skill_node=object(), loading_mission=object())

    assert preparation_calls == [
        {"char_CID": 1381, "equipper": "牺牲洁纯"},
        {"char_CID": 1381, "equipper": "牺牲洁纯"},
        {"char_CID": 1381, "equipper": "牺牲洁纯"},
    ]


@pytest.mark.parametrize(
    (
        "skill_tag",
        "preload_tick_offset",
        "labels",
        "trigger_buff_level",
        "expected_result",
        "expected_signals",
    ),
    [
        (["1381"], 0, {"aftershock_attack": object()}, 2, True, [2]),
        (["1381"], 0, {"not_aftershock": object()}, 2, None, []),
        (["1381"], 0, None, 0, True, [0]),
        (["1381"], 0, None, 1, True, [1]),
        (["1381"], 0, None, 2, True, [1]),
        (["1381"], 0, None, 9, False, []),
        (["9999"], 0, None, 0, False, []),
        (["1381"], -1, None, 0, False, []),
        (["1381"], 1, None, 0, False, []),
    ],
)
def test_severed_special_judge_logic_pins_signal_gates(
    monkeypatch: pytest.MonkeyPatch,
    skill_tag: list[str],
    preload_tick_offset: int,
    labels: dict[str, object] | None,
    trigger_buff_level: int,
    expected_result: bool | None,
    expected_signals: list[int],
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, tick=300)
    tick_calls = _install_tick(monkeypatch, harness=harness)
    skill_node = _skill_node(
        skill_tag=skill_tag,
        preload_tick=harness.sim_instance.tick + preload_tick_offset,
        labels=labels,
        trigger_buff_level=trigger_buff_level,
    )

    result = harness.logic.special_judge_logic(
        skill_node=skill_node,
        loading_mission=object(),
    )

    assert result is expected_result
    assert preparation_calls == [{"char_CID": 1381, "equipper": "牺牲洁纯"}]
    assert tick_calls == [harness.sim_instance]
    assert cast(Any, buff_0.history.record).update_signal == expected_signals


def test_severed_special_start_logic_pins_no_signal_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness, buff_0, preparation_calls = _prepared_logic(monkeypatch, tick=420)
    _install_tick(monkeypatch, harness=harness)
    harness.buff_instance.simple_start = lambda *args, **kwargs: pytest.fail(
        "no signal must not call simple_start"
    )
    harness.buff_instance.update_to_buff_0 = lambda *args, **kwargs: pytest.fail(
        "no signal must not call update_to_buff_0"
    )
    before_box = list(harness.buff_instance.dy.built_in_buff_box)

    harness.logic.special_start_logic()

    assert preparation_calls == [
        {"char_CID": 1381, "equipper": "牺牲洁纯", "sub_exist_buff_dict": 1}
    ]
    assert cast(Any, buff_0.history.record).update_signal == []
    assert harness.buff_instance.dy.built_in_buff_box == before_box
    assert harness.buff_instance.dy.count == 9


def test_severed_special_start_logic_pins_unique_batching_boxes_and_update_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness(tick=500, maxduration=90)
    owner = "安比"
    buff_0 = _buff_0()
    sub_exist_buff_dict = {harness.buff_instance.ft.index: buff_0, "neighbor": object()}
    preparation_context, _, _ = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
        preparation_context=preparation_context,
        sub_exist_buff_dict=sub_exist_buff_dict,
    )
    tick_calls = _install_tick(monkeypatch, harness=harness)
    events: list[tuple[str, object]] = []

    def fake_simple_start(timenow: int, exist_buff_dict: dict[str, object], **kwargs: object) -> None:
        events.append(
            (
                "simple_start",
                {
                    "timenow": timenow,
                    "exist_buff_dict": exist_buff_dict,
                    "kwargs": dict(kwargs),
                },
            )
        )

    def fake_update_to_buff_0(target_buff_0: object) -> None:
        events.append(("update_to_buff_0", target_buff_0))

    harness.buff_instance.simple_start = fake_simple_start
    harness.buff_instance.update_to_buff_0 = fake_update_to_buff_0
    harness.logic.check_record_module()
    record = cast(Any, buff_0.history.record)
    record.update_signal = [2, 1, 1, 0, 2]

    harness.logic.special_start_logic()

    assert preparation_calls == [
        {"char_CID": 1381, "equipper": "牺牲洁纯", "sub_exist_buff_dict": 1}
    ]
    assert tick_calls == [harness.sim_instance]
    assert record.active_tick_box == {
        0: {"start": 500, "end": 590},
        1: {"start": 500, "end": 590},
        2: {"start": 500, "end": 590},
    }
    assert events == [
        (
            "simple_start",
            {
                "timenow": 500,
                "exist_buff_dict": sub_exist_buff_dict,
                "kwargs": {"no_count": 1},
            },
        ),
        ("update_to_buff_0", buff_0),
    ]
    assert harness.buff_instance.dy.built_in_buff_box == [
        [500, 590],
        [500, 590],
        [500, 590],
    ]
    assert harness.buff_instance.dy.count == 3


def test_severed_special_start_logic_pins_expired_mode_filter_and_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = _logic_harness(tick=640, maxduration=120)
    owner = "安比"
    buff_0 = _buff_0()
    preparation_context, _, _ = _install_preparation_context(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
    )
    _install_preparation(
        monkeypatch,
        harness=harness,
        owner=owner,
        buff_0=buff_0,
        preparation_context=preparation_context,
    )
    _install_tick(monkeypatch, harness=harness)
    harness.buff_instance.simple_start = lambda *args, **kwargs: None
    harness.buff_instance.update_to_buff_0 = lambda *args, **kwargs: None
    harness.logic.check_record_module()
    record = cast(Any, buff_0.history.record)
    record.active_tick_box[0] = {"start": 300, "end": 500}
    record.active_tick_box[1] = {"start": 400, "end": 650}
    record.update_signal = [2]

    harness.logic.special_start_logic()

    assert record.active_tick_box == {
        0: {"start": 300, "end": 500},
        1: {"start": 400, "end": 650},
        2: {"start": 640, "end": 760},
    }
    assert harness.buff_instance.dy.built_in_buff_box == [
        [400, 650],
        [640, 760],
    ]
    assert harness.buff_instance.dy.count == 2
