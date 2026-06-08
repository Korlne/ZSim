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
- [x] 建立事件驱动基础设施边界，明确事件对象、事件上下文、事件分发入口与订阅入口。
- [x] 让 `Simulator` 不再直接控制旧 Buff 运行细节；阶段 1 范围内已由 `LegacyBuffRuntimeFacade` 接管 tick sweep、pending activation、active removal 与 individual-settled stack cleanup，旧容器对象身份仍保留。
- [x] 让 `ScheduledEvent` 改为依赖 Buff runtime facade；阶段 1 范围内已集中创建 runtime view / command port，并用 guardrail 收窄 raw runtime getter 扩散，构造兼容边界仍保留。
- [x] 让 `Update_Buff` 改为依赖 Buff runtime facade；阶段 1 范围内 live main-loop lifecycle 分支已走 facade，`KickOutBuff()` 与 no-facade fallback 仍是 retained compatibility path。
- [x] 为 `Calculator` 建立属性读取接口，隔离 `MultiplierData` 直读；`BuffAttributeReader` 已覆盖代表性 AM / AP 只读样本，`MultiplierData` 仍是公式与 retained XLogic compatibility snapshot。
- [x] 为基础设施解耦新增单元测试。
- [x] 为事件分发边界与事件顺序新增单元测试。
- [x] 为主循环一致性与性能验证补齐真实命令入口。
- [x] 为旧 `event_list` 发现口建立删除就绪清单、风险矩阵和 AST / 结构化数据 guardrail。
- [x] 执行旧 `event_list` 发现口删除 / 显式关闭：`JudgeTools.find_event_list()`、`check_preparation(..., event_list=...)` 缓存分支与 `BuffRecordBaseClass.event_list` 已关闭，并由 post-deletion guardrail 守门。

## 阶段 2：XLogic 全量分析与复用收敛

- [x] 输出 XLogic 全量分类结果。
- [x] 输出可复用方法清单。
- [x] 输出可复用记录对象清单。
- [x] 输出可复用 stat reader / event adapter / state sync 模式清单。
- [x] 输出可复用事件类型 / 事件处理器 / 事件订阅模式清单。
- [x] 明确 XLogic 替换优先级。
- [x] 明确高风险耦合桶和回归风险点。

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
- [x] 这条 2026-06-05 阶段 1 backlog 已被后续 `PRD-8` 至 `PRD-12 US-024` 的复扫、删除发现口、guardrail / validation evidence 与 closure decision 覆盖；当前作为历史记录保留，不再是 active 阶段 1 backlog。只有 guardrail / validation / root-workspace source scan 给出新的生产证据时，才重新开窄 blocker PRD。

## 本轮剩余 producer batch / shared-validation PRD 收口状态（2026-06-06）

- [x] 代表性 `AlicePolarizedAssaultTrigger -> PolarizedAssaultEvent` 计划事件链，以及本轮收口的 `ElegantVanitySpRecover`、`LunarNoviluna`、`MagneticStormCharlieSpRecover`、`SeedAdditionalAbilityTrigger`、`SliceofTimeExtraResources`、`CannonRotor`、`YanagiPolarityDisorderTrigger`、`HugoCorePassiveTotalizeTrigger` 与 `DecibelManager`，现都已改经 `ScheduleDispatchPort` 发布 planned event。
- [x] `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 仍是本轮唯一沿用的 same-tick 显式写边界；`SkillEventHandler` 的 `update_anomaly()` / `ScheduleBuffSettle()` 与 `AnomalyEventHandler` 的 `ScheduleBuffSettle(..., anomaly_bar=event)` 同 tick 写边界保持走显式命令口，没有引入第二套 write facade。
- [x] `implicit-events` 共享验证入口现已同时覆盖 `test_schedule_dispatch.py`、聚焦 dispatch/runtime-boundary pytest，以及这些 focused 回归文件本身的 scoped mypy，handoff 文档已同步记录验证命令与当前基线。
- [x] 这条 2026-06-06 阶段 1 剩余 producer / helper backlog 已被 `PRD-12 US-024` 显式 supersede：已闭合的 producer batch 和已删除的 `event_list` surface 不作为默认后续工作。若后续 guardrail / validation / root-workspace source scan 发现具体生产失败证据，再按失败文件、符号和验证入口开窄 blocker PRD。

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

## 本轮 PRD-12 阶段 1 基础设施完成交接状态（2026-06-07）

- [x] `ScheduledEvent` / `EventContext` raw runtime 暴露已完成 audit、compatibility getter 收窄、same-tick helper 处理、构造集中化与 no-new-raw-runtime guardrail；handler requeue、`LoadDamageEvent` damage-effect continuation、`SPUpdateData` 面板刷新读路径、`ScheduleDispatchPort` 队列语义、`RuntimeCommandPort` same-tick 写边界和 `BuffRuntimeReadPort` 只读语义均保留。
- [x] `Update_Buff` lifecycle 块已完成 audit、active removal / individual-settled stack cleanup facade routing、raw-container guardrail 与 main-loop safety 验证；`KickOutBuff()`、no-facade fallback、anomaly expiration、dot expiration、enemy debuff mirror 单一事实源与公式语义仍是 retained compatibility / non-target。
- [x] Calculator read seam 已完成 `MultiplierData` / alias usage inventory、`BuffAttributeReader` 最小接口、两个代表性 XLogic 只读样本与 `calculator-reads` guardrail/profile 覆盖；`MultiplierData` 仍保留给 Calculator / CalAnomaly 公式和 retained XLogic compatibility snapshot。
- [x] anomaly / debuff / dot bypass 块已完成分类、`AnomalyBar.__get_max_duration()` runtime view 读口样本、`BuffAddStrategy` active-store / enemy-mirror facade 写入样本与 bypass-layer semantics tests；scheduled publish、listener broadcast、dot runtime registration 与 runtime immediate write 保持四层分离。
- [x] phase-1 guardrail matrix 已同步到 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)，覆盖 deleted `event_list` surfaces、raw scheduler queue writes、raw old-container passthrough、`ScheduledEvent` raw runtime getter、lifecycle raw container、Calculator read seam 与 anomaly / debuff / dot bypass。
- [x] 阶段 1 验证证据已记录：`implicit-events`、`calculator-reads` 与默认 lifecycle validation profile 均通过；`青衣雷属性队` `stop-tick 120` consistency JSON 样本 `matches=true`，benchmark JSON 样本在复用 consistency damage-data fallback 后通过。
- [x] `--legacy-runtime` / `--candidate-runtime` 继续只是 consistency / benchmark 报告标签，不是 live runtime switch；只有 live simulator 真正消费 `config.buff_runtime.mode` 后，才可把这些命令当真实 runtime 切换证据。
- [x] 旧容器仍是 retained compatibility boundary：本阶段关闭的是基础设施扩散风险和代表性 facade / read / dispatch seam，不等同于删除 `exist_buff_dict`、`DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT`、legacy `buff_add()`、legacy `KickOutBuff()` 或全部 `MultiplierData` 公式快照。
- [x] `US-024` 已基于 completion matrix、guardrail matrix、serial validation 和 handoff docs 声明阶段 1 基础设施解耦关闭；阶段 2 可以作为下一轮 PRD 默认入口。
- [x] 2026-06-08 gap-closure guardrail evidence 已补齐 `zsim/sim_progress/Buff/ScheduleBuffSettle.py` raw old-container guardrail 覆盖，并将其纳入 `lifecycle` 与 `implicit-events` scoped mypy targets；当前旧容器写入只按 `legacy ScheduleBuffSettle command-adapter internals` retained boundary 和 ceiling 保留。
- [x] 该 gap-closure PRD 不替换 live runtime path，不删除旧容器，不重开已删除的 `event_list` surface，不重启已闭合的 producer batch，也不合并 listener broadcast / scheduled queue / runtime write 分层；完整 closure 后默认路线仍返回阶段 2。
- [x] gap-closure final validation 已通过：`implicit-events` profile 基础 `2 passed`、隔离队伍 `3 passed`、focused `105 passed`、mypy `76 source files` clean；默认 lifecycle profile 基础 `2 passed`、隔离队伍 `3 passed`、focused raw-container guardrail `18 passed`、mypy `9 source files` clean。root-workspace scan 未新增 production raw `event_list` producer 或 handler/helper direct `ScheduleBuffSettle(...)` caller，阶段 2 仍是下一轮默认入口。

## 本轮阶段 2 XLogic 全量分类与复用收敛 PRD 收口状态（2026-06-08）

- [x] [BuffXLogic阶段2全量分类与复用矩阵.md](./BuffXLogic阶段2全量分类与复用矩阵.md) 已输出非排他分类 schema、149 个 root-workspace `BuffXLogic` census、infrastructure / leaf 分离、逐文件 class / record / public method 元数据和可复现扫描命令。
- [x] 已分类 Calculator / 属性读取、事件触发 / scheduled publish、record / count / state-sync、runtime container / service-location、anomaly / debuff / dot / formula bypass 等耦合桶；`.codex_worktrees/` 仅作为历史证据，未作为生产 blocker。
- [x] 可复用方法 / stat reader 方向已收敛为 `BuffAttributeReader` helper family：AM / AP 已有代表样本，impact、full crit rate、personal crit rate、personal crit damage 是后续候选，不在本 PRD 删除 `MultiplierData` / `MulData` / CalAnomaly 公式快照。
- [x] 可复用记录对象与 state-sync 模式已记录：`check_record_module()` / `get_prepared(...)`、record lazy init、trigger-state read、computed count writeback、`dy.count`、`built_in_buff_box` tuple sync、ledger / cooldown state、`update_to_buff_0(...)` template sync。
- [x] event adapter / handler / listener 模式已记录：`ScheduleDispatchPort` queue-only publish、handler runtime-view reads、`RuntimeCommandPort` same-tick writes、listener broadcast 同步分层、dot runtime registration / removal 分层；不把这些合并成一个事件总线。
- [x] 优先级与高风险矩阵已输出：默认下一 phase-2 PRD 是 AM/AP reader + computed count state-sync family；crit / impact reader、trigger-state read-only gate、scheduled publish ordering parity、dot runtime-state、BuffAddStrategy facade-write 作为同阶段候选池保留。
- [x] 本 PRD 没有替换 live XLogic、runtime port、facade、dispatch adapter、listener、Dot 或 validation wiring；它只完成分类、复用设计与 handoff 同步。
- [x] 验证基线：`implicit-events` 与 `calculator-reads` profiles 在分类 stories 中均已串行通过；US-009 final validation 继续复跑这两个入口。

## 本轮阶段 2 AM/AP reader + computed count state-sync PRD 收口状态（2026-06-08）

- [x] P2-A 六个 root-workspace 文件已完成 AM/AP reader 迁移：`AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`、`YuzuhaAdditionalAbilityAnomalyDmgBonus.py`、`JaneCinema1APTransToDmgBonus.py`、`JaneCoreSkillStrikeCritRateBonus.py`、`JanePassionStateAPTransToATK.py`。
- [x] `create_anomaly_attribute_read_context(...)` 只承担 `BuffAttributeReadContext` 构造；各 XLogic 文件仍显式保留 `read_anomaly_mastery(...)` / `read_anomaly_proficiency(...)`、阈值 / count 公式、`simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` 顺序。
- [x] `tests/simulator/test_buff_attribute_reader.py`、`tests/simulator/test_buff_attribute_state_sync.py` 与 `tests/simulator/test_migrated_am_ap_reader_guardrail.py` 已覆盖 reader parity、computed count state-sync 顺序、source guardrail 与 `.codex_worktrees/` 排除。
- [x] 验证基线：US-013 已串行通过 focused pytest `45 passed`、`calculator-reads` profile（base `2 passed`、isolated teams `3 passed`、focused `63 passed`、mypy `20 source files` clean）与 `implicit-events` profile（base `2 passed`、isolated teams `3 passed`、focused `105 passed`、mypy `76 source files` clean）。
- [x] 当前注册队伍不含 Alice / Yuzuha / Jane 代表样本，未运行 main-loop behavior sample；本轮以 parity / order / guardrail tests 与两个 validation profiles 作为 P2-A 收口证据。
- [x] P2-A 没有重写 Calculator / CalAnomaly 公式，没有删除 old containers，没有重开 raw queue、`ScheduleDispatchPort`、`RuntimeCommandPort`、listener broadcast、dot runtime registration 或 same-tick runtime write 边界。

## 本轮阶段 2 crit / impact reader family PRD 收口状态（2026-06-08）

- [x] P2-B 九个 root-workspace 文件已完成 reader 迁移：`LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py`、`CannonRotor.py`、`MiyabiCoreSkill_IceFire.py`、`WoodpeckerElectroSet4_NA.py`、`WoodpeckerElectroSet4_E_EX.py`、`WoodpeckerElectroSet4_CA.py`。
- [x] `CalculatorBuffAttributeReader` 已覆盖 `read_impact(...)`、`read_full_crit_rate(...)`、`read_personal_crit_rate(...)`、`read_personal_crit_damage(...)`；full crit 包含 `crit_rate_received_increase`，personal crit rate / damage 不包含 received crit。
- [x] `tests/simulator/test_buff_attribute_reader.py`、`tests/simulator/test_buff_attribute_state_sync.py`、`tests/simulator/test_full_crit_event_adjacent_reader.py`、file-specific dispatch tests 与 `tests/simulator/test_migrated_p2b_reader_guardrail.py` 已覆盖 reader parity、count/order sync、event-adjacent branches、source guardrail 与 `.codex_worktrees/` 排除。
- [x] 验证基线：US-017 已串行通过 focused P2-B pytest `107 passed`、`calculator-reads` profile（base `2 passed`、isolated teams `3 passed`、focused `129 passed`、mypy `22 source files` clean）与 `implicit-events` profile（base `2 passed`、isolated teams `3 passed`、focused `136 passed`、mypy `77 source files` clean）。
- [x] 行为样本：`uv run python scripts/run_buff_main_loop_consistency.py --team "莱特火属性队" --stop-tick 600 --legacy-runtime "p2b-us017-baseline" --candidate-runtime "p2b-us017-reader" --json` 已通过；`matches=true`，总伤 `646446.67` vs `646446.67`，event count `19` vs `19`，buff timeline 差异为零。
- [x] P2-B 没有重写 Calculator / CalAnomaly 公式，没有删除 old containers，没有重开 raw queue、`ScheduleDispatchPort`、`RuntimeCommandPort`、listener broadcast、dot runtime registration、same-tick runtime write 或 phase-1 deletion 边界。

## 当前默认下一步

- [x] `US-024` 已完成 closure decision，没有输出 phase-1 blocker package；不得继续生成新的阶段 1 实现 PRD，除非 guardrail / validation 给出新的生产失败证据。
- [x] 阶段 2 第一轮“全量分类、复用方法 / 记录对象 / stat reader / event adapter / state sync / handler / listener pattern 清单与风险矩阵”已完成；后续不再把“做全量分类”当默认下一步。
- [x] P2-A “AM/AP reader + computed count state-sync family” 已完成；后续不再把六个已迁移文件当默认实现 backlog，除非 source guardrail 或 validation 给出具体回归证据。
- [x] P2-B “crit / impact reader family package” 已完成；后续不再把九个已迁移 impact / crit 文件当默认实现 backlog，除非 source guardrail、focused test 或 validation 给出具体回归证据。
- [ ] 下一轮默认 PRD 应沿 [Buff重构方案.md](./Buff重构方案.md) 继续留在阶段 2，优先选择 “trigger-state read-only gates” 作为 P2-C old-template-state read / no-write gate focused test 包，而不是单文件薄切片或阶段 3 全面替换。
- [ ] 同阶段候选池必须继续保留 scheduled publish ordering parity、dot runtime-state / initialization、BuffAddStrategy caller / facade-write design、direct simulator context helpers 与 phase-3-only formula snapshot replacement，避免 PRD 生成器只沿上一个文件继续。
- [ ] 若后续 validation 或 guardrail 重新暴露阶段 1 blocker，下一轮 PRD 只处理 blocker package 中列出的具体文件、符号、失败测试、失败 guardrail 或验证命令；不得重开已删除的 `event_list` surface 或已闭合的 producer batch，除非 guardrail 给出新的生产证据。
