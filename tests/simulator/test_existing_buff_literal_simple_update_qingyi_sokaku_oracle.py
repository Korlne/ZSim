from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TICK_NOW = 2468
SUB_EXIST_BUFF_DICT = {"sub": "registry"}

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/QingYiCoreSkillExtraStunBonus.py",
        "module": "QingYiCoreSkillExtraStunBonus",
        "logic": "QingYiCoreSkillExtraStunBonus",
        "record": "QintYiCoreSkillExtraStunRecord",
        "owner": "青衣",
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/SokakuUniqueSkillMajorATKBonus.py",
        "module": "SokakuUniqueSkillMajorATKBonus",
        "logic": "SokakuUniqueSkillMajorATKBonus",
        "record": "SokakuAdditionalAbilityATKRecord",
        "owner": "苍角",
    },
)


def _module(row: dict[str, str]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


def _template_buff(*, record: object | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        history=SimpleNamespace(record=record),
        dy=SimpleNamespace(count=0, active=False),
        ft=SimpleNamespace(step=1),
    )


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str = "literal-template-index",
        tick: int = TICK_NOW,
        maxcount: float = 100,
    ) -> None:
        self.sim_instance = SimpleNamespace(tick=tick)
        self.ft = SimpleNamespace(index=index, maxcount=maxcount)
        self.dy = SimpleNamespace(count=0, active=False)
        self.call_order: list[str] = []
        self.simple_start_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.update_to_buff_0_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def simple_start(self, *args: object, **kwargs: object) -> None:
        self.call_order.append("simple_start")
        self.simple_start_calls.append((args, dict(kwargs)))

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        self.call_order.append("update_to_buff_0")
        self.update_to_buff_0_calls.append((args, dict(kwargs)))


class _ActionStack:
    def __init__(self, mission_tag: str) -> None:
        self._current = SimpleNamespace(mission_tag=mission_tag)

    def peek(self) -> SimpleNamespace:
        return self._current


class _CharacterProbe:
    def __init__(self, *, atk: float = 3000, resource: float = 90) -> None:
        self.statement = SimpleNamespace(ATK=atk)
        self._resource = resource

    def get_resources(self) -> tuple[object, float]:
        return (None, self._resource)


def _install_owner_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    owner: str,
    index: str,
    buff_0: SimpleNamespace,
    registry: dict[str, dict[str, object]] | None = None,
) -> tuple[list[object], list[tuple[str, object]]]:
    direct_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []
    lookup_registry = registry if registry is not None else {owner: {index: buff_0}}

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        direct_calls.append(sim_instance)
        return lookup_registry

    class _FakePreparationContext:
        def __init__(self, sim_instance: object) -> None:
            self.sim_instance = sim_instance

        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            context_calls.append((owner_name, self.sim_instance))
            return lookup_registry[owner_name]

    def fake_build_preparation_context_from_buff(
        buff_instance: object,
    ) -> _FakePreparationContext:
        return _FakePreparationContext(buff_instance.sim_instance)

    monkeypatch.setattr(
        module.JudgeTools,
        "find_exist_buff_dict",
        fake_find_exist_buff_dict,
        raising=False,
    )
    monkeypatch.setattr(
        module,
        "build_preparation_context_from_buff",
        fake_build_preparation_context_from_buff,
        raising=False,
    )
    return direct_calls, context_calls


def _install_tick(monkeypatch: pytest.MonkeyPatch, module: Any) -> None:
    monkeypatch.setattr(
        module.JudgeTools,
        "find_tick",
        lambda *, sim_instance: sim_instance.tick,
        raising=False,
    )


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: SimpleNamespace,
    char: object,
    action_stack: object,
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
        observed = dict(kwargs)
        observed.pop("preparation_context", None)
        preparation_calls.append(observed)
        if raises is not None:
            raise raises
        record = buff_0_ref.history.record
        if kwargs.get("char_CID") is not None:
            record.char = char_ref
        if kwargs.get("action_stack") is not None:
            record.action_stack = action_stack_ref
        if kwargs.get("sub_exist_buff_dict") is not None:
            record.sub_exist_buff_dict = SUB_EXIST_BUFF_DICT

    buff_0_ref = buff_0
    char_ref = char
    action_stack_ref = action_stack
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_selected_check_record_module_pins_owner_index_and_record_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    record_cls = getattr(module, row["record"])
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    template = _template_buff()
    direct_calls, context_calls = _install_owner_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    assert (direct_calls, context_calls) in (
        ([harness.sim_instance], []),
        ([], [(row["owner"], harness.sim_instance)]),
    )
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    assert logic.record is existing_record
    assert template.history.record is existing_record
    assert (direct_calls, context_calls) in (
        ([harness.sim_instance], []),
        ([], [(row["owner"], harness.sim_instance)]),
    )


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {"OWNER": {}}])
def test_selected_check_record_module_preserves_missing_owner_or_index_errors(
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
    _install_owner_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=_template_buff(),
        registry=normalized_registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


def test_qingyi_start_preserves_preparation_simple_start_update_order_and_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    template = _template_buff()
    harness = _RecordingBuffInstance(maxcount=100)
    logic = module.QingYiCoreSkillExtraStunBonus(harness)
    _install_owner_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=template,
    )
    _install_tick(monkeypatch, module)
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=_CharacterProbe(resource=90),
        action_stack=_ActionStack("1251_SNA_1"),
    )

    logic.check_record_module()
    logic.record.count = 46
    logic.special_start_logic()

    assert preparation_calls == [
        {"char_CID": 1251, "sub_exist_buff_dict": 1, "action_stack": 1}
    ]
    assert harness.simple_start_calls == [((TICK_NOW, SUB_EXIST_BUFF_DICT), {})]
    assert template.dy.count == -1
    assert harness.dy.count == 45
    assert harness.update_to_buff_0_calls == [((template,), {})]
    assert harness.call_order == ["simple_start", "update_to_buff_0"]


def test_sokaku_start_preserves_preparation_simple_start_update_order_and_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    template = _template_buff()
    harness = _RecordingBuffInstance(maxcount=1000)
    logic = module.SokakuUniqueSkillMajorATKBonus(harness)
    _install_owner_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=template,
    )
    _install_tick(monkeypatch, module)
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=_CharacterProbe(atk=3000),
        action_stack=_ActionStack("1131_E_EX_A"),
    )

    logic.special_start_logic()

    assert preparation_calls == [{"char_CID": 1131, "sub_exist_buff_dict": 1}]
    assert harness.simple_start_calls == [((TICK_NOW, SUB_EXIST_BUFF_DICT), {})]
    assert harness.dy.count == 500
    assert harness.update_to_buff_0_calls == [((template,), {})]
    assert harness.call_order == ["simple_start", "update_to_buff_0"]


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_selected_start_propagates_preparation_errors_before_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, str],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, row["logic"])
    template = _template_buff()
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    _install_owner_lookup(
        monkeypatch,
        module=module,
        owner=row["owner"],
        index=harness.ft.index,
        buff_0=template,
    )
    _install_tick(monkeypatch, module)
    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=_CharacterProbe(),
        action_stack=_ActionStack("1251_SNA_1"),
        raises=RuntimeError("missing preparation"),
    )

    with pytest.raises(RuntimeError, match="missing preparation"):
        logic.special_start_logic()

    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
    assert harness.call_order == []


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_selected_files_keep_either_legacy_or_preparation_helper_lookup_shape(
    row: dict[str, str],
) -> None:
    source = (PROJECT_ROOT / row["file"]).read_text(encoding="utf-8")
    if "JudgeTools.find_exist_buff_dict" in source:
        assert f"[\"{row['owner']}\"][self.buff_instance.ft.index]" in source
    else:
        assert "prepare_with_context(" in source
        assert "ensure_owner_template_record(" in source
        assert "build_preparation_context_from_buff" in source
        assert f"owner_name=\"{row['owner']}\"" in source
