from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Mapping, Sequence

if TYPE_CHECKING:
    from .. import Buff
    from zsim.simulator.simulator_class import Simulator


@dataclass(frozen=True)
class CharacterLookup:
    characters: Sequence[Any]

    def by_cid(self, cid: int) -> Any:
        for character in self.characters:
            if character.CID == cid:
                return character
        raise ValueError(f"并未找到CID为{cid}的角色！")

    def by_name(self, name: str) -> Any:
        for character in self.characters:
            if character.NAME == name:
                return character
        raise ValueError(f"未找到名为{name}的角色")


@dataclass(frozen=True)
class EquipmentOwnerLookup:
    judge_list_set: Sequence[Sequence[str]]

    def owner_for(self, item_name: str) -> str | None:
        if "二件套" not in item_name:
            for sub_list in self.judge_list_set:
                for item in sub_list:
                    if item == item_name and item != sub_list[3]:
                        return sub_list[0]
        else:
            for sub_list in self.judge_list_set:
                for item in sub_list:
                    if item == item_name and item == sub_list[3]:
                        return sub_list[0]
        return None


@dataclass(frozen=True)
class BuffTemplateRegistryReadPort:
    templates_by_owner: Mapping[str, Mapping[str, Any]]

    def all_templates(self) -> Mapping[str, Mapping[str, Any]]:
        return self.templates_by_owner

    def for_owner(self, owner_name: str) -> Mapping[str, Any]:
        return self.templates_by_owner[owner_name]


@dataclass(frozen=True)
class TriggerBuffLookup:
    template_registry: BuffTemplateRegistryReadPort

    def find_by_operator_and_index(self, operator: str, buff_index: str) -> Any:
        founded_list = []
        for buff_found in self.template_registry.for_owner(operator).values():
            if buff_index in buff_found.ft.index:
                founded_list.append(buff_found)
        if len(founded_list) != 1:
            founded_buff_index_list = [founded_buff.ft.index for founded_buff in founded_list]
            if len(set(founded_buff_index_list)) != len(founded_list):
                raise ValueError(f"在{operator}的sub_exist_buff_dict中找到了2个以上的同名buff！")
            trigger_index_length = len(buff_index)
            for buff_found in founded_list:
                if buff_found.ft.index[-trigger_index_length:] == buff_index:
                    return buff_found
            raise ValueError(
                f"并未找到Buff名后缀为{buff_index}的触发器Buff，说明提供的用于寻找trigger_buff_0的关键词无法有效筛选出触发器，请调整关键词或者数据库Buff Index"
            )
        return founded_list[0]


@dataclass(frozen=True)
class PreparationContext:
    character_lookup: CharacterLookup
    equipment_owner_lookup: EquipmentOwnerLookup
    template_registry: BuffTemplateRegistryReadPort
    trigger_buff_lookup: TriggerBuffLookup
    active_buff_view: Any
    enemy: Any
    action_stack: Any
    preload_data: Any
    char_obj_list: Sequence[Any]

    def find_equipper(self, item_name: str) -> str | None:
        return self.equipment_owner_lookup.owner_for(item_name)

    def find_char_from_cid(self, cid: int) -> Any:
        return self.character_lookup.by_cid(cid)

    def find_char_from_name(self, name: str) -> Any:
        return self.character_lookup.by_name(name)

    def find_sub_exist_buff_dict(self, owner_name: str) -> Mapping[str, Any]:
        return self.template_registry.for_owner(owner_name)

    def find_trigger_buff(self, operator: str, buff_index: str) -> Any:
        return self.trigger_buff_lookup.find_by_operator_and_index(operator, buff_index)


def build_preparation_context_from_sim_instance(
    sim_instance: "Simulator",
) -> PreparationContext:
    template_registry = BuffTemplateRegistryReadPort(
        templates_by_owner=sim_instance.load_data.exist_buff_dict
    )
    return PreparationContext(
        character_lookup=CharacterLookup(sim_instance.char_data.char_obj_list),
        equipment_owner_lookup=EquipmentOwnerLookup(sim_instance.init_data.Judge_list_set),
        template_registry=template_registry,
        trigger_buff_lookup=TriggerBuffLookup(template_registry),
        active_buff_view=sim_instance.global_stats.DYNAMIC_BUFF_DICT,
        enemy=sim_instance.schedule_data.enemy,
        action_stack=sim_instance.load_data.action_stack,
        preload_data=sim_instance.preload.preload_data,
        char_obj_list=sim_instance.char_data.char_obj_list,
    )


def build_preparation_context_from_buff(buff_instance: "Buff") -> PreparationContext:
    return build_preparation_context_from_sim_instance(buff_instance.sim_instance)


def create_calculator_runtime_read_context_from_sim_instance(
    *,
    sim_instance: Any,
    enemy: Any,
    character: Any | None = None,
    query_node: Any | None = None,
    beneficiary: str | None = None,
) -> Any:
    from zsim.sim_progress.ScheduledEvent.Calculator import (
        create_anomaly_attribute_read_context,
    )
    from zsim.sim_progress.ScheduledEvent.Calculator import (
        create_calculator_runtime_read_context_from_sim_instance as _create_calculator_runtime_read_context_from_sim_instance,
    )

    try:
        return _create_calculator_runtime_read_context_from_sim_instance(
            sim_instance=sim_instance,
            enemy=enemy,
            character=character,
            query_node=query_node,
            beneficiary=beneficiary,
        )
    except AttributeError as exc:
        if str(exc) != "sim_instance must expose buff_runtime_state":
            raise
        if hasattr(sim_instance, "global_stats"):
            raise
        return create_anomaly_attribute_read_context(
            enemy=enemy,
            active_buff_view={},
            character=character,
            query_node=query_node,
            sim_instance=sim_instance,
            char_name=beneficiary,
        )
