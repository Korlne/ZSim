from __future__ import annotations

import ast
import importlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.run_buff_refactor_validation import (
    DEFAULT_PATH_LEGACY_RUNTIME_REFERENCE_FAMILY,
    LEGACY_RUNTIME_COMMAND_ADAPTER_FAMILY,
    RUNTIME_DEPENDENCY_CATEGORIES,
    RUNTIME_DEPENDENCY_STRICT_COMMAND,
    RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES,
    SCHEDULED_EVENT_IMPLICIT_CONSTRUCTOR_FAMILY,
    RuntimeDependencyZeroScanner,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FULL_CONVERGENCE_ZERO_CENSUS_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-21-US-009-guardrail-zero-census.json"
)
TRIGGER_REF_TUPLE_CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-21-US-005-trigger-ref-tuple-family-checkpoint.json"
)
FROZEN_EDGE_EQUIPMENT_TEMPLATE_CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "ralph"
    / "checkpoints"
    / "2026-06-21-US-004-frozen-edge-equipment-template-checkpoint.json"
)
PREPARATION_HELPERS_PATH = (
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "_preparation_helpers.py"
)


def _assert_uses_preparation_template_helpers(
    source: str,
    *,
    equipper_required: bool = True,
) -> None:
    helper_source = PREPARATION_HELPERS_PATH.read_text(encoding="utf-8")

    assert "prepare_with_context(" in source
    if equipper_required:
        assert "ensure_equipper_template_record(" in source
        assert "preparation_context.find_equipper(" in helper_source
    else:
        assert (
            "ensure_equipper_template_record(" in source
            or "ensure_owner_template_record(" in source
        )
    assert "preparation_context.find_sub_exist_buff_dict(" in helper_source
    assert "check_preparation_func(" in helper_source

SCANNED_PRODUCTION_FILES = (
    PROJECT_ROOT / "zsim" / "simulator" / "dataclasses.py",
    PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "buff_runtime.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "__init__.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "runtime_command.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Update" / "Update_Buff.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffLoad.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAdd.py",
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py",
)

SCHEDULED_EVENT_DIR = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent"
EVENT_HANDLERS_DIR = SCHEDULED_EVENT_DIR / "event_handlers"
SCHEDULED_EVENT_RUNTIME_GUARDRAIL_FILES = (
    SCHEDULED_EVENT_DIR / "__init__.py",
    SCHEDULED_EVENT_DIR / "buff_runtime.py",
    SCHEDULED_EVENT_DIR / "runtime_command.py",
    *sorted(EVENT_HANDLERS_DIR.rglob("*.py")),
)
RUNTIME_COMMAND_LEGACY_ADAPTER_GUARDRAIL_FILES = tuple(
    sorted((PROJECT_ROOT / "zsim").rglob("*.py"))
)
RUNTIME_COMMAND_FACTORY_DIRECT_CALL_GUARDRAIL_FILES = tuple(
    sorted((PROJECT_ROOT / "zsim").rglob("*.py"))
)
SCHEDULED_EVENT_RAW_CONSTRUCTOR_GUARDRAIL_FILES = tuple(
    sorted((PROJECT_ROOT / "zsim").rglob("*.py"))
)

CALCULATOR_READ_GUARDRAIL_FILES = (
    PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "Calculator.py",
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
    / "VivianCorePassiveTrigger.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "VivianCinema6Trigger.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "LinaCoreSkillPenRatioBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "BranchBladeSongCritDamageBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "LighterAdditionalAbility_IceFireBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "MiyabiCoreSkill_IceFire.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "QingYiAdditionalAbilityStunConvertToATK.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "CannonRotor.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "TriggerAdditionalAbilityStunBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "WoodpeckerElectroSet4_NA.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "WoodpeckerElectroSet4_E_EX.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "WoodpeckerElectroSet4_CA.py",
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
    / "YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "Soldier0AnbyCoreSkillCritDMGBonus.py",
    PROJECT_ROOT
    / "zsim"
    / "sim_progress"
    / "Buff"
    / "BuffXLogic"
    / "TimeweaverDisorderDmgMul.py",
)

RAW_CONTAINER_NAMES = {
    "DYNAMIC_BUFF_DICT",
    "LOADING_BUFF_DICT",
    "_enemy_debuff_mirror",
    "_dynamic_buff",
    "_dynamic_buff_dict",
    "_exist_buff_dict",
    "_loading_buff_dict",
    "dynamic_buff",
    "dynamic_buff_dict",
    "dynamic_debuff_list",
    "enemy_debuff_mirror",
    "exist_buff_dict",
    "existbuff_dict",
    "loading_buff",
    "loading_buff_dict",
    "sub_exist_buff_dict",
}

RAW_CONTAINER_ATTRS = {
    "DYNAMIC_BUFF_DICT",
    "LOADING_BUFF_DICT",
    "_enemy_debuff_mirror",
    "_dynamic_buff",
    "_dynamic_buff_dict",
    "_exist_buff_dict",
    "_loading_buff_dict",
    "dynamic_buff",
    "dynamic_debuff_list",
    "enemy_debuff_mirror",
    "exist_buff_dict",
    "loading_buff",
}

LEGACY_RUNTIME_GETTER_NAMES = {
    "_get_context_dynamic_buff",
    "_get_context_exist_buff_dict",
    "_get_context_legacy_dynamic_buff",
    "_get_context_legacy_exist_buff_dict",
    "get_dynamic_buff",
    "get_exist_buff_dict",
    "get_legacy_dynamic_buff_dict",
    "get_legacy_exist_buff_dict",
}

SCHEDULED_RUNTIME_NAMES = RAW_CONTAINER_NAMES | LEGACY_RUNTIME_GETTER_NAMES
SCHEDULED_RUNTIME_ATTRS = RAW_CONTAINER_ATTRS | LEGACY_RUNTIME_GETTER_NAMES

TRIAGE_NEXT_ACTION = (
    "migrate to an explicit facade/runtime port, retain as documented "
    "compatibility, or block the story"
)

PENDING_QUEUE_RAW_WRITE_NEXT_ACTION = (
    "route pending writes through PendingBuffQueue owner APIs, keep raw dict "
    "mutation inside the documented owner/compat adapter, or block the story"
)

ACTIVE_STORE_RAW_WRITE_NEXT_ACTION = (
    "route active writes through ActiveBuffStore or EnemyDebuffMirror owner APIs, "
    "keep raw mutation inside the documented owner/migration adapter, or block the story"
)

CALCULATOR_READ_NEXT_ACTION = (
    "migrate read-only usage to CalculatorBuffAttributeReader, retain as "
    "documented formula/compatibility snapshot, or block the story"
)

RUNTIME_COMMAND_LEGACY_ADAPTER_NEXT_ACTION = (
    "pass buff_runtime_state to create_runtime_command_port, or keep "
    "LegacyRuntimeCommandAdapter construction inside the explicit "
    "migration/test/rollback factory fallback"
)

RUNTIME_COMMAND_FACTORY_DIRECT_CALL_NEXT_ACTION = (
    "route runtime command-port creation through ScheduledEventRuntimePortFactory, "
    "or keep lower-level create_runtime_command_port calls inside explicit "
    "migration/test/rollback coverage"
)

SCHEDULED_EVENT_RAW_CONSTRUCTOR_NEXT_ACTION = (
    "use ScheduledEvent.from_runtime_state(...) for production scheduled-event "
    "processing, or keep direct raw-container construction inside explicit "
    "migration/test/rollback compatibility"
)

SCHEDULED_EVENT_RAW_CONSTRUCTOR_NAMES = {
    "DYNAMIC_BUFF_DICT",
    "LOADING_BUFF_DICT",
    "dynamic_buff",
    "exist_buff_dict",
    "loading_buff",
}

ACTIVE_STORE_RAW_DICT_NAMES = {
    "DYNAMIC_BUFF_DICT",
    "_dynamic_buff",
    "_dynamic_buff_dict",
    "_stores",
    "active_store",
    "dynamic_buff",
    "dynamic_buff_dict",
}

ACTIVE_STORE_COMPAT_DICT_METHODS = {
    "_active_store_for_compat",
    "active_store_for_compat",
}

ENEMY_MIRROR_RAW_LIST_NAMES = {
    "_enemy_debuff_mirror",
    "_mirror",
    "dynamic_debuff_list",
    "enemy_debuff_mirror",
}

ENEMY_MIRROR_COMPAT_LIST_METHODS = {
    "as_compat_list",
    "enemy_mirror_for_compat",
    "get_enemy_debuff_mirror_for_compat",
}

RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE = (
    "retained XLogic compatibility snapshot read"
)

XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW = (
    "active_buff_view=self.record.dynamic_buff_list"
)
XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION = (
    "direct CalculatorBuffAttributeReader() construction"
)
XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND = "broad JudgeTools.find_* call"
XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN = "direct trigger_buff_0 registry scan"
XLOGIC_ADAPTER_LEGACY_GET_PREPARED = (
    "legacy get_prepared without PreparationContext"
)
XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE = (
    "record/template cached runtime service"
)
XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE = "legacy trigger_buff_0 tuple keyword"

XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE_FIELDS = frozenset(
    {
        "buff_runtime_read_port",
        "buff_runtime_state",
        "dispatch_port",
        "dot_runtime_adapter",
        "dot_runtime_state",
        "dot_runtime_writer",
        "event_emitter",
        "preload_commands",
        "runtime_command_port",
        "runtime_read_port",
        "schedule_dispatch_port",
        "scheduled_event",
        "scheduled_event_emitter",
        "scheduled_event_emitter_provider",
        "sim_instance",
        "simulator",
    }
)

US005_ACTIVE_VIEW_CALCULATOR_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
    "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py",
)

TRIGGER_REF_TUPLE_FAMILY_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/CordisGerminaSNAAndQIgnoreDefense.py",
    "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeveredInnocencELEDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerAnomalyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SpectralGazeImpactBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyAdditionalSkillDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCinema4EleResReduce.py",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/WeepingCradleDMGBonusIncrease.py",
    "zsim/sim_progress/Buff/BuffXLogic/YangiCinema1ApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YunkuiTalesSheerAtkBonus.py",
)

TRIGGER_REF_EQUIPMENT_TEMPLATE_RETAINED_TICK_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/WeepingCradleDMGBonusIncrease.py",
)

FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py",
)

BRANCH_BLADE_SONG_CRITDAMAGE_PREPARATION_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py",
)

RESOURCE_REFRESH_EQUIPMENT_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py",
    "zsim/sim_progress/Buff/BuffXLogic/LunarNoviluna.py",
    "zsim/sim_progress/Buff/BuffXLogic/MagneticStormCharlieSpRecover.py",
    "zsim/sim_progress/Buff/BuffXLogic/SliceofTimeExtraResources.py",
)

XLOGIC_ADAPTER_CALCULATOR_SERVICE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py",
    *US005_ACTIVE_VIEW_CALCULATOR_FILES,
    "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/LinaCoreSkillPenRatioBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py",
    "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py",
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py",
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py",
)
XLOGIC_ADAPTER_TRIGGER_REF_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/AstralVoice.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStatePhyBuildupBonus.py",
)
XLOGIC_ADAPTER_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/AstralVoice.py",
    *BRANCH_BLADE_SONG_CRITDAMAGE_PREPARATION_TEMPLATE_FILES,
    *FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES,
    *RESOURCE_REFRESH_EQUIPMENT_TEMPLATE_FILES,
    "zsim/sim_progress/Buff/BuffXLogic/RoaringRideBuffTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedBesiegeBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedBesiegeBonusTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedCinema2BesiegeIgnoreDefenceTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedCinema2BesiegeIgnoreDefense.py",
    "zsim/sim_progress/Buff/BuffXLogic/_char_buff_mod.py",
    "zsim/sim_progress/Buff/BuffXLogic/_euipment_buff_mod.py",
)
XLOGIC_ADAPTER_RECORD_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/_buff_record_base_class.py",
    "zsim/sim_progress/Buff/BuffXLogic/_char_buff_mod.py",
    "zsim/sim_progress/Buff/BuffXLogic/_euipment_buff_mod.py",
)

FULL_CONVERGENCE_US002_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py",
)

FULL_CONVERGENCE_US003_TRIGGER_REF_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritDmgBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py",
    "zsim/sim_progress/Buff/BuffXLogic/JanePassionStatePhyBuildupBonus.py",
)

FULL_CONVERGENCE_US004_TEMPLATE_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/RoaringRideBuffTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedBesiegeBonus.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedBesiegeBonusTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedCinema2BesiegeIgnoreDefenceTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/SeedCinema2BesiegeIgnoreDefense.py",
)

FULL_CONVERGENCE_US005_CALCULATOR_FILES = US005_ACTIVE_VIEW_CALCULATOR_FILES

FULL_CONVERGENCE_US006_ENEMY_HELPER_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/dot_runtime_state_read.py",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_map_read.py",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_anomaly_read.py",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_debuff_mirror_read.py",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_edge_state_read.py",
    "zsim/sim_progress/Buff/BuffXLogic/enemy_state_read.py",
)

FULL_CONVERGENCE_US008_EVENT_PRELOAD_TARGETS = (
    "zsim/sim_progress/Buff/BuffXLogic/AlicePolarizedAssaultTrigger.py::AlicePolarizedAssaultTrigger.special_effect_logic",
    "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py::CannonRotor.special_hit_logic",
    "zsim/sim_progress/Buff/BuffXLogic/YixuanCinema1Trigger.py::YixuanCinema1Trigger.special_hit_logic",
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaCinema6SheelTrigger.py::YuzuhaCinema6SheelTrigger",
)

FULL_CONVERGENCE_MIGRATED_BATCH_FILES = {
    "US-002": FULL_CONVERGENCE_US002_TEMPLATE_FILES,
    "US-003": FULL_CONVERGENCE_US003_TRIGGER_REF_FILES,
    "US-004": FULL_CONVERGENCE_US004_TEMPLATE_FILES,
    "US-005": FULL_CONVERGENCE_US005_CALCULATOR_FILES,
    "US-006": FULL_CONVERGENCE_US006_ENEMY_HELPER_FILES,
    "US-008": FULL_CONVERGENCE_US008_EVENT_PRELOAD_TARGETS,
}

FULL_CONVERGENCE_COPIED_OUTPUT_PAYLOAD_RISK_FILES = (
    "zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py",
    "zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py",
)

FULL_CONVERGENCE_LIFECYCLE_SCOPE_FILES = (
    "zsim/sim_progress/Buff/ScheduleBuffSettle.py",
    "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
    "zsim/sim_progress/Update/UpdateAnomaly.py",
    "zsim/sim_progress/Update/Update_Buff.py",
    "zsim/simulator/simulator_class.py",
)

FULL_CONVERGENCE_RETAINED_COMPATIBILITY_FILES = (
    "zsim/sim_progress/Buff/BuffAddStrategy.py",
    "zsim/sim_progress/Buff/BuffXLogic/AstralVoice.py",
    "zsim/sim_progress/Buff/BuffXLogic/_buff_record_base_class.py",
    "zsim/sim_progress/Buff/BuffXLogic/_char_buff_mod.py",
    "zsim/sim_progress/Buff/BuffXLogic/_euipment_buff_mod.py",
    "zsim/sim_progress/Buff/JudgeTools/PreparationContext.py",
    "zsim/sim_progress/Buff/JudgeTools/__init__.py",
    "zsim/sim_progress/ScheduledEvent/Calculator.py",
)

XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS = {
    path: frozenset(
        {
            XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
            XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
        }
    )
    for path in XLOGIC_ADAPTER_CALCULATOR_SERVICE_FILES
}
for path in XLOGIC_ADAPTER_TRIGGER_REF_FILES:
    XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[path] = XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.get(
        path, frozenset()
    ) | frozenset({XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN})
for path in XLOGIC_ADAPTER_TEMPLATE_FILES:
    XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[path] = XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.get(
        path, frozenset()
    ) | frozenset(
        {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        }
    )
for path in XLOGIC_ADAPTER_RECORD_TEMPLATE_FILES:
    XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[path] = XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.get(
        path, frozenset()
    ) | frozenset({XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE})
for path in TRIGGER_REF_TUPLE_FAMILY_FILES:
    XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[path] = XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.get(
        path, frozenset()
    ) | frozenset(
        {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
            XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE,
        }
    )

XLOGIC_ADAPTER_RETAINED_JUDGE_TOOLS_FIND_CALLS_BY_FILE = {
    path: frozenset({"JudgeTools.find_tick"})
    for path in (
        FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES
        + RESOURCE_REFRESH_EQUIPMENT_TEMPLATE_FILES
        + TRIGGER_REF_EQUIPMENT_TEMPLATE_RETAINED_TICK_FILES
    )
}

PENDING_QUEUE_RAW_WRITE_ALLOWED_CONTEXTS = {
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "PendingBuffQueue.reset_for_beneficiaries",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "PendingBuffQueue.enqueue",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "PendingBuffQueue.__setitem__",
    ),
    (
        "zsim/sim_progress/Buff/BuffLoad.py",
        "_LegacyPendingQueueCompatAdapter.reset_for_beneficiaries",
    ),
    (
        "zsim/sim_progress/Buff/BuffLoad.py",
        "_LegacyPendingQueueCompatAdapter.enqueue",
    ),
    (
        "zsim/sim_progress/Buff/BuffLoad.py",
        "_LegacyPendingQueueCompatAdapter.__setitem__",
    ),
}

ACTIVE_STORE_RAW_WRITE_ALLOWED_CONTEXTS = {
    (
        "zsim/simulator/dataclasses.py",
        "ScheduleData.reset_myself",
    ),
    (
        "zsim/simulator/dataclasses.py",
        "GlobalStats.__post_init__",
    ),
    (
        "zsim/simulator/dataclasses.py",
        "GlobalStats.reset_myself",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "BuffRuntimeState._collapse_enemy_debuff_store",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "ActiveBuffStore.append",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "ActiveBuffStore.remove",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "EnemyDebuffMirror.sync",
    ),
    (
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "EnemyDebuffMirror.remove",
    ),
}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    next_action: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {self.next_action}"
        )


@dataclass(frozen=True)
class PendingQueueRawWriteFinding:
    path: str
    line: int
    kind: str
    matched_expression: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"forbidden pending raw write: {self.kind}; "
            f"next action: {PENDING_QUEUE_RAW_WRITE_NEXT_ACTION}"
        )


@dataclass(frozen=True)
class ActiveStoreRawWriteFinding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"forbidden active raw write: {self.kind}; "
            f"next action: {ACTIVE_STORE_RAW_WRITE_NEXT_ACTION}"
        )


@dataclass(frozen=True)
class XLogicAdapterGuardrailFinding:
    path: str
    line: int
    kind: str
    matched_expression: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"forbidden migrated-file pattern: {self.kind}"
        )


@dataclass(frozen=True)
class RuntimeCommandLegacyAdapterFinding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {RUNTIME_COMMAND_LEGACY_ADAPTER_NEXT_ACTION}"
        )


@dataclass(frozen=True)
class RuntimeCommandFactoryDirectCallFinding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {RUNTIME_COMMAND_FACTORY_DIRECT_CALL_NEXT_ACTION}"
        )


@dataclass(frozen=True)
class ScheduledEventRawConstructorFinding:
    path: str
    line: int
    kind: str
    matched_expression: str
    classification_suggestion: str
    context: str

    def message(self) -> str:
        return (
            f"{self.path}:{self.line}: matched expression: {self.matched_expression}; "
            f"classification suggestion: {self.classification_suggestion}; "
            f"next action: {SCHEDULED_EVENT_RAW_CONSTRUCTOR_NEXT_ACTION}"
        )


class RawContainerVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[Finding] = []
        self._parents: list[ast.AST] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

    def visit(self, node: ast.AST):
        self._parents.append(node)
        try:
            return super().visit(node)
        finally:
            self._parents.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in RAW_CONTAINER_NAMES:
            self._add_finding(
                line=node.lineno,
                kind="raw_container_name",
                expression=self._expression_context(node),
                container=node.id,
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in RAW_CONTAINER_ATTRS:
            self._add_finding(
                line=node.lineno,
                kind="raw_container_attribute",
                expression=self._expression_context(node),
                container=node.attr,
            )
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg in RAW_CONTAINER_NAMES:
            line = getattr(node.value, "lineno", 0)
            self._add_finding(
                line=line,
                kind="raw_container_keyword",
                expression=self._source_for(node),
                container=node.arg,
            )
        self.generic_visit(node)

    def _visit_arguments(self, function_name: str, args: ast.arguments) -> None:
        all_args = [
            *args.posonlyargs,
            *args.args,
            *args.kwonlyargs,
        ]
        if args.vararg is not None:
            all_args.append(args.vararg)
        if args.kwarg is not None:
            all_args.append(args.kwarg)
        for arg in all_args:
            if arg.arg in RAW_CONTAINER_NAMES:
                self._add_finding(
                    line=arg.lineno,
                    kind="raw_container_parameter",
                    expression=f"{function_name}(..., {arg.arg}, ...)",
                    container=arg.arg,
                )

    def _add_finding(
        self, *, line: int, kind: str, expression: str, container: str
    ) -> None:
        self.findings.append(
            Finding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=self._classification_for(container),
                next_action=TRIAGE_NEXT_ACTION,
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _expression_context(self, node: ast.AST) -> str:
        parent = self._parents[-2] if len(self._parents) >= 2 else None
        if isinstance(parent, ast.Subscript) and parent.value is node:
            return self._source_for(parent)
        if isinstance(parent, ast.Assign):
            return self._source_for(parent)
        if isinstance(parent, ast.AnnAssign):
            return self._source_for(parent)
        return self._source_for(node)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())

    @staticmethod
    def _classification_for(container: str) -> str:
        if "debuff_mirror" in container or container == "dynamic_debuff_list":
            return "enemy debuff mirror old-container passthrough"
        if container in LEGACY_RUNTIME_GETTER_NAMES:
            return "compatibility-only legacy runtime getter"
        if "LOADING" in container or "loading" in container:
            return "pending queue old-container passthrough"
        if "DYNAMIC" in container or "dynamic" in container:
            return "active store old-container passthrough"
        return "registry/template old-container passthrough"


class PendingQueueRawWriteVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[PendingQueueRawWriteFinding] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._add_subscript_write_if_pending(target, "pending_queue_subscript_write")
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._add_subscript_write_if_pending(node.target, "pending_queue_subscript_write")
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._add_subscript_write_if_pending(node.target, "pending_queue_subscript_write")
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self._add_subscript_write_if_pending(target, "pending_queue_subscript_delete")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
            and isinstance(node.func.value, ast.Subscript)
            and self._is_pending_queue_expr(node.func.value.value)
        ):
            self._add_finding(
                line=node.lineno,
                kind="pending_queue_raw_list_append",
                expression=self._source_for(node.func.value),
            )
        self.generic_visit(node)

    def _add_subscript_write_if_pending(self, node: ast.AST, kind: str) -> None:
        if isinstance(node, ast.Subscript) and self._is_pending_queue_expr(node.value):
            self._add_finding(
                line=node.lineno,
                kind=kind,
                expression=self._source_for(node),
            )

    def _is_pending_queue_expr(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return self._is_pending_queue_name(node.id)
        if isinstance(node, ast.Attribute):
            if node.attr == "_queues":
                return True
            return self._is_pending_queue_name(node.attr)
        return False

    @staticmethod
    def _is_pending_queue_name(name: str) -> bool:
        if name in {
            "LOADING_BUFF_DICT",
            "_loading_buff_dict",
            "loading_buff_dict",
        }:
            return True
        lowered = name.lower()
        return "pending" in lowered and (
            "queue" in lowered or "owner" in lowered or "buff" in lowered
        )

    def _add_finding(self, *, line: int, kind: str, expression: str) -> None:
        self.findings.append(
            PendingQueueRawWriteFinding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())


class ActiveStoreRawWriteVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[ActiveStoreRawWriteFinding] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []
        self._active_list_alias_stack: list[set[str]] = [set()]
        self._enemy_mirror_alias_stack: list[set[str]] = [set()]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        self._active_list_alias_stack.append(set())
        self._enemy_mirror_alias_stack.append(set())
        try:
            self.generic_visit(node)
        finally:
            self._enemy_mirror_alias_stack.pop()
            self._active_list_alias_stack.pop()
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        self._active_list_alias_stack.append(set())
        self._enemy_mirror_alias_stack.append(set())
        try:
            self.generic_visit(node)
        finally:
            self._enemy_mirror_alias_stack.pop()
            self._active_list_alias_stack.pop()
            self._function_stack.pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._add_subscript_write_if_active(target, "active_store_subscript_write")
            self._record_alias_if_raw_list(target, node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._add_subscript_write_if_active(node.target, "active_store_subscript_write")
        if node.value is not None:
            self._record_alias_if_raw_list(node.target, node.value)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._add_subscript_write_if_active(node.target, "active_store_subscript_write")
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self._add_subscript_write_if_active(target, "active_store_subscript_delete")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"append", "remove"}:
            method = node.func.attr
            value = node.func.value
            if isinstance(value, ast.Subscript) and self._is_active_store_expr(value.value):
                self._add_finding(
                    line=node.lineno,
                    kind=f"active_store_raw_list_{method}",
                    expression=self._source_for(value),
                    classification_suggestion="active store raw write",
                )
            elif self._is_active_list_expr(value):
                self._add_finding(
                    line=node.lineno,
                    kind=f"active_store_compat_list_{method}",
                    expression=self._source_for(value),
                    classification_suggestion="active-store compatibility write",
                )
            elif self._is_enemy_mirror_expr(value):
                self._add_finding(
                    line=node.lineno,
                    kind=f"enemy_mirror_raw_list_{method}",
                    expression=self._source_for(value),
                    classification_suggestion="enemy debuff mirror raw write",
                )
        self.generic_visit(node)

    def _add_subscript_write_if_active(self, node: ast.AST, kind: str) -> None:
        if isinstance(node, ast.Subscript) and self._is_active_store_expr(node.value):
            self._add_finding(
                line=node.lineno,
                kind=kind,
                expression=self._source_for(node),
                classification_suggestion="active store raw write",
            )

    def _record_alias_if_raw_list(self, target: ast.AST, value: ast.AST) -> None:
        if not isinstance(target, ast.Name):
            return
        if (
            isinstance(value, ast.Subscript)
            and self._is_active_store_expr(value.value)
        ) or self._is_active_list_expr(value):
            self._active_list_alias_stack[-1].add(target.id)
            return
        if self._is_enemy_mirror_expr(value):
            self._enemy_mirror_alias_stack[-1].add(target.id)

    def _is_active_store_expr(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in ACTIVE_STORE_RAW_DICT_NAMES
        if isinstance(node, ast.Attribute):
            return node.attr in ACTIVE_STORE_RAW_DICT_NAMES
        if isinstance(node, ast.Call):
            return self._call_name(node.func) in ACTIVE_STORE_COMPAT_DICT_METHODS
        return False

    def _is_active_list_expr(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return any(node.id in aliases for aliases in self._active_list_alias_stack)
        if isinstance(node, ast.Subscript):
            return self._is_active_store_expr(node.value)
        return False

    def _is_enemy_mirror_expr(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in ENEMY_MIRROR_RAW_LIST_NAMES or any(
                node.id in aliases for aliases in self._enemy_mirror_alias_stack
            )
        if isinstance(node, ast.Attribute):
            return node.attr in ENEMY_MIRROR_RAW_LIST_NAMES
        if isinstance(node, ast.Call):
            return self._call_name(node.func) in ENEMY_MIRROR_COMPAT_LIST_METHODS
        return False

    @staticmethod
    def _call_name(func: ast.AST) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _add_finding(
        self,
        *,
        line: int,
        kind: str,
        expression: str,
        classification_suggestion: str,
    ) -> None:
        self.findings.append(
            ActiveStoreRawWriteFinding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=classification_suggestion,
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())


class ScheduledEventRuntimeVisitor(RawContainerVisitor):
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            if node.name in LEGACY_RUNTIME_GETTER_NAMES:
                self._add_finding(
                    line=node.lineno,
                    kind="legacy_runtime_getter_definition",
                    expression=f"def {node.name}(...)",
                    container=node.name,
                )
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            if node.name in LEGACY_RUNTIME_GETTER_NAMES:
                self._add_finding(
                    line=node.lineno,
                    kind="legacy_runtime_getter_definition",
                    expression=f"async def {node.name}(...)",
                    container=node.name,
                )
            self._visit_arguments(node.name, node.args)
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in SCHEDULED_RUNTIME_NAMES:
            self._add_finding(
                line=node.lineno,
                kind="scheduled_runtime_name",
                expression=self._expression_context(node),
                container=node.id,
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in SCHEDULED_RUNTIME_ATTRS:
            self._add_finding(
                line=node.lineno,
                kind="scheduled_runtime_attribute",
                expression=self._expression_context(node),
                container=node.attr,
            )
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        if node.arg in RAW_CONTAINER_NAMES:
            line = getattr(node.value, "lineno", 0)
            self._add_finding(
                line=line,
                kind="scheduled_runtime_keyword",
                expression=self._source_for(node),
                container=node.arg,
            )
        self.generic_visit(node)


class RuntimeCommandLegacyAdapterVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[RuntimeCommandLegacyAdapterFinding] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []
        self._legacy_adapter_aliases = {"LegacyRuntimeCommandAdapter"}
        self._factory_aliases = {"create_runtime_command_port"}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            imported_name = alias.name
            local_name = alias.asname or alias.name
            if imported_name == "LegacyRuntimeCommandAdapter":
                self._legacy_adapter_aliases.add(local_name)
            if imported_name == "create_runtime_command_port":
                self._factory_aliases.add(local_name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._call_name(node.func)
        if call_name in self._legacy_adapter_aliases:
            self._add_finding(
                line=node.lineno,
                kind="legacy_runtime_command_adapter_constructor",
                expression=self._source_for(node),
                classification_suggestion=(
                    "legacy runtime command adapter construction"
                ),
            )
        if call_name in self._factory_aliases and self._omits_runtime_state(node):
            self._add_finding(
                line=node.lineno,
                kind="runtime_command_factory_without_state",
                expression=self._source_for(node),
                classification_suggestion=(
                    "create_runtime_command_port fallback without BuffRuntimeState"
                ),
            )
        self.generic_visit(node)

    @staticmethod
    def _call_name(func: ast.AST) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    @staticmethod
    def _omits_runtime_state(node: ast.Call) -> bool:
        for keyword in node.keywords:
            if keyword.arg != "buff_runtime_state":
                continue
            return (
                isinstance(keyword.value, ast.Constant)
                and keyword.value.value is None
            )
        return True

    def _add_finding(
        self,
        *,
        line: int,
        kind: str,
        expression: str,
        classification_suggestion: str,
    ) -> None:
        self.findings.append(
            RuntimeCommandLegacyAdapterFinding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=classification_suggestion,
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())


class RuntimeCommandFactoryDirectCallVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[RuntimeCommandFactoryDirectCallFinding] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []
        self._factory_aliases = {"create_runtime_command_port"}

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            imported_name = alias.name
            local_name = alias.asname or alias.name
            if imported_name == "create_runtime_command_port":
                self._factory_aliases.add(local_name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        call_name = self._call_name(node.func)
        if call_name in self._factory_aliases:
            self._add_finding(
                line=node.lineno,
                kind="runtime_command_factory_direct_call",
                expression=self._source_for(node),
                classification_suggestion=(
                    "direct create_runtime_command_port call"
                ),
            )
        self.generic_visit(node)

    @staticmethod
    def _call_name(func: ast.AST) -> str | None:
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
        return None

    def _add_finding(
        self,
        *,
        line: int,
        kind: str,
        expression: str,
        classification_suggestion: str,
    ) -> None:
        self.findings.append(
            RuntimeCommandFactoryDirectCallFinding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=classification_suggestion,
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())


class ScheduledEventRawConstructorVisitor(ast.NodeVisitor):
    def __init__(self, path: Path, source: str) -> None:
        self.path = path
        self.source = source
        self.findings: list[ScheduledEventRawConstructorFinding] = []
        self._class_stack: list[str] = []
        self._function_stack: list[str] = []
        self._constructor_aliases = {"ScheduledEvent", "ScE"}

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.endswith("ScheduledEvent") and alias.asname is not None:
                self._constructor_aliases.add(alias.asname)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            imported_name = alias.name
            local_name = alias.asname or alias.name
            if imported_name in {"ScheduledEvent", "ScE"}:
                self._constructor_aliases.add(local_name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        constructor_name = self._constructor_name(node.func)
        if constructor_name is None:
            self.generic_visit(node)
            return

        if self._uses_raw_container_handoff(node):
            self._add_finding(
                line=node.lineno,
                kind="scheduled_event_raw_constructor_handoff",
                expression=self._source_for(node),
                classification_suggestion=(
                    "raw-container ScheduledEvent constructor handoff"
                ),
            )
        else:
            self._add_finding(
                line=node.lineno,
                kind="scheduled_event_direct_constructor",
                expression=self._source_for(node),
                classification_suggestion=(
                    "direct ScheduledEvent constructor bypass"
                ),
            )
        self.generic_visit(node)

    def _constructor_name(self, func: ast.AST) -> str | None:
        if isinstance(func, ast.Name) and func.id in self._constructor_aliases:
            return func.id
        if isinstance(func, ast.Attribute) and func.attr in self._constructor_aliases:
            return func.attr
        return None

    def _uses_raw_container_handoff(self, node: ast.Call) -> bool:
        for argument in node.args:
            if self._contains_raw_container_name(argument):
                return True
        for keyword in node.keywords:
            if keyword.arg in SCHEDULED_EVENT_RAW_CONSTRUCTOR_NAMES:
                return True
            if self._contains_raw_container_name(keyword.value):
                return True
        return False

    @staticmethod
    def _contains_raw_container_name(node: ast.AST) -> bool:
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Name)
                and child.id in SCHEDULED_EVENT_RAW_CONSTRUCTOR_NAMES
            ):
                return True
            if (
                isinstance(child, ast.Attribute)
                and child.attr in SCHEDULED_EVENT_RAW_CONSTRUCTOR_NAMES
            ):
                return True
        return False

    def _add_finding(
        self,
        *,
        line: int,
        kind: str,
        expression: str,
        classification_suggestion: str,
    ) -> None:
        self.findings.append(
            ScheduledEventRawConstructorFinding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=classification_suggestion,
                context=self._context(),
            )
        )

    def _relative_path(self) -> str:
        return self.path.relative_to(PROJECT_ROOT).as_posix()

    def _context(self) -> str:
        parts = [*self._class_stack, *self._function_stack]
        if not parts:
            return "<module>"
        return ".".join(parts)

    def _source_for(self, node: ast.AST) -> str:
        segment = ast.get_source_segment(self.source, node)
        if segment is None:
            return f"<{type(node).__name__}>"
        return self._normalize(segment)

    @staticmethod
    def _normalize(expression: str) -> str:
        return " ".join(expression.strip().split())


class CalculatorReadVisitor(RawContainerVisitor):
    def __init__(self, path: Path, source: str) -> None:
        super().__init__(path, source)
        self._multiplier_aliases = {"MultiplierData"}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function_stack.append(node.name)
        try:
            self.generic_visit(node)
        finally:
            self._function_stack.pop()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module.endswith("Calculator"):
            for alias in node.names:
                if alias.name == "MultiplierData":
                    self._multiplier_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_multiplier_constructor(node.func):
            self._add_calculator_finding(
                line=node.lineno,
                kind="calculator_multiplier_snapshot",
                expression=self._source_for(node),
                classification_suggestion="direct MultiplierData compatibility snapshot",
            )
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "dynamic_buff_list" and isinstance(node.ctx, ast.Load):
            self._add_calculator_finding(
                line=node.lineno,
                kind="calculator_dynamic_buff_list_read",
                expression=self._expression_context(node),
                classification_suggestion="raw dynamic_buff_list attribute-read input",
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr == "dynamic_buff_list" and isinstance(node.ctx, ast.Load):
            self._add_calculator_finding(
                line=node.lineno,
                kind="calculator_dynamic_buff_list_read",
                expression=self._expression_context(node),
                classification_suggestion="raw dynamic_buff_list attribute-read input",
            )
        self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> None:
        self.generic_visit(node)

    def _is_multiplier_constructor(self, func: ast.AST) -> bool:
        if isinstance(func, ast.Name):
            return func.id in self._multiplier_aliases
        if isinstance(func, ast.Attribute):
            return func.attr in self._multiplier_aliases
        return False

    def _add_calculator_finding(
        self,
        *,
        line: int,
        kind: str,
        expression: str,
        classification_suggestion: str,
    ) -> None:
        self.findings.append(
            Finding(
                path=self._relative_path(),
                line=line,
                kind=kind,
                matched_expression=self._normalize(expression),
                classification_suggestion=classification_suggestion,
                next_action=CALCULATOR_READ_NEXT_ACTION,
                context=self._context(),
            )
        )


def _collect_findings_from_source(path: Path, source: str) -> list[Finding]:
    tree = ast.parse(source, filename=str(path))
    visitor = RawContainerVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in SCANNED_PRODUCTION_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_findings_from_source(path, source))
    return findings


def _collect_pending_queue_raw_write_findings_from_source(
    path: Path, source: str
) -> list[PendingQueueRawWriteFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = PendingQueueRawWriteVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_pending_queue_raw_write_findings() -> list[PendingQueueRawWriteFinding]:
    findings: list[PendingQueueRawWriteFinding] = []
    for path in SCANNED_PRODUCTION_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_pending_queue_raw_write_findings_from_source(path, source))
    return findings


def _is_allowed_pending_queue_raw_write(
    finding: PendingQueueRawWriteFinding,
) -> bool:
    return (
        finding.path,
        finding.context,
    ) in PENDING_QUEUE_RAW_WRITE_ALLOWED_CONTEXTS


def _collect_active_store_raw_write_findings_from_source(
    path: Path, source: str
) -> list[ActiveStoreRawWriteFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = ActiveStoreRawWriteVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_active_store_raw_write_findings() -> list[ActiveStoreRawWriteFinding]:
    findings: list[ActiveStoreRawWriteFinding] = []
    for path in SCANNED_PRODUCTION_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_active_store_raw_write_findings_from_source(path, source))
    return findings


def _is_allowed_active_store_raw_write(
    finding: ActiveStoreRawWriteFinding,
) -> bool:
    return (
        finding.path,
        finding.context,
    ) in ACTIVE_STORE_RAW_WRITE_ALLOWED_CONTEXTS


def _collect_scheduled_runtime_findings_from_source(
    path: Path, source: str
) -> list[Finding]:
    tree = ast.parse(source, filename=str(path))
    visitor = ScheduledEventRuntimeVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_scheduled_runtime_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in SCHEDULED_EVENT_RUNTIME_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_scheduled_runtime_findings_from_source(path, source))
    return findings


def _collect_runtime_command_legacy_adapter_findings_from_source(
    path: Path, source: str
) -> list[RuntimeCommandLegacyAdapterFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = RuntimeCommandLegacyAdapterVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_runtime_command_legacy_adapter_findings() -> list[
    RuntimeCommandLegacyAdapterFinding
]:
    findings: list[RuntimeCommandLegacyAdapterFinding] = []
    for path in RUNTIME_COMMAND_LEGACY_ADAPTER_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(
            _collect_runtime_command_legacy_adapter_findings_from_source(path, source)
        )
    return findings


def _collect_runtime_command_factory_direct_call_findings_from_source(
    path: Path, source: str
) -> list[RuntimeCommandFactoryDirectCallFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = RuntimeCommandFactoryDirectCallVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_runtime_command_factory_direct_call_findings() -> list[
    RuntimeCommandFactoryDirectCallFinding
]:
    findings: list[RuntimeCommandFactoryDirectCallFinding] = []
    for path in RUNTIME_COMMAND_FACTORY_DIRECT_CALL_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(
            _collect_runtime_command_factory_direct_call_findings_from_source(
                path, source
            )
        )
    return findings


def _collect_scheduled_event_raw_constructor_findings_from_source(
    path: Path, source: str
) -> list[ScheduledEventRawConstructorFinding]:
    tree = ast.parse(source, filename=str(path))
    visitor = ScheduledEventRawConstructorVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_scheduled_event_raw_constructor_findings() -> list[
    ScheduledEventRawConstructorFinding
]:
    findings: list[ScheduledEventRawConstructorFinding] = []
    for path in SCHEDULED_EVENT_RAW_CONSTRUCTOR_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(
            _collect_scheduled_event_raw_constructor_findings_from_source(
                path, source
            )
        )
    return findings


def _collect_calculator_read_findings_from_source(
    path: Path, source: str
) -> list[Finding]:
    tree = ast.parse(source, filename=str(path))
    visitor = CalculatorReadVisitor(path, source)
    visitor.visit(tree)
    return visitor.findings


def _collect_calculator_read_findings() -> list[Finding]:
    findings: list[Finding] = []
    for path in CALCULATOR_READ_GUARDRAIL_FILES:
        source = path.read_text(encoding="utf-8")
        findings.extend(_collect_calculator_read_findings_from_source(path, source))
    return findings


def _allowance_for(finding: Finding) -> str | None:
    path = finding.path
    context = finding.context
    if path == "zsim/simulator/dataclasses.py":
        return "core Load/Schedule/GlobalStats container ownership"
    if path == "zsim/sim_progress/ScheduledEvent/buff_runtime.py":
        return "legacy facade adapter internals"
    if path == "zsim/simulator/simulator_class.py":
        if context == "Simulator.__init_data_struct":
            return "BuffRuntimeState owner construction"
        if context == "Simulator._create_buff_runtime_facade":
            return "legacy facade construction"
    if path == "zsim/sim_progress/Buff/BuffLoad.py":
        return "retained BuffLoadLoop trigger judgement and pending queue population"
    if path == "zsim/sim_progress/Buff/BuffAdd.py":
        if context == "buff_add":
            return "legacy buff_add pending-to-active compatibility path"
        if context == "add_debuff_to_enemy":
            return "legacy buff_add enemy debuff mirror sync"
    if path == "zsim/sim_progress/Buff/JudgeTools/FindMain.py":
        if context == "_legacy_exist_buff_dict_for_compat":
            return "JudgeTools registry compatibility fallback"
    if path == "zsim/sim_progress/Update/Update_Buff.py":
        if context == "update_time_related_effect":
            return "retained Update_Buff time-effect compatibility wrapper"
        if context == "update_buff":
            return "retained Update_Buff active-store traversal and no-facade fallback"
        if context == "KickOutBuff":
            return "legacy KickOutBuff active-removal compatibility path"
    if path == "zsim/sim_progress/ScheduledEvent/__init__.py":
        if context == "ScheduledEvent.__init__":
            return "retained ScheduledEvent constructor setup"
    if path == "zsim/sim_progress/ScheduledEvent/runtime_command.py":
        return "RuntimeCommandPort compatibility reads"
    return None


def _scheduled_runtime_allowance_for(finding: Finding) -> str | None:
    path = finding.path
    context = finding.context
    expression = finding.matched_expression

    if path == "zsim/sim_progress/ScheduledEvent/__init__.py":
        if context == "ScheduledEvent.__init__":
            return "retained ScheduledEvent constructor setup"
        if context == "ScheduledEvent._create_runtime_ports":
            return "runtime view / command adapter setup"
        if context == "ScheduledEvent.event_start" and expression in {
            "dynamic_buff=self.data.dynamic_buff",
            "self.data.dynamic_buff",
        }:
            return "retained SPUpdateData runtime read candidate"

    if path == "zsim/sim_progress/ScheduledEvent/buff_runtime.py":
        return "runtime view / facade adapter internals"

    if path == "zsim/sim_progress/ScheduledEvent/runtime_command.py":
        return "existing RuntimeCommandPort adapter reads"

    if path == "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/skill.py":
        if context == "SkillEventHandler._calculate_damage":
            return "runtime view passed to Calculator formula boundary"

    if path in {
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/abloom.py",
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py",
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/disorder.py",
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/polarity_disorder.py",
    }:
        if context.endswith(".handle"):
            return "runtime view passed to anomaly formula boundary"

    return None


def _runtime_command_legacy_adapter_allowance_for(
    finding: RuntimeCommandLegacyAdapterFinding,
) -> str | None:
    if (
        finding.path == "zsim/sim_progress/ScheduledEvent/runtime_command.py"
        and finding.context == "create_runtime_command_port"
        and finding.kind == "legacy_runtime_command_adapter_constructor"
    ):
        return "explicit legacy runtime command factory fallback"
    return None


def _runtime_command_factory_direct_call_allowance_for(
    finding: RuntimeCommandFactoryDirectCallFinding,
) -> str | None:
    if finding.path.startswith("tests/"):
        return "test-only runtime command-port helper coverage"
    if finding.path.startswith("scripts/"):
        return "migration/rollback runtime command-port helper coverage"
    if (
        finding.path == "zsim/sim_progress/ScheduledEvent/__init__.py"
        and finding.context == "ScheduledEventRuntimePortFactory.create"
    ):
        return "ScheduledEventRuntimePortFactory production boundary"
    return None


def _scheduled_event_raw_constructor_allowance_for(
    finding: ScheduledEventRawConstructorFinding,
) -> str | None:
    return None


def _calculator_read_allowance_for(finding: Finding) -> str | None:
    path = finding.path
    context = finding.context

    if path == "zsim/sim_progress/ScheduledEvent/Calculator.py":
        if (
            context == "Calculator.__init__"
            and finding.kind == "calculator_multiplier_snapshot"
        ):
            return "Calculator formula snapshot construction"

    if path in {
        "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py",
    }:
        if (
            context.endswith(".special_judge_logic")
            and finding.kind == "calculator_dynamic_buff_list_read"
        ):
            return "migrated attribute-reader active_buff_view input"

    if path.startswith("zsim/sim_progress/Buff/BuffXLogic/"):
        return RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE

    return None


def _allowance_counts(findings: list[Finding]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _scheduled_runtime_allowance_counts(findings: list[Finding]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _scheduled_runtime_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _runtime_command_legacy_adapter_allowance_counts(
    findings: list[RuntimeCommandLegacyAdapterFinding],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _runtime_command_legacy_adapter_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _runtime_command_factory_direct_call_allowance_counts(
    findings: list[RuntimeCommandFactoryDirectCallFinding],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _runtime_command_factory_direct_call_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _scheduled_event_raw_constructor_allowance_counts(
    findings: list[ScheduledEventRawConstructorFinding],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _scheduled_event_raw_constructor_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


def _calculator_read_allowance_counts(findings: list[Finding]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        allowance = _calculator_read_allowance_for(finding)
        if allowance is not None:
            counts[allowance] += 1
    return counts


EXPECTED_RETAINED_REFERENCE_CEILINGS = {
    "core Load/Schedule/GlobalStats container ownership": 16,
    "BuffRuntimeState owner construction": 4,
    "legacy facade adapter internals": 59,
    "legacy facade construction": 8,
    # US-002 documents the three metrics-only BuffLoadLoop scan observations
    # that moved this retained-boundary ceiling from 41 to 44.
    "retained BuffLoadLoop trigger judgement and pending queue population": 44,
    "legacy buff_add pending-to-active compatibility path": 10,
    "legacy buff_add enemy debuff mirror sync": 3,
    "JudgeTools registry compatibility fallback": 1,
    "retained Update_Buff time-effect compatibility wrapper": 5,
    "retained Update_Buff active-store traversal and no-facade fallback": 7,
    "legacy KickOutBuff active-removal compatibility path": 5,
    "retained ScheduledEvent constructor setup": 16,
    "RuntimeCommandPort compatibility reads": 11,
}

EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS = {
    "retained ScheduledEvent constructor setup": 16,
    "runtime view / command adapter setup": 6,
    "retained SPUpdateData runtime read candidate": 2,
    "runtime view / facade adapter internals": 63,
    "existing RuntimeCommandPort adapter reads": 11,
    "runtime view passed to Calculator formula boundary": 3,
    "runtime view passed to anomaly formula boundary": 4,
}

EXPECTED_RUNTIME_COMMAND_LEGACY_ADAPTER_CEILINGS = {
    "explicit legacy runtime command factory fallback": 1,
}

EXPECTED_RUNTIME_COMMAND_FACTORY_DIRECT_CALL_CEILINGS = {
    "ScheduledEventRuntimePortFactory production boundary": 1,
}

EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS = {
    # US-001 freezes the US-013 retained snapshot backlog by file. Later
    # migration stories may lower these counts with focused evidence.
    "zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py": 2,
    "zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py": 1,
    "zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py": 1,
}

EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS = {
    "Calculator formula snapshot construction": 1,
    "migrated attribute-reader active_buff_view input": 2,
    RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE: sum(
        EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS.values()
    ),
}


def _calculator_read_retained_snapshot_counts(
    findings: list[Finding],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for finding in findings:
        if (
            _calculator_read_allowance_for(finding)
            == RETAINED_XLOGIC_COMPATIBILITY_SNAPSHOT_ALLOWANCE
        ):
            counts[finding.path] += 1
    return counts


def _calculator_read_retained_snapshot_expansions(
    findings: list[Finding],
) -> dict[str, int]:
    counts = _calculator_read_retained_snapshot_counts(findings)
    return {
        path: count
        for path, count in counts.items()
        if count > EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS.get(path, 0)
    }


def _is_calculator_reader_constructor(func: ast.expr) -> bool:
    if isinstance(func, ast.Name):
        return func.id == "CalculatorBuffAttributeReader"
    if isinstance(func, ast.Attribute):
        return func.attr == "CalculatorBuffAttributeReader"
    return False


def _judge_tools_find_call_name(func: ast.expr) -> str | None:
    if (
        isinstance(func, ast.Attribute)
        and func.attr.startswith("find_")
        and isinstance(func.value, ast.Name)
        and func.value.id == "JudgeTools"
    ):
        return f"JudgeTools.{func.attr}"
    return None


def _is_judge_tools_find_call(func: ast.expr) -> bool:
    return _judge_tools_find_call_name(func) is not None


def _is_check_preparation_call(func: ast.expr) -> bool:
    if isinstance(func, ast.Name):
        return func.id == "check_preparation"
    return isinstance(func, ast.Attribute) and func.attr == "check_preparation"


def _check_preparation_call_has_context(node: ast.Call) -> bool:
    return any(keyword.arg == "preparation_context" for keyword in node.keywords)


def _is_legacy_trigger_tuple_keyword(keyword: ast.keyword) -> bool:
    return keyword.arg == "trigger_buff_0" and isinstance(keyword.value, ast.Tuple)


def _legacy_get_prepared_check_preparation_calls(
    node: ast.FunctionDef,
) -> list[ast.Call]:
    if node.name != "get_prepared":
        return []
    findings: list[ast.Call] = []
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Call)
            and _is_check_preparation_call(child.func)
            and not _check_preparation_call_has_context(child)
        ):
            findings.append(child)
    return findings


def _is_find_exist_buff_dict_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name):
        return node.func.id == "find_exist_buff_dict"
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "find_exist_buff_dict"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "JudgeTools"
    )


def _is_direct_trigger_registry_scan(node: ast.AST) -> bool:
    if not isinstance(node, ast.Subscript):
        return False
    if not _is_find_exist_buff_dict_call(node.value):
        return False
    return not isinstance(node.slice, ast.Constant)


def _is_self_record_dynamic_buff_list(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "dynamic_buff_list"
        and isinstance(node.value, ast.Attribute)
        and node.value.attr == "record"
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "self"
    )


def _is_record_template_class(node: ast.ClassDef) -> bool:
    return node.name == "BuffRecordBaseClass" or node.name.endswith("Record")


def _self_attribute_name(node: ast.AST) -> str | None:
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
    ):
        return node.attr
    return None


def _record_assignment_targets(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, ast.Assign):
        return list(node.targets)
    if isinstance(node, ast.AnnAssign):
        return [node.target]
    if isinstance(node, ast.AugAssign):
        return [node.target]
    return []


def _collect_record_runtime_cache_findings_from_tree(
    path: Path, source: str, tree: ast.AST
) -> list[XLogicAdapterGuardrailFinding]:
    findings: list[XLogicAdapterGuardrailFinding] = []
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    for class_node in (
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and _is_record_template_class(node)
    ):
        for child in ast.walk(class_node):
            for target in _record_assignment_targets(child):
                attribute_name = _self_attribute_name(target)
                if attribute_name not in XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE_FIELDS:
                    continue
                findings.append(
                    XLogicAdapterGuardrailFinding(
                        path=relative_path,
                        line=getattr(target, "lineno", getattr(child, "lineno", 0)),
                        kind=XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE,
                        matched_expression=_adapter_source_for(source, child),
                    )
                )
    return findings


def _adapter_source_for(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        return f"<{type(node).__name__}>"
    return " ".join(segment.strip().split())


def _collect_xlogic_adapter_guardrail_findings_from_source(
    path: Path,
    source: str,
    forbidden_kinds: frozenset[str],
) -> list[XLogicAdapterGuardrailFinding]:
    findings: list[XLogicAdapterGuardrailFinding] = []
    tree = ast.parse(source, filename=str(path))
    relative_path = path.relative_to(PROJECT_ROOT).as_posix()

    if XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE in forbidden_kinds:
        findings.extend(
            _collect_record_runtime_cache_findings_from_tree(path, source, tree)
        )

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and XLOGIC_ADAPTER_LEGACY_GET_PREPARED in forbidden_kinds
        ):
            for call in _legacy_get_prepared_check_preparation_calls(node):
                findings.append(
                    XLogicAdapterGuardrailFinding(
                        path=relative_path,
                        line=call.lineno,
                        kind=XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
                        matched_expression=_adapter_source_for(source, call),
                    )
                )

        if (
            isinstance(node, ast.Subscript)
            and XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN in forbidden_kinds
            and _is_direct_trigger_registry_scan(node)
        ):
            findings.append(
                XLogicAdapterGuardrailFinding(
                    path=relative_path,
                    line=node.lineno,
                    kind=XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN,
                    matched_expression=_adapter_source_for(source, node),
                )
            )

        if not isinstance(node, ast.Call):
            continue

        if (
            XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION in forbidden_kinds
            and _is_calculator_reader_constructor(node.func)
        ):
            findings.append(
                XLogicAdapterGuardrailFinding(
                    path=relative_path,
                    line=node.lineno,
                    kind=XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
                    matched_expression=_adapter_source_for(source, node),
                )
            )

        judge_tools_find_call = _judge_tools_find_call_name(node.func)
        retained_judge_tools_find_calls = (
            XLOGIC_ADAPTER_RETAINED_JUDGE_TOOLS_FIND_CALLS_BY_FILE.get(
                relative_path, frozenset()
            )
        )
        if (
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND in forbidden_kinds
            and judge_tools_find_call is not None
            and judge_tools_find_call not in retained_judge_tools_find_calls
        ):
            findings.append(
                XLogicAdapterGuardrailFinding(
                    path=relative_path,
                    line=node.lineno,
                    kind=XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
                    matched_expression=_adapter_source_for(source, node),
                )
            )

        if XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE in forbidden_kinds:
            for keyword in node.keywords:
                if _is_legacy_trigger_tuple_keyword(keyword):
                    findings.append(
                        XLogicAdapterGuardrailFinding(
                            path=relative_path,
                            line=keyword.value.lineno,
                            kind=XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE,
                            matched_expression=_adapter_source_for(source, keyword),
                        )
                    )

        if XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW in forbidden_kinds:
            for keyword in node.keywords:
                if (
                    keyword.arg == "active_buff_view"
                    and _is_self_record_dynamic_buff_list(keyword.value)
                ):
                    findings.append(
                        XLogicAdapterGuardrailFinding(
                            path=relative_path,
                            line=keyword.value.lineno,
                            kind=XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
                            matched_expression=_adapter_source_for(source, keyword),
                        )
                    )

    return findings


def _collect_xlogic_adapter_guardrail_findings() -> list[XLogicAdapterGuardrailFinding]:
    findings: list[XLogicAdapterGuardrailFinding] = []
    for relative_path, forbidden_kinds in XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS.items():
        path = PROJECT_ROOT / relative_path
        findings.extend(
            _collect_xlogic_adapter_guardrail_findings_from_source(
                path,
                path.read_text(encoding="utf-8"),
                forbidden_kinds,
            )
        )
    return findings


def test_runtime_dependency_zero_scanner_reports_required_schema_and_families() -> None:
    report = RuntimeDependencyZeroScanner(PROJECT_ROOT).build_report(
        expected_zero=True
    )

    assert report["schemaVersion"] == "zsim-runtime-dependency-zero.v1"
    assert report["profile"] == "runtime-dependency-zero"
    assert report["strictExpectedZero"] is True
    assert report["strictCommand"] == RUNTIME_DEPENDENCY_STRICT_COMMAND
    assert report["categorySchema"] == list(RUNTIME_DEPENDENCY_CATEGORIES)
    assert set(report["categories"]) == set(RUNTIME_DEPENDENCY_CATEGORIES)
    assert (
        set(RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES)
        <= set(report["trackedProductionFamilies"])
    )
    assert (
        set(RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES)
        <= set(report["families"])
    )
    assert report["productionRuntimeTotal"] == 0
    assert report["productionRuntimeFamilies"] == []
    assert (
        report["families"][DEFAULT_PATH_LEGACY_RUNTIME_REFERENCE_FAMILY][
            "production runtime"
        ]
        == 0
    )
    assert (
        report["families"][LEGACY_RUNTIME_COMMAND_ADAPTER_FAMILY][
            "production runtime"
        ]
        == 0
    )
    assert (
        report["families"][SCHEDULED_EVENT_IMPLICIT_CONSTRUCTOR_FAMILY][
            "production runtime"
        ]
        == 0
    )
    assert report["findingCount"] > 0


def test_runtime_dependency_zero_scanner_tracks_legacy_command_adapter_separately() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)
    production_findings = scanner.scan_source(
        "zsim/simulator/_fixture.py",
        "from zsim.sim_progress.ScheduledEvent.runtime_command import (\n"
        "    LegacyRuntimeCommandAdapter,\n"
        "    RuntimeCommandPort,\n"
        ")\n"
        "def build_legacy(data, action_stack, sim_instance, exist_buff_dict):\n"
        "    return LegacyRuntimeCommandAdapter(\n"
        "        data=data,\n"
        "        action_stack=action_stack,\n"
        "        sim_instance=sim_instance,\n"
        "        exist_buff_dict=exist_buff_dict,\n"
        "    )\n",
    )
    migration_findings = scanner.scan_source(
        "zsim/sim_progress/ScheduledEvent/runtime_command.py",
        "class LegacyRuntimeCommandAdapter(RuntimeCommandPort):\n"
        "    pass\n",
    )

    assert {
        finding.matched_text
        for finding in production_findings
        if finding.family == LEGACY_RUNTIME_COMMAND_ADAPTER_FAMILY
        and finding.category == "production runtime"
    } == {"LegacyRuntimeCommandAdapter"}
    assert {
        finding.matched_text
        for finding in production_findings
        if finding.family == "stable runtime contract names"
        and finding.category == "stable contract name"
    } == {"RuntimeCommandPort"}
    assert {
        finding.category
        for finding in migration_findings
        if finding.family == LEGACY_RUNTIME_COMMAND_ADAPTER_FAMILY
    } == {"migration-only"}


def test_runtime_dependency_zero_scanner_blocks_scheduled_event_implicit_fallback() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)
    production_findings = scanner.scan_source(
        "zsim/simulator/_fixture.py",
        "from zsim.sim_progress.ScheduledEvent import ScheduledEvent as ScE\n"
        "def build_event(self):\n"
        "    return ScE(\n"
        "        self.global_stats.DYNAMIC_BUFF_DICT,\n"
        "        self.schedule_data,\n"
        "        self.tick,\n"
        "        self.load_data.exist_buff_dict,\n"
        "        self.load_data.action_stack,\n"
        "    )\n",
    )
    runtime_state_findings = scanner.scan_source(
        "zsim/simulator/_fixture.py",
        "from zsim.sim_progress.ScheduledEvent import ScheduledEvent as ScE\n"
        "def build_event(self):\n"
        "    return ScE.from_runtime_state(\n"
        "        schedule_data=self.schedule_data,\n"
        "        tick=self.tick,\n"
        "        action_stack=self.load_data.action_stack,\n"
        "        buff_runtime_state=self.buff_runtime_state,\n"
        "        sim_instance=self,\n"
        "    )\n",
    )
    test_findings = scanner.scan_source(
        "tests/simulator/_fixture.py",
        "from zsim.sim_progress.ScheduledEvent import ScheduledEvent\n"
        "def build_event(dynamic_buff, data, tick, exist_buff_dict, action_stack):\n"
        "    return ScheduledEvent(\n"
        "        dynamic_buff,\n"
        "        data,\n"
        "        tick,\n"
        "        exist_buff_dict,\n"
        "        action_stack,\n"
        "    )\n",
    )

    assert {
        finding.matched_text
        for finding in production_findings
        if finding.family == SCHEDULED_EVENT_IMPLICIT_CONSTRUCTOR_FAMILY
        and finding.category == "production runtime"
    } == {"ScE(...)"}
    assert [
        finding
        for finding in runtime_state_findings
        if finding.family == SCHEDULED_EVENT_IMPLICIT_CONSTRUCTOR_FAMILY
    ] == []
    assert {
        finding.category
        for finding in test_findings
        if finding.family == SCHEDULED_EVENT_IMPLICIT_CONSTRUCTOR_FAMILY
    } == {"test-only"}


def test_runtime_dependency_zero_scanner_classifies_reference_categories() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)
    fixture_source = (
        "# DYNAMIC_BUFF_DICT comment only\n"
        "class UsesPort(RuntimeCommandPort):\n"
        "    def run(self, exist_buff_dict):\n"
        "        return exist_buff_dict\n"
    )

    production_findings = scanner.scan_source("zsim/simulator/_fixture.py", fixture_source)
    test_findings = scanner.scan_source("tests/simulator/_fixture.py", fixture_source)
    docs_findings = scanner.scan_source("docs/_fixture.md", "LegacyBuffRuntimeFacade\n")
    migration_findings = scanner.scan_source(
        "scripts/run_buff_refactor_validation.py",
        "LegacyBuffRuntimeReadAdapter\n",
    )
    runtime_owner_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/BuffLoad.py",
        "def load(exist_buff_dict, LOADING_BUFF_DICT):\n"
        "    return exist_buff_dict, LOADING_BUFF_DICT\n",
    )
    api_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "def leak(sim_instance):\n"
        "    return sim_instance.load_data.exist_buff_dict\n",
    )

    assert "production runtime" in {
        finding.category for finding in production_findings
    }
    assert "comment" in {finding.category for finding in production_findings}
    assert "stable contract name" in {
        finding.category for finding in production_findings
    }
    assert {finding.category for finding in test_findings} == {
        "comment",
        "stable contract name",
        "test-only",
    }
    assert {finding.category for finding in docs_findings} == {"docs-only"}
    assert {finding.category for finding in migration_findings} == {"migration-only"}
    assert {finding.category for finding in runtime_owner_findings} == {
        "migration-only"
    }
    assert "production runtime" in {
        finding.category for finding in api_findings
    }


def test_default_path_legacy_runtime_scanner_blocks_production_defaults() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)
    simulator_findings = scanner.scan_source(
        "zsim/simulator/_fixture.py",
        "from zsim.sim_progress.ScheduledEvent.buff_runtime import create_legacy_buff_runtime_facade\n"
        "def build_default_runtime(self):\n"
        "    self._record_buff_runtime_rebuild('legacy_buff_runtime_facade')\n"
        "    return create_legacy_buff_runtime_facade(runtime_state=self.buff_runtime_state)\n",
    )
    api_findings = scanner.scan_source(
        "zsim/api_src/services/sim_controller/_fixture.py",
        "from zsim.sim_progress.ScheduledEvent.buff_runtime import LegacyBuffRuntimeFacade\n"
        "def build_api_runtime(runtime_state):\n"
        "    return LegacyBuffRuntimeFacade(runtime_state=runtime_state)\n",
    )
    webui_findings = scanner.scan_source(
        "zsim/lib_webui/_fixture.py",
        "DEFAULT_RUNTIME_LABEL = 'legacy_runtime'\n",
    )
    benchmark_findings = scanner.scan_source(
        "zsim/utils/_fixture.py",
        "def build_parser(parser):\n"
        "    parser.add_argument('--legacy-runtime', dest='legacy_runtime')\n",
    )

    assert {
        finding.matched_text
        for finding in simulator_findings
        if finding.family == DEFAULT_PATH_LEGACY_RUNTIME_REFERENCE_FAMILY
        and finding.category == "production runtime"
    } == {
        "create_legacy_buff_runtime_facade",
        "legacy_buff_runtime_facade",
    }
    assert {
        finding.matched_text
        for finding in api_findings
        if finding.family == "LegacyBuffRuntimeFacade"
        and finding.category == "production runtime"
    } == {"LegacyBuffRuntimeFacade"}
    assert {
        finding.matched_text
        for finding in webui_findings
        if finding.family == DEFAULT_PATH_LEGACY_RUNTIME_REFERENCE_FAMILY
        and finding.category == "production runtime"
    } == {"legacy_runtime"}
    assert {
        finding.matched_text
        for finding in benchmark_findings
        if finding.family == DEFAULT_PATH_LEGACY_RUNTIME_REFERENCE_FAMILY
        and finding.category == "production runtime"
    } == {"--legacy-runtime", "legacy_runtime"}


def test_default_path_legacy_runtime_scanner_allows_report_compat_aliases() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)
    consistency_findings = scanner.scan_source(
        "zsim/utils/main_loop_consistency.py",
        "def required_alias(\n"
        "    legacy_runtime: str | None,\n"
        "):\n"
        "    if legacy_runtime is not None:\n"
        "        return legacy_runtime\n"
        "    return {\n"
        '        "legacy_runtime": "report compatibility alias for baseline_runtime",\n'
        '        "legacy_runtime": baseline_label,\n'
        '        "legacy_runtime": "alias for baseline_runtime",\n'
        '        "default_path": report.get("baseline_runtime", report["legacy_runtime"]),\n'
        "    }\n"
        "def optional_alias(\n"
        "    legacy_runtime: str | None = None,\n"
        "):\n"
        "    return run(\n"
        "        legacy_runtime=legacy_runtime,\n"
        "    )\n"
        "parser.add_argument(\n"
        '    "--legacy-runtime",\n'
        ")\n",
    )
    benchmark_findings = scanner.scan_source(
        "zsim/utils/runtime_benchmark.py",
        "def optional_alias(\n"
        "    legacy_runtime: str | None = None,\n"
        "):\n"
        "    report = {\n"
        '        "baseline": first_report.get("baseline_runtime", first_report["legacy_runtime"]),\n'
        '        "legacy": first_report["legacy_runtime"],\n'
        '        "legacy_runtime": baseline_label,\n'
        '        "legacy_runtime": "alias for baseline_runtime",\n'
        "    }\n"
        "    return run(\n"
        "        legacy_runtime=legacy_runtime,\n"
        "        report=report,\n"
        "    )\n"
        "parser.add_argument(\n"
        '    "--legacy-runtime",\n'
        ")\n",
    )

    alias_findings = [
        finding
        for finding in [*consistency_findings, *benchmark_findings]
        if finding.family == DEFAULT_PATH_LEGACY_RUNTIME_REFERENCE_FAMILY
    ]

    assert alias_findings
    assert {finding.category for finding in alias_findings} == {"migration-only"}


def test_template_registry_runtime_dependency_scanner_blocks_direct_load_data_truth_sources() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)

    simulator_findings = scanner.scan_source(
        "zsim/simulator/simulator_class.py",
        "def leak(self):\n"
        "    return self.load_data.exist_buff_dict\n",
    )
    api_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "def leak(sim_instance):\n"
        "    return sim_instance.load_data.exist_buff_dict\n",
    )
    sim_progress_read_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/BuffXLogic/_fixture.py",
        "def leak(sim_instance):\n"
        "    return sim_instance.load_data.exist_buff_dict\n",
    )
    sim_progress_write_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/BuffXLogic/_fixture.py",
        "def leak(sim_instance, templates):\n"
        "    sim_instance.load_data.exist_buff_dict['enemy'] = templates\n",
    )

    for findings in (
        simulator_findings,
        api_findings,
        sim_progress_read_findings,
        sim_progress_write_findings,
    ):
        assert {
            finding.category
            for finding in findings
            if finding.family == "exist_buff_dict"
        } == {"production runtime"}


def test_template_registry_runtime_dependency_scanner_allows_bounded_owner_and_migration_contexts() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)

    simulator_owner_findings = scanner.scan_source(
        "zsim/simulator/simulator_class.py",
        "template_registry=self.load_data.exist_buff_dict,\n",
    )
    simulator_scheduled_event_findings = scanner.scan_source(
        "zsim/simulator/simulator_class.py",
        "    self.load_data.exist_buff_dict,\n",
    )
    judgetools_fallback_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/JudgeTools/FindMain.py",
        "def _legacy_exist_buff_dict_for_compat(sim_instance):\n"
        "    return sim_instance.load_data.exist_buff_dict\n",
    )
    preparation_read_port_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/JudgeTools/PreparationContext.py",
        "return create_buff_runtime_read_port(\n"
        "    exist_buff_dict=sim_instance.load_data.exist_buff_dict,\n"
        ")\n",
    )
    preparation_registry_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/JudgeTools/PreparationContext.py",
        "return BuffTemplateRegistryReadPort(\n"
        "    templates_by_owner=sim_instance.load_data.exist_buff_dict\n"
        ")\n",
    )
    dot_initialization_findings = scanner.scan_source(
        "zsim/sim_progress/Dot/initialization.py",
        "return DotInitializationReadContext(\n"
        "    exist_buff_dict=sim_instance.load_data.exist_buff_dict,\n"
        ")\n",
    )
    runtime_owner_findings = scanner.scan_source(
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "def compat(self):\n"
        "    return self._exist_buff_dict\n",
    )

    for findings in (
        simulator_owner_findings,
        simulator_scheduled_event_findings,
        judgetools_fallback_findings,
        preparation_read_port_findings,
        preparation_registry_findings,
        dot_initialization_findings,
        runtime_owner_findings,
    ):
        assert {
            finding.category
            for finding in findings
            if finding.family == "exist_buff_dict"
        } == {"migration-only"}


def test_pending_queue_runtime_dependency_scanner_classifies_reference_categories() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)

    production_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "def leak(LOADING_BUFF_DICT):\n"
        "    return LOADING_BUFF_DICT['enemy']\n",
    )
    migration_findings = scanner.scan_source(
        "zsim/sim_progress/Buff/BuffLoad.py",
        "def compat(LOADING_BUFF_DICT):\n"
        "    return LOADING_BUFF_DICT\n",
    )
    test_findings = scanner.scan_source(
        "tests/simulator/_fixture.py",
        "def compat(LOADING_BUFF_DICT):\n"
        "    return LOADING_BUFF_DICT\n",
    )
    docs_findings = scanner.scan_source(
        "docs/_fixture.md",
        "LOADING_BUFF_DICT is compatibility-only pending state.\n",
    )
    comment_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "# LOADING_BUFF_DICT historical note only\n"
        "def clean():\n"
        "    return None\n",
    )

    assert {
        finding.category
        for finding in production_findings
        if finding.family == "LOADING_BUFF_DICT"
    } == {"production runtime"}
    assert {
        finding.category
        for finding in migration_findings
        if finding.family == "LOADING_BUFF_DICT"
    } == {"migration-only"}
    assert {
        finding.category
        for finding in test_findings
        if finding.family == "LOADING_BUFF_DICT"
    } == {"test-only"}
    assert {
        finding.category
        for finding in docs_findings
        if finding.family == "LOADING_BUFF_DICT"
    } == {"docs-only"}
    assert {
        finding.category
        for finding in comment_findings
        if finding.family == "LOADING_BUFF_DICT"
    } == {"comment"}


def test_active_store_runtime_dependency_scanner_classifies_compat_references() -> None:
    scanner = RuntimeDependencyZeroScanner(PROJECT_ROOT)

    production_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "def leak(runtime_state):\n"
        "    return runtime_state.active_store_for_compat()\n",
    )
    migration_findings = scanner.scan_source(
        "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
        "def compat(runtime_state):\n"
        "    return runtime_state.active_store_for_compat()\n",
    )
    test_findings = scanner.scan_source(
        "tests/simulator/_fixture.py",
        "def compat(facade):\n"
        "    return facade.active_store_for_compat()\n",
    )
    docs_findings = scanner.scan_source(
        "docs/_fixture.md",
        "`active_store_for_compat()` is a migration-only compatibility view.\n",
    )
    comment_findings = scanner.scan_source(
        "zsim/api_src/_fixture.py",
        "# active_store_for_compat historical note only\n"
        "def clean():\n"
        "    return None\n",
    )

    assert {
        finding.category
        for finding in production_findings
        if finding.family == "active-store compatibility references"
    } == {"production runtime"}
    assert {
        finding.category
        for finding in migration_findings
        if finding.family == "active-store compatibility references"
    } == {"migration-only"}
    assert {
        finding.category
        for finding in test_findings
        if finding.family == "active-store compatibility references"
    } == {"test-only"}
    assert {
        finding.category
        for finding in docs_findings
        if finding.family == "active-store compatibility references"
    } == {"docs-only"}
    assert {
        finding.category
        for finding in comment_findings
        if finding.family == "active-store compatibility references"
    } == {"comment"}


def test_raw_old_container_passthroughs_stay_inside_retained_boundaries() -> None:
    findings = _collect_findings()
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert not disallowed, (
        "Raw old-container guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_raw_old_container_retained_boundary_counts_do_not_expand() -> None:
    findings = _collect_findings()
    counts = _allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_RETAINED_REFERENCE_CEILINGS[allowance]
    }

    assert not expanded, (
        "Raw old-container guardrail found widened retained-boundary references:\n"
        + "\n".join(
            f"- {allowance}: {count} > {EXPECTED_RETAINED_REFERENCE_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_pending_queue_raw_writes_stay_inside_owner_and_compat_adapter() -> None:
    findings = _collect_pending_queue_raw_write_findings()
    disallowed = [
        finding
        for finding in findings
        if not _is_allowed_pending_queue_raw_write(finding)
    ]

    assert not disallowed, (
        "Pending queue ownership guardrail found raw writes outside owner APIs:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )
    assert {
        (finding.path, finding.context, finding.kind)
        for finding in findings
    } == {
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "PendingBuffQueue.reset_for_beneficiaries",
            "pending_queue_subscript_write",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "PendingBuffQueue.enqueue",
            "pending_queue_raw_list_append",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "PendingBuffQueue.__setitem__",
            "pending_queue_subscript_write",
        ),
        (
            "zsim/sim_progress/Buff/BuffLoad.py",
            "_LegacyPendingQueueCompatAdapter.reset_for_beneficiaries",
            "pending_queue_subscript_write",
        ),
        (
            "zsim/sim_progress/Buff/BuffLoad.py",
            "_LegacyPendingQueueCompatAdapter.enqueue",
            "pending_queue_raw_list_append",
        ),
        (
            "zsim/sim_progress/Buff/BuffLoad.py",
            "_LegacyPendingQueueCompatAdapter.__setitem__",
            "pending_queue_subscript_write",
        ),
    }


def test_pending_queue_raw_write_guardrail_blocks_production_dict_and_list_writes() -> None:
    source = (
        "def raw_pending_writes(LOADING_BUFF_DICT, pending_buff_queue, buff):\n"
        "    LOADING_BUFF_DICT['enemy'] = []\n"
        "    pending_buff_queue['enemy'].append(buff)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py"
    findings = _collect_pending_queue_raw_write_findings_from_source(path, source)
    disallowed = [
        finding
        for finding in findings
        if not _is_allowed_pending_queue_raw_write(finding)
    ]

    assert [finding.kind for finding in disallowed] == [
        "pending_queue_subscript_write",
        "pending_queue_raw_list_append",
    ]
    assert "LOADING_BUFF_DICT['enemy']" in disallowed[0].matched_expression
    assert "pending_buff_queue['enemy']" in disallowed[1].matched_expression
    assert f"next action: {PENDING_QUEUE_RAW_WRITE_NEXT_ACTION}" in disallowed[1].message()


def test_active_store_raw_writes_stay_inside_owner_and_migration_adapter() -> None:
    findings = _collect_active_store_raw_write_findings()
    disallowed = [
        finding
        for finding in findings
        if not _is_allowed_active_store_raw_write(finding)
    ]

    assert not disallowed, (
        "Active store ownership guardrail found raw writes outside owner APIs:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )
    assert {
        (finding.path, finding.context, finding.kind)
        for finding in findings
    } == {
        (
            "zsim/simulator/dataclasses.py",
            "ScheduleData.reset_myself",
            "active_store_subscript_write",
        ),
        (
            "zsim/simulator/dataclasses.py",
            "GlobalStats.__post_init__",
            "active_store_subscript_write",
        ),
        (
            "zsim/simulator/dataclasses.py",
            "GlobalStats.reset_myself",
            "active_store_subscript_write",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "BuffRuntimeState._collapse_enemy_debuff_store",
            "active_store_subscript_write",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "ActiveBuffStore.append",
            "active_store_raw_list_append",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "ActiveBuffStore.remove",
            "active_store_raw_list_remove",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "EnemyDebuffMirror.sync",
            "enemy_mirror_raw_list_remove",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "EnemyDebuffMirror.sync",
            "enemy_mirror_raw_list_append",
        ),
        (
            "zsim/sim_progress/ScheduledEvent/buff_runtime.py",
            "EnemyDebuffMirror.remove",
            "enemy_mirror_raw_list_remove",
        ),
    }


def test_active_store_raw_write_guardrail_blocks_production_writes() -> None:
    source = (
        "def raw_active_writes(DYNAMIC_BUFF_DICT, dynamic_buff, runtime_state, facade, enemy, buff):\n"
        "    DYNAMIC_BUFF_DICT['enemy'] = []\n"
        "    DYNAMIC_BUFF_DICT['enemy'].append(buff)\n"
        "    dynamic_buff['enemy'].remove(buff)\n"
        "    active_list = runtime_state.active_store_for_compat()['enemy']\n"
        "    active_list.append(buff)\n"
        "    mirror = runtime_state.enemy_mirror_for_compat()\n"
        "    mirror.remove(buff)\n"
        "    enemy.dynamic.dynamic_debuff_list.append(buff)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py"
    findings = _collect_active_store_raw_write_findings_from_source(path, source)
    disallowed = [
        finding
        for finding in findings
        if not _is_allowed_active_store_raw_write(finding)
    ]

    assert [finding.kind for finding in disallowed] == [
        "active_store_subscript_write",
        "active_store_raw_list_append",
        "active_store_raw_list_remove",
        "active_store_compat_list_append",
        "enemy_mirror_raw_list_remove",
        "enemy_mirror_raw_list_append",
    ]
    message = "\n".join(finding.message() for finding in disallowed)
    assert "matched expression: DYNAMIC_BUFF_DICT['enemy']" in message
    assert "matched expression: active_list" in message
    assert "matched expression: enemy.dynamic.dynamic_debuff_list" in message
    assert "classification suggestion: active-store compatibility write" in message
    assert "classification suggestion: enemy debuff mirror raw write" in message
    assert f"next action: {ACTIVE_STORE_RAW_WRITE_NEXT_ACTION}" in message


def test_main_loop_has_no_raw_container_passthroughs_after_runtime_state_factory() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/simulator/simulator_class.py"
        and finding.context == "Simulator.main_loop"
    ]

    assert findings == []


def test_raw_old_container_guardrail_blocks_main_loop_scheduled_event_handoff() -> None:
    source = (
        "class Simulator:\n"
        "    def main_loop(self):\n"
        "        sce = ScE(\n"
        "            self.global_stats.DYNAMIC_BUFF_DICT,\n"
        "            self.schedule_data,\n"
        "            self.tick,\n"
        "            self.load_data.exist_buff_dict,\n"
        "            self.load_data.action_stack,\n"
        "            loading_buff=self.load_data.LOADING_BUFF_DICT,\n"
        "        )\n"
        "        return sce\n"
    )
    path = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"
    findings = _collect_findings_from_source(path, source)
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert disallowed
    message = "\n".join(finding.message() for finding in disallowed)
    assert "matched expression: self.global_stats.DYNAMIC_BUFF_DICT" in message
    assert "matched expression: self.load_data.exist_buff_dict" in message
    assert "loading_buff=self.load_data.LOADING_BUFF_DICT" in message
    assert "classification suggestion: active store old-container passthrough" in message
    assert "classification suggestion: registry/template old-container passthrough" in message
    assert "classification suggestion: pending queue old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_scheduled_event_raw_container_allowance_is_constructor_only() -> None:
    source = (
        "class ScheduledEvent:\n"
        "    @classmethod\n"
        "    def from_runtime_state(cls, sim_instance):\n"
        "        return sim_instance.global_stats.DYNAMIC_BUFF_DICT\n"
        "    def __init__(self, dynamic_buff, data, tick, exist_buff_dict, action_stack):\n"
        "        self.data = data\n"
        "        self.data.dynamic_buff = dynamic_buff\n"
        "        self.exist_buff_dict = exist_buff_dict\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "__init__.py"
    findings = _collect_findings_from_source(path, source)

    disallowed = [finding for finding in findings if _allowance_for(finding) is None]
    allowed = [finding for finding in findings if _allowance_for(finding) is not None]

    assert disallowed
    assert {finding.context for finding in disallowed} == {
        "ScheduledEvent.from_runtime_state"
    }
    assert {finding.context for finding in allowed} == {"ScheduledEvent.__init__"}
    assert {_allowance_for(finding) for finding in allowed} == {
        "retained ScheduledEvent constructor setup"
    }


def test_scheduled_event_raw_constructor_guardrail_blocks_production_raw_handoff() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent import ScheduledEvent as ScE\n"
        "class Simulator:\n"
        "    def main_loop(self):\n"
        "        sce = ScE(\n"
        "            self.global_stats.DYNAMIC_BUFF_DICT,\n"
        "            self.schedule_data,\n"
        "            self.tick,\n"
        "            self.load_data.exist_buff_dict,\n"
        "            self.load_data.action_stack,\n"
        "            loading_buff=self.load_data.LOADING_BUFF_DICT,\n"
        "            sim_instance=self,\n"
        "        )\n"
        "        return sce\n"
    )
    path = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"
    findings = _collect_scheduled_event_raw_constructor_findings_from_source(
        path, source
    )
    disallowed = [
        finding
        for finding in findings
        if _scheduled_event_raw_constructor_allowance_for(finding) is None
    ]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert "zsim/simulator/simulator_class.py:4" in message
    assert "matched expression: ScE(" in message
    assert (
        "classification suggestion: raw-container ScheduledEvent constructor "
        "handoff"
    ) in message
    assert f"next action: {SCHEDULED_EVENT_RAW_CONSTRUCTOR_NEXT_ACTION}" in message


def test_scheduled_event_raw_constructor_guardrail_allows_from_runtime_state_path() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent import ScheduledEvent as ScE\n"
        "class Simulator:\n"
        "    def main_loop(self):\n"
        "        return ScE.from_runtime_state(\n"
        "            schedule_data=self.schedule_data,\n"
        "            tick=self.tick,\n"
        "            action_stack=self.load_data.action_stack,\n"
        "            buff_runtime_state=self.buff_runtime_state,\n"
        "            sim_instance=self,\n"
        "        )\n"
    )
    path = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"

    assert _collect_scheduled_event_raw_constructor_findings_from_source(
        path, source
    ) == []


def test_scheduled_event_raw_constructor_guardrail_current_production_has_no_bypass() -> None:
    source_path = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"
    source = source_path.read_text(encoding="utf-8")
    findings = _collect_scheduled_event_raw_constructor_findings()
    disallowed = [
        finding
        for finding in findings
        if _scheduled_event_raw_constructor_allowance_for(finding) is None
    ]

    assert "sce = ScE.from_runtime_state(" in source
    assert disallowed == []


def test_scheduled_event_raw_constructor_guardrail_blocks_test_raw_handoff() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent import ScheduledEvent\n"
        "def build_test_event(\n"
        "    dynamic_buff, data, tick, exist_buff_dict, action_stack, loading_buff\n"
        "):\n"
        "    return ScheduledEvent(\n"
        "        dynamic_buff,\n"
        "        data,\n"
        "        tick,\n"
        "        exist_buff_dict,\n"
        "        action_stack,\n"
        "        loading_buff=loading_buff,\n"
        "    )\n"
    )
    path = PROJECT_ROOT / "tests" / "simulator" / "_scheduled_event_fixture.py"
    findings = _collect_scheduled_event_raw_constructor_findings_from_source(
        path, source
    )

    assert len(findings) == 1
    assert _scheduled_event_raw_constructor_allowance_for(findings[0]) is None
    assert findings[0].classification_suggestion == (
        "raw-container ScheduledEvent constructor handoff"
    )
    assert _scheduled_event_raw_constructor_allowance_counts(findings) == Counter()


def test_main_loop_keeps_runtime_api_order_before_scheduled_events() -> None:
    source_path = PROJECT_ROOT / "zsim" / "simulator" / "simulator_class.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    simulator_class = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Simulator"
    )
    main_loop = next(
        node
        for node in simulator_class.body
        if isinstance(node, ast.FunctionDef) and node.name == "main_loop"
    )
    main_loop_source = ast.get_source_segment(source, main_loop)

    assert main_loop_source is not None
    load_index = main_loop_source.index("buff_runtime.load_pending_buffs")
    activate_index = main_loop_source.index("buff_runtime.activate_pending_buffs")
    scheduled_index = main_loop_source.index("sce = ScE.from_runtime_state(")
    shutdown_index = main_loop_source.index("stop_report_threads()")

    assert load_index < activate_index < scheduled_index < shutdown_index
    assert "BuffLoadLoop(" not in main_loop_source
    assert "LOADING_BUFF_DICT" not in main_loop_source


def test_update_buff_active_sweep_is_runtime_owned_without_kickout_fallback() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Update/Update_Buff.py"
    ]

    assert all(finding.context not in {"update_buff", "KickOutBuff"} for finding in findings)

    report = RuntimeDependencyZeroScanner(PROJECT_ROOT).build_report(expected_zero=False)
    assert report["families"]["Update_Buff no-facade fallback"]["production runtime"] == 0


def test_retained_buff_add_module_is_migration_only_without_raw_activation() -> None:
    buff_add_module = importlib.import_module("zsim.sim_progress.Buff.BuffAdd")

    with pytest.raises(RuntimeError, match="migration-only"):
        getattr(buff_add_module, "buff_add")()
    with pytest.raises(RuntimeError, match="migration-only"):
        getattr(buff_add_module, "add_debuff_to_enemy")()

    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Buff/BuffAdd.py"
    ]
    assert findings == []

    report = RuntimeDependencyZeroScanner(PROJECT_ROOT).build_report(expected_zero=False)
    assert report["families"]["retained BuffAdd.py activation"]["production runtime"] == 0


def test_raw_old_container_guardrail_failure_message_includes_triage_fields() -> None:
    source = (
        "def spread(sim_instance):\n"
        "    return handler(sim_instance.global_stats.DYNAMIC_BUFF_DICT)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic" / "_fixture.py"
    findings = _collect_findings_from_source(path, source)

    assert len(findings) == 1
    message = findings[0].message()
    assert "zsim/sim_progress/Buff/BuffXLogic/_fixture.py:2" in message
    assert "matched expression: sim_instance.global_stats.DYNAMIC_BUFF_DICT" in message
    assert "classification suggestion: active store old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_classifies_enemy_debuff_mirror_passthrough() -> None:
    source = (
        "def spread(enemy):\n"
        "    return handler(enemy.dynamic.dynamic_debuff_list)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic" / "_fixture.py"
    findings = _collect_findings_from_source(path, source)

    assert len(findings) == 1
    message = findings[0].message()
    assert "zsim/sim_progress/Buff/BuffXLogic/_fixture.py:2" in message
    assert "matched expression: enemy.dynamic.dynamic_debuff_list" in message
    assert "classification suggestion: enemy debuff mirror old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''DYNAMIC_BUFF_DICT LOADING_BUFF_DICT exist_buff_dict dynamic_buff loading_buff'''\n"
        "    # ScheduleData.dynamic_buff remains a historical note only.\n"
        "    return None\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffXLogic" / "_fixture.py"

    assert _collect_findings_from_source(path, source) == []


def test_schedule_buff_settle_old_container_family_stays_deleted() -> None:
    schedule_buff_settle_path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "ScheduleBuffSettle.py"
    )
    package_init = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "__init__.py"

    assert not schedule_buff_settle_path.exists()
    assert all(path != schedule_buff_settle_path for path in SCANNED_PRODUCTION_FILES)
    assert "ScheduleBuffSettle" not in package_init.read_text(encoding="utf-8")
    assert "ScheduleBuffSettle old-container settlement" not in (
        RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES
    )


def test_judgetools_registry_lookup_boundary_is_only_allowed_fallback() -> None:
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "JudgeTools" / "FindMain.py"
    findings = [
        finding
        for finding in _collect_findings_from_source(
            path,
            path.read_text(encoding="utf-8"),
        )
        if "exist_buff_dict" in finding.matched_expression
    ]

    assert findings
    assert {_allowance_for(finding) for finding in findings} == {
        "JudgeTools registry compatibility fallback"
    }
    assert len(findings) == EXPECTED_RETAINED_REFERENCE_CEILINGS[
        "JudgeTools registry compatibility fallback"
    ]


def test_judgetools_registry_guardrail_blocks_new_direct_load_data_lookup() -> None:
    source = (
        "def unexpected_lookup(sim_instance):\n"
        "    return sim_instance.load_data.exist_buff_dict\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "JudgeTools" / "FindMain.py"
    findings = _collect_findings_from_source(path, source)
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert "zsim/sim_progress/Buff/JudgeTools/FindMain.py:2" in message
    assert "matched expression: sim_instance.load_data.exist_buff_dict" in message
    assert "old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_blocks_new_schedule_buff_settle_raw_write() -> None:
    source = (
        "def unexpected_schedule_write(DYNAMIC_BUFF_DICT, buff):\n"
        "    DYNAMIC_BUFF_DICT['enemy'].append(buff)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "ScheduleBuffSettle.py"
    )
    findings = _collect_findings_from_source(path, source)
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert disallowed
    write_finding = next(finding for finding in disallowed if finding.line == 2)
    message = write_finding.message()
    assert "zsim/sim_progress/Buff/ScheduleBuffSettle.py:2" in message
    assert "matched expression: DYNAMIC_BUFF_DICT['enemy']" in message
    assert "classification suggestion: active store old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_raw_old_container_guardrail_classifies_buff_add_strategy_boundary() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Buff/BuffAddStrategy.py"
    ]

    assert findings == []


def test_raw_old_container_guardrail_blocks_new_buff_add_strategy_pending_write() -> None:
    source = (
        "def let_buff_start(sim_instance, buff):\n"
        "    sim_instance.load_data.LOADING_BUFF_DICT['enemy'].append(buff)\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "BuffAddStrategy.py"
    findings = _collect_findings_from_source(path, source)
    disallowed = [finding for finding in findings if _allowance_for(finding) is None]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert "zsim/sim_progress/Buff/BuffAddStrategy.py:2" in message
    assert "classification suggestion: pending queue old-container passthrough" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_scheduled_event_raw_runtime_access_stays_inside_allowlist() -> None:
    findings = _collect_scheduled_runtime_findings()
    disallowed = [
        finding
        for finding in findings
        if _scheduled_runtime_allowance_for(finding) is None
    ]

    assert not disallowed, (
        "ScheduledEvent raw runtime guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_scheduled_event_context_and_base_do_not_define_legacy_raw_getters() -> None:
    forbidden_contexts = {
        "EventContext.get_legacy_dynamic_buff_dict",
        "EventContext.get_legacy_exist_buff_dict",
        "EventContext.get_dynamic_buff",
        "EventContext.get_exist_buff_dict",
        "BaseEventHandler._get_context_legacy_dynamic_buff",
        "BaseEventHandler._get_context_legacy_exist_buff_dict",
        "BaseEventHandler._get_context_dynamic_buff",
        "BaseEventHandler._get_context_exist_buff_dict",
    }
    findings = _collect_scheduled_runtime_findings()
    retained = [
        finding
        for finding in findings
        if finding.kind == "legacy_runtime_getter_definition"
        and finding.context in forbidden_contexts
    ]

    assert not retained, (
        "ScheduledEvent production context/base legacy raw getter definitions remain:\n"
        + "\n".join(f"- {finding.message()}" for finding in retained)
    )


def test_scheduled_event_raw_runtime_retained_counts_do_not_expand() -> None:
    findings = _collect_scheduled_runtime_findings()
    counts = _scheduled_runtime_allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS[allowance]
    }

    assert not expanded, (
        "ScheduledEvent raw runtime guardrail found widened retained references:\n"
        + "\n".join(
            f"- {allowance}: {count} > "
            f"{EXPECTED_SCHEDULED_RUNTIME_REFERENCE_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_runtime_command_legacy_adapter_stays_inside_explicit_fallback() -> None:
    findings = _collect_runtime_command_legacy_adapter_findings()
    disallowed = [
        finding
        for finding in findings
        if _runtime_command_legacy_adapter_allowance_for(finding) is None
    ]

    assert not disallowed, (
        "RuntimeCommand legacy adapter guardrail found default-path production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_runtime_command_legacy_adapter_retained_counts_do_not_expand() -> None:
    findings = _collect_runtime_command_legacy_adapter_findings()
    counts = _runtime_command_legacy_adapter_allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_RUNTIME_COMMAND_LEGACY_ADAPTER_CEILINGS[allowance]
    }

    assert not expanded, (
        "RuntimeCommand legacy adapter guardrail found widened retained fallbacks:\n"
        + "\n".join(
            f"- {allowance}: {count} > "
            f"{EXPECTED_RUNTIME_COMMAND_LEGACY_ADAPTER_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_runtime_command_legacy_adapter_guardrail_blocks_direct_constructor() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import "
        "LegacyRuntimeCommandAdapter\n"
        "def build_default(data, action_stack, sim_instance, exist_buff_dict):\n"
        "    return LegacyRuntimeCommandAdapter(\n"
        "        data=data,\n"
        "        action_stack=action_stack,\n"
        "        sim_instance=sim_instance,\n"
        "        exist_buff_dict=exist_buff_dict,\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "ScheduledEvent"
        / "event_handlers"
        / "handlers"
        / "_fixture.py"
    )
    findings = _collect_runtime_command_legacy_adapter_findings_from_source(
        path, source
    )
    disallowed = [
        finding
        for finding in findings
        if _runtime_command_legacy_adapter_allowance_for(finding) is None
    ]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert (
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/_fixture.py:3"
        in message
    )
    assert "matched expression: LegacyRuntimeCommandAdapter(" in message
    assert (
        "classification suggestion: legacy runtime command adapter construction"
        in message
    )
    assert f"next action: {RUNTIME_COMMAND_LEGACY_ADAPTER_NEXT_ACTION}" in message


def test_runtime_command_legacy_adapter_guardrail_blocks_factory_without_state() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import "
        "create_runtime_command_port as make_runtime_command_port\n"
        "def build_default(data, action_stack, sim_instance, exist_buff_dict):\n"
        "    return make_runtime_command_port(\n"
        "        data=data,\n"
        "        action_stack=action_stack,\n"
        "        sim_instance=sim_instance,\n"
        "        exist_buff_dict=exist_buff_dict,\n"
        "    )\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "_fixture.py"
    findings = _collect_runtime_command_legacy_adapter_findings_from_source(
        path, source
    )
    disallowed = [
        finding
        for finding in findings
        if _runtime_command_legacy_adapter_allowance_for(finding) is None
    ]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert "zsim/sim_progress/ScheduledEvent/_fixture.py:3" in message
    assert "matched expression: make_runtime_command_port(" in message
    assert (
        "classification suggestion: create_runtime_command_port fallback "
        "without BuffRuntimeState"
    ) in message
    assert f"next action: {RUNTIME_COMMAND_LEGACY_ADAPTER_NEXT_ACTION}" in message


def test_runtime_command_legacy_adapter_guardrail_allows_current_factory_state() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import "
        "RuntimeCommandPort, create_runtime_command_port\n"
        "class LegacyRuntimeCommandAdapter(RuntimeCommandPort):\n"
        "    pass\n"
        "def build_default(\n"
        "    data, action_stack, sim_instance, exist_buff_dict, buff_runtime_state\n"
        "):\n"
        "    return create_runtime_command_port(\n"
        "        data=data,\n"
        "        action_stack=action_stack,\n"
        "        sim_instance=sim_instance,\n"
        "        exist_buff_dict=exist_buff_dict,\n"
        "        buff_runtime_state=buff_runtime_state,\n"
        "    )\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "_fixture.py"

    assert (
        _collect_runtime_command_legacy_adapter_findings_from_source(path, source)
        == []
    )


def test_runtime_command_factory_direct_calls_stay_behind_scheduled_event_factory() -> None:
    findings = _collect_runtime_command_factory_direct_call_findings()
    disallowed = [
        finding
        for finding in findings
        if _runtime_command_factory_direct_call_allowance_for(finding) is None
    ]
    counts = _runtime_command_factory_direct_call_allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_RUNTIME_COMMAND_FACTORY_DIRECT_CALL_CEILINGS[allowance]
    }

    assert not disallowed, (
        "RuntimeCommand factory guardrail found direct production calls:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )
    assert counts == Counter({"ScheduledEventRuntimePortFactory production boundary": 1})
    assert not expanded, (
        "RuntimeCommand factory guardrail found widened production boundaries:\n"
        + "\n".join(
            f"- {allowance}: {count} > "
            f"{EXPECTED_RUNTIME_COMMAND_FACTORY_DIRECT_CALL_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_runtime_command_factory_guardrail_blocks_direct_state_factory_call() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import "
        "create_runtime_command_port as make_runtime_command_port\n"
        "class NewHandler:\n"
        "    def build(self, data, action_stack, sim_instance, buff_runtime_state):\n"
        "        return make_runtime_command_port(\n"
        "            data=data,\n"
        "            action_stack=action_stack,\n"
        "            sim_instance=sim_instance,\n"
        "            buff_runtime_state=buff_runtime_state,\n"
        "        )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "ScheduledEvent"
        / "event_handlers"
        / "handlers"
        / "_fixture.py"
    )
    findings = _collect_runtime_command_factory_direct_call_findings_from_source(
        path, source
    )
    disallowed = [
        finding
        for finding in findings
        if _runtime_command_factory_direct_call_allowance_for(finding) is None
    ]

    assert len(disallowed) == 1
    message = disallowed[0].message()
    assert (
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/_fixture.py:4"
        in message
    )
    assert "matched expression: make_runtime_command_port(" in message
    assert "classification suggestion: direct create_runtime_command_port call" in message
    assert f"next action: {RUNTIME_COMMAND_FACTORY_DIRECT_CALL_NEXT_ACTION}" in message


def test_runtime_command_factory_guardrail_allows_scheduled_event_factory_boundary() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import "
        "create_runtime_command_port\n"
        "class ScheduledEventRuntimePortFactory:\n"
        "    def create(\n"
        "        self, data, action_stack, sim_instance, buff_runtime_state, buff_runtime_view\n"
        "    ):\n"
        "        return create_runtime_command_port(\n"
        "            data=data,\n"
        "            action_stack=action_stack,\n"
        "            sim_instance=sim_instance,\n"
        "            buff_runtime_state=buff_runtime_state,\n"
        "            buff_runtime_view=buff_runtime_view,\n"
        "        )\n"
    )
    path = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent" / "__init__.py"
    findings = _collect_runtime_command_factory_direct_call_findings_from_source(
        path, source
    )

    assert len(findings) == 1
    assert _runtime_command_factory_direct_call_allowance_for(findings[0]) == (
        "ScheduledEventRuntimePortFactory production boundary"
    )
    assert _runtime_command_factory_direct_call_allowance_counts(findings) == Counter(
        {"ScheduledEventRuntimePortFactory production boundary": 1}
    )


def test_runtime_command_factory_guardrail_classifies_test_helper_coverage() -> None:
    source = (
        "from zsim.sim_progress.ScheduledEvent.runtime_command import "
        "create_runtime_command_port\n"
        "def build_test_port(data, action_stack, sim_instance, exist_buff_dict):\n"
        "    return create_runtime_command_port(\n"
        "        data=data,\n"
        "        action_stack=action_stack,\n"
        "        sim_instance=sim_instance,\n"
        "        exist_buff_dict=exist_buff_dict,\n"
        "    )\n"
    )
    path = PROJECT_ROOT / "tests" / "simulator" / "test_runtime_command_port.py"
    findings = _collect_runtime_command_factory_direct_call_findings_from_source(
        path, source
    )

    assert len(findings) == 1
    assert _runtime_command_factory_direct_call_allowance_for(findings[0]) == (
        "test-only runtime command-port helper coverage"
    )


def test_scheduled_event_raw_runtime_guardrail_failure_message_includes_triage_fields() -> None:
    source = (
        "class NewHandler:\n"
        "    def handle(self, context):\n"
        "        return context.get_dynamic_buff()\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "ScheduledEvent"
        / "event_handlers"
        / "handlers"
        / "_fixture.py"
    )
    findings = _collect_scheduled_runtime_findings_from_source(path, source)

    assert len(findings) == 1
    message = findings[0].message()
    assert (
        "zsim/sim_progress/ScheduledEvent/event_handlers/handlers/_fixture.py:3"
        in message
    )
    assert "matched expression: context.get_dynamic_buff" in message
    assert "classification suggestion: compatibility-only legacy runtime getter" in message
    assert f"next action: {TRIAGE_NEXT_ACTION}" in message


def test_scheduled_event_raw_runtime_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''get_dynamic_buff get_legacy_dynamic_buff_dict dynamic_buff loading_buff'''\n"
        "    # context.get_exist_buff_dict() remains a historical note only.\n"
        "    return None\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "ScheduledEvent"
        / "event_handlers"
        / "handlers"
        / "_fixture.py"
    )

    assert _collect_scheduled_runtime_findings_from_source(path, source) == []


def test_calculator_read_surfaces_stay_inside_allowlist() -> None:
    findings = _collect_calculator_read_findings()
    disallowed = [
        finding
        for finding in findings
        if _calculator_read_allowance_for(finding) is None
    ]

    assert not disallowed, (
        "Calculator-read guardrail found disallowed production uses:\n"
        + "\n".join(f"- {finding.message()}" for finding in disallowed)
    )


def test_calculator_read_retained_counts_do_not_expand() -> None:
    findings = _collect_calculator_read_findings()
    counts = _calculator_read_allowance_counts(findings)
    expanded = {
        allowance: count
        for allowance, count in counts.items()
        if count > EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS[allowance]
    }

    assert not expanded, (
        "Calculator-read guardrail found widened retained references:\n"
        + "\n".join(
            f"- {allowance}: {count} > "
            f"{EXPECTED_CALCULATOR_READ_REFERENCE_CEILINGS[allowance]}"
            for allowance, count in sorted(expanded.items())
        )
    )


def test_calculator_read_retained_snapshot_backlog_files_do_not_expand() -> None:
    findings = _collect_calculator_read_findings()
    expanded = _calculator_read_retained_snapshot_expansions(findings)

    assert not expanded, (
        "Calculator-read guardrail found widened retained snapshot files:\n"
        + "\n".join(
            f"- {path}: {count} > "
            f"{EXPECTED_CALCULATOR_READ_RETAINED_SNAPSHOT_COUNTS.get(path, 0)}"
            for path, count in sorted(expanded.items())
        )
    )


def test_xlogic_adapter_migrated_files_do_not_reintroduce_legacy_inputs() -> None:
    findings = _collect_xlogic_adapter_guardrail_findings()

    assert not findings, (
        "Migrated BuffXLogic adapter guardrail found legacy inputs:\n"
        + "\n".join(f"- {finding.message()}" for finding in findings)
    )


def test_full_convergence_campaign_batches_have_xlogic_guardrail_coverage() -> None:
    template_files = (
        FULL_CONVERGENCE_US002_TEMPLATE_FILES + FULL_CONVERGENCE_US004_TEMPLATE_FILES
    )
    trigger_ref_files = FULL_CONVERGENCE_US003_TRIGGER_REF_FILES
    calculator_files = FULL_CONVERGENCE_US005_CALCULATOR_FILES

    assert set(template_files) <= set(XLOGIC_ADAPTER_TEMPLATE_FILES)
    assert set(trigger_ref_files) <= set(XLOGIC_ADAPTER_TRIGGER_REF_FILES)
    assert set(calculator_files) <= set(XLOGIC_ADAPTER_CALCULATOR_SERVICE_FILES)

    for relative_path in template_files:
        assert {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        } <= XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[relative_path]

    for relative_path in trigger_ref_files:
        assert (
            XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN
            in XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[relative_path]
        )

    for relative_path in calculator_files:
        assert {
            XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
            XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
        } <= XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[relative_path]


def test_trigger_ref_tuple_family_has_exact_xlogic_guardrail_coverage() -> None:
    expected_files = {
        "zsim/sim_progress/Buff/BuffXLogic/CordisGerminaSNAAndQIgnoreDefense.py",
        "zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerApBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/SeveredInnocencELEDMGBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerAnomalyBuildupBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/SpectralGazeImpactBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyAdditionalSkillDMGBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCinema4EleResReduce.py",
        "zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/WeepingCradleDMGBonusIncrease.py",
        "zsim/sim_progress/Buff/BuffXLogic/YangiCinema1ApBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/YunkuiTalesSheerAtkBonus.py",
    }
    required_forbidden_kinds = frozenset(
        {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
            XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE,
        }
    )

    assert set(TRIGGER_REF_TUPLE_FAMILY_FILES) == expected_files

    for relative_path in TRIGGER_REF_TUPLE_FAMILY_FILES:
        assert relative_path in XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS
        assert (
            XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE
            in XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[relative_path]
        )
        assert required_forbidden_kinds <= XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[
            relative_path
        ]

        path = PROJECT_ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        file_findings = _collect_xlogic_adapter_guardrail_findings_from_source(
            path,
            source,
            required_forbidden_kinds,
        )

        assert not file_findings
        assert "TriggerBuffRef." in source
        assert "build_preparation_context_from_buff" in source
        _assert_uses_preparation_template_helpers(
            source,
            equipper_required=False,
        )
        assert "JudgeTools.find_equipper" not in source
        assert "JudgeTools.find_exist_buff_dict" not in source

    retained_tick_files = set(TRIGGER_REF_EQUIPMENT_TEMPLATE_RETAINED_TICK_FILES)
    assert retained_tick_files <= set(TRIGGER_REF_TUPLE_FAMILY_FILES)
    assert XLOGIC_ADAPTER_RETAINED_JUDGE_TOOLS_FIND_CALLS_BY_FILE == {
        **{
            relative_path: frozenset({"JudgeTools.find_tick"})
            for relative_path in (
                FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES
                + RESOURCE_REFRESH_EQUIPMENT_TEMPLATE_FILES
            )
        },
        **{
            relative_path: frozenset({"JudgeTools.find_tick"})
            for relative_path in TRIGGER_REF_EQUIPMENT_TEMPLATE_RETAINED_TICK_FILES
        },
    }


def test_trigger_ref_tuple_checkpoint_matches_guardrail_scope() -> None:
    with TRIGGER_REF_TUPLE_CHECKPOINT_PATH.open(encoding="utf-8") as handle:
        checkpoint = json.load(handle)

    migrated_files = {entry["path"] for entry in checkpoint["migratedTupleFiles"]}
    helper_boundaries = {
        boundary["name"] for boundary in checkpoint["helperBoundaries"]
    }
    retained_direct_reads = {
        entry["path"]: set(entry["reads"])
        for entry in checkpoint["retainedDirectTimeWindowReads"]
    }
    blocked_patterns = set(checkpoint["blockedPatterns"])
    disjoint_families = {
        family["name"]: set(family["files"])
        for family in checkpoint["disjointFromFamilies"]
    }
    disjoint_files: set[str] = set().union(*disjoint_families.values())

    assert checkpoint["schemaVersion"] == "zsim-trigger-ref-tuple-checkpoint.v1"
    assert checkpoint["storyId"] == "US-005"
    assert migrated_files == set(TRIGGER_REF_TUPLE_FAMILY_FILES)
    assert {
        "TriggerBuffRef.owner",
        "TriggerBuffRef.equipper",
        "TriggerBuffLookup.find_by_ref",
        "check_preparation",
        "trigger_buff_0_handler",
    } <= helper_boundaries
    assert retained_direct_reads == {
        "zsim/sim_progress/Buff/BuffXLogic/WeepingCradleDMGBonusIncrease.py": {
            "self.record.trigger_buff_0.dy.startticks",
            "self.record.trigger_buff_0.dy.endticks",
        }
    }
    assert {
        XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE,
        XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
        XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN,
        XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
        XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
        XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE,
    } <= blocked_patterns
    assert {
        "copied-output",
        "dot/debuff runtime-state",
        "anomaly-map",
        "edge-detection",
        "event/preload producer",
        "lifecycle",
        "main-loop",
    } <= set(disjoint_families)
    assert set(TRIGGER_REF_TUPLE_FAMILY_FILES).isdisjoint(disjoint_files)
    assert checkpoint["validation"] == [
        "uv run pytest tests/simulator/test_trigger_state_read_only_gates.py tests/simulator/test_buff_raw_container_guardrail.py tests/simulator/test_enemy_dynamic_read_guardrail.py -q",
        "uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events",
        "uv run python scripts/run_buff_refactor_validation.py --typecheck-profile runtime-dependency-zero --runtime-dependency-expected-zero",
    ]


def test_frozen_edge_equipment_template_family_has_exact_guardrail_coverage() -> None:
    expected_files = {
        "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py",
    }
    required_forbidden_kinds = frozenset(
        {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        }
    )

    assert set(FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES) == expected_files

    for relative_path in FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES:
        assert relative_path in XLOGIC_ADAPTER_TEMPLATE_FILES
        assert required_forbidden_kinds <= XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[
            relative_path
        ]

        path = PROJECT_ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        file_findings = _collect_xlogic_adapter_guardrail_findings_from_source(
            path,
            source,
            required_forbidden_kinds,
        )

        assert not file_findings
        assert "build_preparation_context_from_buff" in source
        _assert_uses_preparation_template_helpers(source)
        assert "JudgeTools.find_tick" in source


def test_prd001c_selected_xlogic_helpers_stay_on_preparation_context() -> None:
    selected_files = {
        "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritRateBonus.py",
        "zsim/sim_progress/Buff/BuffXLogic/PolarMetalFreezeBonus.py",
    }

    for relative_path in selected_files:
        path = PROJECT_ROOT / relative_path
        source = path.read_text(encoding="utf-8")

        assert "build_preparation_context_from_buff" in source
        _assert_uses_preparation_template_helpers(source)
        assert "JudgeTools.find_exist_buff_dict" not in source


def test_branch_blade_song_critdamage_preparation_template_has_exact_guardrail_coverage() -> None:
    expected_files = {
        "zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py",
    }
    required_forbidden_kinds = frozenset(
        {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        }
    )

    assert set(BRANCH_BLADE_SONG_CRITDAMAGE_PREPARATION_TEMPLATE_FILES) == expected_files

    for relative_path in BRANCH_BLADE_SONG_CRITDAMAGE_PREPARATION_TEMPLATE_FILES:
        assert relative_path in XLOGIC_ADAPTER_TEMPLATE_FILES
        assert required_forbidden_kinds <= XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[
            relative_path
        ]

        path = PROJECT_ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        file_findings = _collect_xlogic_adapter_guardrail_findings_from_source(
            path,
            source,
            required_forbidden_kinds,
        )

        assert not file_findings
        assert "build_preparation_context_from_buff" in source
        _assert_uses_preparation_template_helpers(source)
        assert "create_calculator_runtime_read_context_from_sim_instance" in source
        assert "JudgeTools.find_equipper" not in source
        assert "JudgeTools.find_exist_buff_dict" not in source


def test_resource_refresh_equipment_template_family_has_exact_guardrail_coverage() -> None:
    expected_files = {
        "zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py",
        "zsim/sim_progress/Buff/BuffXLogic/LunarNoviluna.py",
        "zsim/sim_progress/Buff/BuffXLogic/MagneticStormCharlieSpRecover.py",
        "zsim/sim_progress/Buff/BuffXLogic/SliceofTimeExtraResources.py",
    }
    required_forbidden_kinds = frozenset(
        {
            XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
            XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        }
    )

    assert set(RESOURCE_REFRESH_EQUIPMENT_TEMPLATE_FILES) == expected_files

    for relative_path in RESOURCE_REFRESH_EQUIPMENT_TEMPLATE_FILES:
        assert relative_path in XLOGIC_ADAPTER_TEMPLATE_FILES
        assert required_forbidden_kinds <= XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[
            relative_path
        ]

        path = PROJECT_ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        file_findings = _collect_xlogic_adapter_guardrail_findings_from_source(
            path,
            source,
            required_forbidden_kinds,
        )

        assert not file_findings
        assert "build_preparation_context_from_buff" in source
        _assert_uses_preparation_template_helpers(source)
        assert "JudgeTools.find_equipper" not in source
        assert "JudgeTools.find_exist_buff_dict" not in source


def test_frozen_edge_equipment_template_checkpoint_matches_guardrail_scope() -> None:
    with FROZEN_EDGE_EQUIPMENT_TEMPLATE_CHECKPOINT_PATH.open(
        encoding="utf-8"
    ) as handle:
        checkpoint = json.load(handle)

    selected_files = {entry["path"] for entry in checkpoint["selectedFiles"]}
    helper_boundaries = {
        boundary["name"] for boundary in checkpoint["helperBoundaries"]
    }
    retained_find_calls = {
        entry["path"]: set(entry["calls"])
        for entry in checkpoint["retainedDirectJudgeToolsFindCalls"]
    }
    blocked_patterns = set(checkpoint["blockedPatterns"])
    preserved_guardrail_families = set(checkpoint["preservedGuardrailFamilies"])
    exclusions = {family["name"] for family in checkpoint["exclusions"]}
    deletion_readiness = checkpoint["broadDeletionReadiness"]

    assert checkpoint["schemaVersion"] == (
        "zsim-frozen-edge-equipment-template-checkpoint.v1"
    )
    assert checkpoint["storyId"] == "US-004"
    assert selected_files == set(FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES)
    assert {
        "build_preparation_context_from_buff",
        "PreparationContext.find_equipper",
        "PreparationContext.find_sub_exist_buff_dict",
        "read_enemy_frozen_edge_state",
        "EnemyEdgeStateReadPort",
    } <= helper_boundaries
    assert retained_find_calls == {
        relative_path: {"JudgeTools.find_tick"}
        for relative_path in FROZEN_EDGE_EQUIPMENT_TEMPLATE_FILES
    }
    assert {
        XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND,
        XLOGIC_ADAPTER_LEGACY_GET_PREPARED,
        "JudgeTools.find_equipper(...)",
        "JudgeTools.find_exist_buff_dict(...)",
    } <= blocked_patterns
    assert {
        "trigger tuple",
        "active-view",
        "Calculator reader",
        "enemy helper",
        "event/preload",
        "record/template cache",
    } <= preserved_guardrail_families
    assert {
        "copied-output",
        "Hugo dispatch/report-state",
        "trigger tuple",
        "dot/debuff runtime-state",
        "anomaly-map",
        "event/preload",
        "lifecycle",
        "main-loop",
    } <= exclusions
    assert deletion_readiness == {
        "find_exist_buff_dict": False,
        "find_equipper": False,
        "get_prepared": False,
    }
    assert checkpoint["validation"] == [
        "uv run pytest tests/simulator/test_freeze_stun_edge_detection_characterization.py tests/simulator/test_buff_raw_container_guardrail.py tests/simulator/test_enemy_dynamic_read_guardrail.py -q",
        "uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events",
        "uv run python scripts/run_buff_refactor_validation.py --typecheck-profile runtime-dependency-zero --runtime-dependency-expected-zero",
    ]


def test_full_convergence_zero_census_matches_guardrail_scope() -> None:
    with FULL_CONVERGENCE_ZERO_CENSUS_PATH.open(encoding="utf-8") as handle:
        census = json.load(handle)

    assert census["schemaVersion"] == "zsim-full-convergence-zero-census.v1"
    assert census["storyId"] == "US-009"

    migrated_batches = {
        batch["storyId"]: tuple(batch["files"]) for batch in census["migratedBatches"]
    }
    assert migrated_batches == FULL_CONVERGENCE_MIGRATED_BATCH_FILES

    blockers = {
        blocker["blocker"]: tuple(blocker["files"])
        for blocker in census["remainingCandidatesByBlocker"]
    }
    assert blockers["copied-output payload risk"] == (
        FULL_CONVERGENCE_COPIED_OUTPUT_PAYLOAD_RISK_FILES
    )
    assert blockers["PRD-003/PRD-005 lifecycle scope"] == (
        FULL_CONVERGENCE_LIFECYCLE_SCOPE_FILES
    )
    assert blockers["intentionally retained compatibility path"] == (
        FULL_CONVERGENCE_RETAINED_COMPATIBILITY_FILES
    )
    assert blockers["no oracle"]


def test_us005_active_view_calculator_batch_has_exact_guardrail_coverage() -> None:
    findings = _collect_calculator_read_findings()
    retained_snapshot_counts = _calculator_read_retained_snapshot_counts(findings)
    required_forbidden_kinds = frozenset(
        {
            XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
            XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
        }
    )

    for relative_path in US005_ACTIVE_VIEW_CALCULATOR_FILES:
        assert relative_path in XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS
        assert required_forbidden_kinds.issubset(
            XLOGIC_ADAPTER_MIGRATED_FILE_GUARDRAILS[relative_path]
        )

        path = PROJECT_ROOT / relative_path
        source = path.read_text(encoding="utf-8")
        file_findings = _collect_xlogic_adapter_guardrail_findings_from_source(
            path,
            source,
            required_forbidden_kinds,
        )

        assert not file_findings
        assert retained_snapshot_counts[relative_path] == 0
        assert "create_calculator_runtime_read_context_from_sim_instance" in source
        assert "get_calculator_buff_attribute_reader_service" in source
        assert "CalculatorBuffAttributeReader" not in source


def test_xlogic_adapter_guardrail_preserves_record_field_contract() -> None:
    record_module = importlib.import_module(
        "zsim.sim_progress.Buff.BuffXLogic._buff_record_base_class"
    )
    classifications = record_module.BUFF_RECORD_FIELD_CLASSIFICATION

    assert classifications["cd"] == "mutable_local_state"
    assert classifications["last_active_tick"] == "mutable_local_state"
    assert classifications["trigger_skill_tag"] == "stable_identity"
    assert classifications["additional_damage_skill_tag"] == "stable_identity"
    assert classifications["trigger_buff_0"] == "retained_old_template_link"
    assert not XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE_FIELDS.intersection(classifications)


def test_xlogic_adapter_guardrail_flags_record_runtime_cache_fields() -> None:
    source = (
        "class NewTemplateRecord:\n"
        "    def __init__(self):\n"
        "        self.scheduled_event = None\n"
        "        self.runtime_command_port = None\n"
        "        self.sim_instance = None\n"
        "        self.dot_runtime_writer = None\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_template_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE}),
    )

    assert len(findings) == 4
    assert {finding.kind for finding in findings} == {
        XLOGIC_ADAPTER_RECORD_RUNTIME_CACHE
    }
    messages = [finding.message() for finding in findings]
    assert any("self.scheduled_event = None" in message for message in messages)
    assert any("self.runtime_command_port = None" in message for message in messages)
    assert any("self.sim_instance = None" in message for message in messages)
    assert any("self.dot_runtime_writer = None" in message for message in messages)


def test_xlogic_adapter_guardrail_flags_calculator_reader_regressions() -> None:
    source = (
        "def read(self):\n"
        "    reader = CalculatorBuffAttributeReader()\n"
        "    return reader.read_anomaly_mastery(\n"
        "        active_buff_view=self.record.dynamic_buff_list,\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset(
            {
                XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
                XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
            }
        ),
    )

    assert {finding.kind for finding in findings} == {
        XLOGIC_ADAPTER_DIRECT_ACTIVE_VIEW,
        XLOGIC_ADAPTER_DIRECT_READER_CONSTRUCTION,
    }
    messages = [finding.message() for finding in findings]
    assert any("CalculatorBuffAttributeReader()" in message for message in messages)
    assert any(
        "active_buff_view=self.record.dynamic_buff_list" in message
        for message in messages
    )


def test_xlogic_adapter_guardrail_can_freeze_migrated_judgetools_find_calls() -> None:
    source = (
        "def prepare(self):\n"
        "    return JudgeTools.find_exist_buff_dict(\n"
        "        sim_instance=self.buff_instance.sim_instance,\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND}),
    )

    assert len(findings) == 1
    message = findings[0].message()
    assert "JudgeTools.find_exist_buff_dict" in message
    assert XLOGIC_ADAPTER_BROAD_JUDGE_TOOLS_FIND in message


def test_xlogic_adapter_guardrail_flags_legacy_get_prepared_wrapper() -> None:
    source = (
        "def get_prepared(self, **kwargs):\n"
        "    return check_preparation(\n"
        "        buff_instance=self.buff_instance,\n"
        "        buff_0=self.buff_0,\n"
        "        **kwargs,\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_LEGACY_GET_PREPARED}),
    )

    assert len(findings) == 1
    message = findings[0].message()
    assert "check_preparation" in message
    assert XLOGIC_ADAPTER_LEGACY_GET_PREPARED in message


def test_xlogic_adapter_guardrail_flags_trigger_registry_scans() -> None:
    source = (
        "def prepare(self, operator):\n"
        "    trigger_buff_0 = JudgeTools.find_exist_buff_dict(\n"
        "        sim_instance=self.buff_instance.sim_instance,\n"
        "    )[operator]\n"
        "    return trigger_buff_0\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN}),
    )

    assert len(findings) == 1
    message = findings[0].message()
    assert "find_exist_buff_dict" in message
    assert "[operator]" in message
    assert XLOGIC_ADAPTER_DIRECT_TRIGGER_REGISTRY_SCAN in message


def test_xlogic_adapter_guardrail_flags_legacy_trigger_tuple_keyword() -> None:
    source = (
        "def prepare(self):\n"
        "    return self.get_prepared(\n"
        "        trigger_buff_0=(\"equipper\", \"fixture-trigger\"),\n"
        "    )\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_adapter_fixture.py"
    )

    findings = _collect_xlogic_adapter_guardrail_findings_from_source(
        path,
        source,
        frozenset({XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE}),
    )

    assert len(findings) == 1
    message = findings[0].message()
    assert "trigger_buff_0=(\"equipper\", \"fixture-trigger\")" in message
    assert XLOGIC_ADAPTER_LEGACY_TRIGGER_TUPLE in message


def test_calculator_read_guardrail_rejects_unlisted_retained_snapshot_file() -> None:
    source = (
        "def read(record):\n"
        "    return record.dynamic_buff_list\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_new_retained_calculator_snapshot.py"
    )
    findings = _collect_calculator_read_findings() + (
        _collect_calculator_read_findings_from_source(path, source)
    )

    relative_path = path.relative_to(PROJECT_ROOT).as_posix()
    expanded = _calculator_read_retained_snapshot_expansions(findings)

    assert expanded == {relative_path: 1}


def test_calculator_read_guardrail_failure_message_includes_triage_fields() -> None:
    source = (
        "from .Calculator import MultiplierData as MulData\n"
        "def read(record, enemy, char):\n"
        "    return MulData(enemy, record.dynamic_buff_list, char)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_calculator_read_fixture.py"
    )
    findings = _collect_calculator_read_findings_from_source(path, source)

    assert len(findings) == 2
    messages = [finding.message() for finding in findings]
    assert any(
        "zsim/sim_progress/Buff/BuffXLogic/_calculator_read_fixture.py:3"
        in message
        and "matched expression: MulData(enemy, record.dynamic_buff_list, char)"
        in message
        and "classification suggestion: direct MultiplierData compatibility snapshot"
        in message
        and f"next action: {CALCULATOR_READ_NEXT_ACTION}" in message
        for message in messages
    )
    assert any(
        "matched expression: record.dynamic_buff_list" in message
        and "classification suggestion: raw dynamic_buff_list attribute-read input"
        in message
        and f"next action: {CALCULATOR_READ_NEXT_ACTION}" in message
        for message in messages
    )


def test_calculator_read_guardrail_uses_ast_not_text_matching() -> None:
    source = (
        "def clean():\n"
        "    '''MultiplierData(...) Mul(...) dynamic_buff_list'''\n"
        "    # Planned-event producer notes are not Calculator read evidence.\n"
        "    return None\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_calculator_read_fixture.py"
    )

    assert _collect_calculator_read_findings_from_source(path, source) == []


def test_calculator_read_guardrail_does_not_flag_dispatch_only_producer() -> None:
    source = (
        "from zsim.sim_progress.data_struct.schedule_dispatch import create_schedule_dispatch_port\n"
        "def publish(schedule_data, payload):\n"
        "    create_schedule_dispatch_port(schedule_data).publish(payload)\n"
    )
    path = (
        PROJECT_ROOT
        / "zsim"
        / "sim_progress"
        / "Buff"
        / "BuffXLogic"
        / "_dispatch_fixture.py"
    )

    assert _collect_calculator_read_findings_from_source(path, source) == []
