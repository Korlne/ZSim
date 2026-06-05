from __future__ import annotations

from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping, Sequence

if TYPE_CHECKING:
    from zsim.sim_progress.Buff import Buff


class BuffRuntimeReadPort(ABC):
    """Buff runtime 只读接口。"""

    @abstractmethod
    def get_active_buffs(self, beneficiary: str) -> Sequence["Buff"]:
        """读取指定受益者当前激活中的 Buff。"""

    @abstractmethod
    def get_active_buff_view(self) -> Mapping[str, Sequence["Buff"]]:
        """读取全部受益者的激活 Buff 只读视图。"""

    @abstractmethod
    def get_exist_buff_snapshot(self, beneficiary: str) -> Mapping[str, "Buff"]:
        """读取指定受益者的旧快照 Buff 只读视图。"""

    @abstractmethod
    def get_exist_buff_snapshot_view(self) -> Mapping[str, Mapping[str, "Buff"]]:
        """读取全部受益者的旧快照 Buff 只读视图。"""

    @abstractmethod
    def get_legacy_dynamic_buff_dict(self) -> dict[str, list["Buff"]]:
        """过渡期兼容读口，返回旧 `dynamic_buff` 容器。"""

    @abstractmethod
    def get_legacy_exist_buff_dict(self) -> dict[str, dict[str, "Buff"]]:
        """过渡期兼容读口，返回旧 `exist_buff_dict` 容器。"""


class LegacyBuffRuntimeReadAdapter(BuffRuntimeReadPort):
    """基于旧容器的 Buff runtime 兼容只读适配器。"""

    def __init__(
        self,
        dynamic_buff: dict[str, list["Buff"]],
        exist_buff_dict: dict[str, dict[str, "Buff"]],
    ) -> None:
        self._dynamic_buff = dynamic_buff
        self._exist_buff_dict = exist_buff_dict

    def get_active_buffs(self, beneficiary: str) -> Sequence["Buff"]:
        return tuple(self._dynamic_buff.get(beneficiary, []))

    def get_active_buff_view(self) -> Mapping[str, Sequence["Buff"]]:
        return MappingProxyType(
            {beneficiary: tuple(buffs) for beneficiary, buffs in self._dynamic_buff.items()}
        )

    def get_exist_buff_snapshot(self, beneficiary: str) -> Mapping[str, "Buff"]:
        return MappingProxyType(dict(self._exist_buff_dict.get(beneficiary, {})))

    def get_exist_buff_snapshot_view(self) -> Mapping[str, Mapping[str, "Buff"]]:
        return MappingProxyType(
            {
                beneficiary: MappingProxyType(dict(buff_dict))
                for beneficiary, buff_dict in self._exist_buff_dict.items()
            }
        )

    def get_legacy_dynamic_buff_dict(self) -> dict[str, list["Buff"]]:
        return self._dynamic_buff

    def get_legacy_exist_buff_dict(self) -> dict[str, dict[str, "Buff"]]:
        return self._exist_buff_dict


def create_buff_runtime_read_port(
    *,
    dynamic_buff: dict[str, list["Buff"]],
    exist_buff_dict: dict[str, dict[str, "Buff"]],
) -> BuffRuntimeReadPort:
    """创建 Buff runtime 只读入口，但不把 raw 容器当作主契约继续扩散。"""
    return LegacyBuffRuntimeReadAdapter(
        dynamic_buff=dynamic_buff,
        exist_buff_dict=exist_buff_dict,
    )


__all__ = [
    "BuffRuntimeReadPort",
    "LegacyBuffRuntimeReadAdapter",
    "create_buff_runtime_read_port",
]
