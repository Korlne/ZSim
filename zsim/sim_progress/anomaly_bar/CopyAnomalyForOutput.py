from __future__ import annotations

import copy
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any

from .AnomalyBarClass import AnomalyBar

if TYPE_CHECKING:
    from zsim.sim_progress.Preload import SkillNode
    from zsim.simulator.simulator_class import Simulator


class _CopiedAnomalyBase(AnomalyBar):
    def __init__(
        self,
        anomaly_bar: AnomalyBar,
        *,
        active_by: "SkillNode | str | None" = None,
        sim_instance: "Simulator | None" = None,
    ) -> None:
        if not isinstance(anomaly_bar, AnomalyBar):
            raise TypeError(f"{anomaly_bar} 涓嶆槸 AnomalyBar 绫诲瀷")

        copied = copy.deepcopy(anomaly_bar)
        self.__dict__ = copied.__dict__.copy()
        if sim_instance is not None:
            self.sim_instance = sim_instance
        if active_by is not None:
            self.activated_by = self._normalize_active_by(active_by)

    @property
    def activate_by(self) -> Any:
        return self.activated_by

    @activate_by.setter
    def activate_by(self, value: Any) -> None:
        self.activated_by = value

    def _normalize_active_by(self, active_by: "SkillNode | str") -> Any:
        if hasattr(active_by, "skill"):
            return active_by
        if not isinstance(active_by, str):
            return active_by
        if not active_by.isdigit():
            return self.activated_by
        char_obj = self.sim_instance.char_data.find_char_obj(CID=int(active_by))
        if char_obj is None:
            return self.activated_by
        return SimpleNamespace(
            char_name=char_obj.NAME,
            skill_tag=active_by,
            skill=SimpleNamespace(char_obj=char_obj),
        )


class NewAnomaly(_CopiedAnomalyBase):
    pass


class Disorder(_CopiedAnomalyBase):
    def __init__(
        self,
        anomaly_bar: AnomalyBar,
        *,
        active_by: "SkillNode | str | None" = None,
        sim_instance: "Simulator | None" = None,
    ) -> None:
        super().__init__(anomaly_bar, active_by=active_by, sim_instance=sim_instance)
        self.is_disorder = True


class PolarityDisorder(Disorder):
    def __init__(
        self,
        anomaly_bar: AnomalyBar,
        polarity_ratio: float,
        *,
        active_by: "SkillNode | str | None" = None,
        sim_instance: "Simulator | None" = None,
    ) -> None:
        super().__init__(anomaly_bar, active_by=active_by, sim_instance=sim_instance)
        self.polarity_disorder_ratio = polarity_ratio
        self.additional_dmg_ap_ratio = 32


class DirgeOfDestinyAnomaly(NewAnomaly):
    def __init__(
        self,
        anomaly_bar: AnomalyBar,
        *,
        active_by: "SkillNode | str | None" = None,
        sim_instance: "Simulator | None" = None,
    ) -> None:
        super().__init__(anomaly_bar, active_by=active_by, sim_instance=sim_instance)
        self.anomaly_dmg_ratio = 1.0
