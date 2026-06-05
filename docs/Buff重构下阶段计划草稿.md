# Buff重构下阶段计划草稿

## 当前状态

- 当前总路线已重置。
- 当前默认阶段仍为“基础设施解耦”。
- Buff 系统现已明确要求采用事件驱动架构。
- 阶段 1 当前实现基线已经落地：
  - `ScheduleDispatchPort` 已接入 `SchedulePreload`、`QuickAssistSystem`、`UpdateAnomaly` 以及 `BattleEventListener` 中的 `AliceDotTriggerListener` 样本路径；剩余 raw `event_list` producer 主要收敛到代表性 `BuffXLogic` / `PolarizedAssaultEvent` 与其他未迁移监听器入口。
  - `BuffRuntimeReadPort` / `EventContext.buff_runtime_view` 已接入 `ScheduledEvent`，`anomaly`、`abloom`、`disorder`、`polarity_disorder` 与高风险 `SkillEventHandler` 主读路径已改用 runtime view。
  - 当前尚未引入新的 `runtime_command_port` / write facade；`ScheduleBuffSettle()`、`update_anomaly()` 等同 tick 写边界仍保留 legacy 容器身份。
  - `scripts/run_buff_main_loop_consistency.py` 与 `scripts/run_buff_runtime_benchmark.py` 已是仓库内真实命令入口，不再是占位脚本。
  - `--legacy-runtime` / `--candidate-runtime` 仍只是报告标签；live simulator 还未消费 `config.buff_runtime.mode`。
- 下一轮 Ralph PRD 仍应留在阶段 1，继续围绕“剩余发布入口收口 + 高风险 runtime 边界推进”，而不是直接挑角色 XLogic 开始迁移。
- 下一轮路线仍然严格遵循 [Buff重构方案.md](./Buff重构方案.md) 中的阶段顺序，不回退到角色驱动式切片。

## 本文档的用途

- 记录“当前 PRD 完成后，下一阶段准备调查什么”。
- 为下一轮 `scripts/ralph/prd.json` 提供调查清单和切片边界。
- 避免 PRD 方向重新漂移回“看到一个 XLogic 就改一个”的模式。

## 当前默认下一轮实现型 PRD 草稿

### 下一轮 PRD 名称建议

`Buff 重构 PRD-4：代表性 BuffXLogic 计划事件生产者与同 tick 写边界收口`

### 下一轮 PRD 的建议范围

- 继续收口剩余计划事件直写入口，优先覆盖代表性 `BuffXLogic` / `PolarizedAssaultEvent` 与其他仍会直接感知 `event_list` 的 producer，不再把已完成的 `UpdateAnomaly` / `AliceDotTriggerListener` 样本重复作为主目标。
- 在 `SkillEventHandler` 已迁到 runtime view 主读口的基础上，继续收口 `ScheduleBuffSettle()`、`update_anomaly()` 等同 tick 写边界，减少 legacy getter 继续同时承担读口与写边界双重职责。
- 如果本轮触达同 tick 写边界，只补最小 `runtime_command_port` / write facade，而不是继续把 raw `dynamic_buff` / `exist_buff_dict` 深透传给新代码。
- 保持 `Simulator` 仍做总流程编排，但不顺手扩大到 `UpdateAnomaly` 全量拆分、`Calculator` 全量迁移或 enemy debuff 单一事实源收口。

### 下一轮 PRD 的建议产物

- 额外一组或多组改经 dispatch gateway 的代表性 `BuffXLogic` / `PolarizedAssaultEvent` producer 样本。
- `SkillEventHandler` 同 tick 写边界的最小 `runtime_command_port` / write facade 样本，或等价的显式兼容写边界收口。
- 聚焦事件顺序、发布边界与同 tick 写语义的单元测试或 focused pytest。
- 按实际触达面同步扩大 `implicit-events` typecheck profile 的目标文件，避免 scoped gate 漏掉新 callsite。
- 继续复用现有真实验证入口，而不是再引入新的占位脚本名。

### 下一轮 PRD 的非目标

- 不做具体角色的大面积 XLogic 替换。
- 不在同一切片里同时重写 `ScheduledEvent` 全部 handler、`UpdateAnomaly` 全部逻辑和 `Calculator` 全量公式。
- 不删除旧 Buff 核心路径或旧容器字段，只允许先包出边界和适配层。
- 不把 `listener_manager.broadcast_event()`、计划事件队列和 runtime 立即写入口重新混成单一“事件总线”。
- 在 live simulator 真正消费 `config.buff_runtime.mode` 之前，不把 `--legacy-runtime` / `--candidate-runtime` 伪装成真实 runtime 开关。
- 不在没有真实 `main_loop` 一致性证据前提前下最终性能或完成结论。

## 已存在的真实验证入口

- `uv run python scripts/run_buff_main_loop_consistency.py --team <team> --stop-tick <n> --legacy-runtime <label> --candidate-runtime <label> --json`
  输出至少包含 `team`、`apl`、`stop_tick`、`total_damage`、`event_counts`、`buff_timeline` 与 `differences`；`--apl` 可选。
- `uv run python scripts/run_buff_runtime_benchmark.py --team <team> --stop-tick <n> --legacy-runtime <label> --candidate-runtime <label> --json`
  输出至少包含 `team`、`apl`、`stop_tick`、`total_runtime_ms`、`hotspots` 与 `comparisons`；`--apl` 可选。
- 两个命令里的 `--legacy-runtime` / `--candidate-runtime` 当前都只是报告标签；只有 live simulator 真正消费 `config.buff_runtime.mode` 后，它们才应承载真实 runtime 切换语义。

## 下一轮 PRD 的验证要求

- 必跑：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`
- 若触达生命周期容器或 runtime 写路径，追加：`uv run python scripts/run_buff_refactor_validation.py`
- 若触达 `Calculator` seam，追加：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`
- 若故事改动了验证命令契约、帮助文本或执行路径，补跑对应的 `--help` / focused pytest / 样例命令，而不是继续引用占位入口。

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
