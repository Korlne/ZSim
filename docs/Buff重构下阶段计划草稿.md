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
- 当前默认下一 Ralph story 仍沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段顺序推进；US-012 已完成阶段 2 closure / phase-3 formula snapshot readiness decision，US-014 已新增 scoped `formula-parity` profile，US-015 已同步 handoff docs 与下一候选池，US-016 已完成 final serial validation / Go / No-Go，US-025 已给出 serial gate green evidence，US-026 完成最终 handoff，replacement blocker closure PRD 已把 `Calculator.AnomalyMul.cal_res_pen()` 收敛为唯一 proposal-eligible bounded domain。
- 2026-06-11 bounded proposal PRD 已完成最终 handoff：later implementation PRD 为 Go，但只允许实现 `Calculator.AnomalyMul.cal_res_pen()` 的 bounded production diff；本 PRD 本身未替换任何 production formula，也未删除 retained compatibility。下一轮不得把该 Go 扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite，仍必须保留 `MultiplierData` / `MulData` / `DynamicStatement`、`AnomalyBar.current_ndarray`、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 与 `LegacyBuffRuntimeFacade`，并先通过 `formula-parity`、`calculator-reads`，触达 copied-output / event / runtime 分层时追加 `implicit-events`；若改 live semantic diff，还必须使用真实 registered route 与 nonzero anomaly event count 证明。
- 2026-06-11 bounded implementation PRD 已完成最终 handoff：`Calculator.AnomalyMul.cal_res_pen()` 已实现为 behavior-preserving bounded selector extraction，状态为 implemented，非 partially blocked / rolled back。最终串行验证 `formula-parity`（focused `116 passed` / mypy 9 files clean）与 `calculator-reads`（focused `216 passed` / mypy 22 files clean）均通过；本最终 story 未触达 copied-output、event-adjacent、dispatch、listener、dot runtime、same-tick runtime-write、lifecycle container 或 validation-runner 行为，因此 `implicit-events` 与默认 profile 只保留为后续触达对应边界时的 gate。
- 2026-06-11 AM/AP/impact oracle-gap closure PRD 已完成最终 handoff：`Calculator.AnomalyMul.cal_am()`、`Calculator.AnomalyMul.cal_ap()`、`Calculator.StunMul.cal_imp()` 与对应 `CalculatorBuffAttributeReader` 读口已具备 retained oracle、reader snapshot parity、formula boundary split、validation wiring、registered-sample 条件和最终 serial gates。AM/AP/impact 当前状态是 ready for bounded production proposal PRD，不再只是 readiness-only；但下一轮仍必须先选择 exact helper scope、rollback anchors、focused pytest、scoped mypy、registered-sample 条件、retained `formula-parity` / `calculator-reads` gates 和 non-goals，不能直接扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite 或 retained compatibility 删除。
- 2026-06-12 AM/AP/impact bounded production proposal PRD 已完成最终 handoff：最终决策为 later implementation PRD Go，但只授权 scalar AM/AP/impact helper-family 的 bounded diff。下一默认 PRD 可以在 `Calculator.py` 内保持 AM helper-backed baseline、让 AP 收敛到 `_calculate_anomaly_proficiency(...)`、新增 scalar `_calculate_impact(...)` 并让 `Calculator.StunMul.cal_imp()` 委托该 helper；不得扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite，也不得删除 retained compatibility。
- 2026-06-12 AM/AP/impact bounded production implementation PRD 已完成最终 handoff：`Calculator.AnomalyMul.cal_ap()` 已收敛到 `_calculate_anomaly_proficiency(...)`，`Calculator.StunMul.cal_imp()` 已委托 scalar `_calculate_impact(...)`，AM helper-backed baseline 保持不变。最终验证为 focused reader pytest `134 passed`、`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `134 passed` / mypy `9 source files` clean、`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `234 passed` / mypy `22 source files` clean；未触达 copied-output、event/runtime、lifecycle、validation-runner 或 registered-route live semantics。
- 2026-06-12 array-output / RegularMul oracle readiness PRD 已完成最终 handoff：`Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()`、`Calculator.RegularMul` 三个 array output 和 selected RegularMul branch matrix 均已有 characterization / retained oracle 证据；US-005 明确生产 proposal No-Go，US-006 串行复跑 focused reader pytest `138 passed`、`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `138 passed` / mypy `9 source files` clean、`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `22 source files` clean。当前没有 production formula replacement 授权，下一轮仍应留在 phase-3 characterization / proposal-readiness pool。
- 2026-06-12 RegularMul sheer reader-snapshot readiness PRD 已完成最终 handoff：`Calculator.RegularMul.cal_base_attr(..., base_attr=4)` 已有 retained runtime-dependency oracle，`cal_sheer_dmg_bonus()` 仍为 reader-snapshot-compatible；US-003 / US-005 明确 production proposal No-Go，因为当前 `_CalculatorReadSnapshot` 不携带 runtime `char_instance.sheer_attack_conversion_rate`，且现有注册队伍没有 `仪玄` / `Yixuan` 的真实 nonzero sheer route。US-006 串行复跑 focused reader pytest `139 passed`、`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `139 passed` / mypy `9 source files` clean、`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `239 passed` / mypy `22 source files` clean、`implicit-events` base `2 passed` / isolated teams `3 passed` / focused `242 passed` / mypy `88 source files` clean；本 handoff 不改 production / validation-runner / event-runtime source。
- 2026-06-13 copied-output handler/report payload parity PRD 已完成最终 handoff：copied payload constructor matrix、`UpdateAnomaly.spawn_output(...)` listener boundary、anomaly / disorder / polarity / abloom handler report payload parity、registered behavior sample eligibility、serial retained gates 和 rollback-anchor decision 均已记录；最终决策为 conditional Go for a later bounded proposal package only。下一默认 PRD 可写 copied-output handler/report bounded proposal package，但不得直接实现 production diff、不得扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite、不得新增 validation-only registered team，也不得删除 retained compatibility。
- 2026-06-14 copied-output handler/report bounded proposal PRD 已完成最终 handoff：proposal result 为 conditional Go with named blockers for one later bounded copied-output handler/report implementation PRD。下一默认 PRD 可生成该 implementation PRD，但必须先从 `CopyAnomalyForOutput.py` copied payload constructors、`UpdateAnomaly.spawn_output(...)` mode 0 / 1 / 2 creation and missing-`polarity_ratio` failure path、anomaly / disorder / polarity / abloom handler report payload paths 中选择 one coherent copied-output handler/report slice；必须保留 focused pytest、scoped mypy、`formula-parity` / `calculator-reads` / `implicit-events` serial gates、registered-route sample 条件、rollback anchors 和 stop conditions。此 Go 不授权 broad `Calculator.py` / `CalAnomaly.py` rewrite、validation-runner rewrite、registered-team fixture creation、old-container deletion、retained compatibility 删除或 listener / scheduled publish / dot runtime / same-tick runtime write layer merge。
- 2026-06-14 copied-payload handler/report bounded implementation PRD 已完成最终 handoff：`CopyAnomalyForOutput.py` copied-payload constructor boundary、`UpdateAnomaly.spawn_output(...)` mode boundary、scheduled publish / dot runtime / debuff layer-preservation anchors、handler report payload boundary、scoped mypy coverage 和 registered-route No-Go verdict 均已记录。最终串行验证为 focused copied-output pytest `172 passed`、`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `140 passed` / mypy `9 source files` clean、`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `240 passed` / mypy `22 source files` clean、`implicit-events` base `2 passed` / isolated teams `3 passed` / focused `247 passed` / mypy `90 source files` clean，以及默认 lifecycle gate base `2 passed` / isolated teams `3 passed` / focused `18 passed` / mypy `9 source files` clean；main-loop consistency sample 仍只在 future live semantic diff 且真实 registered route 具备 nonzero copied-output/anomaly counts 时运行。
- 2026-06-14 registered sample / formula candidate-selection PRD 已完成最终 handoff：selected surface 为 `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array output；focused oracle、retained `formula-parity` / `calculator-reads` gates、conditional `implicit-events`、registered-route conditional No-Go、rollback anchors、stop conditions 和 reviewer verdict 已记录。最终 verdict 为 Go for one later bounded proposal / implementation PRD only，不授权 broad formula rewrite、RegularMul 打包、retained-only sheer 快捷升级、registered-team fixture creation、validation-runner rewrite、old-container deletion、layer merge 或 retained compatibility 删除。
- 2026-06-14 RegularMul crit-rate bounded implementation PRD 已完成 US-007 handoff：`Calculator.RegularMul.cal_crit_rate(data)` 的 bounded implementation 已落地为 `_calculate_full_crit_rate(...)` helper seam，handoff 状态为 implemented / no-op verified；`CalculatorBuffAttributeReader.read_full_crit_rate(context)` 仍走 full crit retained formula path，full crit 继续包含 `crit_rate_received_increase`，personal crit 仍排除 received crit。Verifier evidence：focused mypy `uv run python -m mypy scripts/ralph/campaign_status.py scripts/ralph/context_index.py` exited `0` after a type-only Ralph context-index boundary typing fix；retained formula/read evidence 继承本 PRD US-005 的 selected crit nodes `10 passed`、full reader suite `143 passed`、`formula-parity` focused `143 passed` / mypy `9 source files` clean 和 `calculator-reads` focused `243 passed` / mypy `22 source files` clean。Reviewer verdict：PASS，changed files stay in docs / Ralph evidence / typecheck tooling boundary，event queue、listener broadcast、same-tick runtime writes、old containers、validation-runner behavior、registered teams/APLs 和 retained compatibility paths 未改变。
- 2026-06-14 RegularMul remaining-branch proposal-readiness PRD 已完成 US-008 handoff：selected candidate 为 `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `CalculatorBuffAttributeReader.read_personal_crit_damage(context)`，proposal result 为 Conditional Go for one later bounded implementation PRD only。Verifier evidence：US-006 retained gates 已串行通过 focused reader pytest `143 passed`、`formula-parity` exited `0` with mypy success on `9 source files` and `[验证完成] 所有步骤通过`、`calculator-reads` exited `0` with mypy success on `22 source files` and `[验证完成] 所有步骤通过`；US-007 reviewer verdict 为 PASS，event queue、synchronous listener broadcasts、same-tick runtime writes、old containers、copied-output constructors、validation-runner behavior、registered teams/APLs 和 retained compatibility paths 未改变。
- 2026-06-15 RegularMul remaining-branch proposal-readiness PRD 已完成 US-009 final evidence / next-intake closure：Ralph progress、campaign dashboard、evidence ledger、checkpoint、PRD completion bit、JSON sanity、scoped Ralph mypy、UTF-8 scan 和 focused `git diff --check` 均记录为 handoff evidence。下一默认 PRD 保持 Phase-3 RegularMul personal crit damage bounded implementation PRD，仅限 `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` 的等价 helper seam；same-phase pool 继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if new evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- 2026-06-15 RegularMul personal crit damage bounded implementation PRD 已完成 US-008 final handoff：`Calculator.RegularMul.cal_personal_crit_dmg(data)` 已通过 `_calculate_personal_crit_damage(static_statement, dynamic_statement)` helper seam 实现 / no-op verified，public signature、reader anchor `CalculatorBuffAttributeReader.read_personal_crit_damage(context)`、公式 `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`、full crit damage received-bonus contrast、`_CalculatorReadSnapshot` 字段集、old containers、event/runtime/listener layers、validation-runner behavior、registered routes 和 retained compatibility 均保持不变。US-008 handoff 记录 focused personal-crit-damage pytest、scoped mypy、focused docs `git diff --check`、JSON sanity、UTF-8 / mojibake scan、campaign refresh、reviewer / invariant verdict 与 rollback anchors；未发现新 Buff coupling 或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal，而不是继续跟随 personal crit damage；same-phase pool 继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if new evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- 2026-06-15 RegularMul personal crit rate proposal-readiness PRD 已完成 US-008 final handoff：proposal result 为 Conditional Go for one later bounded implementation PRD only，目标仅限 `Calculator.RegularMul.cal_personal_crit_rate(data)` 与可选 module-local `_calculate_personal_crit_rate(static_statement, dynamic_statement)` helper，且必须保持 `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` 并继续排除 `crit_rate_received_increase`。`CalculatorBuffAttributeReader.read_personal_crit_rate(context)`、`_CalculatorReadSnapshot`、full `cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` contrast、old containers、event/runtime/listener layers、validation-runner behavior、registered routes 和 retained compatibility 均未改变。US-008 handoff 记录 focused typecheck、docs `git diff --check`、JSON sanity、UTF-8 / mojibake scan、campaign refresh、reviewer / invariant verdict 与 rollback anchors；未发现新 Buff coupling 或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。下一默认 PRD 可生成 personal crit rate bounded implementation；same-phase pool 继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- 2026-06-15 RegularMul personal crit rate bounded implementation PRD 已完成 US-008 final handoff：`Calculator.RegularMul.cal_personal_crit_rate(data)` 已通过 `_calculate_personal_crit_rate(static_statement, dynamic_statement)` helper seam 实现 / no-op verified，public signature、reader anchor `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`、公式 `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate`、full crit received-bonus contrast、`_CalculatorReadSnapshot` 字段集、old containers、event/runtime/listener layers、validation-runner behavior、registered routes 和 retained compatibility 均保持不变。US-008 handoff 记录 focused personal/full crit pytest `10 passed, 135 deselected`、scoped mypy `Success: no issues found in 2 source files`、focused docs `git diff --check`、Ralph JSON sanity、UTF-8 / mojibake scan、campaign refresh、reviewer / invariant verdict 与 rollback anchors；未发现新 Buff coupling 或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal，而不是继续跟随 personal crit rate；same-phase pool 继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- 2026-06-15 RegularMul full crit damage proposal-readiness PRD 已完成 US-008 final handoff：proposal result 为 Conditional Go for one later bounded implementation PRD only，目标仅限 `Calculator.RegularMul.cal_crit_dmg(data)` 与可选 module-local behavior-preserving helper。future helper 必须保持 static crit damage、dynamic crit damage、field crit damage、`aftershock_attack` label bonus、`received_crit_dmg_bonus` 和 `min(5, crit_dmg)` cap 行为，保留 public method signature 与当前 `SkillNode` assumption；不得新增 public `CalculatorBuffAttributeReader.read_full_crit_damage(...)`，不得扩展 `_CalculatorReadSnapshot`。Verifier evidence：US-003 / US-004 focused oracle 和 contrast-boundary tests 已落地，US-007 serial `formula-parity` exited `0` with base `2 passed` / isolated `3 passed` / focused `148 passed` / mypy `9 source files` clean；US-008 focused full-crit pytest exited `0` with `5 passed, 143 deselected`，scoped mypy exited `0` with `Success: no issues found in 2 source files`。Reviewer / invariant verdict：PASS，event queue、synchronous listener broadcasts、same-tick runtime writes、explicit ports/adapters、old containers、validation-runner behavior、registered routes 和 retained compatibility paths 未改变。未发现新 Buff coupling 或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。下一默认 PRD 可生成 one bounded full-crit-damage implementation PRD；same-phase pool 继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。

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

Phase-3 same-phase candidate selection / bounded proposal PRD（当前默认）：当前 personal crit rate bounded implementation PRD 已完成 handoff，`Calculator.RegularMul.cal_personal_crit_rate(data)` 已通过 `_calculate_personal_crit_rate(...)` helper seam implemented / no-op verified，且不需要第二个 personal-crit-rate follow-up。下一轮默认应从 retained same-phase pool 中选择一个 exact bounded candidate，写清 candidate files / symbols、known coupling、Ralph-sized work directions、focused tests、scoped mypy targets、registered-sample 条件、rollback anchors、retained `formula-parity` / conditional `calculator-reads` / conditional `implicit-events` gate、non-goals 和 stop conditions。不得默认重开已完成的 copied-payload handler/report implementation、`Calculator.AnomalyMul.cal_res_pen()` selector extraction、AM/AP/impact helper implementation、selected Stun implementation、current `Calculator.RegularMul.cal_crit_rate(data)` implementation、current `Calculator.RegularMul.cal_personal_crit_dmg(data)` implementation、current `Calculator.RegularMul.cal_personal_crit_rate(data)` implementation、retained-only sheer No-Go 或 P2 guarded buckets，也不得把下一轮直接扩大为 broad formula rewrite。same-phase pool 必须继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。

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
- US-014 最终串行验证已通过：changed focused pytest `tests/simulator/test_buff_attribute_reader.py -q` 为 `38 passed`；`calculator-reads` profile base `2 passed` / isolated teams `3 passed` / focused `138 passed` / mypy `22 source files` clean；`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean。该 story 未改 production formula behavior、live registered-team semantics、lifecycle/runtime write paths 或 validation wiring，因此默认 lifecycle profile 与 main-loop consistency sample 均按规则跳过。
- US-015 已完成 handoff docs / next-pool 同步：`formula-parity` 是当前 phase-3 characterization profile，`calculator-reads` 仍是 retained reader / guardrail gate；当时 production formula replacement 继续 No-Go，等待 US-016 serial validation 和 final Go / No-Go entry 给出明确结论。
- US-016 final serial validation 已通过：touched focused pytest `test_buff_attribute_reader.py` 为 `60 passed`，Vivian copied-output focused tests 为 `3 passed`；`formula-parity`、`calculator-reads`、`implicit-events` 与默认 lifecycle profile 均串行退出 `0`。Final Go / No-Go 仍判定 production formula replacement 下一 PRD No-Go；下一默认工作应先补 deterministic formula oracle 和 field / payload matrix 缺口。
- US-025 serial formula gate 已通过：`formula-parity` profile base `2 passed` / isolated teams `3 passed` / focused `95 passed` / mypy `9 source files` clean，`calculator-reads` profile base `2 passed` / isolated teams `3 passed` / focused `195 passed` / mypy `22 source files` clean，`implicit-events` profile base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean。
- US-026 final handoff：production formula replacement 仍 No-Go，当前没有单个 production formula domain 获得替换许可。下一默认 PRD 应关闭并复核 exact blockers：`Calculator.AnomalyMul.cal_res_pen()` / `anomaly_snapshot` vector assembly、`CalAnomaly.cal_k_level()` clamp、copied-output handler/report payload parity、真实 registered-route 触发条件和 rollback / retained gate 证据；若这些 blocker 未关闭，就继续 characterization 而不是提交生产替换 proposal。
- US-009 final handoff：`Calculator.AnomalyMul.cal_res_pen()` 已成为唯一 proposal-eligible bounded domain；`anomaly_snapshot` vector assembly、`CalAnomaly.cal_k_level()` clamp、copied-output handler/report payload parity、registered-route eligibility 与 rollback anchors 已作为该 proposal 的前置守门证据关闭或 codify。该结论不替换 `Calculator.py` / `CalAnomaly.py` 生产公式，也不授权删除旧容器或 runtime / copied-output 兼容层。
- US-007 final proposal handoff：current proposal package 已通过 serial gate；下一轮可生成 later implementation PRD，但只能改 `Calculator.AnomalyMul.cal_res_pen()` 的 bounded selector / extraction。`anomaly_snapshot`、`CalAnomaly.cal_k_level()`、copied-output handler/report payload、registered-route sample 条件、P2-A through P2-G guarded maintenance 与 retained compatibility 都是守门 / 回滚 / same-phase pool，不是本次 Go 一并授权的生产替换域。
- Current US-013 final handoff：AM/AP/impact oracle-gap closure 已通过 final serial gates，状态从 readiness-only 改为 ready for bounded production proposal PRD；下一轮可写 AM/AP/impact proposal，但仍不得在 proposal story 中直接实现 broad formula rewrite、删除 retained formula snapshots、删除 old containers 或绕过 registered-sample 条件。

### 本轮未解决或新暴露的耦合点

- P2-G direct simulator context helpers 已补齐为 completed guarded bucket；P2-A through P2-G 没有剩余同阶段默认实现 backlog。
- Phase-3 formula parity suite design、P2-D / P2-E / P2-F / P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules 都保留为后续候选块，不能因为 P2-G 或 readiness decision 已完成就从候选池删除。
- P2-A / P2-B / P2-C / P2-D / P2-E / P2-F / P2-G 不再作为默认实现 backlog；后续只在 source guardrail、reader parity、trigger-state no-write / order tests、dispatch tests、dot runtime-state guardrails、P2-F forced-write guardrail、P2-G direct-context guardrail 或 validation profile 暴露具体回归时开窄 blocker。
- Formula snapshots、CalAnomaly internals、old containers、legacy `buff_add()` / `KickOutBuff()` 和 deleted raw queue discovery surfaces 仍是 retained compatibility / phase-3 / blocker-only 项；下一轮默认转向 remaining formula oracle / proposal-readiness，不直接删除 retained compatibility。
- AM/AP/impact bounded implementation、array-output / RegularMul oracle readiness PRD、RegularMul sheer reader-snapshot readiness PRD、copied-output handler/report parity / proposal / bounded implementation PRD 均已完成最终 handoff；后续不再把 `cal_am()`、`cal_ap()`、`cal_imp()` helper-family、copied-output handler/report implementation、已完成的 Stun / RegularMul array contract、selected branch matrix 或 retained-only sheer No-Go 当默认 implementation backlog。
- Current RegularMul crit-rate implementation PRD 已完成 handoff：`Calculator.RegularMul.cal_crit_rate(data)` 已 marked implemented / no-op verified，full crit 保留 `crit_rate_received_increase`，personal crit 保留排除 received crit 的 contrast boundary。当前默认 PRD 改为 Phase-3 same-phase candidate selection / bounded proposal PRD；registered behavior sample 仍为 conditional No-Go，直到 future live semantic diff 且真实 registered route 证明 nonzero selected formula relevance 与候选相关输入。remaining `Calculator.RegularMul` branches / retained-only sheer、future `Calculator.StunMul.get_stun_array()` follow-up with named evidence、P2-A through P2-G guarded maintenance、retained compatibility 和 blocker-only reopen rules 仍保留为后续候选。
- Current RegularMul personal crit rate proposal-readiness PRD 已完成 handoff：`Calculator.RegularMul.cal_personal_crit_rate(data)` 获得 one later bounded implementation PRD 的 Conditional Go，但只允许等价 helper seam 并继续排除 `crit_rate_received_increase`；该 Go 不重开 full `cal_crit_rate(data)`、crit damage、damage bonus、defense/resistance/vulnerability、base damage、retained-only sheer、Stun array、copied-output、P2 guarded buckets、event/runtime/listener layers 或 retained compatibility deletion。

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

US-022 将 Phase 3 公式 / 行为域细分为以下 registered-team trigger；完整矩阵记录在 [Buff公式候选与测试目标清单.md](./Buff公式候选与测试目标清单.md)。

| 触发域 | 只需要 focused characterization 的情况 | 语义变更后必须追加 registered main-loop sample 的情况 |
| --- | --- | --- |
| damage / crit / defense / resistance / vulnerability | 只新增 oracle、reader seam 或 retained helper parity test。 | 生产公式输出会改变 live damage route，且注册队伍 APL 能在 stop-tick 内触达对应伤害事件。 |
| stun / impact | 只锁定 `Calculator.StunMul` 或 impact reader 快照。 | impact、stun ratio 或 stun received 语义改变，且注册队伍能打出目标失衡 route。 |
| anomaly / settlement | 只刻画 `CalAnomaly`、`AnomalyBar.current_ndarray`、settlement snapshot。 | 异常积蓄、结算、异常伤害或 active anomaly snapshot 语义改变，且注册队伍能触发目标异常 route。 |
| copied-output | 只锁 copied anomaly / disorder payload fields 和 formula inputs。 | NewAnomaly / Disorder / PolarityDisorder / Vivian copied payload 语义或 listener-facing 字段改变，且注册队伍能生成该 payload。 |
| Buff timeline | 只新增 no-write / runtime facade / guardrail evidence。 | Buff / debuff / dot add、refresh、activation、duration、removal 顺序改变，且注册队伍 route 会产生相关 timeline entries。 |
| event publish timing | 只新增 dispatch order / fail-fast queue focused tests。 | `execute_tick`、priority、target fan-out 或 producer-local publish order 改变，且注册队伍 live route 会发布该事件。 |

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

#### 候选块 Phase-3：AM/AP/impact bounded production implementation（已完成 / rollback anchor）

- 候选文件 / 符号：`zsim/sim_progress/ScheduledEvent/Calculator.py` 中的 `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `_calculate_anomaly_mastery(...)`, `_calculate_anomaly_proficiency(...)`, `_calculate_impact(...)`, `CalculatorBuffAttributeReader.read_anomaly_mastery(...)`, `read_anomaly_proficiency(...)`, `read_impact(...)`；focused tests 入口为 `tests/simulator/test_buff_attribute_reader.py` 中 `test_cal_am_retained_multiplier_data_oracle_rows`, `test_cal_ap_retained_multiplier_data_oracle_rows`, `test_cal_imp_retained_multiplier_data_oracle_rows`, `test_calculator_am_ap_impact_formula_boundaries_remain_retained_compatibility`。
- 实施结果：AM 保持 helper-backed baseline；AP 已保留 public signature 与 `@lru_cache(maxsize=16)` 并委托 `_calculate_anomaly_proficiency(...)`；impact 已新增 scalar `_calculate_impact(...)` 并让 `Calculator.StunMul.cal_imp()` 委托该 helper。
- 当前状态：已完成，不再作为下一默认实现 backlog。最终验证为 focused reader pytest `134 passed`，`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `134 passed` / mypy `9 source files` clean，`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `234 passed` / mypy `22 source files` clean。
- 后续规则：只有 focused regression、validation failure 或明确语义 follow-up 命名 AM/AP/impact helper-family 时才重开；不得用后续 rollback 删除 `MultiplierData`、`MulData`、`DynamicStatement`、old containers、copied-output constructors、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 或 `LegacyBuffRuntimeFacade`。
- 行为样本规则：本 implementation 经 focused parity 证明 behavior-preserving，且未触达 registered-route live semantics；后续只有真实 production semantic diff 且真实注册队伍可触达目标 route 时才跑 `scripts/run_buff_main_loop_consistency.py`。

#### 候选块 Phase-3：RegularMul selected personal crit damage implementation + retained formula pool（implemented / same-phase pool retained）

- 候选文件 / 符号：`zsim/sim_progress/ScheduledEvent/Calculator.py` 中的 `Calculator.RegularMul.cal_personal_crit_dmg(data)`；reader anchor 为 `CalculatorBuffAttributeReader.read_personal_crit_damage(context)`；contrast anchors 为 `Calculator.RegularMul.cal_crit_dmg(data)`、`Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)`、`_CalculatorReadSnapshot`；retained pool 仍包括 `Calculator.RegularMul` remaining branches、retained-only sheer、future `Calculator.StunMul.get_stun_array()` follow-up with named evidence、copied-output retained boundaries 和 P2-A through P2-G guarded buckets。
- 当前已知耦合：selected personal crit damage 必须继续只读 `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`，并排除 `received_crit_dmg_bonus`；full `Calculator.RegularMul.cal_crit_dmg(data)` 仍是包含 received crit damage 的 contrast branch。`_CalculatorReadSnapshot` 保持 private static / dynamic / judge / enemy / level adapter，不新增 `char_instance` 或 public field。
- 本轮结果：proposal-readiness PRD 已选择 exact candidate `Calculator.RegularMul.cal_personal_crit_dmg(data)` 并关闭 oracle / rollback / retained-gate / reviewer gaps；当前 implementation PRD 已把 public method 委托到 `_calculate_personal_crit_damage(static_statement, dynamic_statement)`，保持 `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` 等价语义和 reader anchor。
- 当前默认下一 PRD：Phase-3 same-phase candidate selection / bounded proposal PRD。先从 retained pool 中选择一个 exact surface，不再继续把 personal crit damage 作为默认实现 backlog。
- 当前 verdict：Implemented / no-op verified at handoff for `Calculator.RegularMul.cal_personal_crit_dmg(data)` only。Registered main-loop sample 仍是 conditional No-Go，除非 future live semantic diff 且真实 registered direct crit route 在 explicit stop tick 内证明 nonzero selected-branch relevance；不得创建 validation-only team、fake APL、fixture-only route 或 retained-vs-retained sample。
- 必须保留：full-vs-personal crit damage contrast、implemented `cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` closure、AM/AP/impact helper implementation、`Calculator.AnomalyMul.cal_res_pen()` selector extraction、selected Stun implementation、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、dispatch/runtime ports、listener broadcast、dot runtime registration、retained formula snapshots 和 P2-A through P2-G guarded buckets。
- 同阶段候选池：
  - registered behavior sample eligibility：只在 future live production semantic diff 且真实注册队伍可触达目标 route 时运行 main-loop consistency；不得创建 validation-only team，样本必须证明 nonzero selected formula relevance 和候选相关输入 / event / formula count。
  - remaining `Calculator.RegularMul` branches / retained-only sheer follow-up：继续只按 exact branch、deterministic oracle、rollback anchors 和 registered-sample 条件重开；personal crit damage Conditional Go 不授权其他 branches。
  - future `Calculator.StunMul.get_stun_array()` follow-up：当前 helper extraction 已完成；只有 named regression、focused oracle gap、validation failure 或新的 proposal-readiness packet 才能重开。
  - P2-A through P2-G guarded maintenance：继续只由 guardrail / focused test / validation 的 concrete blocker 触发，不作为默认实现 backlog。
  - retained compatibility / blocker-only reopen：old containers、legacy Buff write paths、dispatch/runtime/listener/dot layers 与 retained formula snapshots 只能由 root-workspace source、guardrail、focused test、validation 或 real registered-route blocker evidence 命名后重开。
- 验证入口：当前 handoff 的 exact commands 为 `uv run pytest tests/simulator/test_buff_attribute_reader.py -q -k "personal_crit_damage or regular_mul_branch_matrix or crit_formula_families"`、`uv run python -m mypy zsim/sim_progress/ScheduledEvent/Calculator.py tests/simulator/test_buff_attribute_reader.py --follow-imports skip --ignore-missing-imports`、focused docs `git diff --check`、Ralph JSON sanity 和 UTF-8 / mojibake scan。后续 formula/read candidate 仍保留 `formula-parity` 与 `calculator-reads`；触达 copied-output、event、dispatch、runtime 或 listener 边界时追加 `implicit-events`；触达 lifecycle container / runtime write path 时追加默认 profile；live semantic diff 且 route/count 合格时才追加 main-loop consistency。
- 非目标：不做 broad `Calculator.py` / `CalAnomaly.py` rewrite；不删除 retained compatibility；不把 `cal_crit_expect()`、full crit damage、crit rate、personal crit rate、damage bonus、defense/resistance/vulnerability、base damage、retained-only sheer、Stun array、copied-output、registered-team fixtures、validation-runner rewrite 或 event/runtime/listener layer merge 合并进 selected personal crit damage implementation PRD。

#### 候选块 Phase-3：RegularMul personal crit rate bounded implementation PRD（已完成 / retained boundary）

- 候选文件 / 符号：`zsim/sim_progress/ScheduledEvent/Calculator.py` 中的 `Calculator.RegularMul.cal_personal_crit_rate(data)`，可选 module-local `_calculate_personal_crit_rate(static_statement, dynamic_statement)`；reader anchor 为 `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`；contrast anchors 为 full `Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)`、`_CalculatorReadSnapshot` 与 full-vs-personal focused tests。
- 当前已知耦合：personal crit rate 必须继续只读 `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate`，并排除 `crit_rate_received_increase`；full crit rate 仍包含 received crit rate。`_CalculatorReadSnapshot` 保持 private static / dynamic / judge / enemy / level adapter，不新增 `char_instance`、runtime view、array output 或 public field。
- 本轮结果：bounded implementation PRD 已关闭 helper-seam implementation、reader anchor / full-personal contrast review、focused oracle / scoped typecheck、retained validation-gate decision、registered-sample conditional No-Go、reviewer invariant / rollback gate 与 final handoff。`Calculator.RegularMul.cal_personal_crit_rate(data)` now delegates to module-local `_calculate_personal_crit_rate(static_statement, dynamic_statement)` while preserving `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` and excluding `crit_rate_received_increase`。
- 当前默认下一 PRD：Phase-3 same-phase candidate selection / bounded proposal PRD。不得自动生成第二个 personal-crit-rate follow-up；future generation must reselect from the retained same-phase pool。
- 当前 verdict：Implemented / no-op verified at handoff。Registered main-loop sample 仍是 conditional No-Go，除非 future live semantic diff 且真实 registered direct crit route 在 explicit stop tick 内证明 nonzero selected personal-crit-rate relevance；不得创建 validation-only team、fake APL、fixture-only route 或 retained-vs-retained sample。
- 必须保留：implemented full crit rate helper seam、implemented personal crit damage helper seam、full-vs-personal crit rate contrast、full-vs-personal crit damage contrast、selected Stun implementation、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、dispatch/runtime ports、listener broadcast、dot runtime registration、retained formula snapshots 和 P2-A through P2-G guarded buckets。
- 同阶段候选池：registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility、blocker-only phase-1 reopen rules。
- 验证入口：current handoff exact commands include focused personal/full crit pytest `10 passed, 135 deselected` and scoped mypy over `Calculator.py` / focused tests with `Success: no issues found in 2 source files`；handoff 还记录 focused docs `git diff --check`、Ralph JSON sanity 和 UTF-8 / mojibake scan。后续 formula/read candidate 仍保留 `formula-parity` 与 conditional `calculator-reads`；触达 copied-output、event、dispatch、runtime 或 listener 边界时追加 `implicit-events`；触达 lifecycle container / runtime write path 时追加默认 profile；live semantic diff 且 route/count 合格时才追加 main-loop consistency。
- 非目标：不做 broad `Calculator.py` / `CalAnomaly.py` rewrite；不包含 `crit_rate_received_increase`；不重开 full crit、crit damage、`cal_crit_expect()`、damage bonus、defense/resistance/vulnerability、base damage、retained-only sheer、Stun array、copied-output、registered-team fixtures、validation-runner rewrite、old-container deletion 或 event/runtime/listener layer merge。

#### 候选块 Phase-3：copied-output handler/report bounded implementation PRD（已完成 / retained boundary）

- 候选文件 / 符号：`zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py` 中 `NewAnomaly`、`Disorder`、`PolarityDisorder`、`DirgeOfDestinyAnomaly`；`zsim/sim_progress/Update/UpdateAnomaly.py` 中 `spawn_output(...)` / `update_anomaly(...)`；`zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py`、`disorder.py`、`polarity_disorder.py`、`abloom.py` 的 handler report payload paths；focused evidence in `tests/simulator/test_buff_attribute_reader.py`、`test_update_anomaly_dispatch.py`、`test_anomaly_handler_runtime_view.py`。
- 当前已知耦合：constructor field matrix、listener broadcast vs scheduled publish separation、handler report payload parity、registered-sample eligibility、rollback anchors、stop conditions 和 reviewer questions 已由 bounded proposal PRD 覆盖；bounded implementation PRD 已完成 copied-payload constructor boundary、spawn-output mode boundary、layer-preservation anchors、handler report payload boundary、scoped mypy coverage 和 registered-route No-Go verdict。copied-output payload、listener broadcast、scheduled queue publish、dot runtime registration 与 same-tick runtime writes 仍是分层 retained boundaries。
- 本轮结果：实现 PRD 已收口，不再作为下一默认 backlog。最终证据包括 focused copied-output pytest `172 passed`、serial `formula-parity` / `calculator-reads` / `implicit-events` / default lifecycle validation green，以及 main-loop consistency sample 的条件式跳过理由。
- 后续工作方向：不要自动生成第二个 copied-output implementation follow-up。若 future regression、guardrail 或 validation 命名 copied-output 文件 / 符号 / gate，再开 blocker 或 proposal PRD；否则下一轮应从 same-phase pool 重新选择一个 exact bounded candidate。
- 必须保留：`Calculator.py` / `CalAnomaly.py` retained formula snapshots、`MultiplierData` / `MulData` / `DynamicStatement`、`AnomalyBar.current_ndarray`、old containers、legacy `buff_add()` / `KickOutBuff()`、`ScheduleDispatchPort`、listener broadcast、dot runtime registration、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、已完成 `cal_res_pen()` 与 AM/AP/impact bounded implementations、array / RegularMul / sheer characterization evidence。
- 同阶段候选池：registered behavior sample eligibility、`Calculator.RegularMul` remaining branches / retained-only sheer follow-up、`Calculator.StunMul.get_stun_array()` / array output follow-up、P2-A through P2-G guarded maintenance、retained compatibility、blocker-only phase-1 reopen rules。
- 验证入口：后续 candidate-selection / proposal PRD 至少跑 story-local docs / JSON / UTF-8 checks 和 active story scoped typecheck gate；触达 formula / reader 时串行保留 `formula-parity` / `calculator-reads`，触达 copied-output / event / dispatch / runtime / listener 时追加 `implicit-events`。live semantic diff 只有在 real registered route 且 nonzero relevant event count 时才追加 main-loop consistency sample。
- 非目标：不扩大为 broad production diff，不创建 validation-only registered team，不把 `.codex_worktrees/` 命中当 current source blocker，不重写 validation runner，不删除 retained compatibility，不把 P2-A through P2-G guardrails 或 RegularMul / Stun array follow-ups 合并到 copied-output implementation。

## 已存在的真实验证入口

- `uv run python scripts/run_buff_main_loop_consistency.py --team <team> --stop-tick <n> --legacy-runtime <label> --candidate-runtime <label> --json`
  输出至少包含 `team`、`apl`、`stop_tick`、`total_damage`、`event_counts`、`buff_timeline` 与 `differences`；`--apl` 可选。
- `uv run python scripts/run_buff_runtime_benchmark.py --team <team> --stop-tick <n> --legacy-runtime <label> --candidate-runtime <label> --json`
  输出至少包含 `team`、`apl`、`stop_tick`、`total_runtime_ms`、`hotspots` 与 `comparisons`；`--apl` 可选。
- 两个命令里的 `--legacy-runtime` / `--candidate-runtime` 当前都只是报告标签；只有 live simulator 真正消费 `config.buff_runtime.mode` 后，它们才应承载真实 runtime 切换语义。

## 下一轮 PRD 的验证要求

- 当前默认 PRD 改为 Phase-3 same-phase candidate selection / bounded proposal：先从 retained candidate pool 中选择一个 exact bounded surface，再命名 candidate files/symbols、focused tests、scoped mypy targets、registered-sample 条件、rollback anchors、retained `formula-parity` / `calculator-reads` / conditional `implicit-events` gate、non-goals 和 stop conditions。不得默认重开已完成的 copied-payload handler/report implementation、`Calculator.AnomalyMul.cal_res_pen()` selector extraction、AM/AP/impact helper implementation、selected Stun implementation、current `Calculator.RegularMul.cal_crit_rate(data)` implementation、retained-only sheer No-Go 或 P2 guarded buckets，也不得把下一轮直接扩大为 broad formula rewrite。
- 若触达 event-adjacent copied-output、validation wiring、dispatch/runtime boundaries，追加：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events`。
- 若触达生命周期容器、runtime 写路径或更广 validation script 行为，追加：`uv run python scripts/run_buff_refactor_validation.py`。
- 若维护已完成 P2-D scheduled publish ordering / adapter parity bucket，必须保留 exact-file source guardrail、file-specific dispatch tests、adapter 按需创建与 `ScheduleData.reset_myself()` 后 event_list rebinding 证据；不要把 guardrail 扩成阻断 P2-E / P2-F / P2-G，也不要新增 raw queue passthrough 或 runtime write facade。
- 若维护已完成 P2-E dot runtime-state / initialization bucket，必须保留 exact-file source guardrail、runtime-list helper parity、Shock duration read helper parity、Vivian / UpdateAnomaly focused tests 与 scheduled follow-up 分层证据；不要把 guardrail 扩成阻断 P2-F / P2-G，也不要把 dot runtime state 转成 planned-event backlog。
- 若维护已完成 P2-G direct simulator context helpers bucket，必须保留 service-family guardrail、focused branch tests 与 `.codex_worktrees/` 排除；触达 preload schedule、Character action/resource、listener/report/RNG 或 live behavior semantics 时追加对应 file-specific pytest，只有真实注册代表队存在且 live behavior 变化时才运行 main-loop consistency sample。
- US-026 后的 validation decision：`formula-parity`、`calculator-reads` 与 `implicit-events` serial gates 已通过，但当时 production replacement 仍 No-Go。US-013 / proposal PRD / implementation PRD 已把 AM/AP/impact scalar helper-family 从 readiness 推进到 bounded implementation complete。下一轮必须从本文件的 Phase-3 array-output / remaining formula 候选块和 `docs/Buff公式候选与测试目标清单.md` 的 oracle / retained-gate 证据取材，命名 exact formula surface、focused tests、scoped mypy targets、registered behavior sample 条件、rollback plan、retained `formula-parity` / `calculator-reads` / conditional `implicit-events` gate 与 remaining blockers。
- Current US-007 后的 validation / handoff decision：AM/AP/impact final serial `formula-parity`（base `2 passed` / isolated teams `3 passed` / focused `132 passed` / mypy 9 files clean）与 `calculator-reads`（base `2 passed` / isolated teams `3 passed` / focused `232 passed` / mypy 22 files clean）均通过；下一轮默认生成 bounded production implementation PRD，不在 focused regression 或 validation failure 之外重开 `cal_res_pen()`，也不把 AM/AP/impact scalar-helper Go 外推成 whole-Calculator replacement approval。
- Current array / RegularMul US-007 后的 handoff decision：Stun array、RegularMul arrays 和 selected RegularMul branch matrix 只构成 characterization / retained oracle evidence，production proposal 当前 No-Go；下一轮默认继续 phase-3 characterization / proposal-readiness continuation，从 copied-output handler/report payload parity、registered-team behavior sample eligibility、remaining RegularMul / retained-only sheer follow-up、`StunMul.get_stun_array()` follow-up 或 P2-A through P2-G guarded maintenance 中选择 exact bounded slice。
- Current sheer reader-snapshot US-007 后的 handoff decision：`cal_base_attr(..., base_attr=4)` retained oracle、reader-snapshot No-Go、registered-route sample-condition No-Go 与 final serial gates 均已记录；下一轮仍默认继续 phase-3 characterization / proposal-readiness continuation，不把 `RegularMul` sheer conversion 升级为 production proposal，也不把 next PRD 折叠成只跟随该 single branch。
- Current copied-output bounded proposal US-008 后的 handoff decision：proposal result 为 conditional Go with named blockers for one later bounded copied-output handler/report implementation PRD；下一轮默认可生成该 implementation PRD，但必须保持 one coherent copied-output handler/report slice、retained gates、registered-route conditions、rollback anchors 和 stop conditions。same-phase candidate pool 继续保留 registered sample eligibility、remaining RegularMul / retained-only sheer follow-up、`StunMul.get_stun_array()` follow-up、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- Current copied-payload bounded implementation US-008 后的 handoff decision：implementation 已完成并验证；下一轮默认改为 Phase-3 same-phase candidate selection / bounded proposal PRD，从 registered sample eligibility、remaining RegularMul / retained-only sheer、`StunMul.get_stun_array()` / array-output、P2-A through P2-G guarded maintenance、retained compatibility 或 blocker-only reopen rules 中选择 exact bounded slice。PRD 生成步骤只产出 Markdown PRD，不直接修改 `scripts/ralph/prd.json`；Ralph JSON conversion 留给后续显式步骤。
- Current candidate-selection US-008 后的 handoff decision：selected Stun array output contract 已具备 focused oracle、retained gates、registered-route condition、rollback anchors、stop conditions 和 reviewer Go；下一轮默认可生成 one bounded `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` proposal / implementation PRD。该默认不授权 broad formula rewrite、RegularMul 打包、retained-only sheer shortcut、validation-runner rewrite、registered-team fixture creation、old-container deletion、layer merge 或 retained compatibility 删除；若触达 live semantic diff，必须先证明真实 registered stun / impact route 和 nonzero relevant counts。
- Current Stun array bounded implementation US-008 后的 handoff decision：selected implementation 已完成且 handoff 为 implemented / no-op verified；`Calculator.StunMul.get_stun_array()` 已委托 `_build_stun_multiplier_array(...)`，`Calculator.cal_stun()` product consumer、五字段顺序和 `np.float64` dtype 保持不变。下一默认 PRD 改为 Phase-3 same-phase candidate selection / bounded proposal PRD，从 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if new evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 或 blocker-only reopen rules 中选择 exact bounded slice；不得把本 implementation 外推为 broad `Calculator.py` / `CalAnomaly.py` rewrite、RegularMul bundling、registered-team fixture creation、validation-runner rewrite、old-container deletion、layer merge 或 retained compatibility 删除。
- Current RegularMul remaining-branch US-008 后的 handoff decision：selected `Calculator.RegularMul.cal_crit_rate(data)` proposal packet 已完成 final handoff；下一默认 PRD 为 one bounded implementation PRD limited to `Calculator.RegularMul.cal_crit_rate(data)`。Registered behavior sample 仍为 conditional No-Go，只有 future live semantic diff 且真实 registered route 证明 nonzero selected formula relevance 与 nonzero `crit_rate_received_increase` 时才运行；same-phase candidate pool 继续保留 registered sample eligibility、remaining RegularMul branches / retained-only sheer、future Stun follow-up with named evidence、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。
- Current RegularMul crit-rate bounded implementation US-008 后的 handoff decision：`Calculator.RegularMul.cal_crit_rate(data)` 已完成 helper-seam implementation、retained gate review、handoff docs sync 和 Ralph evidence bookkeeping；下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal，而不是再次跟随 `cal_crit_rate(data)`。候选池继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if new evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- Current RegularMul personal-crit-damage bounded implementation US-008 后的 handoff decision：`Calculator.RegularMul.cal_personal_crit_dmg(data)` 已完成 helper-seam implementation / no-op verification，`CalculatorBuffAttributeReader.read_personal_crit_damage(context)` 仍委托该 public formula path，full `cal_crit_dmg(data)` retained contrast、`_CalculatorReadSnapshot`、event queue、listener broadcast、same-tick runtime writes、old containers、validation-runner behavior、registered routes 和 retained compatibility 均未改变。下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal；候选池继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if new evidence names one、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- Current RegularMul personal-crit-rate proposal-readiness US-008 后的 handoff decision：proposal result 为 Conditional Go for one later bounded implementation PRD limited to `Calculator.RegularMul.cal_personal_crit_rate(data)` plus optional module-local `_calculate_personal_crit_rate(static_statement, dynamic_statement)`。该 future helper 必须保持 `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` 并排除 `crit_rate_received_increase`；`CalculatorBuffAttributeReader.read_personal_crit_rate(context)`、`_CalculatorReadSnapshot`、full crit contrast、event queue、listener broadcast、same-tick runtime writes、old containers、validation-runner behavior、registered routes 与 retained compatibility 均未改变。候选池继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- Current RegularMul personal-crit-rate bounded implementation US-008 后的 handoff decision：`Calculator.RegularMul.cal_personal_crit_rate(data)` 已完成 helper-seam implementation / no-op verification，`CalculatorBuffAttributeReader.read_personal_crit_rate(context)` 仍委托该 public formula path，full `cal_crit_rate(data)` retained contrast、`_CalculatorReadSnapshot`、event queue、listener broadcast、same-tick runtime writes、old containers、validation-runner behavior、registered routes 和 retained compatibility 均未改变。下一默认 PRD 返回 Phase-3 same-phase candidate selection / bounded proposal；候选池继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
- Current RegularMul full-crit-damage proposal-readiness US-008 后的 handoff decision：proposal result 为 Conditional Go for one later bounded implementation PRD limited to `Calculator.RegularMul.cal_crit_dmg(data)` plus optional module-local behavior-preserving helper。该 future helper 必须保持 `aftershock_attack` label branch、`received_crit_dmg_bonus` inclusion、`min(5, crit_dmg)` cap、public signature 和 current `SkillNode` assumption；public full-crit-damage reader API、snapshot public expansion、full/personal crit bundling、retained-only sheer shortcut、registered-team fixture creation、validation-runner rewrite、old-container deletion、layer merge 和 retained compatibility deletion 均为 No-Go。候选池继续保留 registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears、P2-A through P2-G guarded maintenance、retained compatibility 与 blocker-only reopen rules。当前 handoff 未发现新 Buff 耦合或既有耦合分类变化，因此不更新 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)。
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
