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
- [ ] 每个 production semantic 切片都有主循环一致性验证；文档 / test-only / guardrail-only / retained-compatibility story 记录跳过原因，不创建 validation-only team。
- [x] Phase 3 formula rollback plan 已 codify：失败 helper / profile / formula diff 必须回退到 retained source anchors，并保留 `formula-parity`、`calculator-reads`、`implicit-events` 与 old Buff runtime compatibility gates；P2-A through P2-G 只按 concrete blocker 证据重开。
- [x] Phase 3 replacement blocker closure 已完成最终 handoff：`Calculator.AnomalyMul.cal_res_pen()` 是唯一允许进入下一轮 bounded production replacement proposal 的公式域；本 PRD 没有替换生产公式或删除 retained runtime/container compatibility。
- [x] Phase 3 bounded proposal handoff 已完成最终 Go / No-Go：later implementation PRD 为 Go，但只限 `Calculator.AnomalyMul.cal_res_pen()`；broad `Calculator.py` / `CalAnomaly.py` rewrite、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、runtime ports/facades 与 `MultiplierData` / `MulData` / `DynamicStatement` 删除仍为 No-Go。
- [x] Phase 3 bounded implementation handoff 已完成最终验证：`Calculator.AnomalyMul.cal_res_pen()` 已实现为 behavior-preserving selector extraction，最终状态是 implemented，非 partially blocked / rolled back；`formula-parity` 与 `calculator-reads` 串行通过，`implicit-events` / 默认 profile 因未触达对应边界而跳过并记录原因。
- [x] Phase 3 AM/AP/impact oracle-gap closure 已完成最终 handoff：`Calculator.AnomalyMul.cal_am()`、`Calculator.AnomalyMul.cal_ap()`、`Calculator.StunMul.cal_imp()` 与 `CalculatorBuffAttributeReader` 对应读口已具备 retained oracle、reader snapshot parity、boundary split、profile wiring、registered-sample 条件和串行 `formula-parity` / `calculator-reads` 证据；下一默认 PRD 可进入 bounded production proposal，但不得扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite 或 retained compatibility 删除。
- [x] Phase 3 AM/AP/impact bounded implementation 已完成最终 handoff：`Calculator.AnomalyMul.cal_ap()` 已委托 `_calculate_anomaly_proficiency(...)`，`Calculator.StunMul.cal_imp()` 已委托 `_calculate_impact(...)`，AM helper-backed baseline 保持不变；focused reader pytest、`formula-parity` 与 `calculator-reads` 串行通过，copied-output、event/runtime、lifecycle、validation-runner 和 registered-route live semantics 均未触达。
- [x] Phase 3 RegularMul sheer reader-snapshot readiness 已完成最终 handoff：`Calculator.RegularMul.cal_base_attr(..., base_attr=4)` retained runtime dependency 已有 focused oracle，`cal_sheer_dmg_bonus()` 保持 snapshot-compatible；最终 Go / No-Go 为 production proposal No-Go，阻塞项是 reader-snapshot contract gap 与缺少真实 registered sheer route。retained gates 为 `formula-parity`、`calculator-reads` 与条件式 `implicit-events`；rollback anchors 继续保留 `Calculator.py`、`_CalculatorReadSnapshot`、`MultiplierData`、`DynamicStatement`、old containers、copied-output constructors、dispatch/runtime/listener boundaries 和 validation-runner wiring。
- [x] Phase 3 RegularMul crit-rate bounded implementation 已完成 US-007 handoff：`Calculator.RegularMul.cal_crit_rate(data)` 已通过 `_calculate_full_crit_rate(...)` helper seam 实现 / no-op verified；full crit 继续包含 `crit_rate_received_increase`，personal crit / personal reader contrast boundary 继续排除 received crit。Retained gates：selected crit focused tests、`formula-parity`、`calculator-reads` 保留为 formula/read rollback anchors；`implicit-events`、default lifecycle validation 和 main-loop consistency 仍只在后续触达对应 copied-output / event / dispatch/runtime / listener / lifecycle / validation-runner / old-container / registered-route live semantic surface 时追加。
- [x] Phase 3 RegularMul personal crit damage bounded implementation 已完成 US-008 handoff：`Calculator.RegularMul.cal_personal_crit_dmg(data)` 已通过 `_calculate_personal_crit_damage(static_statement, dynamic_statement)` helper seam 实现 / no-op verified；`CalculatorBuffAttributeReader.read_personal_crit_damage(context)` 仍委托 public formula path，公式保持 `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` 且继续排除 `received_crit_dmg_bonus`。Verifier commands：focused personal-crit-damage pytest、scoped mypy、focused docs `git diff --check`、Ralph JSON sanity 与 UTF-8 / mojibake scan；reviewer / invariant verdict：PASS，event queue、synchronous listener broadcasts、same-tick runtime writes、old containers、validation-runner behavior、registered routes 和 retained compatibility paths 未改变。
- [x] Phase 3 RegularMul personal crit rate bounded implementation 已完成 US-008 handoff：`Calculator.RegularMul.cal_personal_crit_rate(data)` 已通过 `_calculate_personal_crit_rate(static_statement, dynamic_statement)` helper seam 实现 / no-op verified；`CalculatorBuffAttributeReader.read_personal_crit_rate(context)` 仍委托 public formula path，公式保持 `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` 且继续排除 `crit_rate_received_increase`。Verifier commands：focused personal/full crit pytest `10 passed, 135 deselected`、scoped mypy `Success: no issues found in 2 source files`、focused docs `git diff --check`、Ralph JSON sanity 与 UTF-8 / mojibake scan；reviewer / invariant verdict：PASS，event queue、synchronous listener broadcasts、same-tick runtime writes、old containers、validation-runner behavior、registered routes 和 retained compatibility paths 未改变。
- [x] Phase 3 RegularMul full crit damage proposal-readiness 已完成 US-008 handoff：proposal result 为 Conditional Go for one later bounded implementation PRD only，目标限 `Calculator.RegularMul.cal_crit_dmg(data)` 与可选 module-local behavior-preserving helper；future helper 必须保持 `aftershock_attack` label branch、`received_crit_dmg_bonus` inclusion、`min(5, crit_dmg)` cap、public signature 和 current `SkillNode` assumption。Verifier commands：focused full-crit pytest `5 passed, 143 deselected`、scoped mypy `Success: no issues found in 2 source files`，并继承 US-007 serial `formula-parity` success。Reviewer / invariant verdict：PASS，event queue、synchronous listener broadcasts、same-tick runtime writes、explicit ports/adapters、old containers、validation-runner behavior、registered routes 和 retained compatibility paths 未改变。
- [x] Phase 3 RegularMul full crit damage bounded implementation 已完成 US-008 handoff：`Calculator.RegularMul.cal_crit_dmg(data)` 已通过 `_calculate_full_crit_damage(static_statement, dynamic_statement, judge_node)` helper seam 实现 / no-op verified；`aftershock_attack` label branch、`received_crit_dmg_bonus` inclusion、`min(5, crit_dmg)` cap、public signature、current `SkillNode` assumption、old containers、event/runtime/listener layers、validation-runner behavior、registered routes 和 retained compatibility 均保持不变。下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal，不继续折叠到 full crit damage。
- [x] Phase 3 same-phase candidate selection PRD US-011 handoff 已同步：selected candidate outcome 为 Conditional Go / No-Go for one later bounded implementation PRD，且只限 `Calculator.RegularMul.cal_dmg_bonus(data)` 的 `regular-dmg-bonus-character-field-stack`（fire / normal attack / `aftershock_attack` / all-damage）等价 helper seam。下一默认 PRD 改为该 exact `cal_dmg_bonus()` bounded implementation；retained boundaries 继续保留 focused oracle / scoped mypy、serial `formula-parity` / `calculator-reads`、conditional `implicit-events` / default profile、registered-sample Conditional No-Go、old containers、event queue、synchronous listener broadcasts、same-tick runtime writes、dispatch/runtime ports、listener/dot layers 和 retained compatibility。same-phase pool 未折叠：registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future Stun follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留；本 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Phase 3 same-phase candidate selection PRD US-012 final evidence 已封存：Ralph JSON sanity、focused `git diff --check`、UTF-8 / U+FFFD / mojibake scan、checkpoint、reviewer verdict、staged-set 检查与 progress / dashboard / evidence ledger 已同步；Markdown PRD 与 `scripts/ralph/prd.json` 继续分离，Ralph JSON conversion 保留为后续显式步骤。下一 likely PRD 类型是 bounded implementation，目标仍只限 `Calculator.RegularMul.cal_dmg_bonus(data)` / `regular-dmg-bonus-character-field-stack`，proposal-readiness、guarded maintenance 与 No-Go/blocker closure 仅作为保留候选池类别。

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

## 本轮阶段 2 trigger-state read-only gates PRD 收口状态（2026-06-08）

- [x] P2-C 只读触发状态 helper 已落地：`zsim/sim_progress/Buff/JudgeTools/TriggerState.py` 提供 frozen `TriggerBuffState` 与 `read_trigger_buff_state(record)`，只读取已由 `check_preparation(..., trigger_buff_0=...)` / `trigger_buff_0_handler(...)` 写入 `history.record.trigger_buff_0` 的旧模板 Buff 状态。
- [x] 五个 root-workspace migrated files 已完成：`FlamemakerShakerApBonus.py`、`SpectralGazeImpactBonus.py`、`SharpenedStingerAnomalyBuildupBonus.py`、`CordisGerminaSNAAndQIgnoreDefense.py` 与 `AstralVoice.py` 不再通过 `record.trigger_buff_0.dy.active` / `.count` / `.built_in_buff_box` direct chain 读取已迁移 gate。
- [x] `AstralVoice.special_effect_logic(...)` 保留旧 state-sync 顺序：先 `simple_start(...)`，再从 `TriggerBuffState.count` 写 current `dy.count`，最后 `update_to_buff_0(self.buff_0)`；old equipment-owner `buff_0` identity 与 `record.sub_exist_buff_dict` 仍由旧兼容路径提供。
- [x] P2-C focused tests 与 guardrail 已覆盖 active / inactive、threshold、tuple-box length、lazy `history.record`、old template identity、no-write branch、count-mirror order 和 source guardrail；`tests/simulator/test_migrated_p2c_trigger_state_guardrail.py` 只扫描五个已迁移 root 文件并排除 `.codex_worktrees/`。
- [x] 验证基线：US-012 已串行通过 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`，base `2 passed`、isolated teams `3 passed`、focused `181 passed`、mypy `80 source files` clean。
- [x] 行为样本：`uv run python scripts/run_buff_main_loop_consistency.py --team "席德大安比队" --stop-tick 1000 --legacy-runtime p2c-baseline --candidate-runtime p2c-current --json` 已通过；`matches=true`，总伤 `5744827.24` vs `5744827.24`，event count `50` vs `50`，buff timeline 差异为零。
- [x] P2-C 没有给 `BuffRuntimeReadPort` 新增写 API，没有删除 old containers，没有重开 raw queue、`ScheduleDispatchPort`、`RuntimeCommandPort`、listener broadcast、dot runtime registration、Calculator formula 或 phase-1 deletion 边界。
- [x] 本轮未发现新的旧 Buff 耦合点；`docs/旧Buff系统耦合审查结果.md` 不需要新增 P2-C blocker 条目。

## 本轮阶段 2 BuffAddStrategy caller / facade-write design PRD 收口状态（2026-06-09）

- [x] P2-F 已完成 caller taxonomy 与 focused coverage：`test_buff_add_strategy_runtime_facade.py` 锁定 active replacement、enemy mirror sync、target fan-out、template identity 和 no-pending-queue 写入；Hugo、Roaring Ride、Seed、`UpdateAnomaly`、BattleEventListener 与 Character manager representative caller tests 均已覆盖 exact `buff_add_strategy(...)` arguments、branch/no-op gates 和 `sim_instance` forwarding。
- [x] P2-F cross-layer semantics 已由 `test_bypass_layer_semantics.py` 覆盖：forced Buff / Debuff write 仍是 same-tick runtime write，和 `ScheduleDispatchPort` planned publish、同步 listener broadcast、`RuntimeCommandPort` scheduled-handler command write、`BuffRuntimeReadPort` read-only access 分层。
- [x] P2-F guardrail 已由 `tests/simulator/test_migrated_p2f_buff_add_strategy_guardrail.py` 接入 `FOCUSED_PYTEST_PROFILES["implicit-events"]` 和 scoped mypy；guardrail exact-file 扫描 `BuffAddStrategy.py` / `buff_runtime.py`，排除 `.codex_worktrees/`、`__pycache__/` 和 archive paths，阻断 raw pending queue、raw active store、raw enemy mirror、deleted event-list discovery、scheduled queue conversion、listener broadcast conversion、第二 write facade 与 `BuffRuntimeReadPort` write API 回流。
- [x] 验证基线：P2-F release validation 已串行通过 uncovered caller focused pytest（Roaring Ride `5 passed`、Seed `6 passed`、`UpdateAnomaly` `10 passed`、listener `4 passed`、Character `4 passed`）与 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`；profile 覆盖 base simulator `2 passed`、isolated teams `3 passed`、focused implicit-events `229 passed`，类型检查通过。
- [x] 本 PRD 没有删除 old containers、legacy `buff_add()`、legacy `KickOutBuff()`，没有替换 Calculator / CalAnomaly formulas，没有迁移 direct simulator context helpers，没有把 forced Buff / Debuff write 转成 scheduled queue 或 listener broadcast，也没有新增第二套 write facade。
- [x] 本轮未发现新的旧 Buff 耦合点；`docs/旧Buff系统耦合审查结果.md` 不需要新增 P2-F blocker 条目。

## 本轮阶段 2 direct simulator context helpers PRD 收口状态（2026-06-09）

- [x] P2-G 已完成 direct simulator service-family representative coverage：Yuzuha tick / preload / next-character / report-state、enemy context、listener lookup、RNG service、report-state representative 与 factory-backed scheduled preload contrast 均有 focused tests。
- [x] `tests/simulator/test_migrated_p2g_direct_context_guardrail.py` 已接入 `implicit-events` focused pytest 与 scoped mypy；guardrail 只扫描 selected root files / symbols，排除 `.codex_worktrees/`、`__pycache__/`、generated logs 和 `scripts/ralph/archive/**`，不扩散到 P2-A through P2-F completed buckets。
- [x] P2-G 保留 tick / preload / char-data / enemy / listener / RNG / report-state 的服务分层；没有抽取 universal simulator context helper，也没有把 direct context reads 伪装成 `LegacyBuffRuntimeFacade`、`RuntimeCommandPort`、`ScheduleDispatchPort` 或 `BuffRuntimeReadPort` 工作。
- [x] 验证基线：US-012 已串行通过 changed focused pytest `67 passed`、`implicit-events` profile（base `2 passed`、isolated teams `3 passed`、focused `238 passed`、mypy `88 source files` clean）与 `calculator-reads` profile（base `2 passed`、isolated teams `3 passed`、focused `133 passed`、mypy `22 source files` clean）。
- [x] 本 PRD 没有改 root production behavior、lifecycle wiring 或 live registered-team semantics；main-loop consistency sample 因无 live semantic change 而跳过。
- [x] 本轮未发现新的旧 Buff 耦合点；`docs/旧Buff系统耦合审查结果.md` 不需要新增 P2-G blocker 条目。

## 当前默认下一步

- [x] `US-024` 已完成 closure decision，没有输出 phase-1 blocker package；不得继续生成新的阶段 1 实现 PRD，除非 guardrail / validation 给出新的生产失败证据。
- [x] 阶段 2 第一轮“全量分类、复用方法 / 记录对象 / stat reader / event adapter / state sync / handler / listener pattern 清单与风险矩阵”已完成；后续不再把“做全量分类”当默认下一步。
- [x] P2-A “AM/AP reader + computed count state-sync family” 已完成；后续不再把六个已迁移文件当默认实现 backlog，除非 source guardrail 或 validation 给出具体回归证据。
- [x] P2-B “crit / impact reader family package” 已完成；后续不再把九个已迁移 impact / crit 文件当默认实现 backlog，除非 source guardrail、focused test 或 validation 给出具体回归证据。
- [x] P2-C “trigger-state read-only gates” 已完成；后续不再把五个已迁移 trigger-state 文件当默认实现 backlog，除非 P2-C source guardrail、focused no-write / count-mirror tests、`implicit-events` 或 behavior sample 给出具体回归证据。
- [x] P2-D “scheduled publish ordering / adapter parity” 已完成 guarded scope：adapter rebinding、resource refresh payload / order、`SkillNode` / `LoadingMission` order、stateful anomaly / dot layer separation、fan-out / multi-publish parity 与 exact-file source guardrail 已由 focused tests、`test_migrated_p2d_scheduled_publish_guardrail.py` 和 `implicit-events` 串行验证覆盖；后续不再把 P2-D 当默认 backlog，除非 guardrail / validation 给出具体回归证据。
- [x] P2-E “dot runtime-state / initialization” 已完成 guarded scope：`DotRuntimeStateAdapter`、`DotInitializationReadContext`、Vivian dot presence / registration、Shock duration initialization、`UpdateAnomaly` replacement / removal、freeze follow-up 分层、exact-file P2-E guardrail 与 `implicit-events` 串行验证均已覆盖；后续不再把 P2-E 当默认 backlog，除非 P2-E guardrail / focused tests / validation 给出具体回归证据。
- [x] P2-F “BuffAddStrategy caller / facade-write design” 已完成 guarded scope：caller taxonomy、active replacement、enemy mirror sync、selected-target fan-out、Character / listener / BuffXLogic / `UpdateAnomaly` 代表 caller tests、cross-layer semantics、exact-file P2-F guardrail 和 `implicit-events` validation 均已覆盖；后续不再把 P2-F 当默认 backlog，除非 P2-F guardrail / focused tests / validation 给出具体回归证据。
- [x] P2-G “direct simulator context helpers” 已完成 guarded scope：Yuzuha、enemy context、listener lookup、RNG service、report-state representative、exact-file / selected-symbol guardrail 和 `implicit-events` validation 均已覆盖；后续不再把 P2-G 当默认 backlog，除非 P2-G guardrail / focused tests / validation 给出具体回归证据。
- [x] 阶段 2 closure / phase-3 formula snapshot readiness decision 已完成：P2-A through P2-G 没有剩余默认实现候选，phase-3 production formula replacement 当前 No-Go。
- [x] 下一轮默认 PRD 应沿 [Buff重构方案.md](./Buff重构方案.md) 从阶段 2 guarded-maintenance 状态转入 phase-3 formula parity suite design / characterization：先命名 candidate files、focused pytest targets、scoped mypy targets、behavior-sample 条件、rollback plan、validation entrypoints 和 non-goals，再评估是否允许 production formula replacement。
- [x] US-014 closure / readiness PRD 最终串行验证已通过：changed focused pytest `tests/simulator/test_buff_attribute_reader.py -q` 为 `38 passed`；`calculator-reads` profile 为 base `2 passed`、isolated teams `3 passed`、focused `138 passed`、mypy `22 source files` clean；`implicit-events` profile 为 base `2 passed`、isolated teams `3 passed`、focused `238 passed`、mypy `88 source files` clean。
- [x] US-015 handoff docs 已同步：phase-3 characterization / validation-readiness 证据、`formula-parity` scoped profile、`calculator-reads` retained gate、下一候选池和 production formula replacement No-Go 边界均已回写到 checklist、下阶段计划、阶段 2/3 矩阵与替换说明。
- [x] US-016 final serial validation / Go / No-Go handoff 已完成：touched focused pytest `tests/simulator/test_buff_attribute_reader.py -q` 为 `60 passed`，Vivian copied-output dispatch focused tests 为 `3 passed`；`formula-parity` profile 为 base `2 passed` / isolated teams `3 passed` / focused `60 passed` / mypy `9 source files` clean；`calculator-reads` profile 为 base `2 passed` / isolated teams `3 passed` / focused `160 passed` / mypy `22 source files` clean；`implicit-events` profile 为 base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean；默认 lifecycle profile 为 base `2 passed` / isolated teams `3 passed` / focused `18 passed` / mypy `9 source files` clean。
- [x] US-025 serial validation gate 已通过：`formula-parity` profile 为 base `2 passed` / isolated teams `3 passed` / focused `95 passed` / mypy `9 source files` clean；`calculator-reads` profile 为 base `2 passed` / isolated teams `3 passed` / focused `195 passed` / mypy `22 source files` clean；`implicit-events` profile 为 base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean；未改 lifecycle container / runtime write path / validation runner 行为，因此默认 lifecycle profile 不作为本次新增证据重跑。
- [x] US-026 Final Go / No-Go：production formula replacement 下一 PRD 仍 No-Go，当前没有单个生产公式域获得替换许可。下一默认 PRD 改为 phase-3 replacement blocker closure / bounded-domain eligibility decision：先补 `Calculator.AnomalyMul.cal_res_pen()` 与 `anomaly_snapshot` vector assembly、`CalAnomaly.cal_k_level()` clamp、copied-output handler/report payload parity 和真实 registered-route 触发条件；这些 blocker 关闭前不得替换 `Calculator.py` / `CalAnomaly.py` / copied-output 生产公式。
- [x] 同阶段候选池继续保留 P2-A through P2-G guarded maintenance、phase-3 formula parity design、retained compatibility 与 blocker-only phase-1 reopen rules，避免 PRD 生成器只沿上一个文件继续。
- [x] US-007 Final proposal Go / No-Go：当前 PRD 已验证 bounded `cal_res_pen()` proposal package；下一默认 PRD 可以实现 exactly `Calculator.AnomalyMul.cal_res_pen()` 的 bounded diff，但不得实现 broad formula rewrite、不得删除 retained compatibility，也不得把 `anomaly_snapshot`、`CalAnomaly.cal_k_level()` 或 copied-output payload parity 扩成第二生产替换域。
- [x] US-007 保留边界确认：本 PRD 未删除 old containers、legacy `buff_add()`、legacy `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、`MultiplierData`、`MulData`、`DynamicStatement` 或 copied-output constructors；P2-A through P2-G 继续只按 guardrail / validation concrete blocker 重开。
- [x] Current US-009 Final implementation handoff：bounded `cal_res_pen()` selector extraction 已完成并由 focused oracle / retained reader-snapshot parity、`formula-parity`（focused `116 passed` / mypy 9 files clean）与 `calculator-reads`（focused `216 passed` / mypy 22 files clean）证明；下一默认 PRD 改为 Phase-3 next-candidate selection / oracle-gap closure，不在 focused regression 或 validation failure 之外重开 `cal_res_pen()`。
- [x] Current US-009 保留边界确认：`Calculator.AnomalyMul.cal_res_pen(data)` 仍是 public retained formula method，`Calculator.AnomalyMul.__init__` 仍从该方法赋值 `self.res_pen`；`Calculator.AnomalyMul.anomaly_snapshot`、`CalAnomaly.cal_k_level()`、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade` 与 P2-A through P2-G guarded buckets 均未删除或扩大替换。
- [x] Current US-013 Final AM/AP/impact handoff：oracle/readiness 闭环已完成，US-013 复跑 `formula-parity`（base `2 passed` / isolated teams `3 passed` / focused `132 passed` / mypy 9 files clean）与 `calculator-reads`（base `2 passed` / isolated teams `3 passed` / focused `232 passed` / mypy 22 files clean）均通过；下一默认 PRD 改为 bounded AM/AP/impact production proposal，先选择 exact helper scope、rollback、registered-sample 条件、retained gates 和 non-goals，再进入实现。
- [x] Current US-013 保留边界确认：AM/AP/impact proposal-ready 不等于立即生产改写；`MultiplierData` / `MulData` / `DynamicStatement`、`AnomalyBar.current_ndarray`、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade` 与 P2-A through P2-G guarded buckets 均保留。
- [x] Current US-007 Final AM/AP/impact proposal Go / No-Go：bounded production implementation PRD 为 Go；US-007 串行复跑 `formula-parity`（base `2 passed` / isolated teams `3 passed` / focused `132 passed` / mypy 9 files clean）与 `calculator-reads`（base `2 passed` / isolated teams `3 passed` / focused `232 passed` / mypy 22 files clean）均通过。授权只限 `Calculator.py` 内 scalar helper-family：AM helper-backed baseline 保持不变、`Calculator.AnomalyMul.cal_ap()` 委托 `_calculate_anomaly_proficiency(...)`、新增 scalar `_calculate_impact(...)` 并让 `Calculator.StunMul.cal_imp()` 委托该 helper；不得扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite。
- [x] Current US-007 保留边界确认：本 PRD 只更新 handoff / Ralph docs，未删除 old containers、legacy `buff_add()`、legacy `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、`MultiplierData`、`MulData`、`DynamicStatement`、copied-output constructors 或 retained formula snapshots；`StunMul.get_stun_array()` / array outputs、`Calculator.RegularMul` remaining branches、registered-team behavior samples、copied-output handler/report payload parity 与 P2-A through P2-G guarded maintenance 继续留在 same-phase candidate pool。
- [x] Current implementation PRD US-007 Final AM/AP/impact bounded implementation handoff：AP helper convergence 与 impact scalar helper extraction 已完成，AM baseline 保持不变；最终验证为 focused reader pytest `134 passed`、`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `134 passed` / mypy `9 source files` clean、`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `234 passed` / mypy `22 source files` clean。
- [x] Current implementation PRD US-007 same-phase candidate pool：下一默认 PRD 改为 Phase-3 `Calculator.StunMul.get_stun_array()` / array outputs 与 `Calculator.RegularMul` remaining branches 的 oracle / proposal-readiness closure；copied-output handler/report payload parity、registered-team behavior sample eligibility、P2-A through P2-G guarded maintenance 和 retained compatibility 继续保留，不因 AM/AP/impact implementation 完成而删除。
- [x] Current array / RegularMul PRD US-007 final handoff：`Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()`、`Calculator.RegularMul` arrays 与 selected branch matrix 已完成 characterization，US-005 明确 production proposal No-Go；US-006 final serial focused reader pytest `138 passed`、`formula-parity` focused `138 passed` / mypy `9 source files` clean、`calculator-reads` focused `238 passed` / mypy `22 source files` clean；本 handoff 只更新 docs / Ralph artifacts，不改 production / validation-runner / event-runtime source。
- [x] Current array / RegularMul same-phase candidate pool：下一默认 PRD 继续 phase-3 characterization / proposal-readiness continuation，保留 copied-output handler/report payload parity、registered-team behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、`Calculator.StunMul.get_stun_array()` follow-up、P2-A through P2-G guarded maintenance 与 retained compatibility；不得把本轮 characterization evidence 外推为 broad formula replacement。
- [x] Current sheer reader-snapshot PRD US-007 final handoff：`cal_base_attr(..., base_attr=4)` retained oracle、reader-snapshot eligibility No-Go、registered-route sample-condition No-Go、proposal readiness No-Go 和 final serial gates 已同步到 handoff docs；focused reader pytest `139 passed`、`formula-parity` focused `139 passed` / mypy `9 source files` clean、`calculator-reads` focused `239 passed` / mypy `22 source files` clean、`implicit-events` focused `242 passed` / mypy `88 source files` clean。
- [x] Current sheer same-phase candidate pool：下一默认 PRD 继续 phase-3 characterization / proposal-readiness continuation，不能只沿 `RegularMul` sheer conversion 生成 production proposal；copied-output handler/report payload parity、registered-team behavior sample eligibility、remaining `Calculator.RegularMul` branches、`Calculator.StunMul.get_stun_array()` follow-up、P2-A through P2-G guarded maintenance 与 retained compatibility 均继续保留。
- [x] Current copied-output bounded proposal PRD US-008 final handoff：proposal result 为 conditional Go with named blockers for one later bounded copied-output handler/report implementation PRD；下一默认 PRD 可生成该 implementation PRD，但必须保持 one coherent copied-output handler/report slice、focused copied-output pytest、scoped mypy、`formula-parity` / `calculator-reads` / `implicit-events` retained gates、registered-route sample conditions、rollback anchors、stop conditions 和 non-goals。
- [x] Current copied-output bounded proposal same-phase candidate pool：registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、`Calculator.StunMul.get_stun_array()` / array-output follow-up、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留；不得把 conditional Go 外推为 broad `Calculator.py` / `CalAnomaly.py` rewrite、validation-runner rewrite、registered-team fixture creation、old-container deletion、layer merge 或 retained compatibility 删除。
- [x] Current copied-payload handler/report bounded implementation PRD US-008 final handoff：`CopyAnomalyForOutput.py` copied-payload constructor boundary、`UpdateAnomaly.spawn_output(...)` mode boundary、scheduled publish / dot runtime / debuff layer-preservation anchors、handler report payload boundary、scoped mypy coverage 和 registered-route No-Go verdict 已收口。最终验证为 focused copied-output pytest `172 passed`、`formula-parity` focused `140 passed` / mypy `9 source files` clean、`calculator-reads` focused `240 passed` / mypy `22 source files` clean、`implicit-events` focused `247 passed` / mypy `90 source files` clean，以及默认 lifecycle focused `18 passed` / mypy `9 source files` clean。
- [x] Current copied-payload implementation same-phase candidate pool：下一默认 PRD 改为 Phase-3 same-phase candidate selection / bounded proposal PRD；registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、`Calculator.StunMul.get_stun_array()` / array-output follow-up、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Current candidate-selection PRD US-008 final handoff：selected surface 为 `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array output；US-007 retained gates 已通过 focused reader pytest `140 passed`、`formula-parity` focused `140 passed` / mypy `9 source files` clean、`calculator-reads` focused `240 passed` / mypy `22 source files` clean、`implicit-events` focused `247 passed` / mypy `90 source files` clean。Registered behavior sample 仍为 conditional No-Go，只有 future live semantic diff 且真实 registered stun / impact route 在 explicit stop tick 内有 nonzero relevant counts 时才运行；rollback anchors 和 stop conditions 继续绑定 source methods、focused oracle、retained docs、validation profiles、old containers 与 layer-separation invariants。Verdict：Go for one later bounded proposal / implementation PRD only。
- [x] Current candidate-selection same-phase candidate pool：下一默认 PRD 可围绕 selected Stun array output 生成 bounded proposal / implementation package，但 registered sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、`Calculator.StunMul.get_stun_array()` future follow-up、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留；不得把本 Go 外推为 broad `Calculator.py` / `CalAnomaly.py` rewrite、RegularMul 打包、registered-team fixture creation、validation-runner rewrite、old-container deletion、layer merge 或 retained compatibility 删除。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Current Stun array bounded implementation PRD US-008 final handoff：selected implementation 为 implemented / no-op verified at handoff。`Calculator.StunMul.get_stun_array()` 已通过 `_build_stun_multiplier_array(...)` 承担五字段 `np.float64` array construction，`Calculator.cal_stun()` 的一次数组读取与 `np.prod(...)` product consumer 保持不变；US-008 本身只更新 handoff docs / Ralph evidence / bookkeeping，不再改 production source。Verifier evidence 继承本 PRD retained gates：focused reader pytest `141 passed`、`formula-parity` focused reader `141 passed` / mypy `9 source files` clean、`calculator-reads` focused reader `241 passed` / mypy `22 source files` clean；registered behavior sample 仍为 conditional No-Go，只有 future live semantic diff 且真实 registered route 在 explicit stop tick 内有 nonzero relevant counts 时才运行。
- [x] Current Stun implementation same-phase candidate pool：下一默认 PRD 改为 Phase-3 same-phase candidate selection / bounded proposal PRD；registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if new evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Current route reconciliation US-001：stale Stun default 已与最新 handoff 对齐；selected Stun implementation 继续是 implemented / no-op verified，不得在 focused regression、validation failure、root-workspace source evidence 或 named proposal-readiness packet 之外重开。当前默认 PRD 改为 `Calculator.RegularMul` remaining branch matrix / exact candidate or No-Go；copied-output implementation、`cal_res_pen()` selector extraction、AM/AP/impact helper implementation、selected Stun implementation 和 P2-A through P2-G guarded buckets 均是 completed evidence，不是默认实现 backlog。当前 production conclusion 排除 `.codex_worktrees/`、`scripts/ralph/archive/`、`scripts/ralph/run-logs/`、logs 与 generated history。
- [x] Current RegularMul remaining-branch proposal-readiness PRD US-008 final handoff：selected candidate 为 `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `CalculatorBuffAttributeReader.read_personal_crit_damage(context)`；focused oracle gap、proposal boundary、rollback anchors、retained gates、reviewer invariant verdict 和 handoff docs 已收口。Verdict 为 Conditional Go for one later bounded implementation PRD only；later diff 只能保持 `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` 的等价 helper seam，且必须继续排除 `received_crit_dmg_bonus`。
- [x] Current RegularMul retained gates：US-006 serial verifier evidence 为 focused reader pytest `143 passed`、`formula-parity` exited `0` with scoped mypy success on `9 source files` and `[验证完成] 所有步骤通过`、`calculator-reads` exited `0` with scoped mypy success on `22 source files` and `[验证完成] 所有步骤通过`。Known pytest-asyncio / async log-writer shutdown noise 按 exit status 与 success markers 分离，不作为 failure。
- [x] Current RegularMul reviewer / invariant verdict：US-007 reviewer verdict 为 PASS；event queue semantics、synchronous listener broadcasts、same-tick runtime writes、old containers、copied-output constructors、validation-runner behavior、registered teams/APLs、dispatch/runtime/listener/dot/lifecycle layers 和 retained compatibility paths 均未改变。`Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` remains implemented / no-op verified and is not reopened by this handoff。
- [x] Current RegularMul same-phase candidate pool：personal crit damage implementation 已完成并从默认实现 backlog 移出；下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal。registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Current RegularMul proposal-readiness PRD US-008 final evidence：Ralph progress、campaign dashboard、evidence ledger、checkpoint、PRD completion bit 和 handoff docs 已记录 final verifier evidence / next-intake signal。不得重开 completed copied-output、`cal_res_pen()`、AM/AP/impact、selected Stun、current `cal_crit_rate(data)` implementation、P2 guarded buckets 或 phase-1 surfaces，除非 root-workspace source、focused regression、guardrail、validation 或 reviewer-named evidence 给出新证据。
- [x] Current RegularMul proposal-readiness PRD US-009 final closure：Ralph durable evidence / next-intake state 已落盘到 progress、campaign dashboard、evidence ledger、checkpoint、replacement notes、PRD completion bit 和 refreshed state JSON。下一默认 PRD 为 Phase-3 RegularMul personal crit damage bounded implementation PRD，仅限 `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` 的等价 helper seam；registered sample eligibility、remaining RegularMul / retained-only sheer、future Stun evidence、P2 guarded maintenance、retained compatibility 与 blocker-only reopen rules 继续保留为 same-phase pool。
- [x] Current RegularMul personal crit damage implementation PRD US-008 final closure：`Calculator.RegularMul.cal_personal_crit_dmg(data)` 已实现 / no-op verified，rollback anchors 为 public method、`_calculate_personal_crit_damage(...)`、reader anchor、focused crit-family tests、`formula-parity` / `calculator-reads` retained gates、old containers 与 layer-separation invariants。下一默认 route 改为 Phase-3 same-phase candidate selection / bounded proposal，不再继续跟随 personal crit damage；不得重开 completed copied-output、`cal_res_pen()`、AM/AP/impact、selected Stun、current `cal_crit_rate(data)` implementation、P2 guarded buckets 或 phase-1 surfaces，除非 root-workspace source、focused regression、guardrail、validation 或 reviewer-named evidence 给出新证据。
- [x] Current RegularMul personal crit rate proposal-readiness PRD US-008 final handoff：proposal result 为 Conditional Go for one later bounded implementation PRD only，目标限 `Calculator.RegularMul.cal_personal_crit_rate(data)` 与可选 `_calculate_personal_crit_rate(static_statement, dynamic_statement)` helper；必须保持 `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` 并排除 `crit_rate_received_increase`。Rollback anchors 为 public method、future helper if added、reader anchor、focused full/personal crit tests、`formula-parity` / conditional `calculator-reads` gates、old containers 与 layer-separation invariants。
- [x] Current RegularMul personal crit rate same-phase pool：下一默认 route 可生成 bounded personal-crit-rate implementation PRD，但不得继续连锁生成 narrow follow-up；registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Current RegularMul personal crit rate implementation PRD US-008 final closure：`Calculator.RegularMul.cal_personal_crit_rate(data)` 已实现 / no-op verified，rollback anchors 为 public method、`_calculate_personal_crit_rate(...)`、reader anchor、focused full/personal crit tests、`formula-parity` / conditional `calculator-reads` retained gates、old containers 与 layer-separation invariants。下一默认 route 改为 Phase-3 same-phase candidate selection / bounded proposal，不再继续跟随 personal crit rate；不得重开 completed copied-output、`cal_res_pen()`、AM/AP/impact、selected Stun、current `cal_crit_rate(data)` implementation、current `cal_personal_crit_dmg(data)` implementation、P2 guarded buckets 或 phase-1 surfaces，除非 root-workspace source、focused regression、guardrail、validation 或 reviewer-named evidence 给出新证据。
- [x] Current RegularMul full crit damage proposal-readiness PRD US-008 final handoff：selected candidate 为 `Calculator.RegularMul.cal_crit_dmg(data)`；focused label-branch / received-bonus oracle、full-vs-personal contrast boundary、proposal boundary、rollback anchors、retained gate evidence、reviewer invariant verdict 和 handoff docs 已收口。Verdict 为 Conditional Go for one later bounded implementation PRD only；later diff 只能是等价 module-local helper seam，且必须继续包含 `received_crit_dmg_bonus`、`aftershock_attack` label bonus 和 `min(5, crit_dmg)` cap。
- [x] Current full crit damage same-phase pool：下一默认 route 可生成 bounded full-crit-damage implementation PRD，但不得把 route 折叠成 single-branch-only automation；registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 均继续保留。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- [x] Current RegularMul full crit damage implementation PRD US-008 final closure：`Calculator.RegularMul.cal_crit_dmg(data)` 已实现 / no-op verified，rollback anchors 为 public method、`_calculate_full_crit_damage(...)`、focused full-crit oracle rows、full-vs-personal contrast tests、`Calculator.py`、`test_buff_attribute_reader.py`、retained `formula-parity`、conditional `calculator-reads`、old containers 和 layer-separation invariants。下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal；same-phase pool 继续保留 registered sample eligibility、remaining RegularMul / retained-only sheer、future Stun evidence、P2 guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- [x] Current route and completed surfaces reconciliation US-001：current-root docs、`migration-board.json` 与 `hotspots.json` 对齐到 Phase-3 same-phase candidate selection / bounded proposal。copied-output handler/report implementation、`Calculator.AnomalyMul.cal_res_pen()` selector extraction、AM/AP/impact helper implementation、selected Stun array implementation、full crit rate、personal crit rate、personal crit damage 和 full crit damage 均记录为 completed / no-reopen surfaces；除非 focused regression、validation failure、root-workspace source evidence、guardrail 或 reviewer-named evidence 明确命名，否则不得作为默认实现 follow-up 重开。当前结论排除 `.codex_worktrees/`、`scripts/ralph/archive/`、`scripts/ralph/run-logs/`、logs、generated history 与 historical worktree evidence。
- [x] 若后续 validation 或 guardrail 重新暴露阶段 1 blocker，下一轮 PRD 只处理 blocker package 中列出的具体文件、符号、失败测试、失败 guardrail 或验证命令；不得重开已删除的 `event_list` surface 或已闭合的 producer batch，除非 guardrail 给出新的生产证据。
