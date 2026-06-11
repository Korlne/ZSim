from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from zsim.models.event_enums import ListenerBroadcastSignal as LBS
from zsim.sim_progress.ScheduledEvent.buff_runtime import BuffRuntimeReadPort
from zsim.sim_progress.ScheduledEvent.event_handlers.context import EventContext
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import abloom as abloom_module
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import anomaly as anomaly_module
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import disorder as disorder_module
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers import (
    polarity_disorder as polarity_disorder_module,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.abloom import AbloomEventHandler
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.anomaly import AnomalyEventHandler
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.disorder import (
    DisorderEventHandler,
)
from zsim.sim_progress.ScheduledEvent.event_handlers.handlers.polarity_disorder import (
    PolarityDisorderEventHandler,
)
from zsim.sim_progress.anomaly_bar import AnomalyBar
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
    DirgeOfDestinyAnomaly,
    Disorder,
    NewAnomaly,
    PolarityDisorder,
)


class _RuntimeViewProbe(BuffRuntimeReadPort):
    def __init__(self, dynamic_buff, exist_buff_dict, *, allow_legacy: bool) -> None:
        self.active_buff_view = {
            beneficiary: tuple(buffs) for beneficiary, buffs in dynamic_buff.items()
        }
        self.exist_buff_snapshot_view = {
            beneficiary: dict(buff_dict) for beneficiary, buff_dict in exist_buff_dict.items()
        }
        self.legacy_dynamic_buff = dynamic_buff
        self.legacy_exist_buff_dict = exist_buff_dict
        self.allow_legacy = allow_legacy
        self.active_buff_calls = 0
        self.active_view_calls = 0
        self.snapshot_view_calls = 0
        self.legacy_dynamic_calls = 0
        self.legacy_exist_calls = 0

    def get_active_buffs(self, beneficiary: str):
        self.active_buff_calls += 1
        return self.active_buff_view.get(beneficiary, ())

    def get_active_buff_view(self):
        self.active_view_calls += 1
        return self.active_buff_view

    def get_exist_buff_snapshot(self, beneficiary: str):
        return self.exist_buff_snapshot_view.get(beneficiary, {})

    def get_exist_buff_snapshot_view(self):
        self.snapshot_view_calls += 1
        return self.exist_buff_snapshot_view

    def get_legacy_dynamic_buff_dict(self):
        self.legacy_dynamic_calls += 1
        if not self.allow_legacy:
            raise AssertionError("legacy dynamic buff access should not happen on read-only path")
        return self.legacy_dynamic_buff

    def get_legacy_exist_buff_dict(self):
        self.legacy_exist_calls += 1
        if not self.allow_legacy:
            raise AssertionError("legacy exist buff access should not happen on read-only path")
        return self.legacy_exist_buff_dict


def _build_context(
    runtime_view: BuffRuntimeReadPort,
    runtime_command_port: Any = None,
) -> tuple[EventContext, list[dict]]:
    broadcasts: list[dict] = []
    enemy = SimpleNamespace(
        dynamic=SimpleNamespace(get_status=lambda: {}),
        update_stun=lambda stun: broadcasts.append({"stun": stun}),
    )
    sim_instance = SimpleNamespace(
        listener_manager=SimpleNamespace(
            broadcast_event=lambda **kwargs: broadcasts.append(kwargs),
        ),
    )
    context = EventContext(
        data=SimpleNamespace(),
        tick=10,
        enemy=enemy,
        buff_runtime_view=runtime_view,
        runtime_command_port=runtime_command_port or SimpleNamespace(),
        action_stack=SimpleNamespace(),
        sim_instance=sim_instance,
    )
    return context, broadcasts


def _build_copied_output_source(
    sim_instance: Any,
    *,
    element_type: int,
    rename_tag: str | None = None,
) -> AnomalyBar:
    bar = AnomalyBar(sim_instance=sim_instance, element_type=element_type)
    bar.rename_tag = rename_tag
    bar.max_duration = 600
    bar.last_active = 100
    bar.active = True
    return bar


def _build_activation(skill_tag: str = "1001_HANDLER_PAYLOAD"):
    return SimpleNamespace(
        char_name="handler-copied-output",
        skill_tag=skill_tag,
        skill=SimpleNamespace(char_obj=SimpleNamespace(CID=1001)),
    )


class _DurationBuffProbe:
    def __init__(
        self,
        *,
        index: str,
        active: bool,
        count: int,
        effect_dct: dict[str, float],
    ) -> None:
        self.ft = SimpleNamespace(index=index)
        self.dy = SimpleNamespace(active=active, count=count)
        self.effect_dct = effect_dct


class _FailFastLegacyDynamicBuff(dict):
    def get(self, *args, **kwargs):
        raise AssertionError("runtime view path should not read legacy dynamic_buff_dict")


def _build_duration_bar() -> AnomalyBar:
    bar = AnomalyBar(sim_instance=SimpleNamespace(), element_type=3)
    bar.basic_max_duration = 600
    bar.duration_buff_list = ["Buff-角色-丽娜-组队被动-延长感电"]
    bar.duration_buff_key_list = [
        "感电时间延长",
        "所有异常时间延长百分比",
    ]
    return bar


def test_anomaly_bar_duration_read_uses_runtime_view_without_legacy_dynamic_container():
    target_index = "Buff-角色-丽娜-组队被动-延长感电"
    matching_buff = _DurationBuffProbe(
        index=target_index,
        active=True,
        count=2,
        effect_dct={
            "感电时间延长": 30,
            "所有异常时间延长百分比": 0.1,
        },
    )
    inactive_buff = _DurationBuffProbe(
        index=target_index,
        active=False,
        count=99,
        effect_dct={
            "感电时间延长": 999,
            "所有异常时间延长百分比": 9.9,
        },
    )
    unrelated_buff = _DurationBuffProbe(
        index="Buff-其他",
        active=True,
        count=99,
        effect_dct={
            "感电时间延长": 999,
            "所有异常时间延长百分比": 9.9,
        },
    )
    enemy_buffs = [matching_buff, inactive_buff, unrelated_buff]
    skill_node = SimpleNamespace(skill_tag="1001_TEST")

    legacy_bar = _build_duration_bar()
    legacy_bar.change_info_cause_active(
        10,
        skill_node=skill_node,
        dynamic_buff_dict={"enemy": enemy_buffs},
    )

    runtime_view = _RuntimeViewProbe({"enemy": enemy_buffs}, {}, allow_legacy=False)
    runtime_bar = _build_duration_bar()
    runtime_bar.change_info_cause_active(
        10,
        skill_node=skill_node,
        dynamic_buff_dict=_FailFastLegacyDynamicBuff(),
        buff_runtime_view=runtime_view,
    )

    assert runtime_bar.max_duration == legacy_bar.max_duration == 780
    assert runtime_view.active_buff_calls == 1
    assert runtime_view.active_view_calls == 0
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0


def test_abloom_handler_reads_active_buff_view_without_legacy_dynamic_container(
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_view = _RuntimeViewProbe(
        {"alpha": [object()], "enemy": [object()]}, {}, allow_legacy=False
    )
    context, _ = _build_context(runtime_view)
    captured: dict[str, object] = {}

    class _FakeCalculator:
        def __init__(self, *, dynamic_buff, **kwargs) -> None:
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 12.34

    monkeypatch.setattr(abloom_module, "CalAbloom", _FakeCalculator)
    monkeypatch.setattr(abloom_module.Report, "report_dmg_result", lambda **kwargs: None)

    event = SimpleNamespace(element_type=1, UUID="abloom")
    AbloomEventHandler().handle(event, context)

    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0


@pytest.mark.parametrize(
    ("module", "handler_cls", "calculator_name"),
    [
        (disorder_module, DisorderEventHandler, "CalDisorder"),
        (polarity_disorder_module, PolarityDisorderEventHandler, "CalPolarityDisorder"),
    ],
)
def test_disorder_family_handlers_read_runtime_view_without_legacy_dynamic_container(
    monkeypatch: pytest.MonkeyPatch,
    module,
    handler_cls,
    calculator_name: str,
):
    runtime_view = _RuntimeViewProbe(
        {"alpha": [object()], "enemy": [object()]}, {}, allow_legacy=False
    )
    context, broadcasts = _build_context(runtime_view)
    captured: dict[str, object] = {}

    class _FakeCalculator:
        def __init__(self, *, dynamic_buff, **kwargs) -> None:
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 23.45

        def cal_disorder_stun(self):
            return 6.78

    monkeypatch.setattr(module, calculator_name, _FakeCalculator)
    monkeypatch.setattr(module.Report, "report_dmg_result", lambda **kwargs: None)

    event = SimpleNamespace(element_type=1, UUID="disorder")
    handler_cls().handle(event, context)

    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0
    assert broadcasts


def test_copied_anomaly_handler_reports_payload_fields_separate_from_settle_port(
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_view = _RuntimeViewProbe(
        {"alpha": [object()], "enemy": [object()]}, {}, allow_legacy=False
    )
    captured: dict[str, object] = {}
    reports: list[dict[str, object]] = []

    class _RuntimeCommandPortProbe:
        def update_anomaly(self, **kwargs) -> None:
            raise AssertionError("report payload path should not issue update_anomaly")

        def settle_buffs(self, *, tick, enemy, skill_node=None, anomaly_bar=None) -> None:
            captured["settle_tick"] = tick
            captured["settle_enemy"] = enemy
            captured["settle_skill_node"] = skill_node
            captured["settle_anomaly_bar"] = anomaly_bar

    context, broadcasts = _build_context(
        runtime_view,
        runtime_command_port=_RuntimeCommandPortProbe(),
    )
    context.enemy.dynamic.get_status = lambda: {"enemy_status": "runtime"}

    class _FakeCalculator:
        def __init__(self, *, anomaly_obj, dynamic_buff, **kwargs) -> None:
            captured["calculator_event"] = anomaly_obj
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 12.346

    monkeypatch.setattr(anomaly_module, "CalAnomaly", _FakeCalculator)
    monkeypatch.setattr(
        anomaly_module.Report,
        "report_dmg_result",
        lambda **kwargs: reports.append(kwargs),
    )

    source = _build_copied_output_source(
        context.sim_instance,
        element_type=4,
        rename_tag="copied-anomaly-report",
    )
    event = NewAnomaly(
        source,
        active_by=_build_activation(),
        sim_instance=context.sim_instance,
    )
    event.UUID = "new-anomaly-report-uuid"

    AnomalyEventHandler().handle(event, context)

    assert reports == [
        {
            "tick": 10,
            "skill_tag": "copied-anomaly-report",
            "element_type": 4,
            "dmg_expect": 12.35,
            "is_anomaly": True,
            "dmg_crit": 12.35,
            "stun": 0,
            "buildup": 0,
            "enemy_status": "runtime",
            "UUID": "new-anomaly-report-uuid",
        }
    ]
    assert broadcasts == []
    assert captured["calculator_event"] is event
    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert captured["settle_tick"] == 10
    assert captured["settle_enemy"] is context.enemy
    assert captured["settle_skill_node"] is None
    assert captured["settle_anomaly_bar"] is event
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0


def test_abloom_copied_output_handler_reports_payload_fields(
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_view = _RuntimeViewProbe(
        {"alpha": [object()], "enemy": [object()]}, {}, allow_legacy=False
    )
    context, broadcasts = _build_context(runtime_view)
    context.enemy.dynamic.get_status = lambda: {"enemy_status": "runtime"}
    captured: dict[str, object] = {}
    reports: list[dict[str, object]] = []

    class _FakeCalculator:
        def __init__(self, *, abloom_obj, dynamic_buff, **kwargs) -> None:
            captured["calculator_event"] = abloom_obj
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 45.678

    monkeypatch.setattr(abloom_module, "CalAbloom", _FakeCalculator)
    monkeypatch.setattr(
        abloom_module.Report,
        "report_dmg_result",
        lambda **kwargs: reports.append(kwargs),
    )

    source = _build_copied_output_source(context.sim_instance, element_type=1)
    event = DirgeOfDestinyAnomaly(
        source,
        active_by=_build_activation("1001_ABLOOM"),
        sim_instance=context.sim_instance,
    )
    event.UUID = "abloom-report-uuid"

    AbloomEventHandler().handle(event, context)

    assert reports == [
        {
            "tick": 10,
            "element_type": 1,
            "skill_tag": "异放",
            "dmg_expect": 45.68,
            "is_anomaly": True,
            "dmg_crit": 45.68,
            "stun": 0,
            "buildup": 0,
            "enemy_status": "runtime",
            "UUID": "abloom-report-uuid",
        }
    ]
    assert broadcasts == []
    assert captured["calculator_event"] is event
    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0


def test_disorder_handler_reports_payload_and_listener_fields(
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_view = _RuntimeViewProbe(
        {"alpha": [object()], "enemy": [object()]}, {}, allow_legacy=False
    )
    context, broadcasts = _build_context(runtime_view)
    context.enemy.dynamic.get_status = lambda: {"enemy_status": "runtime"}
    captured: dict[str, object] = {}
    reports: list[dict[str, object]] = []

    class _FakeCalculator:
        def __init__(self, *, disorder_obj, dynamic_buff, **kwargs) -> None:
            captured["calculator_event"] = disorder_obj
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 23.456

        def cal_disorder_stun(self):
            return 6.789

    monkeypatch.setattr(disorder_module, "CalDisorder", _FakeCalculator)
    monkeypatch.setattr(
        disorder_module.Report,
        "report_dmg_result",
        lambda **kwargs: reports.append(kwargs),
    )

    source = _build_copied_output_source(context.sim_instance, element_type=3)
    event = Disorder(
        source,
        active_by=_build_activation("1001_DISORDER"),
        sim_instance=context.sim_instance,
    )
    event.UUID = "disorder-report-uuid"

    DisorderEventHandler().handle(event, context)

    assert reports == [
        {
            "tick": 10,
            "element_type": 3,
            "dmg_expect": 23.46,
            "dmg_crit": 23.46,
            "is_anomaly": True,
            "is_disorder": True,
            "stun": 6.79,
            "buildup": 0,
            "enemy_status": "runtime",
            "UUID": "disorder-report-uuid",
        }
    ]
    assert "skill_tag" not in reports[0]
    assert broadcasts[0] == {"event": event, "signal": LBS.DISORDER_SETTLED}
    assert broadcasts[1]["stun"] == pytest.approx(6.789)
    assert captured["calculator_event"] is event
    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0


def test_polarity_disorder_handler_reports_payload_and_listener_fields(
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_view = _RuntimeViewProbe(
        {"alpha": [object()], "enemy": [object()]}, {}, allow_legacy=False
    )
    context, broadcasts = _build_context(runtime_view)
    context.enemy.dynamic.get_status = lambda: {"enemy_status": "runtime"}
    captured: dict[str, object] = {}
    reports: list[dict[str, object]] = []

    class _FakeCalculator:
        def __init__(self, *, disorder_obj, dynamic_buff, **kwargs) -> None:
            captured["calculator_event"] = disorder_obj
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 34.567

    monkeypatch.setattr(polarity_disorder_module, "CalPolarityDisorder", _FakeCalculator)
    monkeypatch.setattr(
        polarity_disorder_module.Report,
        "report_dmg_result",
        lambda **kwargs: reports.append(kwargs),
    )

    source = _build_copied_output_source(context.sim_instance, element_type=6)
    event = PolarityDisorder(
        source,
        1.6,
        active_by=_build_activation("1001_POLARITY"),
        sim_instance=context.sim_instance,
    )
    event.UUID = "polarity-report-uuid"

    PolarityDisorderEventHandler().handle(event, context)

    assert reports == [
        {
            "tick": 10,
            "element_type": 6,
            "skill_tag": "极性紊乱",
            "dmg_expect": 34.57,
            "dmg_crit": 34.57,
            "is_anomaly": True,
            "is_disorder": True,
            "stun": 0,
            "buildup": 0,
            "enemy_status": "runtime",
            "UUID": "polarity-report-uuid",
        }
    ]
    assert broadcasts == [{"event": event, "signal": LBS.DISORDER_SETTLED}]
    assert captured["calculator_event"] is event
    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0


def test_anomaly_handler_uses_runtime_command_port_for_settle_boundary(
    monkeypatch: pytest.MonkeyPatch,
):
    legacy_dynamic_buff = {"alpha": [object()], "enemy": [object()]}
    legacy_exist_buff_dict = {"alpha": {"alpha-buff": object()}, "enemy": {}}
    runtime_view = _RuntimeViewProbe(
        legacy_dynamic_buff,
        legacy_exist_buff_dict,
        allow_legacy=False,
    )
    captured: dict[str, object] = {}

    class _RuntimeCommandPortProbe:
        def update_anomaly(self, **kwargs) -> None:
            raise AssertionError("anomaly handler should not issue update_anomaly")

        def settle_buffs(self, *, tick, enemy, skill_node=None, anomaly_bar=None) -> None:
            captured["settle_tick"] = tick
            captured["settle_enemy"] = enemy
            captured["settle_skill_node"] = skill_node
            captured["settle_anomaly_bar"] = anomaly_bar

    runtime_command_port = _RuntimeCommandPortProbe()
    context, _ = _build_context(runtime_view, runtime_command_port=runtime_command_port)

    class _FakeCalculator:
        def __init__(self, *, dynamic_buff, **kwargs) -> None:
            captured["dynamic_buff"] = dynamic_buff

        def cal_anomaly_dmg(self):
            return 34.56

    monkeypatch.setattr(anomaly_module, "CalAnomaly", _FakeCalculator)
    monkeypatch.setattr(anomaly_module.Report, "report_dmg_result", lambda **kwargs: None)

    handler = AnomalyEventHandler()
    monkeypatch.setattr(handler, "_validate_event", lambda *args, **kwargs: None)
    event = SimpleNamespace(rename=False, rename_tag=None, element_type=1, UUID="anomaly")

    handler.handle(event, context)

    assert captured["dynamic_buff"] is runtime_view.active_buff_view
    assert captured["settle_tick"] == 10
    assert captured["settle_enemy"] is context.enemy
    assert captured["settle_skill_node"] is None
    assert captured["settle_anomaly_bar"] is event
    assert runtime_view.active_view_calls == 1
    assert runtime_view.legacy_dynamic_calls == 0
    assert runtime_view.legacy_exist_calls == 0
