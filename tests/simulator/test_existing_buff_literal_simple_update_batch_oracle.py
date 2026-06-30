from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFXLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-30-US-001-existing-buff-literal-simple-update-batch-oracle.json"
)

SUB_EXIST_BUFF_DICT = {"sub": "registry"}
TICK_NOW = 777

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
        "module": "JaneCinema1APTransToDmgBonus",
        "logic": "JaneCinema1APTransToDmgBonus",
        "record": "JaneCinema1APTransToDmgBonusRecord",
        "owner": "简",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
        "module": "JaneCoreSkillStrikeCritRateBonus",
        "logic": "JaneCoreSkillStrikeCritRateBonus",
        "record": "JaneCoreSkillStrikeCritRateBonusRecord",
        "owner": "简",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
        "module": "JanePassionStateAPTransToATK",
        "logic": "JanePassionStateAPTransToATK",
        "record": "JanePassionStateAPTransToATKRecord",
        "owner": "简",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py",
        "module": "LighterAdditionalAbility_IceFireBonus",
        "logic": "LighterExtraSkill_IceFireBonus",
        "record": "LighterExtraSkillRecord",
        "owner": "莱特",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/LighterUniqueSkillStunBonus.py",
        "module": "LighterUniqueSkillStunBonus",
        "logic": "LighterUniqueSkillStunBonus",
        "record": "LighterUniqueSkillStunBonusRecord",
        "owner": "莱特",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/LinaCoreSkillPenRatioBonus.py",
        "module": "LinaCoreSkillPenRatioBonus",
        "logic": "LinaCoreSkillPenRatioBonus",
        "record": "LinaCoreSkillRecord",
        "owner": "丽娜",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py",
        "module": "QingYiAdditionalAbilityStunConvertToATK",
        "logic": "QingYiAdditionalAbilityStunConvertToATK",
        "record": "QingYiAdditionalSkillRecord",
        "owner": "青衣",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/QingYiCoreSkillStunDMGBonus.py",
        "module": "QingYiCoreSkillStunDMGBonus",
        "logic": "QingYiCoreSkillStunDMGBonus",
        "record": "QintYiCoreSkillRecord",
        "owner": "青衣",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/SokakuUniqueSkillMinorATKBonus.py",
        "module": "SokakuUniqueSkillMinorATKBonus",
        "logic": "SokakuUniqueSkillMinorATKBonus",
        "record": "SokakuUniqueSkillMinorATKRecord",
        "owner": "苍角",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py",
        "module": "TriggerAdditionalAbilityStunBonus",
        "logic": "TriggerAdditionalAbilityStunBonus",
        "record": "TriggerAdditionalAbilityStunBonusRecord",
        "owner": "扳机",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
        "module": "YuzuhaAdditionalAbilityAnomalyBuildupBonus",
        "logic": "YuzuhaAdditionalAbilityAnomalyBuildupBonus",
        "record": "YuzuhaAdditionalAbilityAnomalyBuildupBonusRecord",
        "owner": "柚叶",
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)


def _module(row: dict[str, str]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


def _buff_0(*, record: object | None = None, count: float = 0, step: float = 1) -> SimpleNamespace:
    return SimpleNamespace(
        history=SimpleNamespace(record=record),
        dy=SimpleNamespace(count=count, active=False),
        ft=SimpleNamespace(step=step),
    )


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str = "literal-template-index",
        tick: int = TICK_NOW,
        step: float = 1,
        maxcount: float = 100,
    ) -> None:
        self.sim_instance = SimpleNamespace(tick=tick)
        self.ft = SimpleNamespace(index=index, step=step, maxcount=maxcount)
        self.dy = SimpleNamespace(count=0, active=False, startticks=0, endticks=0)
        self.simple_start_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.update_to_buff_0_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def simple_start(self, *args: object, **kwargs: object) -> None:
        self.simple_start_calls.append((args, dict(kwargs)))
        self.dy.count += self.ft.step

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        self.update_to_buff_0_calls.append((args, dict(kwargs)))


def _install_existing_buff_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    owner: str,
    index: str,
    buff_0: SimpleNamespace,
    registry: dict[str, dict[str, object]] | None = None,
) -> list[object]:
    lookup_calls: list[object] = []
    lookup_registry = registry if registry is not None else {owner: {index: buff_0}}

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        lookup_calls.append(sim_instance)
        return lookup_registry

    class _FakePreparationContext:
        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            assert module_context_buff is not None
            return fake_find_exist_buff_dict(
                sim_instance=module_context_buff.sim_instance
            )[owner_name]

    module_context_buff: object | None = None

    def fake_build_preparation_context_from_buff(buff_instance: object) -> _FakePreparationContext:
        nonlocal module_context_buff
        module_context_buff = buff_instance
        return _FakePreparationContext()

    judge_tools = getattr(module, "JudgeTools", None)
    if judge_tools is not None:
        monkeypatch.setattr(judge_tools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    monkeypatch.setattr(
        module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
        raising=False,
    )
    return lookup_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, module: Any) -> None:
    if hasattr(module, "find_tick"):
        monkeypatch.setattr(module, "find_tick", lambda *, sim_instance: sim_instance.tick)
    judge_tools = getattr(module, "JudgeTools", None)
    if judge_tools is not None:
        monkeypatch.setattr(
            judge_tools,
            "find_tick",
            lambda *, sim_instance: sim_instance.tick,
            raising=False,
        )


class _CalculatorReader:
    def __init__(self, method_name: str, value: float) -> None:
        self._method_name = method_name
        self._value = value

    def __getattr__(self, name: str) -> object:
        if name == self._method_name:
            return lambda _context: self._value
        raise AttributeError(name)


def _install_calculator(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    *,
    method_name: str | None,
    value: float,
) -> None:
    if method_name is None:
        return
    monkeypatch.setattr(
        module,
        "get_calculator_buff_attribute_reader_service",
        lambda: _CalculatorReader(method_name, value),
        raising=False,
    )
    monkeypatch.setattr(
        module,
        "create_calculator_runtime_read_context_from_sim_instance",
        lambda **kwargs: SimpleNamespace(**kwargs),
        raising=False,
    )


class _ActionStack:
    def __init__(self, current: str, previous: str) -> None:
        self._current = SimpleNamespace(mission_tag=current)
        self._previous = SimpleNamespace(mission_tag=previous)

    def peek(self) -> SimpleNamespace:
        return self._current

    def peek_bottom(self) -> SimpleNamespace:
        return self._previous


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: SimpleNamespace,
    char: object,
    enemy: object,
    action_stack: object,
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
        preparation_calls.append(dict(kwargs))
        record = buff_0_ref.history.record
        if kwargs.get("char_CID") is not None:
            record.char = char_ref
        if kwargs.get("enemy") is not None:
            record.enemy = enemy_ref
        if kwargs.get("sub_exist_buff_dict") is not None:
            record.sub_exist_buff_dict = SUB_EXIST_BUFF_DICT
        if kwargs.get("action_stack") is not None:
            record.action_stack = action_stack_ref
        if kwargs.get("trigger_buff_0") is not None:
            record.trigger_buff_0 = SimpleNamespace(dy=SimpleNamespace(active=True))

    buff_0_ref = buff_0
    char_ref = char
    enemy_ref = enemy
    action_stack_ref = action_stack
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _literal_simple_update_scan() -> dict[str, list[dict[str, str]]]:
    literal_rows: list[dict[str, str]] = []
    equipper_rows: list[dict[str, str]] = []
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        if (
            "JudgeTools.find_exist_buff_dict" not in source
            and "ensure_owner_template_record" not in source
            and "ensure_equipper_template_record" not in source
        ):
            continue
        if (
            "simple_start" not in source
            or "update_to_buff_0" not in source
        ):
            continue
        tree = ast.parse(source)
        owners: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript) or not isinstance(node.value, ast.Subscript):
                continue
            owner_node = node.value.slice
            owner: str | None = None
            if isinstance(owner_node, ast.Constant) and isinstance(owner_node.value, str):
                owner = owner_node.value
            elif (
                isinstance(owner_node, ast.Attribute)
                and isinstance(owner_node.value, ast.Name)
                and owner_node.value.id == "self"
                and owner_node.attr == "equipper"
            ):
                owner = "self.equipper"
            if owner is None:
                continue
            if any(
                isinstance(child, ast.Attribute) and child.attr == "find_exist_buff_dict"
                for child in ast.walk(node.value.value)
            ):
                owners.add(owner)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name):
                continue
            if node.func.id == "ensure_owner_template_record" and rel_path in SELECTED_FILES:
                for keyword in node.keywords:
                    if (
                        keyword.arg == "owner_name"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        owners.add(keyword.value.value)
            elif node.func.id == "ensure_equipper_template_record" and rel_path in SELECTED_FILES:
                owners.add("self.equipper")
        for owner in sorted(owners):
            row = {"file": rel_path, "owner": owner}
            if owner == "self.equipper":
                equipper_rows.append(row)
            else:
                literal_rows.append(row)
    return {"literal": literal_rows, "equipper": equipper_rows}


def test_us001_checkpoint_matches_current_bounded_literal_simple_update_census() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    scan = _literal_simple_update_scan()
    selected_files = {entry["file"] for entry in checkpoint["needs_focused_oracle"]}
    scanned_literal_files = {entry["file"] for entry in scan["literal"]}

    assert checkpoint["schema"] == "zsim-existing-buff-literal-simple-update-batch-oracle.v1"
    assert checkpoint["us002_target"] == "existing-buff-literal-simple-update-batch-migration"
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == SELECTED_FILES
    assert selected_files <= scanned_literal_files
    assert checkpoint["scan_summary"]["literal_simple_update_selected_count"] == len(SELECTED_FILES)
    assert checkpoint["scan_summary"]["literal_simple_update_broad_scan_count"] == len(
        scan["literal"]
    )
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_literal_simple_update_check_record_module_pins_owner_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    record_cls = getattr(module, row["record"])
    harness = _RecordingBuffInstance(index="literal-template-index")
    logic = logic_cls(harness)
    template = _buff_0()
    lookup_calls = _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert logic.record is existing_record
    assert template.history.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {"OWNER": {}}])
def test_literal_simple_update_check_record_module_pins_current_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
    registry: dict[str, dict[str, object]],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    harness = _RecordingBuffInstance(index="missing-template-index")
    logic = logic_cls(harness)
    normalized_registry = (
        registry if not registry else {row["owner"]: registry["OWNER"]}
    )
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=_buff_0(),
        registry=normalized_registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


BEHAVIOR_CASES = (
    {
        "module": "JaneCinema1APTransToDmgBonus",
        "logic": "JaneCinema1APTransToDmgBonus",
        "record": "JaneCinema1APTransToDmgBonusRecord",
        "owner": "简",
        "method": "special_hit_logic",
        "calculator": "read_anomaly_proficiency",
        "calculator_value": 250,
        "maxcount": 20,
        "expected_count": 20,
        "expected_preparation": {"char_CID": 1261, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_trigger_ref": ("简", "Buff-角色-简-狂热状态触发器", "owner"),
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {"no_count": 1},
    },
    {
        "module": "JaneCoreSkillStrikeCritRateBonus",
        "logic": "JaneCoreSkillStrikeCritRateBonus",
        "record": "JaneCoreSkillStrikeCritRateBonusRecord",
        "owner": "简",
        "method": "special_hit_logic",
        "calculator": "read_anomaly_proficiency",
        "calculator_value": 300,
        "expected_count": 88,
        "expected_preparation": {"char_CID": 1261, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_trigger_ref": ("enemy", "Buff-角色-简-核心被动-啮咬触发器", "enemy"),
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {"no_count": 1},
    },
    {
        "module": "JanePassionStateAPTransToATK",
        "logic": "JanePassionStateAPTransToATK",
        "record": "JanePassionStateAPTransToATKRecord",
        "owner": "简",
        "method": "special_hit_logic",
        "calculator": "read_anomaly_proficiency",
        "calculator_value": 125.8,
        "expected_count": 5,
        "expected_preparation": {"char_CID": 1261, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_trigger_ref": ("简", "Buff-角色-简-狂热状态触发器", "owner"),
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {"no_count": 1},
    },
    {
        "module": "LighterAdditionalAbility_IceFireBonus",
        "logic": "LighterExtraSkill_IceFireBonus",
        "record": "LighterExtraSkillRecord",
        "owner": "莱特",
        "method": "special_hit_logic",
        "calculator": "read_impact",
        "calculator_value": 190,
        "step": 5,
        "maxcount": 300,
        "expected_count": 7,
        "expected_record": {"real_count": 5},
        "expected_preparation": {"char_CID": 1161, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {},
    },
    {
        "module": "LighterUniqueSkillStunBonus",
        "logic": "LighterUniqueSkillStunBonus",
        "record": "LighterUniqueSkillStunBonusRecord",
        "owner": "莱特",
        "method": "special_effect_logic",
        "calculator": None,
        "calculator_value": 0,
        "initial_record": {"buff_count": 3.5},
        "expected_count": 3.5,
        "expected_preparation": {"char_CID": 1161, "sub_exist_buff_dict": 1},
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {},
    },
    {
        "module": "LinaCoreSkillPenRatioBonus",
        "logic": "LinaCoreSkillPenRatioBonus",
        "record": "LinaCoreSkillRecord",
        "owner": "丽娜",
        "method": "special_start_logic",
        "calculator": "read_pen_ratio",
        "calculator_value": 0.5,
        "expected_count": 22,
        "expected_preparation": {
            "action_stack": 1,
            "char_CID": 1211,
            "enemy": 1,
            "sub_exist_buff_dict": 1,
        },
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {},
    },
    {
        "module": "QingYiAdditionalAbilityStunConvertToATK",
        "logic": "QingYiAdditionalAbilityStunConvertToATK",
        "record": "QingYiAdditionalSkillRecord",
        "owner": "青衣",
        "method": "special_hit_logic",
        "calculator": "read_impact",
        "calculator_value": 150,
        "maxcount": 200,
        "expected_count": 180,
        "expected_preparation": {"char_CID": 1251, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {},
    },
    {
        "module": "QingYiCoreSkillStunDMGBonus",
        "logic": "QingYiCoreSkillStunDMGBonus",
        "record": "QintYiCoreSkillRecord",
        "owner": "青衣",
        "method": "special_start_logic",
        "calculator": None,
        "calculator_value": 0,
        "buff0_count": 7,
        "action_stack_current": "1251_SNA_1",
        "action_stack_previous": "1251_EX",
        "expected_count": 7,
        "expected_record": {"pre_saved_counts": 1},
        "expected_preparation": {"char_CID": 1251, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {},
    },
    {
        "module": "SokakuUniqueSkillMinorATKBonus",
        "logic": "SokakuUniqueSkillMinorATKBonus",
        "record": "SokakuUniqueSkillMinorATKRecord",
        "owner": "苍角",
        "method": "special_start_logic",
        "calculator": None,
        "calculator_value": 0,
        "char": SimpleNamespace(statement=SimpleNamespace(ATK=3000), cinema=0),
        "expected_count": 500,
        "expected_preparation": {"char_CID": 1131, "sub_exist_buff_dict": 1},
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {},
    },
    {
        "module": "TriggerAdditionalAbilityStunBonus",
        "logic": "TriggerAdditionalAbilityStunBonus",
        "record": "TriggerAdditionalAbilityStunBonusRecord",
        "owner": "扳机",
        "method": "special_hit_logic",
        "calculator": "read_personal_crit_rate",
        "calculator_value": 0.6,
        "expected_count": 30,
        "expected_preparation": {"char_CID": 1361, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_simple_args": (TICK_NOW, SUB_EXIST_BUFF_DICT),
        "expected_simple_kwargs": {"no_count": 1},
    },
    {
        "module": "YuzuhaAdditionalAbilityAnomalyBuildupBonus",
        "logic": "YuzuhaAdditionalAbilityAnomalyBuildupBonus",
        "record": "YuzuhaAdditionalAbilityAnomalyBuildupBonusRecord",
        "owner": "柚叶",
        "method": "special_hit_logic",
        "calculator": "read_anomaly_mastery",
        "calculator_value": 150,
        "char": SimpleNamespace(statement=SimpleNamespace(ATK=1000), cinema=1),
        "expected_count": 65,
        "expected_record": {"cinema_1_ratio": 1.3},
        "expected_preparation": {"char_CID": 1411, "enemy": 1, "sub_exist_buff_dict": 1},
        "expected_simple_args": (),
        "expected_simple_kwargs": {
            "timenow": TICK_NOW,
            "sub_exist_buff_dict": SUB_EXIST_BUFF_DICT,
            "no_count": 1,
        },
    },
)


@pytest.mark.parametrize("case", BEHAVIOR_CASES)
def test_literal_simple_update_representative_behavior_pins_simple_start_update_and_count(
    monkeypatch: pytest.MonkeyPatch,
    case: dict[str, Any],
) -> None:
    module = importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{case['module']}"
    )
    logic_cls = getattr(module, case["logic"])
    record_cls = getattr(module, case["record"])
    record = record_cls()
    for attr, value in case.get("initial_record", {}).items():
        setattr(record, attr, value)
    buff_0 = _buff_0(
        record=record,
        count=case.get("buff0_count", 0),
        step=case.get("step", 1),
    )
    harness = _RecordingBuffInstance(
        index="literal-template-index",
        step=case.get("step", 1),
        maxcount=case.get("maxcount", 100),
    )
    logic = logic_cls(harness)
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=case["owner"],
        index=harness.ft.index,
        buff_0=buff_0,
    )
    _install_tick(monkeypatch, module)
    _install_calculator(
        monkeypatch,
        module,
        method_name=case.get("calculator"),
        value=case["calculator_value"],
    )
    action_stack = _ActionStack(
        case.get("action_stack_current", "1251_SNA_1"),
        case.get("action_stack_previous", "1251_EX"),
    )
    judge_tools = getattr(module, "JudgeTools", None)
    if judge_tools is not None:
        monkeypatch.setattr(
            judge_tools,
            "find_stack",
            lambda *, sim_instance: action_stack,
            raising=False,
        )
    char = case.get("char", SimpleNamespace(statement=SimpleNamespace(ATK=1000), cinema=0))
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=buff_0,
        char=char,
        enemy=SimpleNamespace(marker="enemy"),
        action_stack=action_stack,
    )

    getattr(logic, case["method"])()

    assert len(preparation_calls) == 1
    actual_preparation = preparation_calls[0]
    for key, expected in case["expected_preparation"].items():
        assert actual_preparation[key] == expected
    if "expected_trigger_ref" in case:
        trigger_ref = actual_preparation["trigger_buff_0"]
        assert (
            trigger_ref.operator,
            trigger_ref.buff_index,
            trigger_ref.operator_kind,
        ) == case["expected_trigger_ref"]
    else:
        assert "trigger_buff_0" not in actual_preparation
    assert harness.simple_start_calls == [
        (case["expected_simple_args"], case["expected_simple_kwargs"])
    ]
    assert harness.dy.count == pytest.approx(case["expected_count"])
    assert len(harness.update_to_buff_0_calls) == 1
    args, kwargs = harness.update_to_buff_0_calls[0]
    updated_buff_0 = args[0] if args else kwargs["buff_0"]
    assert updated_buff_0 is buff_0
    for attr, expected in case.get("expected_record", {}).items():
        assert getattr(record, attr) == pytest.approx(expected)
