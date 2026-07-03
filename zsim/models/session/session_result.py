import math
from collections.abc import Mapping
from typing import Any, Literal, Self, Union

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, RootModel

# --- Payloads for different result types ---

NORMAL_RESULT_OPTIONAL_SECTIONS = ("dmg_result", "buff_result")
DAMAGE_RESULT_SECTIONS = (
    "dmg_result_df",
    "char_dmg_df",
    "uuid_df",
    "char_chart_data",
)
DAMAGE_UUID_AGGREGATE_FIELDS = (
    "UUID",
    "name",
    "element_type",
    "is_anomaly",
    "cid",
    "skill_tag",
    "skill_cn_name",
    "dmg_expect_sum",
    "stun_sum",
    "buildup_sum",
)
BUFF_TIMELINE_PUBLIC_FIELDS = ("Task", "Start", "Finish", "Value")
LEGACY_INTEGER_BUFF_TIMELINE_VALUE_TASKS = frozenset(
    {
        "Buff-角色-扳机-额外能力-追加攻击失衡值提升",
        "Buff-角色-雅-核心被动-冰焰",
        "Buff-角色-柚叶-组队被动-属性异常与紊乱伤害增幅",
        "Buff-角色-柚叶-组队被动-积蓄值增幅",
    }
)


def normalize_damage_result_schema(dmg_result_df: pl.DataFrame) -> pl.DataFrame:
    """Normalize damage.csv schema variants used by utility, WebUI, and parity code."""
    normalized = _normalize_bool_result_column(dmg_result_df, "is_anomaly")
    normalized = _normalize_bool_result_column(normalized, "is_disorder")
    if "skill_tag" not in normalized.columns:
        return normalized
    return normalized.with_columns(
        (
            pl.col("is_disorder")
            | pl.col("skill_tag")
            .cast(pl.Utf8)
            .str.contains("紊乱")
            .fill_null(False)
        ).alias("is_disorder")
    )


def _normalize_bool_result_column(
    dmg_result_df: pl.DataFrame,
    column: str,
) -> pl.DataFrame:
    if column not in dmg_result_df.columns or dmg_result_df[column].is_null().all():
        return dmg_result_df.with_columns(pl.lit(False).alias(column))

    if dmg_result_df[column].dtype == pl.Boolean:
        return dmg_result_df.with_columns(pl.col(column).fill_null(False))

    return dmg_result_df.with_columns(
        pl.col(column)
        .cast(pl.Utf8)
        .str.to_lowercase()
        .is_in(["true", "1"])
        .fill_null(False)
        .alias(column)
    )


def normalize_result_contract_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (AttributeError, ValueError):
            pass
    if value is None:
        return None
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return round(float(value), 6)
    if isinstance(value, str):
        return value
    return str(value)


def normalize_buff_timeline_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        return normalize_result_contract_scalar(float(value))
    except (TypeError, ValueError):
        return normalize_result_contract_scalar(value)


def normalize_buff_timeline_display_value(task: Any, value: Any) -> Any:
    normalized = normalize_buff_timeline_value(value)
    if str(task) in LEGACY_INTEGER_BUFF_TIMELINE_VALUE_TASKS and isinstance(
        normalized, (int, float)
    ):
        return float(math.floor(float(normalized)))
    return normalized


def build_buff_timeline_entry(
    *,
    task: Any,
    start: Any,
    finish: Any,
    value: Any,
) -> dict[str, Any]:
    return {
        "Task": str(task),
        "Start": int(start),
        "Finish": int(finish),
        "Value": normalize_buff_timeline_display_value(task, value),
    }


def normalize_buff_timeline_entry(source: str, entry: Any) -> dict[str, Any]:
    if not isinstance(entry, Mapping):
        raise ValueError(f"buff timeline entry for '{source}' must be an object")

    missing_fields = [field for field in BUFF_TIMELINE_PUBLIC_FIELDS if field not in entry]
    if missing_fields:
        raise ValueError(
            f"buff timeline entry for '{source}' missing public fields: "
            + ", ".join(missing_fields)
        )

    return build_buff_timeline_entry(
        task=entry["Task"],
        start=entry["Start"],
        finish=entry["Finish"],
        value=normalize_buff_timeline_value(entry["Value"]),
    )


def normalize_buff_timeline_payload(payload: Any) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(payload, Mapping):
        raise ValueError("buff timeline payload must be an object keyed by source")

    normalized: dict[str, list[dict[str, Any]]] = {}
    for source in sorted(payload, key=lambda item: str(item)):
        source_key = str(source)
        entries = payload[source]
        if entries is None:
            entries = []
        if not isinstance(entries, list):
            raise ValueError(f"buff timeline entries for '{source_key}' must be a list")
        normalized[source_key] = [
            normalize_buff_timeline_entry(source_key, entry) for entry in entries
        ]
    return normalized


# --- Normal Mode ---
class DmgResult(RootModel[dict[str, Any] | None]):
    """
    Represents the damage calculation results.
    The root is a dictionary containing various dataframes (as list of dicts)
    for detailed damage analysis. The structure is preserved from the webui
    processing functions for compatibility.
    """

    pass


class BuffTimelineBarValue(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
    )

    task: str = Field(description="Buff name", alias="Task")
    start: int = Field(description="Start tick of the buff", alias="Start")
    finish: int = Field(description="End tick of the buff", alias="Finish")
    value: float = Field(description="Buff value/stack", alias="Value")


class BuffResult(RootModel[dict[str, list[BuffTimelineBarValue]] | None]):
    """
    Represents the buff timeline results.
    The root is a dictionary where keys are source identifiers (e.g., file keys)
    and values are lists of buff timeline points.
    """

    pass


class NormalResultPayload(BaseModel):
    dmg_result: DmgResult | None
    buff_result: BuffResult | None


# --- Parallel Mode ---
class AttrCurvePoint(BaseModel):
    result: float = Field(description="Total damage for this data point")
    rate: float | None = Field(description="Rate of return compared to the previous point")


class AttrCurvePayload(RootModel[dict[str, dict[str, dict[str, AttrCurvePoint]]]]):
    """
    Represents the attribute curve results.
    Structure: {char_name: {sc_name: {sc_value: point_data}}}
    """

    pass


class WeaponResultPoint(BaseModel):
    damage: float = Field(description="Total damage for this weapon configuration")


class WeaponPayload(RootModel[dict[str, dict[str, dict[str, WeaponResultPoint]]]]):
    """
    Represents the weapon comparison results.
    Structure: {char_name: {weapon_name: {weapon_level: point_data}}}
    """

    pass


class ParallelAttrCurveResultPayload(BaseModel):
    func: Literal["attr_curve"]
    result: AttrCurvePayload


class ParallelWeaponResultPayload(BaseModel):
    func: Literal["weapon"]
    result: WeaponPayload


class ParallelResultPayload(
    RootModel[Union[ParallelAttrCurveResultPayload, ParallelWeaponResultPayload]]
):
    root: Union[ParallelAttrCurveResultPayload, ParallelWeaponResultPayload] = Field(
        ..., discriminator="func"
    )


# --- Discriminated Union Models ---


class NormalModeResult(BaseModel):
    mode: Literal["normal"]
    result: NormalResultPayload


class ParallelModeResult(BaseModel):
    mode: Literal["parallel"]
    func: Literal["attr_curve", "weapon"]
    result: ParallelResultPayload


# --- Top-level SessionResult Factory Class ---


class SessionResult:
    """
    This class acts as a factory for creating specific result models
    (NormalModeResult or ParallelModeResult) based on the 'mode' field.
    It allows instantiation like `SessionResult(mode='normal', result=...)`,
    and the returned object will be a validated instance of the correct model.
    This is not a Pydantic model itself, but a dispatcher.
    """

    def __new__(cls, **kwargs: Any) -> Self | NormalModeResult | ParallelModeResult:
        # This is not a standard Pydantic model, but a factory that returns one.
        # It's designed to match the instantiation pattern in the controller.
        if cls is not SessionResult:
            # This allows subclasses to be instantiated normally if needed.
            return super().__new__(cls)

        mode = kwargs.get("mode")
        if mode == "normal":
            return NormalModeResult(**kwargs)
        elif mode == "parallel":
            return ParallelModeResult(**kwargs)
        else:
            raise ValueError(f"Invalid 'mode' for SessionResult: {mode}")
