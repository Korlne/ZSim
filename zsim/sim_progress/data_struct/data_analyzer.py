from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any, Sequence

from zsim.define import BACK_ATTACK_RATE
from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import NewAnomaly
from zsim.sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from zsim.sim_progress.anomaly_bar import AnomalyBar
    from zsim.sim_progress.Buff import Buff
    from zsim.sim_progress.Dot.BaseDot import Dot
    from zsim.sim_progress.Preload.SkillsQueue import SkillNode
    from zsim.simulator.simulator_class import Simulator


@lru_cache(maxsize=128)
def cal_buff_total_bonus(
    enabled_buff: Sequence["Buff | Dot"],
    judge_obj: "SkillNode | AnomalyBar | None" = None,
    sim_instance: "Simulator" = None,
    char_name: str | None = None,
) -> dict[str, float]:
    """过滤并计算buff总加成。"""

    # 初始化动态语句字典，用于累加buff效果的值
    dynamic_statement: dict[str, float] = {}

    from zsim.sim_progress.anomaly_bar import AnomalyBar
    from zsim.sim_progress.Buff import Buff
    from zsim.sim_progress.Buff.Effect.definitions import BonusEffect
    from zsim.sim_progress.Dot.BaseDot import Dot
    from zsim.sim_progress.Preload.SkillsQueue import SkillNode

    buff_obj: Buff | Dot
    for buff_obj in enabled_buff:
        # 确保buff是Buff类的实例 或 新适配的 Dot 实例
        if not isinstance(buff_obj, (Buff, Dot)):
            raise TypeError(f"{buff_obj} 不是Buff类型，无法计算！")
        else:
            # 检查buff是否激活
            if not buff_obj.dy.active:
                report_to_log(f"[Warning] 动态buff列表中混入了未激活buff: {str(buff_obj)}，已跳过")
                continue
            # 检查buff的标签是否与技能节点匹配
            if judge_obj is not None:
                if not __check_activation_origin(
                    buff_obj=buff_obj,
                    judge_obj=judge_obj,
                    sim_instance=sim_instance,
                    char_name=char_name,
                ):
                    continue
                if isinstance(judge_obj, SkillNode) and not __check_skill_node(buff_obj, judge_obj):
                    continue
                if isinstance(judge_obj, AnomalyBar) and not __check_special_anomly(
                    buff_obj, judge_obj
                ):
                    continue
            # 获取buff的层数
            count = buff_obj.dy.count
            count = count if count > 0 else 0

            # [Refactor] 使用新架构的 effects 列表
            for effect in buff_obj.effects:
                # 处理 BonusEffect 且启用的效果
                if isinstance(effect, BonusEffect) and effect.enable:
                    key = effect.target_attribute
                    value = effect.value
                    try:
                        dynamic_statement[key] = dynamic_statement.get(key, 0) + value * count
                    except TypeError:
                        continue

    return dynamic_statement


def __check_skill_node(buff: "Buff", skill_node: "SkillNode") -> bool:
    """
    检查 buff 的标签是否与 skill node 匹配。
    """
    # 定义允许的标签类型
    ALLOWED_LABELS = [
        "only_skill",
        "only_label",
        "only_trigger_buff_level",
        "only_back_attack",
        "only_element",
        "only_skill_type",
    ]
    # [Refactor] 直接访问 label
    buff_labels: dict[str, list[str] | str] = buff.ft.label

    # 如果buff没有标签限制，则直接返回True
    if not buff_labels:
        return True

    # 获取技能节点的标签信息
    skill_tag: str = skill_node.skill_tag
    skill_labels: dict[str, Any] = skill_node.labels
    has_relevant_labels = False
    all_labels_satisfied = True

    # 遍历buff的所有标签进行检查
    for label_key, label_value in buff_labels.items():
        if not label_value:
            continue
        if not isinstance(label_value, list):
            raise TypeError(
                f"Buff {buff} 的标签 {label_key} 的值存在，对应Value为：{label_value} ，但不是列表类型。"
            )

        if any(
            [
                __check_label_key(label_key=label_key, target_label_key=_tlk)
                for _tlk in ALLOWED_LABELS
            ]
        ):
            has_relevant_labels = True
            label_satisfied = False

            if __check_label_key(label_key=label_key, target_label_key="only_skill"):
                if skill_tag in label_value:
                    label_satisfied = True
            elif __check_label_key(label_key=label_key, target_label_key="only_label"):
                if skill_labels is None:
                    label_satisfied = False
                elif any(_sub_label in skill_labels.keys() for _sub_label in label_value):
                    label_satisfied = True
            elif __check_label_key(label_key=label_key, target_label_key="only_trigger_buff_level"):
                if skill_node.skill.trigger_buff_level in label_value:
                    label_satisfied = True
            elif __check_label_key(label_key=label_key, target_label_key="only_back_attack"):
                from zsim.sim_progress.RandomNumberGenerator import RNG

                rng: RNG = buff.sim_instance.rng_instance
                normalized_value = rng.random_float()
                if normalized_value <= BACK_ATTACK_RATE:
                    label_satisfied = True
            elif __check_label_key(label_key=label_key, target_label_key="only_element"):
                from zsim.define import ELEMENT_EQUIVALENCE_MAP

                if not isinstance(label_value, list):
                    raise TypeError(f"Buff {buff} 的标签 {label_key} 值不是列表类型。")
                for _ele_type in label_value:
                    if skill_node.element_type in ELEMENT_EQUIVALENCE_MAP[_ele_type]:
                        label_satisfied = True
                        break
            elif __check_label_key(label_key=label_key, target_label_key="only_skill_type"):
                if skill_node.skill.skill_type in label_value:
                    label_satisfied = True

            if not label_satisfied:
                all_labels_satisfied = False

    if not has_relevant_labels:
        return True
    return all_labels_satisfied


def __check_label_key(label_key: str, target_label_key: str):
    """用于筛选出对应的label"""
    pattern = r"_\d{1,2}$"  # 匹配结尾是_加1-2位数字
    import re

    if bool(re.search(pattern, label_key)):
        base_key = label_key.rsplit("_", 1)[0]
    else:
        base_key = label_key
    return base_key == target_label_key


def __check_special_anomly(buff: "Buff", anomaly_node: "AnomalyBar") -> bool:
    """
    检查 buff 的标签是否与异常匹配。
    """
    from zsim.sim_progress.anomaly_bar.Anomalies import (
        AuricInkAnomaly,
        ElectricAnomaly,
        EtherAnomaly,
        FireAnomaly,
        FrostAnomaly,
        IceAnomaly,
        PhysicalAnomaly,
    )
    from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
        DirgeOfDestinyAnomaly as Abloom,
    )
    from zsim.sim_progress.anomaly_bar.CopyAnomalyForOutput import (
        Disorder,
        PolarityDisorder,
    )

    ALLOW_LABELS = ["only_anomaly", "specified_disorder_element_type"]
    SELECT_ANOMALY_MAP = {
        "Disorder": [Disorder],
        "Abloom": [Abloom],
        "PolarityDisorder": [PolarityDisorder],
        "AllAnomaly": [
            IceAnomaly,
            PhysicalAnomaly,
            FireAnomaly,
            FrostAnomaly,
            EtherAnomaly,
            ElectricAnomaly,
            AuricInkAnomaly,
            NewAnomaly,
        ],
    }

    # [Refactor] 直接访问 label
    buff_labels: dict[str, list[str] | str] = buff.ft.label
    if not buff_labels:
        return True

    for label_key, label_value in buff_labels.items():
        if not label_value:
            continue
        if label_key in ALLOW_LABELS:
            if label_key == "only_anomaly":
                if isinstance(label_value, str):
                    if label_value in SELECT_ANOMALY_MAP.keys():
                        for sig_value in SELECT_ANOMALY_MAP[label_value]:
                            if isinstance(anomaly_node, sig_value):
                                return True
                if isinstance(label_value, list):
                    for checked_value in label_value:
                        if checked_value in SELECT_ANOMALY_MAP.keys():
                            for sig_value in SELECT_ANOMALY_MAP[checked_value]:
                                if isinstance(anomaly_node, sig_value):
                                    return True
            elif label_key == "specified_disorder_element_type":
                if not isinstance(anomaly_node, Disorder | PolarityDisorder):
                    continue
                if isinstance(label_value, int):
                    if anomaly_node.element_type == label_value:
                        return True
                if isinstance(label_value, list):
                    for checked_value in label_value:
                        if checked_value == anomaly_node.element_type:
                            return True
            else:
                print(
                    f"【data_analyzer警告】识别到暂无处理逻辑的标签类型：{label_key}，故当前buff{buff.ft.index}无法对对象{type(anomaly_node).__name__}生效"
                )
                return False
    return False


def __check_activation_origin(
    buff_obj: "Buff", judge_obj: "SkillNode | AnomalyBar", sim_instance: "Simulator", char_name: str
):
    """检查buff的label是否存在“only_active_by”"""

    # [Refactor] 直接访问 label 和 beneficiary
    if buff_obj.ft.label is None:
        return True
    if "only_active_by" not in buff_obj.ft.label.keys():
        return True

    from zsim.sim_progress.anomaly_bar import AnomalyBar
    from zsim.sim_progress.Preload import SkillNode

    CID_list = buff_obj.ft.label.get("only_active_by")
    if CID_list[0] == "self":
        beneficiary = buff_obj.ft.beneficiary
        if isinstance(judge_obj, SkillNode):
            skill_result = beneficiary == judge_obj.char_name
            return skill_result
        elif isinstance(judge_obj, AnomalyBar):
            if judge_obj.activated_by is None:
                print(f"未检测到异常对象{judge_obj.element_type}的激活源！")
                return False
            anomaly_result = judge_obj.activated_by.char_name == beneficiary
            return anomaly_result
        else:
            print(f"judge_obj的类型未定义！{type(judge_obj)}")
            return False
    else:
        print(f"尚未定义的“only_active_by参数{CID_list}")
        return False


if __name__ == "__main__":
    base_key = "only_skill"
    key_1 = "only_skill_1"
    key_2 = "only_skill_trigger_buff_level"
    key_3 = "only_skill_trigger_buff_level_1"
    list1 = [key_1, key_2, key_3]
    for _key in list1:
        print(__check_label_key(label_key=_key, target_label_key=base_key))
