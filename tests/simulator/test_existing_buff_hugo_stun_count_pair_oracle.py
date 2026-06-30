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
    / "2026-06-30-US-001-existing-buff-hugo-stun-count-pair-oracle.json"
)

OWNER = "雨果"

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveSingleStunAtkBonus.py",
        "module": "HugoCorePassiveSingleStunAtkBonus",
        "logic": "HugoCorePassiveSingleStunAtkBonus",
        "record": "HugoCorePassiveSingleStunAtkBonusRecord",
        "threshold": 1,
        "report_label": "单击破角色攻击力Buff",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveDoubleStunAtkBonus.py",
        "module": "HugoCorePassiveDoubleStunAtkBonus",
        "logic": "HugoCorePassiveDoubleStunAtkBonus",
        "record": "HugoCorePassiveDoubleStunAtkBonusRecord",
        "threshold": 2,
        "report_label": "双击破角色攻击力Buff",
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema2StunTimeLimitBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaSugarBurstAnomalyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaSugarBurstMaxAnomalyBuildupBonus.py",
)


def _module(row: dict[str, object]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


class _TemplateBuff:
    def __init__(self, *, record: object | None = None) -> None:
        self.history = SimpleNamespace(record=record)


class _RecordingScheduleData:
    def __init__(self) -> None:
        self.change_process_state_calls = 0

    def change_process_state(self) -> None:
        self.change_process_state_calls += 1


class _RecordingBuffInstance:
    def __init__(self, *, index: str = "hugo-template-index") -> None:
        self.schedule_data = _RecordingScheduleData()
        self.sim_instance = SimpleNamespace(schedule_data=self.schedule_data)
        self.ft = SimpleNamespace(index=index)


class _FakeCharacter:
    def __init__(self, specialty: str) -> None:
        self.specialty = specialty


def _install_character_type(monkeypatch: pytest.MonkeyPatch) -> None:
    character_package = importlib.import_module("zsim.sim_progress.Character")
    monkeypatch.setattr(character_package, "Character", _FakeCharacter)


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
    char_obj_list_ref: dict[str, list[object]],
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
        buff_0_ref.history.record.char_obj_list = char_obj_list_ref["value"]

    buff_0_ref = buff_0
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _hugo_stun_count_helper_scan() -> list[str]:
    rows: list[str] = []
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if (
            'owner_name="雨果"' in source
            and "ensure_owner_template_record" in source
            and "prepare_with_context" in source
            and "get_prepared(char_CID=1291, char_obj_list=1)" in source
            and "stun_char_count" in source
        ):
            rows.append(path.relative_to(PROJECT_ROOT).as_posix())
    return rows


def test_us001_checkpoint_rows_match_current_hugo_helper_migration() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))

    assert checkpoint["schema"] == "zsim-existing-buff-hugo-stun-count-pair-oracle.v1"
    assert checkpoint["safe_mechanical"] == []
    assert checkpoint["us002_target"] == "existing-buff-hugo-stun-count-pair-migration"
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert tuple(entry["file"] for entry in checkpoint["excluded_or_deferred"][:6]) == (
        EXCLUDED_OR_DEFERRED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 2
    assert checkpoint["scan_summary"]["bounded_hugo_stun_count"] == 2
    assert checkpoint["scan_summary"]["bounded_hugo_stun_count_rows"] == list(
        SELECTED_FILES
    )
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []
    assert checkpoint["us002_target_allowed_values"] == [
        "existing-buff-hugo-stun-count-pair-migration",
        "none-safe-to-implement",
    ]
    scan = _hugo_stun_count_helper_scan()
    assert len(scan) == len(SELECTED_FILES)
    assert set(scan) == set(SELECTED_FILES)


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_hugo_check_record_module_pins_owner_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    record_cls = getattr(module, str(row["record"]))
    harness = _RecordingBuffInstance(index="hugo-template-index")
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

    existing_record = logic.record
    logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert logic.record is existing_record
    assert template.history.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {OWNER: {}}])
def test_hugo_check_record_module_pins_current_missing_owner_or_index_errors(
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
def test_hugo_judge_pins_preparation_kwargs_cached_stun_count_and_thresholds(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    _install_character_type(monkeypatch)
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
        index=harness.ft.index,
        buff_0=template,
    )
    char_obj_list_ref = {
        "value": [_FakeCharacter("击破"), _FakeCharacter("强攻")]
    }
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char_obj_list_ref=char_obj_list_ref,
    )

    assert logic.special_judge_logic() is (row["threshold"] == 1)
    assert logic.record.stun_char_count == 1
    assert preparation_calls == [{"char_CID": 1291, "char_obj_list": 1}]

    char_obj_list_ref["value"] = [_FakeCharacter("击破"), _FakeCharacter("击破")]
    assert logic.special_judge_logic() is (row["threshold"] == 1)
    assert logic.record.stun_char_count == 1
    assert preparation_calls == [
        {"char_CID": 1291, "char_obj_list": 1},
        {"char_CID": 1291, "char_obj_list": 1},
    ]

    logic.record.stun_char_count = None
    assert logic.special_judge_logic() is True
    assert logic.record.stun_char_count == 2


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_hugo_judge_pins_report_state_behavior(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    row: dict[str, object],
) -> None:
    _install_character_type(monkeypatch)
    module = _module(row)
    monkeypatch.setattr(module, "HUGO_REPORT", True)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance()
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
        char_obj_list_ref={
            "value": [_FakeCharacter("击破"), _FakeCharacter("击破")]
        },
    )

    assert logic.special_judge_logic() is True
    captured = capsys.readouterr()

    assert harness.schedule_data.change_process_state_calls == 1
    assert str(row["report_label"]) in captured.out
    assert "2名击破角色" in captured.out
    assert preparation_calls == [{"char_CID": 1291, "char_obj_list": 1}]

    assert logic.special_judge_logic() is True
    captured = capsys.readouterr()

    assert harness.schedule_data.change_process_state_calls == 1
    assert captured.out == ""


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_hugo_judge_pins_preparation_and_character_type_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    _install_character_type(monkeypatch)
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=OWNER,
        index=harness.ft.index,
        buff_0=template,
    )
    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char_obj_list_ref={"value": []},
        raises=RuntimeError("missing preparation"),
    )

    with pytest.raises(RuntimeError, match="missing preparation"):
        logic.special_judge_logic()

    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char_obj_list_ref={"value": [object()]},
    )

    with pytest.raises(TypeError, match="char_obj_list"):
        logic.special_judge_logic()
