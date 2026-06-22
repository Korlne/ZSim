from __future__ import annotations

import ast
import importlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from scripts.run_buff_refactor_validation import (
    RUNTIME_DEPENDENCY_CATEGORIES,
    RUNTIME_DEPENDENCY_STRICT_COMMAND,
    RUNTIME_DEPENDENCY_TRACKED_PRODUCTION_FAMILIES,
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
    PROJECT_ROOT / "zsim" / "sim_progress" / "Buff" / "ScheduleBuffSettle.py",
)

SCHEDULED_EVENT_DIR = PROJECT_ROOT / "zsim" / "sim_progress" / "ScheduledEvent"
EVENT_HANDLERS_DIR = SCHEDULED_EVENT_DIR / "event_handlers"
SCHEDULED_EVENT_RUNTIME_GUARDRAIL_FILES = (
    SCHEDULED_EVENT_DIR / "__init__.py",
    SCHEDULED_EVENT_DIR / "buff_runtime.py",
    SCHEDULED_EVENT_DIR / "runtime_command.py",
    *sorted(EVENT_HANDLERS_DIR.rglob("*.py")),
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

CALCULATOR_READ_NEXT_ACTION = (
    "migrate read-only usage to CalculatorBuffAttributeReader, retain as "
    "documented formula/compatibility snapshot, or block the story"
)

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

SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY = (
    "legacy ScheduleBuffSettle command-adapter internals"
)

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

SCHEDULE_BUFF_SETTLE_RETAINED_SIGNATURES = {
    (
        "ScheduleBuffSettle",
        "raw_container_parameter",
        "ScheduleBuffSettle(..., exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_parameter",
        "ScheduleBuffSettle(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "sub_exist_buff_dict = exist_buff_dict[char_name]",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "exist_buff_dict[char_name]",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "ScheduleBuffSettle",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_parameter",
        "process_schedule_on_field_buff(..., sub_exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_parameter",
        "process_schedule_on_field_buff(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_on_field_buff",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_parameter",
        "process_schedule_backend_buff(..., sub_exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_parameter",
        "process_schedule_backend_buff(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "process_schedule_backend_buff",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT",
        "active store old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_parameter",
        "add_schedule_buff(..., sub_exist_buff_dict, ...)",
        "registry/template old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_parameter",
        "add_schedule_buff(..., DYNAMIC_BUFF_DICT, ...)",
        "active store old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_name",
        "sub_exist_buff_dict",
        "registry/template old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_name",
        "DYNAMIC_BUFF_DICT[characters]",
        "active store old-container passthrough",
    ),
    (
        "add_schedule_buff",
        "raw_container_attribute",
        "enemy.dynamic.dynamic_debuff_list",
        "enemy debuff mirror old-container passthrough",
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
        if context == "Simulator.main_loop":
            return "retained ScheduledEvent main-loop boundary"
    if path == "zsim/sim_progress/Buff/BuffLoad.py":
        return "retained BuffLoadLoop trigger judgement and pending queue population"
    if path == "zsim/sim_progress/Buff/BuffAdd.py":
        if context == "buff_add":
            return "legacy buff_add pending-to-active compatibility path"
        if context == "add_debuff_to_enemy":
            return "legacy buff_add enemy debuff mirror sync"
    if path == "zsim/sim_progress/Buff/ScheduleBuffSettle.py":
        signature = (
            context,
            finding.kind,
            finding.matched_expression,
            finding.classification_suggestion,
        )
        if signature in SCHEDULE_BUFF_SETTLE_RETAINED_SIGNATURES:
            return SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY
    if path == "zsim/sim_progress/Update/Update_Buff.py":
        if context == "update_time_related_effect":
            return "retained Update_Buff time-effect compatibility wrapper"
        if context == "update_buff":
            return "retained Update_Buff active-store traversal and no-facade fallback"
        if context == "KickOutBuff":
            return "legacy KickOutBuff active-removal compatibility path"
    if path == "zsim/sim_progress/ScheduledEvent/__init__.py":
        return "retained ScheduledEvent raw-container boundary"
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
    "retained ScheduledEvent main-loop boundary": 2,
    # US-002 documents the three metrics-only BuffLoadLoop scan observations
    # that moved this retained-boundary ceiling from 41 to 44.
    "retained BuffLoadLoop trigger judgement and pending queue population": 44,
    "legacy buff_add pending-to-active compatibility path": 10,
    "legacy buff_add enemy debuff mirror sync": 3,
    SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY: 26,
    "retained Update_Buff time-effect compatibility wrapper": 5,
    "retained Update_Buff active-store traversal and no-facade fallback": 7,
    "legacy KickOutBuff active-removal compatibility path": 5,
    "retained ScheduledEvent raw-container boundary": 21,
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
    assert report["findingCount"] > 0


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


def test_main_loop_keeps_buffload_pending_queue_behind_runtime_api() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/simulator/simulator_class.py"
        and finding.context == "Simulator.main_loop"
    ]

    assert all(
        finding.classification_suggestion != "pending queue old-container passthrough"
        for finding in findings
    )


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
    scheduled_index = main_loop_source.index("sce = ScE(")
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


def test_raw_old_container_guardrail_classifies_schedule_buff_settle_boundary() -> None:
    findings = [
        finding
        for finding in _collect_findings()
        if finding.path == "zsim/sim_progress/Buff/ScheduleBuffSettle.py"
    ]
    allowances = {_allowance_for(finding) for finding in findings}
    classifications = {finding.classification_suggestion for finding in findings}

    assert findings
    assert allowances == {SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY}
    assert "active store old-container passthrough" in classifications
    assert "enemy debuff mirror old-container passthrough" in classifications
    assert (
        len(findings)
        == EXPECTED_RETAINED_REFERENCE_CEILINGS[SCHEDULE_BUFF_SETTLE_RETAINED_BOUNDARY]
    )


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
        assert "preparation_context.find_sub_exist_buff_dict(" in source
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
        assert "preparation_context.find_equipper(" in source
        assert "preparation_context.find_sub_exist_buff_dict(" in source
        assert "JudgeTools.find_tick" in source


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
        assert "preparation_context.find_equipper(" in source
        assert "preparation_context.find_sub_exist_buff_dict(" in source
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
