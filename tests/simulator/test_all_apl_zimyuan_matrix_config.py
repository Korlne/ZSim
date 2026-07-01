from __future__ import annotations

from pathlib import Path

from scripts.buff_agents.run_all_apl_zimyuan_parity import (
    DEFAULT_STOP_TICK,
    MATRIX_ROWS,
    _remove_existing_path,
    _rng_seed,
    _session_id,
    build_common_cfg,
    build_matrix,
    compare_artifact,
)


OLD_ROOT = Path("C:/Users/59275/Desktop/Korlne/zimyuan")
NEW_ROOT = Path(".")


def test_all_apl_matrix_has_expected_rows_and_stop_tick() -> None:
    matrix = build_matrix(OLD_ROOT, NEW_ROOT, DEFAULT_STOP_TICK)

    assert matrix["row_count"] == 8
    assert [row["apl_filename"] for row in matrix["rows"]] == [
        "爱丽丝-柚叶-简.toml",
        "大安比扳机双人组.toml",
        "莱特-扳机-雨果.toml",
        "青衣-丽娜-雅.toml",
        "薇薇安-柳-耀嘉音.toml",
        "席德-大安比-扳机.toml",
        "仪玄-耀嘉音-扳机.toml",
        "柚叶-雅-薇薇安.toml",
    ]
    assert {row["stop_tick"] for row in matrix["rows"]} == {10800}


def test_zero_anby_trigger_row_uses_rina_as_third_commoncfg_character() -> None:
    row = next(row for row in MATRIX_ROWS if row.row_id == "apl-zeroanby-trigger-rina")

    common_cfg = build_common_cfg(root=NEW_ROOT, row=row, session_id="1")

    assert [character["name"] for character in common_cfg["char_config"]] == [
        "零号·安比",
        "扳机",
        "丽娜",
    ]


def test_every_matrix_commoncfg_uses_shared_enemy_and_three_characters() -> None:
    for row in MATRIX_ROWS:
        common_cfg = build_common_cfg(root=NEW_ROOT, row=row, session_id="1")

        assert len(common_cfg["char_config"]) == 3
        assert common_cfg["enemy_config"] == {
            "index_id": 11412,
            "adjustment_id": 22412,
            "difficulty": 8.74,
        }
        assert common_cfg["apl_path"] == f"./zsim/data/APLData/{row.apl_filename}"


def test_alice_row_has_shared_character_config_after_manual_copy() -> None:
    matrix = build_matrix(OLD_ROOT, NEW_ROOT, DEFAULT_STOP_TICK)
    alice_row = next(row for row in matrix["rows"] if row["apl_filename"] == "爱丽丝-柚叶-简.toml")

    assert alice_row["old_missing_character_config"] == []
    assert alice_row["new_missing_character_config"] == []
    assert alice_row["selected_characters_have_config"] is True

    row = next(row for row in MATRIX_ROWS if row.row_id == "apl-alice-yuzuha-jane")
    common_cfg = build_common_cfg(root=NEW_ROOT, row=row, session_id="1")

    assert [character["name"] for character in common_cfg["char_config"]] == [
        "爱丽丝",
        "柚叶",
        "简",
    ]


def test_parity_runner_uses_deterministic_row_session_ids() -> None:
    row = next(row for row in MATRIX_ROWS if row.row_id == "apl-lighter-trigger-hugo")

    first = _session_id(row, DEFAULT_STOP_TICK)
    second = _session_id(row, DEFAULT_STOP_TICK)

    assert first == second
    assert first.isdecimal()
    assert 10**18 <= int(first) < 2 * 10**18


def test_parity_runner_uses_deterministic_row_rng_seeds() -> None:
    row = next(row for row in MATRIX_ROWS if row.row_id == "apl-lighter-trigger-hugo")

    first = _rng_seed(row, DEFAULT_STOP_TICK)
    second = _rng_seed(row, DEFAULT_STOP_TICK)

    assert first == second
    assert isinstance(first, int)
    assert 0 <= first < 2**31 - 1


def test_parity_runner_removes_stale_session_artifacts(tmp_path: Path) -> None:
    stale_result = tmp_path / "result"
    stale_result.mkdir()
    (stale_result / "old.txt").write_text("stale", encoding="utf-8")
    stale_log = tmp_path / "session.log"
    stale_log.write_text("stale", encoding="utf-8")
    missing = tmp_path / "missing"

    _remove_existing_path(stale_result)
    _remove_existing_path(stale_log)
    _remove_existing_path(missing)

    assert not stale_result.exists()
    assert not stale_log.exists()
    assert not missing.exists()


def test_damage_attribution_compare_ignores_result_serialization_noise(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    baseline.mkdir()
    candidate.mkdir()
    (baseline / "damage_attribution.json").write_text(
        '{"扳机": {"direct_damage": 2601203.0600000033}}',
        encoding="utf-8",
    )
    (candidate / "damage_attribution.json").write_text(
        '{"扳机": {"direct_damage": 2601203.0600000024}}',
        encoding="utf-8",
    )

    diff = compare_artifact(
        baseline_dir=baseline,
        candidate_dir=candidate,
        artifact="damage_attribution.json",
    )

    assert diff.matches is True
    assert diff.domain_report == {
        "raw_matches": False,
        "normalized_matches": True,
    }


def test_damage_attribution_compare_keeps_behavior_sized_differences_red(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    baseline.mkdir()
    candidate.mkdir()
    (baseline / "damage_attribution.json").write_text(
        '{"扳机": {"direct_damage": 1906888.12}}',
        encoding="utf-8",
    )
    (candidate / "damage_attribution.json").write_text(
        '{"扳机": {"direct_damage": 1921550.81}}',
        encoding="utf-8",
    )

    diff = compare_artifact(
        baseline_dir=baseline,
        candidate_dir=candidate,
        artifact="damage_attribution.json",
    )

    assert diff.matches is False
    assert diff.changed_sample == [
        {
            "path": "$.扳机.direct_damage",
            "old": 1906888.12,
            "new": 1921550.81,
            "reason": "value",
        }
    ]
