# Buff系统重构Checklist

## 使用规则

- 本文档是 Buff 重构的总 checklist。
- 每个 `scripts/ralph/prd.json` 全部完成后，必须更新本文档。
- 更新时要同时标记“已完成项”“进行中项”“阻塞项”。
- 任何新增耦合块、验证要求、删除计划，都要先落本文档，再进入下一轮 PRD。

## 阶段 0：重规划与基线

- [x] 回到 `main` 分支重新规划。
- [x] 保留 `scripts/ralph` 和 `scripts/ralph/prompts`。
- [x] 重写总计划文档。
- [x] 建立旧 Buff 系统耦合审查结果文档。
- [x] 建立下阶段计划草稿文档。
- [x] 重置 Ralph loop 的 PRD 基线。

## 阶段 1：基础设施解耦

- [x] 完成阶段 1 的调查型 PRD，产出生命周期、事件模型、Calculator seam、验证入口与交接包。
- [x] 为 Buff runtime 建立抽象接口与适配层。
- [x] 为 `exist_buff_dict`、`DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT` 建立第一层 legacy-backed runtime facade 隔离边界；旧容器对象身份仍保留，本项不等同于容器删除。
- [ ] 建立事件驱动基础设施边界，明确事件对象、事件上下文、事件分发入口与订阅入口。
- [ ] 让 `Simulator` 不再直接控制旧 Buff 运行细节。
- [ ] 让 `ScheduledEvent` 改为依赖 Buff runtime facade。
- [ ] 让 `Update_Buff` 改为依赖 Buff runtime facade。
- [ ] 为 `Calculator` 建立属性读取接口，隔离 `MultiplierData` 直读。
- [ ] 为基础设施解耦新增单元测试。
- [ ] 为事件分发边界与事件顺序新增单元测试。
- [x] 为主循环一致性与性能验证补齐真实命令入口。
- [x] 为旧 `event_list` 发现口建立删除就绪清单、风险矩阵和 AST / 结构化数据 guardrail。
- [x] 执行旧 `event_list` 发现口删除 / 显式关闭：`JudgeTools.find_event_list()`、`check_preparation(..., event_list=...)` 缓存分支与 `BuffRecordBaseClass.event_list` 已关闭，并由 post-deletion guardrail 守门。

## 阶段 2：XLogic 全量分析与复用收敛

- [ ] 输出 XLogic 全量分类结果。
- [ ] 输出可复用方法清单。
- [ ] 输出可复用记录对象清单。
- [ ] 输出可复用 stat reader / event adapter / state sync 模式清单。
- [ ] 输出可复用事件类型 / 事件处理器 / 事件订阅模式清单。
- [ ] 明确 XLogic 替换优先级。
- [ ] 明确高风险耦合桶和回归风险点。

## 阶段 3：XLogic 全面替换

- [ ] 替换属性读取类 XLogic。
- [ ] 替换事件触发类 XLogic。
- [ ] 替换 count 写回类 XLogic。
- [ ] 替换异常附带 debuff 类 XLogic。
- [ ] 替换直接依赖 `sim_instance` 服务定位的 XLogic。
- [ ] 将旧触发链收口到统一事件驱动分发链路。
- [ ] 每个切片都有对应单元测试。
- [ ] 每个切片都有主循环一致性验证。

## 阶段 4：旧 Buff 残余删除

- [ ] 删除不再使用的旧 Buff 入口。
- [ ] 删除不再使用的旧适配器。
- [ ] 删除旧 `MultiplierData` 直连路径。
- [ ] 删除旧容器同步残余逻辑。
- [ ] 删除无用文档和无用兼容说明。

## 阶段 5：一致性与性能收口

- [ ] 新旧 Buff 系统 `main_loop` 结果一致。
- [ ] 对应角色配队 APL 结果一致。
- [ ] 关键 Buff 生效时序一致。
- [ ] 关键事件分发顺序一致。
- [ ] 异常 / debuff 关键结果一致。
- [ ] 总耗时优于旧系统。
- [ ] 事件分发热点性能优于旧系统。
- [ ] 输出最终验证结论。

## 每个 PRD 完成后的必做项

- [ ] 更新本 checklist 的状态。
- [ ] 更新 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)。
- [ ] 回写 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md) 中新增或已消解的耦合项。
- [ ] 记录本轮验证命令与结果。
- [ ] 确认下一轮 PRD 的调查范围和非目标。

## 本轮调查 PRD 收口状态（2026-06-05）

- [x] 更新本 checklist 的状态。
- [x] 更新 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)。
- [x] 回写 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md) 中新增或已消解的耦合项，并补入验证入口与交接要求。
- [x] 记录本轮验证命令与结果。
- [x] 确认下一轮 PRD 的实现范围和非目标。

## 本轮阶段 1 实现基线 PRD 收口状态（2026-06-05）

- [x] `ScheduleDispatchPort` 已落地，`SchedulePreload` 与 `QuickAssistSystem` 已改经 dispatch gateway。
- [x] `BuffRuntimeReadPort` / `EventContext.buff_runtime_view` 已落地，`anomaly`、`abloom`、`disorder`、`polarity_disorder` 已改走 runtime view。
- [x] `scripts/run_buff_main_loop_consistency.py` 与 `scripts/run_buff_runtime_benchmark.py` 已提供真实 CLI 入口与稳定输出字段约定。
- [x] 更新 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)、[Buff重构替换说明.md](./Buff重构替换说明.md) 与 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)，同步阶段 1 当前基线。
- [x] `UpdateAnomaly` 计划事件发布路径与 `BattleEventListener` 中 `AliceDotTriggerListener` 样本已改经 dispatch gateway，当前不再把这两条入口列为阶段 1 主缺口。
- [x] 高风险 `SkillEventHandler` 已把 `Calculator` / `update_anomaly()` 的主 Buff 读口迁到 runtime view。
- [ ] 其余 `BuffXLogic` / `Character` 旁路计划事件生产者、可能隐藏在 listener helper 中的发布入口，以及其他相邻同 tick runtime 写路径仍待后续阶段 1 切片推进。

## 本轮剩余 producer batch / shared-validation PRD 收口状态（2026-06-06）

- [x] 代表性 `AlicePolarizedAssaultTrigger -> PolarizedAssaultEvent` 计划事件链，以及本轮收口的 `ElegantVanitySpRecover`、`LunarNoviluna`、`MagneticStormCharlieSpRecover`、`SeedAdditionalAbilityTrigger`、`SliceofTimeExtraResources`、`CannonRotor`、`YanagiPolarityDisorderTrigger`、`HugoCorePassiveTotalizeTrigger` 与 `DecibelManager`，现都已改经 `ScheduleDispatchPort` 发布 planned event。
- [x] `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 仍是本轮唯一沿用的 same-tick 显式写边界；`SkillEventHandler` 的 `update_anomaly()` / `ScheduleBuffSettle()` 与 `AnomalyEventHandler` 的 `ScheduleBuffSettle(..., anomaly_bar=event)` 同 tick 写边界保持走显式命令口，没有引入第二套 write facade。
- [x] `implicit-events` 共享验证入口现已同时覆盖 `test_schedule_dispatch.py`、聚焦 dispatch/runtime-boundary pytest，以及这些 focused 回归文件本身的 scoped mypy，handoff 文档已同步记录验证命令与当前基线。
- [ ] 阶段 1 剩余缺口已收敛为其他 one-off `BuffXLogic`、`Character` 旁路 producer 的 raw `event_list` 写入口、可能隐藏的 listener/helper 发布入口，以及后续若继续暴露出来的相邻高风险 same-tick 写路径。

## 本轮 remaining bypass producers runtime-boundary PRD 收口状态（2026-06-06）

- [x] `MiyabiCoreSkill_IceFire`、`YixuanCinema1Trigger`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger` 与 `Character/Yuzuha` cinema-6 energy 分支的 planned-event 直写入口已全部改经 `ScheduleDispatchPort`。
- [x] `implicit-events` 共享 gate 已覆盖这组 producer 的 focused no-raw-queue 回归、生产文件 mypy target 与测试文件 scoped mypy target；本轮验证命令为 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`。
- [x] 当前源码扫描未在 `BattleEventListener` 目录发现直接 `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` planned-event 写入；`AliceDotTriggerListener` 保留的是 dot runtime registration，不再把整个 listener 目录作为已知 raw queue backlog。
- [x] `Character/Yixuan/AdrenalineManagerClass.py` 已在 2026-06-07 审计为本地事件组 helper，`BreakingLegManager` hidden helper 已闭合到 `ScheduleDispatchPort`；后续不再把这两个入口列为未判断的 planned-event backlog。

## 本轮 Character helper hidden-listener audit PRD 收口状态（2026-06-07）

- [x] `Character/Yixuan/AdrenalineManagerClass.py` 已锁定为本地 `BaseAdrenalineEvent` 事件组 helper，不是 `schedule_data.event_list` scheduler queue writer。
- [x] `EnemyUniqueMechanic/BreakingLegManager` part-break `ScheduleRefreshData` 已改经 `ScheduleDispatchPort` 发布，并由 shared `implicit-events` 覆盖 focused regression 与 scoped mypy。
- [x] `LoadDamageEvent` 的 Load-stage event spawn / damage-effect continuation 与 `ScheduledEvent` handler not-yet-executable requeue 已保留为 core dispatcher / requeue 边界，没有改写队列语义。
- [x] 复扫后没有在 `BuffXLogic` / `Character` / `BattleEventListener` / `EnemyUniqueMechanic` / `DecibelManager` 发现新的具体 producer-level raw scheduler writer；`AliceDotTriggerListener` dot runtime registration 不列入 planned-event backlog。
- [x] `--legacy-runtime` / `--candidate-runtime` 继续只是报告标签，不是 live runtime switch；下一轮仍沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段 1 路线推进。

## 本轮 PRD-8 旧兼容发现口 / producer 守门收口状态（2026-06-07）

- [x] `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` 当前只承担 legacy discovery / compatibility cache：`FindMain.find_event_list(...)` 返回当前 `schedule_data.event_list`，`check_preparation(..., event_list=True)` 只缓存 `record.event_list`，不 append、不创建 planned-event payload。
- [x] `tests/simulator/test_legacy_event_list_discovery_guardrail.py` 与 `tests/simulator/test_check_preparation_event_list_compatibility.py` 已纳入 `implicit-events` shared pytest 与 scoped mypy，守门新增生产 `find_event_list` 调用、`record.event_list` 读写、配置 / BuffXLogic `event_list=True` 入口。
- [x] PRD-8 没有发现新的 producer-level planned-event writer；后续不得从注释、历史字符串、本地事件组、core Load/Schedule append、handler requeue 或 dot runtime registration 发明迁移故事。
- [x] 删除 `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` 前，必须先保持 guardrail 绿色，并确认没有生产 allowlist 外调用、没有 `record.event_list.append(...)` publisher、没有配置或 `BuffXLogic` 路径请求 `event_list=True`。
- [x] `--legacy-runtime` / `--candidate-runtime` 继续只是报告标签，不是 live runtime switch；下一轮仍沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段 1 路线推进，只有 phase-1 守门证据稳定后才进入 XLogic 全量分析。

## 本轮 PRD-9 旧兼容发现口删除前置 / same-tick 写边界收口状态（2026-06-07）

- [x] PRD-9 已完成 post-PRD-8 复扫、删除就绪清单与风险矩阵：`JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` 当前仍只承担 legacy discovery / compatibility cache，`data_struct/schedule_dispatch.py` adapter queue access 明确保留为 `ScheduleDispatchPort` 兼容语义，不是删除目标。
- [x] `tests/simulator/test_legacy_event_list_deletion_readiness.py` 已纳入 `implicit-events` shared pytest 与 scoped mypy，守门 allowlist 外 `find_event_list` 调用、`record.event_list` / `BuffRecordBaseClass.event_list` 读写、`record.event_list.append(...)` publisher、BuffXLogic / config / data `event_list=True` 入口。
- [x] PRD-9 没有发现新的 producer-level planned-event writer；`US-005` 已证据式关闭，后续只有在扫描给出文件、函数、事件类型、payload、target 和相对顺序证据时才新增 producer 迁移故事。
- [x] `AnomalyEventHandler.handle()` 原本通过 legacy dynamic/exist getter 直调 `ScheduleBuffSettle(..., anomaly_bar=event)`；本轮已收口到 `RuntimeCommandPort.settle_buffs(..., anomaly_bar=event)`。
- [x] `tests/simulator/test_anomaly_handler_runtime_view.py` 已阻断 handler 侧 legacy getter 访问，并断言 anomaly settle 写入走 `runtime_command_port`；`implicit-events` 验证通过。
- [x] 本轮没有新增 raw `dynamic_buff`、`exist_buff_dict`、`sub_exist_buff_dict` 或 `event_list` passthrough，也没有引入第二套 write facade。
- [x] `--legacy-runtime` / `--candidate-runtime` 继续只是 consistency / benchmark 报告标签，不是 live runtime switch。
- [x] PRD-9 最终交接已同步到 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)、[旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md) 与 [Buff重构替换说明.md](./Buff重构替换说明.md)：删除就绪状态为“guardrail 绿色后可尝试删除或显式关闭旧发现口”，剩余阻塞是继续证明没有 allowlist 外生产调用、没有 `record.event_list.append(...)` publisher、没有 BuffXLogic / config / data `event_list=True` 入口。
- [x] 下一轮默认入口仍属于阶段 1：优先执行旧兼容发现口删除 / 显式关闭；若删除条件不满足，继续 guardrail 与兼容 fallback；只有发现真实 producer-level planned-event writer 证据时才新增迁移故事。

## 本轮 PRD-10 旧兼容发现口删除执行 / guardrail 收口状态（2026-06-07）

- [x] `JudgeTools.find_event_list()` 已从 `FindMain.py` 删除，并从 `JudgeTools.__init__` 公共导出中移除；本轮没有保留生产 fallback，也没有新增 raw scheduler queue getter。
- [x] `check_preparation(..., event_list=...)` 旧缓存分支已删除，显式传入 `event_list` 关键字会按 key presence 被拒绝，不再通过 truthy / falsy 值静默缓存 `record.event_list`。
- [x] `BuffRecordBaseClass.event_list` 初始化字段已删除；guardrail 现在把任何新的 `record.event_list` 读写、`BuffRecordBaseClass.event_list` 访问或 `record.event_list.append(...)` publisher 视为删除后违规或需要显式 blocker 说明。
- [x] `data_struct/schedule_dispatch.py` 的 `ScheduleDispatchPort` adapter queue access 仍是唯一允许的底层 scheduler queue 接触面；core Load/Schedule append、handler requeue、本地事件组、dot runtime registration、base runtime compatibility helpers 与 `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 语义保留。
- [x] PRD-10 没有发现新的 producer-level planned-event writer，也没有发现新的 handler/helper same-tick legacy getter 加写入协作；本轮主要删除 / 关闭兼容发现面，没有替换 live simulator runtime path。
- [x] 本轮验证命令 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` 已通过：基础 simulator pytest、隔离队伍 pytest、48 个 focused `implicit-events` 回归与 68 个 scoped mypy target 均通过。
- [x] `--legacy-runtime` / `--candidate-runtime` 继续只是 consistency / benchmark 报告标签，不是 live runtime switch；下一轮仍沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段 1 路线推进。

## 本轮 PRD-11 旧容器 runtime facade 扩展收口状态（2026-06-07）

- [x] `zsim/sim_progress/ScheduledEvent/buff_runtime.py` 已新增 `BuffRuntimeFacade` / `LegacyBuffRuntimeFacade` / `create_legacy_buff_runtime_facade()`，按引用包住 `LoadData.exist_buff_dict`、`LoadData.LOADING_BUFF_DICT`、`GlobalStats.DYNAMIC_BUFF_DICT` 与 `enemy.dynamic.dynamic_debuff_list`，并区分 registry/template read、pending queue、active store、enemy debuff mirror sync 与 compatibility-only identity access。
- [x] `Simulator.main_loop()` 的 tick sweep 与 pending-to-active activation 已改经 `LegacyBuffRuntimeFacade.update_time_related_effects()` / `activate_pending_buffs()`；主循环不再为这两个边界直接拼接 `DYNAMIC_BUFF_DICT` / `exist_buff_dict` / `LOADING_BUFF_DICT` / `enemy` 参数。
- [x] `Update_Buff.update_buff(..., runtime_facade=...)` 在 live facade tick sweep 中把 active Buff 结束 / 移除委托给 `LegacyBuffRuntimeFacade.end_active_buff()`，保留 `Buff.end(...) -> active-list remove -> Buff end log -> enemy debuff mirror removal` 的旧顺序；`KickOutBuff()` 仍是 direct compatibility path。
- [x] `tests/simulator/test_buff_raw_container_guardrail.py` 已纳入 `implicit-events` shared gate，阻断 PRD-11 facade scope 中新增或扩散 raw `DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT`、`exist_buff_dict`、`ScheduleData.dynamic_buff`、`ScheduleData.loading_buff` passthrough。
- [x] 旧容器仍是 runtime source of truth：`BuffLoadLoop()` trigger judgement / pending queue population、`ScheduledEvent(...)` 构造时的 raw active/exist 参数、legacy `buff_add()`、legacy `KickOutBuff()`、core Load/Schedule append、handler requeue、dot runtime registration 与 `RuntimeCommandPort` compatibility reads 都是 retained boundary，不在 PRD-11 删除。
- [x] `BuffRuntimeReadPort` 保持只读；`RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 仍是 scheduled handlers 的 same-tick 写边界，PRD-11 没有新增第二套 handler write facade。
- [x] 验证通过：focused facade / simulator / guardrail / consistency pytest 均通过；`uv run python scripts/run_buff_main_loop_consistency.py --team "莱特火属性队" --stop-tick 600 --legacy-runtime "prd-10-baseline" --candidate-runtime "prd-11-facade" --json` 输出 `matches: true`、总伤 `646446.67` 且差异为空；`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` 与 full `uv run python scripts/run_buff_refactor_validation.py` 均通过。
- [x] `--legacy-runtime` / `--candidate-runtime` 继续只是 consistency / benchmark 报告标签，不是 live runtime switch；下一轮仍沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段 1 路线推进。

## 当前默认下一步

- [ ] 下一轮仍属于“阶段 1：基础设施解耦”，默认从 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md) 的“`ScheduledEvent` 对 Buff runtime facade 的依赖收口”候选块生成 Ralph PRD，优先收窄 `ScheduledEvent` / `EventContext` raw `dynamic_buff`、`exist_buff_dict`、`loading_buff` 暴露面，而不是继续扩写主循环 facade 样本。
- [ ] 若 PRD 生成器选择其他候选块，应仍从阶段 1 候选池中选择一个完整耦合块：`Update_Buff` 剩余生命周期内聚、Calculator 属性读取 seam、或异常 / debuff / dot 旁路耦合；不得只因为旧文本命中 `event_list` 就重开已闭合 producer 批次。
- [ ] PRD-11 已完成旧容器 facade 主体扩展；后续只有在 guardrail 暴露具体新增 raw-container passthrough、或 source scan 发现新的生产文件 / 函数 / 写表达式 / payload / target / 顺序证据时，才重新处理旧容器或已删除 `event_list` surface。
- [ ] 仅在 live simulator 真正消费 `config.buff_runtime.mode` 后，再把一致性 / benchmark 命令升级为真实 runtime switch 证据。
