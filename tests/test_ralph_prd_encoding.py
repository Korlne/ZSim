import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_auto_prd_runner_has_no_non_ascii_literals() -> None:
    script = ROOT / "scripts" / "ralph" / "auto-prd-ralph-codex.ps1"
    text = script.read_text(encoding="utf-8")

    offenders = [
        f"{line_no}: {line}"
        for line_no, line in enumerate(text.splitlines(), 1)
        if any(ord(char) > 127 for char in line)
    ]

    assert offenders == []


def test_ralph_prd_json_has_valid_encoding_and_doc_paths() -> None:
    prd_path = ROOT / "scripts" / "ralph" / "prd.json"
    text = prd_path.read_bytes().decode("utf-8")
    json.loads(text)

    assert "\ufffd" not in text
    assert not any(0xE000 <= ord(char) <= 0xF8FF for char in text)

    doc_refs = {
        match.group(0).rstrip(".;:")
        for match in re.finditer(r"docs[\\/][^`\"'\s,\]\)]+", text)
    }
    missing = [
        doc_ref
        for doc_ref in sorted(doc_refs)
        if re.search(r"(\.md|\?md)$", doc_ref)
        and not (ROOT / doc_ref.replace("\\", "/")).is_file()
    ]

    assert missing == []
