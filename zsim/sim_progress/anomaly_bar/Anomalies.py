from dataclasses import dataclass
from .AnomalyBarClass import AnomalyBar

class AnomalyBuffIDs:
    SHOCK = "9001"
    IGNITE = "9002"
    CORRUPTION = "9003"
    FREEZE = "9004"
    #暂时保留旧 ID， buff_db.json 里重构后再修改了
    ASSAULT_DEBUFF = "Buff-异常-畏缩" 
    FROST_DEBUFF = "Buff-异常-霜寒"

@dataclass
class PhysicalAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 0
        self.accompany_debuff = [AnomalyBuffIDs.ASSAULT_DEBUFF]
        self.max_duration = 0
        # 简(Jane)的代码重构后再修改
        self.duration_buff_list = ["Buff-角色-简-核心被动-啮咬触发器"]
        self.basic_max_duration = 600
        self.duration_buff_key_list = [
            "畏缩时间延长",
            "所有异常时间延长",
            "畏缩时间延长百分比",
            "所有异常时间延长百分比",
        ]

    def __hash__(self):
        return hash(self.UUID)


@dataclass
class FireAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.accompany_dot = AnomalyBuffIDs.IGNITE 
        self.element_type = 1
        self.basic_max_duration = 600
        self.duration_buff_list = ["Buff-角色-柏妮思-组队被动-延长灼烧"]
        self.max_duration = 0
        self.duration_buff_key_list = [
            "灼烧时间延长",
            "所有异常时间延长",
            "灼烧时间延长百分比",
            "所有异常时间延长百分比",
        ]


@dataclass
class IceAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 2
        self.accompany_debuff = [AnomalyBuffIDs.FROST_DEBUFF]
        self.accompany_dot = AnomalyBuffIDs.FREEZE
        self.basic_max_duration = 600
        self.max_duration = 0
        self.duration_buff_key_list = [
            "霜寒时间延长",
            "所有异常时间延长",
            "霜寒时间延长百分比",
            "所有异常时间延长百分比",
        ]


@dataclass
class ElectricAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 3
        self.accompany_dot = AnomalyBuffIDs.SHOCK
        self.basic_max_duration = 600
        self.duration_buff_list = ["Buff-角色-丽娜-组队被动-延长感电"]
        self.max_duration = 0
        self.duration_buff_key_list = [
            "感电时间延长",
            "所有异常时间延长",
            "感电时间延长百分比",
            "所有异常时间延长百分比",
        ]


@dataclass
class EtherAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 4
        self.accompany_dot = AnomalyBuffIDs.CORRUPTION
        self.basic_max_duration = 600
        self.max_duration = 0
        self.duration_buff_key_list = [
            "侵蚀时间延长",
            "所有异常时间延长",
            "侵蚀时间延长百分比",
            "所有异常时间延长百分比",
        ]


@dataclass
class FrostAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 5
        # 烈霜也使用冻结逻辑
        self.accompany_dot = AnomalyBuffIDs.FREEZE
        self.basic_max_duration = 1200
        self.accompany_debuff = ["Buff-异常-烈霜霜寒", "Buff-角色-雅-核心被动-霜灼"]
        self.max_duration = 0
        self.duration_buff_key_list = [
            "烈霜霜寒时间延长",
            "所有异常时间延长",
            "烈霜霜寒时间延长百分比",
            "所有异常时间延长百分比",
        ]


@dataclass
class AuricInkAnomaly(AnomalyBar):
    def __post_init__(self):
        super().__post_init__()
        self.element_type = 6
        #暂时复用侵蚀 ID
        self.accompany_dot = AnomalyBuffIDs.CORRUPTION 
        self.basic_max_duration = 600
        self.max_duration = 0
        self.duration_buff_key_list = [
            "玄墨侵蚀时间延长",
            "所有异常时间延长",
            "玄墨侵蚀时间延长百分比",
            "所有异常时间延长百分比",
        ]