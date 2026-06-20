from __future__ import annotations

from abc import ABC, abstractmethod
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping, Sequence

from zsim.sim_progress.Report import report_to_log

if TYPE_CHECKING:
    from zsim.sim_progress.Buff import Buff
    from zsim.sim_progress.Enemy import Enemy


class BuffRuntimeState:
    """Run-scoped Buff runtime owner for retained legacy container identities."""

    def __init__(
        self,
        *,
        template_registry: dict[str, dict[str, "Buff"]],
        pending_queue: dict[str, list["Buff"]],
        active_store: dict[str, list["Buff"]],
        enemy_mirror: list["Buff"],
    ) -> None:
        self._template_registry = template_registry
        self._pending_queue = pending_queue
        self._active_store = active_store
        self._enemy_mirror = enemy_mirror

    def create_facade(self) -> "BuffRuntimeFacade":
        return LegacyBuffRuntimeFacade(runtime_state=self)

    def create_read_port(self) -> "BuffRuntimeReadPort":
        return LegacyBuffRuntimeReadAdapter(runtime_state=self)

    def template_registry_for_compat(self) -> dict[str, dict[str, "Buff"]]:
        return self._template_registry

    def pending_queue_for_compat(self) -> dict[str, list["Buff"]]:
        return self._pending_queue

    def active_store_for_compat(self) -> dict[str, list["Buff"]]:
        return self._active_store

    def enemy_mirror_for_compat(self) -> list["Buff"]:
        return self._enemy_mirror


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
        """过渡期兼容读口，返回旧 `dynamic_buff` 容器。仅供同 tick 写边界读取。"""

    @abstractmethod
    def get_legacy_exist_buff_dict(self) -> dict[str, dict[str, "Buff"]]:
        """过渡期兼容读口，返回旧 `exist_buff_dict` 容器。仅供同 tick 写边界读取。"""


class LegacyBuffRuntimeReadAdapter(BuffRuntimeReadPort):
    """基于旧容器的 Buff runtime 兼容只读适配器。"""

    def __init__(self, *, runtime_state: BuffRuntimeState) -> None:
        self._runtime_state = runtime_state

    def get_active_buffs(self, beneficiary: str) -> Sequence["Buff"]:
        return tuple(self._runtime_state.active_store_for_compat().get(beneficiary, []))

    def get_active_buff_view(self) -> Mapping[str, Sequence["Buff"]]:
        return MappingProxyType(
            {
                beneficiary: tuple(buffs)
                for beneficiary, buffs in self._runtime_state.active_store_for_compat().items()
            }
        )

    def get_exist_buff_snapshot(self, beneficiary: str) -> Mapping[str, "Buff"]:
        return MappingProxyType(
            dict(self._runtime_state.template_registry_for_compat().get(beneficiary, {}))
        )

    def get_exist_buff_snapshot_view(self) -> Mapping[str, Mapping[str, "Buff"]]:
        return MappingProxyType(
            {
                beneficiary: MappingProxyType(dict(buff_dict))
                for beneficiary, buff_dict in self._runtime_state.template_registry_for_compat().items()
            }
        )

    def get_legacy_dynamic_buff_dict(self) -> dict[str, list["Buff"]]:
        # 兼容旧容器身份；仅供同 tick 写边界读取，不是新的主读口。
        return self._runtime_state.active_store_for_compat()

    def get_legacy_exist_buff_dict(self) -> dict[str, dict[str, "Buff"]]:
        # 兼容旧容器身份；仅供同 tick 写边界读取，不是新的主读口。
        return self._runtime_state.template_registry_for_compat()


class BuffRuntimeFacade(ABC):
    """旧 Buff 容器运行时写侧门面。"""

    @abstractmethod
    def get_registered_buff(self, beneficiary: str, buff_index: str) -> "Buff | None":
        """读取旧模板注册表中的 Buff。"""

    @abstractmethod
    def get_registered_buff_view(self, beneficiary: str) -> Mapping[str, "Buff"]:
        """读取旧模板注册表的只读视图。"""

    @abstractmethod
    def enqueue_pending_buff(self, beneficiary: str, buff: "Buff") -> None:
        """写入本 tick 待激活 Buff 队列。"""

    @abstractmethod
    def drain_pending_buffs(self, beneficiary: str) -> list["Buff"]:
        """按旧 pop 顺序清空并返回本 tick 待激活 Buff。"""

    @abstractmethod
    def clear_pending_buffs(self, beneficiary: str) -> None:
        """清空本 tick 待激活 Buff 队列。"""

    @abstractmethod
    def append_active_buff(self, beneficiary: str, buff: "Buff") -> None:
        """写入激活 Buff 容器。"""

    @abstractmethod
    def remove_active_buff(self, beneficiary: str, buff: "Buff") -> None:
        """从激活 Buff 容器移除指定 Buff。"""

    @abstractmethod
    def end_active_buff(self, beneficiary: str, buff: "Buff", *, tick: int) -> None:
        """执行 Buff.end 并从旧 active 容器移除。"""

    @abstractmethod
    def settle_individual_buff_stack(self, buff: "Buff", *, tick: int) -> None:
        """结算层数独立 Buff 的过期 stack。"""

    @abstractmethod
    def find_active_buff_by_index(self, beneficiary: str, buff_index: str) -> "Buff | None":
        """按 Buff index 查找激活 Buff。"""

    @abstractmethod
    def sync_enemy_debuff_mirror(self, buff: "Buff") -> None:
        """按 Buff index 替换 enemy debuff 镜像并追加新 Buff。"""

    @abstractmethod
    def remove_enemy_debuff_mirror(self, buff: "Buff") -> None:
        """按 Buff index 从 enemy debuff 镜像移除 Buff。"""

    @abstractmethod
    def activate_pending_buffs(self, *, timenow: float) -> dict[str, list["Buff"]]:
        """把本 tick 待激活 Buff 提升到旧 active 容器。"""

    @abstractmethod
    def get_pending_queue_for_compat(self, beneficiary: str) -> list["Buff"]:
        """过渡期兼容入口，返回指定受益者的旧待激活队列。"""

    @abstractmethod
    def get_active_buffs_for_compat(self, beneficiary: str) -> list["Buff"]:
        """过渡期兼容入口，返回指定受益者的旧激活 Buff 列表。"""

    @abstractmethod
    def get_enemy_debuff_mirror_for_compat(self) -> list["Buff"]:
        """过渡期兼容入口，返回旧 enemy debuff 镜像列表。"""

    @abstractmethod
    def update_time_related_effects(
        self, *, tick: int, enemy: "Enemy"
    ) -> dict[str, list["Buff"]]:
        """执行本 tick 的时间相关 Buff runtime 扫描。"""


class LegacyBuffRuntimeFacade(BuffRuntimeFacade):
    """基于旧容器身份的 Buff runtime 门面。"""

    def __init__(self, *, runtime_state: BuffRuntimeState) -> None:
        self._runtime_state = runtime_state

    def get_registered_buff(self, beneficiary: str, buff_index: str) -> "Buff | None":
        return self._runtime_state.template_registry_for_compat().get(beneficiary, {}).get(
            buff_index
        )

    def get_registered_buff_view(self, beneficiary: str) -> Mapping[str, "Buff"]:
        return MappingProxyType(
            dict(self._runtime_state.template_registry_for_compat().get(beneficiary, {}))
        )

    def enqueue_pending_buff(self, beneficiary: str, buff: "Buff") -> None:
        self._get_pending_queue(beneficiary).append(buff)

    def drain_pending_buffs(self, beneficiary: str) -> list["Buff"]:
        queue = self._get_pending_queue(beneficiary)
        drained: list["Buff"] = []
        while queue:
            drained.append(queue.pop())
        return drained

    def clear_pending_buffs(self, beneficiary: str) -> None:
        self._get_pending_queue(beneficiary).clear()

    def append_active_buff(self, beneficiary: str, buff: "Buff") -> None:
        self._get_active_buffs(beneficiary).append(buff)

    def remove_active_buff(self, beneficiary: str, buff: "Buff") -> None:
        self._get_active_buffs(beneficiary).remove(buff)

    def end_active_buff(self, beneficiary: str, buff: "Buff", *, tick: int) -> None:
        sub_exist_buff_dict = self._runtime_state.template_registry_for_compat()[
            beneficiary
        ]
        buff.end(tick, sub_exist_buff_dict)
        self.remove_active_buff(beneficiary, buff)
        report_to_log(
            f"[Buff END]:{tick}:{beneficiary} 的 {buff.ft.index} 结束，已从动态列表移除",
            level=4,
        )
        if buff.ft.is_debuff:
            self._runtime_state.enemy_mirror_for_compat().remove(buff)

    def settle_individual_buff_stack(self, buff: "Buff", *, tick: int) -> None:
        expired_stack_items = [
            stack_item for stack_item in buff.dy.built_in_buff_box if stack_item[1] < tick
        ]
        for expired_stack_item in expired_stack_items:
            buff.dy.built_in_buff_box.remove(expired_stack_item)
        buff.dy.count = len(buff.dy.built_in_buff_box)

    def find_active_buff_by_index(self, beneficiary: str, buff_index: str) -> "Buff | None":
        return next(
            (
                active_buff
                for active_buff in self._get_active_buffs(beneficiary)
                if self._get_buff_index(active_buff) == buff_index
            ),
            None,
        )

    def sync_enemy_debuff_mirror(self, buff: "Buff") -> None:
        existing_buff = self._find_enemy_debuff_mirror(buff)
        if existing_buff is not None:
            self._runtime_state.enemy_mirror_for_compat().remove(existing_buff)
        self._runtime_state.enemy_mirror_for_compat().append(buff)

    def remove_enemy_debuff_mirror(self, buff: "Buff") -> None:
        existing_buff = self._find_enemy_debuff_mirror(buff)
        if existing_buff is not None:
            self._runtime_state.enemy_mirror_for_compat().remove(existing_buff)

    def activate_pending_buffs(self, *, timenow: float) -> dict[str, list["Buff"]]:
        for beneficiary in self._runtime_state.pending_queue_for_compat():
            for buff in self.drain_pending_buffs(beneficiary):
                self._activate_pending_buff(beneficiary, buff)
        return self._runtime_state.active_store_for_compat()

    def get_pending_queue_for_compat(self, beneficiary: str) -> list["Buff"]:
        # 兼容旧容器身份；仅供迁移期局部桥接，不是新的主契约。
        return self._get_pending_queue(beneficiary)

    def get_active_buffs_for_compat(self, beneficiary: str) -> list["Buff"]:
        # 兼容旧容器身份；仅供迁移期局部桥接，不是新的主契约。
        return self._get_active_buffs(beneficiary)

    def get_enemy_debuff_mirror_for_compat(self) -> list["Buff"]:
        # 兼容旧容器身份；仅供迁移期局部桥接，不是新的主契约。
        return self._runtime_state.enemy_mirror_for_compat()

    def update_time_related_effects(
        self, *, tick: int, enemy: "Enemy"
    ) -> dict[str, list["Buff"]]:
        from zsim.sim_progress.Update import Update_Buff

        return Update_Buff.update_time_related_effect(
            self._runtime_state.active_store_for_compat(),
            tick,
            self._runtime_state.template_registry_for_compat(),
            enemy,
            runtime_facade=self,
        )

    def _get_pending_queue(self, beneficiary: str) -> list["Buff"]:
        return self._runtime_state.pending_queue_for_compat()[beneficiary]

    def _get_active_buffs(self, beneficiary: str) -> list["Buff"]:
        return self._runtime_state.active_store_for_compat()[beneficiary]

    def _find_enemy_debuff_mirror(self, buff: "Buff") -> "Buff | None":
        buff_index = self._get_buff_index(buff)
        return next(
            (
                existing_buff
                for existing_buff in self._runtime_state.enemy_mirror_for_compat()
                if self._get_buff_index(existing_buff) == buff_index
            ),
            None,
        )

    def _activate_pending_buff(self, beneficiary: str, buff: "Buff") -> None:
        from zsim.sim_progress.Buff.buff_class import Buff

        if not isinstance(buff, Buff):
            raise ValueError(f"loading_buff_dict中的{buff}元素不是Buff类")
        if self._should_skip_pending_buff(buff):
            return

        existing_buff = self.find_active_buff_by_index(beneficiary, buff.ft.index)
        if existing_buff is not None:
            if buff.ft.alltime:
                return
            self.remove_active_buff(beneficiary, existing_buff)

        self.append_active_buff(beneficiary, buff)
        if beneficiary == "enemy":
            self.sync_enemy_debuff_mirror(buff)

    @staticmethod
    def _should_skip_pending_buff(buff: "Buff") -> bool:
        return (
            not buff.dy.active
            or (buff.dy.startticks == 0 and buff.dy.endticks == 0)
            or buff.dy.count == 0
        )

    @staticmethod
    def _get_buff_index(buff: "Buff") -> str:
        return buff.ft.index


def create_buff_runtime_read_port(
    *,
    runtime_state: BuffRuntimeState | None = None,
    dynamic_buff: dict[str, list["Buff"]] | None = None,
    exist_buff_dict: dict[str, dict[str, "Buff"]] | None = None,
) -> BuffRuntimeReadPort:
    """创建 Buff runtime 只读入口，但不把 raw 容器当作主契约继续扩散。"""
    if runtime_state is None:
        if dynamic_buff is None or exist_buff_dict is None:
            raise ValueError("runtime_state or legacy read containers are required")
        runtime_state = BuffRuntimeState(
            template_registry=exist_buff_dict,
            pending_queue={},
            active_store=dynamic_buff,
            enemy_mirror=[],
        )
    return runtime_state.create_read_port()


def create_legacy_buff_runtime_facade(
    *,
    exist_buff_dict: dict[str, dict[str, "Buff"]],
    loading_buff_dict: dict[str, list["Buff"]],
    dynamic_buff_dict: dict[str, list["Buff"]],
    enemy_debuff_mirror: list["Buff"],
) -> BuffRuntimeFacade:
    """创建旧 Buff 容器运行时门面，不复制或替换旧容器身份。"""
    runtime_state = BuffRuntimeState(
        template_registry=exist_buff_dict,
        pending_queue=loading_buff_dict,
        active_store=dynamic_buff_dict,
        enemy_mirror=enemy_debuff_mirror,
    )
    return runtime_state.create_facade()


__all__ = [
    "BuffRuntimeReadPort",
    "BuffRuntimeFacade",
    "BuffRuntimeState",
    "LegacyBuffRuntimeReadAdapter",
    "LegacyBuffRuntimeFacade",
    "create_buff_runtime_read_port",
    "create_legacy_buff_runtime_facade",
]
