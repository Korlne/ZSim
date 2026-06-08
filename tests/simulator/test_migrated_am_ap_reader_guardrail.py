from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MIGRATED_AM_AP_READER_FILES = (
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "AliceAdditionalAbilityApBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "JaneCinema1APTransToDmgBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "JaneCoreSkillStrikeCritRateBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "JanePassionStateAPTransToATK.py",
)

RETAINED_FORMULA_SNAPSHOT_FILES = {
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "Calculator.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "CalAnomaly.py",
}

FORBIDDEN_ANOMALY_CALCULATOR_METHODS = {"cal_am", "cal_ap"}


@dataclass(frozen=True)
class LegacyAnomalyReadFinding:
    path: str
    line: int
    kind: str
    expression: str

    def message(self) -> str:
        return f"{self.path}:{self.line}: {self.kind}: {self.expression}"


class MigratedAnomalyReaderVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[LegacyAnomalyReadFinding] = []
        self._multiplier_aliases = {"MultiplierData", "Mul"}
        self._calculator_aliases = {"Calculator", "Cal"}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module.endswith("Calculator"):
            for alias in node.names:
                if alias.name == "MultiplierData":
                    self._multiplier_aliases.add(alias.asname or alias.name)
                    self._add_finding(
                        line=getattr(alias, "lineno", node.lineno),
                        kind="legacy_multiplier_import",
                        expression=self._source_for(alias),
                    )
                if alias.name == "Calculator":
                    self._calculator_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_multiplier_constructor(node.func):
            self._add_finding(
                line=node.lineno,
                kind="legacy_multiplier_constructor",
                expression=self._source_for(node),
            )
        if self._is_direct_anomaly_calculator_call(node.func):
            self._add_finding(
                line=node.lineno,
                kind="legacy_anomaly_calculator_call",
                expression=self._source_for(node.func),
            )
        self.generic_visit(node)

    def _is_multiplier_constructor(self, func: ast.AST) -> bool:
        if isinstance(func, ast.Name):
            return func.id in self._multiplier_aliases
        if isinstance(func, ast.Attribute):
            return func.attr in self._multiplier_aliases
        return False

    def _is_direct_anomaly_calculator_call(self, func: ast.AST) -> bool:
        chain = self._attribute_chain(func)
        return (
            len(chain) >= 3
            and chain[-1] in FORBIDDEN_ANOMALY_CALCULATOR_METHODS
            and chain[-2] == "AnomalyMul"
            and chain[-3] in self._calculator_aliases
        )

    def _attribute_chain(self, node: ast.AST) -> list[str]:
        parts: list[str] = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return list(reversed(parts))

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        self.findings.append(
            LegacyAnomalyReadFinding(
                path=self.path.relative_to(PROJECT_ROOT).as_posix(),
                line=line,
                kind=kind,
                expression=self._normalize(expression),
            )
        )

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())


def _collect_legacy_anomaly_read_findings_from_source(
    path: Path, source: str
) -> list[LegacyAnomalyReadFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = MigratedAnomalyReaderVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_migrated_file_findings() -> list[LegacyAnomalyReadFinding]:
    findings: list[LegacyAnomalyReadFinding] = []
    for path in MIGRATED_AM_AP_READER_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_legacy_anomaly_read_findings_from_source(path, source))
    return findings


def test_migrated_am_ap_files_do_not_use_legacy_anomaly_reads() -> None:
    findings = _collect_migrated_file_findings()

    assert not findings, (
        "Migrated P2-A AM/AP files reintroduced direct legacy anomaly reads:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_migrated_am_ap_guardrail_scope_is_exact_root_file_set() -> None:
    scanned_files = {
        path.relative_to(PROJECT_ROOT).as_posix() for path in MIGRATED_AM_AP_READER_FILES
    }

    assert scanned_files == {
        "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
    }
    assert all(".codex_worktrees" not in path.parts for path in MIGRATED_AM_AP_READER_FILES)
    assert all(path.is_file() for path in MIGRATED_AM_AP_READER_FILES)
    assert not RETAINED_FORMULA_SNAPSHOT_FILES & set(MIGRATED_AM_AP_READER_FILES)


def test_migrated_am_ap_guardrail_reports_legacy_patterns() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.Calculator import Calculator, MultiplierData as Mul\n"
        "from zsim.sim_progress.ScheduledEvent.Calculator import Calculator as Cal\n"
        "def legacy(record):\n"
        "    mul_data = Mul(record.enemy, record.dynamic_buff_list, record.char)\n"
        "    return Calculator.AnomalyMul.cal_am(mul_data) + Cal.AnomalyMul.cal_ap(mul_data)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_migrated_am_ap_fixture.py"
    )
    findings = _collect_legacy_anomaly_read_findings_from_source(path, source)
    messages = [finding.message() for finding in findings]

    assert len(findings) == 4
    assert any("legacy_multiplier_import: MultiplierData as Mul" in message for message in messages)
    assert any("legacy_multiplier_constructor: Mul(" in message for message in messages)
    assert any(
        "legacy_anomaly_calculator_call: Calculator.AnomalyMul.cal_am" in message
        for message in messages
    )
    assert any(
        "legacy_anomaly_calculator_call: Cal.AnomalyMul.cal_ap" in message
        for message in messages
    )


def test_migrated_am_ap_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''MultiplierData(...) MultiplierData as Mul Mul(...) Calculator.AnomalyMul.cal_am'''\n"
        "    # Cal.AnomalyMul.cal_ap remains a historical note only.\n"
        "    return None\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_migrated_am_ap_fixture.py"
    )

    assert _collect_legacy_anomaly_read_findings_from_source(path, source) == []
