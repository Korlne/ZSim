import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "scripts" / "ralph" / "record_story_trace.py"
CHECK = ROOT / "scripts" / "ralph" / "check_workflow.py"


def write_prd(repo: Path, trace_required: bool = True) -> None:
    ralph_dir = repo / "scripts" / "ralph"
    ralph_dir.mkdir(parents=True)
    (ralph_dir / "prd.json").write_text(
        json.dumps(
            {
                "project": "Trace Test",
                "branchName": "ralph/trace-test",
                "baseBranch": "main",
                "description": "Trace test PRD.",
                "userStories": [
                    {
                        "id": "US-001",
                        "title": "Trace Story",
                        "description": "Record one trace.",
                        "acceptanceCriteria": ["Run a focused check."],
                        "allowedPaths": ["src/", "scripts/ralph/"],
                        "exitCriteria": ["Validation command succeeds."],
                        "traceRequired": trace_required,
                        "priority": 1,
                        "passes": True,
                        "notes": "done",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run(command: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def test_record_story_trace_and_check_workflow(tmp_path: Path) -> None:
    write_prd(tmp_path)

    result = run(
        [
            sys.executable,
            str(RECORD),
            "--repo",
            str(tmp_path),
            "--story-id",
            "US-001",
            "--status",
            "pass",
            "--validation",
            "python -m pytest tests/test_ralph_story_trace.py -q -> exit 0",
            "--reviewer-verdict",
            "allowed paths and evidence checked",
            "--changed-file",
            "src/example.py",
            "--strict",
        ],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    latest = tmp_path / "scripts" / "ralph" / "state" / "latest-run.json"
    trace = json.loads(latest.read_text(encoding="utf-8"))
    assert trace["schema"] == "zsim-ralph-story-trace.v1"
    assert trace["allowed_paths_check"]["status"] == "pass"

    check = run([sys.executable, str(CHECK), "--repo", str(tmp_path), "--strict"], tmp_path)
    assert check.returncode == 0, check.stderr + check.stdout


def test_record_story_trace_strict_fails_outside_allowed_paths(tmp_path: Path) -> None:
    write_prd(tmp_path)

    result = run(
        [
            sys.executable,
            str(RECORD),
            "--repo",
            str(tmp_path),
            "--story-id",
            "US-001",
            "--status",
            "pass",
            "--validation",
            "check -> exit 0",
            "--changed-file",
            "README.md",
            "--strict",
        ],
        tmp_path,
    )

    assert result.returncode == 1
    trace = json.loads((tmp_path / "scripts" / "ralph" / "state" / "latest-run.json").read_text(encoding="utf-8"))
    assert trace["allowed_paths_check"]["status"] == "fail"
    assert trace["allowed_paths_check"]["outside"] == ["README.md"]


def test_check_workflow_requires_trace_for_trace_required_story(tmp_path: Path) -> None:
    write_prd(tmp_path)

    result = run([sys.executable, str(CHECK), "--repo", str(tmp_path), "--strict"], tmp_path)

    assert result.returncode == 1
    assert "US-001 passes=true but has no story trace" in result.stdout
