import json
from collections.abc import Callable

import polars as pl
import pytest

from zsim.lib_webui import process_buff_result as webui_buff
from zsim.lib_webui import process_dmg_result as webui_dmg
from zsim.models.session.session_result import (
    BUFF_TIMELINE_PUBLIC_FIELDS,
    DAMAGE_RESULT_SECTIONS,
    DAMAGE_UUID_AGGREGATE_FIELDS,
    NORMAL_RESULT_OPTIONAL_SECTIONS,
    AttrCurvePayload,
    BuffResult,
    DmgResult,
    NormalModeResult,
    NormalResultPayload,
    ParallelAttrCurveResultPayload,
    ParallelModeResult,
    ParallelResultPayload,
    build_buff_timeline_entry,
    normalize_buff_timeline_payload,
    normalize_damage_result_schema,
)
from zsim.utils import main_loop_consistency as mlc
from zsim.utils import process_buff_result as utility_buff
from zsim.utils import process_dmg_result as utility_dmg


DamageNormalizer = Callable[[pl.DataFrame], pl.DataFrame]


@pytest.mark.parametrize(
    ("frame", "expected"),
    [
        (pl.DataFrame({"damage": [1.0, 2.0]}), [False, False]),
        (
            pl.DataFrame(
                {
                    "damage": [1.0, 2.0],
                    "is_anomaly": pl.Series([None, None], dtype=pl.Null),
                }
            ),
            [False, False],
        ),
        (
            pl.DataFrame({"damage": [1.0, 2.0], "is_anomaly": [True, None]}),
            [True, False],
        ),
        (
            pl.DataFrame({"damage": [1.0, 2.0, 3.0], "is_anomaly": ["true", "1", "false"]}),
            [True, True, False],
        ),
    ],
)
def test_damage_schema_normalization_is_shared_by_data_analysis_processors(
    frame: pl.DataFrame,
    expected: list[bool],
) -> None:
    normalizers: tuple[DamageNormalizer, ...] = (
        normalize_damage_result_schema,
        utility_dmg._normalize_damage_schema,
        webui_dmg._normalize_damage_schema,
        mlc._normalize_consistency_damage_df,
    )

    for normalize in normalizers:
        normalized = normalize(frame)
        assert normalized["is_anomaly"].to_list() == expected


def test_buff_timeline_public_fields_are_shared_by_processors_and_parity() -> None:
    timeline_frame = pl.DataFrame(
        {
            "time_tick": [1, 2, 3],
            "buff_alpha": [0.0, 1.0, 1.0],
            "buff_beta": [None, 2.0, 0.0],
        }
    )

    utility_entries = utility_buff._prepare_buff_timeline_data(timeline_frame)
    webui_entries = webui_buff._prepare_buff_timeline_data(timeline_frame)
    expected_payload = normalize_buff_timeline_payload({"source": utility_entries})

    assert utility_entries == webui_entries
    assert mlc._normalize_buff_timeline_payload({"source": webui_entries}) == expected_payload
    summary = mlc._buff_timeline_summary(
        present=True,
        source_type="json",
        source_paths=[],
        timeline=expected_payload,
        records=mlc._buff_timeline_records(expected_payload),
    )
    assert summary["public_fields"] == list(BUFF_TIMELINE_PUBLIC_FIELDS)
    assert {tuple(entry) for entry in utility_entries} == {BUFF_TIMELINE_PUBLIC_FIELDS}


def test_normal_mode_result_serializes_data_analysis_contract_shape() -> None:
    damage_uuid_row = {field: None for field in DAMAGE_UUID_AGGREGATE_FIELDS}
    damage_uuid_row.update(
        {
            "UUID": "attack-1",
            "name": "agent",
            "element_type": "electric",
            "is_anomaly": False,
            "dmg_expect_sum": 10.0,
        }
    )
    damage_payload = {section: [] for section in DAMAGE_RESULT_SECTIONS}
    damage_payload["uuid_df"] = [damage_uuid_row]
    buff_payload = {
        "agent": [
            build_buff_timeline_entry(
                task="buff_alpha",
                start=1,
                finish=3,
                value=2.0,
            )
        ]
    }

    result = NormalModeResult(
        mode="normal",
        result=NormalResultPayload(
            dmg_result=DmgResult(root=damage_payload),
            buff_result=BuffResult(root=buff_payload),
        ),
    )

    dumped = result.model_dump(mode="json")
    json.dumps(dumped)

    assert tuple(dumped["result"]) == NORMAL_RESULT_OPTIONAL_SECTIONS
    assert tuple(dumped["result"]["dmg_result"]) == DAMAGE_RESULT_SECTIONS
    buff_entry = dumped["result"]["buff_result"]["agent"][0]
    assert tuple(buff_entry) == BUFF_TIMELINE_PUBLIC_FIELDS
    assert "task" not in buff_entry


def test_normal_mode_result_accepts_current_and_internal_buff_timeline_payloads() -> None:
    result = NormalModeResult(
        mode="normal",
        result=NormalResultPayload(
            dmg_result=DmgResult(root=None),
            buff_result=BuffResult(
                root={
                    "alias_payload": [{"Task": "buff_alpha", "Start": 1, "Finish": 2, "Value": 1}],
                    "field_payload": [
                        {"task": "buff_beta", "start": 3, "finish": 4, "value": 2.5}
                    ],
                }
            ),
        ),
    )

    dumped = result.model_dump(mode="json")

    assert dumped["result"]["buff_result"]["alias_payload"][0] == {
        "Task": "buff_alpha",
        "Start": 1,
        "Finish": 2,
        "Value": 1.0,
    }
    assert dumped["result"]["buff_result"]["field_payload"][0] == {
        "Task": "buff_beta",
        "Start": 3,
        "Finish": 4,
        "Value": 2.5,
    }


def test_parallel_result_contract_still_validates() -> None:
    payload = ParallelAttrCurveResultPayload(
        func="attr_curve",
        result=AttrCurvePayload(
            root={
                "agent": {
                    "atk": {
                        "1": {
                            "result": 100.0,
                            "rate": None,
                        }
                    }
                }
            }
        ),
    )
    result = ParallelModeResult(
        mode="parallel",
        func="attr_curve",
        result=ParallelResultPayload(root=payload),
    )

    dumped = result.model_dump(mode="json")

    assert dumped["mode"] == "parallel"
    assert dumped["func"] == "attr_curve"
    assert dumped["result"]["func"] == "attr_curve"
    assert dumped["result"]["result"]["agent"]["atk"]["1"] == {
        "result": 100.0,
        "rate": None,
    }
