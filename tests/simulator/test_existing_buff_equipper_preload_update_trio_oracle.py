from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFXLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-30-US-001-existing-buff-equipper-preload-update-trio-oracle.json"
)

TICK_NOW = 1800
SUB_EXIST_BUFF_DICT = {"sub": "registry"}

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerDmgBonus.py",
        "module": "FlamemakerShakerDmgBonus",
        "logic": "FlamemakerShakerDmgBonus",
        "record": "FlamemakerShakerDmgBonusRecord",
        "item": "灼心摇壶",
        "judge_prepared": {"equipper": "灼心摇壶"},
        "effect_prepared": {
            "equipper": "灼心摇壶",
            "preload_data": 1,
            "sub_exist_buff_dict": 1,
        },
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerPhyDmgBonus.py",
        "module": "SharpenedStingerPhyDmgBonus",
        "logic": "SharpenedStingerPhyDmgBonus",
        "record": "SharpenedStingerPhyDmgBonusRecord",
        "item": "淬锋钳刺",
        "judge_prepared": {"equipper": "淬锋钳刺", "preload_data": 1},
        "effect_prepared": {
            "equipper": "淬锋钳刺",
            "preload_data": 1,
            "sub_exist_buff_dict": 1,
        },
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/SpectralGazeSpiritLock.py",
        "module": "SpectralGazeSpiritLock",
        "logic": "SpectralGazeSpiritLock",
        "record": "SpectralGazeSpiritLockRecord",
        "item": "索魂影眸",
        "judge_prepared": {"equipper": "索魂影眸", "preload_data": 1},
        "effect_prepared": {"equipper": "索魂影眸", "preload_data": 1},
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED = (
    "manager/resource rows",
    "trigger-buff rows",
    "listener/action-stack/dynamic-active-view rows",
    "scheduled emitter rows",
    "existing-buff-only rows",
    "dynamic char_name owner rows",
    "Calculator internals",
    "anomaly runtime internals",
    "character manager internals",
    "broader runtime-truth-source pools",
)


def _module(row: dict[str, object]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


class _TemplateBuff:
    def __init__(self, *, record: object | None = None, ready: bool = True) -> None:
        self.history = SimpleNamespace(record=record)
        self.dy = SimpleNamespace(ready=ready, count=0)
        self.ready_judge_calls: list[int] = []

    def ready_judge(self, tick: int) -> None:
        self.ready_judge_calls.append(tick)


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str = "equipper-preload-update-template-index",
        tick: int = TICK_NOW,
        maxcount: int = 9,
        count: int = 0,
    ) -> None:
        self.sim_instance = SimpleNamespace(tick=tick)
        self.ft = SimpleNamespace(index=index, maxcount=maxcount)
        self.dy = SimpleNamespace(count=count)
        self.simple_start_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.update_to_buff_0_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def simple_start(self, *args: object, **kwargs: object) -> None:
        self.simple_start_calls.append((args, dict(kwargs)))

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        self.update_to_buff_0_calls.append((args, dict(kwargs)))


def _install_tick(monkeypatch: pytest.MonkeyPatch, module: Any) -> list[object]:
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return sim_instance.tick

    monkeypatch.setattr(module, "find_tick", fake_find_tick)
    return tick_calls


def _install_equipper_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    item: str,
    index: str,
    buff_0: _TemplateBuff,
    registry: dict[str, dict[str, object]] | None = None,
) -> SimpleNamespace:
    equipper = f"equipper:{item}"
    lookup_registry = registry if registry is not None else {equipper: {index: buff_0}}
    raw_equipper_calls: list[tuple[str, object]] = []
    raw_existing_buff_calls: list[object] = []
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_find_equipper(item_name: str, *, sim_instance: object) -> str:
        raw_equipper_calls.append((item_name, sim_instance))
        return equipper

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        raw_existing_buff_calls.append(sim_instance)
        return lookup_registry

    class FakePreparationContext:
        def __init__(self, sim_instance: object) -> None:
            self.sim_instance = sim_instance

        def find_equipper(self, item_name: str) -> str:
            context_calls.append(("find_equipper", item_name))
            return equipper

        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            context_calls.append(("find_sub_exist_buff_dict", owner_name))
            return lookup_registry[owner_name]

    def fake_context_builder(buff_instance: object) -> FakePreparationContext:
        context_build_calls.append(buff_instance)
        return FakePreparationContext(buff_instance.sim_instance)

    monkeypatch.setattr(module.JudgeTools, "find_equipper", fake_find_equipper)
    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    monkeypatch.setattr(
        module,
        "build_preparation_context_from_buff",
        fake_context_builder,
        raising=False,
    )
    return SimpleNamespace(
        owner=equipper,
        raw_equipper_calls=raw_equipper_calls,
        raw_existing_buff_calls=raw_existing_buff_calls,
        context_build_calls=context_build_calls,
        context_calls=context_calls,
    )


def _lookup_asserts_one_owner_and_template_resolution(
    lookup: SimpleNamespace,
    *,
    item: str,
    sim_instance: object,
) -> None:
    raw_path = lookup.raw_equipper_calls == [(item, sim_instance)] and (
        lookup.raw_existing_buff_calls == [sim_instance]
    )
    context_path = lookup.context_build_calls and lookup.context_calls == [
        ("find_equipper", item),
        ("find_sub_exist_buff_dict", lookup.owner),
    ]
    assert raw_path or context_path


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: _TemplateBuff,
    char: object | None = None,
    preload_data: object | None = None,
    sub_exist_buff_dict: dict[str, object] | None = None,
    raises: Exception | None = None,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness
        assert buff_0 is buff_0_ref
        observed_kwargs = dict(kwargs)
        observed_kwargs.pop("preparation_context", None)
        preparation_calls.append(observed_kwargs)
        if raises is not None:
            raise raises
        record = buff_0_ref.history.record
        if kwargs.get("equipper") is not None:
            record.equipper = lookup_owner
        if char_ref is not None:
            record.char = char_ref
        if kwargs.get("preload_data") is not None:
            record.preload_data = preload_data_ref
        if kwargs.get("sub_exist_buff_dict") is not None:
            record.sub_exist_buff_dict = sub_exist_buff_dict_ref

    buff_0_ref = buff_0
    lookup_owner = f"equipper:{kwargs_item(module)}"
    char_ref = char
    preload_data_ref = preload_data
    sub_exist_buff_dict_ref = sub_exist_buff_dict if sub_exist_buff_dict is not None else SUB_EXIST_BUFF_DICT
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def kwargs_item(module: Any) -> str:
    module_name = module.__name__.rsplit(".", 1)[-1]
    for row in SELECTED_ROWS:
        if row["module"] == module_name:
            return str(row["item"])
    raise AssertionError(f"unknown module {module_name}")


def _skill_node(
    *,
    char_name: str = "equipper:灼心摇壶",
    trigger_buff_level: int = 2,
    labels: object | None = None,
    skill_tag: str = "1311-aftershock",
    element_type: int = 3,
    instance_id: int = 1,
) -> SkillNode:
    node = SkillNode.__new__(SkillNode)
    node.char_name = char_name
    node.skill = SimpleNamespace(
        trigger_buff_level=trigger_buff_level,
        labels=labels,
        element_type=element_type,
    )
    node.skill_tag = skill_tag
    node._element_type_change = None
    node.get_total_instances = lambda: instance_id
    return node


def _loading_mission(node: SkillNode) -> LoadingMission:
    mission = LoadingMission.__new__(LoadingMission)
    mission.mission_node = node
    return mission


def _equipper_preload_update_trio_scan() -> list[str]:
    rows: list[str] = []
    row_terms = {
        "FlamemakerShakerDmgBonus.py": (
            '"灼心摇壶"',
            "FlamemakerShakerDmgBonusRecord",
            "preload_data",
            "simple_start",
            "update_to_buff_0",
        ),
        "SharpenedStingerPhyDmgBonus.py": (
            '"淬锋钳刺"',
            "SharpenedStingerPhyDmgBonusRecord",
            "ready_judge",
            "update_signal",
            "update_to_buff_0",
        ),
        "SpectralGazeSpiritLock.py": (
            '"索魂影眸"',
            "SpectralGazeSpiritLockRecord",
            "loading_mission.is_hit_now",
            "last_update_node_id",
            "aftershock_attack",
        ),
    }
    for filename, terms in row_terms.items():
        path = BUFFXLOGIC_ROOT / filename
        source = path.read_text(encoding="utf-8")
        lookup_path = (
            "JudgeTools.find_equipper" in source
            and "JudgeTools.find_exist_buff_dict" in source
        ) or "ensure_equipper_template_record(" in source
        if lookup_path and all(term in source for term in terms):
            rows.append(path.relative_to(PROJECT_ROOT).as_posix())
    return rows


def test_us001_checkpoint_and_current_census_match_equipper_preload_update_trio() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))

    assert checkpoint["schema"] == (
        "zsim-existing-buff-equipper-preload-update-trio-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 3
    assert checkpoint["scan_summary"]["bounded_equipper_preload_update_rows"] == list(
        SELECTED_FILES
    )
    assert checkpoint["excluded_or_deferred"] == [
        {"pool": pool} for pool in EXCLUDED_OR_DEFERRED
    ]
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-equipper-preload-update-trio-migration"
    )
    assert checkpoint["us002_target_allowed_values"] == [
        "existing-buff-equipper-preload-update-trio-migration",
        "none-safe-to-implement",
    ]
    assert _equipper_preload_update_trio_scan() == list(SELECTED_FILES)


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_trio_check_record_module_pins_equipper_index_lazy_record_and_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    record_cls = getattr(module, str(row["record"]))
    harness = _RecordingBuffInstance(index="selected-template-index")
    logic = logic_cls(harness)
    template = _TemplateBuff()
    lookup = _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    _lookup_asserts_one_owner_and_template_resolution(
        lookup,
        item=str(row["item"]),
        sim_instance=harness.sim_instance,
    )
    assert logic.equipper == lookup.owner
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    _lookup_asserts_one_owner_and_template_resolution(
        lookup,
        item=str(row["item"]),
        sim_instance=harness.sim_instance,
    )
    assert template.history.record is existing_record
    assert logic.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {"EQUIPPER": {}}])
def test_trio_check_record_module_pins_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
    registry: dict[str, dict[str, object]],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index="missing-template-index")
    logic = logic_cls(harness)
    normalized_registry = (
        registry
        if not registry
        else {f"equipper:{row['item']}": registry["EQUIPPER"]}
    )
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=_TemplateBuff(),
        registry=normalized_registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


def test_flamemaker_judge_pins_loading_mission_trigger_label_and_owner_gates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.FlamemakerShakerDmgBonus(harness)
    template = _TemplateBuff()
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(CID=101),
    )
    owner = "equipper:灼心摇壶"

    assert logic.special_judge_logic() is False
    assert logic.special_judge_logic(skill_node=object()) is False
    assert logic.special_judge_logic(
        skill_node=_skill_node(char_name="other", trigger_buff_level=2)
    ) is False
    assert logic.special_judge_logic(
        skill_node=_loading_mission(_skill_node(char_name=owner, trigger_buff_level=2))
    ) is True
    assert logic.special_judge_logic(
        skill_node=_skill_node(
            char_name=owner,
            trigger_buff_level=1,
            labels={"Assist_Attack": 1},
        )
    ) is True
    assert logic.special_judge_logic(
        skill_node=_skill_node(
            char_name=owner,
            trigger_buff_level=1,
            labels={"Basic_Attack": 1},
        )
    ) is False
    assert logic.special_judge_logic(
        skill_node=_skill_node(char_name=owner, trigger_buff_level=1, labels=None)
    ) is None

    assert preparation_calls == [row["judge_prepared"]] * 7


@pytest.mark.parametrize(
    ("operating_now", "initial_count", "expected_kwargs", "expected_count"),
    [
        (999, 8, {"no_count": 1}, 9),
        (101, 4, {}, 4),
    ],
)
def test_flamemaker_hit_pins_background_active_simple_start_manual_count_and_update(
    monkeypatch: pytest.MonkeyPatch,
    operating_now: int,
    initial_count: int,
    expected_kwargs: dict[str, object],
    expected_count: int,
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    harness = _RecordingBuffInstance(maxcount=9, count=initial_count)
    logic = module.FlamemakerShakerDmgBonus(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(CID=101),
        preload_data=SimpleNamespace(operating_now=operating_now),
        sub_exist_buff_dict=SUB_EXIST_BUFF_DICT,
    )

    logic.special_hit_logic()

    assert preparation_calls == [row["effect_prepared"]]
    assert harness.simple_start_calls == [
        ((TICK_NOW, SUB_EXIST_BUFF_DICT), expected_kwargs)
    ]
    assert harness.dy.count == expected_count
    assert harness.update_to_buff_0_calls == [((template,), {})]


def test_sharpened_stinger_judge_pins_type_ready_stack_and_update_signals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.SharpenedStingerPhyDmgBonus(harness)
    template = _TemplateBuff(ready=False)
    _install_tick(monkeypatch, module)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    char = SimpleNamespace(NAME="equipper:淬锋钳刺", CID=202)
    preload_data = SimpleNamespace(personal_node_stack={202: [_skill_node()]})
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
        preload_data=preload_data,
    )

    assert logic.special_judge_logic() is False
    with pytest.raises(TypeError, match="不是SkillNode"):
        logic.special_judge_logic(skill_node=object())
    assert logic.special_judge_logic(skill_node=_skill_node(char_name="other")) is False
    assert logic.special_judge_logic(skill_node=_skill_node(char_name=char.NAME)) is False

    template.dy.ready = True
    assert logic.special_judge_logic(skill_node=_skill_node(char_name=char.NAME)) is True
    assert logic.record.update_signal == 1

    logic.record.update_signal = None
    preload_data.personal_node_stack[202] = [_skill_node(), _skill_node()]
    assert logic.special_judge_logic(
        skill_node=_skill_node(char_name=char.NAME, trigger_buff_level=2)
    ) is False
    assert logic.record.update_signal is None
    assert logic.special_judge_logic(
        skill_node=_skill_node(char_name=char.NAME, trigger_buff_level=3)
    ) is True
    assert logic.record.update_signal == 0
    assert logic.special_judge_logic(
        skill_node=_skill_node(char_name=char.NAME, trigger_buff_level=4)
    ) is True
    assert logic.record.update_signal == 1

    assert preparation_calls == [row["judge_prepared"]] * 8
    assert template.ready_judge_calls == [TICK_NOW] * 5


@pytest.mark.parametrize(
    ("update_signal", "expected_calls", "expected_count", "expected_updates"),
    [
        (None, [], 0, []),
        (0, [((TICK_NOW, SUB_EXIST_BUFF_DICT), {})], 0, []),
        (1, [((TICK_NOW, SUB_EXIST_BUFF_DICT), {"no_count": 1})], 9, [((_TemplateBuff,), {})]),
    ],
)
def test_sharpened_stinger_start_pins_update_signal_simple_start_max_count_and_update(
    monkeypatch: pytest.MonkeyPatch,
    update_signal: int | None,
    expected_calls: list[tuple[tuple[object, ...], dict[str, object]]],
    expected_count: int,
    expected_updates: list[tuple[tuple[object, ...], dict[str, object]]],
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    harness = _RecordingBuffInstance(maxcount=9)
    logic = module.SharpenedStingerPhyDmgBonus(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(NAME="equipper:淬锋钳刺", CID=202),
        preload_data=SimpleNamespace(personal_node_stack={202: []}),
        sub_exist_buff_dict=SUB_EXIST_BUFF_DICT,
    )

    logic.check_record_module()
    logic.record.update_signal = update_signal
    logic.special_start_logic()

    assert preparation_calls == [row["effect_prepared"]]
    assert harness.simple_start_calls == expected_calls
    assert harness.dy.count == expected_count
    if expected_updates:
        assert harness.update_to_buff_0_calls == [((template,), {})]
    else:
        assert harness.update_to_buff_0_calls == []


def test_spectral_gaze_judge_pins_missing_type_and_loading_mission_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.SpectralGazeSpiritLock(harness)
    template = _TemplateBuff()
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(NAME="equipper:索魂影眸", CID=1311),
        preload_data=SimpleNamespace(operating_now=999),
    )

    with pytest.raises(ValueError, match="缺少skill_node"):
        logic.special_judge_logic()
    with pytest.raises(TypeError):
        logic.special_judge_logic(skill_node=object())
    with pytest.raises(AttributeError):
        logic.special_judge_logic(skill_node=_skill_node(skill_tag="1311-aftershock"))

    assert preparation_calls == [row["judge_prepared"]] * 3


@pytest.mark.parametrize(
    (
        "hit_now",
        "skill_tag",
        "labels",
        "element_type",
        "operating_now",
        "instance_id",
        "expected",
        "expected_last_id",
    ),
    [
        (False, "1311-aftershock", {"aftershock_attack": 1}, 3, 999, 1, False, None),
        (True, "9999-aftershock", {"aftershock_attack": 1}, 3, 999, 1, False, None),
        (True, "1311-aftershock", None, 3, 999, 1, False, None),
        (True, "1311-aftershock", {"basic_attack": 1}, 3, 999, 1, False, None),
        (True, "1311-aftershock", {"aftershock_attack": 1}, 2, 999, 1, False, None),
        (True, "1311-aftershock", {"aftershock_attack": 1}, 3, 1311, 1, False, None),
        (True, "1311-aftershock", {"aftershock_attack": 1}, 3, 999, 7, True, 7),
    ],
)
def test_spectral_gaze_judge_pins_hit_cid_label_element_background_and_dedup_gates(
    monkeypatch: pytest.MonkeyPatch,
    hit_now: bool,
    skill_tag: str,
    labels: dict[str, object] | None,
    element_type: int,
    operating_now: int,
    instance_id: int,
    expected: bool,
    expected_last_id: int | None,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.SpectralGazeSpiritLock(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(NAME="equipper:索魂影眸", CID=1311),
        preload_data=SimpleNamespace(operating_now=operating_now),
    )
    hit_checks: list[int] = []
    loading_mission = SimpleNamespace(
        is_hit_now=lambda tick: hit_checks.append(tick) or hit_now
    )
    skill_node = _skill_node(
        skill_tag=skill_tag,
        labels=labels,
        element_type=element_type,
        instance_id=instance_id,
    )

    assert logic.special_judge_logic(
        skill_node=skill_node,
        loading_mission=loading_mission,
    ) is expected
    assert logic.record.last_update_node_id == expected_last_id
    assert preparation_calls == [row["judge_prepared"]]
    assert hit_checks == [TICK_NOW]

    if expected:
        assert logic.special_judge_logic(
            skill_node=skill_node,
            loading_mission=loading_mission,
        ) is False
        assert logic.record.last_update_node_id == instance_id


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_trio_preparation_errors_propagate_before_file_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_equipper_lookup(
        monkeypatch,
        module=module,
        item=str(row["item"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        raises=RuntimeError("missing preparation"),
    )

    with pytest.raises(RuntimeError, match="missing preparation"):
        if row["module"] == "FlamemakerShakerDmgBonus":
            logic.special_hit_logic()
        elif row["module"] == "SharpenedStingerPhyDmgBonus":
            logic.special_start_logic()
        else:
            logic.special_judge_logic(
                skill_node=_skill_node(skill_tag="1311-aftershock"),
                loading_mission=SimpleNamespace(is_hit_now=lambda tick: True),
            )

    assert preparation_calls == [row["effect_prepared"]]
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
