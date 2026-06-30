from __future__ import annotations

import importlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from zsim.sim_progress.Load import LoadingMission
from zsim.sim_progress.Preload import SkillNode
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import DirgeOfDestinyAnomaly
from zsim.sim_progress.data_struct.schedule_dispatch import (
    ScheduleDispatchPort,
    ScheduledEventEmitterProvider,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFFXLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-30-US-001-existing-buff-preload-scheduled-trigger-quartet-oracle.json"
)

SELECTED_ROWS = (
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema2Trigger.py",
        "module": "YuzuhaCinema2Trigger",
        "logic": "YuzuhaCinema2Trigger",
        "record": "YuzuhaCinema2TriggerRecord",
        "owner": "柚叶",
        "index": "Buff-角色-柚叶-2画触发",
        "judge_prepared": {"char_CID": 1411, "enemy": 1},
        "hit_prepared": {"char_CID": 1411},
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema2StunTimeLimitBonus.py",
        "module": "YixuanCinema2StunTimeLimitBonus",
        "logic": "YixuanCinema2StunTimeLimitBonus",
        "record": "YixuanCinema2StunTimeLimitBonusRecord",
        "owner": "仪玄",
        "index": "Buff-角色-仪玄-2画-失衡时间延长",
        "judge_prepared": {"char_CID": 1371, "enemy": 1},
        "exit_prepared": {"char_CID": 1371, "enemy": 1},
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
        "module": "VivianCorePassiveTrigger",
        "logic": "VivianCorePassiveTrigger",
        "record": "VivianCorePassiveTriggerRecord",
        "owner": "薇薇安",
        "index": "Buff-角色-薇薇安-核心被动-异放触发器",
        "judge_prepared": {"char_CID": 1331, "enemy": 1},
        "effect_prepared": {
            "char_CID": 1361,
            "preload_data": 1,
            "enemy": 1,
            "sub_exist_buff_dict": 1,
        },
    },
    {
        "file": "zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py",
        "module": "VivianDotTrigger",
        "logic": "VivianDotTrigger",
        "record": "VivianDotTriggerRecord",
        "owner": "薇薇安",
        "index": "Buff-角色-薇薇安-核心被动-Dot触发器",
        "judge_prepared": {"char_CID": 1331, "enemy": 1},
        "hit_prepared": {"char_CID": 1361, "enemy": 1},
    },
)

SELECTED_FILES = tuple(row["file"] for row in SELECTED_ROWS)
EXCLUDED_OR_DEFERRED = (
    "manager/preload/resource rows",
    "trigger-buff rows",
    "dynamic char_name owner rows",
    "action-stack/listener/report-state/dynamic-active-view rows",
    "scheduled/preload producer rows beyond the selected quartet",
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
    def __init__(self, *, record: object | None = None) -> None:
        self.history = SimpleNamespace(record=record)


class _ScheduleDataProbe:
    def __init__(self) -> None:
        self.event_list: list[object] = []
        self.change_process_state_calls = 0

    def change_process_state(self) -> None:
        self.change_process_state_calls += 1


class _BuffInstanceProbe:
    def __init__(self, *, index: str, tick: int = 960) -> None:
        self.schedule_data = _ScheduleDataProbe()
        self.sim_instance = SimpleNamespace(
            tick=tick,
            schedule_data=self.schedule_data,
            char_data=SimpleNamespace(
                find_char_obj=lambda CID: SimpleNamespace(NAME="薇薇安", CID=CID)
            ),
            listener_manager=SimpleNamespace(
                broadcast_event=lambda **_: pytest.fail(
                    "quartet oracle should not broadcast listener events"
                )
            ),
        )
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


class _RecordingDispatchPort(ScheduleDispatchPort):
    def __init__(self, order_log: list[str] | None = None) -> None:
        self.events: list[object] = []
        self.order_log = order_log

    def publish_scheduled(self, event: object) -> None:
        if self.order_log is not None:
            self.order_log.append("publish")
        self.events.append(event)


class _EnemyDynamicProbe:
    def __init__(
        self,
        *,
        stunned: bool = False,
        anomaly_active: bool = False,
        active_anomalies: list[object] | None = None,
        active_dots: list[object] | None = None,
    ) -> None:
        self.stunned = stunned
        self.anomaly_active = anomaly_active
        self.active_anomalies = active_anomalies or []
        self.dynamic_dot_list = list(active_dots or [])
        self.stun_reads = 0
        self.anomaly_reads = 0
        self.active_anomaly_reads = 0

    @property
    def stun(self) -> bool:
        self.stun_reads += 1
        return self.stunned

    def is_under_anomaly(self) -> bool:
        self.anomaly_reads += 1
        return self.anomaly_active

    def get_active_anomaly(self) -> list[object]:
        self.active_anomaly_reads += 1
        return self.active_anomalies


class _Cinema2SkillProbe:
    def __init__(
        self, *, skill_tag: str = "1411_E_EX_A", last_hit: bool = True
    ) -> None:
        self.skill_tag = skill_tag
        self.force_qte_trigger = False
        self._last_hit = last_hit
        self.last_hit_ticks: list[int] = []

    def is_last_hit(self, *, tick: int) -> bool:
        self.last_hit_ticks.append(tick)
        return self._last_hit


def _skill_node(
    *,
    skill_tag: str = "1331_CoAttack_A",
    preload_tick: int = 960,
    uuid: str = "node-1",
    hit_now: bool = True,
) -> SkillNode:
    skill = SimpleNamespace(
        skill_tag=skill_tag,
        char_name="薇薇安",
        hit_times=1,
        labels=None,
        ticks=12,
        tick_list=[3],
        heavy_attack=False,
        element_type=4,
    )
    node = SkillNode(skill, preload_tick)
    node.UUID = uuid

    class _LoadingMissionProbe:
        def __init__(self) -> None:
            self.hit_checks: list[int] = []

        def is_hit_now(self, tick: int) -> bool:
            self.hit_checks.append(tick)
            return hit_now

    node.loading_mission = _LoadingMissionProbe()
    return node


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
    harness: _BuffInstanceProbe,
    buff_0: _TemplateBuff,
    char: object | None = None,
    enemy: object | None = None,
    sub_exist_buff_dict: dict[str, object] | None = None,
    preload_data: object | None = None,
    raises: Exception | None = None,
) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []

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
        calls.append(observed)
        if raises is not None:
            raise raises
        record = buff_0_ref.history.record
        if char is not None:
            record.char = char
        if enemy is not None:
            record.enemy = enemy
        if sub_exist_buff_dict is not None:
            record.sub_exist_buff_dict = sub_exist_buff_dict
        if preload_data is not None:
            record.preload_data = preload_data

    buff_0_ref = buff_0
    monkeypatch.setattr(module, "check_preparation", fake_check_preparation)
    return calls


def _preload_scheduled_quartet_scan() -> list[str]:
    rows: list[str] = []
    row_rules = {
        "YuzuhaCinema2Trigger.py": (
            '"柚叶"',
            "YuzuhaCinema2TriggerRecord",
            "get_prepared(char_CID=1411, enemy=1)",
            "get_prepared(char_CID=1411)",
            "skill_node.force_qte_trigger = True",
            "YUZUHA_REPORT",
        ),
        "YixuanCinema2StunTimeLimitBonus.py": (
            '"仪玄"',
            "YixuanCinema2StunTimeLimitBonusRecord",
            "get_prepared(char_CID=1371, enemy=1)",
            'required_skill_tag = "1371_Q"',
            "skill_node.preload_tick != self.buff_instance.sim_instance.tick",
            "YIXUAN_REPORT",
        ),
        "VivianCorePassiveTrigger.py": (
            '"薇薇安"',
            "VivianCorePassiveTriggerRecord",
            "get_prepared(char_CID=1331, enemy=1)",
            "preload_data=1",
            "emit_scheduled(dirge_of_destiny_anomaly)",
            "VIVIAN_REPORT",
        ),
        "VivianDotTrigger.py": (
            '"薇薇安"',
            "VivianDotTriggerRecord",
            "get_prepared(char_CID=1331, enemy=1)",
            "get_prepared(char_CID=1361, enemy=1)",
            'find_active_by_index("ViviansProphecy")',
            "emit_scheduled(dot.skill_node_data)",
            "VIVIAN_REPORT",
        ),
    }
    for filename, terms in row_rules.items():
        path = BUFFXLOGIC_ROOT / filename
        source = path.read_text(encoding="utf-8")
        lookup_path = (
            "JudgeTools.find_exist_buff_dict" in source
            or "ensure_owner_template_record(" in source
        )
        if lookup_path and all(term in source for term in terms):
            rows.append(path.relative_to(PROJECT_ROOT).as_posix())
    return rows


def test_us001_checkpoint_rows_match_current_preload_scheduled_trigger_quartet_census() -> None:
    checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))

    assert checkpoint["schema"] == (
        "zsim-existing-buff-preload-scheduled-trigger-quartet-oracle.v1"
    )
    assert checkpoint["safe_mechanical"] == []
    assert tuple(entry["file"] for entry in checkpoint["needs_focused_oracle"]) == (
        SELECTED_FILES
    )
    assert checkpoint["scan_summary"]["selected_needs_focused_oracle_count"] == 4
    assert checkpoint["scan_summary"]["bounded_preload_scheduled_trigger_count"] == 4
    assert checkpoint["scan_summary"]["bounded_preload_scheduled_trigger_rows"] == list(
        SELECTED_FILES
    )
    assert checkpoint["excluded_or_deferred"] == [
        {"pool": pool} for pool in EXCLUDED_OR_DEFERRED
    ]
    assert checkpoint["none_safe_to_implement_stop_evidence"] == []
    assert checkpoint["us002_target"] == (
        "existing-buff-preload-scheduled-trigger-quartet-migration"
    )
    assert checkpoint["us002_target_allowed_values"] == [
        "existing-buff-preload-scheduled-trigger-quartet-migration",
        "none-safe-to-implement",
    ]
    assert _preload_scheduled_quartet_scan() == list(SELECTED_FILES)


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_quartet_check_record_module_pins_owner_index_lazy_record_and_identity(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    record_cls = getattr(module, str(row["record"]))
    harness = _BuffInstanceProbe(index=str(row["index"]))
    logic = logic_cls(harness)
    template = _TemplateBuff()
    lookup_calls = _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
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
    assert template.history.record is existing_record
    assert logic.record is existing_record


@pytest.mark.parametrize("row", SELECTED_ROWS)
@pytest.mark.parametrize("registry", [{}, {"wrong-owner": {}}])
def test_quartet_check_record_module_pins_missing_owner_or_index_errors(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
    registry: dict[str, dict[str, object]],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _BuffInstanceProbe(index="missing-template-index")
    logic = logic_cls(harness)
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=_TemplateBuff(),
        registry=registry,
    )

    with pytest.raises(KeyError):
        logic.check_record_module()


@pytest.mark.parametrize(
    ("skill_tag", "stunned", "last_update_tick", "last_hit", "expected", "last_hit_checks"),
    [
        ("1411_E_EX_A", False, None, True, True, [1500]),
        ("1411_OTHER", False, None, True, False, []),
        ("1411_E_EX_A", True, None, True, False, []),
        ("1411_E_EX_A", False, 1490, True, False, []),
        ("1411_E_EX_A", False, None, False, False, [1500]),
    ],
)
def test_yuzuha_cinema2_judge_pins_tag_stun_cooldown_and_last_hit_gates(
    monkeypatch: pytest.MonkeyPatch,
    skill_tag: str,
    stunned: bool,
    last_update_tick: int | None,
    last_hit: bool,
    expected: bool,
    last_hit_checks: list[int],
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=1500)
    logic = module.YuzuhaCinema2Trigger(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(stunned=stunned))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )
    skill_node = _Cinema2SkillProbe(skill_tag=skill_tag, last_hit=last_hit)

    logic.check_record_module()
    logic.record.last_update_tick = last_update_tick
    result = logic.special_judge_logic(skill_node=skill_node)

    assert result is expected
    assert preparation_calls == [row["judge_prepared"]]
    assert enemy.dynamic.stun_reads == 1
    assert skill_node.last_hit_ticks == last_hit_checks
    assert logic.record.skill_node_be_changed is (skill_node if expected else None)
    assert harness.schedule_data.change_process_state_calls == 0
    assert harness.schedule_data.event_list == []


def test_yuzuha_cinema2_hit_sets_qte_and_report_then_clears_pending_signal(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=1500)
    logic = module.YuzuhaCinema2Trigger(harness)
    template = _TemplateBuff()
    skill_node = _Cinema2SkillProbe()
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
    )
    monkeypatch.setattr(module, "YUZUHA_REPORT", True)

    logic.check_record_module()
    logic.record.skill_node_be_changed = skill_node
    logic.special_hit_logic()

    assert preparation_calls == [row["hit_prepared"]]
    assert skill_node.force_qte_trigger is True
    assert logic.record.skill_node_be_changed is None
    assert logic.record.last_update_tick == 1500
    assert harness.schedule_data.change_process_state_calls == 1
    assert "柚叶2画" in capsys.readouterr().out


def test_yuzuha_cinema2_pending_and_missing_signal_errors_precede_side_effects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[0]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=1500)
    logic = module.YuzuhaCinema2Trigger(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(stunned=False))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )

    logic.check_record_module()
    pending = object()
    logic.record.skill_node_be_changed = pending
    with pytest.raises(ValueError, match="尚未处理"):
        logic.special_judge_logic(skill_node=_Cinema2SkillProbe())
    assert logic.record.skill_node_be_changed is pending

    logic.record.skill_node_be_changed = None
    with pytest.raises(ValueError, match="未发现更新信号"):
        logic.special_hit_logic()

    assert preparation_calls == [row["judge_prepared"], row["hit_prepared"]]
    assert harness.schedule_data.change_process_state_calls == 0


@pytest.mark.parametrize(
    ("skill_tag", "stunned", "preload_tick", "expected", "stun_reads"),
    [
        ("1371_Q", True, 720, True, 1),
        ("1371_E_EX", True, 720, False, 0),
        ("1371_Q", False, 720, False, 1),
        ("1371_Q", True, 719, False, 1),
    ],
)
def test_yixuan_cinema2_judge_pins_required_tag_stun_tick_and_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    skill_tag: str,
    stunned: bool,
    preload_tick: int,
    expected: bool,
    stun_reads: int,
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=720)
    logic = module.YixuanCinema2StunTimeLimitBonus(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(stunned=stunned))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )
    monkeypatch.setattr(module, "YIXUAN_REPORT", True)
    skill_node = SimpleNamespace(skill_tag=skill_tag, preload_tick=preload_tick)

    assert logic.special_judge_logic(skill_node=skill_node) is expected

    assert preparation_calls == [row["judge_prepared"]]
    assert enemy.dynamic.stun_reads == stun_reads
    assert harness.schedule_data.change_process_state_calls == (1 if expected else 0)
    if expected:
        assert "仪玄" in capsys.readouterr().out


@pytest.mark.parametrize(("stunned", "expected"), [(False, True), (True, False)])
def test_yixuan_cinema2_exit_pins_inverse_stun_and_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stunned: bool,
    expected: bool,
) -> None:
    row = SELECTED_ROWS[1]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=720)
    logic = module.YixuanCinema2StunTimeLimitBonus(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(stunned=stunned))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )
    monkeypatch.setattr(module, "YIXUAN_REPORT", True)

    assert logic.special_exit_logic() is expected

    assert preparation_calls == [row["exit_prepared"]]
    assert enemy.dynamic.stun_reads == 1
    assert harness.schedule_data.change_process_state_calls == (1 if expected else 0)
    if expected:
        assert "失衡状态中恢复" in capsys.readouterr().out


def test_vivian_core_judge_pins_skillnode_type_tag_anomaly_and_duplicate_uuid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=96)
    logic = module.VivianCorePassiveTrigger(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(anomaly_active=True))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )

    with pytest.raises(TypeError):
        logic.special_judge_logic(skill_node=object())
    assert logic.special_judge_logic(skill_node=_skill_node(skill_tag="1331_SNA_2")) is False
    first = _skill_node(uuid="same-node")
    second = _skill_node(uuid="same-node")
    third = _skill_node(uuid="next-node")
    assert logic.special_judge_logic(skill_node=first) is True
    assert logic.special_judge_logic(skill_node=second) is False
    assert logic.special_judge_logic(skill_node=third) is True

    assert preparation_calls == [row["judge_prepared"]] * 5
    assert enemy.dynamic.anomaly_reads == 3
    assert logic.record.last_update_node is third


def test_vivian_core_judge_blocks_when_enemy_has_no_anomaly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=96)
    logic = module.VivianCorePassiveTrigger(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(anomaly_active=False))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )

    assert logic.special_judge_logic(skill_node=_skill_node()) is False

    assert preparation_calls == [row["judge_prepared"]]
    assert enemy.dynamic.anomaly_reads == 1
    assert logic.record.last_update_node is None


def test_vivian_core_effect_pins_copied_anomaly_schedule_ap_ratio_and_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    order: list[str] = []
    dispatch_port = _RecordingDispatchPort(order)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=96)
    logic = module.VivianCorePassiveTrigger(
        harness,
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: dispatch_port
        ),
    )
    template = _TemplateBuff()
    active_anomaly = AnomalyBar.__new__(AnomalyBar)
    active_anomaly.sim_instance = harness.sim_instance
    active_anomaly.element_type = 3
    active_anomaly.settled = False
    enemy = SimpleNamespace(
        dynamic=_EnemyDynamicProbe(active_anomalies=[active_anomaly])
    )
    char = SimpleNamespace(NAME="薇薇安", cinema=2)
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
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
        sub_exist_buff_dict={},
        preload_data=object(),
    )
    context = object()
    context_calls: list[dict[str, object]] = []
    reader_calls: list[object] = []

    def fake_context(**kwargs: object) -> object:
        context_calls.append(dict(kwargs))
        return context

    class _Reader:
        def read_anomaly_proficiency(self, reader_context: object) -> float:
            reader_calls.append(reader_context)
            return 250.0

    monkeypatch.setattr(
        module, "create_calculator_runtime_read_context_from_sim_instance", fake_context
    )
    monkeypatch.setattr(
        module, "get_calculator_buff_attribute_reader_service", lambda: _Reader()
    )
    monkeypatch.setattr(module, "VIVIAN_REPORT", True)

    def fake_anomaly_settled(self: AnomalyBar) -> None:
        self.settled = True

    monkeypatch.setattr(AnomalyBar, "anomaly_settled", fake_anomaly_settled)

    logic.special_effect_logic()

    assert preparation_calls == [row["effect_prepared"]]
    assert enemy.dynamic.active_anomaly_reads == 1
    assert order == ["publish"]
    assert harness.schedule_data.change_process_state_calls == 1
    assert "异放" in capsys.readouterr().out
    assert len(dispatch_port.events) == 1
    published = dispatch_port.events[0]
    assert isinstance(published, DirgeOfDestinyAnomaly)
    assert published is not active_anomaly
    assert published.settled is True
    assert active_anomaly.settled is False
    assert published.anomaly_dmg_ratio == pytest.approx(1.04)
    assert logic.record.cinema_ratio == pytest.approx(1.3)
    assert context_calls == [
        {
            "sim_instance": harness.sim_instance,
            "enemy": enemy,
            "character": char,
        }
    ]
    assert reader_calls == [context]


def test_vivian_core_effect_empty_active_anomaly_error_precedes_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    row = SELECTED_ROWS[2]
    module = _module(row)
    dispatch_port = _RecordingDispatchPort()
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=96)
    logic = module.VivianCorePassiveTrigger(
        harness,
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: dispatch_port
        ),
    )
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(active_anomalies=[]))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(NAME="薇薇安", cinema=0),
        enemy=enemy,
    )

    with pytest.raises(ValueError, match="enemy.get_active_anomlay"):
        logic.special_effect_logic()

    assert preparation_calls == [row["effect_prepared"]]
    assert dispatch_port.events == []
    assert harness.schedule_data.change_process_state_calls == 0


@pytest.mark.parametrize(
    ("skill_tag", "hit_now", "anomaly_active", "expected", "anomaly_reads"),
    [
        ("1331_EX_A", True, True, False, 0),
        ("1331_SNA_2", False, True, False, 0),
        ("1331_SNA_2", True, False, False, 1),
        ("1331_CoAttack_A", True, True, True, 1),
    ],
)
def test_vivian_dot_judge_pins_type_tag_hit_now_and_anomaly_gate(
    monkeypatch: pytest.MonkeyPatch,
    skill_tag: str,
    hit_now: bool,
    anomaly_active: bool,
    expected: bool,
    anomaly_reads: int,
) -> None:
    row = SELECTED_ROWS[3]
    module = _module(row)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=96)
    logic = module.VivianDotTrigger(harness)
    template = _TemplateBuff()
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(anomaly_active=anomaly_active))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        enemy=enemy,
    )
    skill_node = _skill_node(skill_tag=skill_tag, hit_now=hit_now)

    assert logic.special_judge_logic(skill_node=skill_node) is expected

    assert preparation_calls == [row["judge_prepared"]]
    assert skill_node.loading_mission.hit_checks == (
        [96] if skill_tag in {"1331_SNA_2", "1331_CoAttack_A"} else []
    )
    assert enemy.dynamic.anomaly_reads == anomaly_reads

    with pytest.raises(TypeError):
        logic.special_judge_logic(skill_node=object())


def test_vivian_dot_hit_pins_active_dot_suppression_registration_schedule_and_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    row = SELECTED_ROWS[3]
    module = _module(row)
    order: list[str] = []
    dispatch_port = _RecordingDispatchPort(order)
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=96)
    logic = module.VivianDotTrigger(
        harness,
        scheduled_event_emitter_provider=ScheduledEventEmitterProvider(
            lambda: dispatch_port
        ),
    )
    template = _TemplateBuff()
    inactive_dot = SimpleNamespace(ft=SimpleNamespace(index="ViviansProphecy"), dy=SimpleNamespace(active=False))
    enemy = SimpleNamespace(dynamic=_EnemyDynamicProbe(active_dots=[inactive_dot]))
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
        index=harness.ft.index,
        buff_0=template,
    )
    preparation_calls = _install_preparation(
        monkeypatch,
        module=module,
        harness=harness,
        buff_0=template,
        char=SimpleNamespace(NAME="薇薇安"),
        enemy=enemy,
    )
    dot_node = _skill_node(skill_tag="1331_Core_Passive", preload_tick=96)
    dot = SimpleNamespace(
        ft=SimpleNamespace(index="ViviansProphecy"),
        dy=SimpleNamespace(active=True),
        skill_node_data=dot_node,
        started_at=None,
    )

    def fake_start(timenow: int) -> None:
        order.append("dot_start")
        dot.started_at = timenow

    dot.start = fake_start
    spawn_calls: list[str] = []

    def fake_spawn_normal_dot(dot_index: str, *, sim_instance: object) -> object:
        spawn_calls.append(dot_index)
        assert sim_instance is harness.sim_instance
        return dot

    monkeypatch.setattr(
        "zsim.sim_progress.Update.UpdateAnomaly.spawn_normal_dot",
        fake_spawn_normal_dot,
    )
    original_mission_start = LoadingMission.mission_start

    def fake_mission_start(self: LoadingMission, timenow: int, **kwargs: object) -> None:
        order.append("mission_start")
        original_mission_start(self, timenow, **kwargs)

    monkeypatch.setattr(LoadingMission, "mission_start", fake_mission_start)
    monkeypatch.setattr(module, "VIVIAN_REPORT", True)

    logic.special_hit_logic()
    logic.special_hit_logic()

    assert preparation_calls == [row["hit_prepared"], row["hit_prepared"]]
    assert spawn_calls == ["ViviansProphecy"]
    assert order == ["dot_start", "mission_start", "publish"]
    assert dot.started_at == 96
    assert enemy.dynamic.dynamic_dot_list == [inactive_dot, dot]
    assert dispatch_port.events == [dot_node]
    assert isinstance(cast(Any, dot_node).loading_mission, LoadingMission)
    assert harness.schedule_data.change_process_state_calls == 1
    assert "薇薇安的预言" in capsys.readouterr().out


@pytest.mark.parametrize("row", SELECTED_ROWS)
def test_quartet_preparation_errors_propagate_before_file_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    row: dict[str, object],
) -> None:
    module = _module(row)
    logic_cls = getattr(module, str(row["logic"]))
    harness = _BuffInstanceProbe(index=str(row["index"]), tick=960)
    logic = logic_cls(harness)
    template = _TemplateBuff()
    _install_existing_buff_lookup(
        monkeypatch,
        module=module,
        owner=str(row["owner"]),
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
    if row["module"] == "YixuanCinema2StunTimeLimitBonus":
        expected = row["exit_prepared"]
    elif row["module"] == "VivianCorePassiveTrigger":
        expected = row["effect_prepared"]
    else:
        expected = row["hit_prepared"]

    with pytest.raises(RuntimeError, match="missing preparation"):
        if row["module"] == "YixuanCinema2StunTimeLimitBonus":
            logic.special_exit_logic()
        elif row["module"] == "VivianCorePassiveTrigger":
            logic.special_effect_logic()
        else:
            logic.special_hit_logic()

    assert preparation_calls == [expected]
    assert harness.schedule_data.change_process_state_calls == 0
    assert harness.schedule_data.event_list == []
    assert harness.simple_start_calls == []
    assert harness.update_to_buff_0_calls == []
