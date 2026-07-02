from __future__ import annotations

import ast
from dataclasses import dataclass

from .unsupported_patterns import UnsupportedXLogicPattern


@dataclass(frozen=True, slots=True)
class XLogicClassification:
    xlogic_path: str
    triggers: tuple[str, ...]
    conditions: tuple[str, ...]
    reads: tuple[str, ...]
    effects: tuple[str, ...]
    state: tuple[str, ...]
    unsupported_patterns: tuple[UnsupportedXLogicPattern, ...]
    migration_wave: str

    @property
    def is_supported_by_low_risk_blocks(self) -> bool:
        return not self.unsupported_patterns and bool(self.triggers or self.conditions or self.effects)


def classify_xlogic_source(*, xlogic_path: str, source: str) -> XLogicClassification:
    lowered = source.lower()
    unsupported: list[UnsupportedXLogicPattern] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        unsupported.append(
            UnsupportedXLogicPattern(
                pattern_id="parse_error",
                reason="XLogic source could not be parsed into an AST.",
                evidence=f"{exc.msg} at line {exc.lineno}",
            )
        )
        tree = ast.Module(body=[], type_ignores=[])

    names = _names_from_ast(tree)
    text = " ".join((lowered, " ".join(name.lower() for name in names)))

    triggers: list[str] = []
    conditions: list[str] = []
    reads: list[str] = []
    effects: list[str] = []
    state: list[str] = []

    if "xhit" in text or "skill" in text or "hit" in text:
        triggers.append("trigger.skill_hit")
    if "refresh" in text or "fresh" in text:
        triggers.append("trigger.buff_refresh")
    if "character" in text or "char" in text or "owner" in text:
        conditions.append("condition.character_identity")
    if "buff" in text and ("active" in text or "count" in text):
        conditions.append("condition.buff_active")
    if "tick" in text:
        reads.append("read.current_tick")
    if "buff_runtime" in text or "buff_runtime_view" in text:
        reads.append("read.buff_runtime_view")
    if "start" in text or "add_buff" in text:
        effects.append("effect.start_buff")
    if "count" in text or "stack" in text:
        effects.append("effect.update_buff_count")
    if "cooldown" in text or "cd" in text:
        state.append("state.cooldown_gate")
    if "record" in text or "last" in text:
        state.append("state.last_active_tick")

    _record_unsupported(
        unsupported,
        text=text,
        token=("runtimecommand", "scheduledispatch", "schedule", "event_list"),
        pattern_id="runtime_command_or_scheduled_producer",
        reason="Runtime command or scheduled producer behavior needs a dedicated building block.",
    )
    _record_unsupported(
        unsupported,
        text=text,
        token=("enemy", "anomaly", "dot"),
        pattern_id="enemy_anomaly_or_dot_read",
        reason="Enemy, anomaly, or DOT reads need dedicated graph read/condition blocks.",
    )
    _record_unsupported(
        unsupported,
        text=text,
        token=("manager", "additional_attack", "quickassist", "qte"),
        pattern_id="character_manager_side_effect",
        reason="Character manager or additional attack side effects need dedicated effect blocks.",
    )

    migration_wave = "low-risk"
    if unsupported:
        migration_wave = "unsupported-pattern"
    elif state:
        migration_wave = "record-cooldown-stack"

    return XLogicClassification(
        xlogic_path=xlogic_path,
        triggers=tuple(dict.fromkeys(triggers)),
        conditions=tuple(dict.fromkeys(conditions)),
        reads=tuple(dict.fromkeys(reads)),
        effects=tuple(dict.fromkeys(effects)),
        state=tuple(dict.fromkeys(state)),
        unsupported_patterns=tuple(unsupported),
        migration_wave=migration_wave,
    )


def _names_from_ast(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            names.append(node.name)
    return tuple(names)


def _record_unsupported(
    unsupported: list[UnsupportedXLogicPattern],
    *,
    text: str,
    token: tuple[str, ...],
    pattern_id: str,
    reason: str,
) -> None:
    for item in token:
        if item in text:
            unsupported.append(UnsupportedXLogicPattern(pattern_id, reason, item))
            return
