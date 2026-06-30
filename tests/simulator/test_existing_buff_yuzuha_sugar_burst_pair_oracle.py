from __future__ import annotations

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
    / "2026-06-30-US-001-existing-buff-yuzuha-sugar-burst-pair-oracle.json"
)

OWNER = "柚叶"

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YuzuhaSugarBurstAnomalyBuildupBonus.py",
        "module": "YuzuhaSugarBurstAnomalyBuildupBonus",
        "logic": "YuzuhaSugarBurstAnomalyBuildupBonus",
        "record": "YuzuhaSugarBurstAnomalyBuildupBonusRecord",
        "skill_tag": "1411_SNA_A",
        "index": "Buff-角色-柚叶-彩糖花火积蓄值提升",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YuzuhaSugarBurstMaxAnomalyBuildupBonus.py",
        "module": "YuzuhaSugarBurstMaxAnomalyBuildupBonus",
        "logic": "YuzuhaSugarBurstMaxAnomalyBuildupBonus",
        "record": "YuzuhaSugarBurstMaxAnomalyBuildupBonusRecord",
        "skill_tag": "1411_SNA_B",
        "index": "Buff-角色-柚叶-彩糖花火·极积蓄值提升",
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema2StunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaTanukiWishAtkBonus.py",
)


def _module(row: dict[str, object]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


class _TemplateBuff:
    def __init__(self, *, record: object | None = None) -> None:
        self.history = SimpleNamespace(record=record)


class _RecordingBuffInstance:
    def __init__(self, *, index: str, tick: int = 1800) -> None:
        self.sim_instance = SimpleNamespace(tick=tick)
        self.ft = SimpleNamespace(index=index, maxcount=999)
        self.dy = SimpleNamespace(count=0)
        self.simple_start_calls: list[dict[str, object]] = []
        self.update_to_buff_0_calls: list[object] = []

    def simple_start(
        self,
        *,
        timenow: int,
        sub_exist_buff_dict: dict[str, object],
        **kwargs: object,
    ) -> None:
        call = {"timenow": timenow, "sub_exist_buff_dict": sub_exist_buff_dict}
        call.update(kwargs)
        self.simple_start_calls.append(call)

    def update_to_buff_0(self, *, buff_0: object) -> None:
        self.update_to_buff_0_calls.append(buff_0)


class _SkillNodeProbe:
    def __init__(self, *, skill_tag: str, preload_tick: int) -> None:
        self.skill_tag = skill_tag
        self.preload_tick = preload_tick


def _install_existing_buff_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    owner: str,
    index: str,
    buff_0: _TemplateBuff,
    registry: dict[str, dict[str, object]] | None = None,
) -> list[object]:
    lookup_calls: list[object] = []
    lookup_registry = registry if registry is not None else {owner: {index: buff_0}}

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        lookup_calls.append(sim_instance)
        return lookup_registry

    class _FakePreparationContext:
        def __init__(self, sim_instance: object) -> None:
            self.sim_instance = sim_instance

        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            return fake_find_exist_buff_dict(sim_instance=self.sim_instance)[owner_name]

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakePreparationContext:
        return _FakePreparationContext(buff_instance.sim_instance)

    if hasattr(module, "JudgeTools"):
        monkeypatch.setattr(
            module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict
        )
    monkeypatch.setattr(
        module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
        raising=False,
    )
    return lookup_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: _TemplateBuff,
    na_skill_level: int = 8,
    sub_exist_buff_dict: dict[str, object] | None = None,
    raises: Exception | None = None,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []
    buff_0_ref = buff_0
    sub_dict = sub_exist_buff_dict if sub_exist_buff_dict is not None else {}

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
        buff_0_ref.history.record.na_skill_level = na_skill_level
        buff_0_ref.history.record.sub_exist_buff_dict = sub_dict

    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _yuzuha_sugar_burst_scan() -> list[str]:
    rows: list[str] = []
    required_terms = (
        "ensure_owner_template_record(",
        'owner_name="柚叶"',
        "prepare_with_context(",
        "build_preparation_context_from_buff",
        "get_prepared(char_CID=1411)",
        "get_prepared(char_CID=1411, na_skill_level=1, sub_exist_buff_dict=1)",
        "skill_node.preload_tick != self.buff_instance.sim_instance.tick",
        "simple_start(",
        "no_count=1",
        "basic_count",
        "count_growth_per_level",
        "update_to_buff_0(buff_0=self.buff_0)",
    )
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if all(term in source for term in required_terms):
            rows.append(path.relative_to(PROJECT_ROOT).as_posix())
    return rows


def test_us001_checkpoint_rows_match_current_yuzuha_sugar_burst_census() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))

    assert checkpoint["schema"] == (
        "zsim-existing-buff-yuzuha-sugar-burst-pair-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-yuzuha-sugar-burst-pair-migration"
    )
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert tuple(entry["file"] for entry in checkpoint["excluded_or_deferred"][:6]) == (
        EXCLUDED_OR_DEFERRED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 2
    assert checkpoint["scan_summary"]["bounded_yuzuha_sugar_burst_count"] == 2
    assert checkpoint["scan_summary"]["bounded_yuzuha_sugar_burst_rows"] == list(
        SELECTED_FILES
    )
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []
    assert checkpoint["us002_target_allowed_values"] == [
        "existing-buff-yuzuha-sugar-burst-pair-migration",
        "none-safe-to-implement",
    ]
    assert _yuzuha_sugar_burst_scan() == list(SELECTED_FILES)


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_yuzuha_sugar_burst_check_record_module_pins_owner_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    record_cls = getattr(module, str(row["record"]))
    harness = _RecordingBuffInstance(index=str(row["index"]))
    logic = logic_cls(harness)
    template = _TemplateBuff()
    lookup_calls = _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
        index=harness.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record
    assert logic.record.skill_tag == row["skill_tag"]

    existing_record = logic.record
    logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert logic.record is existing_record
    assert template.history.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {OWNER: {}}])
def test_yuzuha_sugar_burst_check_record_module_pins_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
    registry: dict[str, dict[str, object]],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index="missing-template-index")
    logic = logic_cls(harness)
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
        index=harness.ft.index,
        buff_0=_TemplateBuff(),
        registry=registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_yuzuha_sugar_burst_judge_pins_preparation_skill_tag_and_preload_tick(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=1800)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
    )

    matching_skill = _SkillNodeProbe(skill_tag=str(row["skill_tag"]), preload_tick=1800)
    assert logic.special_judge_logic(skill_node=matching_skill) is True

    wrong_tag = _SkillNodeProbe(skill_tag="1411_OTHER", preload_tick=1800)
    assert logic.special_judge_logic(skill_node=wrong_tag) is False

    wrong_tick = _SkillNodeProbe(skill_tag=str(row["skill_tag"]), preload_tick=1799)
    assert logic.special_judge_logic(skill_node=wrong_tick) is False

    assert logic.special_judge_logic() is False
    assert preparation_calls == [{"char_CID": 1411}] * 4
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_yuzuha_sugar_burst_hit_pins_simple_start_count_formula_and_update(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=2040)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    sub_exist_buff_dict = {harness.ft.index: template}
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        na_skill_level=8,
        sub_exist_buff_dict=sub_exist_buff_dict,
    )

    logic.special_hit_logic()

    assert preparation_calls == [
        {"char_CID": 1411, "na_skill_level": 1, "sub_exist_buff_dict": 1}
    ]
    assert harness.simple_start_calls == [
        {
            "timenow": 2040,
            "sub_exist_buff_dict": sub_exist_buff_dict,
            "no_count": 1,
        }
    ]
    assert harness.dy.count == 18.0
    assert harness.update_to_buff_0_calls == [template]


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("method", ["judge", "hit"])
def test_yuzuha_sugar_burst_preparation_errors_propagate_before_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
    method: str,
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=1800)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
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
        if method == "judge":
            skill_node = _SkillNodeProbe(
                skill_tag=str(row["skill_tag"]), preload_tick=1800
            )
            logic.special_judge_logic(skill_node=skill_node)
        else:
            logic.special_hit_logic()

    assert preparation_calls in (
        [{"char_CID": 1411}],
        [{"char_CID": 1411, "na_skill_level": 1, "sub_exist_buff_dict": 1}],
    )
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
