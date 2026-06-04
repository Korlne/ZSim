# Buff重构下阶段计划草稿

## 当前状态

- 当前总路线已重置。
- 当前默认阶段为“基础设施解耦”。
- Buff 系统现已明确要求采用事件驱动架构。
- 当前调查型 PRD 已完成生命周期、事件模型、Calculator seam、验证入口与交接包的整理。
- 下一轮 Ralph PRD 应切换为“阶段 1 的首个实现型 PRD”，仍围绕“事件驱动基础设施 + 运行时解耦”，而不是直接挑角色 XLogic 开始迁移。
- 下一轮路线仍然严格遵循 [Buff重构方案.md](./Buff重构方案.md) 中的阶段顺序，不回退到角色驱动式切片。

## 本文档的用途

- 记录“当前 PRD 完成后，下一阶段准备调查什么”。
- 为下一轮 `scripts/ralph/prd.json` 提供调查清单和切片边界。
- 避免 PRD 方向重新漂移回“看到一个 XLogic 就改一个”的模式。

## 当前默认下一轮实现型 PRD 草稿

### 下一轮 PRD 名称建议

`Buff 重构 PRD-2：事件发布入口、EventContext Runtime View 与最小适配层落地`

### 下一轮 PRD 的建议范围

- 建立 `ScheduleDispatchPort` 或等价 publisher gateway，优先替换 `JudgeTools.find_event_list()`、`schedule_data.event_list.append(...)` 这类生产者旁路入口。
- 在 `ScheduledEvent` / `EventContext` 上引入 `buff_runtime_view` 或等价 read port，停止继续把 raw `dynamic_buff` / `exist_buff_dict` 作为 handler 主契约。
- 保持 `Simulator` 仍做总流程编排，但在本轮触达路径中把 Buff 相关发布动作改经 gateway 或 runtime facade，而不是继续直写旧队列和旧容器。
- 若切片容量允许，只补当前触达路径需要的最小适配层，不顺手扩大到 `UpdateAnomaly` 全量拆分、`Calculator` 迁移或 enemy debuff 单一事实源收口。

### 下一轮 PRD 的建议产物

- `ScheduleDispatchPort`、发布者 gateway、`BuffRuntimeReadPort` / `buff_runtime_view` 的最小可运行接口。
- 至少一组把生产者旁路入口改经 gateway 的落地样本。
- `ScheduledEvent` / `EventContext` 的最小接线改造与旧系统适配器。
- 聚焦事件顺序与发布边界的单元测试或 focused pytest。
- 继续复用 `scripts/run_buff_refactor_validation.py` 的现有切片命令。
- 把主循环一致性验证入口和性能验证入口落成真实命令，或至少落成可运行的脚本骨架与输出字段约定。

### 下一轮 PRD 的非目标

- 不做具体角色的大面积 XLogic 替换。
- 不在同一切片里同时重写 `ScheduledEvent` 全部 handler、`UpdateAnomaly` 全部逻辑和 `Calculator` 全量公式。
- 不删除旧 Buff 核心路径或旧容器字段，只允许先包出边界和适配层。
- 不把 `listener_manager.broadcast_event()`、计划事件队列和 runtime 立即写入口重新混成单一“事件总线”。
- 不在没有 `main_loop` 一致性证据前提前下最终性能或完成结论。

## 下一轮 PRD 的验证要求

- 必跑：`uv run python scripts/run_buff_refactor_validation.py`
- 必跑：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`
- 按触达范围决定是否追加：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`
- 必须把主循环一致性验证与性能验证写成真实命令或明确占位脚本，并在 PRD 中说明输出字段和比较维度。

## 下一轮 PRD 开始前必须先看的文件

- [Buff重构方案.md](./Buff重构方案.md)
- [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)
  重点先看 `6.6`、`6.7`、`6.8`、`6.9`
- [Buff系统重构Checklist.md](./Buff系统重构Checklist.md)
- `scripts/ralph/progress.txt`
  重点先看 `## Codebase Patterns`

## 基础设施阶段完成后的下一轮调查提纲

当“阶段一：基础设施解耦”的实现型 PRD 完成后，下一轮 PRD 再切到“XLogic 全量分析与复用收敛”，调查重点如下：

- 哪些 XLogic 只是属性读取问题。
- 哪些 XLogic 可以直接映射到已有事件类型，哪些需要新增事件类型。
- 哪些 XLogic 主要问题是 `dynamic_buff_list / sub_exist_buff_dict`。
- 哪些 XLogic 会跨到 `ScheduledEvent`、`UpdateAnomaly`、`dot`、`anomaly_bar`。
- 哪些 count 写回逻辑可以提炼为公共方法。
- 哪些 record 同步逻辑可以提炼为公共基类或公共服务。
- 哪些旧触发链需要合并成公共事件处理器或统一订阅模式。

## 每次更新本文档时必须补充的内容

- 本轮 PRD 消解了哪些耦合点。
- 本轮 PRD 没解决但暴露出来的新耦合点。
- 本轮 PRD 新增或确认了哪些事件类型、事件上下文与事件顺序约束。
- 下一轮 PRD 开始前必须先看的文件。
- 下一轮 PRD 的非目标。
