# Buff重构下阶段计划草稿

## 当前状态

- 当前总路线已重置。
- 当前默认阶段仍为“基础设施解耦”。
- Buff 系统现已明确要求采用事件驱动架构。
- 阶段 1 当前实现基线已经落地：
  - `ScheduleDispatchPort` 已接入 `SchedulePreload`、`QuickAssistSystem`、`UpdateAnomaly`、`BattleEventListener` 中的 `AliceDotTriggerListener`、代表性 `AlicePolarizedAssaultTrigger -> PolarizedAssaultEvent` planned-event 链，以及已收口的 `ElegantVanitySpRecover`、`LunarNoviluna`、`MagneticStormCharlieSpRecover`、`SeedAdditionalAbilityTrigger`、`SliceofTimeExtraResources`、`CannonRotor`、`YanagiPolarityDisorderTrigger`、`HugoCorePassiveTotalizeTrigger`、`DecibelManager`、`MiyabiCoreSkill_IceFire`、`YixuanCinema1Trigger`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger`、`Character/Yuzuha` cinema-6 energy 分支与 `EnemyUniqueMechanic/BreakingLegManager` part-break refresh。
  - `BuffRuntimeReadPort` / `EventContext.buff_runtime_view` 已接入 `ScheduledEvent`，`anomaly`、`abloom`、`disorder`、`polarity_disorder` 与高风险 `SkillEventHandler` 主读路径已改用 runtime view。
  - `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 已接入 `ScheduledEvent` / `EventContext`；`SkillEventHandler` 的 `ScheduleBuffSettle()`、`update_anomaly()` 等同 tick 写边界已改走显式命令口，同时仍通过 adapter 保留 legacy 容器身份。
  - `implicit-events` 共享验证入口现已同时覆盖 `test_schedule_dispatch.py`、上述 focused dispatch/runtime-boundary pytest，以及这些回归文件本身的 scoped mypy，不再只类型检查它们所命中的生产代码。
  - `scripts/run_buff_main_loop_consistency.py` 与 `scripts/run_buff_runtime_benchmark.py` 已是仓库内真实命令入口，不再是占位脚本。
  - `--legacy-runtime` / `--candidate-runtime` 仍只是报告标签；live simulator 还未消费 `config.buff_runtime.mode`。
  - 2026-06-07 `US-005` 复扫 `BuffXLogic`、`Character`、`BattleEventListener`、`EnemyUniqueMechanic` 与 `DecibelManager` 后，未发现新的 producer-level `schedule_data.event_list.append(...)` / `JudgeTools.find_event_list()` planned-event writer；`BattleEventListener` 目录明确没有新的 raw queue backlog，`AliceDotTriggerListener` 的 `dynamic_dot_list.append(dot)` 仍是 dot runtime registration。
- 下一轮 Ralph PRD 仍应留在阶段 1，继续围绕真实剩余边界推进：先补 shared validation / handoff 与旧兼容发现口清理证据，再在发现具体 producer-level planned-event writer 时收口；不要从注释、本地 list 或 `change_process_state()` 推断新迁移目标。
- 下一轮路线仍然严格遵循 [Buff重构方案.md](./Buff重构方案.md) 中的阶段顺序，不回退到角色驱动式切片。

## 本文档的用途

- 记录“当前 PRD 完成后，下一阶段准备调查什么”。
- 为下一轮 `scripts/ralph/prd.json` 提供调查清单和切片边界。
- 避免 PRD 方向重新漂移回“看到一个 XLogic 就改一个”的模式。

## 当前默认下一轮实现型 PRD 草稿

### 下一轮 PRD 名称建议

`Buff 重构 PRD-7：剩余 Character helper 与 hidden listener 发布入口审计`

### 下一轮 PRD 的建议范围

- `Character/Yixuan/AdrenalineManagerClass.py` 已确认是本地 `BaseAdrenalineEvent` 事件组，`EnemyUniqueMechanic/BreakingLegManager.py` part-break `ScheduleRefreshData` 已改经 `ScheduleDispatchPort`；复扫未在 `BuffXLogic`、`Character`、`BattleEventListener`、`EnemyUniqueMechanic` 或 `DecibelManager` 发现新的具体 one-off raw scheduler writer。不再重开已闭合的 `MiyabiCoreSkill_IceFire`、`YixuanCinema1Trigger`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger`、`Character/Yuzuha` cinema-6 energy 分支及前序 xstart/xhit refresh、`CannonRotor`、`Yanagi`、`Hugo`、`DecibelManager`、`BreakingLegManager` 批次。
- 当前源码扫描未在 `BattleEventListener` 目录发现直接 `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` planned-event 写入；`AliceDotTriggerListener` 的 dot runtime registration 不应继续被写成 listener raw queue backlog。
- 真实剩余 backlog 是 `US-006` 把 `Yixuan` / `BreakingLegManager` focused regressions 纳入 shared `implicit-events` gate、`US-007` 同步 handoff，以及后续在所有 producer 迁移稳定后收口 `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` 旧兼容发现口；当前没有可立即迁移的新 producer payload。
- 仅在发现其他具体 handler / helper 仍通过 legacy getter 承担 same-tick 写协作时，继续扩展 `RuntimeCommandPort` / write facade，减少读口与写边界双重职责继续泄露。
- 如果本轮触达同 tick 写边界，沿用现有 `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 模式，而不是继续把 raw `dynamic_buff` / `exist_buff_dict` 深透传给新代码。
- 除非 focused validation 暴露回归，否则不要重新打开已经闭合的 `SkillEventHandler` 代表性读写分层样本，也不要把已经收口的 xstart/xhit refresh、`CannonRotor`、`Yanagi`、`Hugo` 或 `DecibelManager` 批次重新当成主故事。
- 保持 `Simulator` 仍做总流程编排，但不顺手扩大到 `UpdateAnomaly` 全量拆分、`Calculator` 全量迁移或 enemy debuff 单一事实源收口。

### 下一轮 PRD 的建议产物

- 只有在新扫描发现具体 producer-level planned-event writer 时，才新增 dispatch gateway 迁移样本，并先记录文件、函数、事件类型、payload 与相对顺序。
- 如有需要，再补一组沿用 `RuntimeCommandPort` 的相邻 handler / helper same-tick 写边界样本，而不是重新发明新的写门面。
- 聚焦事件顺序、发布边界与同 tick 写语义的单元测试或 focused pytest。
- 按实际触达面同步扩大 `implicit-events` typecheck profile 的目标文件，并把新增 focused 回归文件本身纳入 scoped mypy，避免 gate 只类型检查生产模块。
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
- 上述验证命令应串行执行，不要并发跑多个 profile；它们会共享 sqlite `sessions` 数据与异步日志写线程，并发时容易制造假失败。

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
