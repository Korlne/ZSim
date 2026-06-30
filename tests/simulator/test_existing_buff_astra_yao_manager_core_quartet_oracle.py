from __future__ import annotations

import importlib
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFXLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
TICK_NOW = 2460
OWNER = "耀嘉音"
SUB_EXIST_BUFF_DICT = {"Buff-角色-耀嘉音-核心被动攻击力": object()}

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/AstraYaoQuickAssistManagerTrigger.py",
        "module": "AstraYaoQuickAssistManagerTrigger",
        "logic": "AstraYaoQuickAssistManagerTrigger",
        "record": "AstraYaoQuickAssistManagerTriggerRecord",
        "prepared": {"char_CID": 1311},
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/AstraYaoChordManagerTrigger.py",
        "module": "AstraYaoChordManagerTrigger",
        "logic": "AstraYaoChordManagerTrigger",
        "record": "AstraYaoChordManagerTriggerRecord",
        "prepared": {"char_CID": 1311},
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/AstraYaoCorePassiveAtkBonus.py",
        "module": "AstraYaoCorePassiveAtkBonus",
        "logic": "AstraYaoCorePassiveAtkBonus",
        "record": "AstraYaoCorePassiveAtkBonusRecord",
        "prepared": {"char_CID": 1311, "sub_exist_buff_dict": 1},
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/AstraYaoIdyllicCadenza.py",
        "module": "AstraYaoIdyllicCadenza",
        "logic": "AstraYaoIdyllicCadenza",
        "record": "AstraYaoIdyllicCadenzaRecord",
        "prepared": {"char_CID": 1311},
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED = (
    "non-Astra manager/resource rows",
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


class _TemplateBuff:
    def __init__(self, *, record: object | None = None, active: bool = False) -> None:
        self.history = SimpleNamespace(record=record)
        self.dy = SimpleNamespace(active=active)


class _RecordingBuffInstance:
    def __init__(
        self,
        *,
        index: str = "astra-template-index",
        tick: int = TICK_NOW,
        maxcount: int = 999,
        maxduration: int = 2400,
    ) -> None:
        self.order_log: list[str] = []
        self.report_calls = 0

        def change_process_state() -> None:
            self.report_calls += 1
            self.order_log.append("report")

        self.sim_instance = SimpleNamespace(
            tick=tick,
            schedule_data=SimpleNamespace(change_process_state=change_process_state),
        )
        self.ft = SimpleNamespace(index=index, maxcount=maxcount, maxduration=maxduration)
        self.dy = SimpleNamespace(active=False, startticks=0, endticks=0, count=0)
        self.simple_start_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.update_to_buff_0_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def simple_start(self, *args: object, **kwargs: object) -> None:
        self.simple_start_calls.append((args, dict(kwargs)))
        if not kwargs.get("no_start"):
            self.dy.startticks = int(args[0])
        self.order_log.append("simple_start")

    def update_to_buff_0(self, *args: object, **kwargs: object) -> None:
        self.update_to_buff_0_calls.append((args, dict(kwargs)))
        self.order_log.append("update_to_buff_0")


def _module(row: dict[str, object]) -> Any:
    return importlib.import_module(
        f"zsim.sim_progress.Buff.BuffXLogic.{row['module']}"
    )


def _install_tick(monkeypatch: pytest.MonkeyPatch, module: Any) -> list[object]:
    tick_calls: list[object] = []

    def fake_find_tick(*, sim_instance: object) -> int:
        tick_calls.append(sim_instance)
        return sim_instance.tick

    monkeypatch.setattr(module, "find_tick", fake_find_tick, raising=False)
    return tick_calls


def _install_owner_lookup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    index: str,
    buff_0: _TemplateBuff,
    registry: dict[str, dict[str, object]] | None = None,
) -> SimpleNamespace:
    lookup_registry = registry if registry is not None else {OWNER: {index: buff_0}}
    raw_existing_buff_calls: list[object] = []
    context_build_calls: list[object] = []
    context_calls: list[tuple[str, object]] = []

    def fake_find_exist_buff_dict(*, sim_instance: object) -> dict[str, dict[str, object]]:
        raw_existing_buff_calls.append(sim_instance)
        return lookup_registry

    class FakePreparationContext:
        def find_sub_exist_buff_dict(self, owner_name: str) -> dict[str, object]:
            context_calls.append(("find_sub_exist_buff_dict", owner_name))
            return lookup_registry[owner_name]

    def fake_context_builder(buff_instance: object) -> FakePreparationContext:
        context_build_calls.append(buff_instance)
        return FakePreparationContext()

    if hasattr(module, "JudgeTools"):
        monkeypatch.setattr(
            module.JudgeTools,
            "find_exist_buff_dict",
            fake_find_exist_buff_dict,
        )
    monkeypatch.setattr(
        module,
        "build_preparation_context_from_buff",
        fake_context_builder,
        raising=False,
    )
    return SimpleNamespace(
        raw_existing_buff_calls=raw_existing_buff_calls,
        context_build_calls=context_build_calls,
        context_calls=context_calls,
    )


def _assert_owner_template_lookup(
    lookup: SimpleNamespace,
    *,
    sim_instance: object,
) -> None:
    assert (
        lookup.raw_existing_buff_calls == [sim_instance]
        or lookup.context_calls == [("find_sub_exist_buff_dict", OWNER)]
    )


def _install_preparation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    module: Any,
    harness: _RecordingBuffInstance,
    buff_0: _TemplateBuff,
    char: object | None = None,
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
        if char_ref is not None and getattr(record, "char", None) is None:
            record.char = char_ref
        if kwargs.get("sub_exist_buff_dict") is not None:
            record.sub_exist_buff_dict = SUB_EXIST_BUFF_DICT

    buff_0_ref = buff_0
    char_ref = char
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return preparation_calls


def _skill_node(
    *,
    trigger_buff_level: int = 5,
    preload_tick: int = TICK_NOW,
    skill_tag: str = "1311_QTE",
    char_name: str = "苍角",
) -> SimpleNamespace:
    return SimpleNamespace(
        skill=SimpleNamespace(trigger_buff_level=trigger_buff_level),
        preload_tick=preload_tick,
        skill_tag=skill_tag,
        char_name=char_name,
    )


def _astra_quartet_scan() -> dict[str, list[str]]:
    selected: list[str] = []
    for row in SELECTED_ROWS:
        path = PROJECT_ROOT / str(row["file"])
        source = path.read_text(encoding="utf-8")
        has_owner_lookup = (
            ('["耀嘉音"][self.buff_instance.ft.index]' in source)
            or (
                'owner_name="耀嘉音"' in source
                and "ensure_owner_template_record(" in source
            )
        )
        has_preparation = (
            "return check_preparation(buff_instance=self.buff_instance, buff_0=self.buff_0, **kwargs)"
            in source
            or "prepare_with_context(" in source
        )
        if has_owner_lookup and has_preparation and str(row["record"]) in source:
            selected.append(str(row["file"]))
    return {
        "safe_mechanical": [],
        "needs_focused_oracle": selected,
        "excluded_or_deferred": list(EXCLUDED_OR_DEFERRED),
    }


def test_bounded_census_classifies_astra_manager_core_quartet() -> None:
    assert _astra_quartet_scan() == {
        "safe_mechanical": [],
        "needs_focused_oracle": list(SELECTED_FILES),
        "excluded_or_deferred": list(EXCLUDED_OR_DEFERRED),
    }


def test_astra_quartet_source_uses_preparation_context_helper_path() -> None:
    for relative_path in SELECTED_FILES:
        source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")

        assert "prepare_with_context(" in source
        assert "ensure_owner_template_record(" in source
        assert "build_preparation_context_from_buff" in source
        assert 'owner_name="耀嘉音"' in source
        assert "JudgeTools.find_exist_buff_dict" not in source
        assert "return check_preparation(buff_instance=self.buff_instance, buff_0=self.buff_0, **kwargs)" not in source


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_quartet_check_record_module_pins_owner_index_lazy_record_and_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    record_cls = getattr(module, str(row["record"]))
    harness = _RecordingBuffInstance(index="selected-template-index")
    logic = logic_cls(harness)
    template = _TemplateBuff()
    lookup = _install_owner_lookup(
        monkeypatch,
        module=module,
        index=harness.ft.index,
        buff_0=template,
    )

    logic.check_record_module()

    _assert_owner_template_lookup(lookup, sim_instance=harness.sim_instance)
    assert logic.buff_0 is template
    assert isinstance(template.history.record, record_cls)
    assert logic.record is template.history.record

    existing_record = logic.record
    logic.check_record_module()

    assert template.history.record is existing_record
    assert logic.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {OWNER: {}}])
def test_quartet_check_record_module_pins_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
    registry: dict[str, dict[str, object]],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance(index="missing-template-index")
    logic = logic_cls(harness)
    _install_owner_lookup(
        monkeypatch,
        module=module,
        index=harness.ft.index,
        buff_0=_TemplateBuff(),
        registry=registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


def test_quick_assist_manager_trigger_pins_preparation_and_update_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.AstraYaoQuickAssistManagerTrigger(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)
    update_calls: list[tuple[int, object]] = []
    char = SimpleNamespace(
        chord_manager=SimpleNamespace(
            quick_assist_trigger_manager=SimpleNamespace(
                update_myself=lambda tick, node: update_calls.append((tick, node))
            )
        )
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
    )
    skill_node = object()

    assert logic.special_judge_logic() is True
    assert logic.special_effect_logic() is None
    logic.special_effect_logic(skill_node=skill_node)

    assert preparation_calls == [row["prepared"], row["prepared"]]
    assert update_calls == [(TICK_NOW, skill_node)]


def test_chord_manager_trigger_pins_judge_gate_and_start_manager_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.AstraYaoChordManagerTrigger(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)
    spawn_calls: list[tuple[int, object]] = []
    from zsim.sim_progress.Character.AstraYao import AstraYao

    char = AstraYao.__new__(AstraYao)
    char.chord_manager = SimpleNamespace(
        chord_trigger=SimpleNamespace(
            try_spawn_chord_coattack=lambda tick, skill_node: spawn_calls.append(
                (tick, skill_node)
            )
        )
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
    )
    matching_node = _skill_node()

    assert logic.special_judge_logic(skill_node=_skill_node(trigger_buff_level=4)) is False
    assert logic.special_judge_logic(skill_node=_skill_node(preload_tick=TICK_NOW + 1)) is False
    assert logic.special_judge_logic(skill_node=matching_node) is True
    for trigger_level in (7, 8):
        node = _skill_node(trigger_buff_level=trigger_level)
        assert logic.special_judge_logic(skill_node=node) is True
        assert template.history.record.last_update_node is node
    template.history.record.last_update_node = matching_node
    logic.special_start_logic()

    assert template.history.record.last_update_node is matching_node
    assert spawn_calls == [(TICK_NOW, matching_node)]
    assert preparation_calls == [row["prepared"]] * 6


def test_chord_manager_trigger_pins_astra_type_check_and_report_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.AstraYaoChordManagerTrigger(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)
    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(),
    )
    logic.check_record_module()
    logic.record.last_update_node = _skill_node()

    with pytest.raises(TypeError, match="record.char is not AstraYao"):
        logic.special_start_logic()

    from zsim.sim_progress.Character.AstraYao import AstraYao

    spawn_calls: list[tuple[int, object]] = []
    astra_char = AstraYao.__new__(AstraYao)
    astra_char.chord_manager = SimpleNamespace(
        chord_trigger=SimpleNamespace(
            try_spawn_chord_coattack=lambda tick, skill_node: spawn_calls.append(
                (tick, skill_node)
            )
        )
    )
    monkeypatch.setattr(module, "ASTRAYAO_REPORT", True)
    logic.record.char = astra_char

    logic.special_start_logic()

    assert spawn_calls == [(TICK_NOW, logic.record.last_update_node)]
    assert harness.report_calls == 1
    assert harness.order_log == ["report"]


def test_core_passive_pins_sub_registry_count_duration_update_and_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _RecordingBuffInstance(maxcount=600, maxduration=2000)
    logic = module.AstraYaoCorePassiveAtkBonus(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)

    class FakeCharacter:
        def __init__(self) -> None:
            self.statement = SimpleNamespace(ATK=2000)

    import zsim.sim_progress.Character as character_pkg

    monkeypatch.setattr(character_pkg, "Character", FakeCharacter)
    char = FakeCharacter()
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
    )

    logic.special_start_logic(benifit="苍角")

    assert preparation_calls == [row["prepared"]]
    assert harness.simple_start_calls == [
        ((TICK_NOW, SUB_EXIST_BUFF_DICT), {"no_count": 1, "no_end": 1})
    ]
    assert harness.dy.count == 600
    assert harness.dy.endticks == TICK_NOW + 1200
    assert template.history.record.update_info_box["苍角"] == {
        "startticks": TICK_NOW,
        "endticks": TICK_NOW + 1200,
        "count": 600,
    }
    assert harness.update_to_buff_0_calls == [((template,), {})]
    assert harness.order_log == ["simple_start", "update_to_buff_0"]


def test_core_passive_pins_missing_benifit_character_type_and_report_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _RecordingBuffInstance(maxcount=600, maxduration=2000)
    logic = module.AstraYaoCorePassiveAtkBonus(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)
    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(statement=SimpleNamespace(ATK=2000)),
    )

    with pytest.raises(TypeError):
        logic.special_start_logic(benifit="苍角")

    class FakeCharacter:
        def __init__(self) -> None:
            self.statement = SimpleNamespace(ATK=2000)

    import zsim.sim_progress.Character as character_pkg

    monkeypatch.setattr(character_pkg, "Character", FakeCharacter)
    monkeypatch.setattr(module, "ASTRAYAO_REPORT", True)
    logic.record.char = FakeCharacter()
    with pytest.raises(ValueError, match="xstart函数并未获取到benifit参数"):
        logic.special_start_logic()

    logic.special_start_logic(benifit="苍角")

    assert harness.report_calls == 1
    assert harness.order_log == ["simple_start", "update_to_buff_0", "report"]


@pytest.mark.parametrize(
    ("existing_endtick", "expected_endtick"),
    [
        (TICK_NOW + 300, TICK_NOW + 1500),
        (TICK_NOW - 1, TICK_NOW + 1200),
    ],
)
def test_core_passive_pins_same_tick_dedupe_and_duration_extension(
    monkeypatch: pytest.MonkeyPatch,
    existing_endtick: int,
    expected_endtick: int,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _RecordingBuffInstance(maxduration=2400)
    logic = module.AstraYaoCorePassiveAtkBonus(harness)
    template = _TemplateBuff(active=True)
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)

    class FakeCharacter:
        def __init__(self) -> None:
            self.statement = SimpleNamespace(ATK=1000)

    import zsim.sim_progress.Character as character_pkg

    monkeypatch.setattr(character_pkg, "Character", FakeCharacter)
    _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=FakeCharacter(),
    )
    logic.check_record_module()
    logic.record.update_info_box["苍角"] = {
        "startticks": TICK_NOW,
        "endticks": TICK_NOW + 1200,
        "count": 350.0,
    }

    logic.special_start_logic(benifit="苍角")

    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
    assert logic.record.update_info_box["苍角"]["endticks"] == TICK_NOW + 1200

    logic.record.update_info_box["苍角"] = {
        "startticks": TICK_NOW - 30,
        "endticks": existing_endtick,
        "count": 350.0,
    }
    logic.special_start_logic(benifit="苍角")

    assert harness.simple_start_calls == [
        (
            (TICK_NOW, SUB_EXIST_BUFF_DICT),
            {"no_start": 1, "no_count": 1, "no_end": 1},
        )
    ]
    assert harness.dy.startticks == TICK_NOW
    assert harness.dy.endticks == expected_endtick
    assert harness.update_to_buff_0_calls == [((template,), {})]


def test_idyllic_cadenza_pins_resource_judge_and_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[3]
    module = _module(row)
    harness = _RecordingBuffInstance()
    logic = module.AstraYaoIdyllicCadenza(harness)
    template = _TemplateBuff()
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)
    char = SimpleNamespace(get_resources=lambda: ("咏叹华彩", True))
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=char,
    )

    assert logic.special_judge_logic() is True
    assert logic.special_exit_logic() is False

    char.get_resources = lambda: ("咏叹华彩", False)
    assert logic.special_judge_logic() is False
    assert logic.special_exit_logic() is True

    assert preparation_calls == [row["prepared"]] * 4


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_quartet_preparation_errors_propagate_before_file_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _RecordingBuffInstance()
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_tick(monkeypatch, module)
    _install_owner_lookup(monkeypatch, module=module, index=harness.ft.index, buff_0=template)
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        raises=RuntimeError("missing preparation"),
    )

    with pytest.raises(RuntimeError, match="missing preparation"):
        if row["module"] == "AstraYaoQuickAssistManagerTrigger":
            logic.special_effect_logic(skill_node=object())
        elif row["module"] == "AstraYaoChordManagerTrigger":
            logic.special_judge_logic(skill_node=_skill_node())
        elif row["module"] == "AstraYaoCorePassiveAtkBonus":
            logic.special_start_logic(benifit="苍角")
        else:
            logic.special_judge_logic()

    assert preparation_calls == [row["prepared"]]
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
