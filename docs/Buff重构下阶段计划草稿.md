# Buff重构下阶段计划草稿

## 当前状态

- 当前总路线已重置。
- 当前默认阶段已进入“XLogic 全量分析与复用收敛”的 PRD 准备；阶段 1 基础设施解耦已由 `PRD-12 US-024` 关闭。
- Buff 系统现已明确要求采用事件驱动架构。
- 阶段 1 当前实现基线已经落地：
  - `ScheduleDispatchPort` 已接入 `SchedulePreload`、`QuickAssistSystem`、`UpdateAnomaly`、`BattleEventListener` 中的 `AliceDotTriggerListener`、代表性 `AlicePolarizedAssaultTrigger -> PolarizedAssaultEvent` planned-event 链，以及已收口的 `ElegantVanitySpRecover`、`LunarNoviluna`、`MagneticStormCharlieSpRecover`、`SeedAdditionalAbilityTrigger`、`SliceofTimeExtraResources`、`CannonRotor`、`YanagiPolarityDisorderTrigger`、`HugoCorePassiveTotalizeTrigger`、`DecibelManager`、`MiyabiCoreSkill_IceFire`、`YixuanCinema1Trigger`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger`、`Character/Yuzuha` cinema-6 energy 分支与 `EnemyUniqueMechanic/BreakingLegManager` part-break refresh。
  - `BuffRuntimeReadPort` / `EventContext.buff_runtime_view` 已接入 `ScheduledEvent`，`anomaly`、`abloom`、`disorder`、`polarity_disorder` 与高风险 `SkillEventHandler` 主读路径已改用 runtime view。
  - `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 已接入 `ScheduledEvent` / `EventContext`；`SkillEventHandler` 的 `ScheduleBuffSettle()`、`update_anomaly()` 以及 `AnomalyEventHandler` 的 `ScheduleBuffSettle(..., anomaly_bar=event)` 同 tick 写边界已改走显式命令口，同时仍通过 adapter 保留 legacy 容器身份。
  - `implicit-events` 共享验证入口现已同时覆盖 `test_schedule_dispatch.py`、上述 focused dispatch/runtime-boundary pytest，以及这些回归文件本身的 scoped mypy，不再只类型检查它们所命中的生产代码。
  - `scripts/run_buff_main_loop_consistency.py` 与 `scripts/run_buff_runtime_benchmark.py` 已是仓库内真实命令入口，不再是占位脚本。
  - `--legacy-runtime` / `--candidate-runtime` 仍只是报告标签；live simulator 还未消费 `config.buff_runtime.mode`。
  - 2026-06-07 `PRD-8 US-001` 复扫 raw queue 与旧发现口后，`JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` 只剩 legacy discovery / compatibility cache 证据，`data_struct/schedule_dispatch.py` 只保留 adapter 取队列点，`ScheduledEvent` handler 的 `.event_list.append(...)` 仍是 not-yet-executable requeue；未在 `BuffXLogic`、`Character`、`BattleEventListener`、`EnemyUniqueMechanic` 或 `DecibelManager` 发现新的 producer-level planned-event writer。
  - 2026-06-07 `PRD-8 US-002` / `US-006` 已把 `tests/simulator/test_legacy_event_list_discovery_guardrail.py` 纳入 `implicit-events` shared pytest 与 scoped mypy；新增生产 `find_event_list` 调用、`BuffRecordBaseClass.event_list` / `record.event_list` 访问都必须通过 AST guardrail 或显式 allowlist 说明。
  - 2026-06-07 `PRD-8 US-003` 用 focused pytest 锁定 `check_preparation(..., event_list=True)` 只缓存 `record.event_list = find_event_list(...)`，并用 AST / 结构化配置扫描确认 `BuffXLogic`、`zsim/config*.json` 与 `zsim/data` CSV / JSON / TOML 当前没有显式 `event_list=True` 生产入口；没有新的 producer-level planned-event writer 可迁移。
  - 2026-06-07 `PRD-8 US-005` 已把 `LoadDamageEvent` Load-stage spawn / damage-effect continuation、`ScheduledEvent` handler requeue、`Character/Yixuan` 本地 `BaseAdrenalineEvent` 事件组与 `AliceDotTriggerListener` dot runtime registration 写入 retained-boundary 清单；这些路径后续只能由各自的 dispatcher / handler / runtime-state PRD 处理，不应被重新当成 Buff producer raw queue backlog。
  - 2026-06-07 `PRD-9 US-006` 已把 `AnomalyEventHandler.handle()` 中通过 legacy getter 直调 `ScheduleBuffSettle(..., anomaly_bar=event)` 的 same-tick 写协作收口到 `RuntimeCommandPort.settle_buffs(...)`，focused pytest 已阻断 handler 再访问 legacy getter。
- 2026-06-07 `PRD-10` 已执行旧兼容发现口删除 / 显式关闭：`JudgeTools.find_event_list()` 已删除并移除公共导出，`check_preparation(..., event_list=...)` 已按 key presence 拒绝旧关键字，`BuffRecordBaseClass.event_list` 初始化字段已删除；post-deletion guardrail 现在对这些 deleted surfaces 执行 absence / blocker 守门。
- PRD-10 没有保留删除 blocker 或生产 fallback，也没有发现新的 producer-level planned-event writer 或新的 handler/helper same-tick legacy getter 加写入协作；`data_struct/schedule_dispatch.py` adapter queue access 仍是 `ScheduleDispatchPort` 兼容语义下唯一允许的底层队列触点。
- 2026-06-07 `PRD-11` 已完成旧容器隔离与 Buff runtime facade 扩展主体：`LegacyBuffRuntimeFacade` 以引用方式包住 `exist_buff_dict`、`LOADING_BUFF_DICT`、`DYNAMIC_BUFF_DICT` 与 `enemy.dynamic.dynamic_debuff_list`；`Simulator.main_loop()` 的 tick sweep / pending activation 和 live `Update_Buff` active removal 已走 facade，no-new-raw-container guardrail 与主循环一致性样本已通过。
- PRD-11 没有删除旧容器，也没有把 `BuffRuntimeReadPort` 扩成写口；`RuntimeCommandPort` 仍是 scheduled handlers 的 same-tick 写边界，`--legacy-runtime` / `--candidate-runtime` 仍只是报告标签。
- PRD-11 收口后，下一轮 Ralph PRD 仍应留在阶段 1，默认入口从旧容器 facade 主体扩展转向“`ScheduledEvent` 对 Buff runtime facade 的依赖收口”；除非 guardrail 暴露新的具体证据，不再围绕 `find_event_list` / `record.event_list` / `event_list=True` 或已完成的 facade 主体重复开薄切片。
- 2026-06-07 `PRD-12 US-024` 已完成阶段 1 closure decision：候选块 B/C/D/E 均已有 audit、代表性实现或 guardrail / validation evidence，`implicit-events`、`calculator-reads` 与默认 lifecycle validation profile 在 US-024 串行复跑通过，未输出 phase-1 blocker package。
- PRD-12 closure 不删除旧容器，也不把 sample CLI label 当 live runtime switch；`exist_buff_dict`、`DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT`、legacy `buff_add()`、legacy `KickOutBuff()`、Calculator / CalAnomaly 公式快照、handler requeue、damage continuation、dot runtime registration 与 listener broadcast 都仍按各自 retained boundary 保留。
- 2026-06-08 gap-closure blocker PRD 已把 `docs/查漏补缺.md` 中的 `ScheduleBuffSettle.py` guardrail / validation 覆盖缺口收敛为 retained-boundary 守门：`ScheduleBuffSettle.py` 进入 raw old-container guardrail 扫描和 `lifecycle` / `implicit-events` scoped mypy targets，分类为 `legacy ScheduleBuffSettle command-adapter internals`。这不是 live runtime path 替换，也不重开已闭合 producer batch。
- 2026-06-08 gap-closure blocker PRD 已完整关闭：root-workspace source scan 排除 `.codex_worktrees/` 后未发现新的 production-level raw `event_list` producer，也未发现 handler/helper 直接调用 `ScheduleBuffSettle(...)`；CodeGraph 命中的 `.codex_worktrees/` direct caller 仅作为历史快照证据处理。`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`ScheduleDispatchPort`、`BuffRuntimeReadPort` 与 `LegacyBuffRuntimeFacade` retained boundaries 保持 intact。
- 本 blocker PRD 已完整关闭，默认路线返回阶段 2；只有新的 guardrail / validation / root-workspace source scan 证据暴露 phase-1 production blocker 时，才回到阶段 1 窄修复。
- 阶段 1 / 阶段 2 的源码复扫必须把 `.codex_worktrees/` 视为本地历史 worktree 快照并默认排除；除非明确审计归档分支，不能把其中的 CodeGraph / `rg` 命中当作当前生产 blocker。最终 blocker 结论必须回到根工作区源码、focused tests 和 validation profiles。
- 当前默认下一 Ralph PRD 应进入阶段 2：XLogic 全量分析与复用收敛。阶段 2 的第一轮只做分类、复用清单与风险矩阵，不直接进入阶段 3 的具体替换。
- 下一轮路线仍然严格遵循 [Buff重构方案.md](./Buff重构方案.md) 中的阶段顺序，不回退到角色驱动式切片，也不把阶段 2 的分类工作直接升级成单个 XLogic 替换故事。

## 本文档的用途

- 记录“当前 PRD 完成后，下一阶段准备调查什么”。
- 为下一轮 `scripts/ralph/prd.json` 提供调查清单和切片边界。
- 避免 PRD 方向重新漂移回“看到一个 XLogic 就改一个”的模式。

## PRD 取材原则

- 本文档不强制规定 PRD 的固定 story 结构；`prd` skill 和 `ralph` skill 可以继续按它们自己的格式生成 Markdown PRD 与 `scripts/ralph/prd.json`。
- 本文档必须给 PRD 生成器提供足够大的候选池，而不是只描述一个最小安全下一步。每次更新“当前默认下一步”时，都要同时保留后续同阶段候选块，避免自动循环在完成一个窄切片后只能继续生成很薄的 PRD。
- 每个候选块都应写清：候选文件 / 符号、当前已知耦合、可以拆出的 Ralph-sized 工作方向、必须保留的边界、验证入口和不应触碰的非目标。
- PRD 可以只选择其中一个连贯耦合块，但不应只因为找到第一个安全 callsite 就停止扩展；同一耦合块内具有相同风险面、相同验证入口、相同回滚方式的工作，应优先作为一组后续 story 候选提供给 PRD 生成器。
- 如果当前默认 PRD 只是删除收尾或 guardrail 收口，本文档仍要写出“该 PRD 完成后立即可进入的下一组阶段 1 候选块”。只有文档证据显示阶段 1 已无安全候选块时，才切到阶段 2 的 XLogic 全量分析。
- 后续 PRD 不需要为了填充数量发明迁移目标；但应该主动从 checklist 未完成项、旧耦合审查分组和现有测试缺口中提取可验证的实现候选，而不是只沿用上一轮最后一句“下一步”。

## 当前默认下一步

### 下一轮默认 Ralph PRD

`阶段 2：XLogic 全量分析与复用收敛`

### 阶段 2 第一轮建议范围

- 从 `zsim/sim_progress/Buff/BuffXLogic/` 做全量分类，不从单个最近迁移样本直接进入替换。
- 分类每个 XLogic 的主要耦合类型：属性读取、事件触发、count / record 写回、异常 / debuff / dot 旁路、`sim_instance` service-location、Calculator / CalAnomaly 公式快照、listener broadcast、scheduled publish、runtime immediate write。
- 对每类耦合给出可复用方法、记录对象、stat reader、event adapter、state sync 模式或 handler / listener 模式候选。
- 复核 `docs/旧Buff系统耦合审查结果.md`、`scripts/ralph/progress.txt` `## Codebase Patterns` 与现有 focused tests，确认哪些 phase-1 retained boundary 仍必须保留。
- 产出 XLogic 优先级和风险矩阵，但不在第一轮直接批量替换 XLogic。

### 阶段 2 第一轮建议产物

- XLogic 全量分类表。
- 可复用方法 / record / stat reader / event adapter / state sync 模式清单。
- 高风险耦合桶与回归风险点。
- 下一轮阶段 2 PRD 的候选池：可以按同一耦合类型、同一验证入口、同一回滚方式分组，而不是按最近发现的单个角色文件拆薄切片。
- validation 计划：至少保留 `implicit-events` 和 `calculator-reads` 作为相关耦合块的守门入口；触达 lifecycle/runtime 写路径时继续追加默认 lifecycle profile。

### 阶段 2 第一轮非目标

- 不删除旧容器，不删除 legacy `buff_add()` / `KickOutBuff()`，不删除 Calculator / CalAnomaly `MultiplierData` 公式快照。
- 不把 `--legacy-runtime` / `--candidate-runtime` 当 live runtime switch。
- 不把 listener broadcast、scheduled queue publish、dot runtime registration、runtime immediate write 合并成单一总线。
- 不重开已删除 `event_list` surface 或已闭合的 producer batch，除非 guardrail / validation 给出新的生产证据。
- 不直接进入阶段 3 的 XLogic 替换；第一轮阶段 2 先做分类与复用收敛。

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

## PRD-12 US-024 后的阶段 1 blocker 候选池状态

PRD-12 已按候选块 B/C/D/E 完成阶段 1 基础设施收口样本、guardrail 与 validation evidence，并由 `US-024` 在 serial validation 通过后声明阶段 1 closed。以下候选池不再作为默认同阶段实现 backlog，只保留给 blocker 定位：只有 guardrail、source scan 或 validation 给出新的生产证据时，才从相应块生成修复 PRD。

### 候选块 A：旧容器隔离与 Buff runtime facade 扩展（PRD-11 已完成主体，PRD-12 复核保留）

- 候选文件 / 符号：
  - `zsim/simulator/dataclasses.py`
  - `zsim/simulator/simulator_class.py`
  - `zsim/sim_progress/Buff/Buff0Manager/Buff0ManagerClass.py`
  - `zsim/sim_progress/Buff/BuffLoad.py`
  - `zsim/sim_progress/Buff/BuffAdd.py`
  - `zsim/sim_progress/Update/Update_Buff.py`
  - `zsim/sim_progress/ScheduledEvent/buff_runtime.py`
  - `tests/simulator/test_buff_runtime_view.py`
  - `tests/simulator/test_runtime_command_port.py`
- 当前耦合：
  - PRD-11 已完成主体：`LegacyBuffRuntimeFacade` 包住 registry/template read、pending queue、active store、enemy debuff mirror sync；`Simulator.main_loop()` 的 tick sweep / pending activation 和 live `Update_Buff` active removal 已走 facade。
  - 旧容器对象身份仍保留；`BuffLoadLoop()` trigger judgement / pending queue population、`ScheduledEvent(...)` 构造 raw active/exist 参数、legacy `buff_add()` 与 legacy `KickOutBuff()` 仍是 retained compatibility boundary。
- 可拆工作方向：
  - 后续只在 guardrail 发现新增 raw-container passthrough，或需要补齐 `BuffLoadLoop()` pending population 的更窄 facade 入口时，才回到本候选块。
  - 不再把“再迁一个 main-loop callsite”当默认下一步；阶段 2 默认只做 XLogic 全量分类，除非 guardrail 给出新的 phase-1 blocker 证据。
- 必须保留：
  - 旧容器对象身份和现有 main loop 行为。
  - `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 作为 same-tick 写边界。
  - 已有 `BuffRuntimeReadPort` 的只读语义，不把它扩成任意写口。
- 验证入口：
  - `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`
  - 触达 main loop / lifecycle 写路径时追加 `uv run python scripts/run_buff_refactor_validation.py`
  - 视改动补充 `tests/simulator/test_buff_runtime_view.py`、`tests/simulator/test_runtime_command_port.py` 或新的 focused pytest。
- 非目标：
  - 不删除旧容器，不把 `--legacy-runtime` / `--candidate-runtime` 当 live switch，不重写 `BuffLoadLoop()` 判定或 `Calculator` 公式。

### 候选块 B：`ScheduledEvent` 对 Buff runtime facade 的依赖收口

- 候选文件 / 符号：
  - `zsim/sim_progress/ScheduledEvent/__init__.py`
  - `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`
  - `zsim/sim_progress/ScheduledEvent/event_handlers/base.py`
  - `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/*.py`
  - `zsim/sim_progress/ScheduledEvent/buff_runtime.py`
  - `zsim/sim_progress/ScheduledEvent/runtime_command.py`
  - `tests/simulator/test_skill_handler_runtime_view.py`
  - `tests/simulator/test_anomaly_handler_runtime_view.py`
- 当前耦合：
  - PRD-12 已完成 raw runtime exposure audit、compatibility getter narrowing、same-tick helper classification / routing、construction centralization 与 no-new-raw-runtime guardrail。
  - `ScheduledEvent` 构造层仍保留 raw `dynamic_buff`、`exist_buff_dict`、`loading_buff` compatibility boundary；这是 retained boundary，不是 phase-1 blocker。
- 可拆工作方向：
  - 当前只保留 blocker-driven follow-up：如果 guardrail 发现新的 handler legacy getter 调用、raw runtime passthrough 或 same-tick 写协作，再按文件 / 符号开窄故事。
  - 不从已闭合的 `SkillEventHandler` / `AnomalyEventHandler` 文本重复开迁移故事。
- 必须保留：
  - handler requeue 的 `.event_list.append(...)` 语义。
  - `LoadDamageEvent` damage-effect continuation。
  - `ScheduleDispatchPort` 与 listener broadcast 的分层边界。
- 验证入口：
  - `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`
  - 触达 handler 行为时补对应 focused pytest，断言不访问 legacy getter 或只访问明确 allowlist。
- 非目标：
  - 不重写全部 handler，不改变 handler requeue / DamageEvent continuation / ScheduleDispatchPort queue semantics，不新增第二套 write facade。

### 候选块 C：`Update_Buff` 生命周期结算边界

- 候选文件 / 符号：
  - `zsim/sim_progress/Update/Update_Buff.py`
  - `zsim/sim_progress/Buff/BuffAdd.py`
  - `zsim/sim_progress/Buff/buff_class.py`
  - `zsim/simulator/simulator_class.py`
  - `tests/simulator/` 下新增或扩展生命周期 focused tests。
- 当前耦合：
  - PRD-12 已完成 lifecycle audit，并把 live active removal 与 individual-settled stack cleanup 代表性分支收口到 `LegacyBuffRuntimeFacade`。
  - `KickOutBuff()`、no-facade fallback、anomaly expiration、dot expiration、non-expired / alltime reporting、complex `xexit()` 与 enemy debuff 单一事实源仍保留为 retained compatibility / non-target。
- 可拆工作方向：
  - 当前只保留 blocker-driven follow-up：如果 default lifecycle profile 或 raw-container guardrail 暴露新增 direct active-store / mirror 写入，再补窄 lifecycle adapter 或 allowlist 说明。
  - 不把 retained `KickOutBuff()` 删除当作 phase-1 默认工作。
- 必须保留：
  - `Buff.end(...)` 的旧行为和 count / state sync 副作用。
  - enemy debuff 镜像现状；本候选块不做单一事实源收口。
- 验证入口：
  - `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`
  - 若改主循环生命周期调用，追加全量 `uv run python scripts/run_buff_refactor_validation.py`。
- 非目标：
  - 不改 anomaly expiration、dot expiration、Calculator 公式或 enemy debuff 单一事实源；不删除 legacy `KickOutBuff()` 兼容入口。

### 候选块 D：Calculator 属性读取 seam

- 候选文件 / 符号：
  - `zsim/sim_progress/ScheduledEvent/Calculator.py`
  - 直接构造 `MultiplierData(...)` 或 `MultiplierData as Mul` 的 `zsim/sim_progress/Buff/BuffXLogic/*.py`
  - `tests/simulator/test_skill_handler_runtime_view.py`
  - `tests/simulator/test_vivian_core_passive_trigger_dispatch.py`
  - `tests/simulator/test_vivian_cinema6_trigger_dispatch.py`
- 当前耦合：
  - PRD-12 已完成 `MultiplierData(...)` / alias inventory、`BuffAttributeReader` seam、AM / AP 两个代表性只读 XLogic migration samples 与 `calculator-reads` guardrail/profile。
  - `MultiplierData` 仍保留给 Calculator / CalAnomaly 公式和 retained XLogic compatibility snapshot；这不是 phase-1 deletion blocker。
- 可拆工作方向：
  - phase 2 应先做 XLogic 全量分类与复用收敛，继续从 retained XLogic read inventory 中批量分类，而不是在 phase-1 closure 后立即替换单个角色文件。
  - 如果 `calculator-reads` guardrail 失败，按失败文件 / alias / raw read 表达式开 blocker 修复。
- 必须保留：
  - 公式和数值语义不在本候选块里重写。
  - 不把属性读取 seam 和 planned-event dispatch seam 混成一个事件总线。
- 验证入口：
  - `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`
  - 若同时触达 implicit event handler，则追加 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`。
- 非目标：
  - 不把属性读取 seam 伪装成 planned-event producer 迁移，不重写完整伤害公式或一次性删除 `MultiplierData`。

### 候选块 E：异常 / debuff / dot 旁路耦合

- 候选文件 / 符号：
  - `zsim/sim_progress/Update/UpdateAnomaly.py`
  - `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`
  - `zsim/sim_progress/Dot/Dots/Shock.py`
  - `zsim/sim_progress/Buff/BuffAddStrategy.py`
  - `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`
- 当前耦合：
  - PRD-12 已完成 anomaly / debuff / dot bypass audit、`AnomalyBar.__get_max_duration()` runtime-view read sample、`BuffAddStrategy` active-store / enemy-mirror facade write sample 与 bypass-layer semantics tests。
  - `UpdateAnomaly.update_anomaly()` scheduled queue publish 已走 `ScheduleDispatchPort`；`spawn_output()` listener broadcast、dot runtime registration、runtime immediate write 与 scheduled queue publish 仍是分离 retained layers。
  - `Shock.DotFeature.__post_init__()` 与 `CalAnomaly.__init__()` 仍是后续 read/formula classification 候选，不是 phase-1 closure blocker。
- 可拆工作方向：
  - 当前只保留 blocker-driven follow-up：如果 bypass semantics tests 或 raw-container guardrail 失败，再按 scheduled publish / listener broadcast / dot registration / runtime write 层分类修复。
  - phase 2 可继续分类 `Shock.DotFeature`、`CalAnomaly` 与更广的 anomaly / dot formula reads，但不得把 dot runtime registration 重新归为 planned-event queue backlog。
- 必须保留：
  - `listener_manager.broadcast_event()` 与 scheduled queue 的分层。
  - dot runtime registration。
  - enemy debuff 镜像现状，除非另开单独事实源收口 PRD。
- 验证入口：
  - `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`
  - 触达异常 / dot 计算结果时追加 main loop consistency 样例命令，至少覆盖一个相关 team / stop tick。
- 非目标：
  - 不把 dot runtime registration 当 planned-event backlog，不收口 enemy debuff 单一事实源，不把 listener broadcast、scheduled queue、runtime immediate write 混成单一总线。

## 下一轮 PRD 开始前必须先看的文件

- [Buff重构方案.md](./Buff重构方案.md)
- [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)
  重点先看 `6.6`、`6.7`、`6.8`、`6.9`
- [Buff系统重构Checklist.md](./Buff系统重构Checklist.md)
- `scripts/ralph/progress.txt`
  重点先看 `## Codebase Patterns`

## Phase 1 closed 后的下一轮调查提纲

`US-024` 已证据式声明“阶段一：基础设施解耦”关闭，下一轮 PRD 切到“XLogic 全量分析与复用收敛”，调查重点如下：

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
