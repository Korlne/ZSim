# Buff重构下阶段计划草稿

## 当前状态

- 当前总路线已重置。
- 当前默认阶段仍在阶段 2 收口；阶段 1 基础设施解耦已由 `PRD-12 US-024` 关闭，阶段 2 全量分类、P2-A AM/AP reader + computed count state-sync、P2-B crit / impact reader、P2-C trigger-state read-only gates、P2-D scheduled publish ordering / adapter parity、P2-E dot runtime-state / initialization、P2-F BuffAddStrategy caller / facade-write design 与 P2-G direct simulator context helpers 均已完成 guarded scope。
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
- 2026-06-08 阶段 2 第一轮分类 PRD 已完成：`docs/BuffXLogic阶段2全量分类与复用矩阵.md` 现在持有非排他分类 schema、149 个 root-workspace `BuffXLogic` census、helper / record / reader / event-adapter / state-sync / handler / listener pattern catalog、风险矩阵与 ranked follow-up pool。
- 当前默认下一 Ralph PRD 仍沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段顺序推进；US-012 已完成阶段 2 closure / phase-3 formula snapshot readiness decision，下一轮默认转为“phase-3 formula parity suite design / characterization”。该默认 PRD 只设计和刻画公式一致性套件，不做 production formula replacement，不回退到角色驱动式单文件薄切片，也不跳过 parity contract 去改 `Calculator` / `CalAnomaly` 公式。

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

`Phase-3 formula parity suite design / characterization（production formula replacement 仍 No-Go）`

### 本轮已消解的耦合点

- XLogic 全量分类不再是空白项：已完成 root-workspace 149 模块 census、infrastructure / leaf 分离、class / record / public method 元数据、可复现 `rg` pattern counts 和 CodeGraph 导航说明。
- 分类轴已固定为非排他：属性读取、事件触发、record / count 写回、anomaly / debuff / dot bypass、`sim_instance` service-location、Calculator / CalAnomaly formula snapshot、listener broadcast、scheduled publish、runtime immediate write、retained compatibility only。
- 第一轮复用目录已形成：`BuffAttributeReader` helper family、record object catalog、state-sync helper、scheduled event adapter、runtime command / facade、handler pattern、listener pattern、dot / bypass runtime-state adapter、explicit context helper 和 validation entrypoints。
- 风险矩阵已给出 behavior risk、ordering risk、validation coverage、runtime-boundary risk、rollback complexity 与 likely follow-up PRD size；下一轮不再需要先做一遍全量分类。
- P2-A 已完成：六个 AM/AP read-then-writeback 文件改为 `create_anomaly_attribute_read_context(...)` + `CalculatorBuffAttributeReader.read_anomaly_mastery(...)` / `read_anomaly_proficiency(...)`，并由 reader parity、state-sync order、source guardrail 和 validation profiles 覆盖。
- P2-A source guardrail 已阻断六个迁移文件回退到 direct `MultiplierData`、`MultiplierData as Mul`、`Mul(...)` 或 direct `Calculator.AnomalyMul.cal_am/cal_ap(...)` / `Cal.AnomalyMul.cal_am/cal_ap(...)`。
- P2-A 最终验证已通过：focused pytest `45 passed`，`calculator-reads` profile base `2 passed` / isolated teams `3 passed` / focused `63 passed` / mypy `20 source files` clean，`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `105 passed` / mypy `76 source files` clean。
- P2-B 已完成：`LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py`、`CannonRotor.py`、`MiyabiCoreSkill_IceFire.py` 与 `WoodpeckerElectroSet4_*` 九个 root 文件已改用 `CalculatorBuffAttributeReader.read_impact(...)` / `read_full_crit_rate(...)` / `read_personal_crit_rate(...)` / `read_personal_crit_damage(...)`。
- P2-B 已由 reader parity、state-sync order、full-crit event-adjacent tests、file-specific dispatch tests、`tests/simulator/test_migrated_p2b_reader_guardrail.py` 与 `.codex_worktrees/` 排除 guardrail 覆盖；retained Calculator / CalAnomaly formula snapshots 仍允许。
- P2-B 最终验证已通过：focused pytest `107 passed`，`calculator-reads` profile base `2 passed` / isolated teams `3 passed` / focused `129 passed` / mypy `22 source files` clean，`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `136 passed` / mypy `77 source files` clean；`莱特火属性队` stop-tick 600 consistency sample `matches=true`，总伤 `646446.67` vs `646446.67`，event count `19` vs `19`，buff timeline 差异为零。
- P2-C 已完成：`TriggerBuffState` / `read_trigger_buff_state(record)` 建立旧模板 trigger Buff state 只读快照，`FlamemakerShakerApBonus.py`、`SpectralGazeImpactBonus.py`、`SharpenedStingerAnomalyBuildupBonus.py`、`CordisGerminaSNAAndQIgnoreDefense.py` 与 `AstralVoice.py` 已迁移到 helper，并保留 `check_preparation(..., trigger_buff_0=...)`、旧模板 Buff identity 与 `history.record` lazy init。
- P2-C 已由 `tests/simulator/test_trigger_state_read_only_gates.py`、`tests/simulator/test_migrated_p2c_trigger_state_guardrail.py` 与 `implicit-events` 覆盖；guardrail 只扫描五个已迁移 root 文件并排除 `.codex_worktrees/`，不阻断剩余 `trigger_buff_0=` pool。
- P2-C 最终验证已通过：`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `181 passed` / mypy `80 source files` clean；`席德大安比队` stop-tick 1000 consistency sample `matches=true`，总伤 `5744827.24` vs `5744827.24`，event count `50` vs `50`，buff timeline 差异为零。
- P2-D 已完成 guarded scope：`tests/simulator/test_schedule_dispatch.py` 锁定 `create_schedule_dispatch_port(...)` 当前队列绑定、event-list rebinding 和 queue-only public API；resource-refresh、`SkillNode` / `LoadingMission`、stateful anomaly / dot、fan-out / multi-publish focused tests 覆盖 payload fields、target fan-out、priority / execute-tick、source-specific order 与 no-publish branches。
- P2-D source guardrail 已由 `tests/simulator/test_migrated_p2d_scheduled_publish_guardrail.py` 锁定 exact root migrated producer set，排除 `.codex_worktrees/`，阻断 raw queue access、legacy event-list discovery、`event_list` preparation requests 和 long-lived cached dispatch adapters。
- P2-D 最终验证已通过：`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `194 passed` / mypy `81 source files` clean；本 PRD 未改 root production behavior，main-loop consistency sample 因无 live scheduled-publish order change 而跳过。
- P2-E 已完成 guarded scope：`DotRuntimeStateAdapter` 锁定 runtime dot list 的 snapshot / find / active find / register / replace / remove 语义，Vivian dot gates、`UpdateAnomaly.anomaly_effect_active(...)` replacement、`remove_dots_cause_disorder(...)` removal 与 freeze follow-up 已迁移到 helper 或 guarded caller-owned 分层；`DotInitializationReadContext` 显式承接 `Shock.DotFeature.__post_init__()` 的 Rina passive duration reads。
- P2-E source guardrail 已由 `tests/simulator/test_migrated_p2e_dot_runtime_guardrail.py` 锁定 exact root migrated file set，排除 `.codex_worktrees/`，阻断 raw scheduler queue 写入 / deleted discovery surfaces、错误 scheduled publish、第二 same-tick write facade、`BuffRuntimeReadPort` 写 API 与 Shock direct retained read 回流。
- P2-E 最终验证已通过：`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `217 passed` / mypy `86 source files` clean；本 PRD 通过 parity-tested helper migration 与 exact-file guardrail 保持 live duration / tick / damage / timeline 语义不变，main-loop consistency sample 因无 live semantic change 而跳过。
- P2-F 已完成 guarded scope：caller taxonomy 与 focused tests 覆盖 `BuffAddStrategy` active replacement、enemy mirror sync、selected-target fan-out、Hugo / Roaring Ride / Seed / `UpdateAnomaly` / BattleEventListener / Character manager representatives、cross-layer semantics 和 no-pending-queue-write behavior；`tests/simulator/test_migrated_p2f_buff_add_strategy_guardrail.py` 已接入 `implicit-events`，阻断 scheduled queue conversion、listener broadcast conversion、第二 write facade、raw pending / active / mirror 写入和 `BuffRuntimeReadPort` write API 回流。
- P2-F 最终验证已通过：uncovered caller focused pytest 串行通过，`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `229 passed` / typecheck clean；本 PRD 没有改 root production behavior，main-loop consistency sample 因 test-only caller / guardrail evidence 而跳过。
- P2-G 已完成 guarded scope：Yuzuha tick / preload / next-character / report-state、enemy context、listener lookup、RNG service、report-state representative 与 exact-file / selected-symbol source guardrail 均由 focused tests 覆盖；没有抽取 universal simulator context helper。
- P2-G 最终验证已通过：changed focused pytest `67 passed`，`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean，`calculator-reads` profile base `2 passed` / isolated teams `3 passed` / focused `133 passed` / mypy `22 source files` clean；本 PRD 未改 root production behavior，main-loop consistency sample 因无 live semantic change 而跳过。
- US-012 已把 phase-3 production formula replacement 判定为 No-Go：下一轮只能设计 / characterization 公式 parity suite，不能新增 production formula rewrite、不能删除 retained formula snapshots，也不能新增未命名 pytest / mypy targets 的 validation profile。

### 本轮未解决或新暴露的耦合点

- P2-G direct simulator context helpers 已补齐为 completed guarded bucket；P2-A through P2-G 没有剩余同阶段默认实现 backlog。
- Phase-3 formula parity suite design、P2-D / P2-E / P2-F / P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 都保留为后续候选块，不能因为 P2-G 或 readiness decision 已完成就从候选池删除。
- P2-A / P2-B / P2-C / P2-D / P2-E / P2-F / P2-G 不再作为默认实现 backlog；后续只在 source guardrail、reader parity、trigger-state no-write / order tests、dispatch tests、dot runtime-state guardrails、P2-F forced-write guardrail、P2-G direct-context guardrail 或 validation profile 暴露具体回归时开窄 blocker。
- Formula snapshots、CalAnomaly internals、old containers、legacy `buff_add()` / `KickOutBuff()` 和 deleted raw queue discovery surfaces 仍是 retained compatibility / phase-3 / blocker-only 项，不是下一轮默认替换目标。
- US-012 决定：phase-3 formula snapshot replacement 的 production implementation 当前 No-Go；只允许进入下一轮 formula parity 设计 / characterization PRD，不允许直接替换 `Calculator` / `CalAnomaly` 公式。验证 wiring 本轮不改，继续用 `calculator-reads` + focused characterization tests 作为 formula-readiness gate，并用 `implicit-events` 保留事件 / runtime 边界回归。

### 已确认事件 / 上下文 / 顺序约束

- P2-A / P2-B 已用 focused tests 锁定 reader parity 与 `simple_start(...)`、`dy.count`、`update_to_buff_0(...)` 相对顺序；维护已迁移文件时先跑对应 source guardrail 和 focused order tests，不能只看 reader 表达式。
- full crit rate helper 已保留 `crit_rate_received_increase` 语义；personal crit rate / damage helper 不包含 received crit。后续 full / personal crit 维护仍不得合并语义，AP-to-crit-rate 文件也不能误归入 personal crit reader。
- P2-C helper 维护必须保持 `BuffRuntimeReadPort` 只读；P2-D 维护必须保持 `ScheduleDispatchPort` queue-only 语义，不在 scheduled publish parity 故事里新增 raw queue、old-container 删除或 same-tick runtime write facade。
- P2-E guarded maintenance 必须保持 dot runtime registration / removal 与 scheduled queue publish 分层；`enemy.dynamic.dynamic_dot_list` 仍是 runtime dot state，只有已有 scheduled follow-up payload 继续走 `ScheduleDispatchPort`。
- P2-F guarded maintenance 必须保持 `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` 为 forced same-tick Buff / Debuff write 边界；不得把 Buff / Debuff write 转成 `ScheduleDispatchPort` backlog、listener broadcast 或新的第二写 facade。
- P2-G guarded maintenance 必须继续按具体服务拆分 direct simulator context：tick / preload / char-data / enemy / listener / RNG / report-state 不能混成一个 adapter，也不能伪装成 `LegacyBuffRuntimeFacade` 替换。
- `LoadingMission.mission_start(...) -> ScheduleDispatchPort.publish_scheduled(...)`、publish 后 record reset、payload target / priority / fan-out 等 order 证据已由 scheduled-publish focused tests 保护；维护 P2-D 时先跑 exact-file guardrail 和 file-specific dispatch tests。
- listener broadcast、scheduled queue publish、dot runtime registration / removal、runtime immediate write 是四层边界；下一轮不得合并为一个 event bus。
- `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 仍是唯一 same-tick command boundary；`BuffRuntimeReadPort` 保持只读，不扩成 write API。
- `.codex_worktrees/` 仍只作为历史 worktree 快照；PRD blocker 必须回到 root-workspace source、focused tests 和 validation profiles。
- validation profiles 必须串行执行；P2-B 已用真实注册 `莱特火属性队` 样本证明 Lighter / Trigger route baseline 与 candidate 一致，P2-C 已用真实注册 `席德大安比队` 样本证明 `机巧心种` + `索魂影眸` route baseline 与 candidate 一致。P2-D / P2-E / P2-F 未改 live production semantics，已明确跳过 behavior sample；后续 P2-G / direct context 候选只有在存在真实注册代表队且故事触达 live 行为时才运行 behavior sample。

### 行为样本决策矩阵

| 后续故事类型 | 是否运行 `scripts/run_buff_main_loop_consistency.py` | 判定规则 |
| --- | --- | --- |
| 文档、分类、guardrail 或 test-only 变更 | 不运行，除非同一 story 也改生产语义 | 用 focused characterization、source guardrail、`calculator-reads` / `implicit-events` 串行验证作为证据；在 progress 里记录跳过原因。 |
| 已完成 P2-A through P2-G 的 guarded maintenance | 仅当 guardrail / focused test / validation 指向具体生产回归，且真实注册队伍覆盖该 live route 时运行 | 不为了补样本而创建 validation-only team；无注册队伍时记录缺口并以 focused tests + validation profile 收口。 |
| phase-3 formula snapshot replacement 或 formula-output parity | 若 story 实际改 `Calculator.py`、`CalAnomaly.py`、`AnomalyBar.current_ndarray`、copied anomaly / disorder ratio 或输出数值语义，且有真实注册队伍能跑到目标 route，则运行 | main-loop sample 只作为 live behavior 证据；仍必须先有 focused formula parity suite、候选文件、rollback plan 和 validation entrypoint。 |
| phase-3 readiness / go-no-go 决策但不改生产公式 | 不运行 | 只记录样本要求、注册队伍覆盖状态和缺口；不得把 CLI label 当 live runtime switch。 |

已有成功样本只证明各自 route：

- `莱特火属性队` stop-tick 600 证明 P2-B Lighter / Trigger / Hugo route 在该样本下 baseline 与 candidate 的总伤、event count 和 buff timeline 一致；它不证明 Alice / Yuzuha / Jane / Vivian / Yanagi，也不证明 Calculator / CalAnomaly 公式可删除。
- `席德大安比队` stop-tick 1000 证明 P2-C `机巧心种` + `索魂影眸` route 在该样本下 baseline 与 candidate 一致；它不证明 P2-A AM/AP、P2-D scheduled publish、P2-E dot runtime、P2-F forced write、P2-G direct context 或 phase-3 formula replacement。
- 当前真实注册队伍为 `青衣雷属性队`、`席德大安比队`、`莱特火属性队`、`薇薇安物理队`。Alice / 爱丽丝、Yuzuha / 柚叶、Jane / 简 目前没有注册代表队；Vivian / 薇薇安 与 Yanagi / 柳 有 `薇薇安物理队`，但本文档尚未记录通过的 main-loop consistency 样本，后续只能在 APL 确认触达目标 formula / output route 后使用。

### 阶段 2 同阶段候选池

#### 候选块 P2-A：AM/AP reader + computed count state-sync（已完成 / guardrail 维护）

- 候选文件 / 符号：`AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`、`YuzuhaAdditionalAbilityAnomalyDmgBonus.py`、`JaneCinema1APTransToDmgBonus.py`、`JaneCoreSkillStrikeCritRateBonus.py`、`JanePassionStateAPTransToATK.py`、已有 AM / AP reader samples。
- 当前状态：六个文件已从 direct `MultiplierData` / alias reads 迁到 AM/AP reader seam；`dynamic_buff_list` 只作为 `BuffAttributeReadContext.active_buff_view` 输入保留，computed count writeback 顺序由 focused tests 和 source guardrail 保护。
- 可拆工作方向：不再作为默认实现 backlog；后续只在 source guardrail、focused parity/order tests 或 validation profile 暴露具体回归时开 blocker 修复。
- 必须保留：`MultiplierData` formula snapshot、old `buff_0` identity、record fields、state-sync order。
- 验证入口：`calculator-reads` 与 `implicit-events` 已通过；维护时先跑 `tests/simulator/test_migrated_am_ap_reader_guardrail.py`、`tests/simulator/test_buff_attribute_reader.py`、`tests/simulator/test_buff_attribute_state_sync.py`。
- 非目标：不做 scheduled publish 迁移，不重写 Calculator 公式，不删除旧容器。

#### 候选块 P2-B：crit / impact reader family package（已完成 / guardrail 维护）

- 候选文件 / 符号：`LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py`、`CannonRotor.py`、`MiyabiCoreSkill_IceFire.py`、`WoodpeckerElectroSet4_*`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py`。
- 当前状态：九个 root 文件已迁移到 impact / full crit / personal crit reader seam；source guardrail 阻断 direct `MultiplierData` / `Mul(...)` / direct impact 或 crit Calculator reads 回流。
- 可拆工作方向：不再作为默认实现 backlog；仅在 `tests/simulator/test_migrated_p2b_reader_guardrail.py`、focused reader/state-sync/full-crit tests、file-specific dispatch tests 或 validation profile 暴露回归时开 blocker。
- 必须保留：full crit 包含 received crit；personal crit 不包含 received crit；已有 event publishers 保持 `ScheduleDispatchPort`，retained Calculator / CalAnomaly formula snapshots 不删除。
- 验证入口：维护时跑 `calculator-reads`；event-adjacent 维护加 `implicit-events` 与 file-specific dispatch tests。
- 非目标：不把 full / personal crit 语义合并，不把 P2-B guardrail 扩成阻断 P2-C / P2-D / P2-E / P2-F。

#### 候选块 P2-C：trigger-state read-only gates（已完成 / guarded scope）

- 候选文件 / 符号：`AstralVoice.py`、`FlamemakerShakerApBonus.py`、`CordisGerminaSNAAndQIgnoreDefense.py`、`SpectralGazeImpactBonus.py`、`SharpenedStingerAnomalyBuildupBonus.py`、`trigger_buff_0=` 相关文件。
- 当前状态：五个 root migrated files 已经通过 `read_trigger_buff_state(record)` 读取 `active`、`count`、`built_in_buff_box`；`AstralVoice.special_effect_logic(...)` 的 count mirror 保留 `simple_start(...) -> current dy.count -> update_to_buff_0(self.buff_0)` 顺序。
- 可拆工作方向：不再作为默认实现 backlog；后续只在 migrated-file guardrail、focused no-write / count-mirror tests、`implicit-events` 或行为样本暴露回归时开 blocker。剩余未迁移 `trigger_buff_0=` pool 仍保留给后续独立分类，不由 P2-C guardrail 自动阻断。
- 必须保留：`BuffRuntimeReadPort` 只读语义、旧模板身份、`check_preparation(..., trigger_buff_0=...)` / `trigger_buff_0_handler(...)` 兼容路径、`JudgeTools.find_exist_buff_dict(...)` lookup。
- 验证入口：维护时跑 `tests/simulator/test_trigger_state_read_only_gates.py`、`tests/simulator/test_migrated_p2c_trigger_state_guardrail.py` 与 `implicit-events`。
- 非目标：不在 `BuffRuntimeReadPort` 上加写 API，不删除 old containers，不把 P2-C guardrail 扩展到未迁移 trigger-state pool。

#### 候选块 P2-D：scheduled publish ordering / adapter parity（已完成 / guarded scope）

- 候选文件 / 符号：`CannonRotor.py`、`HugoCorePassiveTotalizeTrigger.py`、`YixuanCinema1Trigger.py`、`VivianDotTrigger.py`、`YanagiPolarityDisorderTrigger.py`、`ElegantVanitySpRecover.py`、`SliceofTimeExtraResources.py`、`UpdateAnomaly.update_anomaly(...)`、`DecibelManager`、`BreakingLegManager`、`Character/Yuzuha` cinema-6 energy。
- 当前状态：payload fields、target fan-out、priority / execute-tick、`LoadingMission.mission_start(...)`、publish-before/after-reset、adapter rebinding 与 no-publish branches 已由 focused tests 覆盖；exact-file source guardrail 阻断 raw queue / stale adapter regression。
- 可拆工作方向：不再作为默认实现 backlog；后续只在 exact-file P2-D guardrail、file-specific dispatch tests 或 `implicit-events` validation 暴露具体回归时开 blocker 修复。
- 必须保留：`ScheduleDispatchPort` queue-only boundary、adapter 按需创建、listener broadcast 分层、dot runtime registration 分层、runtime write 分层。
- 验证入口：维护时跑 `tests/simulator/test_migrated_p2d_scheduled_publish_guardrail.py`、相关 file-specific dispatch tests 与 `implicit-events`。
- 非目标：不重开 raw queue，不扩展 P2-D guardrail 去阻断 P2-E / P2-F / P2-G，不把 dot runtime registration 改成 planned-event backlog。

#### 候选块 P2-E：dot runtime-state and initialization（已完成 / guarded scope）

- 候选文件 / 符号：`VivianDotTrigger.py`、`VivianCinema1Debuff.py`、`Shock.DotFeature.__post_init__()`、`UpdateAnomaly.anomaly_effect_active(...)`、`remove_dots_cause_disorder(...)`。
- 当前状态：Vivian dot gates、Shock duration init read、`UpdateAnomaly` dot replacement / removal 和 freeze follow-up 分层已由 helper / focused tests / exact-file guardrail 覆盖；`DotRuntimeStateAdapter` 与 `DotInitializationReadContext` 已落地。
- 可拆工作方向：不再作为默认实现 backlog；后续只在 P2-E exact-file guardrail、focused dot tests 或 `implicit-events` validation 暴露具体回归时开 blocker 修复。
- 必须保留：`enemy.dynamic.dynamic_dot_list` runtime state；`ScheduleDispatchPort` 只负责 scheduled payload；Buff / Debuff writes 留在 existing `buff_add_strategy(...)` / facade paths。
- 验证入口：维护时跑 `tests/simulator/test_dot_runtime_state_adapter.py`、`tests/simulator/test_dot_runtime_initialization.py`、`tests/simulator/test_vivian_dot_trigger_dispatch.py`、`tests/simulator/test_update_anomaly_dispatch.py`、`tests/simulator/test_migrated_p2e_dot_runtime_guardrail.py` 与 `implicit-events`。
- 非目标：dot runtime registration 不是 planned-event backlog；不新增第二套 runtime write facade；不重写 `Shock.DotFeature` duration formula 或 `CalAnomaly` 公式。

#### 候选块 P2-F：BuffAddStrategy caller / facade-write design（已完成 / guarded scope）

- 候选文件 / 符号：`zsim/sim_progress/Buff/BuffAddStrategy.py`、`HugoCorePassiveTotalizeTrigger.py`、`RoaringRideBuffTrigger.py`、`Seed*Trigger.py`、`UpdateAnomaly.anomaly_effect_active(...)`、BattleEventListener callers、Character manager callers。
- 当前状态：caller taxonomy、facade contract tests、representative caller tests、cross-layer semantics 与 exact-file P2-F guardrail 已完成；forced same-tick Buff / Debuff writes 仍经 `buff_add_strategy(...)` 与 `LegacyBuffRuntimeFacade`，target fan-out、active replacement、enemy mirror sync、template identity 和 no pending queue write 均有 focused coverage。
- 可拆工作方向：不再作为默认实现 backlog；后续只在 P2-F guardrail、caller focused tests、raw-container guardrail 或 `implicit-events` validation 暴露具体回归时开 blocker 修复。
- 必须保留：现有 `LegacyBuffRuntimeFacade`、old registry/template identity、唯一 write facade 规则、同步 listener broadcast / scheduled publish / runtime command / read-only runtime view 分层。
- 验证入口：维护时跑 `test_buff_add_strategy_runtime_facade.py`、`test_bypass_layer_semantics.py`、P2-F caller-family tests、`test_migrated_p2f_buff_add_strategy_guardrail.py` 与 `implicit-events`；触达 lifecycle 才跑默认 profile。
- 非目标：不新增第二套 write facade，不转换成 scheduled publish，不删除 legacy `buff_add()` / `KickOutBuff()`，不把 P2-G direct simulator context helper 并入 P2-F。

#### 候选块 P2-G：direct simulator context helpers（已完成 / guarded scope）

- 候选文件 / 符号：`YuzuhaHardCandyShotTrigger.py`、`YuzuhaCinema4QuickAssistTrigger.py`、`YuzuhaCinema6SheelTrigger.py`、`YuzuhaCinema2Trigger.py`、`YuzuhaSugarBurstAnomalyBuildupBonus.py`、`YixuanAdditionalAbilityDmgBonus.py`, `HeartstringNocturne.py`, `CannonRotor.special_judge_logic()`, `WoodpeckerElectroSet4_*`, `AstraYaoCorePassiveAtkBonus.py`, report-only `change_process_state()` files。
- 当前状态：service-family focused tests 与 `tests/simulator/test_migrated_p2g_direct_context_guardrail.py` 已覆盖 selected representatives；没有证据支持抽取 universal simulator context helper。
- 可拆工作方向：不再作为默认实现 backlog；后续只在 P2-G guardrail、focused branch tests 或 `implicit-events` validation 暴露具体回归时开 blocker。若未来重复同一服务模式且 helper 能减少真实复杂度，再开单服务 helper PRD。
- 必须保留：local preload、Character action / resource、listener broadcast、report state、RNG 与 scheduled publish / runtime write 的分层。
- 验证入口：维护时跑 P2-G focused tests、`tests/simulator/test_migrated_p2g_direct_context_guardrail.py` 与 `implicit-events`；触达真实队伍行为时再选 registered main-loop consistency sample。
- 非目标：不是 `LegacyBuffRuntimeFacade` 替换，不是 raw queue backlog，不迁移 Calculator formula，不把不同 direct services 合并成一个 adapter。

#### 候选块 Phase-3：formula parity suite design / characterization（当前默认 / 不替换生产公式）

- 候选文件 / 符号：`zsim/sim_progress/ScheduledEvent/Calculator.py` (`Calculator`, `MultiplierData`, `DynamicStatement`, `cal_am`, `cal_ap`, `cal_imp`, `cal_crit_rate`, `cal_personal_crit_rate`, `cal_personal_crit_dmg`)、`zsim/sim_progress/ScheduledEvent/CalAnomaly.py` (`CalAnomaly`, `MulData`)、`zsim/sim_progress/anomaly_bar/AnomalyBarClass.py` (`current_ndarray`)、`zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`、`zsim/sim_progress/Update/UpdateAnomaly.py`，以及 `docs/BuffXLogic阶段2全量分类与复用矩阵.md` 中已列明的 AM/AP、impact、crit、anomaly ratio / copied output、enemy anomaly-state read 候选。
- 当前耦合：公式快照定义伤害与异常数值，当前 reader seams 只隔离部分 XLogic 属性读取，不等价于公式替换。
- US-012 Go / No-Go：phase-3 production formula replacement 当前 No-Go；下一轮只 Go 到 parity suite 设计 / characterization。不得新增 `formula-readiness` / `formula-parity` validation profile，直到 focused pytest 与 scoped mypy targets 已在 PRD 中逐项命名。
- 当前默认 Ralph-sized 工作方向：建立公式 parity suite contract，按候选域列出 focused characterization / parity tests、scoped mypy targets、behavior-sample 触发条件、rollback plan 和 non-goals；覆盖 Calculator 属性公式、CalAnomaly / anomaly bar snapshot、copied anomaly / disorder 输出数值、enemy anomaly-state read helpers 和已迁移 reader seam 的回归样本。通过前不得改 production formula。
- 必须保留：`MultiplierData` / `MulData` formula snapshots、`AnomalyBar.current_ndarray`、Calculator / CalAnomaly formulas。
- 验证入口：当前 gate 仍是 `calculator-reads` + existing focused characterization tests；触达事件 / runtime / dispatch boundary 时追加 `implicit-events`。未来若确实新增 formula parity profile，必须先列出 pytest targets、mypy targets、`--help` 验证和仍需保留的 `calculator-reads` / `implicit-events` 串行验证。
- 行为样本规则：本 readiness / go-no-go story 不跑 main-loop sample；未来 production formula 或 formula-output 语义变更只有在真实注册队伍能触达目标 route 时才跑 `scripts/run_buff_main_loop_consistency.py`，否则记录注册队伍缺口并用 focused parity tests 收口。
- 回滚计划：保留现有 formula snapshots 和 old compatibility paths 作为 rollback anchor；若未来 parity profile、reader helper 或 formula replacement 失败，回退该 helper / profile / formula diff，继续走 `MultiplierData` / `MulData` / `AnomalyBar.current_ndarray` / existing Calculator / CalAnomaly formulas，不删除 old containers 或 legacy Buff write paths。
- 非目标：不在 phase-2 scheduled publish / trigger-state / dot runtime-state / context helper PRD 中重写公式；不把 CLI label 当 live runtime switch；不删除 old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 或 `LegacyBuffRuntimeFacade`。

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
- 若维护已完成 P2-D scheduled publish ordering / adapter parity bucket，必须保留 exact-file source guardrail、file-specific dispatch tests、adapter 按需创建与 `ScheduleData.reset_myself()` 后 event_list rebinding 证据；不要把 guardrail 扩成阻断 P2-E / P2-F / P2-G，也不要新增 raw queue passthrough 或 runtime write facade。
- 若维护已完成 P2-E dot runtime-state / initialization bucket，必须保留 exact-file source guardrail、runtime-list helper parity、Shock duration read helper parity、Vivian / UpdateAnomaly focused tests 与 scheduled follow-up 分层证据；不要把 guardrail 扩成阻断 P2-F / P2-G，也不要把 dot runtime state 转成 planned-event backlog。
- 若维护已完成 P2-G direct simulator context helpers bucket，必须保留 service-family guardrail、focused branch tests 与 `.codex_worktrees/` 排除；触达 preload schedule、Character action/resource、listener/report/RNG 或 live behavior semantics 时追加对应 file-specific pytest，只有真实注册代表队存在且 live behavior 变化时才运行 main-loop consistency sample。
- 若采用当前默认 phase-3 formula parity suite design / characterization PRD，必须先从本文件的 Phase-3 候选块和 `docs/BuffXLogic阶段2全量分类与复用矩阵.md` 的 formula-readiness 证据取材，产出 candidate files、focused pytest targets、scoped mypy targets、validation entrypoints、behavior-sample 条件、rollback plan 和 non-goals；不得在这些契约落地前改 production formula。
- US-012 后的 validation decision：本轮不新增 validation profile；下一轮若只做 phase-3 parity 设计 / characterization，继续跑 `calculator-reads`、`implicit-events` 和需要的 focused characterization tests。只有实际新增 formula parity profile 或验证命令契约时，才更新 `scripts/run_buff_refactor_validation.py`，并补跑 `--help`、新增 profile、`calculator-reads` 与 `implicit-events`。
- 若维护已完成 P2-A / P2-B / P2-C 文件，必须保留 migrated-source guardrail 范围和 `.codex_worktrees/` 排除，不得把 guardrail 扩成阻断未迁移 P2-D / P2-E / P2-F / P2-G 候选。
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
- [BuffXLogic阶段2全量分类与复用矩阵.md](./BuffXLogic阶段2全量分类与复用矩阵.md)
  重点先看 `US-008 复用模式目录与风险矩阵`、`Ranked follow-up pool`、P2-A / P2-B / P2-C / P2-D / P2-E / P2-F / P2-G completion updates 和 phase-2 closure / phase-3 readiness 的 next pool state。
- [Buff系统重构Checklist.md](./Buff系统重构Checklist.md)
- `scripts/ralph/progress.txt`
  重点先看 `## Codebase Patterns`

## Phase 2 分类 PRD 后的下一轮调查提纲

阶段 2 第一轮已完成“XLogic 全量分析与复用收敛”的分类与设计产物，P2-A AM/AP reader + computed count state-sync package、P2-B crit / impact reader family package、P2-C trigger-state read-only gates、P2-D scheduled publish ordering / adapter parity、P2-E dot runtime-state / initialization、P2-F BuffAddStrategy caller / facade-write design 和 P2-G direct simulator context helpers 均已完成 guarded scope。下一轮 PRD 不再重复 census，也不继续沿已迁移 AM/AP、impact / crit、trigger-state、scheduled-publish、dot runtime-state、forced Buff write 或 direct simulator context 文件做薄切片；当前默认应做 phase-2 closure / phase-3 formula snapshot readiness decision：

- P2-A through P2-G 哪些 guardrail / focused tests / validation profiles 已证明 completed bucket，不应继续生成默认 implementation backlog。
- 是否还有同阶段候选必须由 root-workspace source scan、guardrail failure、focused test failure 或 validation profile failure 证明；没有证据时，只保留 guarded maintenance / blocker-only follow-up。
- Phase-3 formula snapshot replacement 的候选文件、公式边界、parity suite、validation profile、registered behavior-sample 条件和 rollback plan 应如何定义。
- Calculator / CalAnomaly / `MultiplierData` / `MulData` formula snapshots、`AnomalyBar.current_ndarray` 与 retained XLogic compatibility snapshot 哪些必须保留到 phase-3 readiness 明确后再动。
- P2-G direct context 行为仍必须继续分层为 local preload、Character action/resource、listener broadcast、report state、RNG、scheduled publish 或 runtime write，不能在 phase-3 readiness PRD 中混成新的 `LegacyBuffRuntimeFacade`、`ScheduleDispatchPort` backlog、listener replacement 或第二 write facade。
- 下一轮 validation 至少复核 `implicit-events`；若 readiness PRD 触达 Calculator / formula scope，应追加 `calculator-reads` 或先定义新的 formula parity suite；只有 live behavior semantic changes 才运行真实注册 main-loop consistency sample。

## 每次更新本文档时必须补充的内容

- 本轮 PRD 消解了哪些耦合点。
- 本轮 PRD 没解决但暴露出来的新耦合点。
- 本轮 PRD 新增或确认了哪些事件类型、事件上下文与事件顺序约束。
- 下一轮 PRD 开始前必须先看的文件。
- 下一轮 PRD 的非目标。
