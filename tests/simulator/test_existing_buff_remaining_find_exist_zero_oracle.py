from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFXLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"

LITERAL_ROWS = (
    ("HugoCorePassiveTotalizeTrigger", "HugoCorePassiveTotalizeTrigger", "HugoCorePassiveTotalizeTriggerRecord", "雨果"),
    ("MiyabiCoreSkill_IceFire", "MiyabiCoreSkill_IceFire", "MiyabiCoreSkillIF", "雅"),
    ("SeedCinema6Trigger", "SeedCinema6Trigger", "SeedCinema6TriggerRecord", "席德"),
    ("SokakuAdditionalAbilityICEBonus", "SokakuAdditionalAbilityICEBonus", "SokakuAdditionalAbilityIBRecord", "苍角"),
    ("Soldier0AnbyCoreSkillDMGBonus", "Soldier0AnbyCoreSkillDMGBonus", "Soldier0AnbyCoreSkillDMGBonusRecord", "零号·安比"),
    ("Soldier0AnbySilverStarTrigger", "Soldier0AnbySilverStarTrigger", "Soldier0AnbySilverStarTriggerRecord", "零号·安比"),
    ("TriggerAfterShockTrigger", "TriggerAfterShockTrigger", "TriggerAfterShockTriggerRecord", "扳机"),
    ("VivianAdditionalAbilityCoAttackTrigger", "VivianAdditionalAbilityCoAttackTrigger", "VivianAdditionalAbilityCoAttackTriggerRecord", "薇薇安"),
    ("VivianCinema6Trigger", "VivianCinema6Trigger", "VivianCinema6TriggerRecord", "薇薇安"),
    ("VivianCoattackTrigger", "VivianCoattackTrigger", "VivianCoattackTriggerRecord", "薇薇安"),
    ("VivianFeatherTrigger", "VivianFeatherTrigger", "VivianFeatherTriggerRecord", "薇薇安"),
    ("YanagiPolarityDisorderTrigger", "YanagiPolarityDisorderTrigger", "YanagiPolarityDisorderTriggerRecord", "柳"),
    ("YixuanAdditionalAbilityDmgBonus", "YixuanAdditionalAbilityDmgBonus", "YixuanAdditionalAbilityDmgBonusRecord", "仪玄"),
    ("YixuanCinema1Trigger", "YixuanCinema1Trigger", "YixuanCinema1TriggerRecord", "仪玄"),
    ("YixuanCinema4Tranquility", "YixuanCinema4Tranquility", "YixuanCinema4TranquilityRecord", "仪玄"),
    ("YuzuhaCinema4QuickAssistTrigger", "YuzuhaCinema4QuickAssistTrigger", "YuzuhaCinema4QuickAssistTriggerRecord", "柚叶"),
    ("YuzuhaCinema6SheelTrigger", "YuzuhaCinema6SheelTrigger", "YuzuhaCinema6SheelTriggerRecord", "柚叶"),
    ("YuzuhaCinema6SugarBurstMaxTrigger", "YuzuhaCinema6SugarBurstMaxTrigger", "YuzuhaCinema6SugarBurstMaxTriggerRecord", "柚叶"),
    ("YuzuhaHardCandyShotTrigger", "YuzuhaHardCandyShotTrigger", "YuzuhaHardCandyShotTriggerRecord", "柚叶"),
)

EQUIPPER_ROWS = (
    ("CannonRotor", "CannonRotor", "CannonRotorRecord", "加农转子"),
    ("HeartstringNocturne", "HeartstringNocturne", "HeartstringNocturneRecord", "心弦夜响"),
    ("TimeweaverDisorderDmgMul", "TimeweaverDisorderDmgMul", "TimeweaverDisorderDmgMulRecord", "时流贤者"),
    ("WeepingGeminiApBonus", "WeepingGeminiApBonus", "WeepingGeminiApBonusRecord", "双生泣星"),
    ("WoodpeckerElectroSet4_NA", "WoodpeckerElectroSet4_NA", "WoodpeckerElectroNARecord", "啄木鸟电音"),
    ("ZanshinHerbCase", "ZanshinHerbCase", "ZanshinHerbCaseRecord", "残心青囊"),
)


def _module(module_name: str) -> Any:
    return importlib.import_module(f"zsim.sim_progress.Buff.BuffXLogic.{module_name}")


def _template_buff(*, record: object | None = None, include_record_attr: bool = True) -> SimpleNamespace:
    history = SimpleNamespace(record=record) if include_record_attr else SimpleNamespace()
    return SimpleNamespace(
        history=history,
        dy=SimpleNamespace(count=0, active=False),
        ft=SimpleNamespace(step=1),
    )


class _BuffInstance:
    def __init__(self, *, index: str = "template-index") -> None:
        self.sim_instance = SimpleNamespace(tick=777)
        self.ft = SimpleNamespace(index=index, maxcount=100, step=1)
        self.dy = SimpleNamespace(count=0, active=False)


def _install_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    owner: str,
    index: str,
    buff_0: SimpleNamespace,
    item_name: str | None = None,
    registry: dict[str, dict[str, object]] | None = None,
) -> tuple[list[object], list[tuple[str, object]], list[tuple[str, object]], list[tuple[str, object]]]:
    direct_existing_calls: list[object] = []
    direct_equipper_calls: list[tuple[str, object]] = []
    context_existing_calls: list[tuple[str, object]] = []
    context_equipper_calls: list[tuple[str, object]] = []
    equipper = f"equipper:{item_name}" if item_name is not None else owner
    lookup_registry = registry if registry is not None else {owner: {index: buff_0}, equipper: {index: buff_0}}

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        direct_existing_calls.append(sim_instance)
        return lookup_registry

    def fake_find_equipper(name: str, *, sim_instance: object) -> str:
        direct_equipper_calls.append((name, sim_instance))
        return equipper

    class _PreparationContext:
        def __init__(self, sim_instance: object) -> None:
            self.sim_instance = sim_instance

        def find_equipper(self, name: str) -> str:
            context_equipper_calls.append((name, self.sim_instance))
            return equipper

        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            context_existing_calls.append((owner_name, self.sim_instance))
            return lookup_registry[owner_name]

    def fake_context_builder(buff_instance: object) -> _PreparationContext:
        return _PreparationContext(buff_instance.sim_instance)

    monkeypatch.setattr(module.JudgeTools, "find_exist_buff_dict", fake_find_exist_buff_dict, raising=False)
    monkeypatch.setattr(module.JudgeTools, "find_equipper", fake_find_equipper, raising=False)
    monkeypatch.setattr(module, "build_preparation_context_from_buff", fake_context_builder, raising=False)
    return direct_existing_calls, direct_equipper_calls, context_existing_calls, context_equipper_calls


@pytest.mark.parametrize(("module_name", "logic_name", "record_name", "owner"), LITERAL_ROWS)
def test_remaining_literal_owner_record_lookup_identity_and_errors(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    logic_name: str,
    record_name: str,
    owner: str,
) -> None:
    module = _module(module_name)
    logic = getattr(module, logic_name)(_BuffInstance())
    record_cls = getattr(module, record_name)
    template = _template_buff()
    direct, _, context, _ = _install_lookup(
        monkeypatch,
        module=module,
        owner=owner,
        index=logic.buff_instance.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    assert (direct, context) in (
        ([logic.buff_instance.sim_instance], []),
        ([], [(owner, logic.buff_instance.sim_instance)]),
    )
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    assert logic.record is existing_record
    assert template.history.record is existing_record

    missing = getattr(module, logic_name)(_BuffInstance(index="missing-index"))
    _install_lookup(
        monkeypatch,
        module=module,
        owner=owner,
        index=missing.buff_instance.ft.index,
        buff_0=_template_buff(),
        registry={owner: {}},
    )
    with pytest.raises(KeyError):
        missing.check_record_module()


@pytest.mark.parametrize(("module_name", "logic_name", "record_name", "item_name"), EQUIPPER_ROWS)
def test_remaining_equipper_record_lookup_identity_and_errors(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    logic_name: str,
    record_name: str,
    item_name: str,
) -> None:
    module = _module(module_name)
    logic = getattr(module, logic_name)(_BuffInstance())
    record_cls = getattr(module, record_name)
    template = _template_buff()
    equipper = f"equipper:{item_name}"
    direct, direct_equipper, context, context_equipper = _install_lookup(
        monkeypatch,
        module=module,
        owner=equipper,
        item_name=item_name,
        index=logic.buff_instance.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    assert logic.equipper == equipper
    assert (direct_equipper, context_equipper) in (
        ([(item_name, logic.buff_instance.sim_instance)], []),
        ([], [(item_name, logic.buff_instance.sim_instance)]),
    )
    assert (direct, context) in (
        ([logic.buff_instance.sim_instance], []),
        ([], [(equipper, logic.buff_instance.sim_instance)]),
    )
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    assert logic.record is existing_record
    assert template.history.record is existing_record

    missing = getattr(module, logic_name)(_BuffInstance(index="missing-index"))
    _install_lookup(
        monkeypatch,
        module=module,
        owner=equipper,
        item_name=item_name,
        index=missing.buff_instance.ft.index,
        buff_0=_template_buff(),
        registry={equipper: {}},
    )
    with pytest.raises(KeyError):
        missing.check_record_module()


def test_basic_complex_dynamic_owner_preserves_char_name_required_and_missing_record_attr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module("BasicComplexBuffClass")
    logic = module.BasicComplexBuffClass(_BuffInstance())
    template = _template_buff(include_record_attr=False)
    direct, _, context, _ = _install_lookup(
        monkeypatch,
        module=module,
        owner="动态角色",
        index=logic.buff_instance.ft.index,
        buff_0=template,
    )

    with pytest.raises(ValueError):
        logic.check_record_module()

    logic.check_record_module(char_name="动态角色")

    assert (direct, context) in (
        ([logic.buff_instance.sim_instance], []),
        ([], [("动态角色", logic.buff_instance.sim_instance)]),
    )
    assert logic.buff_0 is template
    assert isinstance(template.history.record, module.BaseBuffRecord)
    assert logic.record is template.history.record


def test_remaining_files_have_no_direct_find_exist_after_migration_or_legacy_shape_before() -> None:
    direct_files = sorted(
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in BUFFXLOGIC_ROOT.glob("*.py")
        if "JudgeTools.find_exist_buff_dict" in path.read_text(encoding="utf-8")
    )
    allowed_before_migration = {
        "zsim/sim_progress/Buff/BuffXLogic/BasicComplexBuffClass.py",
        *(f"zsim/sim_progress/Buff/BuffXLogic/{module}.py" for module, *_ in LITERAL_ROWS),
        *(f"zsim/sim_progress/Buff/BuffXLogic/{module}.py" for module, *_ in EQUIPPER_ROWS),
    }
    assert set(direct_files) <= allowed_before_migration
    if direct_files:
        return
    for module, *_ in LITERAL_ROWS:
        source = (BUFFXLOGIC_ROOT / f"{module}.py").read_text(encoding="utf-8")
        assert "ensure_owner_template_record(" in source
        assert "prepare_with_context(" in source
    for module, *_ in EQUIPPER_ROWS:
        source = (BUFFXLOGIC_ROOT / f"{module}.py").read_text(encoding="utf-8")
        assert "ensure_equipper_template_record(" in source
        assert (
            "prepare_with_context(" in source
            or "preparation_context=preparation_context" in source
        )
    basic_source = (BUFFXLOGIC_ROOT / "BasicComplexBuffClass.py").read_text(encoding="utf-8")
    assert "ensure_owner_template_record(" in basic_source
    assert "prepare_with_context(" in basic_source
