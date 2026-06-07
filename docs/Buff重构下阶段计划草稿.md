# Buff重构下阶段计划草稿

## 当前状态

- 当前总路线已重置。
- 当前默认阶段仍为“基础设施解耦”。
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
- 下一轮路线仍然严格遵循 [Buff重构方案.md](./Buff重构方案.md) 中的阶段顺序，不回退到角色驱动式切片，也不提前进入 XLogic 全量分析。

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

## 当前默认下一轮实现型 PRD 草稿

### 下一轮 PRD 名称建议

`Buff 重构 PRD-12：ScheduledEvent 对 Buff runtime facade 的依赖收口`

### 下一轮 PRD 的建议范围

- 默认从下方“PRD-11 完成后的阶段 1 候选池”中的候选块 B 取材：`zsim/sim_progress/ScheduledEvent/__init__.py`、`event_handlers/context.py`、`event_handlers/base.py`、handler 目录、`buff_runtime.py`、`runtime_command.py` 与对应 focused tests。
- Ralph-sized 工作应收窄 `ScheduledEvent` / `EventContext` 中 raw `dynamic_buff`、`exist_buff_dict`、`loading_buff` 的暴露面，让新 handler 默认依赖 `BuffRuntimeReadPort` / `RuntimeCommandPort` / 必要 gateway，而不是新增 raw container passthrough。
- 本轮不是 handler 全量重写、旧容器删除或 runtime mode 切换 PRD；必须保留 handler requeue、LoadDamageEvent damage-effect continuation、`ScheduleDispatchPort` queue semantics、`RuntimeCommandPort` same-tick 写边界与 `BuffRuntimeReadPort` 只读语义。
- 若 PRD 生成器改选候选块 C/D/E，也应选择一个完整阶段 1 耦合块并写清候选文件、边界、focused tests 与验证入口；不要只围绕已删除的 `event_list` 发现口或已完成的 PRD-11 facade 主体继续生成薄 PRD。
- `JudgeTools.find_event_list()`、`check_preparation(..., event_list=...)` 与 `BuffRecordBaseClass.event_list` 已在 PRD-10 删除 / 关闭；仅当 post-deletion guardrail 给出新的生产文件、函数、旧写表达式、payload、target 或 blocker 证据时，才重新处理这些 surface。
- `--legacy-runtime` / `--candidate-runtime` 当前仍只是 consistency / benchmark 报告标签；live simulator 还没有消费 `config.buff_runtime.mode`。

### 下一轮 PRD 的建议产物

- `ScheduledEvent` / `EventContext` retained raw container 清单，明确哪些 getter / fields 是 compatibility-only，哪些 handler 已经能只依赖 runtime view / command port。
- 一个可验证的 handler/context 收口样本或 guardrail，证明新 handler 不再直接取 raw `dynamic_buff` / `exist_buff_dict`；如果必须保留 legacy getter，应写入 narrow allowlist 与下一步删除条件。
- 如扫描发现新的相邻 handler / helper same-tick 写边界样本，沿用 `RuntimeCommandPort` 处理；不要重新发明新的写门面，也不要从已闭合的 `SkillEventHandler` / `AnomalyEventHandler` 文本重复开故事。
- 如果只新增 guardrail 或 audit 而不替换 live path，必须在 replacement notes 中明确“只建立边界 / 守门，没有替换 live runtime path”。
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

## PRD-11 完成后的阶段 1 候选池

旧容器 facade 主体扩展完成后，默认不要继续围绕已完成的主循环 facade 样本重复开小 PRD；除非 guardrail 暴露新证据，否则下一轮应从以下阶段 1 候选块中选一个连贯块生成更完整的 Ralph backlog。

### 候选块 A：旧容器隔离与 Buff runtime facade 扩展（PRD-11 已完成主体）

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
  - 不再把“再迁一个 main-loop callsite”当默认下一步；默认转向候选块 B 的 `ScheduledEvent` / `EventContext` 收口。
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
  - 代表性 `SkillEventHandler` / `AnomalyEventHandler` 主路径已改走 runtime view / command port，但 `ScheduledEvent` 仍在构造和上下文层知道旧 `dynamic_buff`、`exist_buff_dict`、`loading_buff`。
  - handler 层仍需要复扫是否存在新的 legacy getter 读写协作样本，但不能从已闭合文本重复开故事。
- 可拆工作方向：
  - 收窄 `EventContext` 中 legacy getter 的使用范围，要求新 handler 默认通过 runtime view / command port。
  - 为剩余 handler 建立 focused audit / guardrail，分类 retained requeue、damage-effect continuation、runtime read、same-tick write。
  - 把 handler 的 no-raw-runtime 约束纳入 `implicit-events` scoped mypy / pytest。
  - 只在发现具体同 tick 写协作时，沿用 `RuntimeCommandPort` 迁移；不要新增第二套 facade。
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
  - `Update_Buff` 直接遍历旧动态 Buff 容器，直接移除过期 Buff，并同步 enemy debuff 镜像。
  - `buff.end(...)` 与 `DYNAMIC_BUFF_DICT[charname].remove(buff)` 的顺序和副作用仍靠旧函数内部约定。
- 可拆工作方向：
  - 先抽出最小 settle / expire adapter，锁定 `end -> remove -> enemy debuff mirror` 的顺序。
  - 用 focused tests 覆盖过期、未过期、enemy debuff、普通角色 Buff 四类行为。
  - 让主循环调用边界更接近 runtime facade，而不是直接传三个旧容器。
  - 给新增路径加 no-new-raw-container guardrail。
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
  - `Calculator.MultiplierData` 仍直接聚合 enemy、dynamic buff 与 char。
  - 多个 XLogic 直接构造 `MultiplierData(...)` 或别名 `Mul(...)`，这类路径是属性读取 seam，不应误判为 planned-event producer。
- 可拆工作方向：
  - 先生成最新 `MultiplierData` / `Mul` 使用清单，按“只读属性”“读取后写回 record / buff”“同时触发事件”分类。
  - 建立最小 stat reader / attribute reader 接口草案，并选代表性只读 XLogic 做迁移样本。
  - focused tests 断言迁移后不再直接依赖 raw `dynamic_buff_list`，但保持公式输入字段一致。
  - 将 `calculator-reads` profile 的真实目标文件和测试文件补齐，避免只写文档不进 gate。
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
  - `UpdateAnomaly` 已完成部分 planned-event dispatch 改造，但仍与异常状态、dot、Buff runtime 容器和 enemy debuff 镜像强耦合。
  - `UpdateAnomaly.update_anomaly()` 当前的 scheduled queue publish 已走 `ScheduleDispatchPort`，`spawn_output()` 的 `listener_manager.broadcast_event(...)` 仍是同步 listener broadcast，二者不得合并。
  - `anomaly_effect_active()` 仍通过 `buff_add_strategy(...)` 写入异常附带 debuff，并直接维护 `enemy.dynamic.dynamic_dot_list` 完成 dot runtime registration。
  - `AnomalyBar.change_info_cause_active()` / `__get_max_duration()` 从 `dynamic_buff_dict["enemy"]` 读取影响异常持续时间的 Buff，是当前默认只读迁移样本。
  - `Shock.DotFeature.__post_init__()` 从 `sim_instance.load_data.exist_buff_dict["丽娜"]` 读取丽娜组队被动以决定感电持续时间，属于后续 dot 初始化 read-only 旁路。
  - `CalAnomaly.__init__()` 的 `MulData(...)` 仍是 anomaly / disorder 公式内部，不作为本块第一迁移样本。
  - `BuffAddStrategy` 仍是外部强制写入旧 Buff 运行态的公共入口；US-019 已把 active store replacement 与 enemy debuff mirror sync 迁到按需创建的 `LegacyBuffRuntimeFacade`，但受益人选择、模板 Buff 复制、`simple_start()` 模板回写和私有诊断 helper 仍保留旧 registry / container 兼容边界。
- 可拆工作方向：
  - US-017 已完成旁路读取 / 写入分类；后续故事应直接消费该清单，不把 dot runtime registration 当 planned-event writer，也不重开已迁到 `ScheduleDispatchPort` 的 `UpdateAnomaly` queue publish。
  - 默认下一只读样本：将 `AnomalyBar.__get_max_duration()` 通过 `BuffRuntimeReadPort`、attribute reader 或等价显式读口接入，同时保持持续时间公式、enemy 状态和异常输出不变。
  - 后续 dot 初始化样本可考虑 `Shock.DotFeature.__post_init__()`，但必须先证明 `sim_instance` 校验和 `max_duration` 结果完全兼容。
  - US-019 已完成默认写边界调查目标：`BuffAddStrategy.buff_add_strategy()` / `let_buff_start()` 当前分类为 no pending queue write、active store facade-backed same-tick write、enemy mirror facade-backed sync、registry/template retained compatibility、inactive diagnostic helper retained。后续不要再把该入口作为 raw `event_list` producer 迁移。
  - 补 focused tests 区分 scheduled event、listener broadcast、dot runtime registration、runtime immediate write 四层语义，并纳入 `BuffAddStrategy` facade-backed 强制写入样本。
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
