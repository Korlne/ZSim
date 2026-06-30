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
    / "2026-06-30-US-001-existing-buff-yuzuha-hit-update-pair-oracle.json"
)

OWNER = "柚叶"

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
        "module": "YuzuhaAdditionalAbilityAnomalyDmgBonus",
        "logic": "YuzuhaAdditionalAbilityAnomalyDmgBonus",
        "record": "YuzuhaAdditionalAbilityAnomalyDmgBonusRecord",
        "index": "Buff-角色-柚叶-狸之愿-异常增伤",
        "prepared": {"char_CID": 1411, "sub_exist_buff_dict": 1, "enemy": 1},
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YuzuhaTanukiWishAtkBonus.py",
        "module": "YuzuhaTanukiWishAtkBonus",
        "logic": "YuzuhaTanukiWishAtkBonus",
        "record": "YuzuhaTanukiWishAtkBonusRecord",
        "index": "Buff-角色-柚叶-狸之愿-攻击力",
        "prepared": {"char_CID": 1411, "sub_exist_buff_dict": 1},
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)


def _module(row: dict[str, object]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


class _TemplateBuff:
    def __init__(self, *, record: object | None = None) -> None:
        self.history = SimpleNamespace(record=record)


class _ScheduleDataProbe:
    def __init__(self) -> None:
        self.change_process_state_calls = 0

    def change_process_state(self) -> None:
        self.change_process_state_calls += 1


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str,
        tick: int = 1800,
        maxcount: float = 999.0,
    ) -> None:
        self.schedule_data = _ScheduleDataProbe()
        self.sim_instance = SimpleNamespace(tick=tick, schedule_data=self.schedule_data)
        self.ft = SimpleNamespace(index=index, maxcount=maxcount)
        self.dy = SimpleNamespace(count=0.0)
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

    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict)
    return lookup_calls


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: _TemplateBuff,
    char: object,
    sub_exist_buff_dict: dict[str, object],
    enemy: object | None = None,
    raises: Exception | None = None,
) -> list[dict[str, object]]:
    preparation_calls: list[dict[str, object]] = []
    expected_buff_0 = buff_0

    def fake_check_preparation(
        *,
        buff_instance: object,
        buff_0: object,
        **kwargs: object,
    ) -> None:
        assert buff_instance is harness
        assert buff_0 is expected_buff_0
        preparation_calls.append(dict(kwargs))
        if raises is not None:
            raise raises
        record = expected_buff_0.history.record
        record.char = char
        record.sub_exist_buff_dict = sub_exist_buff_dict
        if enemy is not None:
            record.enemy = enemy

    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


class _AnomalyReaderProbe:
    def __init__(self, values: list[float]) -> None:
        self.values = values
        self.read_calls: list[object] = []

    def read_anomaly_mastery(self, context: object) -> float:
        self.read_calls.append(context)
        return self.values.pop(0)


def _install_anomaly_reader(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    am_values: list[float],
) -> tuple[_AnomalyReaderProbe, list[dict[str, object]]]:
    context_calls: list[dict[str, object]] = []
    reader = _AnomalyReaderProbe(am_values)

    def fake_create_context(
        *,
        sim_instance: object,
        enemy: object,
        character: object,
    ) -> object:
        context = {
            "sim_instance": sim_instance,
            "enemy": enemy,
            "character": character,
        }
        context_calls.append(context)
        return context

    monkeypatch.setattr(
        module,
        "create_calculator_runtime_read_context_from_sim_instance",
        fake_create_context,
    )
    monkeypatch.setattr(
        module,
        "get_calculator_buff_attribute_reader_service",
        lambda: reader,
    )
    return reader, context_calls


def _hit_update_scan() -> list[str]:
    rows: list[str] = []
    base_terms = (
        "JudgeTools.find_exist_buff_dict",
        '"柚叶"',
        "self.buff_instance.ft.index",
        "get_prepared(char_CID=1411, sub_exist_buff_dict=1",
        "simple_start(",
        "no_count=1",
        "update_to_buff_0(buff_0=self.buff_0)",
        "YUZUHA_REPORT",
    )
    formula_term_sets = (
        ("read_anomaly_mastery", "cinema_1_ratio"),
        ("statement.ATK", "core_passive_ratio"),
    )
    for path in sorted(BUFFXLOGIC_ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if all(term in source for term in base_terms) and any(
            all(term in source for term in formula_terms)
            for formula_terms in formula_term_sets
        ):
            rows.append(path.relative_to(PROJECT_ROOT).as_posix())
    return rows


def test_us001_checkpoint_rows_match_current_yuzuha_hit_update_census() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))

    assert checkpoint["schema"] == (
        "zsim-existing-buff-yuzuha-hit-update-pair-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-yuzuha-hit-update-pair-migration"
    )
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 2
    assert checkpoint["scan_summary"]["bounded_yuzuha_hit_update_count"] == 2
    assert checkpoint["scan_summary"]["bounded_yuzuha_hit_update_rows"] == list(
        SELECTED_FILES
    )
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []
    assert checkpoint["us002_target_allowed_values"] == [
        "existing-buff-yuzuha-hit-update-pair-migration",
        "none-safe-to-implement",
    ]
    assert _hit_update_scan() == list(SELECTED_FILES)


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_yuzuha_hit_update_check_record_module_pins_owner_index_and_record_identity(
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

    existing_record = logic.record
    logic.check_record_module()

    assert lookup_calls == [harness.sim_instance]
    assert logic.record is existing_record
    assert template.history.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {OWNER: {}}])
def test_yuzuha_hit_update_check_record_module_pins_missing_owner_or_index_errors(
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


def test_yuzuha_anomaly_damage_pins_calculator_path_cinema_cache_simple_start_and_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=2040)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    sub_exist_buff_dict = {harness.ft.index: template}
    char = SimpleNamespace(cinema=2)
    enemy = object()
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
        char=char,
        enemy=enemy,
        sub_exist_buff_dict=sub_exist_buff_dict,
    )
    reader, context_calls = _install_anomaly_reader(
        monkeypatch,
        module=module,
        am_values=[145.0, 250.0],
    )
    monkeypatch.setattr(module, "YUZUHA_REPORT", True)

    logic.special_hit_logic()
    char.cinema = 0
    logic.special_hit_logic()

    assert preparation_calls == [row["prepared"], row["prepared"]]
    assert context_calls == [
        {"sim_instance": harness.sim_instance, "enemy": enemy, "character": char},
        {"sim_instance": harness.sim_instance, "enemy": enemy, "character": char},
    ]
    assert reader.read_calls == context_calls
    assert template.history.record.cinema_1_ratio == pytest.approx(1.3)
    assert harness.simple_start_calls == [
        {
            "timenow": 2040,
            "sub_exist_buff_dict": sub_exist_buff_dict,
            "no_count": 1,
        },
        {
            "timenow": 2040,
            "sub_exist_buff_dict": sub_exist_buff_dict,
            "no_count": 1,
        },
    ]
    assert harness.dy.count == pytest.approx(130.0)
    assert harness.update_to_buff_0_calls == [template, template]
    assert harness.schedule_data.change_process_state_calls == 2
    assert "异常掌控" in capsys.readouterr().out


def test_yuzuha_anomaly_damage_below_am_threshold_skips_update_after_reader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=2040)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    char = SimpleNamespace(cinema=0)
    enemy = object()
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
        char=char,
        enemy=enemy,
        sub_exist_buff_dict={harness.ft.index: template},
    )
    reader, context_calls = _install_anomaly_reader(
        monkeypatch,
        module=module,
        am_values=[99.99],
    )

    assert logic.special_hit_logic() is None

    assert preparation_calls == [row["prepared"]]
    assert reader.read_calls == context_calls
    assert template.history.record.cinema_1_ratio == pytest.approx(1.0)
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
    assert harness.schedule_data.change_process_state_calls == 0


def test_yuzuha_tanuki_wish_pins_static_atk_count_cap_simple_start_and_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=2060, maxcount=300.0)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    sub_exist_buff_dict = {harness.ft.index: template}
    char = SimpleNamespace(statement=SimpleNamespace(ATK=1000.0))
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
        char=char,
        sub_exist_buff_dict=sub_exist_buff_dict,
    )
    monkeypatch.setattr(module, "YUZUHA_REPORT", True)

    logic.special_hit_logic()

    assert preparation_calls == [row["prepared"]]
    assert template.history.record.core_passive_ratio == pytest.approx(0.4)
    assert harness.simple_start_calls == [
        {
            "timenow": 2060,
            "sub_exist_buff_dict": sub_exist_buff_dict,
            "no_count": 1,
        }
    ]
    assert harness.dy.count == pytest.approx(300.0)
    assert harness.update_to_buff_0_calls == [template]
    assert harness.schedule_data.change_process_state_calls == 1
    assert "场外站街攻击力" in capsys.readouterr().out


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_yuzuha_hit_update_preparation_errors_propagate_before_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index=str(row["index"]), tick=1800)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    char = SimpleNamespace(cinema=0, statement=SimpleNamespace(ATK=1000.0))
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
        char=char,
        enemy=object(),
        sub_exist_buff_dict={harness.ft.index: template},
        raises=RuntimeError("missing preparation"),
    )

    with pytest.raises(RuntimeError, match="missing preparation"):
        logic.special_hit_logic()

    assert preparation_calls == [row["prepared"]]
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
    assert harness.schedule_data.change_process_state_calls == 0
