from __future__ import annotations

import ast
import csv
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, SupportsIndex

import pytest

import zsim.sim_progress.Buff.JudgeTools as judge_tools
from zsim.sim_progress.Buff.BuffXLogic._buff_record_base_class import BuffRecordBaseClass


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUFF_XLOGIC_ROOT = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic"
DATA_ROOT = PROJECT_ROOT / "zsim" / "data"
CONFIG_FILES = [
    PROJECT_ROOT / "zsim" / "config.json",
    PROJECT_ROOT / "zsim" / "config_example.json",
]


@dataclass(frozen=True)
class EventListPreparationFinding:
    path: str
    line: int
    expression: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: {self.expression} -> "
            "event_list=True is legacy discovery caching only; migrate planned-event "
            "writers to ScheduleDispatchPort or add an explicit compatibility note"
        )


@dataclass(frozen=True)
class ConfigEventListFinding:
    path: str
    location: str
    value: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.location}: {self.value} -> "
            "Buff data/config must not request check_preparation(event_list=True)"
        )


class _FailFastEventList(list[object]):
    def __init__(self) -> None:
        super().__init__()
        self.append_calls = 0

    def append(self, item: object) -> None:
        self.append_calls += 1
        raise AssertionError("check_preparation(event_list=True) must not append events")

    def extend(self, items: Any) -> None:
        raise AssertionError("check_preparation(event_list=True) must not create event payloads")

    def insert(self, index: SupportsIndex, item: object) -> None:
        raise AssertionError("check_preparation(event_list=True) must not create event payloads")


def _relative_path(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def _source_for(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return f"<{type(node).__name__}>"
    return " ".join(segment.strip().split())


def _call_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _may_request_event_list(value: ast.expr) -> bool:
    if isinstance(value, ast.Constant):
        return bool(value.value)
    return True


def _unpacked_event_list_values(value: ast.expr) -> list[ast.expr]:
    if not isinstance(value, ast.Dict):
        return []
    matches: list[ast.expr] = []
    for key, item in zip(value.keys, value.values, strict=True):
        if isinstance(key, ast.Constant) and key.value == "event_list":
            matches.append(item)
    return matches


def _collect_event_list_preparation_findings() -> list[EventListPreparationFinding]:
    findings: list[EventListPreparationFinding] = []
    for path in sorted(BUFF_XLOGIC_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _call_name(node.func) not in {"get_prepared", "check_preparation"}:
                continue
            for keyword in node.keywords:
                if keyword.arg == "event_list" and _may_request_event_list(keyword.value):
                    findings.append(
                        EventListPreparationFinding(
                            path=_relative_path(path),
                            line=keyword.value.lineno,
                            expression=_source_for(source, node),
                        )
                    )
                if keyword.arg is None:
                    for value in _unpacked_event_list_values(keyword.value):
                        if _may_request_event_list(value):
                            findings.append(
                                EventListPreparationFinding(
                                    path=_relative_path(path),
                                    line=value.lineno,
                                    expression=_source_for(source, node),
                                )
                            )
    return findings


def _contains_event_list_token(value: object) -> bool:
    return isinstance(value, str) and "event_list" in value


def _walk_config_value(
    path: Path, value: object, location: str = "$"
) -> list[ConfigEventListFinding]:
    findings: list[ConfigEventListFinding] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_location = f"{location}.{key}"
            if _contains_event_list_token(str(key)):
                findings.append(
                    ConfigEventListFinding(_relative_path(path), child_location, str(key))
                )
            findings.extend(_walk_config_value(path, item, child_location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_walk_config_value(path, item, f"{location}[{index}]"))
    elif _contains_event_list_token(value):
        findings.append(ConfigEventListFinding(_relative_path(path), location, str(value)))
    return findings


def _collect_csv_event_list_findings(path: Path) -> list[ConfigEventListFinding]:
    findings: list[ConfigEventListFinding] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row_index, row in enumerate(csv.reader(handle), start=1):
            for column_index, cell in enumerate(row, start=1):
                if "event_list" in cell:
                    findings.append(
                        ConfigEventListFinding(
                            _relative_path(path),
                            f"row {row_index}, column {column_index}",
                            cell,
                        )
                    )
    return findings


def _collect_config_event_list_findings() -> list[ConfigEventListFinding]:
    findings: list[ConfigEventListFinding] = []
    config_paths = [path for path in CONFIG_FILES if path.exists()]
    config_paths.extend(
        path
        for path in sorted(DATA_ROOT.rglob("*"))
        if path.suffix.lower() in {".csv", ".json", ".toml"}
    )
    for path in config_paths:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            findings.extend(_collect_csv_event_list_findings(path))
        elif suffix == ".json":
            findings.extend(
                _walk_config_value(path, json.loads(path.read_text(encoding="utf-8")))
            )
        elif suffix == ".toml":
            findings.extend(
                _walk_config_value(path, tomllib.loads(path.read_text(encoding="utf-8")))
            )
    return findings


def test_check_preparation_event_list_true_only_caches_legacy_queue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = BuffRecordBaseClass()
    legacy_event_list = _FailFastEventList()
    sim_instance = object()
    buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    buff_instance = SimpleNamespace(sim_instance=sim_instance)
    lookup_calls: list[object] = []

    def fake_find_event_list(*, sim_instance: object | None = None) -> list[object]:
        lookup_calls.append(sim_instance)
        return legacy_event_list

    monkeypatch.setattr(judge_tools, "find_event_list", fake_find_event_list)

    result = judge_tools.check_preparation(
        buff_0=buff_0,
        buff_instance=buff_instance,
        event_list=True,
    )

    assert result is None
    assert lookup_calls == [sim_instance]
    assert record.event_list is legacy_event_list
    assert legacy_event_list == []
    assert legacy_event_list.append_calls == 0


def test_check_preparation_event_list_true_reuses_cached_queue_without_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = BuffRecordBaseClass()
    cached_event_list = _FailFastEventList()
    record.event_list = cached_event_list
    buff_0 = SimpleNamespace(history=SimpleNamespace(record=record))
    buff_instance = SimpleNamespace(sim_instance=object())

    def fail_find_event_list(*args: object, **kwargs: object) -> list[object]:
        raise AssertionError("cached record.event_list should not trigger legacy lookup")

    monkeypatch.setattr(judge_tools, "find_event_list", fail_find_event_list)

    judge_tools.check_preparation(
        buff_0=buff_0,
        buff_instance=buff_instance,
        event_list=True,
    )

    assert record.event_list is cached_event_list
    assert cached_event_list == []
    assert cached_event_list.append_calls == 0


def test_buff_xlogic_does_not_request_event_list_preparation_cache() -> None:
    findings = _collect_event_list_preparation_findings()

    assert not findings, (
        "BuffXLogic callsites still request legacy event_list preparation:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_buff_data_and_config_do_not_request_event_list_preparation_cache() -> None:
    findings = _collect_config_event_list_findings()

    assert not findings, (
        "Buff data/config files still expose event_list preparation keys:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )
