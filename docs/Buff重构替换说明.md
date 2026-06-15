# Buff重构替换说明

## 用途

- 记录每一轮 Ralph 在 Buff 重构里实际新增的边界、适配层或运行路径替换。
- 只做增量追加，不重写历史结论。
- 每轮都要更新；如果本轮还没有直接替换旧运行路径，也要明确写出“本轮仅铺边界，尚未正式替换”。

## 追加格式

```text
## [日期时间] - [Story ID / PRD 切片]
- 本轮文件：`file_a`, `file_b`
- 替换说明：
  - `新文件 / 新入口 / 新边界` 替换或准备替换 `旧文件 / 旧入口 / 旧字段 / 旧职责`
- 兼容保留：
  - 本轮仍保留的旧路径、旧容器或旧副作用
- 下一步：
  - 下一轮应继续收口的旧路径
```

## 2026-06-11 09:16 +08:00 - US-001
- Files changed: `scripts/ralph/investigations/2026-06-11-US-001-phase3-blocker-scope.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/prd.json`
- Replacement note:
  - This story only reconfirms the Phase 3 blocker / retained-boundary state and does not replace a live production formula path.
  - The investigation packet prepares the next oracle-inventory slice to replace ad hoc Phase 3 Go/No-Go judgment with explicit blocker evidence.
- Compatibility retained:
  - Production formula replacement remains No-Go at story start.
  - Retained boundaries stay unchanged: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, `buff_add()`, and `KickOutBuff()`.
- Next step:
  - `US-002` should inventory existing oracle evidence and exact remaining blockers before any bounded production replacement proposal.

## 2026-06-11 09:26 +08:00 - US-002
- Files changed: `scripts/ralph/investigations/2026-06-11-US-002-oracle-evidence-inventory.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - This story only inventories existing oracle / parity evidence and does not replace a live production formula path.
  - The investigation packet replaces ad hoc blocker discussion with an explicit map from current evidence to missing blocker-specific cases.
- Compatibility retained:
  - Production formula replacement remains No-Go.
  - `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied-output classes, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, `buff_add()`, and `KickOutBuff()` remain retained boundaries.
- Next step:
  - `US-003` should add deterministic oracle cases for `Calculator.AnomalyMul.cal_res_pen()` before any bounded production replacement proposal.
---

## 2026-06-11 12:12 +08:00 - US-003
- Files changed: `scripts/ralph/investigations/2026-06-11-US-003-bounded-cal-res-pen-proposal.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This story only drafts the bounded replacement proposal and does not replace a live production formula path.
  - `scripts/ralph/investigations/2026-06-11-US-003-bounded-cal-res-pen-proposal.md` prepares to replace the in-method `Calculator.AnomalyMul.cal_res_pen(data)` selector with a later exact bounded selector/extraction, while retaining the current production body as rollback anchor.
- Compatibility retained:
  - `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `anomaly_snapshot`, copied-output constructors, listener/runtime layers, old containers, legacy `buff_add()` / `KickOutBuff()`, and P2-A through P2-G guarded buckets remain unchanged.
- Next step:
  - `US-004` should define focused pytest targets, scoped mypy targets, and the validation contract for the later `cal_res_pen()` implementation PRD without broadening the replacement domain.
---

## 2026-06-11 12:27 +08:00 - US-004
- Files changed: `scripts/ralph/investigations/2026-06-11-US-004-validation-contract.md`, `scripts/ralph/investigations/2026-06-11-US-003-bounded-cal-res-pen-proposal.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 validation contract` replaces implicit future acceptance-gate assumptions with exact focused pytest, scoped mypy, `formula-parity`, and retained `calculator-reads` serial validation commands for the bounded `Calculator.AnomalyMul.cal_res_pen()` proposal.
  - This story builds a proposal validation boundary only; it does not replace a live production formula path, validation runner wiring, copied-output constructor, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, listener/runtime layers, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing validation-runner profile wiring all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-005 by adding registered behavior sample conditions and rollback anchors to the same bounded proposal without implementing production formula changes.
---

## 2026-06-11 12:41 +08:00 - US-005
- Files changed: `scripts/ralph/investigations/2026-06-11-US-005-sample-rollback-plan.md`, `scripts/ralph/investigations/2026-06-11-US-003-bounded-cal-res-pen-proposal.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 sample conditions and rollback plan` replaces implicit future behavior-sample assumptions with explicit rules: main-loop consistency is required only after a live `Calculator.AnomalyMul.cal_res_pen()` semantic diff exists, no validation-only team should be created, and retained sample evidence must prove nonzero relevant anomaly/disorder event counts.
  - This story builds a proposal validation / rollback boundary only; it does not replace a live production formula path, validation runner wiring, registered team fixture, copied-output constructor, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder handlers, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation gates all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-006 by running the serial proposal validation gate and recording command outcomes without adding production formula code, validation-only teams, or runtime switching.
---

## 2026-06-05 - 调查型 PRD 收口基线

- 本轮文件：`docs/旧Buff系统耦合审查结果.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 本轮未直接替换旧 Buff 运行路径；当前交付的是生命周期、事件模型、runtime seam、Calculator seam 与验证入口的调查结论，用来约束下一轮实现型 PRD 的真实替换动作。
- 兼容保留：
  - `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` 仍是计划事件的旧发布入口。
  - `exist_buff_dict` / `DYNAMIC_BUFF_DICT` / `LOADING_BUFF_DICT` 仍是旧 runtime 容器主事实源。
  - `Calculator` 对 `MultiplierData` 的直接依赖仍保留，尚未切到独立属性读取接口。
- 下一步：
  - 下一轮优先落地事件发布入口、`EventContext` runtime view 与最小适配层，并从该轮开始在本文档记录真实的新旧路径替换关系。
---
## 2026-06-09 13:34 +08:00 - US-009
- Files changed: `tests/simulator/test_buffaddstrategy_character_callers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buffaddstrategy_character_callers.py` now replaces manual Character manager `buff_add_strategy(...)` caller review with focused tests for Seed EX-state explicit-target/count forwarding, Yanagi stance forwarding, branch/no-op gating, `sim_instance` forwarding, and caller-layer guardrails.
  - This story locks existing Character manager caller behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - Character manager source files, Seed EX-state transitions, Yanagi stance toggling, Yanagi anomaly/cinema gates, AstraYao core-passive target selection, and AstraYao adjacent scheduled preload publishing remain unchanged.
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff write boundary for Character manager callers.
  - `LOADING_BUFF_DICT` pending queues, scheduled publish, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F Character manager caller coupling.
- Next step:
  - Continue with US-010 by strengthening cross-layer boundary semantics without broadening into source rewrites or Character manager implementation changes.
---
## 2026-06-09 13:46 +08:00 - US-010
- Files changed: `tests/simulator/test_bypass_layer_semantics.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_bypass_layer_semantics.py` now replaces manual P2-F cross-layer boundary review with focused tests for automatic target fan-out, explicit `benifit_list` override, enemy debuff mirror sync, and layer-separation guards.
  - The new boundary test prepares to replace any future ambiguity between forced same-tick Buff / Debuff writes and scheduled publish, listener broadcast, runtime command, or read-port behavior.
  - This story locks existing behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - `LOADING_BUFF_DICT` pending queues, `ScheduleDispatchPort` scheduled backlog, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, P2-G direct simulator context helpers, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F cross-layer boundary coupling.
- Next step:
  - Continue with US-011 by adding the P2-F exact-file source guardrail and validation wiring without broadening completed P2-A / P2-B / P2-C / P2-D / P2-E guardrails.
---
## 2026-06-09 14:07 +08:00 - US-011
- Files changed: `tests/simulator/test_migrated_p2f_buff_add_strategy_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_p2f_buff_add_strategy_guardrail.py` replaces manual P2-F source review with an exact-file AST guardrail for `BuffAddStrategy.py` forced-write conversions and `BuffRuntimeReadPort` write-style API regressions.
  - `scripts/run_buff_refactor_validation.py` now wires the P2-F guardrail into `implicit-events` focused pytest and scoped mypy.
- Compatibility retained:
  - `BuffAddStrategy.py` facade construction from legacy containers, beneficiary selection registry reads, template clone registry compatibility, and inactive diagnostic helper behavior remain covered by the existing raw-container guardrail buckets.
  - `ScheduledEvent/buff_runtime.py` remains the retained `LegacyBuffRuntimeFacade` implementation; this story protects the read-port API contract without outlawing facade internals.
  - No production behavior, P2-A / P2-B / P2-C / P2-D / P2-E guardrail allowlists, old-container deletion boundaries, scheduled publish semantics, listener broadcast semantics, or second write facade was changed.
- Next step:
  - Continue with US-012 by recording serial validation and the behavior-sample decision for this test-only guardrail slice.
---
## 2026-06-05 13:28:48 - US-001
- 本轮文件：`zsim/sim_progress/data_struct/schedule_dispatch.py`, `tests/simulator/test_schedule_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `ScheduleDispatchPort / LegacyEventListScheduleDispatchAdapter / create_schedule_dispatch_port()` 为 `JudgeTools.find_event_list()` 与 `schedule_data.event_list.append(...)` 之间先铺一层计划事件发布边界，但本轮尚未改写具体生产者。
- 兼容保留：
  - `schedule_data.event_list` 仍是底层计划队列，适配器继续沿用原有 `append` 顺序语义。
  - `JudgeTools.find_event_list()`、`SchedulePreload`、`QuickAssistSystem` 等旧发布路径仍保留，等待后续逐个迁移。
- 下一步：
  - 优先把 `SchedulePreload` 改为通过 dispatch gateway 发布，再继续收拢 `QuickAssistSystem` 等低风险生产者。
---
## 2026-06-05 13:45:10 - US-002
- 本轮文件：`zsim/sim_progress/data_struct/SchedulePreload.py`, `tests/simulator/test_schedule_preload_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `schedule_preload_event_factory()` 现通过 `create_schedule_dispatch_port()` 发布 `SchedulePreload`，替换 `JudgeTools.find_event_list()` + `event_list.append(...)` 的计划事件直写入口。
- 兼容保留：
  - `schedule_data.event_list` 仍是底层计划队列，`LegacyEventListScheduleDispatchAdapter` 继续保持原有 `append` 顺序语义。
  - `QuickAssistSystem` 等其他计划事件生产者仍保留旧直写路径，本轮只迁移 `SchedulePreload`。
- 下一步：
  - 继续把 `QuickAssistSystem` 等低风险计划事件生产者迁到 dispatch gateway。
---
## 2026-06-05 13:55:24 - US-003
- 本轮文件：`zsim/sim_progress/data_struct/QuickAssistSystem/__init__.py`, `tests/simulator/test_quick_assist_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `QuickAssistSystem.answer_assist()` / `spawn_event_group()` 现通过 `create_schedule_dispatch_port()` 发布 `QuickAssistEvent`，替换 QuickAssistSystem 内部直写 `JudgeTools.find_event_list()` + `event_list.append(...)` 的计划事件入口。
- 兼容保留：
  - `schedule_data.event_list` 仍是底层计划队列，`QuickAssistEventHandler` 与既有调度排序逻辑保持不变。
  - `UpdateAnomaly`、`PolarizedAssaultEvent` 等其他计划事件生产者仍保留旧直写路径，本轮只迁移 `QuickAssistSystem`。
- 下一步：
  - 在 `ScheduledEvent` / `EventContext` 上接入 `buff_runtime_view`，开始替换 raw `dynamic_buff` / `exist_buff_dict` 读口。
---
## 2026-06-05 14:08:10 - US-004
- 本轮文件：`zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/sim_progress/ScheduledEvent/__init__.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `tests/simulator/test_buff_runtime_view.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `BuffRuntimeReadPort / LegacyBuffRuntimeReadAdapter / create_buff_runtime_read_port()` 与 `EventContext.buff_runtime_view` 开始替换 `EventContext.dynamic_buff` / `exist_buff_dict` 作为 handler 主读口；兼容 getter 现改为经由 runtime view 委托。
- 兼容保留：
  - `ScheduleData.dynamic_buff`、`exist_buff_dict` 与 `sim_instance` 仍保留在调度链路中，`SkillEventHandler`、`ScheduleBuffSettle()`、`update_anomaly()` 仍通过兼容 getter 读取旧容器。
  - 本轮尚未迁移具体 anomaly-family handler 到 runtime view 的细粒度读方法，只先完成上下文接线与兼容适配。
- 下一步：
  - 让 `anomaly`、`abloom`、`disorder`、`polarity_disorder` 这组低风险 handler 直接通过 `buff_runtime_view` 读取所需 Buff 数据，减少对 raw dict 兼容 getter 的依赖。
---
## 2026-06-05 14:31:15 - US-005
- 本轮文件：`zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/abloom.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/disorder.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/polarity_disorder.py`, `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `BaseEventHandler / EventContext` 新增 active-buff read view accessor，开始替换 anomaly-family handler 对 raw `dynamic_buff` / `exist_buff_dict` 的主读口。
  - `AnomalyEventHandler / AbloomEventHandler / DisorderEventHandler / PolarityDisorderEventHandler` 现通过 `buff_runtime_view` 读取 active Buff；仅 `AnomalyEventHandler -> ScheduleBuffSettle()` 保留 legacy 容器作为同 tick 写边界。
- 兼容保留：
  - `ScheduleBuffSettle()`、`update_anomaly()` 与其他会原地修改容器的旧路径仍通过 legacy getter 读取原始容器，本轮未替换 live write path。
- 下一步：
  - 继续把更高风险的 `skill` handler 等 read path 从 legacy getter 收口到 runtime view，并评估是否需要后续 write facade。
---
## 2026-06-05 18:09:00 - US-006
- 本轮文件：`zsim/utils/main_loop_consistency.py`, `scripts/run_buff_main_loop_consistency.py`, `tests/simulator/test_main_loop_consistency.py`, `scripts/run_buff_refactor_validation.py`, `zsim/define.py`
- 替换说明：
  - `scripts/run_buff_main_loop_consistency.py` / `zsim.utils.main_loop_consistency` 把文档中的主循环一致性占位命令替换成真实可运行入口，并固化 `team / apl / total_damage / event_counts / buff_timeline / differences` 输出契约。
  - `implicit-events` typecheck profile 现纳入该入口与其 utility，开始把“主循环一致性验证命令”本身也收进当前 Buff 基础设施切片的验证边界。
- 兼容保留：
  - 当前 `--legacy-runtime` / `--candidate-runtime` 仅作为报告标签记录；live simulator 仍未消费 `config.buff_runtime.mode`，本轮尚未实现真正的新旧 runtime 切换。
  - 比对命令继续复用现有 `Simulator`、`prepare_dmg_data_and_cache()` 与 `prepare_buff_data_and_cache()` 结果链路，因此 session/result id 仍需保持旧链路兼容的纯数字格式。
- 下一步：
  - 为后续 runtime 切换落地真实的 `legacy/candidate` 执行开关，再让该入口输出真正的新旧 runtime 一致性证据，而不只是同一 runtime 的双跑比较骨架。
---

## 2026-06-05 20:33:37 - US-001
- 本轮文件：`zsim/sim_progress/Update/UpdateAnomaly.py`, `tests/simulator/test_update_anomaly_dispatch.py`
- 替换说明：
  - `UpdateAnomaly.update_anomaly()` / `remove_dots_cause_disorder()` 现通过 `create_schedule_dispatch_port()` 发布 `new_anomaly`、`disorder` 与 freeze follow-up 计划事件，替换该路径里对 `event_list.append(...)` 的直接依赖。
- 兼容保留：
  - `spawn_output()` 仍只负责构造异常对象并触发同步 listener broadcast，本轮没有把广播、计划入队与 runtime 立即写混成单一入口。
  - `PolarizedAssaultEvent`、`YanagiPolarityDisorderTrigger`、`BattleEventListener` 等其他 producer 仍保留 raw 队列写法，等待后续故事继续迁移。
- 下一步：
  - 继续收口 `BattleEventListener` 与其他剩余 producer 的 raw 队列写入口，并评估是否需要让 `spawn_output()` 的其他调用方也统一走 dispatch gateway。
---
## 2026-06-05 18:49:32 - US-007
- 本轮文件：`zsim/utils/runtime_benchmark.py`, `scripts/run_buff_runtime_benchmark.py`, `tests/simulator/test_runtime_benchmark.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `scripts/run_buff_runtime_benchmark.py` / `zsim.utils.runtime_benchmark` 把文档中的 Buff runtime 性能验证占位命令替换成真实可运行入口，并固化 `team / apl / stop_tick / total_runtime_ms / hotspots / comparisons` 输出契约。
  - `implicit-events` typecheck profile 现纳入 benchmark 入口与其 utility，开始把“性能验证命令”本身也收进当前 Buff 基础设施切片的验证边界。
- 兼容保留：
  - 当前 `--legacy-runtime` / `--candidate-runtime` 仍仅作为报告标签记录；live simulator 仍未消费 `config.buff_runtime.mode`，本轮尚未实现真正的新旧 runtime 切换。
  - 本轮 `hotspots` 是 `simulator_run`、damage 报表后处理与 buff 报表后处理三段阶段级计时，不是 live runtime 内部细粒度探针。
- 下一步：
  - 为后续 runtime 切换落地真实的 `legacy/candidate` 执行开关，并在需要时把阶段级 hotspot 继续下钻到 live simulator 内部的真实热点探针。
---
## 2026-06-05 18:57:20 - US-008
- 本轮文件：`docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `docs/旧Buff系统耦合审查结果.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 文档基线现明确记录 `SchedulePreload` / `QuickAssistSystem` 已改经 `ScheduleDispatchPort`，`anomaly` / `abloom` / `disorder` / `polarity_disorder` 已改经 `buff_runtime_view`，以及 `scripts/run_buff_main_loop_consistency.py` / `scripts/run_buff_runtime_benchmark.py` 已替换旧的占位验证入口。
- 兼容保留：
  - 本轮仅同步阶段 1 基线文档与 PRD 状态，未新增 live runtime 替换路径。
  - `UpdateAnomaly`、`BattleEventListener`、部分 `BuffXLogic` / `PolarizedAssaultEvent` 计划事件生产者仍保留旧直写路径；高风险 `skill` handler 与 runtime write facade 仍未收口。
- 下一步：
  - 下一轮继续留在阶段 1，收口剩余计划事件生产者与高风险 read/write 边界，不扩到 `Calculator` 全量迁移或旧容器删除。
---
## 2026-06-05 20:50:55 - US-002
- 本轮文件：`zsim/sim_progress/data_struct/BattleEventListener/AliceDotTriggerListener.py`, `tests/simulator/test_alice_dot_trigger_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `AliceDotTriggerListener._create_dispatch_port()` / `dispatch_port.publish_scheduled(dot.anomaly_data)` 开始替换 `BattleEventListener` 内部 Alice 强击 Dot 对 `schedule_data.event_list.append(...)` 的直接计划事件发布入口
- 兼容保留：
  - 同 tick 的 Dot 替换、旧 Dot 移除以及 `listener_manager` 同步广播触发链保持不变；底层计划队列仍由 `LegacyEventListScheduleDispatchAdapter` 追加
- 下一步：
  - 继续收口 `PolarizedAssaultEvent`、代表性 `BuffXLogic` 等剩余 raw 队列 producer；本轮尚未替换 live runtime 写边界
---
## 2026-06-05 21:29:15 - US-003
- 本轮文件：`zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `tests/simulator/test_buff_runtime_view.py`
- 替换说明：
  - `EventContext.get_runtime_*()` / `BaseEventHandler._get_context_runtime_*()` 开始把 `buff_runtime_view` 的 active-buff 与 snapshot 读口显式提升为高风险 handler 可直接依赖的主读契约，减少后续迁移继续默认使用 `dynamic_buff` / `exist_buff_dict` 兼容 getter。
- 兼容保留：
  - `get_dynamic_buff()`、`get_exist_buff_dict()` 与 `get_legacy_*()` 仍保留旧容器身份，仅标记为同 tick 写边界兼容口；本轮没有引入新的 write facade，也没有替换 `ScheduleBuffSettle()`、`update_anomaly()` 等 live write path。
- 下一步：
  - 继续挑选一个高风险 `skill` handler 切到 `get_runtime_*()` 读口，并只在确实需要同 tick 原地写旧容器时保留 legacy getter。
---

## 2026-06-05 21:45:20 - US-004
- 本轮文件：`zsim/sim_progress/ScheduledEvent/event_handlers/handlers/skill.py`, `tests/simulator/test_skill_handler_runtime_view.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `SkillEventHandler` 现在把 `buff_runtime_view.get_active_buff_view()` 作为 `Calculator` 与 `update_anomaly()` 的主 Buff 读口，准备替换技能事件处理路径对 raw `dynamic_buff` 的默认依赖。
- 兼容保留：
  - `ScheduleBuffSettle()` 仍通过 `get_legacy_dynamic_buff_dict()` / `get_legacy_exist_buff_dict()` 拿旧容器身份；本轮没有引入新的 write facade，也尚未替换同 tick 写边界。
- 下一步：
  - 继续收口剩余高风险 skill-side read/write 边界，只在确实需要同 tick 写旧容器的地方再评估最小 write facade。
---
## 2026-06-05 22:25:00 - US-005
- 本轮文件：`docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `docs/旧Buff系统耦合审查结果.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 本轮没有新增 live runtime 替换路径；只同步阶段 1 交接基线，明确 `UpdateAnomaly` 与 `BattleEventListener` 中的 `AliceDotTriggerListener` 已改经 `ScheduleDispatchPort`，`SkillEventHandler` 已把 runtime view 作为主 Buff 读口。
- 兼容保留：
  - 代表性 `BuffXLogic` / `PolarizedAssaultEvent` 与其余未迁移监听器入口仍保留 raw 队列发布；`ScheduleBuffSettle()`、`update_anomaly()` 等同 tick 写边界仍依赖 legacy 容器身份，本轮没有引入新的 write facade。
  - `--legacy-runtime` / `--candidate-runtime` 仍只是报告标签，live simulator 尚未消费 `config.buff_runtime.mode`。
- 下一步：
  - 继续沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段 1 路线，优先收口代表性 `BuffXLogic` / `PolarizedAssaultEvent` producer 与同 tick 写边界的最小 write facade / command port。
---
## 2026-06-05 23:39:09 - US-001
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/AlicePolarizedAssaultTrigger.py`、`tests/simulator/test_alice_polarized_assault_trigger_dispatch.py`、`scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `AlicePolarizedAssaultTrigger._create_dispatch_port()` / `dispatch_port.publish_scheduled(event)` 替换 `AlicePolarizedAssaultTrigger.special_effect_logic()` 内对 `schedule_data.event_list.append(...)` 的直接 planned-event 写入。
- 兼容保留：
  - `PolarizedAssaultEvent.execute()` 里的 anomaly / disorder follow-up planned events 仍直接写 `event_list.append(...)`。
  - `listener_manager.broadcast_event()` 的同步广播语义未改动，本轮只收口 planned-event 入队边界。
- 下一步：
  - 继续把 `PolarizedAssaultEvent` 的 follow-up producer 迁到 dispatch gateway，完成这条代表性事件链的收口。
---
## 2026-06-05 23:51:20 - US-002
- 本轮文件：`zsim/sim_progress/data_struct/PolarizedAssaultEventClass.py`、`tests/simulator/test_polarized_assault_event_dispatch.py`、`scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `PolarizedAssaultEvent._create_dispatch_port()` / `dispatch_port.publish_scheduled(...)` 替换 `PolarizedAssaultEvent.execute()` 内 anomaly 与 disorder follow-up planned-event 对 `schedule_data.event_list.append(...)` 的直写入口
- 兼容保留：
  - `listener_manager.broadcast_event()` 的同步广播语义与 `anomaly_effect_active()` 的同 tick 状态更新顺序保持不变
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 作为底层计划队列承接
- 下一步：
  - 继续为 `SkillEventHandler` 引入最小 write facade / command port，收口 `update_anomaly()` 与 `ScheduleBuffSettle()` 的同 tick 写边界
---
## 2026-06-06 00:22:24 - US-003
- 本轮文件：`zsim/sim_progress/ScheduledEvent/runtime_command.py`、`zsim/sim_progress/ScheduledEvent/__init__.py`、`zsim/sim_progress/ScheduledEvent/event_handlers/context.py`、`zsim/sim_progress/ScheduledEvent/event_handlers/base.py`、`tests/simulator/test_runtime_command_port.py`、`scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `RuntimeCommandPort / LegacyRuntimeCommandAdapter / create_runtime_command_port()` 先把 `update_anomaly()` 与 `ScheduleBuffSettle()` 包进显式 same-tick 写边界，为后续替换 `SkillEventHandler` 对 `get_legacy_*()` 的默认写协作做准备
- 兼容保留：
  - `SkillEventHandler`、`AnomalyEventHandler` 目前仍通过 legacy getter 间接走旧写路径，本轮只新增边界并把它接进 `ScheduledEvent` / `EventContext`
  - `event_list`、`dynamic_buff`、`exist_buff_dict` 仍由旧容器承载；新端口只保持对象身份并避免缓存过期队列引用
- 下一步：
  - 在 `US-004` 把 `SkillEventHandler` 的 same-tick `update_anomaly()` / `ScheduleBuffSettle()` 调用改为显式走 `runtime_command_port`
---
## 2026-06-06 00:42:45 - US-004
- 本轮文件：`zsim/sim_progress/ScheduledEvent/event_handlers/handlers/skill.py`、`zsim/sim_progress/ScheduledEvent/runtime_command.py`、`tests/simulator/test_skill_handler_runtime_view.py`、`tests/simulator/test_runtime_command_port.py`
- 替换说明：
  - `SkillEventHandler` 现通过 `RuntimeCommandPort.update_anomaly()` / `RuntimeCommandPort.settle_buffs()` 替换处理器内部默认依赖 legacy getter 再直连 `update_anomaly()` / `ScheduleBuffSettle()` 的 same-tick 写协作路径
- 兼容保留：
  - `RuntimeCommandPort` 仍由 `LegacyRuntimeCommandAdapter` 承接旧 `event_list`、`dynamic_buff`、`exist_buff_dict` 身份，只在适配器内部保留旧写路径兼容
  - 本轮没有替换 live runtime 容器本身，只把 `SkillEventHandler` 的读写分层显式化
- 下一步：
  - 继续补强代表性 producer 与 write-boundary 组合的 focused validation，并保持后续 handler 迁移沿用 `runtime view` 读、`runtime command` 写的边界
---
## 2026-06-06 00:59:56 - US-005
- 本轮文件：`scripts/run_buff_refactor_validation.py`, `tests/simulator/test_skill_handler_runtime_view.py`, `tests/simulator/test_basic_simulator.py`
- 替换说明：
  - `scripts/run_buff_refactor_validation.py` 里的 `implicit-events` focused pytest 切片开始替换 `progress.txt` 中零散的一次性命令，作为代表性 `BuffXLogic` producer / `PolarizedAssaultEvent` producer / same-tick write-boundary 的共享验证入口。
  - `test_skill_handler_runtime_view.py` 新增 `SkillEventHandler -> RuntimeCommandPort -> legacy containers` 身份断言，开始替换“只证明调用发生、但不证明旧容器身份仍被保留”的隐含假设。
  - `test_basic_simulator.py` 把导入的 `TestSimulator` helper 改成非 `Test*` 别名，替换 pytest 对 `tests/test_simulator.py` 整套异步队列 / 内存用例的误收集路径。
- 兼容保留：
  - 本轮没有新增 live runtime 路径替换；`ScheduleDispatchPort` 与 `RuntimeCommandPort` 仍通过 legacy adapters 承接旧队列和旧容器身份。
  - 验证脚本只清理共享 `sessions` 表来消除重复 `session_id` 噪音，没有改动 simulator 真实运行时的数据结构或业务顺序。
- 下一步：
  - `US-006` 应把“代表性 producer 链已闭合、same-tick write facade 已落地、focused validation 已固化进共享 gate”同步进阶段 1 handoff 文档。
---
## 2026-06-06 01:17:59 - US-006
- 本轮文件：docs/Buff系统重构Checklist.md, docs/Buff重构下阶段计划草稿.md, docs/Buff重构替换说明.md, docs/旧Buff系统耦合审查结果.md, scripts/ralph/prd.json, scripts/ralph/progress.txt
- 替换说明：
  - 阶段 1 handoff 文档现已明确把代表性 AlicePolarizedAssaultTrigger -> PolarizedAssaultEvent planned-event 链标记为“已改经 ScheduleDispatchPort 的真实替换边界”，替换此前“代表性 producer 仍待后续收口”的旧基线表述。
  - 阶段 1 handoff 文档现已明确把 SkillEventHandler -> RuntimeCommandPort -> LegacyRuntimeCommandAdapter 标记为“已落地的 same-tick 显式写边界”，替换此前“ScheduleBuffSettle() / update_anomaly() 仍未引入新 write facade”的旧基线表述。
  - scripts/ralph/prd.json、docs/*handoff 与 scripts/ralph/progress.txt 现已统一把 implicit-events 视为这组代表性 producer / write-boundary 样本的共享验证入口，而不是散落在进度记录里的临时命令集合。
- 兼容保留：
  - 本轮只同步 handoff 基线，没有新增 live runtime 路径替换；ScheduleDispatchPort 与 RuntimeCommandPort 仍通过 legacy adapters 承接旧队列和旧容器身份。
  - --legacy-runtime / --candidate-runtime 仍只是报告标签；在 live simulator 真正消费 config.buff_runtime.mode 前，文档与后续 PRD 仍不得把它们写成真实 runtime 切换开关。
  - 其余未迁移的 BuffXLogic、BattleEventListener、Character 旁路 producer 与相邻 same-tick 高风险写路径仍保留旧入口，本轮没有假装这些边界已经替换完成。
- 下一步：
  - 下一轮继续沿阶段 1 路线，收口其他 raw event_list bypass 与必要的相邻 RuntimeCommandPort 样本，不扩到 Calculator 全量迁移或旧容器删除。
---
## 2026-06-06 08:40:07 - US-001
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py`, `zsim/sim_progress/Buff/BuffXLogic/LunarNoviluna.py`, `tests/simulator/test_xstart_sp_refresh_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `ElegantVanitySpRecover._create_dispatch_port()` / `LunarNoviluna._create_dispatch_port()` 开始替换这两个 xstart SP refresh producer 对 `JudgeTools.find_event_list()` 与 `event_list.append(...)` 的 planned-event 直写入口。
  - `tests/simulator/test_xstart_sp_refresh_dispatch.py` 开始替换“这类低风险 SP refresh producer 顺序都一样”的隐含假设，显式固定 `ElegantVanitySpRecover` 的 `simple_start() -> publish` 与 `LunarNoviluna` 的 `publish -> simple_start()` 兼容顺序。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列和 append 语义没有被改写。
  - 本轮只关闭 xstart SP refresh producer 的 raw queue bypass，`MagneticStormCharlieSpRecover`、`SeedAdditionalAbilityTrigger` 等后续 producer 仍保留旧入口，尚未替换 live runtime 路径。
- 下一步：
  - 继续按同样模式收口 `US-002` 的 xhit SP refresh producer，并把新的 focused regression 继续并入 `implicit-events` 共享验证入口。
---
## 2026-06-06 08:56:11 - US-002
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/MagneticStormCharlieSpRecover.py`, `zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py`, `tests/simulator/test_xhit_sp_refresh_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `MagneticStormCharlieSpRecover._create_dispatch_port()` 与 `SeedAdditionalAbilityTrigger._create_dispatch_port()` 现在替换 xhit SP refresh producers 对 `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` 的 raw planned-event 发布路径。
  - `tests/simulator/test_xhit_sp_refresh_dispatch.py` 现在证明两种 legacy queue bypass 风格都被阻断，同时保留 `simple_start()`、vanguard 目标选择与 `last_active_tick` 语义。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列和 append 语义没有变化。
  - 本轮只关闭 xhit SP refresh raw-queue bypass；`SliceofTimeExtraResources`、`CannonRotor` 以及后续 producer 仍保留旧入口。
- 下一步：
  - `US-003` 继续复用同样的 focused no-raw-queue 回归形态，同时保留 mixed SP/decibel payload 契约。
---
## 2026-06-06 09:28:11 - US-003
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/SliceofTimeExtraResources.py`, `tests/simulator/test_slice_of_time_extra_resources_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `SliceofTimeExtraResources._create_dispatch_port()` / `dispatch_port.publish_scheduled(refresh_data)` 现在替换该 mixed refresh producer 对 `JudgeTools.find_event_list()` 与 `event_list.append(...)` 的 planned-event 直写入口。
  - `tests/simulator/test_slice_of_time_extra_resources_dispatch.py` 显式固定 `simple_start() -> publish` 顺序，并同时验证同一份 `ScheduleRefreshData` 里的 `sp_target / sp_value / decibel_target / decibel_value` 没有在 gateway 迁移中丢失。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列和 append 语义没有变化。
  - 本轮只关闭 `SliceofTimeExtraResources` 的 raw queue bypass；`CannonRotor`、`YanagiPolarityDisorderTrigger`、`HugoCorePassiveTotalizeTrigger` 和 `DecibelManager` 仍保留旧入口。
- 下一步：
  - 继续按同样的 focused no-raw-queue 迁移模式收口 `US-004` 的 `CannonRotor`，但要切换到 follow-up `SkillNode` 发布链的顺序断言而不是 refresh payload 断言。
---
## 2026-06-06 11:29:59 - US-004
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py`, `tests/simulator/test_cannon_rotor_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `CannonRotor._create_dispatch_port()` / `dispatch_port.publish_scheduled(node)` 现在替换 `CannonRotor.special_hit_logic()` 对 `JudgeTools.find_event_list()` 与 `event_list.append(node)` 的 follow-up `SkillNode` 直写入口。
  - `tests/simulator/test_cannon_rotor_dispatch.py` 显式固定 `LoadingMission.mission_start(...) -> publish -> simple_start(...)` 顺序，确保 `whole_skill_tag`、preload tick 和 mission 初始化没有在 gateway 迁移中漂移。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列和 append 语义没有变化。
  - 本轮没有扩到 `CannonRotor` 的 `MultiplierData` 读路径；Calculator seam 与暴击判定逻辑保持原样。
- 下一步：
  - 继续收口 `US-005` 的 `YanagiPolarityDisorderTrigger` raw queue bypass，但要转到 anomaly `spawn_output(...)` 发布链而不是复用 `SkillNode` harness。
---
## 2026-06-06 12:06:25 - US-005
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/YanagiPolarityDisorderTrigger.py`, `tests/simulator/test_yanagi_polarity_disorder_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `YanagiPolarityDisorderTrigger._create_dispatch_port()` / `dispatch_port.publish_scheduled(polarity_disorder_output)` 现在替换 `YanagiPolarityDisorderTrigger.special_effect_logic()` 对 `event_list.append(...)` 的 polarity-disorder planned-event 直写入口。
  - `tests/simulator/test_yanagi_polarity_disorder_dispatch.py` 显式固定 `release -> spawn_output(...) -> publish -> cleanup` 链，并验证发布前使用的是已 `anomaly_settled()` 的 anomaly deepcopy，而不是原始 active bar。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列和 append 语义没有变化。
  - 本轮只关闭 `YanagiPolarityDisorderTrigger` 的 raw queue bypass；`HugoCorePassiveTotalizeTrigger` 和 `DecibelManager` 仍保留旧入口，`spawn_output(...)` 本身的 anomaly 业务计算也没有改写。
- 下一步：
  - 继续收口 `US-006` 的 `HugoCorePassiveTotalizeTrigger` `totalize_node` 发布分支，并保留 `buff_add_strategy(...)` 先于 planned-event 发布的顺序边界。
---
## 2026-06-06 12:34:58 - US-006
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py`, `tests/simulator/test_hugo_totalize_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `HugoCorePassiveTotalizeTrigger._create_dispatch_port()` / `dispatch_port.publish_scheduled(totalize_node)` 现在替换 `special_hit_logic()` 里 `totalize_node` 对 `event_list.append(...)` 的 planned-skill 直写入口。
- 兼容保留：
  - 条件 `StunForcedTerminationEvent` 分支仍保留 `JudgeTools.find_event_list()` / `event_list.append(...)`，本轮只关闭 `totalize_node` 这条 planned-event bypass，尚未替换第二条分支。
  - `buff_add_strategy(...)` 的即时运行态写入、`active_signal == 0` 的早退路径，以及底层 `schedule_data.event_list` 的 append 语义都保持不变。
- 下一步：
  - 继续收口 `US-007` 的 `StunForcedTerminationEvent` 条件发布分支，并显式验证 2 影大招不终结失衡的跳过路径。
---
## 2026-06-06 12:50:41 - US-007
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/HugoCorePassiveTotalizeTrigger.py`, `tests/simulator/test_hugo_totalize_dispatch.py`
- 替换说明：
  - `HugoCorePassiveTotalizeTrigger.special_hit_logic()` 现在复用同一个按需 `dispatch_port`，把条件 `StunForcedTerminationEvent` 和已迁移的 `totalize_node` 一并通过 `publish_scheduled(...)` 发布，替换最后一条 `event_list.append(stun_event)` planned-event 直写入口。
- 兼容保留：
  - `buff_add_strategy(...)` 的同步副作用、`LoadingMission.mission_start(...)` 初始化时序、以及“2 影大招不终结失衡”的分支跳过语义都保持不变。
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接；本轮只是关闭 Hugo 最后一条 raw queue bypass，没有改写底层队列 append 语义。
- 下一步：
  - 继续收口 `US-008` 的 `DecibelManager` planned-event 发布入口；Hugo 这条高风险 producer 的两条 planned-event 分支现已都闭合到 dispatch gateway。
---
## 2026-06-06 15:45:40 - US-008
- 本轮文件：`zsim/sim_progress/data_struct/DecibelManager/DecibelManagerClass.py`, `tests/simulator/test_decibel_manager_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `DecibelManager._create_dispatch_port()` / `publish_scheduled(refresh_data)` 现在替换 `DecibelManager.add_decibel_to_char()` 对 `schedule_data.event_list.append(...)` 的喧响值刷新 planned-event 直写入口。
  - `tests/simulator/test_decibel_manager_dispatch.py` 显式固定 major/minor 分组后的完整 fan-out 事件数与每个 payload，避免 gateway 迁移后只验证单个 recipient 的假阳性。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列与 append 语义保持不变。
  - 本轮只关闭相邻非 Buff producer `DecibelManager` 的 raw queue bypass，没有扩到新的 same-tick write facade 或 live runtime 路径替换。
- 下一步：
  - 继续收口 `US-009` 的 shared `implicit-events` 验证盲区，把 focused dispatch/runtime-boundary 回归文件本身也纳入共享 gate。
---
## 2026-06-06 13:52:21 - US-009
- 本轮文件：`scripts/run_buff_refactor_validation.py`, `tests/simulator/test_schedule_dispatch.py`, `tests/simulator/test_xstart_sp_refresh_dispatch.py`, `tests/simulator/test_cannon_rotor_dispatch.py`, `tests/simulator/test_yanagi_polarity_disorder_dispatch.py`, `tests/simulator/test_skill_handler_runtime_view.py`, `tests/simulator/test_runtime_command_port.py`
- 替换说明：
  - `implicit-events` 共享 gate 现在会直接运行 `test_schedule_dispatch.py`，并对 focused dispatch/runtime-boundary 回归文件本身执行 scoped mypy，不再只类型检查它们命中的生产模块。
  - 上述 focused harness 里的 fake-runtime override 现统一改成 `monkeypatch.setattr(...)` 或窄 `cast(...)` seam，替换会通过 pytest 但会被 mypy 视为 `method-assign` 的直接方法改写。
- 兼容保留：
  - 本轮没有新增 live runtime 路径替换；`ScheduleDispatchPort` 与 `RuntimeCommandPort` 仍通过 legacy adapters 承接旧队列与旧容器身份。
  - 验证命令仍需串行执行；并发跑多个 `run_buff_refactor_validation.py` profile 会共享 sqlite `sessions` 数据与异步日志写线程，制造与迁移代码无关的假失败。
- 下一步：
  - 继续收口 `US-010` 的阶段 1 handoff 文档，把已闭合的 producer batch、共享验证基线与剩余 backlog 同步到 Ralph 工件。
---
## 2026-06-06 16:13:05 - US-010
- 本轮文件：`docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 阶段 1 handoff 文档现已明确记录本轮闭合的剩余 producer batch：`ElegantVanitySpRecover`、`LunarNoviluna`、`MagneticStormCharlieSpRecover`、`SeedAdditionalAbilityTrigger`、`SliceofTimeExtraResources`、`CannonRotor`、`YanagiPolarityDisorderTrigger`、`HugoCorePassiveTotalizeTrigger` 与 `DecibelManager`，替换此前仍把这些 callsite 当成待后续收口的旧表述。
  - 文档现已同步写出 shared `implicit-events` 基线：不仅要跑 focused pytest，也要把 focused dispatch/runtime-boundary 回归文件本身纳入 scoped mypy；同时继续明确 `--legacy-runtime` / `--candidate-runtime` 在 live simulator 真正消费 `config.buff_runtime.mode` 前都只是报告标签。
- 兼容保留：
  - 本轮只是同步真实 handoff 基线，并没有宣布阶段 1 完成；剩余缺口仍是其他 one-off `BuffXLogic` / `Character` raw `event_list` producer，以及后续若继续暴露出来的 same-tick 高风险写路径。
- 下一步：
  - 下一轮 PRD 继续停留在阶段 1，优先扫描剩余 one-off planned-event producer，并且只在确实暴露新 same-tick 协作时才沿用 `RuntimeCommandPort` 扩边界。
---

## 2026-06-06 18:05:08 - US-001
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py`, `tests/simulator/test_miyabi_core_skill_icefire_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `MiyabiCoreSkill_IceFire._create_dispatch_port()` / `publish_scheduled(skill_node)` 现在替换 `special_exit_logic()` 中霜灼上升沿 follow-up `SkillNode` 对 `JudgeTools.find_event_list()` / `event_list.append(skill_node)` 的 raw planned-event 发布路径。
  - `tests/simulator/test_miyabi_core_skill_icefire_dispatch.py` 固定 `publish -> special_resources(skill_node)` 顺序，并证明同一个 frostbite 状态不会重复发布。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列语义没有变化。
  - 本轮不触碰 `special_hit_logic()` 的 `MultiplierData` / `Calculator.RegularMul.cal_crit_rate(...)`，也没有新增 same-tick write facade。
- 下一步：
  - 继续收口 `YixuanCinema1Trigger` 落雷 `SkillNode` 发布路径，同时保留 `LoadingMission` 与闪能恢复顺序。
---
## 2026-06-06 19:14:16 - US-002
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/YixuanCinema1Trigger.py`, `tests/simulator/test_yixuan_cinema1_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `YixuanCinema1Trigger._create_dispatch_port()` / `publish_scheduled(lightning_strick_node)` 现在替换 `special_hit_logic()` 中落雷 `SkillNode` 对 `schedule_data.event_list.append(lightning_strick_node)` 的直接 planned-event 写入路径。
  - `tests/simulator/test_yixuan_cinema1_dispatch.py` 在禁用 raw queue append 时固定 `LoadingMission.mission_start(...) -> publish -> update_adrenaline(sp_value=5) -> simple_start(...)` 顺序。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列 append 语义没有变化。
  - `char.update_adrenaline(sp_value=5)` 仍是现有 Character 资源恢复调用；本轮没有新增第二套 same-tick write facade，也没有改动 `RuntimeCommandPort`。
- 下一步：
  - 继续收口 `VivianDotTrigger` 的 dot `SkillNode` 发布路径，同时保持 planned-skill 发布与 dot runtime registration 分层。
---
## 2026-06-06 19:55:44 - US-003
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py`, `tests/simulator/test_vivian_dot_trigger_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `VivianDotTrigger._create_dispatch_port()` / `publish_scheduled(dot.skill_node_data)` 现在替换 `special_hit_logic()` 中 dot follow-up `SkillNode` 对 `JudgeTools.find_event_list()` / `event_list.append(dot.skill_node_data)` 的 raw planned-event 发布路径。
  - `tests/simulator/test_vivian_dot_trigger_dispatch.py` 在禁用 raw queue lookup 与 append 时固定 `dot.start(...) -> LoadingMission.mission_start(...) -> enemy.dynamic.dynamic_dot_list.append(dot) -> publish` 顺序。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列 append 语义没有变化。
  - Dot runtime registration 仍使用现有 `enemy.dynamic.dynamic_dot_list.append(dot)` 路径；本轮没有新增 facade，也没有改动 `spawn_normal_dot("ViviansProphecy", ...)`。
- 下一步：
  - 继续收口 `VivianCorePassiveTrigger` 异常输出发布路径，同时保留现有 anomaly clone 与 Calculator 读取路径。
---
## 2026-06-06 21:06:06 - US-004
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py`, `tests/simulator/test_vivian_core_passive_trigger_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `VivianCorePassiveTrigger._create_dispatch_port()` / `publish_scheduled(dirge_of_destiny_anomaly)` 现在替换 `special_effect_logic()` 中 `DirgeOfDestinyAnomaly` 对 `JudgeTools.find_event_list()` / `event_list.append(dirge_of_destiny_anomaly)` 的 raw planned-event 发布路径。
  - `tests/simulator/test_vivian_core_passive_trigger_dispatch.py` 在禁用 raw queue lookup 与 append 时固定 cloned anomaly settlement、`active_by="1331"` 归一化、`anomaly_dmg_ratio` 与单次 gateway publish 语义。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列 append 语义没有变化。
  - Active anomaly cloning、`anomaly_settled()`、`MultiplierData` 与 `Calculator.AnomalyMul.cal_ap(...)` 仍保留现有业务路径；本轮没有新增 same-tick write facade，也没有改动 Dirge 公式。
- 下一步：
  - 继续收口 `VivianCinema6Trigger`，保留无异常时的资源分支，同时只把额外异常输出分支改经 dispatch gateway。
---
## 2026-06-06 21:21:50 - US-005
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py`, `tests/simulator/test_vivian_cinema6_trigger_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `VivianCinema6Trigger._create_dispatch_port()` / `publish_scheduled(dirge_of_destiny_anomaly)` 现在替换 `special_effect_logic()` 中条件性额外 `DirgeOfDestinyAnomaly` 对 `JudgeTools.find_event_list()` / `event_list.append(dirge_of_destiny_anomaly)` 的 raw planned-event 发布路径。
  - `tests/simulator/test_vivian_cinema6_trigger_dispatch.py` 在禁用 raw queue lookup 与 append 时固定发布与不发布两个分支。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列 append 语义没有变化。
  - `guard_feather` 消耗、`c1_counter` / `flight_feather` 更新、active anomaly cloning、`anomaly_settled()`、`MultiplierData`、`Calculator.AnomalyMul.cal_ap(...)` 与现有 `feather_manager.update_myself(c6_signal=True)` 资源路径都保持不变；本轮没有新增 same-tick write facade。
- 下一步：
  - 继续收口 `Character/Yuzuha` cinema-6 全队回能 fan-out，同时保留队友目标与 25 点能量语义。
---

## 2026-06-06 21:57:39 - US-006
- 本轮文件：`zsim/sim_progress/Character/Yuzuha/__init__.py`, `tests/simulator/test_yuzuha_cinema6_energy_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明：
  - `Yuzuha._create_dispatch_port()` / `publish_scheduled(schedule_refresh_event)` 现在替换 `special_resources()` 中 cinema-6 全队回能 fan-out 对 `sim_instance.schedule_data.event_list.append(schedule_refresh_event)` 的直接 planned-event 写入路径。
  - `tests/simulator/test_yuzuha_cinema6_energy_dispatch.py` 在禁用 raw queue append 时固定队友 fan-out 数量、Yuzuha 自身排除、目标顺序与 `ScheduleRefreshData(sp_value=25)` payload 语义。
- 兼容保留：
  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 承接，底层 planned-event 队列 append 语义没有变化。
  - `broadcast_and_update(...)`、sugar point 处理、`hard_candy_shot` 与其他非 cinema-6 分支保持不变；本轮没有新增 same-tick write facade。
- 下一步：
  - 继续收口 `US-007` 的 shared `implicit-events` 验证扩展，覆盖本轮剩余 bypass producer batch。
---

## 2026-06-06 22:10:04 - US-007
- 本轮文件：`scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- 替换说明：
  - `REMAINING_BYPASS_PRODUCER_TARGETS` 与 `REMAINING_BYPASS_FOCUSED_TEST_TARGETS` 让 shared `implicit-events` 验证 gate 显式替换此前散落在各 story runner 中的条目，覆盖已迁移的 `MiyabiCoreSkill_IceFire`、`YixuanCinema1Trigger`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger` 与 `Character/Yuzuha` producer batch。
  - 本轮只建立并验证 shared validation boundary，没有替换新的 live raw queue writer。
- 兼容保留：
  - 现有 dispatch gateway adapter、focused no-raw-queue 回归与底层 planned-event 队列语义保持不变。
  - 本轮没有改动 lifecycle/runtime write path，也没有新增 `RuntimeCommandPort` facade 或 raw `event_list` / `dynamic_buff` / `exist_buff_dict` passthrough。
- 下一步：
  - 继续收口 `US-008` final handoff 文档，记录已关闭 producer batch，并区分剩余 phase-1 backlog 与已由本 gate 覆盖的 callsite。
---

## 2026-06-06 22:20:18 - US-008
- 本轮文件：`docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 阶段 1 handoff 文档现在用已关闭 producer batch 替换过期 backlog 表述：`MiyabiCoreSkill_IceFire`、`YixuanCinema1Trigger`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger` 与 `Character/Yuzuha` cinema-6 energy 分支的 planned-event 发布都已改经 `ScheduleDispatchPort`。
  - handoff 现在记录当前 `BattleEventListener` 源码中没有直接 `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` planned-event writer；`AliceDotTriggerListener` 保留 dot runtime registration，与 schedule publishing 分层。
- 兼容保留：
  - 本轮只同步 handoff 与 Ralph 工件；现有 dispatch adapter、runtime command boundary、focused tests 与 planned-event 队列语义保持不变。
  - `--legacy-runtime` / `--candidate-runtime` 仍只是报告标签，不是 live runtime switch。
- 下一步：
  - 下一轮 phase-1 PRD 应审计剩余 `BuffXLogic` / `Character` helper 与可能隐藏的 listener helper，先区分 local event-group list 与真实 scheduler queue write。
---

## 2026-06-07 00:40:53 - US-001
- 本轮文件：`docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 本轮只建立 `zsim/sim_progress` 中剩余 `JudgeTools.find_event_list()`、`schedule_data.event_list` 与 `event_list.append(...)` 命中的分类基线，没有替换新的 live path。
  - 分类结论准备替换后续 PRD 中“所有 event_list.append 都是 raw queue bypass”的粗粒度判断：`Yixuan/AdrenalineManagerClass.py` 是本地 `BaseAdrenalineEvent` 事件组，`LoadDamageEvent.py` 是 core Load-stage event spawn，`ScheduledEvent/event_handlers/handlers/*.py` 是 not-yet-executable requeue，`BreakingLegManager.py` 才是本轮确认的隐藏 helper planned-event writer。
- 兼容保留：
  - 旧 `JudgeTools.find_event_list()`、`schedule_data.event_list` 底层队列、`LegacyEventListScheduleDispatchAdapter`、Load/Schedule 核心调度与 handler requeue 语义全部保留。
  - 本轮没有改动 lifecycle/runtime write path，也没有新增 `RuntimeCommandPort` facade 或 raw `event_list` passthrough。
- 下一步：
  - 下一轮继续按本分类推进：先锁定 `Yixuan` 本地事件组边界，再把 `BreakingLegManager` 的 `ScheduleRefreshData` 发布改经 `ScheduleDispatchPort`。
---

## 2026-06-07 00:50:20 - US-002
- 本轮文件：`tests/simulator/test_yixuan_adrenaline_manager_boundary.py`, `scripts/run_buff_refactor_validation.py`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 本轮没有替换 live path；新增 focused regression 与 shared `implicit-events` gate 条目，准备替换后续 PRD 中把 `Character/Yixuan/AdrenalineManagerClass.py` 的本地 `event_list` 误判为 scheduler queue writer 的旧判断。
  - `test_yixuan_adrenaline_manager_boundary.py` 用 fail-fast `schedule_data.event_list` 证明 `adrenaline_event_factory(...)` 只返回本地 `BaseAdrenalineEvent` 对象组，并保留 `AuricInkUndercurrent` 的 `additional_abililty_active` 过滤。
- 兼容保留：
  - `AdrenalineManagerClass.py` 生产代码未改动，`AdrenalineManager.broadcast()` / `refresh()` 的 runtime-manager 职责保持不变。
  - 未新增 `ScheduleDispatchPort`、`RuntimeCommandPort` facade，也未暴露新的 raw `event_list` / `dynamic_buff` / `exist_buff_dict` passthrough。
- 下一步：
  - 继续把 `BreakingLegManager` 的 part-break `ScheduleRefreshData` 发布路径改经 `ScheduleDispatchPort`，不要重开 Yixuan adrenaline 本地事件组。
---

## 2026-06-07 01:01:25 - US-003
- 本轮文件：`zsim/sim_progress/Enemy/EnemyUniqueMechanic/BreakingLegManager.py`, `tests/simulator/test_breaking_leg_manager_dispatch.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - `BreakingEvent.update_decibel(...)` 现在用 `create_schedule_dispatch_port(sim_instance=self.enemy.sim_instance).publish_scheduled(refresh_data)` 替换旧的 `self.game_state["schedule_data"].event_list.append(refresh_data)` 隐藏 helper raw queue 写入。
  - `test_breaking_leg_manager_dispatch.py` 用 fail-fast `schedule_data.event_list` 锁定 part-break 奖励只经 dispatch gateway 发布一次，并验证 `sp_target=(char_name,)`、`decibel_target=(char_name,)`、`decibel_value=1000` 与 `find_char_from_CID(...)` 缓存语义。
- 兼容保留：
  - 底层 `LegacyEventListScheduleDispatchAdapter` 仍保留旧队列 append 语义；本轮只替换 producer 入口，不改 Schedule 阶段消费、排序或 requeue 逻辑。
  - `BreakingEvent.active(...)` 仍保持 planned-event 喧响刷新先于 same-tick `enemy.update_stun(...)`、`enemy.stun_judge(...)`、`enemy._Enemy__HP_update(...)` 与 `report_dmg_result(...)`。
- 下一步：
  - 在 US-006 中把 `test_breaking_leg_manager_dispatch.py` 加入 shared `implicit-events` pytest 与 scoped mypy gate；后续 handoff 再同步旧审查表和下阶段计划。
---

## 2026-06-07 01:09:56 - US-004
- 本轮文件：`docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明：
  - 本轮只补充保留边界审计，没有替换新的 live path；`LoadDamageEvent` 的 Load-stage event spawn、`SkillEventHandler -> LoadDamageEvent` 的 damage-effect continuation，以及 `ScheduledEvent` handler 的 not-yet-executable requeue 语义继续保留。
  - 新增文档结论用于替换后续 PRD 中“所有 `event_list.append(...)` 都是 raw queue bypass”的粗粒度判断，避免把 core dispatcher / requeue 入口误迁移为 producer publish path。
- 兼容保留：
  - `ScheduledEvent.select_processable_event()` 优先级排序、递归处理、handler requeue、`DamageEventJudge(...)` 与 dot continuation 的队列写入语义都未改动。
  - 本轮没有新增 `ScheduleDispatchPort`、`RuntimeCommandPort` facade，也没有暴露新的 raw `event_list` / `dynamic_buff` / `exist_buff_dict` passthrough。
- 下一步：
  - 继续 US-005 的 post-migration backlog rescan，只把真实 producer-level planned-event writer 记录为后续迁移目标。
---

## 2026-06-07 01:16:11 - US-005
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-005` post-migration scan conclusion replaces stale backlog wording that treated remaining `BuffXLogic` / `Character` / `BattleEventListener` `event_list` mentions as likely raw scheduler writers.
  - No live path was replaced in this story; `BreakingLegManager` was already closed to `ScheduleDispatchPort`, and the rescan found no new concrete one-off planned-event writer.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` compatibility discovery, `LegacyEventListScheduleDispatchAdapter`, local Yixuan event-group lists, dot runtime registration, core Load/Schedule appends, and handler requeue semantics remain in place.
- Next step:
  - Add this PRD's focused regressions to shared `implicit-events` validation, then sync final handoff docs without inventing a new migration target from comments or local lists.
---

## 2026-06-07 01:27:19 - US-006
- Files changed: `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `HIDDEN_HELPER_DISPATCH_TARGETS` and `HIDDEN_HELPER_DISPATCH_FOCUSED_TEST_TARGETS` replace the temporary progress-log instruction to add `test_breaking_leg_manager_dispatch.py` later; the shared `implicit-events` gate now covers this PRD's Yixuan classification regression and `BreakingLegManager` hidden-helper dispatch regression.
  - No live path was replaced in this story; this only closes the shared validation blind spot after the `BreakingLegManager` dispatch migration.
- Compatibility retained:
  - `BreakingLegManager` remains published through `ScheduleDispatchPort`, Yixuan adrenaline events remain local `BaseAdrenalineEvent` objects, and existing dispatch adapter/runtime command boundaries are unchanged.
  - No new raw `event_list`, `dynamic_buff`, or `exist_buff_dict` passthrough interface was introduced.
- Next step:
  - Continue with `US-007` handoff synchronization, recording the closed hidden-helper path and retained core dispatcher/requeue boundaries without inventing a new migration target.
---

## 2026-06-07 01:33:42 - US-007
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-007` handoff docs and Ralph artifacts replace stale wording that still treated `Yixuan` local event groups, `BreakingLegManager`, `LoadDamageEvent`, or `ScheduledEvent` handler requeue branches as unresolved raw scheduler backlog.
  - No live path was replaced in this story; it only synchronizes the phase-1 audit baseline after `BreakingLegManager` was closed to `ScheduleDispatchPort` and shared validation was expanded.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` compatibility discovery, `LegacyEventListScheduleDispatchAdapter`, local Yixuan event groups, dot runtime registration, core Load/Schedule appends, handler requeue semantics, and report-label runtime comparison flags remain in place.
  - `--legacy-runtime` / `--candidate-runtime` remain report labels until live simulator code consumes `config.buff_runtime.mode`.
- Next step:
  - Continue closing the old compatibility discovery path with evidence, and only migrate a new producer when a concrete producer-level planned-event writer is found.
---

## 2026-06-07 02:09:46 - US-001
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-8 US-001` scan evidence replaces stale backlog assumptions that might classify legacy discovery cache, dispatch adapter queue access, handler requeue, local event-group lists, or dot runtime registration as new producer-level planned-event writers.
  - No live path was replaced in this story; it only rebuilds the post-PRD-7 raw queue and legacy discovery scan baseline.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` compatibility discovery, `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, handler requeue, Yixuan local event groups, and Alice dot runtime registration remain in place.
- Next step:
  - Add focused static guardrails for new production uses of `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list`, then keep migrations limited to concrete producer-level planned-event writers if a future scan finds one.
---

## 2026-06-07 02:21:16 - US-002
- Files changed: `tests/simulator/test_legacy_event_list_discovery_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_legacy_event_list_discovery_guardrail.py` prepares to replace manual grep-only checks for `JudgeTools.find_event_list()` and `BuffRecordBaseClass.event_list` with an AST-based guardrail in the shared `implicit-events` gate.
  - No live path was replaced in this story; it only guards the remaining legacy discovery compatibility surface.
- Compatibility retained:
  - `Buff/JudgeTools/__init__.py` may still import/call `find_event_list(...)` to lazily cache `record.event_list`, and `_buff_record_base_class.py` still defines the compatibility field.
  - `FindMain.find_event_list(...)`, `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule queue semantics, handler requeue, and existing dispatch/runtime boundaries remain unchanged.
- Next step:
  - Audit `check_preparation(..., event_list=True)` compatibility evidence in US-003, and only migrate code if a concrete producer-level planned-event writer is found.
---

## 2026-06-07 02:29:00 - US-003
- Files changed: `tests/simulator/test_check_preparation_event_list_compatibility.py`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_check_preparation_event_list_compatibility.py` prepares to replace ad hoc manual checks for `check_preparation(..., event_list=True)` with focused regression evidence that the branch only caches `record.event_list = find_event_list(...)`.
  - No live path was replaced in this story; the slice proves there is no current producer-level planned-event writer behind `event_list=True`.
- Compatibility retained:
  - `Buff/JudgeTools/__init__.py` still supports the legacy `event_list` kwarg by caching the discovered queue on `record.event_list`.
  - `BuffRecordBaseClass.event_list`, `FindMain.find_event_list(...)`, `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule queue semantics, and handler requeue remain unchanged.
- Next step:
  - Continue PRD-8 with the conditional producer story: close it as evidence-only unless a later scan names a concrete planned-event writer with payload and order constraints.
---

## 2026-06-07 02:37:21 - US-004
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-8 US-004` replaces a potential conditional migration with explicit no-migration evidence: US-001 and US-003 found no concrete producer-level planned-event writer behind legacy discovery or `event_list=True`.
  - No live path was replaced in this story; there was no file/function/event payload/order constraint to move through `ScheduleDispatchPort`.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` compatibility discovery, `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule queue semantics, handler requeue, local event groups, and dot runtime registration remain unchanged.
- Next step:
  - Document the retained core dispatcher, handler requeue, local event-group, and dot runtime-registration false-positive boundaries in US-005.
---

## 2026-06-07 02:44:28 - US-005
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-8 US-005` retained-boundary table replaces stale scan ambiguity that could classify `LoadDamageEvent`, `ScheduledEvent` handler requeue, Yixuan local event groups, or Alice dot runtime registration as new producer-level planned-event writers.
  - No live path was replaced in this story; it only documents the retained dispatcher, requeue, local runtime manager, and runtime-registration boundaries.
- Compatibility retained:
  - Core Load/Schedule queue appends, damage-effect continuation, handler not-yet-executable requeue, `Character/Yixuan` local `BaseAdrenalineEvent` groups, Alice dot runtime registration, `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` compatibility discovery, and `LegacyEventListScheduleDispatchAdapter` remain unchanged.
- Next step:
  - Expand the shared `implicit-events` gate in US-006, then synchronize final handoff docs without inventing a migration target from retained false-positive boundaries.
---

## 2026-06-07 02:54:03 - US-006
- Files changed: `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `CHECK_PREPARATION_EVENT_LIST_COMPATIBILITY_FOCUSED_TEST_TARGETS` prepares to replace manual verification of `check_preparation(..., event_list=True)` compatibility with shared `implicit-events` pytest and scoped mypy coverage.
  - No live path was replaced in this story; it only expands the validation boundary for PRD-8 legacy discovery guardrails.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` compatibility discovery, `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule queue semantics, handler requeue, local event groups, and dot runtime registration remain unchanged.
  - No new raw `event_list`, `dynamic_buff`, or `exist_buff_dict` passthrough interface was introduced.
- Next step:
  - Synchronize PRD-8 final handoff docs in US-007, keeping `--legacy-runtime` / `--candidate-runtime` documented as report labels and avoiding invented migration stories when no concrete producer-level writer was found.
---

## 2026-06-07 02:59:26 - US-007
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-8 US-007` final handoff entries replace stale wording that still presented PRD-8 as the next PRD; the long-lived docs now record completed guardrail coverage, deletion prerequisites for `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list`, and the no-new-producer conclusion.
  - No live path was replaced in this story; this only synchronizes the phase-1 handoff after the legacy discovery guardrails entered `implicit-events`.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` remain as legacy discovery / compatibility cache until a later deletion slice proves no allowlist-external producer, config, or `event_list=True` path depends on them.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, handler requeue, local Yixuan event groups, Alice dot runtime registration, and report-label runtime comparison flags remain unchanged.
- Next step:
  - Start the next phase-1 PRD from the guardrail evidence and deletion prerequisites; only add a producer migration story if a scan finds a concrete planned-event writer with payload, target, and order evidence.
---

## 2026-06-07 10:32:38 - US-001
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-9 US-001` post-PRD-8 rescan evidence prepares to replace deletion-prep assumptions with the current retained-boundary baseline for `JudgeTools.find_event_list()`, `BuffRecordBaseClass.event_list`, `schedule_data.event_list`, and `event_list.append(...)` hits.
  - No live path was replaced in this story; it only confirms that no new producer-level planned-event writer re-entered scope after PRD-8.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` remain legacy discovery / compatibility cache only.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, Yixuan local event groups, dot runtime registration, and already-dispatched producer batches remain unchanged.
- Next step:
  - Write the deletion-readiness checklist and risk matrix, keeping `data_struct/schedule_dispatch.py` adapter queue access explicitly outside the deletion target set.
---

## 2026-06-07 11:09:30 - US-002
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-9 US-002` deletion-readiness checklist prepares to replace ad hoc deletion decisions for `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` with explicit responsibility, blocker, verification, risk, and fallback criteria.
  - No live path was replaced in this story; it only documents deletion conditions and keeps `data_struct/schedule_dispatch.py` adapter queue access outside the deletion target set.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` remain legacy discovery / compatibility cache until guardrails prove deletion-safe.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, dot runtime registration, and existing dispatch/runtime boundaries remain unchanged.
- Next step:
  - Add focused static deletion-readiness regression coverage so future deletion work no longer depends on manual checklist review.
---

## 2026-06-07 11:17:24 - US-003
- Files changed: `tests/simulator/test_legacy_event_list_deletion_readiness.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_legacy_event_list_deletion_readiness.py` prepares to replace manual deletion-readiness greps for `JudgeTools.find_event_list()` / `BuffRecordBaseClass.event_list` with AST and structured config/data regression coverage.
  - No live path was replaced in this story; it only adds guardrail evidence and validation wiring for later deletion decisions.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` remain legacy discovery / compatibility cache.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, dot runtime registration, and existing dispatch/runtime boundaries remain unchanged.
- Next step:
  - Audit the `check_preparation(..., event_list=True)` branch as inactive compatibility cache and continue blocking deletion unless allowlist-external production entry points remain absent.
---

## 2026-06-07 11:25:08 - US-004
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-9 US-004` prepares to replace broad manual interpretation of `check_preparation(..., event_list=True)` with explicit evidence that the branch is inactive compatibility cache only.
  - No live path was replaced in this story; it only documents that `event_list=True` does not construct planned-event payloads, does not append, and currently has no explicit production entry point.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` remain legacy discovery / compatibility cache.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, dot runtime registration, and existing dispatch/runtime boundaries remain unchanged.
- Next step:
  - Close the conditional producer story evidence-only unless a future scan finds a concrete `record.event_list.append(...)` or other producer-level planned-event writer with payload, target, and order evidence.
---

## 2026-06-07 11:27:57 - US-005
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-9 US-005` closes the conditional producer migration gate with executable guardrail evidence instead of replacing a live producer path.
  - No live path was replaced in this story; no concrete `record.event_list.append(...)` writer, event payload, target fan-out, or relative-order constraint was found.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` remain legacy discovery / compatibility cache only.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, dot runtime registration, and existing dispatch/runtime boundaries remain unchanged.
- Next step:
  - Continue with the same-tick write boundary story only if it finds a concrete legacy getter plus write collaboration; otherwise close it evidence-only without adding raw passthroughs.
---

## 2026-06-07 11:36:46 - US-006
- Files changed: `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `AnomalyEventHandler.handle() -> runtime_command_port.settle_buffs(..., anomaly_bar=event)` replaces the old `AnomalyEventHandler -> _get_context_legacy_dynamic_buff() / _get_context_legacy_exist_buff_dict() -> ScheduleBuffSettle(..., anomaly_bar=event)` same-tick Buff settle collaboration.
  - `tests/simulator/test_anomaly_handler_runtime_view.py` now prepares future handler cleanup by proving anomaly settle writes use the explicit command boundary and no longer touch legacy getters in the handler.
- Compatibility retained:
  - `RuntimeCommandPort` still delegates through `LegacyRuntimeCommandAdapter`, so old `dynamic_buff`, `exist_buff_dict`, `action_stack`, `sim_instance`, and `ScheduleBuffSettle(..., anomaly_bar=event)` semantics remain inside the adapter.
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list`, `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, and dot runtime registration remain unchanged.
- Next step:
  - Final PRD-9 handoff should state that the newly exposed anomaly same-tick write path is closed through `RuntimeCommandPort`; only add more runtime boundary work if a future scan finds another concrete legacy getter plus same-tick write collaboration.
---

## 2026-06-07 11:43:27 - US-007
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-9 US-007` final handoff docs and Ralph artifacts prepare to replace manual deletion decisions for `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` with the PRD-9 deletion-readiness checklist, risk matrix, and focused guardrails.
  - No live path was replaced in this story; it only synchronizes that PRD-9 found no new producer-level planned-event writer and that the anomaly same-tick write collaboration is already closed through `RuntimeCommandPort`.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` remain until the next deletion execution story proves the guardrails stay green or records a fallback blocker.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, dot runtime registration, existing dispatch/runtime boundaries, and report-label runtime comparison flags remain unchanged.
  - `--legacy-runtime` / `--candidate-runtime` remain report labels until live simulator code consumes `config.buff_runtime.mode`.
- Next step:
  - Start the next phase-1 PRD by executing or explicitly blocking legacy discovery deletion under the guardrails; only migrate a producer if a new scan finds concrete payload, target, and order evidence.
---

## 2026-06-07 12:36 - US-001
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-10 US-001` confirms the deletion execution gate with focused guardrails and structured scans before any live deletion.
  - No live runtime path was replaced in this story; it closes the current evidence gate and prepares `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` for the later deletion or fallback stories.
- Compatibility retained:
  - `JudgeTools.find_event_list()` / `check_preparation(..., event_list=True)` / `BuffRecordBaseClass.event_list` remain legacy discovery / compatibility cache until the targeted deletion stories execute.
  - `LegacyEventListScheduleDispatchAdapter`, core Load/Schedule appends, damage-effect continuation, handler requeue, local event groups, same-tick runtime command adapter access, and already-dispatched producer batches remain unchanged.
- Next step:
  - Proceed to US-002 to delete or explicitly close `JudgeTools.find_event_list()` discovery while keeping `data_struct/schedule_dispatch.py` adapter queue access outside the deletion target set.
---

## 2026-06-07 12:47 - US-002
- Files changed: `zsim/sim_progress/Buff/JudgeTools/FindMain.py`, `zsim/sim_progress/Buff/JudgeTools/__init__.py`, focused simulator guardrail/dispatch tests, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `JudgeTools.find_event_list()` and its package export are deleted, replacing the old raw `schedule_data.event_list` discovery helper with an explicit rejection in `check_preparation(..., event_list=True)`.
  - Focused guardrails now treat any production `find_event_list` import or call as a deletion blocker instead of a compatibility allowlist.
- Compatibility retained:
  - `LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)` remains the only allowed low-level scheduler queue touch point for dispatch-port publishing.
  - `BuffRecordBaseClass.event_list` remains as the next deletion target; this story does not remove unrelated record fields or old runtime containers.
- Next step:
  - Continue with US-003 to remove or quarantine the remaining `event_list=True` keyword/cache surface without reintroducing raw queue discovery.
---

## 2026-06-07 14:15 - US-003
- Files changed: `zsim/sim_progress/Buff/JudgeTools/__init__.py`, `tests/simulator/test_check_preparation_event_list_compatibility.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `check_preparation(..., event_list=...)` now rejects the deleted keyword by presence, replacing the old `event_list = kwargs.get("event_list")` compatibility-cache branch and preventing `record.event_list` from being populated through preparation.
  - No simulator runtime behavior was replaced in this story; this closes a legacy discovery/cache surface without changing planned-event dispatch semantics.
- Compatibility retained:
  - `LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)` remains the only allowed low-level scheduler queue touch point for dispatch-port publishing.
  - `BuffRecordBaseClass.event_list` remains as the next deletion target; unrelated Buff record fields and old runtime containers are unchanged.
- Next step:
  - Continue with US-004 to remove or quarantine `BuffRecordBaseClass.event_list` without widening into unrelated Buff record state.
---

## 2026-06-07 14:22 - US-004
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/_buff_record_base_class.py`, `tests/simulator/test_legacy_event_list_deletion_readiness.py`, `tests/simulator/test_check_preparation_event_list_compatibility.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `BuffRecordBaseClass.__init__` no longer initializes `self.event_list`, replacing the old record-level queue cache field with absence guarded by the focused deletion-readiness tests.
  - `test_check_preparation_event_list_compatibility.py` now proves rejected `event_list` keywords do not recreate a record event-list cache.
- Compatibility retained:
  - `LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)` remains the only allowed low-level scheduler queue touch point for dispatch-port publishing.
  - Unrelated Buff record fields, old runtime containers, core Load/Schedule appends, handler requeue, local event groups, dot runtime registration, and existing dispatch/runtime boundaries are unchanged.
- Next step:
  - Continue with US-005 to tighten post-deletion guardrails around the deleted `find_event_list`, `event_list=True`, and `BuffRecordBaseClass.event_list` surfaces.
---

## 2026-06-07 14:28 - US-005
- Files changed: `tests/simulator/test_legacy_event_list_discovery_guardrail.py`, `tests/simulator/test_legacy_event_list_deletion_readiness.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_legacy_event_list_discovery_guardrail.py` now replaces the deleted `BuffRecordBaseClass.event_list` compatibility allowlist with absence enforcement and post-deletion triage output.
  - `test_legacy_event_list_deletion_readiness.py` now classifies `find_event_list`, `event_list=True`, and `BuffRecordBaseClass.event_list` hits as deleted surfaces, documented fallback candidates, or deletion blockers.
- Compatibility retained:
  - `LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)` remains the only allowed low-level scheduler queue touch point for dispatch-port publishing.
  - No live simulator runtime path was changed; core Load/Schedule appends, handler requeue, local event groups, dot runtime registration, and existing dispatch/runtime boundaries are unchanged.
- Next step:
  - Continue with US-006 evidence triage; only migrate a producer or same-tick write path if concrete file, payload, target, order, or legacy getter evidence appears.
---

## 2026-06-07 14:33 - US-006
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-10 US-006` closes the conditional producer or same-tick migration gate evidence-only instead of replacing a live simulator path.
  - No concrete producer-level planned-event writer was found with old write expression, event type, payload fields, target fan-out, and relative-order evidence; no new handler/helper same-tick legacy getter plus write collaboration was found.
- Compatibility retained:
  - `LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)` remains the only allowed low-level scheduler queue touch point for dispatch-port publishing.
  - Core Load damage-effect continuation, handler requeue, local event groups, base runtime compatibility helpers, and existing `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` semantics remain unchanged.
- Next step:
  - Continue with US-007 final handoff docs; state that PRD-10 removed or closed compatibility discovery surfaces and did not expand producer/runtime migration scope.
---

## 2026-06-07 14:38 - US-007
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-10 US-007` final handoff docs replace stale pre-deletion wording with the completed deletion state for `JudgeTools.find_event_list()`, `check_preparation(..., event_list=...)`, and `BuffRecordBaseClass.event_list`.
  - No live simulator runtime path was replaced in this story; PRD-10 removed or closed compatibility discovery/cache surfaces and tightened guardrails instead of changing scheduler dispatch or runtime write behavior.
- Compatibility retained:
  - `LegacyEventListScheduleDispatchAdapter(schedule_data.event_list)` remains the only allowed low-level scheduler queue touch point for dispatch-port publishing.
  - Core Load/Schedule appends, handler requeue, local event groups, dot runtime registration, base runtime compatibility helpers, and existing `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` semantics remain unchanged.
  - `--legacy-runtime` / `--candidate-runtime` remain report labels until live simulator code consumes `config.buff_runtime.mode`.
- Next step:
  - Start the next phase-1 PRD from the old-container isolation / Buff runtime facade candidate block; only reopen deleted `event_list` surfaces or producer migration if post-deletion guardrails expose concrete production evidence.
---

## 2026-06-07 15:18 - US-001
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-11 US-001` confirms the old-container ownership matrix and prepares the next facade stories to wrap `exist_buff_dict`, `LOADING_BUFF_DICT`, `DYNAMIC_BUFF_DICT`, `ScheduleData.dynamic_buff`, `ScheduleData.loading_buff`, and `enemy.dynamic.dynamic_debuff_list`.
  - No live runtime path was replaced in this story; it builds the evidence boundary for the upcoming minimal legacy-backed Buff runtime facade.
- Compatibility retained:
  - Old container identities are still retained; `BuffRuntimeReadPort` remains read-only and `RuntimeCommandPort` remains the same-tick write boundary.
  - Deleted `JudgeTools.find_event_list()`, `record.event_list`, `BuffRecordBaseClass.event_list`, and `event_list=True` surfaces remain closed unless post-deletion guardrails report concrete production evidence.
  - Already-migrated planned-event producer batches remain on `ScheduleDispatchPort`; this story does not reopen them.
- Next step:
  - Continue with US-002 to add the minimal legacy-backed Buff runtime facade while preserving old container object identity and keeping pending queue, active store, and enemy debuff mirror semantics separate.
---

## 2026-06-07 15:26 - US-002
- Files changed: `zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `tests/simulator/test_buff_runtime_facade.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `LegacyBuffRuntimeFacade` prepares to replace direct old-container plumbing for `LoadData.exist_buff_dict`, `LoadData.LOADING_BUFF_DICT`, `GlobalStats.DYNAMIC_BUFF_DICT`, and `enemy.dynamic.dynamic_debuff_list` with explicit registry, pending queue, active store, and enemy mirror operations.
  - `test_buff_runtime_facade.py` locks old-container object identity, pending queue drain/clear behavior, active store operations, beneficiary key preservation, and enemy debuff mirror sync before any live lifecycle callsite is migrated.
- Compatibility retained:
  - Old containers are still retained and no live main-loop lifecycle call path was routed through the facade in this iteration.
  - `BuffRuntimeReadPort` remains read-only; `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` remain the same-tick write boundary for scheduled handlers.
  - Compatibility identity access is limited to beneficiary/list-scoped `*_for_compat()` methods and is covered by focused tests.
- Next step:
  - Continue with US-003 to route one coherent `Simulator.main_loop()` Buff lifecycle boundary through `LegacyBuffRuntimeFacade` without changing phase order or ScheduleDispatchPort queue semantics.
---

## 2026-06-07 15:34 - US-003
- Files changed: `zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/simulator/simulator_class.py`, `tests/simulator/test_buff_runtime_facade.py`, `tests/simulator/test_simulator_buff_runtime_facade.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `LegacyBuffRuntimeFacade.update_time_related_effects()` replaces `Simulator.main_loop()` tick sweep's direct `DYNAMIC_BUFF_DICT` / `exist_buff_dict` argument assembly with a facade call that delegates to the existing `update_time_related_effect(...)` implementation.
  - `Simulator._create_buff_runtime_facade()` prepares later main-loop lifecycle boundaries to reuse the same old-container facade while preserving container object identity.
- Compatibility retained:
  - Old containers remain the runtime source of truth; the facade delegates to the old tick sweep implementation and does not change `update_buff()`, `KickOutBuff()`, anomaly, dot, or calculator formulas.
  - `BuffLoadLoop()`, `buff_add()`, `ScheduledEvent(...)`, `DamageEventJudge(..., self.schedule_data.event_list, ...)`, and `ScheduleDispatchPort` queue semantics remain unchanged in this story.
  - `BuffRuntimeReadPort` remains read-only; `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` remain the same-tick write boundary for scheduled handlers.
- Next step:
  - Continue with US-004 to move pending-to-active activation semantics through the facade, including invalid pending Buff skip, replacement by `ft.index`, alltime duplicate behavior, pending queue drain, and enemy debuff mirror sync.
---

## 2026-06-07 15:42 - US-004
- Files changed: `zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/simulator/simulator_class.py`, `tests/simulator/test_buff_runtime_facade.py`, `tests/simulator/test_simulator_buff_runtime_facade.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `LegacyBuffRuntimeFacade.activate_pending_buffs()` replaces `Simulator.main_loop()` activation phase's direct `buff_add(self.load_data.LOADING_BUFF_DICT, self.global_stats.DYNAMIC_BUFF_DICT, self.schedule_data.enemy)` raw-container assembly with a facade command.
  - The facade command preserves pending queue drain order, invalid pending Buff skip, active replacement by `ft.index`, alltime duplicate skip, and enemy debuff mirror replacement against the same old container objects.
- Compatibility retained:
  - `BuffLoadLoop()` trigger judgement, `Buff.update(...)`, `update_to_buff_0()`, `ScheduledEvent(...)`, `DamageEventJudge(..., self.schedule_data.event_list, ...)`, and `ScheduleDispatchPort` queue semantics remain unchanged.
  - The legacy `buff_add()` function is retained as an old compatibility path; old containers remain the runtime source of truth.
  - `BuffRuntimeReadPort` remains read-only; `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` remain the same-tick write boundary for scheduled handlers.
- Next step:
  - Continue with US-005 to wrap active Buff expiration/removal semantics through the facade, including `KickOutBuff()` order and enemy debuff mirror removal.
---

## 2026-06-07 15:51 - US-005
- Files changed: `zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/sim_progress/Update/Update_Buff.py`, `tests/simulator/test_buff_runtime_facade.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `LegacyBuffRuntimeFacade.end_active_buff()` replaces the live facade tick sweep's direct `KickOutBuff(DYNAMIC_BUFF_DICT, buff, beneficiary, enemy, sub_exist_buff_dict, tick)` removal step with an explicit active-removal command.
  - `Update_Buff.update_buff(..., runtime_facade=...)` now delegates only active removals through the facade, preserving `Buff.end(...)`, active-list removal, Buff end logging, and exact enemy debuff mirror removal order.
- Compatibility retained:
  - The legacy `KickOutBuff()` function remains for direct compatibility callers without a facade.
  - Old `DYNAMIC_BUFF_DICT`, `exist_buff_dict`, and `enemy.dynamic.dynamic_debuff_list` object identities remain the runtime source of truth behind the facade.
  - `BuffRuntimeReadPort` remains read-only; `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` remain the same-tick write boundary for scheduled handlers.
  - Anomaly expiration, dot expiration, `BuffLoadLoop()` trigger judgement, `Buff.update(...)`, `update_to_buff_0()`, `ScheduledEvent(...)`, `DamageEventJudge(..., self.schedule_data.event_list, ...)`, and `ScheduleDispatchPort` queue semantics remain unchanged.
- Next step:
  - Continue with US-006 to add no-new-raw-container guardrails for the new facade boundary while keeping documented retained boundaries narrow.
---

## 2026-06-07 15:58 - US-006
- Files changed: `tests/simulator/test_buff_raw_container_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_buff_raw_container_guardrail.py` prepares to replace ad hoc review of new old-container passthroughs with an AST guardrail over the PRD-11 facade scope.
  - The guardrail covers raw `DYNAMIC_BUFF_DICT`, `LOADING_BUFF_DICT`, `exist_buff_dict`, `ScheduleData.dynamic_buff`, and `ScheduleData.loading_buff` references by retained-boundary allowance and ceiling checks.
  - No live simulator runtime path was replaced in this story; it adds a prevention boundary around the facade work already introduced by US-002 through US-005.
- Compatibility retained:
  - Old containers remain the runtime source of truth behind `LegacyBuffRuntimeFacade`.
  - Retained allowances cover facade adapter internals, current facade construction, `BuffLoadLoop()` pending queue population, retained `buff_add()` / `Update_Buff` compatibility paths, `ScheduledEvent(...)`, core Load/Schedule/GlobalStats ownership, and `RuntimeCommandPort` compatibility reads.
  - `BuffRuntimeReadPort` remains read-only and `RuntimeCommandPort` remains the same-tick write boundary; this story adds no new raw-container getter or write facade.
- Next step:
  - Continue with US-007 lifecycle/main-loop validation and keep `--legacy-runtime` / `--candidate-runtime` documented as report labels unless a later story makes them live runtime switches.
---

## 2026-06-07 16:07 - US-007
- Files changed: `zsim/utils/main_loop_consistency.py`, `tests/simulator/test_main_loop_consistency.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `zsim.utils.main_loop_consistency` now replaces the previous validation blocker where consistency samples could fail before comparison when a valid `damage.csv` had a blank `is_anomaly` column; the fallback normalizes that report-only column to `False` and keeps the `team / stop_tick / total_damage / event_counts / buff_timeline / differences` JSON contract usable.
  - This story validates the PRD-11 facade boundary rather than replacing another live runtime path; the tick sweep, pending activation, and active removal replacements from US-003 through US-005 remain the live facade-backed lifecycle changes.
- Compatibility retained:
  - Old containers remain the runtime source of truth behind `LegacyBuffRuntimeFacade`; no container deletion or broad XLogic migration happened in this story.
  - `BuffRuntimeReadPort` remains read-only and `RuntimeCommandPort` remains the same-tick write boundary.
  - `--legacy-runtime` / `--candidate-runtime` remain report labels, not live runtime switches.
- Next step:
  - Continue with US-008 to sync the handoff docs, record that old containers are still retained, and prepare the next phase-1 candidate pool.
---

## 2026-06-07 16:11 - US-008
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-11 US-008` replaces stale “PRD-11 is next” handoff wording with the completed old-container facade-expansion state and promotes the next default phase-1 PRD to `ScheduledEvent` / `EventContext` runtime facade dependency closure.
  - No additional live runtime path was replaced in this story; it records the live replacements from US-003 through US-005 and the guardrail / validation evidence from US-006 through US-007.
- Compatibility retained:
  - Old containers remain the runtime source of truth behind `LegacyBuffRuntimeFacade`; `ScheduledEvent(...)`, `BuffLoadLoop()`, legacy `buff_add()`, legacy `KickOutBuff()`, core Load/Schedule append, handler requeue, and dot runtime registration remain documented retained boundaries.
  - `BuffRuntimeReadPort` remains read-only, `RuntimeCommandPort` remains the same-tick write boundary, and `--legacy-runtime` / `--candidate-runtime` remain report labels rather than live runtime switches.
- Next step:
  - Start the next phase-1 PRD from `ScheduledEvent` / `EventContext` raw old-container exposure closure while keeping candidate blocks C/D/E available for later same-phase PRDs.
---

## 2026-06-07 17:33 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `PRD-12 US-001` prepares to replace loose phase-1 handoff routing with a story-level completion matrix over `ScheduledEvent`, `Update_Buff`, Calculator reads, anomaly/debuff/dot bypasses, guardrails, validation, and final handoff.
  - No live runtime path was replaced in this story; it builds the boundary map and confirms which retained paths must remain compatibility-only or layer-specific for later stories.
- Compatibility retained:
  - `ScheduledEvent(...)`, `BuffLoadLoop()`, legacy `buff_add()`, legacy `KickOutBuff()`, handler requeue, damage-effect continuation, core Load/Schedule append, dot runtime registration, `BuffRuntimeReadPort`, `RuntimeCommandPort`, and `ScheduleDispatchPort` remain retained boundaries.
  - Deleted `JudgeTools.find_event_list()`, `check_preparation(..., event_list=...)`, and `BuffRecordBaseClass.event_list` surfaces stay closed unless guardrails expose concrete new production evidence.
  - Already completed planned-event producer batches remain closed and should not be reopened from historical text alone.
- Next step:
  - Continue with US-002 to audit `ScheduledEvent` / `EventContext` raw runtime exposure before narrowing compatibility getters or changing handler boundaries.
---

## 2026-06-07 17:41 - US-002
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `PRD-12 US-002` does not replace a live runtime path; it prepares the `ScheduledEvent` block by classifying retained raw old-container exposure, compatibility getter reachability, and already-closed handler read/write boundaries.
  - The audit confirms `SkillEventHandler` and `AnomalyEventHandler` already use `BuffRuntimeReadPort` for active Buff reads and `RuntimeCommandPort` for same-tick writes, so later stories should not reopen those migrated paths without new production evidence.
- Compatibility retained:
  - `ScheduledEvent(...)` still accepts raw `dynamic_buff`, `exist_buff_dict`, and `loading_buff` for constructor compatibility.
  - `EventContext.get_dynamic_buff()` / `get_exist_buff_dict()` and `BaseEventHandler._get_context_dynamic_buff()` / `_get_context_exist_buff_dict()` remain compatibility-only identity getters through `BuffRuntimeReadPort.get_legacy_*()`.
  - `ScheduledEvent.event_start()` still reads `ScheduleData.dynamic_buff` for `SPUpdateData`, and `ScheduledEvent.update_anomaly_bar_after_skill_event()` remains the next same-tick helper to route or document.
- Next step:
  - Continue with US-003 to narrow compatibility getter naming/comments/tests, then US-004 to handle the remaining `ScheduledEvent.update_anomaly_bar_after_skill_event()` write helper.
---
## 2026-06-07 17:46 - US-003
- Files changed: `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `tests/simulator/test_buff_runtime_view.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `EventContext.get_legacy_dynamic_buff_dict()` / `get_legacy_exist_buff_dict()` and `BaseEventHandler._get_context_legacy_dynamic_buff()` / `_get_context_legacy_exist_buff_dict()` replace the implicit old getter names as the documented compatibility boundary for raw old-container identity.
  - No live runtime path was replaced in this story; it narrows the compatibility getter surface and keeps handler runtime reads on `BuffRuntimeReadPort` active / snapshot views.
- Compatibility retained:
  - `EventContext.get_dynamic_buff()` / `get_exist_buff_dict()` and `BaseEventHandler._get_context_dynamic_buff()` / `_get_context_exist_buff_dict()` remain old aliases, now typed and documented as compatibility-only shims.
  - Old Buff containers remain retained behind the runtime read and command adapters; this story does not delete old containers or add a write API to `BuffRuntimeReadPort`.
- Next step:
  - Continue with US-004 to route or document `ScheduledEvent.update_anomaly_bar_after_skill_event()` through the existing `RuntimeCommandPort` same-tick write boundary.
---
## 2026-06-07 17:58 - US-004
- Files changed: `zsim/sim_progress/ScheduledEvent/__init__.py`, `tests/simulator/test_runtime_command_port.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `ScheduledEvent.update_anomaly_bar_after_skill_event()` now uses `self.runtime_command_port.update_anomaly(...)` instead of passing `self.data.event_list`, `self.data.char_obj_list`, `self.data.dynamic_buff`, and `self.sim_instance` directly to legacy `update_anomaly(...)`.
  - Focused tests replace implicit compatibility confidence with explicit route / no-route coverage for the retained helper, including `LoadingMission.mission_start(...) -> get_last_hit() -> RuntimeCommandPort.update_anomaly(...)` order.
- Compatibility retained:
  - The helper remains a compatibility method and keeps its anomaly update decision logic.
  - `RuntimeCommandPort` still delegates through `LegacyRuntimeCommandAdapter`, so current `ScheduleData.event_list` rebinding, `dynamic_buff`, `char_obj_list`, and `sim_instance` legacy identity remain inside the adapter.
  - `SkillEventHandler` and `AnomalyEventHandler` were not re-migrated in this story; their existing runtime view / command-port paths remain unchanged.
- Next step:
  - Continue with US-005 to centralize explicit `ScheduledEvent` construction of runtime view and command port without changing public `ScheduledEvent(...)` callsite behavior.
---
## 2026-06-07 18:07 - US-005
- Files changed: `zsim/sim_progress/ScheduledEvent/__init__.py`, `tests/simulator/test_runtime_command_port.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_ScheduledEventRuntimePorts` and `ScheduledEvent._create_runtime_ports()` prepare to replace inline raw constructor setup with one explicit internal boundary for `BuffRuntimeReadPort` and `RuntimeCommandPort` creation.
  - `tests/simulator/test_runtime_command_port.py` adds normal `ScheduledEvent(...)` construction coverage that replaces implicit confidence in port setup with adapter identity, event-list rebinding, and no-new-direct-raw-field assertions.
- Compatibility retained:
  - Public `ScheduledEvent(...)` arguments are unchanged, and the live `Simulator.main_loop()` `ScE(...)` callsite remains compatible.
  - Old `dynamic_buff`, `exist_buff_dict`, and `loading_buff` constructor inputs are still retained compatibility boundaries; `RuntimeCommandPort` keeps old container identity inside `LegacyRuntimeCommandAdapter`.
  - `ScheduleData.loading_buff` remains distinct from `LoadData.LOADING_BUFF_DICT`; no pending queue ownership wiring was inferred in this story.
- Next step:
  - Continue with US-006 to add no-new-raw-runtime guardrails around `ScheduledEvent`, handler compatibility getters, and retained constructor setup.
---
## 2026-06-07 18:16 - US-006
- Files changed: `tests/simulator/test_buff_raw_container_guardrail.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `ScheduledEventRuntimeVisitor` guardrail prepares to replace unchecked `ScheduledEvent` / `event_handlers` raw runtime growth with AST-enforced allowlists and retained-reference ceilings.
  - No live runtime path was replaced in this story; it adds guardrail coverage for raw `dynamic_buff`, `exist_buff_dict`, `loading_buff`, documented legacy getters, and runtime container passthroughs.
- Compatibility retained:
  - Public `ScheduledEvent(...)` constructor raw inputs remain retained compatibility boundaries.
  - `BuffRuntimeReadPort` / `RuntimeCommandPort` adapter internals, documented `EventContext` / `BaseEventHandler` legacy getters, `ScheduledEvent.event_start()` `SPUpdateData` read, and runtime-view formula-boundary `dynamic_buff` keywords remain allowed only in named guardrail buckets.
- Next step:
  - Continue with US-007 to validate ScheduledEvent behavior, retained scheduler semantics, handler requeue, damage-effect continuation, and runtime command separation under the new guardrail coverage.
---
## 2026-06-07 18:26 - US-007
- Files changed: `tests/simulator/test_scheduled_event_retained_semantics.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_scheduled_event_retained_semantics.py` prepares to replace undocumented assumptions about `ScheduledEvent` handler requeue, `LoadDamageEvent` damage-effect continuation, `SPUpdateData` refresh order, and `ScheduleDispatchPort` queue-only behavior with focused regression coverage.
  - `scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` now includes the retained-semantics test in shared pytest and scoped mypy targets.
- Compatibility retained:
  - No live simulator runtime path was replaced in this iteration; handler requeue, damage-effect continuation, `SPUpdateData(..., dynamic_buff=self.data.dynamic_buff)`, `RuntimeCommandPort`, and `ScheduleDispatchPort` semantics remain retained phase-1 boundaries.
- Next step:
  - Continue PRD-12 with `Update_Buff` lifecycle coupling audit and keep old containers retained unless a later story proves a narrower facade-backed lifecycle migration.
---
## 2026-06-07 18:32 - US-008
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/旧Buff系统耦合审查结果.md` prepares to replace broad `Update_Buff` lifecycle ambiguity with a concrete inventory of facade-backed live paths, retained compatibility paths, lifecycle migration candidates, and anomaly / dot non-targets.
  - No live runtime path was replaced in this story; it audits the remaining lifecycle coupling after PRD-11 active removal was routed through `LegacyBuffRuntimeFacade.end_active_buff()`.
- Compatibility retained:
  - Old Buff containers remain the runtime source of truth behind `LegacyBuffRuntimeFacade`.
  - `KickOutBuff()` remains a retained direct compatibility path, and anomaly bar expiration, dot expiration, Calculator formulas, enemy debuff mirror single-source-of-truth, and complex `xexit()` formulas are not changed.
- Next step:
  - Continue with US-009 by selecting one coherent `Update_Buff.update_buff()` lifecycle internal to route through the existing runtime facade or a narrow lifecycle adapter, backed by focused tests.
---
## 2026-06-07 18:43 - US-009
- Files changed: `zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/sim_progress/Update/Update_Buff.py`, `tests/simulator/test_buff_runtime_facade.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `BuffRuntimeFacade.settle_individual_buff_stack()` / `LegacyBuffRuntimeFacade.settle_individual_buff_stack()` replaces the live `Update_Buff.update_buff(..., runtime_facade=...)` direct `process_individual_buff()` call for individual-settled Buff stack cleanup.
  - The focused lifecycle test now proves the individual-settled branch routes through the facade and still preserves stack cleanup, count refresh, and report timing.
- Compatibility retained:
  - No-facade `Update_Buff.update_buff()` callers still use legacy `process_individual_buff()` directly.
  - `KickOutBuff()` remains the retained compatibility path for direct Buff ending, and anomaly bar expiration, dot expiration, Calculator formulas, complex `xexit()` formulas, and enemy debuff single-source-of-truth are unchanged.
- Next step:
  - Continue with US-010 lifecycle raw-container guardrails so the new individual-settled facade command and retained direct compatibility paths are guarded against raw-container expansion.
---
## 2026-06-07 18:53 - US-010
- Files changed: `tests/simulator/test_buff_raw_container_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_buff_raw_container_guardrail.py` prepares to replace manual lifecycle review for `enemy.dynamic.dynamic_debuff_list` and retained `Update_Buff` / `BuffAdd` old-container growth with AST-classified guardrails, context-specific allowances, and retained-reference ceilings.
  - `scripts/run_buff_refactor_validation.py` now runs the raw-container guardrail in the default `lifecycle` validation profile as focused pytest and scoped mypy coverage.
- Compatibility retained:
  - No live simulator runtime path was replaced in this story; old containers remain the runtime source of truth behind `LegacyBuffRuntimeFacade`.
  - `BuffLoadLoop()`, legacy `buff_add()`, legacy `KickOutBuff()`, no-facade `Update_Buff` fallbacks, and current enemy debuff mirror synchronization remain retained compatibility boundaries.
- Next step:
  - Continue with US-011 lifecycle validation and main-loop safety evidence before moving into the Calculator read block.
---
## 2026-06-07 18:59 - US-011
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - This story does not replace a live Buff runtime path; it replaces unproven lifecycle confidence after US-009 / US-010 with focused lifecycle tests, full lifecycle validation, and one representative `run_buff_main_loop_consistency.py` JSON sample.
  - The evidence confirms `LegacyBuffRuntimeFacade` lifecycle routing remains stable for the current main loop after active removal and individual-settled stack cleanup were routed through facade commands.
- Compatibility retained:
  - Old Buff containers remain the runtime source of truth behind `LegacyBuffRuntimeFacade`.
  - `BuffLoadLoop()`, legacy `buff_add()`, legacy `KickOutBuff()`, no-facade `Update_Buff` fallbacks, anomaly bar expiration, dot expiration, and current enemy debuff mirror synchronization remain retained compatibility boundaries.
  - `--legacy-runtime` / `--candidate-runtime` remain consistency report labels only; live simulator runtime mode was not wired in this story.
- Next step:
  - Continue with US-012 Calculator `MultiplierData` / `Mul` usage audit and keep lifecycle work closed unless a later validation profile exposes new production evidence.
---
## 2026-06-07 19:07 - US-012
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-012 Calculator read inventory prepares to replace ad hoc `MultiplierData(...)` / `Mul(...)` audits with a current classified callsite map and one selected first migration sample.
  - No live Calculator, BuffXLogic, anomaly, or scheduled-event path was replaced in this story.
- Compatibility retained:
  - `MultiplierData` remains the compatibility snapshot for Calculator, CalAnomaly, and old BuffXLogic readers.
  - Existing formulas, Buff count writes, record writes, RNG gates, and `ScheduleDispatchPort` planned-event publishes remain unchanged.
- Next step:
  - Continue with US-013 by designing a minimal attribute reader around the anomaly-mastery sample, then use `BranchBladeSongCritDamageBonus.special_judge_logic()` as the first low-risk XLogic migration candidate.
---
## 2026-06-07 19:18 - US-013
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `BuffAttributeReadContext` / `BuffAttributeReader` / `CalculatorBuffAttributeReader` prepares to replace ad hoc high-frequency `MultiplierData(...)` reads for the anomaly-mastery helper group.
  - `_calculate_dynamic_statement()` centralizes the old dynamic Buff aggregation so `MultiplierData` remains a compatibility snapshot while the new reader can compute `read_anomaly_mastery()` without constructing that snapshot.
- Compatibility retained:
  - No live BuffXLogic callsite was migrated in this story; `BranchBladeSongCritDamageBonus.special_judge_logic()` still uses the retained `MultiplierData + Calculator.AnomalyMul.cal_am()` path.
  - Calculator formulas, CalAnomaly formulas, read-then-write XLogic paths, event-producing XLogic paths, and `ScheduleDispatchPort` behavior remain unchanged.
- Next step:
  - Continue with US-014 by migrating the representative `BranchBladeSongCritDamageBonus.special_judge_logic()` read-only gate to the new attribute reader and retaining old-helper parity coverage.
---
## 2026-06-07 19:28 - US-014
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py`, `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `BranchBladeSongCritDamageBonus.special_judge_logic()` now replaces its ad hoc `MultiplierData(...) + Calculator.AnomalyMul.cal_am()` read with `BuffAttributeReadContext` and `CalculatorBuffAttributeReader.read_anomaly_mastery()`.
  - The focused test compares the migrated gate against the old helper path for below-threshold, exactly-threshold, and above-threshold anomaly mastery inputs.
- Compatibility retained:
  - `MultiplierData` remains the compatibility snapshot for Calculator formulas, CalAnomaly formulas, remaining read-then-write XLogic paths, alias read paths, RNG trigger gates, and event-producing XLogic paths.
  - The migrated path remains read-only; no formula value, record write, Buff writeback, scheduler publish, listener broadcast, or runtime command behavior changed.
- Next step:
  - Continue with US-015 by selecting the next low-risk XLogic attribute-read user from the US-012 inventory now that the BranchBladeSong gate is already migrated.
---
## 2026-06-07 19:39 - US-015
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `CalculatorBuffAttributeReader.read_anomaly_proficiency()` prepares to replace ad hoc `MultiplierData(...)` / `MultiplierData as Mul` AP reads with a single-attribute reader seam.
  - `TimeweaverDisorderDmgMul.special_judge_logic()` now replaces its alias `Mul(...) + Calculator.AnomalyMul.cal_ap()` threshold read with `BuffAttributeReadContext` and `CalculatorBuffAttributeReader.read_anomaly_proficiency()`.
  - Focused tests compare the migrated gate against the old helper path for below-threshold, exactly-threshold, and above-threshold anomaly proficiency inputs, and assert the migrated gate no longer directly imports or constructs `MultiplierData` / `Mul(...)`.
- Compatibility retained:
  - `MultiplierData` remains the compatibility snapshot for Calculator formulas, CalAnomaly formulas, read-then-write XLogic paths, remaining alias AP writeback paths, RNG trigger gates, and event-producing XLogic paths.
  - The migrated Timeweaver path remains read-only; no formula value, record write, Buff writeback, scheduled queue publish, listener broadcast, or runtime command behavior changed.
  - `TimeweaverDisorderDmgMul.special_judge_logic()` keeps the old direct comparison return shape, which may be `np.bool_`.
- Next step:
  - Continue with US-016 by adding calculator-read guardrails and profile coverage for remaining direct `MultiplierData(...)`, `MultiplierData as Mul`, and raw `dynamic_buff_list` read surfaces.
---
## 2026-06-07 19:51 - US-016
- Files changed: `tests/simulator/test_buff_raw_container_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `CalculatorReadVisitor` prepares to replace manual review of new direct `MultiplierData(...)` / alias `Mul(...)` / raw `dynamic_buff_list` attribute-read surfaces with an AST guardrail over the selected `calculator-reads` scope.
  - `scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` now runs the calculator guardrail as focused pytest and scoped mypy coverage.
- Compatibility retained:
  - No live Calculator, BuffXLogic, anomaly, scheduled queue, listener broadcast, or runtime command path was replaced in this story; it adds boundary guardrails only.
  - `MultiplierData` remains the compatibility snapshot for Calculator formulas and retained XLogic reads, with current ceilings of 1 Calculator formula snapshot, 25 retained XLogic compatibility findings, and 2 migrated attribute-reader inputs.
- Next step:
  - Continue with US-017 to audit anomaly, debuff, and dot bypass coupling while keeping Calculator-read guardrails in the `calculator-reads` validation profile.
---
## 2026-06-07 19:58 - US-017
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-017 anomaly / debuff / dot bypass inventory prepares to replace ad hoc review of `UpdateAnomaly`, `AnomalyBar`, `Shock`, `BuffAddStrategy`, and `CalAnomaly` with classified runtime-read, runtime-write, scheduled-publish, listener-broadcast, dot-registration, and formula-internal boundaries.
  - No live simulator path was replaced in this story; it is an audit and handoff slice only.
- Compatibility retained:
  - `UpdateAnomaly` scheduled queue publish remains through `ScheduleDispatchPort`; `listener_manager.broadcast_event()` remains synchronous listener broadcast; dot runtime registration remains `enemy.dynamic.dynamic_dot_list` state.
  - `BuffAddStrategy` still writes the old active Buff store and enemy debuff mirror directly, and `CalAnomaly` still uses the retained `MulData(...)` formula snapshot.
- Next step:
  - Continue with US-018 by migrating the `AnomalyBar.__get_max_duration()` read-only duration sample through an explicit read seam, while leaving `BuffAddStrategy` for US-019 write-boundary investigation.
---
## 2026-06-07 20:13 - US-018
- Files changed: `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`, `zsim/sim_progress/Update/UpdateAnomaly.py`, `zsim/sim_progress/ScheduledEvent/__init__.py`, `zsim/sim_progress/ScheduledEvent/runtime_command.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `tests/simulator/test_runtime_command_port.py`, `tests/simulator/test_skill_handler_runtime_view.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `AnomalyBar.__get_max_duration()` now replaces the ScheduledEvent runtime-command path's direct enemy `dynamic_buff_dict` duration read with `BuffRuntimeReadPort.get_active_buffs("enemy")`.
  - `ScheduledEvent._create_runtime_ports()` injects its existing read port into `LegacyRuntimeCommandAdapter`, avoiding a second raw-container adapter in the command boundary.
- Compatibility retained:
  - Direct legacy `update_anomaly(...)` calls without `buff_runtime_view` still use the old `dynamic_buff_dict["enemy"]` compatibility path.
  - Anomaly formulas, `CalAnomaly` `MulData(...)`, `Shock` / Dot runtime registration, scheduled queue publish, listener broadcast, and runtime writes remain unchanged.
- Next step:
  - Continue with US-019 by investigating and classifying `BuffAddStrategy.buff_add_strategy()` / `let_buff_start()` write boundaries.
---
## 2026-06-07 21:28 - US-019
- Files changed: `zsim/sim_progress/Buff/BuffAddStrategy.py`, `tests/simulator/test_buff_add_strategy_runtime_facade.py`, `tests/simulator/test_buff_raw_container_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `BuffAddStrategy.let_buff_start()` active-store replacement now replaces direct `DYNAMIC_BUFF_DICT` list remove / append with `BuffRuntimeFacade.find_active_buff_by_index()`, `remove_active_buff()`, and `append_active_buff()`.
  - `BuffAddStrategy.let_buff_start()` enemy debuff mirror sync now replaces direct `enemy.dynamic.dynamic_debuff_list` remove / append with `BuffRuntimeFacade.sync_enemy_debuff_mirror()`.
  - `test_buff_raw_container_guardrail.py` prepares to replace manual review of new `BuffAddStrategy` raw pending / active / enemy mirror writes with AST-classified allowances and retained-reference ceilings.
- Compatibility retained:
  - `buff_add_strategy()` remains a same-tick runtime write helper, not a planned-event publish; caller behavior from anomaly, listener, Character manager, and BuffXLogic paths remains unchanged.
  - `exist_buff_dict` registry/template identity remains retained for beneficiary selection, Buff template copy, and `simple_start()` template-state writeback.
  - `_create_buff_add_runtime_facade()` still service-locates old containers on demand; it does not cache facade instances across simulator state rebinding.
  - `__check_buff_add_result()` remains an inactive diagnostic compatibility helper and is guarded as retained, not reopened as a live path.
- Next step:
  - Continue with US-020 by adding bypass semantics tests that distinguish scheduled queue publish, listener broadcast, dot runtime registration, and runtime immediate writes, including the `BuffAddStrategy` facade-backed forced-write sample where practical.
---
## 2026-06-07 21:42 - US-020
- Files changed: `tests/simulator/test_bypass_layer_semantics.py`, `scripts/run_buff_refactor_validation.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `tests/simulator/test_bypass_layer_semantics.py` prepares to replace manual review of bypass-layer separation with focused regressions for scheduled queue publish, listener broadcast, handler requeue, dot runtime registration, `RuntimeCommandPort` same-tick writes, and `BuffAddStrategy` facade-backed forced writes.
  - `scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` now includes the bypass-layer semantics tests in both focused pytest and scoped mypy coverage.
- Compatibility retained:
  - No live simulator runtime path was replaced in this story; it adds semantics coverage around boundaries migrated or classified by US-017 through US-019.
  - `ScheduleDispatchPort` remains the planned-event publish boundary, `listener_manager.broadcast_event()` remains synchronous broadcast, handler requeue remains retained scheduler behavior, dot runtime registration remains direct enemy runtime state, and `RuntimeCommandPort` / `LegacyBuffRuntimeFacade` remain same-tick runtime write boundaries.
- Next step:
  - Continue with US-021 by consolidating the phase-1 guardrail matrix across raw queue, raw runtime, lifecycle, Calculator-read, and anomaly / debuff / dot bypass coverage.
---
## 2026-06-07 21:52 - US-021
- Files changed: `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/旧Buff系统耦合审查结果.md` phase-1 guardrail matrix prepares to replace ad hoc cross-PRD review of deleted `event_list` surfaces, raw scheduler writes, raw old-container passthroughs, `ScheduledEvent` raw runtime getters, lifecycle containers, Calculator reads, and anomaly / debuff / dot bypasses.
  - No live simulator runtime path was replaced in this story; it consolidates existing guardrail and validation evidence.
- Compatibility retained:
  - Old containers remain retained compatibility boundaries; the matrix only guards against boundary expansion.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, documented handler compatibility getters, listener broadcast, handler requeue, damage continuation, and dot runtime registration keep their existing semantics.
  - `scripts/run_buff_refactor_validation.py` profile wiring was already aligned with the matrix, so no placeholder validation target was added.
- Next step:
  - Continue with US-022 by running the serial phase-1 validation profiles plus representative consistency and benchmark samples.
---
## 2026-06-07 22:07 - US-022
- Files changed: `zsim/utils/runtime_benchmark.py`, `tests/simulator/test_runtime_benchmark.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `zsim.utils.runtime_benchmark._load_runtime_benchmark_snapshot()` now replaces its direct dependency on raw `prepare_dmg_data_and_cache()` success with the existing main-loop consistency damage-data fallback, so short benchmark samples with blank `is_anomaly` columns can still produce timing JSON.
  - The US-022 validation record replaces phase-1 closure assumptions with serial profile results plus representative consistency and benchmark JSON evidence.
- Compatibility retained:
  - No live simulator runtime behavior, Buff formula, scheduled queue publish, listener broadcast, runtime command, or old-container ownership changed in this story.
  - `--legacy-runtime` / `--candidate-runtime` remain report labels only; this story did not wire a live runtime mode switch.
  - Old containers remain retained compatibility boundaries pending the handoff and closure stories.
- Next step:
  - Continue with US-023 by syncing the phase-1 handoff docs from the US-022 validation evidence, including the benchmark fallback fix and report-label limitation.
---
## 2026-06-07 22:13 - US-023
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-023 handoff docs replace stale PRD-11-era next-step guidance with the current PRD-12 phase-1 evidence map, validation outcomes, retained-boundary list, and `US-024` closure / blocker decision route.
  - No live simulator runtime path was replaced in this story; it synchronizes handoff state after the US-022 validation and benchmark fallback evidence.
- Compatibility retained:
  - Old containers remain retained compatibility boundaries: `exist_buff_dict`, `DYNAMIC_BUFF_DICT`, `LOADING_BUFF_DICT`, legacy `buff_add()`, legacy `KickOutBuff()`, Calculator / CalAnomaly `MultiplierData` formula snapshots, handler requeue, damage continuation, listener broadcast, and dot runtime registration are not deleted by this handoff.
  - `--legacy-runtime` / `--candidate-runtime` remain consistency / benchmark report labels only; no live runtime mode switch was wired.
- Next step:
  - Continue with US-024 to declare phase-1 closure or produce a blocker package from the synchronized checklist, coupling review, validation records, and replacement notes.
---
## 2026-06-07 22:25 - US-024
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-024 closure package replaces the open phase-1 closure / blocker decision with an evidence-backed phase-1 closed state and a phase-2 default PRD route.
  - No live simulator runtime path was replaced in this story; it is a final decision, validation, and handoff slice.
- Compatibility retained:
  - Old containers remain retained compatibility boundaries: `exist_buff_dict`, `DYNAMIC_BUFF_DICT`, `LOADING_BUFF_DICT`, legacy `buff_add()`, legacy `KickOutBuff()`, Calculator / CalAnomaly `MultiplierData` formula snapshots, handler requeue, damage continuation, listener broadcast, and dot runtime registration are not deleted by phase-1 closure.
  - `--legacy-runtime` / `--candidate-runtime` remain consistency / benchmark report labels only; no live runtime mode switch was wired.
- Next step:
  - Start the next PRD from phase 2: XLogic full classification and reuse convergence, while using phase-1 guardrails only as blocker evidence if they fail.
---
## 2026-06-08 00:08 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - No live path was replaced in this audit-only story; it confirms that the current root `ScheduleBuffSettle(...)` production path remains behind `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` and prepares later guardrail/profile/doc-sync stories.
- Compatibility retained:
  - `SkillEventHandler` and `AnomalyEventHandler` still call `runtime_command_port.settle_buffs(...)`; `LegacyRuntimeCommandAdapter` still delegates to the legacy `ScheduleBuffSettle` implementation with old container identity.
  - `.codex_worktrees/` direct-call findings are historical worktree evidence and are not treated as current production blocker evidence.
- Next step:
  - Continue with US-002 by adding raw-container guardrail coverage and a retained-boundary ceiling for `zsim/sim_progress/Buff/ScheduleBuffSettle.py`.
---
## 2026-06-08 07:07 - US-002
- Files changed: `tests/simulator/test_buff_raw_container_guardrail.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `tests/simulator/test_buff_raw_container_guardrail.py` prepares to replace manual review of `ScheduleBuffSettle.py` raw old-container writes with AST-classified retained signatures and the `legacy ScheduleBuffSettle command-adapter internals` reference ceiling.
  - No live simulator runtime path was replaced in this story; it adds guardrail coverage around retained adapter internals.
- Compatibility retained:
  - Production `ScheduleBuffSettle.py` remains unchanged and still runs behind `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` with old container identity retained.
  - Current `DYNAMIC_BUFF_DICT` active-store references, enemy debuff mirror interactions, and registry/template inputs are retained only through the named guardrail boundary and ceiling.
- Next step:
  - Continue with US-003 by wiring validation profile targets for `zsim/sim_progress/Buff/ScheduleBuffSettle.py`.
---
## 2026-06-08 07:26 - US-003
- Files changed: `scripts/run_buff_refactor_validation.py`, `zsim/sim_progress/ScheduledEvent/runtime_command.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `scripts/run_buff_refactor_validation.py` prepares to replace manual confidence in retained `ScheduleBuffSettle.py` internals with explicit `lifecycle` and `implicit-events` scoped mypy coverage.
  - No live simulator runtime path was replaced in this story; the `LegacyRuntimeCommandAdapter` import/call cleanup preserves the same `RuntimeCommandPort` same-tick write boundary while making the retained settle function checkable.
- Compatibility retained:
  - `SkillEventHandler` and `AnomalyEventHandler` still route settle writes through `runtime_command_port.settle_buffs(...)`.
  - `ScheduleBuffSettle.py` still owns the retained legacy old-container settle implementation and keeps the keyword `sim_instance` handoff from the adapter.
- Next step:
  - Continue with US-004 by syncing the handoff docs and stale phase-1 checklist wording from the guardrail and validation evidence.
---
## 2026-06-08 08:07 - US-004
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - Handoff docs now replace stale 2026-06-05 / 2026-06-06 phase-1 backlog wording with historical/superseded status tied to `PRD-12 US-024` and the current guardrail evidence.
  - `docs/旧Buff系统耦合审查结果.md` records `ScheduleBuffSettle.py` raw old-container coverage under `legacy ScheduleBuffSettle command-adapter internals`; this prepares to replace manual review of retained settle internals, not a live runtime path.
- Compatibility retained:
  - `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` still own the same-tick settle write boundary, and `ScheduleBuffSettle.py` remains the retained adapter-internal legacy implementation.
  - Deleted `event_list` surfaces, closed producer batches, old-container ownership, listener broadcast, scheduled queue publish, and runtime write layers are not reopened or unified by this doc-sync story.
- Next step:
  - Continue with US-005 by documenting `.codex_worktrees` audit hygiene without mutating historical worktrees.
---
## 2026-06-08 08:15 - US-005
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/Buff重构下阶段计划草稿.md` and Ralph progress now replace ambiguous phase-1 / phase-2 source-scan handoff wording with an explicit `.codex_worktrees/` exclusion and root-workspace evidence rule.
  - No live simulator runtime path was replaced in this story; it documents audit hygiene for historical local worktree snapshots.
- Compatibility retained:
  - `.codex_worktrees/` remains untouched and is historical local worktree evidence only unless a future story explicitly audits archived branches.
  - Existing guardrail and validation scripts were not changed; `ScheduleBuffSettle.py` remains covered by the retained `legacy ScheduleBuffSettle command-adapter internals` guardrail and scoped typecheck profile.
- Next step:
  - Continue with US-006 final validation and closure handoff; after closure, the default route returns to phase 2 unless new guardrail, validation, or root-workspace source-scan evidence appears.
---
## 2026-06-08 08:23 - US-006
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The final closure handoff replaces the temporary phase-1 blocker-open state with validated closure evidence and restores the default route to phase 2 XLogic full classification / reuse convergence.
  - No live simulator runtime path was replaced in this story; it closes validation and documentation around the retained `ScheduleBuffSettle.py` guardrail boundary.
- Compatibility retained:
  - `ScheduleBuffSettle.py` remains retained `legacy ScheduleBuffSettle command-adapter internals` behind `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter`.
  - No old container was deleted, no `event_list` surface was reopened, no producer batch was restarted, and scheduled queue publish / listener broadcast / runtime immediate write remain separate layers.
- Next step:
  - Start the next PRD from phase 2: XLogic full classification and reuse convergence, unless new guardrail, validation, or root-workspace source-scan evidence exposes a concrete phase-1 production blocker.
---
## 2026-06-08 09:30 +08:00 - US-001
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` prepares to replace ad hoc phase-2 XLogic scans with a non-exclusive classification schema covering attribute reads, event triggers, record/count sync, anomaly / debuff / dot bypasses, service-location, formula snapshots, listener broadcast, scheduled publish, runtime immediate writes, and retained compatibility-only cases.
  - No live simulator runtime path or XLogic behavior was replaced in this story; it establishes the intake schema and boundary rules for later census and classification stories.
- Compatibility retained:
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, and `LegacyBuffRuntimeFacade` keep their current phase-1 retained boundaries.
  - Old containers, legacy `buff_add()`, legacy `KickOutBuff()`, Calculator / CalAnomaly `MultiplierData` snapshots, handler requeue, Load-stage continuation, listener broadcast, dot runtime registration, and `.codex_worktrees/` historical evidence treatment are unchanged.
- Next step:
  - Continue with US-002 by recomputing the full root-workspace `BuffXLogic` census and filling stable file / class / method metadata into the phase-2 matrix.
---
## 2026-06-08 09:40 +08:00 - US-002
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now replaces stale partial BuffXLogic scans with a root-workspace 149-module census, reproducible `rg` pattern counts, infrastructure / leaf separation, per-file class / record / method metadata, and already-migrated scheduled-publisher samples.
  - No live simulator runtime path or XLogic behavior was replaced in this story; it prepares later phase-2 classification and reuse-design stories.
- Compatibility retained:
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, and `LegacyBuffRuntimeFacade` keep their phase-1 retained boundaries.
  - Existing `MultiplierData` / Calculator snapshots, old containers, record/count writebacks, listener broadcast, dot runtime registration, and migrated dispatch publishers are unchanged.
  - `.codex_worktrees/` remains historical navigation evidence only unless a future story explicitly audits archived worktrees.
- Next step:
  - Continue with US-003 by classifying Calculator and attribute-read couplings from the census, using helper-family groups rather than a one-file replacement slice.
---
## 2026-06-08 09:49 +08:00 - US-003
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now replaces loose Calculator-read backlog wording with helper-family classification for AM / AP / impact / full crit rate / personal crit rate / personal crit damage, including read-only gate vs read-then-writeback boundaries.
  - No live Calculator, CalAnomaly, BuffXLogic, scheduled-event, listener, or runtime path was replaced in this story; it produces phase-2 classification evidence only.
- Compatibility retained:
  - `MultiplierData`, `MultiplierData as Mul`, Calculator / CalAnomaly formula snapshots, old dynamic Buff aggregation, old containers, record/count writebacks, and migrated `ScheduleDispatchPort` publishers are unchanged.
  - Existing `BuffAttributeReader` coverage remains limited to AM / AP representative samples; impact and crit helper candidates are documented but not implemented in this story.
- Next step:
  - Continue with US-004 by classifying event trigger and scheduled-publish couplings while keeping event ordering separate from Calculator-read helper buckets.
---
## 2026-06-08 09:59 +08:00 - US-004
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now replaces loose event-trigger backlog wording with event-semantic buckets for direct `ScheduleDispatchPort` publishers, factory-backed `SchedulePreload`, trigger-only `SkillNode` / `LoadingMission` gates, local preload injection, dot runtime registration, report helpers, and deleted raw queue surfaces.
  - No live BuffXLogic, scheduled-event handler, listener, or runtime path was replaced in this story; it produces phase-2 classification evidence only.
- Compatibility retained:
  - Existing `ScheduleDispatchPort` publishers, `schedule_preload_event_factory(...)`, `LoadingMission.mission_start(...)` ordering, `ScheduleRefreshData`, copied-anomaly payloads, `StunForcedTerminationEvent`, dot runtime registration, local `preload_data.external_add_skill(...)`, listener broadcast, and runtime write boundaries remain unchanged.
  - Deleted `JudgeTools.find_event_list()`, `check_preparation(..., event_list=...)`, `BuffRecordBaseClass.event_list`, and `record.event_list.append(...)` surfaces stay closed; root-workspace scans found no production raw queue reopen evidence.
- Next step:
  - Continue with US-005 by classifying record, count, and state-sync patterns without converting event-trigger buckets into implementation targets prematurely.
---
## 2026-06-08 10:09 +08:00 - US-005
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now prepares to replace loose record/count backlog wording with state-sync buckets for record initialization, pure trigger-buff reads, computed count writeback, incremental old-count adjustment, `built_in_buff_box` tuple sync, ledger/cooldown state, and template `update_to_buff_0(...)` sync.
  - No live BuffXLogic, Buff lifecycle, Calculator, scheduled-event, listener, or runtime path was replaced in this story; it produces phase-2 classification evidence only.
- Compatibility retained:
  - Old `buff_0` / `exist_buff_dict` identity, `check_record_module()` / `get_prepared(...)`, `simple_start(...)`, `dy.count`, `dy.built_in_buff_box`, and `update_to_buff_0(...)` semantics remain unchanged.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, deleted raw queue surfaces, listener broadcast, dot runtime registration, and Calculator / CalAnomaly snapshots remain separate retained boundaries.
- Next step:
  - Continue with US-006 by classifying runtime container and service-location couplings without adding a second write facade or expanding `BuffRuntimeReadPort` into writes.
---
## 2026-06-08 10:24 +08:00 - US-006
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now prepares to replace loose runtime-container backlog wording with buckets for static registry lookup, runtime read snapshots, same-tick command writes, facade-internal pending / active / enemy-mirror writes, direct simulator service context, and retained compatibility false positives.
  - No live BuffXLogic, runtime port, lifecycle, facade, or validation path was replaced in this story; it produces phase-2 classification evidence only.
- Compatibility retained:
  - Old `exist_buff_dict`, `LOADING_BUFF_DICT`, `DYNAMIC_BUFF_DICT`, enemy debuff mirror, legacy `buff_add()`, legacy `KickOutBuff()`, retained `ScheduleBuffSettle.py`, and `MultiplierData` formula snapshots remain unchanged.
  - `RuntimeCommandPort` remains the only same-tick write boundary, `BuffRuntimeReadPort` remains read-only, and `LegacyBuffRuntimeFacade` continues to retain old container identity by reference.
- Next step:
  - Continue with US-007 by classifying anomaly, debuff, dot, and formula-bypass couplings without collapsing scheduled publish, listener broadcast, dot runtime registration, and runtime immediate write into one boundary.
---
## 2026-06-08 10:32 +08:00 - US-007
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now prepares to replace loose anomaly / debuff / dot bypass backlog wording with layer-separated buckets for enemy anomaly-state gates, disorder / polarity outputs, freeze / frost / anomaly-debuff state, dot runtime registration / presence, `BuffAddStrategy` same-tick writes, and Calculator / CalAnomaly formula snapshots.
  - No live BuffXLogic, UpdateAnomaly, Dot, Calculator, runtime port, facade, listener, or validation path was replaced in this story; it produces phase-2 classification evidence only.
- Compatibility retained:
  - `UpdateAnomaly` scheduled publish stays on `ScheduleDispatchPort`; listener broadcast, dot runtime registration / removal, runtime immediate write, `AnomalyBar` runtime-view reads, and `BuffAddStrategy` facade-backed writes remain separate boundaries.
  - `Shock.DotFeature`, `CalAnomaly`, old enemy dynamic state, old container identity, `MultiplierData` snapshots, and enemy debuff mirror semantics remain retained compatibility / future classification candidates.
- Next step:
  - Continue with US-008 by producing the reusable pattern catalog and risk matrix from the completed US-001 through US-007 classification buckets, without turning dot runtime registration or formula snapshots into immediate replacement work.
---
## 2026-06-08 10:40 +08:00 - US-008
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now prepares to replace loose phase-2 follow-up planning with a reusable pattern catalog, risk matrix, ranked candidate pool, and CodeGraph cross-check notes for reader, record, event adapter, state-sync, handler, listener, facade-write, dot-runtime and validation patterns.
  - No live BuffXLogic, Calculator, CalAnomaly, dispatch, runtime port, facade, listener, Dot, guardrail, or validation behavior was replaced in this story; it produces phase-2 design evidence only.
- Compatibility retained:
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()`, legacy `KickOutBuff()`, `MultiplierData` / `MulData`, Calculator / CalAnomaly formula snapshots, listener broadcast, dot runtime registration, and deleted raw queue surfaces remain separate retained boundaries.
  - `.codex_worktrees/` CodeGraph hits remain historical navigation evidence only unless explicitly audited.
- Next step:
  - Continue with US-009 final validation and handoff doc sync, preserving the ranked phase-2 candidate pool and recommending the AM/AP reader + computed count state-sync family as the default next PRD seed unless validation exposes a concrete blocker.
---
## 2026-06-08 10:47 +08:00 - US-009
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/旧Buff系统耦合审查结果.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - This PRD replaces stale handoff wording that still treated phase-2 full classification as the next task with completed classification status, a synced coupling-review summary, and a concrete next default PRD: AM/AP reader + computed count state-sync.
  - No live `BuffXLogic`, Calculator, CalAnomaly, runtime port, facade, dispatch adapter, listener, Dot, guardrail, validation wiring, or simulator behavior was replaced in this PRD; it produces classification and handoff artifacts only.
- Compatibility retained:
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()`, legacy `KickOutBuff()`, Calculator / CalAnomaly formula snapshots, listener broadcast, dot runtime registration, and deleted raw queue surfaces remain separate retained boundaries.
  - The next-stage plan preserves a broad phase-2 candidate pool rather than collapsing to a single follow-up file.
- Next step:
  - Generate the next phase-2 PRD from the ranked pool, defaulting to the AM/AP reader + computed count state-sync family with `calculator-reads` validation and focused state-sync order tests.
---
## 2026-06-08 11:45 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - 本故事只建立 `P2-A AM/AP reader + computed count state-sync` 证据边界和 Ralph 工作说明，没有替换 live `BuffXLogic` 路径。
  - 后续 `BuffAttributeReadContext` / `CalculatorBuffAttributeReader` 迁移入口将准备替换六个 P2-A 文件中的 direct `MultiplierData` / `Mul(...)` AM/AP 读取职责。
- Compatibility retained:
  - `MultiplierData` / `CalAnomaly` formula snapshot、old `buff_0` identity、`simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` 顺序、phase-1 dispatch/runtime boundaries 均保留。
- Next step:
  - 继续 US-002，扩展 AM/AP reader parity test fixtures；不要在 parity/order tests 之前编辑生产 XLogic。
---
## 2026-06-08 11:54 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buff_attribute_reader.py` 新增可复用 reader parity fixture，准备替换六个 P2-A 文件中 direct `MultiplierData(...)` / `Mul(...)` AM/AP 读取前的测试基线。
  - 本故事只扩展测试夹具与 parity 覆盖，没有替换 live `BuffXLogic` 路径，也没有新增生产 `BuffAttributeReader` 方法。
- Compatibility retained:
  - `BranchBladeSongCritDamageBonus` 与 `TimeweaverDisorderDmgMul` 的现有 reader-backed sample coverage 保持通过。
  - `Calculator.AnomalyMul.cal_am(...)`、`Calculator.AnomalyMul.cal_ap(...)`、`MultiplierData`、`CalAnomaly` 公式、phase-1 dispatch/runtime boundaries 均保留。
- Next step:
  - 继续 US-003，添加 computed count state-sync 顺序测试，锁定 `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` 后再迁移生产 XLogic。
---
## 2026-06-08 12:01 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buff_attribute_state_sync.py` 新增 test-only computed count state-sync order harness，准备在后续迁移六个 P2-A AM/AP read-then-writeback 文件前替换“无顺序保护”的测试空白。
  - 本故事只新增测试边界，没有替换 live `BuffXLogic` 路径；`AliceAdditionalAbilityApBonus.special_judge_logic()` 仅在测试中通过 fake Buff probe 验证当前顺序。
- Compatibility retained:
  - `AliceAdditionalAbilityApBonus.py` 的 direct `MultiplierData(...)` / `Calculator.AnomalyMul.cal_am(...)` 读取、AM 阈值、`get_prepared(...)` 参数、old `buff_0` identity、`simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` 顺序均保留。
  - `ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、Calculator / CalAnomaly formula snapshots、raw queue deletion边界均未改变。
- Next step:
  - 继续 US-004，把 `tests/simulator/test_buff_attribute_state_sync.py` 接入 `calculator-reads` validation profile，避免后续 reader 迁移绕过顺序测试。
---
## 2026-06-08 12:08 +08:00 - US-004
- Files changed: `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `calculator-reads` validation profile now prepares to replace unguarded P2-A reader migration runs with a combined reader parity + computed count state-sync order validation slice.
  - 本故事只调整验证入口；没有替换 live `BuffXLogic` 路径，也没有新增生产 reader helper、dispatch adapter、runtime write facade 或 Calculator formula。
- Compatibility retained:
  - `tests/simulator/test_buff_attribute_reader.py` 与 `tests/simulator/test_buff_raw_container_guardrail.py` 保持在 `calculator-reads` focused pytest 中；base simulator、isolated teams、implicit-events profile 与既有 mypy targets 保留。
  - P2-A 六个 AM/AP 文件的 direct `MultiplierData(...)` / `Mul(...)` 读取、`simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` 顺序、phase-1 dispatch/runtime boundaries 均未改变。
- Next step:
  - 继续 US-005，决定是否引入窄 AM/AP reader context helper；后续迁移应通过 `calculator-reads` profile 同时覆盖 reader parity 和 state-sync order。
---
## 2026-06-08 12:15 +08:00 - US-005
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `create_anomaly_attribute_read_context(...)` prepares to replace repeated manual `BuffAttributeReadContext(...)` construction for P2-A AM/AP reader migrations without adding new `BuffAttributeReader` methods or hiding count formulas.
  - `tests/simulator/test_buff_attribute_reader.py` now uses the helper in its parity fixture and asserts the existing `BranchBladeSongCritDamageBonus` / `TimeweaverDisorderDmgMul` reader-backed samples do not recreate direct `MultiplierData` reads.
- Compatibility retained:
  - `CalculatorBuffAttributeReader.read_anomaly_mastery(...)` / `read_anomaly_proficiency(...)`, `Calculator.AnomalyMul.cal_am(...)`, `Calculator.AnomalyMul.cal_ap(...)`, `MultiplierData`, and `CalAnomaly` formula snapshots remain unchanged.
  - This story only builds a narrow context boundary and test coverage; no live P2-A `BuffXLogic` path, `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order, `ScheduleDispatchPort`, `RuntimeCommandPort`, or old-container deletion boundary changed.
- Next step:
  - 继续 US-006，迁移 `AliceAdditionalAbilityApBonus.py` 到 helper + AM reader，同时保持当前 AM count formula、max-count clamp 和 state-sync order。
---
## 2026-06-08 12:25 +08:00 - US-006
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/AliceAdditionalAbilityApBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `AliceAdditionalAbilityApBonus.special_judge_logic()` now replaces its direct `MultiplierData(...)` / `Calculator.AnomalyMul.cal_am(...)` AM read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader().read_anomaly_mastery(...)`.
  - `tests/simulator/test_buff_attribute_state_sync.py` now prepares the remaining P2-A migrations by using the old `MultiplierData(...)` path as a count oracle while driving migrated XLogic through the reader path.
- Compatibility retained:
  - Alice `get_prepared(char_CID=1401, sub_exist_buff_dict=1, enemy=1, dynamic_buff_list=1)`, AM threshold, `(am - 140) * trans_ratio`, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order remain covered.
  - `Calculator.AnomalyMul.cal_am(...)`, `MultiplierData`, Calculator / CalAnomaly formulas, phase-1 dispatch/runtime boundaries, scheduled publish, listener broadcast, and old-container deletion remain retained outside this story.
- Next step:
  - 继续 US-007，按同一 reader-oracle + state-sync order 模式迁移 `YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`，并保留 YUZUHA report / process-state behavior。
---
## 2026-06-08 12:34 +08:00 - US-007
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `YuzuhaAdditionalAbilityAnomalyBuildupBonus.special_hit_logic()` now replaces its direct `MultiplierData(...)` / `Calculator.AnomalyMul.cal_am(...)` AM read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader().read_anomaly_mastery(...)`.
  - `tests/simulator/test_buff_attribute_state_sync.py` now covers Yuzuha buildup below-threshold no-op, cinema 0 ratio, cinema 1+ capped ratio, aggregation shape, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order.
- Compatibility retained:
  - Yuzuha buildup `get_prepared(char_CID=1411, sub_exist_buff_dict=1, enemy=1, dynamic_buff_list=1)`, `cinema_1_ratio` initialization, `am < 100` early return, `min(am - 100, 100) * cinema_1_ratio`, and current no-report/process-state behavior remain covered.
  - `Calculator.AnomalyMul.cal_am(...)`, `MultiplierData`, Calculator / CalAnomaly formulas, phase-1 dispatch/runtime boundaries, scheduled publish, listener broadcast, and old-container deletion remain retained outside this story.
- Next step:
  - 继续 US-008，迁移 `YuzuhaAdditionalAbilityAnomalyDmgBonus.py` 到同一 AM reader + state-sync pattern，并保留该 sibling 当前的 `YUZUHA_REPORT` / `schedule_data.change_process_state()` 行为。
---
## 2026-06-08 12:43 +08:00 - US-008
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/YuzuhaAdditionalAbilityAnomalyDmgBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `YuzuhaAdditionalAbilityAnomalyDmgBonus.special_hit_logic()` now replaces its direct `MultiplierData(...)` / `Calculator.AnomalyMul.cal_am(...)` AM read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader().read_anomaly_mastery(...)`.
  - `tests/simulator/test_buff_attribute_state_sync.py` now covers the damage sibling's below-threshold no-op, cinema 0 ratio, cinema 1+ capped ratio, report/process-state ordering, and shared reader-backed AM source pattern.
- Compatibility retained:
  - Yuzuha damage `get_prepared(char_CID=1411, sub_exist_buff_dict=1, enemy=1, dynamic_buff_list=1)`, `cinema_1_ratio` initialization, `am < 100` early return, `min(am - 100, 100) * cinema_1_ratio`, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order remain covered.
  - `YUZUHA_REPORT` still gates `schedule_data.change_process_state()` after explicit `update_to_buff_0(...)`; Calculator / CalAnomaly formula snapshots and phase-1 dispatch/runtime boundaries remain retained outside this story.
- Next step:
  - 继续 US-009，迁移 `JaneCinema1APTransToDmgBonus.py` 到 AP reader seam，同时保留 trigger gate、`find_tick(...)`、AP damage count formula 和 state-sync order。
---
## 2026-06-08 12:54 +08:00 - US-009
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/JaneCinema1APTransToDmgBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `JaneCinema1APTransToDmgBonus.special_hit_logic()` now replaces its direct `MultiplierData as Mul` / `Mul(...)` / `Calculator.AnomalyMul.cal_ap(...)` AP read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader().read_anomaly_proficiency(...)`.
  - `tests/simulator/test_buff_attribute_state_sync.py` now covers Jane cinema-1 inactive trigger gate, active AP count parity, maxcount cap behavior, aggregation shape, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order.
- Compatibility retained:
  - Jane cinema-1 `special_judge_logic()` trigger gate, hit-path `get_prepared(...)` arguments, `find_tick(...)`, `min(ap * 0.1, self.buff_instance.ft.maxcount)`, and state-sync order remain covered.
  - `JaneCoreSkillStrikeCritRateBonus.py` and `JanePassionStateAPTransToATK.py` still retain their direct AP alias reads for their later stories; Calculator / CalAnomaly formula snapshots and phase-1 dispatch/runtime boundaries remain unchanged.
- Next step:
  - 继续 US-010，迁移 `JaneCoreSkillStrikeCritRateBonus.py` 到 AP reader seam，同时明确它是 AP-reader work，不是 full/personal crit-reader work。
---
## 2026-06-08 14:04 +08:00 - US-010
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/JaneCoreSkillStrikeCritRateBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `JaneCoreSkillStrikeCritRateBonus.special_hit_logic()` now replaces its direct `MultiplierData as Mul` / `Mul(...)` / `Cal.AnomalyMul.cal_ap(...)` AP read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader().read_anomaly_proficiency(...)`.
  - `tests/simulator/test_buff_attribute_state_sync.py` now covers Jane core crit-rate inactive trigger gate, active AP count parity, formula cap behavior, aggregation shape, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order.
- Compatibility retained:
  - Jane core crit-rate `special_judge_logic()` trigger gate, hit-path `get_prepared(...)` arguments, `find_tick(...)`, `min(40 + ap * 0.16, 100)`, and state-sync order remain covered.
  - This remains AP-reader work, not full/personal crit-reader work; Calculator / CalAnomaly formula snapshots, phase-1 dispatch/runtime boundaries, scheduled publish, listener broadcast, same-tick runtime write, and old-container deletion remain unchanged.
- Next step:
  - 继续 US-011，迁移 `JanePassionStateAPTransToATK.py` 到 AP reader seam，同时保留狂热状态 trigger gate、`floor(max(ap - 120, 0))` floor 行为和 state-sync order。
---
## 2026-06-08 14:12 +08:00 - US-011
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/JanePassionStateAPTransToATK.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `JanePassionStateAPTransToATK.special_hit_logic()` now replaces its direct `MultiplierData as Mul` / `Mul(...)` / `Cal.AnomalyMul.cal_ap(...)` AP read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader().read_anomaly_proficiency(...)`.
  - `tests/simulator/test_buff_attribute_state_sync.py` now covers Jane passion-state inactive trigger gate, AP under 120, fractional AP above 120, higher AP count parity, aggregation shape, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order.
- Compatibility retained:
  - Jane passion-state `special_judge_logic()` trigger gate, hit-path `get_prepared(...)` arguments, `find_tick(...)`, `floor(max(ap - 120, 0))`, and state-sync order remain covered.
  - This remains AP-reader work for AP-to-ATK count writeback; Calculator / CalAnomaly formula snapshots, phase-1 dispatch/runtime boundaries, scheduled publish, listener broadcast, same-tick runtime write, and old-container deletion remain unchanged.
- Next step:
  - 继续 US-012，为六个已迁移的 P2-A AM/AP 文件添加 source guardrail，防止 direct `MultiplierData(...)` / `Mul(...)` / `Calculator.AnomalyMul.cal_am/cal_ap(...)` 读口回流，同时保留 P2-B crit / impact reader 候选池。
---
## 2026-06-08 14:24 +08:00 - US-012
- Files changed: `tests/simulator/test_migrated_am_ap_reader_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_am_ap_reader_guardrail.py` replaces the remaining unguarded source surface for the six migrated P2-A AM/AP files by blocking direct `MultiplierData` imports, `MultiplierData(...)` / `Mul(...)`, and direct `Calculator.AnomalyMul.cal_am/cal_ap(...)` or `Cal.AnomalyMul.cal_am/cal_ap(...)` reads.
  - `scripts/run_buff_refactor_validation.py` now prepares future `calculator-reads` runs to catch legacy AM/AP reader reintroduction through both focused pytest and mypy target lists.
- Compatibility retained:
  - The guardrail intentionally scans only the six root migrated P2-A files and excludes `.codex_worktrees/`.
  - `zsim/sim_progress/ScheduledEvent/Calculator.py`, `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, and non-migrated phase-2 candidate buckets remain retained formula snapshot locations until their own PRDs run.
  - No live `BuffXLogic` behavior, count formula, state-sync order, `ScheduleDispatchPort`, `RuntimeCommandPort`, old-container deletion, scheduled publish, listener broadcast, or same-tick runtime write boundary changed in this story.
- Next step:
  - 继续 US-013，串行运行最终 focused validation / behavior sample decision，并把结果记录到 Ralph progress；不要把 P2-A guardrail 扩展成 P2-B crit / impact reader work。
---
## 2026-06-08 14:31 +08:00 - US-013
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This validation-only iteration does not replace live XLogic behavior; it validates the migrated P2-A AM/AP reader + computed count state-sync surface through direct focused pytest plus the `calculator-reads` and `implicit-events` validation profiles.
  - The behavior sample decision prepares final handoff by proving current registered teams do not include Alice, Yuzuha/柚叶, or Jane/简, so no main-loop behavior sample was run in this story.
- Compatibility retained:
  - The six migrated P2-A files, reader/context helper, state-sync order tests, source guardrail, Calculator / CalAnomaly formula snapshots, phase-1 dispatch/runtime boundaries, scheduled publish, listener broadcast, same-tick runtime write, and old-container deletion remain unchanged in this validation story.
  - Current registered teams remain `青衣雷属性队`, `席德大安比队`, `莱特火属性队`, and `薇薇安物理队`; future behavior samples should use a real registered Alice/Yuzuha/Jane fixture when one exists.
- Next step:
  - 继续 US-014，更新 handoff docs 和 next candidate pool，保留 P2-B through P2-F 候选块，不要把下一阶段计划收窄成单一路径。
---
## 2026-06-08 14:36 +08:00 - US-014
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - Handoff docs now replace stale “P2-A is next” planning with completed P2-A evidence and promote P2-B `crit / impact reader family package` as the next same-phase default PRD candidate.
  - `docs/BuffXLogic阶段2全量分类与复用矩阵.md` now marks the six P2-A AM/AP read-then-writeback files as migrated through the reader seam and guarded by focused parity / order / source tests.
- Compatibility retained:
  - No production XLogic, Calculator / CalAnomaly formula snapshot, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, old-container deletion, or same-tick runtime write boundary changed in this handoff story.
  - P2-B through P2-F, phase-3 formula snapshot replacement, retained compatibility rows, and blocker-only phase-1 reopen rules remain in the next-stage candidate pool.
- Next step:
  - 生成下一轮 Ralph PRD 时继续沿 [Buff重构方案.md](./Buff重构方案.md) 的阶段 2 路线，默认从 P2-B crit / impact reader family package 取材，并保留 P2-C through P2-F 候选块。
---
## 2026-06-08 16:02 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `scripts/ralph/progress.txt` now prepares P2-B `crit / impact reader family` work by replacing loose next-step context with a concrete source-evidence note, query terms, candidate file groups, required tests, retained boundaries, and non-goals.
  - No live `BuffXLogic`, Calculator, CalAnomaly, dispatch adapter, runtime port, listener, dot runtime-state, validation script, or simulator behavior was replaced in this story.
- Compatibility retained:
  - `MultiplierData`, Calculator / CalAnomaly formula snapshots, old `buff_0` identity, old containers, legacy `buff_add()` / `KickOutBuff()`, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime registration, and same-tick runtime write boundaries remain unchanged.
  - P2-C trigger-state gates, P2-D scheduled publish ordering, P2-E dot runtime-state, P2-F BuffAddStrategy facade-write design, phase-3 formula snapshot replacement, and blocker-only phase-1 reopen rules remain available.
- Next step:
  - Continue with US-002 by adding P2-B reader parity fixtures for impact, full crit rate, personal crit rate, and personal crit damage before production XLogic migrations.
---
## 2026-06-08 16:13 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buff_attribute_reader.py` now prepares to replace future direct P2-B `MultiplierData(...)` impact / crit reads by pinning test-only reader-seam parity against retained `Calculator.StunMul.cal_imp(...)`, `Calculator.RegularMul.cal_crit_rate(...)`, `Calculator.RegularMul.cal_personal_crit_rate(...)`, and `Calculator.RegularMul.cal_personal_crit_dmg(...)` snapshots.
  - This story builds the boundary test harness only; no live `BuffXLogic` path or production `CalculatorBuffAttributeReader` method is replaced yet.
- Compatibility retained:
  - Existing AM/AP reader tests, migrated P2-A XLogic paths, Calculator / CalAnomaly formula snapshots, `MultiplierData`, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, old containers, and state-sync behavior remain unchanged.
  - Full crit rate keeps `crit_rate_received_increase`; personal crit rate and personal crit damage keep received crit fields excluded.
- Next step:
  - Continue with US-003 by adding narrow production `CalculatorBuffAttributeReader` wrappers for impact, full crit rate, personal crit rate, and personal crit damage using the parity fixtures added here.
---
## 2026-06-08 16:22 +08:00 - US-003
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `CalculatorBuffAttributeReader` now prepares to replace future direct P2-B `MultiplierData(...)` impact / crit reads with `read_impact(...)`, `read_full_crit_rate(...)`, `read_personal_crit_rate(...)`, and `read_personal_crit_damage(...)`.
  - The new reader methods wrap retained Calculator snapshot formulas through the existing `BuffAttributeReadContext` / `_build_statements(...)` shape and a minimal `_build_formula_snapshot(...)`; no live `BuffXLogic` path is migrated in this story.
  - `tests/simulator/test_buff_attribute_reader.py` now exercises the production reader methods for P2-B parity instead of direct test-only Calculator calls.
- Compatibility retained:
  - `create_anomaly_attribute_read_context(...)`, AM/AP reader behavior, existing migrated P2-A files, `MultiplierData`, `Calculator.StunMul`, `Calculator.RegularMul`, `CalAnomaly`, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, old containers, and state-sync behavior remain unchanged.
  - Full crit rate still includes `crit_rate_received_increase`; personal crit rate and personal crit damage still exclude received crit fields.
- Next step:
  - Continue with US-004 by adding P2-B state-sync order coverage before migrating Lighter, QingYi, Trigger, or Soldier0 Anby production writeback files.
---
## 2026-06-08 16:38 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buff_attribute_state_sync.py` now prepares to replace future direct P2-B impact / personal crit read-then-writeback paths by pinning current Lighter, QingYi, Trigger, and Soldier0 Anby count formulas, aggregation shape, old `buff_0` identity, inactive gates, and state-sync order.
  - This story builds the state-sync harness only; no live `BuffXLogic` path is migrated yet.
- Compatibility retained:
  - Direct `MultiplierData(...)` / Calculator calls remain in `LighterAdditionalAbility_IceFireBonus.py`, `QingYiAdditionalAbilityStunConvertToATK.py`, `TriggerAdditionalAbilityStunBonus.py`, and `Soldier0AnbyCoreSkillCritDMGBonus.py` until their migration stories run.
  - Calculator / CalAnomaly formula snapshots, full-vs-personal crit semantics, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, old containers, and phase-1 boundaries remain unchanged.
- Next step:
  - Continue with US-005 by confirming P2-B focused tests remain wired into `calculator-reads`, then migrate Lighter impact read-through in US-006 using the pinned order harness.
---
## 2026-06-08 16:44 +08:00 - US-005
- Files changed: `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `CALCULATOR_ATTRIBUTE_READER_FOCUSED_TEST_TARGETS` replaces the inline reader focused-test path inside `calculator-reads`, making `tests/simulator/test_buff_attribute_reader.py` a named shared validation target for both pytest and mypy.
  - This story wires the P2-B validation boundary only; no live `BuffXLogic` path, Calculator formula, or event/runtime boundary was replaced.
- Compatibility retained:
  - `tests/simulator/test_buff_attribute_reader.py`, `tests/simulator/test_buff_attribute_state_sync.py`, raw-container guardrails, migrated AM/AP guardrails, and existing `calculator-reads` / `implicit-events` validation behavior remain covered.
  - Direct P2-B `MultiplierData(...)` / Calculator reads remain in Lighter, QingYi, Trigger, Soldier0 Anby, and event-adjacent full-crit candidates until their migration stories run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime write, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-006 by migrating `LighterAdditionalAbility_IceFireBonus.py` to `read_impact(...)` while preserving the US-004-pinned count/state-sync order.
---
## 2026-06-08 16:53 +08:00 - US-006
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/LighterAdditionalAbility_IceFireBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `LighterAdditionalAbility_IceFireBonus.py` now replaces its direct `MultiplierData(...)` / `Calculator.StunMul.cal_imp(...)` impact read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_impact(...)`.
  - The focused state-sync test now guards this migrated file against reintroducing the direct impact Calculator snapshot path.
- Compatibility retained:
  - Lighter `get_prepared(...)` arguments, impact threshold, `fake_count_delta` / count formula, real-count update, 300-count clamp, old `buff_0` identity, and `simple_start(...) -> read -> dy.count -> update_to_buff_0(...)` order remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.StunMul.cal_imp(...)`; QingYi, Trigger, Soldier0 Anby, and event-adjacent full-crit P2-B candidates remain on their old paths until their own stories run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, and old-container deletion boundaries remain unchanged.
- Next step:
  - Continue with US-007 by migrating `QingYiAdditionalAbilityStunConvertToATK.py` through `read_impact(...)` while preserving its old-`buff_0` adjustment order.
---
## 2026-06-08 17:01 +08:00 - US-007
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/QingYiAdditionalAbilityStunConvertToATK.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `QingYiAdditionalAbilityStunConvertToATK.py` now replaces its direct `MultiplierData(...)` / `Calculator.StunMul.cal_imp(...)` impact read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_impact(...)`.
  - The focused state-sync test now guards this migrated file against reintroducing the direct impact Calculator snapshot path.
- Compatibility retained:
  - QingYi `get_prepared(...)` arguments, `(stun_value - 120) * 6` formula, maxcount cap, old `buff_0` identity, and `simple_start(...) -> old buff_0 decrement -> read_impact(...) -> dy.count -> update_to_buff_0(...)` order remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.StunMul.cal_imp(...)`; Trigger, Soldier0 Anby, and event-adjacent full-crit P2-B candidates remain on their old paths until their own stories run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, and old-container deletion boundaries remain unchanged.
- Next step:
  - Continue with US-008 by migrating `TriggerAdditionalAbilityStunBonus.py` through `read_personal_crit_rate(...)` while preserving aftershock gates and count writeback order.
---
## 2026-06-08 17:10 +08:00 - US-008
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/TriggerAdditionalAbilityStunBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `TriggerAdditionalAbilityStunBonus.py` now replaces its direct `MultiplierData(...)` / `Calculator.RegularMul.cal_personal_crit_rate(...)` personal crit-rate read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_personal_crit_rate(...)`.
  - The focused state-sync test now guards this migrated file against reintroducing the direct personal crit Calculator snapshot path.
- Compatibility retained:
  - Trigger `special_judge_logic(...)` aftershock gate, `get_prepared(...)` arguments, `find_tick(...)`, `min(max(crit_rate - 0.4, 0) / 0.01 * 1.5, 75)` formula, old `buff_0` identity, and `read_personal_crit_rate(...) -> simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` order remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_personal_crit_rate(...)`; Soldier0 Anby and event-adjacent full-crit P2-B candidates remain on their old paths until their own stories run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, and old-container deletion boundaries remain unchanged.
- Next step:
  - Continue with US-009 by migrating `Soldier0AnbyCoreSkillCritDMGBonus.py` through `read_personal_crit_damage(...)` while preserving its existing simple-start-before-read order.
---
## 2026-06-08 17:24 +08:00 - US-009
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/Soldier0AnbyCoreSkillCritDMGBonus.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `Soldier0AnbyCoreSkillCritDMGBonus.py` now replaces its direct `MultiplierData as Mul` / `Calculator.RegularMul.cal_personal_crit_dmg(...)` personal crit-damage read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_personal_crit_damage(...)`.
  - The focused state-sync test now guards this migrated file against reintroducing the direct personal crit damage Calculator snapshot path.
- Compatibility retained:
  - Soldier0 Anby `special_judge_logic(...)` silver-star gate, `get_prepared(...)` arguments, `JudgeTools.find_tick(...)`, `crit_dmg * 0.3 * 100` count formula, uncapped high-count behavior, old `buff_0` identity, and `simple_start(..., no_count=1) -> read_personal_crit_damage(...) -> dy.count -> update_to_buff_0(...)` order remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_personal_crit_dmg(...)`; event-adjacent full-crit P2-B candidates remain on their old paths until their own stories run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, and old-container deletion boundaries remain unchanged.
- Next step:
  - Continue with US-010 by adding full crit event-adjacent test harness coverage for `CannonRotor.py`, `MiyabiCoreSkill_IceFire.py`, and `WoodpeckerElectroSet4_*` before production full-crit migrations.
---
## 2026-06-08 17:41 +08:00 - US-010
- Files changed: `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_full_crit_event_adjacent_reader.py` now prepares to replace future direct full-crit `MultiplierData(...)` / `Calculator.RegularMul.cal_crit_rate(...)` paths by pinning reader parity and current event-adjacent branch behavior for `CannonRotor.py`, `MiyabiCoreSkill_IceFire.py`, and `WoodpeckerElectroSet4_*`.
  - `FULL_CRIT_EVENT_ADJACENT_FOCUSED_TEST_TARGETS` wires this harness into both `calculator-reads` and `implicit-events` focused pytest / mypy profiles.
  - This story builds the full-crit event-adjacent harness only; no live `BuffXLogic` path is migrated yet.
- Compatibility retained:
  - Direct full-crit Calculator reads remain in CannonRotor, Miyabi IceFire, and Woodpecker variants until US-011 through US-015 migrate those files.
  - CannonRotor `LoadingMission.mission_start(...) -> publish_scheduled(...) -> simple_start(...)` ordering and Miyabi exit dispatch ordering remain covered by the existing dispatch tests.
  - Full crit rate still includes `crit_rate_received_increase`; personal crit rate remains distinct. `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and Calculator formula snapshots remain unchanged.
- Next step:
  - Continue with US-011 by migrating `CannonRotor.py` through `CalculatorBuffAttributeReader.read_full_crit_rate(...)` while preserving its RNG gate and scheduled publish behavior.
---
## 2026-06-08 17:51 +08:00 - US-011
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py`, `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `CannonRotor.py` now replaces its direct `MultiplierData(...)` / `Calculator.RegularMul.cal_crit_rate(...)` full-crit gate with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_full_crit_rate(...)`.
  - The focused full-crit event-adjacent test now guards CannonRotor against reintroducing the direct full-crit Calculator snapshot path.
- Compatibility retained:
  - CannonRotor `special_judge_logic(...)` SkillNode gate, `get_prepared(...)` arguments, RNG threshold result, full-crit received-bonus semantics, no-publish judge branch, and aggregation shape remain preserved.
  - CannonRotor `special_hit_logic(...)`, `_create_dispatch_port(...)`, `ScheduleDispatchPort.publish_scheduled(...)`, payload fields, and `LoadingMission.mission_start(...) -> publish_scheduled(...) -> simple_start(...)` order remain unchanged.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_crit_rate(...)`; Miyabi IceFire and Woodpecker variants remain on their old full-crit paths until their own stories run.
  - `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and phase-1 raw queue deletion work remain unchanged.
- Next step:
  - Continue with US-012 by migrating `MiyabiCoreSkill_IceFire.py` through `CalculatorBuffAttributeReader.read_full_crit_rate(...)` while preserving IceFire state, old-count adjustment, and dispatch behavior.
---
## 2026-06-08 17:59 +08:00 - US-012
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/MiyabiCoreSkill_IceFire.py`, `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `MiyabiCoreSkill_IceFire.py` now replaces its direct `MultiplierData(...)` / `Calculator.RegularMul.cal_crit_rate(...)` full-crit count read with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_full_crit_rate(...)`.
  - The focused full-crit event-adjacent test now guards Miyabi against reintroducing the direct full-crit Calculator snapshot path and pins judge gates plus maxcount cap behavior.
- Compatibility retained:
  - Miyabi `special_judge_logic(...)` SkillNode / element / frostburn-debuff gates, `special_exit_logic(...)` frostbite edge detection, dispatch publish behavior, `get_prepared(...)` arguments, old `buff_0` identity, and `simple_start(...) -> old-count decrement -> read_full_crit_rate(...) -> dy.count -> update_to_buff_0(...)` order remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_crit_rate(...)`; Woodpecker variants remain on their old full-crit paths until their own stories run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and phase-1 raw queue deletion work remain unchanged.
- Next step:
  - Continue with US-013 by migrating `WoodpeckerElectroSet4_NA.py` through `CalculatorBuffAttributeReader.read_full_crit_rate(...)` while preserving SkillNode/RNG gate behavior.
---

## 2026-06-08 18:08 +08:00 - US-013
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_NA.py`, `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `WoodpeckerElectroSet4_NA.py` now replaces its direct `MultiplierData(...)` / `Calculator.RegularMul.cal_crit_rate(...)` full-crit gate with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_full_crit_rate(...)`.
  - The focused full-crit event-adjacent test now guards the NA module against reintroducing direct full-crit Calculator snapshot imports or calls and pins the no-SkillNode no-RNG/no-state-sync branch.
- Compatibility retained:
  - NA `special_judge_logic(...)` preparation arguments, SkillNode / LoadingMission normalization, character tag gate, trigger level `0`, full-crit received-bonus semantics, RNG threshold result, no-publish behavior, and aggregation shape remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_crit_rate(...)`; `WoodpeckerElectroSet4_E_EX.py` and `WoodpeckerElectroSet4_CA.py` remain on their old direct full-crit paths until US-014 and US-015.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and phase-1 raw queue deletion work remain unchanged.
- Next step:
  - Continue with US-014 by migrating `WoodpeckerElectroSet4_E_EX.py` through `CalculatorBuffAttributeReader.read_full_crit_rate(...)` while preserving E/EX trigger level `2` and RNG gate behavior.
---

## 2026-06-08 18:18 +08:00 - US-014
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_E_EX.py`, `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `WoodpeckerElectroSet4_E_EX.py` now replaces its direct `MultiplierData(...)` / `Calculator.RegularMul.cal_crit_rate(...)` full-crit gate with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_full_crit_rate(...)`.
  - The focused full-crit event-adjacent test now guards the E/EX module against reintroducing direct full-crit Calculator snapshot imports or calls and pins the no-SkillNode no-RNG/no-state-sync branch.
- Compatibility retained:
  - E/EX `special_judge_logic(...)` preparation arguments, SkillNode / LoadingMission normalization, character tag gate, trigger level `2`, full-crit received-bonus semantics, RNG threshold result, no-publish behavior, and aggregation shape remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_crit_rate(...)`; `WoodpeckerElectroSet4_CA.py` remains on its old direct full-crit path until US-015.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and phase-1 raw queue deletion work remain unchanged.
- Next step:
  - Continue with US-015 by migrating `WoodpeckerElectroSet4_CA.py` through `CalculatorBuffAttributeReader.read_full_crit_rate(...)` while preserving CA trigger level `4` and RNG gate behavior.
---

## 2026-06-08 18:30 +08:00 - US-015
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/WoodpeckerElectroSet4_CA.py`, `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `WoodpeckerElectroSet4_CA.py` now replaces its direct `MultiplierData(...)` / `Calculator.RegularMul.cal_crit_rate(...)` full-crit gate with `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_full_crit_rate(...)`.
  - The focused full-crit event-adjacent test now guards the CA module against reintroducing direct full-crit Calculator snapshot imports or calls, covers the no-SkillNode no-RNG/no-state-sync branch, and pins the reader aggregation before RNG.
- Compatibility retained:
  - CA `special_judge_logic(...)` preparation arguments, SkillNode / LoadingMission normalization, character tag gate, trigger level `4`, full-crit received-bonus semantics, RNG threshold result, no-publish behavior, and aggregation shape remain preserved.
  - The retained Calculator formula snapshot still owns `Calculator.RegularMul.cal_crit_rate(...)`; P2-B source guardrail consolidation remains for US-016.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and phase-1 raw queue deletion work remain unchanged.
- Next step:
  - Continue with US-016 by adding the migrated P2-B source guardrail across the completed impact / crit reader files while keeping retained Calculator snapshots and non-migrated future buckets out of scope.
---
## 2026-06-08 18:39 +08:00 - US-016
- Files changed: `tests/simulator/test_migrated_p2b_reader_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_p2b_reader_guardrail.py` replaces the remaining unguarded source surface for the nine migrated P2-B impact / crit reader files by blocking direct `MultiplierData` imports, `MultiplierData(...)` / `Mul(...)`, and direct `Calculator.StunMul.cal_imp(...)`, `Calculator.RegularMul.cal_crit_rate(...)`, `Calculator.RegularMul.cal_personal_crit_rate(...)`, `Calculator.RegularMul.cal_personal_crit_dmg(...)`, or `Cal.*` alias reads.
  - `MIGRATED_P2B_READER_GUARDRAIL_FOCUSED_TEST_TARGETS` wires this guardrail into both `calculator-reads` focused pytest and mypy.
  - This story adds a source guardrail only; no live `BuffXLogic` behavior or Calculator formula snapshot was replaced.
- Compatibility retained:
  - The guardrail scans only the nine root migrated P2-B files and excludes `.codex_worktrees/`.
  - Retained formula snapshots in `zsim/sim_progress/ScheduledEvent/Calculator.py` and `zsim/sim_progress/ScheduledEvent/CalAnomaly.py` remain allowed.
  - Non-migrated phase-2 candidates such as `BranchBladeSongCritDamageBonus.py`, `Soldier0AnbyCoreSkillDMGBonus.py`, and `TimeweaverDisorderDmgMul.py` remain out of scope until their own PRDs run.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and phase-1 raw queue deletion work remain unchanged.
- Next step:
  - Continue with US-017 by running serial final validation and behavior-sample evidence for the completed P2-B package before handoff docs are updated in US-018.
---
## 2026-06-08 18:46 +08:00 - US-017
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This validation-only iteration does not replace live XLogic behavior; it validates the completed P2-B impact / crit reader family through direct focused pytest, `calculator-reads`, `implicit-events`, and one registered-team main-loop consistency sample.
  - `莱特火属性队` sample evidence covers an existing Lighter / Trigger route and matched baseline vs candidate outputs at stop tick 600.
- Compatibility retained:
  - The nine migrated P2-B files, reader/context helpers, source guardrail, retained Calculator formula snapshots, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and non-migrated P2-C/P2-D/P2-E/P2-F candidates remain unchanged.
- Next step:
  - Continue with US-018 by updating handoff docs and promoting the next same-phase candidate pool without narrowing future phase-2 work to the last migrated P2-B files.
---
## 2026-06-08 18:51 +08:00 - US-018
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - Handoff docs now replace stale “P2-B is next” planning with completed P2-B impact / crit reader evidence, file-specific migration status, validation summaries, behavior-sample evidence, and a concrete next default PRD: P2-C trigger-state read-only gates.
  - `scripts/ralph/progress.txt` records the US-018 preflight query terms and closure learnings so future PRD generation can promote the same-phase pool from evidence rather than the last migrated file.
- Compatibility retained:
  - P2-B migrated files, reader/context helpers, source guardrails, retained Calculator / CalAnomaly formula snapshots, `ScheduleDispatchPort`, `RuntimeCommandPort`, listener broadcast, dot runtime-state, same-tick runtime writes, old-container deletion boundaries, and non-migrated P2-C/P2-D/P2-E/P2-F candidates remain unchanged.
  - P2-C is promoted only as the next default planning route; this story does not replace live XLogic behavior or add a write API to `BuffRuntimeReadPort`.
- Next step:
  - Generate the next phase-2 PRD from [Buff重构方案.md](./Buff重构方案.md), defaulting to P2-C trigger-state read-only gates while preserving P2-D scheduled publish ordering, P2-E dot runtime-state, P2-F BuffAddStrategy facade-write design, phase-3 formula snapshots, retained compatibility rows, and blocker-only phase-1 reopen rules.
---
## 2026-06-08 19:46 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `scripts/ralph/progress.txt` P2-C working note prepares to replace loose trigger-state planning with root-workspace source evidence, current `trigger_buff_0=` pool classification, CodeGraph query evidence, retained boundary list, focused-test requirements, and validation outcomes.
  - This story only builds planning evidence; it does not replace live XLogic behavior yet.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, old template Buff identity in `history.record.trigger_buff_0`, `BuffRuntimeReadPort` read-only semantics, `RuntimeCommandPort` as the only same-tick write boundary, and `ScheduleDispatchPort` queue-only semantics.
- Next step:
  - Continue with US-002 by adding focused trigger-state read-only gate tests before introducing or migrating a production helper.
---
## 2026-06-08 19:54 +08:00 - US-002
- Files changed: `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_trigger_state_read_only_gates.py` prepares to replace ad hoc direct old-template trigger-state assertions with a focused read-only contract for `active`, `count`, `built_in_buff_box`, lazy `history.record`, and retained old `buff_0` identity.
  - This story only adds the focused test boundary; it does not replace live XLogic behavior or introduce the production helper yet.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, direct `record.trigger_buff_0.dy.*` reads in current XLogic files, `BuffRuntimeReadPort` read-only semantics, and separate `RuntimeCommandPort` / `ScheduleDispatchPort` write boundaries.
- Next step:
  - Continue with US-003 by adding the narrow production read-only trigger-state helper and rerunning the focused gate tests before migrating any XLogic file.
---
## 2026-06-08 20:03 +08:00 - US-003
- Files changed: `zsim/sim_progress/Buff/JudgeTools/TriggerState.py`, `zsim/sim_progress/Buff/JudgeTools/__init__.py`, `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `zsim/sim_progress/Buff/JudgeTools/TriggerState.py` prepares to replace direct `record.trigger_buff_0.dy.active` / `.dy.count` / `.dy.built_in_buff_box` read chains with immutable `TriggerBuffState` snapshots.
  - `tests/simulator/test_trigger_state_read_only_gates.py` now exercises the production helper after the existing `check_preparation(..., trigger_buff_0=...)` lookup path, without migrating live XLogic behavior yet.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, direct `record.trigger_buff_0.dy.*` reads in current XLogic files, and old template Buff identity in `history.record.trigger_buff_0`.
  - `BuffRuntimeReadPort` remains read-only and separate from this old-template trigger-state helper; `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, and Calculator formulas remain untouched.
- Next step:
  - Continue with US-004 by wiring the focused P2-C trigger-state test file and helper typing target into `implicit-events`, before migrating the first pure count gates.
---
## 2026-06-08 20:10 +08:00 - US-004
- Files changed: `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `TRIGGER_STATE_READ_ONLY_TARGETS` and `TRIGGER_STATE_READ_ONLY_FOCUSED_TEST_TARGETS` prepare the shared `implicit-events` gate to replace ad hoc direct runs of the P2-C trigger-state helper and focused test.
  - This story only wires validation coverage; it does not replace live XLogic behavior.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, direct `record.trigger_buff_0.dy.*` reads in current XLogic files, and old template Buff identity in `history.record.trigger_buff_0`.
  - `BuffRuntimeReadPort` remains read-only and separate from this old-template trigger-state helper; `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, lifecycle validation, and Calculator formulas remain untouched.
- Next step:
  - Continue with US-005 by migrating only `FlamemakerShakerApBonus.py` and `SpectralGazeImpactBonus.py` pure count gates through `read_trigger_buff_state(...)` while preserving no-write branch semantics.
---
## 2026-06-08 20:18 +08:00 - US-005
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/FlamemakerShakerApBonus.py`, `zsim/sim_progress/Buff/BuffXLogic/SpectralGazeImpactBonus.py`, `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `FlamemakerShakerApBonus.special_judge_logic(...)` and `SpectralGazeImpactBonus.special_judge_logic(...)` replace direct `record.trigger_buff_0.dy.active` / `.dy.count` chains with `read_trigger_buff_state(self.record)` snapshots after the existing `get_prepared(..., trigger_buff_0=...)` lookup.
  - `tests/simulator/test_trigger_state_read_only_gates.py` now includes root-only source assertions for those two migrated files, preparing the later migrated P2-C guardrail without scanning the remaining trigger-state pool.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, and old template Buff identity in `history.record.trigger_buff_0`.
  - Pure gate branches remain no-write: no `simple_start(...)`, no current `dy.count` mutation, no `update_to_buff_0(...)`, no scheduled publish, and no runtime command writes.
  - `SpectralGazeImpactBonus.xexit`, `BuffRuntimeReadPort`, `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, Calculator formulas, and the broader un-migrated `trigger_buff_0=` pool remain unchanged.
- Next step:
  - Continue with US-006 by migrating only `SharpenedStingerAnomalyBuildupBonus.py` through the same read-only trigger-state helper and adding its focused count samples.
---
## 2026-06-08 20:27 +08:00 - US-006
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/SharpenedStingerAnomalyBuildupBonus.py`, `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `SharpenedStingerAnomalyBuildupBonus.special_judge_logic(...)` replaces its direct `record.trigger_buff_0.dy.count` chain with `read_trigger_buff_state(self.record).count` after the existing `get_prepared(equipper="淬锋钳刺", preload_data=1, trigger_buff_0=(...))` lookup.
  - `tests/simulator/test_trigger_state_read_only_gates.py` now covers count `0`, `2`, `3`, and `4`, inverse `special_exit_logic(...)`, lazy record identity, old trigger template identity, retained preload record, no-write behavior, and root-only source assertion for this migrated file.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, and old template Buff identity in `history.record.trigger_buff_0`.
  - Pure gate behavior remains no-write: no `simple_start(...)`, no current `dy.count` mutation, no `update_to_buff_0(...)`, no scheduled publish, and no runtime command writes.
  - `BuffRuntimeReadPort`, `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, Calculator formulas, P2-B migrated files, and the broader un-migrated `trigger_buff_0=` pool remain unchanged.
- Next step:
  - Continue with US-007 by migrating only `CordisGerminaSNAAndQIgnoreDefense.py` tuple-box read-only gate through the helper, without adding tuple-box pruning, rebuild, derived count sync, or template sync behavior.
---
## 2026-06-08 20:38 +08:00 - US-007
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/CordisGerminaSNAAndQIgnoreDefense.py`, `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `CordisGerminaSNAAndQIgnoreDefense.special_judge_logic(...)` replaces the direct `record.trigger_buff_0.dy.built_in_buff_box` chain with `read_trigger_buff_state(self.record).built_in_buff_box` after the existing `get_prepared(equipper="机巧心种", trigger_buff_0=(...))` lookup.
  - `tests/simulator/test_trigger_state_read_only_gates.py` now locks tuple-box lengths `0`, `1`, `2`, and `3`, inverse `special_exit_logic(...)`, lazy record identity, old trigger template identity, no tuple-box sync, and the root-only source assertion for this migrated file.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, and old template Buff identity in `history.record.trigger_buff_0`.
  - This story does not add tuple-box pruning, tuple-box rebuild, derived count sync, template sync helper behavior, `BuffRuntimeReadPort` write APIs, scheduled publish, listener broadcast, runtime command writes, raw queue deletion, or Calculator formula changes.
- Next step:
  - Continue with US-008 by adding `AstralVoice.special_judge_logic(...)` no-write coverage before migrating that judge gate.
---
## 2026-06-08 20:47 +08:00 - US-008
- Files changed: `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_trigger_state_read_only_gates.py` prepares the `AstralVoice.special_judge_logic(...)` migration by adding no-write coverage for `skill_node is None`, production `SkillNode` and `LoadingMission` normalization, inactive trigger, non-7 trigger level, non-start mission state, missing mission tick state, and the active level-7 start branch.
  - This story only adds focused coverage; it does not replace live `AstralVoice.py` behavior yet.
- Compatibility retained:
  - `AstralVoice.py` remains unchanged: the judge gate still reads old-template `record.trigger_buff_0.dy.active`, and `special_effect_logic(...)` still owns the intentional `simple_start(...)` / current `dy.count` / `update_to_buff_0(...)` count-mirror path for a later story.
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, old template Buff identity in `history.record.trigger_buff_0`, `BuffRuntimeReadPort` read-only semantics, and separate `RuntimeCommandPort` / `ScheduleDispatchPort` write boundaries.
- Next step:
  - Continue with US-009 by migrating only `AstralVoice.special_judge_logic(...)` active-state reads through `read_trigger_buff_state(...)` while keeping `special_effect_logic(...)` unchanged until US-010.
---
## 2026-06-08 20:56 +08:00 - US-009
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/AstralVoice.py`, `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `AstralVoice.special_judge_logic(...)` replaces the direct old-template `record.trigger_buff_0.dy.active` chain with `read_trigger_buff_state(self.record).active` after the existing `get_prepared(equipper="静听嘉音", trigger_buff_0=(...), action_stack=1)` lookup.
  - `tests/simulator/test_trigger_state_read_only_gates.py` now includes the root-only `AstralVoice.py` source assertion in the migrated P2-C trigger-state gate set.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, action-stack preparation, `SkillNode` / `LoadingMission` normalization, `mission_dict[tick] == "start"` semantics, and old equipment-owner `buff_0` identity in `history.record`.
  - `AstralVoice.special_effect_logic(...)` remains unchanged for US-010: `simple_start(...)`, current `dy.count` mirror from `record.trigger_buff_0.dy.count`, and `update_to_buff_0(self.buff_0)` still run in the old order.
  - `BuffRuntimeReadPort`, `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, Calculator formulas, and the remaining un-migrated `trigger_buff_0=` pool remain unchanged.
- Next step:
  - Continue with US-010 by migrating only `AstralVoice.special_effect_logic(...)` count reads through the same read-only helper while preserving its current state-sync order.
---
## 2026-06-08 21:06 +08:00 - US-010
- Files changed: `zsim/sim_progress/Buff/BuffXLogic/AstralVoice.py`, `tests/simulator/test_trigger_state_read_only_gates.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `AstralVoice.special_effect_logic(...)` replaces the direct old-template `record.trigger_buff_0.dy.count` chain with `read_trigger_buff_state(self.record).count` while preserving the existing `get_prepared(equipper="静听嘉音", trigger_buff_0=(...), sub_exist_buff_dict=1)` lookup.
  - `tests/simulator/test_trigger_state_read_only_gates.py` now covers trigger counts `0`, `5`, and `99`, retained lazy record identity, retained old trigger template identity, retained `record.sub_exist_buff_dict`, and old template identity passed to `update_to_buff_0(...)`.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, `simple_start(...)`, current `dy.count` mirror write, `update_to_buff_0(self.buff_0)`, and old equipment-owner `buff_0` identity in `history.record`.
  - `BuffRuntimeReadPort` remains read-only and has no write API; `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, Calculator formulas, and the remaining un-migrated `trigger_buff_0=` pool remain unchanged.
- Next step:
  - Continue with US-011 by adding the migrated P2-C source guardrail for the exact completed migrated file set, without scanning the remaining un-migrated trigger-state pool.
---
## 2026-06-08 21:15 +08:00 - US-011
- Files changed: `tests/simulator/test_migrated_p2c_trigger_state_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_p2c_trigger_state_guardrail.py` replaces manual review of the completed migrated P2-C trigger-state source surface by AST-blocking direct `record.trigger_buff_0.dy.active`, `.dy.count`, and `.dy.built_in_buff_box` chains in the exact migrated root file set.
  - `MIGRATED_P2C_TRIGGER_STATE_GUARDRAIL_FOCUSED_TEST_TARGETS` wires the guardrail into `implicit-events` focused pytest and scoped mypy.
  - This story adds a source guardrail only; no live `BuffXLogic` behavior was replaced.
- Compatibility retained:
  - The guardrail scans only root `FlamemakerShakerApBonus.py`, `SpectralGazeImpactBonus.py`, `SharpenedStingerAnomalyBuildupBonus.py`, `CordisGerminaSNAAndQIgnoreDefense.py`, and `AstralVoice.py`, excluding `.codex_worktrees/`.
  - Remaining un-migrated `trigger_buff_0=` files, P2-A/P2-B migrated files, Calculator / CalAnomaly formula snapshots, `BuffAddStrategy`, `BuffRuntimeReadPort`, `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, and old template Buff identity remain unchanged.
- Next step:
  - Continue with US-012 by running serial validation / behavior-sample decision and recording whether registered representative teams exist; do not broaden the P2-C guardrail beyond migrated files.
---
## 2026-06-08 21:23 +08:00 - US-012
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This story is validation-only: `implicit-events` validation and one registered main-loop consistency sample validate the completed P2-C helper / migrated files / guardrail package, but no live `BuffXLogic` path is replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)`, old template Buff identity in `history.record.trigger_buff_0`, and the migrated-file-only P2-C source guardrail.
  - `BuffRuntimeReadPort` remains read-only; no `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion, Calculator formula, or default lifecycle behavior was changed.
  - Registered sample evidence: `席德大安比队` with `机巧心种` + `索魂影眸` matched total damage, event counts, and buff timeline exactly between the two report labels.
- Next step:
  - Continue with US-013 final handoff docs: mark P2-C validated/guarded completion evidence, record that no old-coupling review update was needed unless new evidence appears, and promote the next same-phase default from the retained phase-2 pool.
---
## 2026-06-08 21:34 +08:00 - US-013
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - Final handoff docs now replace stale “P2-C is next” planning with completed P2-C trigger-state helper / migrated-file / source-guardrail evidence, serial validation summaries, registered behavior-sample evidence, and a concrete next default PRD: P2-D scheduled publish ordering / adapter parity.
  - This story updates planning and handoff state only; it does not replace additional live `BuffXLogic` behavior.
- Compatibility retained:
  - P2-C migrated files, `TriggerBuffState`, `read_trigger_buff_state(record)`, focused no-write / count-mirror tests, migrated-file-only guardrail, remaining un-migrated `trigger_buff_0=` pool, `BuffRuntimeReadPort`, `RuntimeCommandPort`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, raw queue deletion boundaries, Calculator / CalAnomaly formula snapshots, old template Buff identity, and old containers remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence found no new coupling beyond existing P2-C completion and retained P2-D/P2-E/P2-F/direct-context pool entries.
- Next step:
  - Generate the next phase-2 PRD from [Buff重构方案.md](./Buff重构方案.md), defaulting to P2-D scheduled publish ordering / adapter parity while preserving P2-E dot runtime-state, P2-F BuffAddStrategy facade-write design, direct simulator context helpers, phase-3 formula snapshots, retained compatibility rows, and blocker-only phase-1 reopen rules.
---
## 2026-06-08 22:38 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `scripts/ralph/progress.txt` now prepares to replace ad hoc P2-D scope selection with root-workspace source evidence, CodeGraph navigation terms, payload-family classification, retained boundaries, and focused-test directions for scheduled publish ordering / adapter parity.
  - This story is evidence and scope setup only; it does not replace a live `BuffXLogic`, `UpdateAnomaly`, dispatch adapter, listener, dot runtime, runtime command, or Calculator path.
- Compatibility retained:
  - All existing scheduled publishers continue through their current `ScheduleDispatchPort` paths, and old retained boundaries remain unchanged: listener broadcast, dot runtime registration/removal, runtime immediate writes, `RuntimeCommandPort`, old containers, Calculator / CalAnomaly formula snapshots, and completed P2-A / P2-B / P2-C guardrails.
  - `ScheduleDispatchPort` remains queue-only, with raw queue access retained only inside `LegacyEventListScheduleDispatchAdapter`.
- Next step:
  - Continue with US-002 by adding adapter creation / event-list rebinding coverage and verifying P2-D producers create dispatch ports on demand rather than caching stale queue adapters.
---
## 2026-06-08 22:48 +08:00 - US-002
- Files changed: `tests/simulator/test_schedule_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_schedule_dispatch.py` prepares to replace manual adapter-boundary review with focused coverage for `create_schedule_dispatch_port(...)` binding to the current `schedule_data.event_list`, rebinding after list replacement, and the queue-only public API surface.
  - This story adds dispatch adapter coverage only; it does not replace a live producer path or change `ScheduleDispatchPort` / `LegacyEventListScheduleDispatchAdapter` production behavior.
- Compatibility retained:
  - Old paths still retained in this iteration: all P2-D producers still create dispatch ports through their existing local `_create_dispatch_port(...)` / direct `create_schedule_dispatch_port(...)` calls, and raw queue access remains internal to `LegacyEventListScheduleDispatchAdapter`.
  - Scheduler priority sorting, handler requeue behavior, core Load/Schedule appends, listener broadcast, dot runtime registration, runtime command writes, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-003 by adding resource-refresh payload parity coverage for the P2-D resource refresh family while reusing the adapter rebinding baseline from `test_schedule_dispatch.py`.
---
## 2026-06-08 22:57 +08:00 - US-003
- Files changed: `tests/simulator/test_xstart_sp_refresh_dispatch.py`, `tests/simulator/test_xhit_sp_refresh_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_xstart_sp_refresh_dispatch.py` prepares to replace manual resource-refresh order review for `ElegantVanitySpRecover` and `LunarNoviluna` by asserting exact `ScheduleRefreshData` SP payload fields, default decibel fields, fail-fast raw queue behavior, and source-specific `simple_start(...)` / `publish_scheduled(...)` order.
  - `tests/simulator/test_xhit_sp_refresh_dispatch.py` prepares to replace manual resource-refresh order review for `MagneticStormCharlieSpRecover` and `SeedAdditionalAbilityTrigger` by asserting exact SP payload fields, default decibel fields, fail-fast raw queue behavior, Seed publish-before-report ordering, and the retained report-only `change_process_state()` / print branch.
  - This story strengthens focused parity coverage only; no live `BuffXLogic` resource-refresh producer behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `ElegantVanitySpRecover`, `LunarNoviluna`, `MagneticStormCharlieSpRecover`, `SeedAdditionalAbilityTrigger`, and `SliceofTimeExtraResources` still publish through their existing `_create_dispatch_port(...)` / `create_schedule_dispatch_port(...)` paths.
  - Scheduler priority sorting, handler requeue behavior, core Load/Schedule appends, listener broadcast, dot runtime registration, runtime command writes, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-004 by adding `SkillNode` / `LoadingMission` publish order parity coverage for the P2-D scheduled publish family, without reopening resource-refresh production behavior.
---
## 2026-06-08 23:07 +08:00 - US-004
- Files changed: `tests/simulator/test_cannon_rotor_dispatch.py`, `tests/simulator/test_yixuan_cinema1_dispatch.py`, `tests/simulator/test_yanagi_polarity_disorder_dispatch.py`, `tests/simulator/test_hugo_totalize_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_cannon_rotor_dispatch.py` and `tests/simulator/test_yixuan_cinema1_dispatch.py` prepare to replace manual SkillNode publish-order review by asserting failed judge branches do not publish and by retaining exact `LoadingMission.mission_start(...) -> publish_scheduled(...)` payload identity/order coverage.
  - `tests/simulator/test_yanagi_polarity_disorder_dispatch.py` prepares to replace manual polarity-disorder publish/reset review by asserting publish happens while `polarity_disorder_update_signal` is still set, then the signal and counter reset, plus a no-anomaly no-publish branch.
  - `tests/simulator/test_hugo_totalize_dispatch.py` prepares to replace manual totalize multi-publish review by asserting totalize node / optional stun event publish before `active_signal` reset and the active-signal `0` no-scheduled-publish branch.
  - This story strengthens focused parity coverage only; no live `BuffXLogic` SkillNode / LoadingMission producer behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `CannonRotor`, `YixuanCinema1Trigger`, `YanagiPolarityDisorderTrigger`, and `HugoCorePassiveTotalizeTrigger` still publish through their existing `_create_dispatch_port(...)` / `create_schedule_dispatch_port(...)` paths.
  - Scheduler priority sorting, handler requeue behavior, core Load/Schedule appends, listener broadcast, dot runtime registration, runtime command writes, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-005 by adding stateful anomaly / dot scheduled publish coverage while keeping scheduled payloads separate from listener broadcast, dot runtime registration, and same-tick runtime writes.
---
## 2026-06-08 23:13 +08:00 - US-005
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `tests/simulator/test_alice_dot_trigger_dispatch.py`, `tests/simulator/test_vivian_dot_trigger_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_update_anomaly_dispatch.py` prepares to replace manual `UpdateAnomaly` stateful publish-layer review by asserting synchronous anomaly / disorder listener broadcasts happen before scheduled publishes, exact anomaly / disorder payload fields are retained, and freeze follow-up publish happens before runtime dot ending/removal.
  - `tests/simulator/test_alice_dot_trigger_dispatch.py` and `tests/simulator/test_vivian_dot_trigger_dispatch.py` prepare to replace manual dot-layer review by asserting dot runtime registration/removal remains on `enemy.dynamic.dynamic_dot_list`, while only the intended anomaly payload or `SkillNode` is published through `ScheduleDispatchPort`.
  - This story strengthens focused parity coverage only; no live `UpdateAnomaly`, `BattleEventListener`, or `BuffXLogic` stateful-dot producer behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `UpdateAnomaly.update_anomaly(...)`, `AliceDotTriggerListener.listener_active(...)`, and `VivianDotTrigger.special_hit_logic(...)` still use their existing on-demand `create_schedule_dispatch_port(...)` / `_create_dispatch_port()` publish paths.
  - Listener broadcast remains synchronous, dot runtime registration/removal remains a direct `dynamic_dot_list` mutation, runtime immediate writes remain outside scheduled-publish parity tests, and Scheduler priority sorting, handler requeue behavior, old containers, `RuntimeCommandPort`, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-006 by inspecting and extending fan-out / multi-publish / priority parity coverage only where P2-D root-workspace gaps remain.
---
## 2026-06-08 23:25 +08:00 - US-006
- Files changed: `tests/simulator/test_decibel_manager_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_decibel_manager_dispatch.py` prepares to replace manual fan-out / adapter-rebinding review for `Decibelmanager` by asserting inactive-generation / unsupported-trigger no-publish branches and real on-demand dispatch rebinding after `schedule_data.event_list` replacement.
  - This story strengthens focused parity coverage only; no live fan-out, multi-publish, priority sorting, or scheduled-publish production behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `Decibelmanager`, `Character/Yuzuha`, `HugoCorePassiveTotalizeTrigger`, `BreakingLegManager`, `VivianCorePassiveTrigger`, and `VivianCinema6Trigger` continue using their existing `_create_dispatch_port(...)` / `create_schedule_dispatch_port(...)` publish paths.
  - Scheduler priority sorting, handler requeue behavior, core Load/Schedule appends, listener broadcast, dot runtime registration, runtime command writes, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-007 by adding exact-file P2-D scheduled-publish source guardrails and validation-profile wiring, using the migrated producer set and retained boundaries recorded in US-001 through US-006.
---
## 2026-06-08 23:32 +08:00 - US-007
- Files changed: `tests/simulator/test_migrated_p2d_scheduled_publish_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_p2d_scheduled_publish_guardrail.py` prepares to replace manual source review for the P2-D migrated scheduled-publish producer set by blocking raw queue access, legacy event-list discovery, event-list preparation requests, and stale cached dispatch adapters.
  - `scripts/run_buff_refactor_validation.py` now includes the P2-D migrated-source guardrail in the implicit-events focused pytest and mypy profiles.
  - This story adds source guardrail coverage only; no live scheduled-publish producer behavior or dispatch adapter behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: all P2-D producers keep their existing on-demand `_create_dispatch_port(...)` / `create_schedule_dispatch_port(...)` publish paths.
  - Core `ScheduleDispatchPort` adapter internals, `SchedulePreload`, listener broadcast, dot runtime registration/removal, runtime immediate writes, local Character event groups, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-008 by running serial validation and recording the behavior-sample decision; if no production behavior changed, focused parity and the new exact-file source guardrail are the relevant evidence.
---
## 2026-06-08 23:44 +08:00 - US-008
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This validation-only story does not replace live scheduled-publish behavior; it validates the completed P2-D focused tests, exact-file guardrail, and implicit-events wiring through one serial `run_buff_refactor_validation.py --typecheck-profile implicit-events` run.
  - The behavior sample is intentionally skipped because this P2-D PRD changed tests, guardrails, validation wiring, docs, and Ralph artifacts only; no production scheduled-publish order changed.
- Compatibility retained:
  - Old paths still retained in this iteration: all P2-D producers keep their existing on-demand `_create_dispatch_port(...)` / `create_schedule_dispatch_port(...)` publish paths.
  - `ScheduleDispatchPort` queue-only semantics, core adapter internals, listener broadcast, dot runtime registration/removal, runtime immediate writes, `RuntimeCommandPort`, old containers, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-009 final handoff docs, promoting the next same-phase pool without reopening P2-D production behavior or broadening the P2-D guardrail beyond migrated scheduled-publish files.
---
## 2026-06-08 23:50 +08:00 - US-009
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - Final handoff docs now replace stale “P2-D is next” planning with completed P2-D scheduled publish ordering / adapter parity evidence, serial validation summaries, behavior-sample skip rationale, and a concrete next default PRD: P2-E dot runtime-state / initialization.
  - This story updates planning and handoff state only; it does not replace additional live `BuffXLogic`, `UpdateAnomaly`, dispatch adapter, listener, dot runtime, runtime command, or Calculator behavior.
- Compatibility retained:
  - P2-D migrated producers, exact-file source guardrail, focused dispatch tests, `ScheduleDispatchPort` queue-only semantics, listener broadcast, dot runtime registration/removal, runtime immediate writes, `RuntimeCommandPort`, old containers, Calculator / CalAnomaly formula snapshots, P2-E / P2-F / direct context candidates, and blocker-only phase-1 reopen rules remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence found no new coupling beyond existing P2-D completion and retained P2-E/P2-F/direct-context pool entries.
- Next step:
  - Generate the next phase-2 PRD from [Buff重构方案.md](./Buff重构方案.md), defaulting to P2-E dot runtime-state / initialization while preserving P2-F BuffAddStrategy facade-write design, direct simulator context helpers, P2-D guarded maintenance, phase-3 formula snapshots, retained compatibility rows, and blocker-only phase-1 reopen rules.
---
## 2026-06-09 03:04 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This evidence-only story prepares P2-E dot runtime-state / initialization coverage to replace manual scope review for `VivianDotTrigger.special_hit_logic(...)`, `VivianCinema1Debuff.special_judge_logic(...)`, `Shock.DotFeature.__post_init__()`, `UpdateAnomaly.anomaly_effect_active(...)`, `spawn_anomaly_dot(...)`, and `remove_dots_cause_disorder(...)`.
  - No live `BuffXLogic`, `UpdateAnomaly`, `Dot`, dispatch adapter, listener, runtime command, facade, old-container, Calculator, or CalAnomaly behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: Vivian dot registration still mutates `enemy.dynamic.dynamic_dot_list`, Shock duration still reads the documented Rina passive inputs, UpdateAnomaly dot replacement / removal still mutates runtime dot state, Vivian and freeze follow-up scheduled payloads still publish through `ScheduleDispatchPort`, and debuff writes still route through `buff_add_strategy(...)`.
  - P2-A / P2-B / P2-C / P2-D completed buckets, phase-1 raw queue deletion, old-container deletion, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, direct simulator context candidates, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-002 by auditing existing dot coverage and defining a minimal dot runtime-state contract before adding helper / adapter production code.
---
## 2026-06-09 03:10 +08:00 - US-002
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This audit-only story prepares a minimal P2-E dot runtime-state contract to replace manual reasoning about `dynamic_dot_list` read / find, register, replace, remove, and snapshot responsibilities before any production helper is introduced.
  - No live `BuffXLogic`, `UpdateAnomaly`, `Dot`, dispatch adapter, listener, runtime command, facade, old-container, Calculator, or CalAnomaly behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: Vivian dot registration still mutates `enemy.dynamic.dynamic_dot_list`, Shock duration still reads the documented Rina passive inputs, UpdateAnomaly dot replacement / removal still mutates runtime dot state, Vivian and freeze follow-up scheduled payloads still publish through `ScheduleDispatchPort`, and debuff writes still route through `buff_add_strategy(...)`.
  - P2-A / P2-B / P2-C / P2-D completed buckets, phase-1 raw queue deletion, old-container deletion, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, direct simulator context candidates, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-003 by adding Vivian dot presence and registration focused coverage before adding a dot runtime-state helper / adapter.
---
## 2026-06-09 03:19 +08:00 - US-003
- Files changed: `tests/simulator/test_vivian_dot_trigger_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_vivian_dot_trigger_dispatch.py` prepares to replace manual Vivian dot-layer review by asserting registration order, duplicate no-publish behavior, `VivianCinema1Debuff.special_judge_logic(...)` dot presence true / false branches, and old record/template identity preservation.
  - This story strengthens focused parity coverage only; no live `VivianDotTrigger`, `VivianCinema1Debuff`, dot runtime-state helper, dispatch adapter, listener, runtime command, old-container, Calculator, or CalAnomaly behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `VivianDotTrigger.special_hit_logic(...)` still creates and starts the dot, starts `LoadingMission`, appends to `enemy.dynamic.dynamic_dot_list`, then publishes dot `skill_node_data` through `ScheduleDispatchPort`.
  - `VivianCinema1Debuff.special_judge_logic(...)` remains a pure `enemy.find_dot("ViviansProphecy")` presence gate; listener broadcast, runtime command writes, raw scheduler queue writes, `RuntimeCommandPort`, `BuffRuntimeReadPort`, old containers, and formula snapshots remain unchanged.
- Next step:
  - Continue with US-004 by adding Shock dot duration initialization coverage before introducing any initialization read helper / adapter.
---
## 2026-06-09 03:27 +08:00 - US-004
- Files changed: `tests/simulator/test_dot_runtime_initialization.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_dot_runtime_initialization.py` prepares to replace manual Shock dot duration review by pinning the existing `sim_instance is None` `ValueError`, no-`丽娜` `600`, `丽娜` without passive `600`, and `丽娜` with `Buff-角色-丽娜-组队被动-延长感电` `780` outcomes.
  - `scripts/run_buff_refactor_validation.py` now includes the Shock duration initialization focused test in the `implicit-events` focused pytest and scoped mypy profiles.
  - This story strengthens focused parity coverage only; no live `Shock.DotFeature.__post_init__()`, dot initialization helper, dispatch adapter, listener, runtime command, old-container, Calculator, or CalAnomaly behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `Shock.DotFeature.__post_init__()` still directly reads `sim_instance.init_data.name_box` and `sim_instance.load_data.exist_buff_dict["丽娜"]` to choose Shock duration.
  - `ScheduleDispatchPort`, `enemy.dynamic.dynamic_dot_list`, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort`, old containers beyond the documented Rina passive read, and Calculator / CalAnomaly formula snapshots remain unchanged.
- Next step:
  - Continue with US-005 by adding `UpdateAnomaly.anomaly_effect_active(...)` dot replacement and debuff-separation focused coverage before introducing any dot runtime-state helper / adapter.
---
## 2026-06-09 03:33 +08:00 - US-005
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_update_anomaly_dispatch.py` prepares to replace manual `UpdateAnomaly.anomaly_effect_active(...)` dot replacement review by pinning same-index old-dot `end(timenow)`, runtime list removal, new-dot append-once behavior, `spawn_anomaly_dot(...) == False` no-mutation behavior, and `buff_add_strategy(...)` debuff separation.
  - This story strengthens focused parity coverage only; no live `UpdateAnomaly`, dot runtime-state helper, dispatch adapter, listener, runtime command, old-container, Calculator, or CalAnomaly behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `anomaly_effect_active(...)` still calls `buff_add_strategy(...)` for accompanying debuffs, uses `spawn_anomaly_dot(...)` for accompanying dots, mutates `enemy.dynamic.dynamic_dot_list` directly for replacement, and leaves the historical `# event_list.append(new_dot)` comment as non-production text.
  - Scheduled publish, listener broadcast, same-tick runtime writes, `RuntimeCommandPort`, `BuffRuntimeReadPort`, old containers, `CalAnomaly`, and anomaly formulas remain unchanged.
- Next step:
  - Continue with US-006 by adding `remove_dots_cause_disorder(...)` non-freeze removal, freeze mutation, process-state, and invalid-entry coverage before introducing the dot runtime-state helper / adapter.
---
## 2026-06-09 03:45 +08:00 - US-006
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_update_anomaly_dispatch.py` prepares to replace manual `remove_dots_cause_disorder(...)` dot removal review by pinning non-freeze runtime-list removal, freeze / freeze-dot follow-up scheduled publish, freeze dot dynamic-state updates, `change_process_state()` side effects, and invalid-entry `TypeError` behavior.
  - This story strengthens focused parity coverage only; no live `UpdateAnomaly`, dot runtime-state helper, dispatch adapter, listener, runtime command, old-container, Calculator, or CalAnomaly behavior was replaced in this iteration.
- Compatibility retained:
  - Old paths still retained in this iteration: `remove_dots_cause_disorder(...)` still mutates `enemy.dynamic.dynamic_dot_list` directly for dot removal, and only freeze / freeze-dot follow-up anomaly data publishes through `ScheduleDispatchPort`.
  - Listener broadcast, same-tick runtime writes, `RuntimeCommandPort`, `BuffRuntimeReadPort`, old containers, `LoadDamageEvent`, `Update_Buff.update_dot()`, handler requeue, damage-effect continuation, `CalAnomaly`, and anomaly formulas remain unchanged.
- Next step:
  - Continue with US-007 by introducing the dot runtime-state helper / adapter against the locked removal / replacement behavior before migrating production callsites.
---
## 2026-06-09 04:01 +08:00 - US-007
- Files changed: `zsim/sim_progress/Dot/runtime_state.py`, `zsim/sim_progress/Dot/__init__.py`, `tests/simulator/test_dot_runtime_state_adapter.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `DotRuntimeStateAdapter` prepares to replace open-coded `enemy.dynamic.dynamic_dot_list` search, duplicate-safe registration, same-index replacement, removal, and iteration-snapshot responsibilities in selected P2-E callsites.
  - `tests/simulator/test_dot_runtime_state_adapter.py` replaces manual helper-boundary review by proving raw-list parity for duplicate prevention, replacement order, removal order, safe snapshots, and no scheduled publish / listener broadcast / runtime-command side effects.
- Compatibility retained:
  - Old paths still retained in this iteration: `VivianDotTrigger`, `VivianCinema1Debuff`, `UpdateAnomaly.anomaly_effect_active(...)`, `remove_dots_cause_disorder(...)`, `Shock.DotFeature.__post_init__()`, `LoadDamageEvent`, `Update_Buff.update_dot()`, and Alice dot listener callsites still use their existing runtime-dot paths.
  - Scheduled follow-up publish remains on `ScheduleDispatchPort`; Buff / Debuff writes remain on existing `buff_add_strategy(...)` / facade paths; listener broadcast, `RuntimeCommandPort`, old containers, Calculator, and CalAnomaly formulas remain unchanged.
- Next step:
  - Continue with US-008 by migrating Vivian dot runtime-state callers to the helper while preserving dot start, `LoadingMission.mission_start(...)`, runtime registration, then scheduled publish order.
---
## 2026-06-09 04:02 +08:00 - US-008
- Files changed: `zsim/sim_progress/Dot/runtime_state.py`, `zsim/sim_progress/Buff/BuffXLogic/VivianDotTrigger.py`, `zsim/sim_progress/Buff/BuffXLogic/VivianCinema1Debuff.py`, `tests/simulator/test_dot_runtime_state_adapter.py`, `tests/simulator/test_vivian_dot_trigger_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `DotRuntimeStateAdapter.find_active_by_index(...)` replaces `enemy.find_dot("ViviansProphecy")` active-presence reads for migrated Vivian dot gates without changing inactive-dot behavior.
  - `VivianDotTrigger.special_hit_logic(...)` now replaces direct runtime-list append with `dot_runtime_state.register(dot)` while retaining caller-owned dot creation, `dot.start(...)`, `LoadingMission.mission_start(...)`, and `ScheduleDispatchPort.publish_scheduled(dot.skill_node_data)` ordering.
  - `VivianCinema1Debuff.special_judge_logic(...)` now uses the dot runtime-state helper for its cinema-1 presence gate.
- Compatibility retained:
  - Scheduled follow-up publish remains on `ScheduleDispatchPort`; dot runtime registration is not converted into scheduled backlog, listener broadcast, runtime command writes, old-container writes, `BuffRuntimeReadPort` writes, Calculator, and CalAnomaly formulas remain unchanged.
  - Old paths still retained in this iteration: `UpdateAnomaly.anomaly_effect_active(...)`, `remove_dots_cause_disorder(...)`, `Shock.DotFeature.__post_init__()`, `LoadDamageEvent`, `Update_Buff.update_dot()`, and Alice dot listener callsites keep their current runtime-dot paths.
- Next step:
  - Continue with US-009 by migrating `UpdateAnomaly` dot replacement / removal callers to the helper while preserving `buff_add_strategy(...)`, freeze follow-up scheduled publish, process-state/report ordering, and removal semantics.
---
## 2026-06-09 04:10 +08:00 - US-009
- Files changed: `zsim/sim_progress/Update/UpdateAnomaly.py`, `tests/simulator/test_update_anomaly_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `UpdateAnomaly.anomaly_effect_active(...)` now replaces open-coded same-index runtime-dot `end(...)`, removal, and append with `DotRuntimeStateAdapter.replace_by_index(...)` after `spawn_anomaly_dot(...)` returns a new dot.
  - `remove_dots_cause_disorder(...)` now replaces open-coded selected runtime-dot removal with `DotRuntimeStateAdapter.remove_all(...)` while keeping freeze follow-up scheduled publish and dot dynamic-state mutations caller-owned.
  - `tests/simulator/test_update_anomaly_dispatch.py` now records helper calls for replacement and freeze / non-freeze removal, so focused tests cover both helper use and the old behavior ordering.
- Compatibility retained:
  - `buff_add_strategy(...)` remains the existing same-tick Debuff write path; scheduled follow-up payloads remain on `ScheduleDispatchPort`; listener broadcast, `RuntimeCommandPort`, old containers, `BuffRuntimeReadPort` write boundaries, `CalAnomaly`, anomaly formulas, `LoadDamageEvent`, and `Update_Buff.update_dot()` remain unchanged.
  - Old paths still retained in this iteration: `Shock.DotFeature.__post_init__()`, `LoadDamageEvent`, `Update_Buff.update_dot()`, Alice dot listener callsites, and final P2-E source guardrails / handoff docs are left for later stories.
- Next step:
  - Continue with US-010 by deciding whether Shock duration initialization needs an explicit read helper, backed by the existing duration parity tests and without touching scheduled publish, runtime writes, dynamic dot registration, Calculator, or CalAnomaly.
---
## 2026-06-09 04:17 +08:00 - US-010
- Files changed: `zsim/sim_progress/Dot/initialization.py`, `zsim/sim_progress/Dot/Dots/Shock.py`, `tests/simulator/test_dot_runtime_initialization.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `DotInitializationReadContext` replaces the open-coded `Shock.DotFeature.__post_init__()` reads of `sim_instance.init_data.name_box` and `sim_instance.load_data.exist_buff_dict` with an explicit Shock dot initialization read boundary.
  - `Shock.DotFeature.__post_init__()` now uses the helper for Rina passive presence while retaining the same `ValueError`, name-box / exist-buff reference exposure, and `600` / `780` duration decisions.
  - `tests/simulator/test_dot_runtime_initialization.py` now proves helper parity and scans the migrated method plus helper for scheduled publish, listener broadcast, runtime command, `BuffRuntimeReadPort`, Calculator, CalAnomaly, and runtime dot-list leaks.
- Compatibility retained:
  - Scheduled publish remains on `ScheduleDispatchPort`; runtime dot registration / removal stays with `DotRuntimeStateAdapter` callsites; Buff / Debuff writes remain on existing `buff_add_strategy(...)` / facade paths; listener broadcast, `RuntimeCommandPort`, Calculator, and CalAnomaly formulas remain unchanged.
  - Old compatibility retained in this iteration: `Shock.DotFeature.__post_init__()` still depends on the existing Rina buff container when `丽娜` is present, and no old containers are deleted.
- Next step:
  - Continue with US-011 by adding exact-file P2-E guardrails for migrated Vivian, UpdateAnomaly, Shock initialization, and validation wiring without broadening into P2-F / P2-G candidates.
---
## 2026-06-09 04:28 +08:00 - US-011
- Files changed: `tests/simulator/test_migrated_p2e_dot_runtime_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_p2e_dot_runtime_guardrail.py` replaces manual migrated P2-E source scans with an exact-file AST guardrail for Vivian dot gates, `UpdateAnomaly` dot replacement / removal, `DotRuntimeStateAdapter`, `DotInitializationReadContext`, and `Shock.DotFeature`.
  - `scripts/run_buff_refactor_validation.py` now includes the P2-E source guardrail in the `implicit-events` focused pytest and scoped mypy profiles.
  - This story builds guardrail coverage and profile wiring only; it does not replace additional live production behavior.
- Compatibility retained:
  - Vivian dot `skill_node_data` and freeze `_dot.anomaly_data` remain the documented scheduled follow-up payloads; dot registration / replacement / removal remains runtime state and is not converted into scheduled backlog.
  - `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, listener broadcast, `buff_add_strategy(...)`, old containers, `LoadDamageEvent`, `Update_Buff.update_dot()`, Alice dot listener retained paths, Calculator, and CalAnomaly formulas remain unchanged.
  - No new old-coupling review update was needed; root source evidence found no new coupling beyond the guarded migrated P2-E file set.
- Next step:
  - Continue with US-012 by recording the serial validation summary and behavior-sample decision without broadening into P2-F / P2-G candidates or final handoff docs.
---
## 2026-06-09 04:33 +08:00 - US-012
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This validation / decision story does not replace additional live production behavior; it records the serial P2-E `implicit-events` validation result and behavior-sample skip rationale after `DotRuntimeStateAdapter`, `DotInitializationReadContext`, and exact-file P2-E guardrails are already in place.
  - The validation profile evidence prepares final handoff to replace manual release readiness review for P2-E dot runtime-state / initialization.
- Compatibility retained:
  - Scheduled follow-up publish remains on `ScheduleDispatchPort`; dot registration / replacement / removal remains runtime state; Buff / Debuff writes remain on existing `buff_add_strategy(...)` / facade paths.
  - `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, listener broadcast, old containers, `LoadDamageEvent`, `Update_Buff.update_dot()`, Alice dot listener retained paths, Calculator, and CalAnomaly formulas remain unchanged.
  - No main-loop consistency sample was run because no live duration / tick / runtime semantic change was introduced in this story; focused parity tests and source guardrails remain the compatibility evidence.
- Next step:
  - Continue with US-013 final handoff docs, marking P2-E state and promoting the next same-phase pool item without collapsing the candidate pool.
---
## 2026-06-09 04:42 +08:00 - US-013
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - Final P2-E handoff docs now replace stale “P2-E is next” planning with completed guarded-scope evidence for `DotRuntimeStateAdapter`, `DotInitializationReadContext`, Vivian dot gates, `UpdateAnomaly` dot replacement / removal, Shock duration initialization, exact-file P2-E guardrails, and serial `implicit-events` validation.
  - The next default same-phase PRD is promoted to P2-F BuffAddStrategy caller / facade-write design while retaining P2-G direct simulator context helpers, P2-D / P2-E guarded maintenance, phase-3 formula snapshots, retained compatibility, and blocker-only phase-1 reopen rows.
- Compatibility retained:
  - Scheduled follow-up publish remains on `ScheduleDispatchPort`; runtime dot registration / replacement / removal remains runtime state; Buff / Debuff writes remain on existing `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` paths.
  - `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, listener broadcast, old containers, `LoadDamageEvent`, `Update_Buff.update_dot()`, Alice dot listener retained paths, Calculator, and CalAnomaly formulas remain unchanged.
  - No new old-coupling review update was needed; this handoff story found no new coupling beyond the guarded P2-E file set and retained P2-F / P2-G candidates.
- Next step:
  - Generate the next phase-2 PRD from [Buff重构方案.md](./Buff重构方案.md), defaulting to P2-F BuffAddStrategy caller / facade-write design while preserving the broader same-phase pool.
---
## 2026-06-09 11:26 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This planning / taxonomy story does not replace live production behavior; it replaces ad hoc P2-F scoping with a root-workspace caller taxonomy for `buff_add_strategy(...)` and a working-note boundary for later focused tests and guardrails.
  - The taxonomy prepares focused P2-F tests to replace manual review of forced same-tick Buff / Debuff write callers in BuffXLogic, BattleEventListener, Character managers, and `UpdateAnomaly.anomaly_effect_active(...)`.
- Compatibility retained:
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary; active-store replacement, enemy debuff mirror sync, registry/template identity, and no pending queue writes remain retained compatibility.
  - `ScheduleDispatchPort`, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, P2-A / P2-B / P2-C / P2-D / P2-E guarded buckets, old containers, Calculator / CalAnomaly formulas, direct simulator context helpers, and legacy `buff_add()` / `KickOutBuff()` deletion all remain out of scope.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F coupling.
- Next step:
  - Continue with US-002 by locking active-store replacement and enemy mirror facade behavior in focused tests without broadening into caller-family coverage or production behavior edits unless a documented contract mismatch appears.
---
## 2026-06-09 11:45 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_add_strategy_runtime_facade.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buff_add_strategy_runtime_facade.py` now replaces manual review of the core `buff_add_strategy(...)` active-store contract with recording-facade assertions for `find_active_buff_by_index(...)`, `remove_active_buff(...)`, `append_active_buff(...)`, and `sync_enemy_debuff_mirror(...)`.
  - The focused tests now prove active replacement removes only the matching old Buff index for the target beneficiary and that enemy mirror sync uses the same runtime object appended through the active-store path.
  - This story locks the existing boundary with tests only; it does not replace live production behavior.
- Compatibility retained:
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - `LOADING_BUFF_DICT` pending queues, `ScheduleDispatchPort` scheduled backlog, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F active-store / enemy mirror coupling.
- Next step:
  - Continue with US-003 by locking beneficiary selection, explicit target override, template identity, and `specified_count` behavior without broadening into caller-family coverage or production behavior edits unless a documented contract mismatch appears.
---
## 2026-06-09 12:01 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_add_strategy_runtime_facade.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buff_add_strategy_runtime_facade.py` now replaces manual review of `confirm_selected_character(...)` target fan-out and explicit `benifit_list` override behavior with focused facade-backed tests.
  - The focused tests now prove per-beneficiary `exist_buff_dict` template writeback through `simple_start(...)`, copied runtime Buff identity, `specified_count` propagation, and untouched pending queues for automatic fan-out and explicit target override paths.
  - This story locks the existing boundary with tests only; it does not replace live production behavior.
- Compatibility retained:
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary, with target selection still flowing through `confirm_selected_character(...)` and runtime writes through `let_buff_start(...)`.
  - `LOADING_BUFF_DICT` pending queues, `ScheduleDispatchPort` scheduled backlog, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F target-selection and template-identity coupling.
- Next step:
  - Continue with US-004 by adding Hugo Totalize caller coverage without broadening into Roaring Ride, Seed, listener, or Character manager caller families.
---
## 2026-06-09 12:15 +08:00 - US-004
- Files changed: `tests/simulator/test_hugo_totalize_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_hugo_totalize_dispatch.py` now replaces manual Hugo Totalize caller review with focused tests for `buff_add_strategy(...)` call order, exact arguments, branch/no-op gating, and scheduled publish ordering.
  - The focused tests now guard Hugo forced-write branches against raw pending queue writes, listener broadcast, `RuntimeCommandPort` creation, and `BuffRuntimeReadPort` write APIs.
  - This story locks existing behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - Hugo formulas, totalize ratios, thresholds, scheduled payload fields, `LoadingMission.mission_start(...)` before dispatch publish, and optional stun termination publish timing remain unchanged.
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - `LOADING_BUFF_DICT` pending queues, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F Hugo caller coupling.
- Next step:
  - Continue with US-005 by adding Roaring Ride caller coverage without broadening into Seed, listener, or Character manager caller families.
---
## 2026-06-09 12:28 +08:00 - US-005
- Files changed: `tests/simulator/test_buffaddstrategy_roaring_ride_callers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buffaddstrategy_roaring_ride_callers.py` now replaces manual Roaring Ride caller review with focused tests for RNG branch boundaries, exact `buff_add_strategy(...)` arguments, `sim_instance` forwarding, and caller-layer boundary guards.
  - This story locks existing behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - Roaring Ride source, refinement-derived Buff index strings, RNG thresholds, and `simple_start(find_tick(...), record.sub_exist_buff_dict)` state/count behavior remain unchanged.
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - `LOADING_BUFF_DICT` pending queues, scheduled publish, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F Roaring Ride caller coupling.
- Next step:
  - Continue with US-006 by adding Seed BuffXLogic caller-family coverage without broadening into listener or Character manager caller families.
---
## 2026-06-09 12:41 +08:00 - US-006
- Files changed: `tests/simulator/test_buffaddstrategy_seed_callers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buffaddstrategy_seed_callers.py` now replaces manual Seed BuffXLogic caller review with focused tests for besiege-state `benifit_list` derivation, direct vanguard target forwarding, branch/no-op gating, exact `buff_add_strategy(...)` arguments, and caller-layer boundary guards.
  - This story locks existing Seed caller behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - Seed source files, record classes, trigger gates, `besiege_active_check(...)`, `direct_strike_active`, benefit-list construction, and absence of `specified_count` forwarding remain unchanged.
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - `LOADING_BUFF_DICT` pending queues, scheduled publish, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F Seed caller coupling.
- Next step:
  - Continue with US-007 by adding `UpdateAnomaly.anomaly_effect_active(...)` debuff activation coverage while keeping dot runtime-state replacement on the P2-E path.
---
## 2026-06-09 12:55 +08:00 - US-007
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_update_anomaly_dispatch.py` now replaces manual `UpdateAnomaly.anomaly_effect_active(...)` debuff/dot boundary review with focused tests for debuff `buff_add_strategy(...)` calls, dot runtime-state replacement, and caller-layer guardrails.
  - This story locks existing `UpdateAnomaly` behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - `anomaly_effect_active(...)` source, anomaly formulas, dot duration initialization, dot replacement semantics, and scheduled anomaly publish behavior remain unchanged.
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary for `bar.accompany_debuff`.
  - `DotRuntimeStateAdapter.replace_by_index(...)` remains the P2-E dot runtime-state path for `bar.accompany_dot`.
  - `LOADING_BUFF_DICT` pending queues, scheduled publish, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F `UpdateAnomaly` caller coupling.
- Next step:
  - Continue with US-008 by adding BattleEventListener caller focused coverage without broadening into Character manager callers or cross-layer source guardrail wiring.
---
## 2026-06-09 13:09 +08:00 - US-008
- Files changed: `tests/simulator/test_buffaddstrategy_listener_callers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_buffaddstrategy_listener_callers.py` now replaces manual BattleEventListener `buff_add_strategy(...)` caller review with focused tests for enemy-target forwarding, explicit target forwarding, repeated same-index writes, valid no-op gating, exact arguments, `sim_instance` forwarding, and caller-layer guardrails.
  - This story locks existing BattleEventListener caller behavior with tests only; it does not replace live production behavior.
- Compatibility retained:
  - BattleEventListener source files, synchronous listener activation, signal/type gates, target lists, Practiced Perfection repeated-write ordering, and the `LBS.ASSAULT_SPAWN` no-op forced-write branch remain unchanged.
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary for listener callers.
  - `LOADING_BUFF_DICT` pending queues, scheduled publish, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; root-workspace evidence matched already documented P2-F BattleEventListener caller coupling.
- Next step:
  - Continue with US-009 by adding Character manager caller focused coverage without broadening into P2-G direct simulator context helpers or source guardrail wiring.
---
## 2026-06-09 14:19 +08:00 - US-012
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `scripts/ralph/progress.txt` now replaces ad-hoc P2-F release-readiness review with a serial validation record, uncovered focused caller command evidence, and an explicit behavior-sample decision.
  - This story builds validation and handoff evidence only; it does not replace live production behavior.
- Compatibility retained:
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort` read-only semantics, pending queues, active-store replacement, enemy mirror sync, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No live APL / team behavior sample was run because this iteration made no production behavior changes and the required evidence is test-only caller / guardrail coverage plus serial validation.
  - No new old-coupling review update was needed; this story did not discover new Buff coupling.
- Next step:
  - Continue with US-013 by updating final P2-F handoff docs and the next candidate pool without claiming production behavior deletion or broad phase migration.
---
## 2026-06-09 14:33 +08:00 - US-013
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - Final P2-F handoff docs now replace ad-hoc next-PRD routing with documented guarded-complete evidence for caller taxonomy, focused tests, guardrail wiring, serial validation, and retained same-tick write boundaries.
  - The next-candidate pool now prepares P2-G direct simulator context helper work to replace manual service-location review with service-specific focused tests and explicit helper design.
- Compatibility retained:
  - `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remains the forced same-tick Buff / Debuff write boundary.
  - Old containers, legacy `buff_add()` / `KickOutBuff()`, Calculator / CalAnomaly formulas, `ScheduleDispatchPort` scheduled queue publish, synchronous listener broadcast, `RuntimeCommandPort`, and `BuffRuntimeReadPort` read-only semantics all remain unchanged.
  - No new old-coupling review update was needed; this story changed handoff docs and Ralph artifacts only and did not discover new or materially changed Buff coupling.
- Next step:
  - Generate the next phase-2 PRD from [Buff重构方案.md](./Buff重构方案.md), defaulting to P2-G direct simulator context helpers while preserving P2-D / P2-E / P2-F guarded maintenance, phase-3 formula snapshot replacement, retained compatibility, and blocker-only phase-1 reopen rows.
---
## 2026-06-09 15:13 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `scripts/ralph/progress.txt` now replaces ad-hoc P2-G service-location intake with documented root `rg` counts, CodeGraph representative inspection, service taxonomy, selected focused-test representatives, and rejected thin slices.
  - This story builds boundary taxonomy only; it does not replace live production behavior.
- Compatibility retained:
  - `sim_instance.tick`, local preload / Character action context, `char_data.find_next_char_obj(...)`, `schedule_data.enemy`, `listener_manager`, `rng_instance`, and `schedule_data.change_process_state()` remain unchanged.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort` read-only semantics, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - P2-A / P2-B / P2-C / P2-D / P2-E / P2-F completed buckets are retained as guarded maintenance evidence and are not reopened by this taxonomy story.
  - No new old-coupling review update was needed; root-workspace evidence matched the existing direct simulator context candidate pool.
- Next step:
  - Continue with US-002 by adding Yuzuha Hard Candy tick / preload branch coverage without broadening into RNG, listener, scheduled publish, runtime write, or formula replacement work.
---
## 2026-06-09 15:28 +08:00 - US-002
- Files changed: `tests/simulator/test_yuzuha_direct_context_helpers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_yuzuha_direct_context_helpers.py` now replaces manual `YuzuhaHardCandyShotTrigger` tick / preload branch review with focused coverage for the allowed local action path, preload-occupied no-op, cooldown no-op, resource read, `simple_start(...)` tick forwarding, and `spawn_hard_candy_shot(...)` signal forwarding.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `YuzuhaHardCandyShotTrigger.py` source, `sim_instance.tick`, `preload.preload_data.char_occupied_check(...)`, Yuzuha resource reads, cooldown math, `simple_start(...)`, and local Character action invocation remain unchanged.
  - `Character/Yuzuha.spawn_hard_candy_shot(...)` and `schedule_preload_event_factory(...)` remain separate scheduled-preload publish behavior and are not migrated by this story.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort` read-only semantics, raw pending queues, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidate.
- Next step:
  - Continue with US-003 by adding Yuzuha Cinema4 quick-assist next-character coverage without broadening into RNG, listener, runtime write, scheduled publish migration, or formula replacement work.
---
## 2026-06-09 15:54 +08:00 - US-003
- Files changed: `tests/simulator/test_yuzuha_direct_context_helpers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_yuzuha_direct_context_helpers.py` now replaces manual `YuzuhaCinema4QuickAssistTrigger` quick-assist / next-character review with focused coverage for allowed last-hit activation, `quick_assist_system` lookup, `find_next_char_obj(char_now=1411, direction=1)`, `tick_now=sim_instance.tick` forwarding, report-state behavior, and no-op last-hit gating.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `YuzuhaCinema4QuickAssistTrigger.py` source, allowed skill tags, last-hit gating, quick-assist activation, next-character lookup, report printing, and `record.trigger_skill_node` reset remain unchanged.
  - `schedule_data.change_process_state()` remains report-state / process-state behavior and is not treated as scheduled payload publication, listener broadcast, runtime write, or raw queue mutation.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort` read-only semantics, raw pending queues, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidate.
- Next step:
  - Continue with US-004 by adding Yuzuha Cinema6 Sheel preload / report-state coverage without broadening into RNG, listener, runtime write, scheduled publish migration, or formula replacement work.
---
## 2026-06-09 16:44 +08:00 - US-004
- Files changed: `tests/simulator/test_yuzuha_direct_context_helpers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_yuzuha_direct_context_helpers.py` now replaces manual `YuzuhaCinema6SheelTrigger` preload / report-state review with focused coverage for current-tick `SchedulePreload` publish, `sim_instance.preload.preload_data` forwarding, charge-gate no-op behavior, `YUZUHA_REPORT` process-state ordering, and raw queue / listener / runtime separation.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `YuzuhaCinema6SheelTrigger.py` source, allowed skill tag, charge-duration gate, Yuzuha resource gate, `schedule_preload_event_factory(...)`, `SchedulePreload` payload fields, counter reset/update behavior, report printing, and `schedule_data.change_process_state()` remain unchanged.
  - Factory-backed scheduled preload publication remains a `ScheduleDispatchPort` / `create_schedule_dispatch_port(...)` responsibility inside `schedule_preload_event_factory(...)`; report-state `change_process_state()` remains separate from scheduled payload publication, listener broadcast, same-tick runtime write, and raw queue mutation.
  - `tests/simulator/test_yuzuha_cinema6_energy_dispatch.py` still covers existing Character/Yuzuha cinema-6 team energy fan-out behavior and file-specific target ordering.
  - `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, listener broadcast, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context / factory-backed `SchedulePreload` candidate.
- Next step:
  - Continue with US-005 by selecting Yuzuha tick-only / report-state representatives without broadening into RNG, listener, runtime write, scheduled publish migration, or formula replacement work.
---
## 2026-06-09 16:58 +08:00 - US-005
- Files changed: `tests/simulator/test_yuzuha_direct_context_helpers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_yuzuha_direct_context_helpers.py` now replaces manual `YuzuhaCinema2Trigger` and `YuzuhaSugarBurstAnomalyBuildupBonus` tick/report-state review with focused coverage for report-state QTE mutation, cooldown no-op behavior, tick-only preload match, preload-tick mismatch, and dispatch/listener/runtime/raw-queue separation.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `YuzuhaCinema2Trigger.py` source, allowed skill tags, enemy stun gate, cooldown math, last-hit gating, QTE flag mutation, report printing, and `schedule_data.change_process_state()` remain unchanged.
  - `YuzuhaSugarBurstAnomalyBuildupBonus.py` source, `preload_tick == sim_instance.tick` gating, `simple_start(timenow=sim_instance.tick, no_count=1)`, count calculation, and `update_to_buff_0(...)` remain unchanged.
  - `YuzuhaTanukiWishAtkBonus.py` and `YuzuhaSugarBurstMaxAnomalyBuildupBonus.py` remain retained candidates; this iteration records why they were not selected instead of duplicating branch-equivalent coverage.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, raw pending queues, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-006 by adding enemy-context representative coverage without broadening into formula replacement, listener/RNG helper extraction, scheduled publish migration, or same-tick runtime write changes.
---
## 2026-06-09 17:10 +08:00 - US-006
- Files changed: `tests/simulator/test_enemy_context_direct_helpers.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_enemy_context_direct_helpers.py` now replaces manual `YixuanAdditionalAbilityDmgBonus` enemy-stun branch review with focused coverage for the positive stunned-enemy path, the no-stun no-op path, direct `schedule_data.enemy.dynamic.stun` reads, old-container lookup blocking, and dispatch/listener/runtime/raw-queue separation.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `YixuanAdditionalAbilityDmgBonus.py` source, enemy stun gate, matching `1371_E_EX_B_` skill-tag gate, optional report-state guard, and return semantics remain unchanged.
  - `AlicePolarizedAssaultTrigger.py` remains a retained mixed enemy-context / scheduled-publish contrast; its existing dispatch-port coverage is not migrated or widened by this story.
  - Broader enemy/debuff fact-source consolidation, anomaly formulas, dot runtime registration, `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, raw pending queues, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-007 by adding listener-manager representative coverage without broadening into RNG helper extraction, scheduled publish migration, formula replacement, or same-tick runtime write changes.
---
## 2026-06-09 17:22 +08:00 - US-007
- Files changed: `tests/simulator/test_listener_manager_direct_context.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_listener_manager_direct_context.py` now replaces manual `HeartstringNocturne` listener lookup review with focused coverage for active-signal listener lookup, cached listener reuse, no-op mismatch behavior, and dispatch/runtime/report/raw-queue separation.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `HeartstringNocturne.py` source, `listener_manager.get_listener(...)`, `record.listener_exist`, active-signal matching, `SkillNode` no-op gates, and return semantics remain unchanged.
  - `CinderCobaltAtkBonus.py`, `HormonePunkAtkBonus.py`, and `ZanshinHerbCase.py` remain retained same-family listener lookup candidates; this iteration does not duplicate branch-equivalent coverage.
  - `listener_manager.get_listener(...)` remains direct listener context lookup, while `listener_manager.broadcast_event()` remains synchronous listener broadcast. Neither is converted into scheduled queue publish, report-state mutation, raw queue mutation, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, or `BuffRuntimeReadPort` work.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-008 by adding RNG-service representative coverage without broadening into listener helper extraction, scheduled publish migration, formula replacement, or same-tick runtime write changes.
---
## 2026-06-09 17:35 +08:00 - US-008
- Files changed: `tests/simulator/test_full_crit_event_adjacent_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_full_crit_event_adjacent_reader.py` now replaces manual RNG-service boundary review for `CannonRotor.special_judge_logic()` and the Woodpecker full-crit RNG gates with deterministic fake RNG assertions plus fail-fast runtime / queue / listener guards.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `CannonRotor.py`, `WoodpeckerElectroSet4_NA.py`, `WoodpeckerElectroSet4_E_EX.py`, `WoodpeckerElectroSet4_CA.py`, and `RoaringRideBuffTrigger.py` source remain unchanged.
  - Cannon Rotor and Woodpecker RNG threshold semantics, full-crit received-bonus semantics, reader-before-RNG order, and no-publish judge behavior remain unchanged.
  - Roaring Ride remains the existing P2-F forced Buff write path through `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade`; this story does not broaden that write boundary.
  - Cannon Rotor `special_hit_logic()` remains the existing P2-D scheduled-publish path through `ScheduleDispatchPort`; this story does not migrate or retest its publish ordering beyond retained guard evidence.
  - `RuntimeCommandPort`, listener broadcast, report-state mutation, raw `event_list` mutation, old-container deletion boundaries, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-009 by adding report-state representative coverage without broadening into RNG helper extraction, listener migration, scheduled publish migration, formula replacement, or same-tick runtime write changes.
---
## 2026-06-09 17:47 +08:00 - US-009
- Files changed: `tests/simulator/test_report_state_direct_context.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_report_state_direct_context.py` now replaces manual `AstraYaoCorePassiveAtkBonus.special_start_logic()` report-state review with focused coverage for positive buff-update/report ordering, same-tick no-op gating, and dispatch/listener/runtime/raw-queue/deletion separation.
  - This story adds branch and boundary evidence only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - `AstraYaoCorePassiveAtkBonus.py` source, `simple_start(...)`, `update_to_buff_0(...)`, `record.update_info_box` same-tick guard, report printing, and `schedule_data.change_process_state()` remain unchanged.
  - `schedule_data.change_process_state()` remains report-state / process-state behavior and is not treated as scheduled payload publication, listener broadcast, runtime immediate write, raw queue mutation, or old-container deletion.
  - `AstraYaoChordManagerTrigger.py`, `HugoCorePassive*`, `SeedAdditionalAbilityTrigger.py`, `SeedCinema6Trigger.py`, `Vivian*`, `Yixuan*`, and already-covered Yuzuha report-state files remain retained candidates or completed contrast evidence; this iteration does not duplicate those branches.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, raw pending queues, old containers, Calculator / CalAnomaly formulas, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-010 by deciding explicit context helpers and retained compatibility boundaries without introducing a universal simulator context object or collapsing report-state, listener, scheduled publish, RNG, and runtime-write semantics.
---
## 2026-06-09 17:56 +08:00 - US-010
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This story records the P2-G helper decision only; it does not replace live production behavior or extract a new helper.
  - The existing P2-G focused tests now replace manual helper-design confidence for the covered service families: Yuzuha tick/preload/next-character/report-state branches, enemy context, listener lookup, RNG service, and report-state process changes.
- Compatibility retained:
  - Tick gate, local preload, next-character lookup, enemy context, listener lookup, RNG service, report-state change, scheduled publish, and same-tick runtime write remain separate boundaries.
  - No universal simulator context object was introduced, and direct context reads were not routed through `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, or `BuffRuntimeReadPort`.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, raw pending queues, old containers, Calculator / CalAnomaly formulas, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-011 by adding exact-file or selected-service-family P2-G source guardrails and validation wiring without broadening into P2-A / P2-B / P2-C / P2-D / P2-E / P2-F guarded buckets, phase-3 formula work, or old-container deletion.
---
## 2026-06-09 18:10 +08:00 - US-011
- Files changed: `tests/simulator/test_migrated_p2g_direct_context_guardrail.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `tests/simulator/test_migrated_p2g_direct_context_guardrail.py` now replaces manual source-review confidence for completed P2-G direct simulator context services with an exact root file / selected-symbol AST guardrail.
  - The new `MIGRATED_P2G_DIRECT_CONTEXT_GUARDRAIL_FOCUSED_TEST_TARGETS` validation bucket wires that guardrail into the `implicit-events` focused pytest and mypy profile.
  - This story adds validation guardrails only; it does not replace live production behavior or extract a new helper.
- Compatibility retained:
  - P2-G tick/preload/next-character, enemy context, listener lookup, RNG service, report-state, and factory-backed scheduled preload behavior remain unchanged.
  - `CannonRotor.special_hit_logic()` and other completed P2-D scheduled-publish paths remain retained; the P2-G guardrail targets `CannonRotor.special_judge_logic()` for RNG-service regression only.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, raw pending queues, old containers, Calculator / CalAnomaly formulas, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No new old-coupling review update was needed; this story found no new Buff coupling beyond the already documented P2-G direct simulator context candidates.
- Next step:
  - Continue with US-012 by running serial validation and updating final handoff docs without adding more P2-G implementation scope unless validation or doc evidence exposes a real gap.
---
## 2026-06-09 18:21 +08:00 - US-012
- Files changed: `docs/Buff重构替换说明.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - Final P2-G handoff docs now replace the previous "P2-G is the current default next PRD" state with completed direct-context evidence, serial validation results, and a phase-2 closure / phase-3 readiness next default.
  - This story adds validation and handoff evidence only; it does not replace live production behavior or extract a new simulator context helper.
- Compatibility retained:
  - P2-G tick / preload / next-character, enemy context, listener lookup, RNG service, report-state, factory-backed scheduled preload, and covered forced-write / scheduled-publish contrast behavior remain unchanged.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, raw pending queues, old containers, Calculator / CalAnomaly formulas, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - `docs/旧Buff系统耦合审查结果.md` was not changed because this final validation found no new direct-context coupling beyond the already documented P2-G candidates.
- Next step:
  - Generate the next PRD as a phase-2 closure / phase-3 formula snapshot readiness decision following `docs/Buff重构方案.md`; keep P2-A through P2-G as guarded maintenance buckets and reopen phase-1 only for concrete guardrail / validation failures.
---
## 2026-06-09 18:59 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This story reconfirms the phase-2 closure / phase-3 formula snapshot readiness boundary; it does not replace live production behavior, calculator formulas, anomaly formulas, or BuffXLogic runtime paths.
  - The current PRD readiness gate replaces manual uncertainty about whether P2-A through P2-G should be reopened by recording doc evidence that they are completed or guarded-maintenance buckets.
- Compatibility retained:
  - P2-A through P2-G implementation buckets, scheduled publish, listener broadcast, same-tick runtime writes, old containers, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, Calculator / CalAnomaly formulas, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this story found no new Buff coupling.
- Next step:
  - Continue with the formula snapshot readiness stories by auditing current guardrail evidence and validation gaps before any phase-3 formula replacement work.
---
## 2026-06-09 19:10 +08:00 - US-002
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - This story builds the root-workspace formula snapshot census and phase-3 readiness buckets; it does not replace a live production path.
  - The new matrix section replaces manual uncertainty about current formula snapshot scope with reproducible scans for `Calculator`, `CalAnomaly`, `MultiplierData`, `MulData`, `current_ndarray`, `DynamicStatement`, and the named Calculator helper terms.
- Compatibility retained:
  - `zsim/sim_progress/ScheduledEvent/Calculator.py` and `zsim/sim_progress/ScheduledEvent/CalAnomaly.py` formula behavior remain unchanged.
  - `.codex_worktrees/**`, generated logs, `__pycache__/**`, and `scripts/ralph/archive/**` remain excluded from blocker conclusions.
  - P2-A through P2-G guarded buckets, scheduled publish, listener broadcast, same-tick runtime writes, old containers, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this story found no new Buff coupling beyond already documented formula snapshot retained boundaries.
- Next step:
  - Continue with US-003 by auditing P2-A through P2-G guardrail evidence and validation gaps before any phase-3 formula replacement work.
---
## 2026-06-09 19:18 +08:00 - US-003
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - The new P2-A through P2-G closure matrix replaces manual cross-reading of prior completion notes with a single guardrail / validation / retained-boundary / blocker-only reopen table.
  - This story adds audit and handoff evidence only; it does not replace live production behavior, Calculator formulas, CalAnomaly formulas, dispatch adapters, same-tick runtime writes, dot runtime state, or direct simulator service helpers.
- Compatibility retained:
  - P2-A through P2-G migrated buckets remain completed guarded-maintenance scope; no guardrail scan set was broadened.
  - P2-D scheduled publish, P2-E dot runtime-state, P2-F same-tick facade writes, and P2-G direct simulator services remain separate boundary families.
  - `ScheduleDispatchPort`, synchronous listener broadcast, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, old containers, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this audit found no new Buff coupling beyond already documented P2-A through P2-G retained boundaries.
- Next step:
  - Continue with US-004 by auditing validation profile wiring and formula-readiness gaps before defining any phase-3 formula parity or replacement suite.
---
## 2026-06-09 19:27 +08:00 - US-004
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new validation-profile / formula-readiness audit section replaces manual interpretation of `run_buff_refactor_validation.py` profile wiring with a documented profile matrix, existing focused-test coverage map, and formula parity gap list.
  - This story adds audit and handoff evidence only; it does not wire a new validation profile or replace live Calculator / CalAnomaly formula behavior.
- Compatibility retained:
  - `implicit-events`, `calculator-reads`, and default `lifecycle` validation semantics remain unchanged.
  - P2-A through P2-G guarded-maintenance buckets, scheduled publish, listener broadcast, same-tick runtime writes, dot runtime state, direct simulator services, old containers, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this audit found no new Buff coupling beyond already documented retained formula snapshot and guarded-maintenance boundaries.
- Next step:
  - Continue with US-005 by defining the formula parity suite contract before any Calculator / CalAnomaly formula replacement or validation-profile wiring.
---
## 2026-06-09 19:47 +08:00 - US-005
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new formula parity suite contract replaces manual phase-3 parity ambiguity with named input domains, output invariants, comparison policy, and focused-vs-registered-sample rules.
  - This story adds contract documentation only; it does not replace live Calculator / CalAnomaly formula behavior or wire a new validation profile.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `MultiplierData`, `MulData`, `DynamicStatement`, and current `CalculatorBuffAttributeReader` helper seams all remain unchanged.
  - P2-A through P2-G guarded-maintenance buckets, scheduled publish, listener broadcast, same-tick runtime writes, dot runtime state, direct simulator services, old containers, formula snapshots, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this contract found no new Buff coupling beyond already documented retained formula snapshot boundaries.
- Next step:
  - Continue with US-006 by characterizing `MultiplierData` and `DynamicStatement` snapshot behavior under this parity contract before any phase-3 formula replacement or validation-profile wiring.
---
## 2026-06-09 19:49 +08:00 - US-006
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot` prepares to replace manual review of `MultiplierData.get_buff_bonus(...)` fan-in and `DynamicStatement` translated fields with focused characterization coverage.
  - This story characterizes retained snapshot behavior only; it does not replace a live production path, Calculator formula, CalAnomaly formula, or validation profile.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `MultiplierData`, `MultiplierData.mul_data_cache`, `_calculate_dynamic_statement(...)`, `DynamicStatement`, `cal_buff_total_bonus(...)`, and current `CalculatorBuffAttributeReader` helper seams all remain unchanged.
  - Active Buff view aggregation, enemy debuff aggregation, old containers, formula snapshots, scheduled publish, listener broadcast, same-tick runtime writes, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot boundaries.
- Next step:
  - Continue with US-007 by characterizing Calculator attribute formula boundaries while keeping reader seam evidence separate from full formula replacement.
---
## 2026-06-09 20:04 +08:00 - US-007
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_calculator_attribute_formula_boundaries_remain_retained_compatibility` prepares to replace manual review of Calculator attribute formula boundaries with focused coverage for `cal_am(...)`, `cal_ap(...)`, `cal_imp(...)`, `cal_crit_rate(...)`, `cal_personal_crit_rate(...)`, and `cal_personal_crit_dmg(...)`.
  - This story characterizes retained formula behavior only; it does not replace a live production path, Calculator formula, CalAnomaly formula, or validation profile.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `Calculator.AnomalyMul`, `Calculator.StunMul`, `Calculator.RegularMul`, `MultiplierData`, `DynamicStatement`, and current `CalculatorBuffAttributeReader` helper seams all remain unchanged.
  - Full crit rate still includes received crit; personal crit rate and personal crit damage still exclude received crit fields.
  - P2-A / P2-B reader helper tests remain compatibility evidence and migrated-file guardrails only; they are not treated as proof that Calculator formulas can be deleted.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot boundaries.
- Next step:
  - Continue with US-008 by characterizing CalAnomaly and AnomalyBar snapshot boundaries before any phase-3 formula replacement or validation-profile wiring.
---
## 2026-06-09 20:15 +08:00 - US-008
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility` prepares to replace manual review of `AnomalyBar.update_snap_shot(...)`, `anomaly_settled()`, and `NewAnomaly(...)` copied snapshot inputs with focused characterization coverage.
  - `test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios` prepares to replace manual review of `CalAnomaly.__init__()` snapshot / `MulData` inputs, `final_multipliers`, `scaling_factor`, and `CalAbloom.anomaly_dmg_ratio` with focused characterization coverage.
  - This story characterizes retained anomaly formula snapshot behavior only; it does not replace a live production path, CalAnomaly formula, AnomalyBar settlement formula, copied-output publish path, or validation profile.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `AnomalyBarClass.py`, `CopyAnomalyForOutput.py`, `MultiplierData` / `MulData`, Calculator multiplier helpers, `AnomalyBar.current_ndarray`, copied anomaly outputs, and current `calculator-reads` validation wiring all remain unchanged.
  - Scheduled publish, listener broadcast, dot runtime registration, same-tick runtime writes, old containers, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot boundaries.
- Next step:
  - Continue with US-009 by using the new CalAnomaly / AnomalyBar baseline as compatibility evidence while keeping phase-3 formula replacement gated behind explicit formula parity scope and validation decisions.
---
## 2026-06-09 20:28 +08:00 - US-009
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new copied anomaly / disorder output classification replaces manual ambiguity between formula snapshot data, copied payload construction, scheduled payload publication, listener broadcast, dot runtime registration, and same-tick runtime writes.
  - This story adds readiness documentation only; it does not replace a live production path, copied-output publisher, listener broadcast, dispatch adapter, dot runtime helper, runtime command boundary, Calculator formula, or CalAnomaly formula.
- Compatibility retained:
  - Old paths still retained in this iteration: `VivianCorePassiveTrigger.py`, `VivianCinema6Trigger.py`, `YanagiPolarityDisorderTrigger.py`, `AlicePolarizedAssaultTrigger.py`, `UpdateAnomaly.py`, `CopyAnomalyForOutput.py`, `ScheduleDispatchPort`, `spawn_output()`, `PolarityDisorder`, `DirgeOfDestinyAnomaly`, `PolarizedAssaultEvent`, `AnomalyBar.current_ndarray`, `MultiplierData` / `MulData`, and existing `implicit-events` validation wiring all remain unchanged.
  - Listener broadcast (`LBS.DISORDER_SPAWN`), dot runtime registration/removal, same-tick runtime writes, old containers, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, `BuffRuntimeReadPort`, and legacy `buff_add()` / `KickOutBuff()` deletion all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained copied-output, scheduled publish, listener, dot runtime, runtime write, and formula snapshot boundaries.
- Next step:
  - Continue with US-010 by classifying remaining XLogic formula-adjacent candidates while keeping copied-output dispatch paths as guarded-maintenance scope unless focused tests or validation name a regression.
---
## 2026-06-09 20:59 +08:00 - US-010
- Files changed: `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-010 matrix classification replaces manual remaining-candidate triage with helper-family buckets for AM/AP, impact, crit, anomaly ratio / copied output, enemy anomaly-state reads, and retained formula snapshots.
  - This story adds readiness documentation only; it does not replace a live production path, formula helper, dispatch adapter, runtime port, guardrail, or validation profile.
- Compatibility retained:
  - Old paths still retained in this iteration: all P2-A through P2-G migrated files remain guarded maintenance, and `BuffXLogic`, `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and deleted event-list discovery surfaces all remain unchanged.
  - No old-coupling review update was needed; this classification found no new Buff coupling beyond already documented formula snapshot, copied-output, enemy-state read, and guarded P2-A through P2-G boundaries.
- Next step:
  - Continue with US-011 by deciding behavior sample matrix and registered-team requirements before any phase-3 go / no-go or formula validation wiring.
---
## 2026-06-09 21:11 +08:00 - US-011
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-011 behavior-sample matrix replaces manual decisions about when to run `scripts/run_buff_main_loop_consistency.py` with explicit registered-team, live-route, and production-semantics requirements.
  - This story adds readiness documentation only; it does not replace a live production path, formula helper, dispatch adapter, runtime port, validation profile, or registered team fixture.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `implicit-events` validation wiring all remain unchanged.
  - Existing successful `莱特火属性队` and `席德大安比队` samples remain route-specific evidence only; no new main-loop sample was run for this doc-only story.
- Next step:
  - Continue with US-012 by deciding phase-3 go / no-go and whether validation wiring should remain `calculator-reads` + `implicit-events` or add a future formula-readiness profile.
---
## 2026-06-09 21:22 +08:00 - US-012
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-012 go / no-go record replaces ambiguous phase-3 readiness wording with an explicit No-Go for immediate production formula snapshot replacement and an explicit requirement to design formula parity before replacement.
  - This story adds readiness documentation only; it does not replace a live production path, validation profile, formula helper, dispatch adapter, runtime port, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this decision found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, and guarded P2-A through P2-G boundaries.
- Next step:
  - Continue with US-013 by updating handoff docs and the next candidate pool so future PRD generation keeps formula parity design, guarded maintenance, retained compatibility, rollback, and non-goals separate.
---
## 2026-06-09 21:34 +08:00 - US-013
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - The US-013 handoff update prepares to replace ambiguous “phase-3 readiness decision” planning with an explicit next PRD default for formula parity suite design / characterization.
  - This story updates planning and Ralph artifacts only; it does not replace a live production path, formula helper, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this handoff found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-014 by running the required serial validation and final Ralph handoff; the next PRD default after this readiness run remains phase-3 formula parity suite design / characterization, not production formula replacement.
---
## 2026-06-09 21:51 +08:00 - US-014
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-014 final validation evidence replaces provisional readiness handoff status with a closed serial-validation record for this PRD.
  - This story updates validation evidence and Ralph artifacts only; it does not replace a live production path, formula helper, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this validation / handoff story found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Generate the next PRD for phase-3 formula parity suite design / characterization under `docs/Buff重构方案.md`; production formula replacement remains No-Go until the parity suite, validation targets, behavior-sample conditions, rollback plan, and non-goals are explicit.
---
## 2026-06-09 23:36 +08:00 - US-001
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-001 scope reconfirmation replaces any ambiguity at the start of the new phase-3 PRD with an explicit No-Go for production formula replacement in this story.
  - This story adds scope and validation evidence only; it does not replace a live production path, formula helper, copied-output formula, dispatch adapter, runtime port, guardrail, validation profile, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this reconfirmation found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-002 by building the formula candidate and focused-test target inventory from root-workspace evidence while keeping production formula replacement No-Go.
---
## 2026-06-09 23:47 +08:00 - US-002
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/Buff公式候选与测试目标清单.md` prepares to replace broad ad hoc formula searches with a root-workspace candidate and focused-test inventory for Phase 3 parity-suite design.
  - This story builds an evidence boundary only; it does not replace a live production path, formula helper, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this inventory found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-003 by turning this inventory into focused formula parity fixtures before any production formula replacement.
---
## 2026-06-10 00:02 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-003 fixture harness prepares to replace ad hoc formula parity setup with focused helpers for `MultiplierData`, `DynamicStatement`, enemy dynamic fields, and settled anomaly snapshots.
  - This story builds deterministic test infrastructure only; it does not replace a live production path, formula helper, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only fixture work found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-004 by using the stabilized fixtures to characterize `MultiplierData` and `DynamicStatement` aggregation before any production formula replacement.
---
## 2026-06-10 00:12 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-004 characterization cases prepare to replace implicit `MultiplierData` / `DynamicStatement` aggregation assumptions with executable focused coverage for empty input, single buff, stacked buffs, and enemy debuffs.
  - This story adds formula parity evidence only; it does not replace a live production path, formula helper, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `_calculate_dynamic_statement()`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-005 by characterizing Calculator AM/AP/impact formula parity against the same retained snapshot boundary before any production formula replacement.
---
## 2026-06-10 00:22 +08:00 - US-005
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_calculator_am_ap_impact_formula_family_matches_reader_snapshot_parity()` prepares to replace ad hoc AM/AP/impact formula confidence with focused characterization across static-only, dynamic-flat, and field-buff reader-backed snapshots.
  - This story adds formula parity evidence only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `Calculator.AnomalyMul`, `Calculator.StunMul`, `MultiplierData`, `_CalculatorReadSnapshot`, `DynamicStatement`, `_calculate_dynamic_statement()`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded-maintenance buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-006 by characterizing Calculator crit formula families while keeping received-crit fields and reader seam evidence separate from any production formula replacement decision.
---
## 2026-06-10 00:32 +08:00 - US-006
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_calculator_regular_mul_crit_formula_families_preserve_received_boundaries()` prepares to replace ad hoc crit-formula confidence with focused characterization for `Calculator.RegularMul.cal_crit_rate(...)`, `cal_personal_crit_rate(...)`, and `cal_personal_crit_dmg(...)`.
  - This story adds formula parity evidence only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `Calculator.RegularMul`, `MultiplierData`, `_CalculatorReadSnapshot`, `DynamicStatement`, `_calculate_dynamic_statement()`, `CalculatorBuffAttributeReader`, P2-B migrated reader files, `CalAnomaly.py`, copied anomaly / disorder output paths, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - P2-B reader-seam tests remain guarded-maintenance evidence only; this story does not use migrated reader files as proof that retained Calculator formulas can be deleted.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-007 by characterizing `CalAnomaly` settled snapshot input contracts before any production formula replacement.
---
## 2026-06-10 00:41 +08:00 - US-007
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_cal_anomaly_rejects_unsettled_or_bad_snapshot_shape()` and the tightened `test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()` prepare to replace manual review of `CalAnomaly.__init__()` settled snapshot guards, `MulData` inputs, helper call order, virtual-level handling, ordered multipliers, and retained `cal_anomaly_dmg(...)` ratio inputs with focused characterization coverage.
  - This story adds formula parity evidence only; it does not replace a live production path, `CalAnomaly` formula, Calculator formula, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `CalAnomaly`, `CalAbloom`, `MulData`, `MultiplierData`, `Calculator.RegularMul`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-008 by characterizing `AnomalyBar` settlement and copied snapshot inputs while keeping production `CalAnomaly.py` and copied-output formula paths retained.
---
## 2026-06-10 00:49 +08:00 - US-008
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The tightened `test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility()` prepares to replace manual review of `AnomalyBar.update_snap_shot(...)`, `anomaly_settled()`, settled `current_ndarray` shape, copied ndarray aliasing, and `active_by` / `activate_by` override semantics with focused characterization coverage.
  - This story adds formula parity evidence only; it does not replace a live production path, `AnomalyBar` settlement formula, copied-output formula, `CalAnomaly` formula, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `AnomalyBarClass.py`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, `CalAnomaly.py`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied anomaly / disorder output paths, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-009 by using this `AnomalyBar` / copied snapshot baseline to characterize Vivian copied anomaly output parity without replacing production formula or publish paths.
---
## 2026-06-10 00:58 +08:00 - US-009
- Files changed: `tests/simulator/test_vivian_core_passive_trigger_dispatch.py`, `tests/simulator/test_vivian_cinema6_trigger_dispatch.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The Vivian focused dispatch tests prepare to replace manual review of `VivianCorePassiveTrigger.py` copied anomaly construction, AP-derived ratio inputs, on-demand dispatch adapter use, `VivianCinema6Trigger.py` pre-active feather/resource ordering, and copied payload publish timing with executable characterization coverage.
  - This story adds formula / dispatch parity evidence only; it does not replace a live production path, copied-output formula, Calculator formula, CalAnomaly formula, dispatch adapter, listener path, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `VivianCorePassiveTrigger.py`, `VivianCinema6Trigger.py`, `CopyAnomalyForOutput.py`, `AnomalyBarClass.py`, `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained copied-output, formula snapshot, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-010 by characterizing disorder and copied-output formula reads without reopening Vivian production triggers or scheduled dispatch infrastructure.
---
## 2026-06-10 01:11 +08:00 - US-010
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()` prepares to replace manual review of `CopyAnomalyForOutput.py` copied disorder / polarity-disorder payload semantics with focused characterization for snapshot independence, formula input fields, listener-facing fields, `remaining_tick()` inputs, and retained scheduled-event payload metadata.
  - The US-010 matrix entry classifies `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, `TimeweaverDisorderDmgMul.py`, Alice disorder listeners, and retained Vivian copied-output evidence by source, formula input, publish boundary, runtime side effect, and retained compatibility.
  - This story adds formula / boundary characterization evidence only; it does not replace a live production path, copied-output formula, Calculator formula, CalAnomaly formula, dispatch adapter, listener path, dot runtime helper, same-tick runtime write facade, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, `TimeweaverDisorderDmgMul.py`, Alice disorder listeners, Vivian copied-output triggers, `CalAnomaly.py`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - Listener broadcast, scheduled queue publish, dot runtime registration, and same-tick Buff runtime writes remain documented as separate retained layers; this story found no new Buff coupling beyond those already documented boundaries.
- Next step:
  - Continue with US-011 by characterizing enemy dynamic and debuff aggregation reads without turning copied-output or listener broadcast evidence into a production formula replacement.
---
## 2026-06-10 01:20 +08:00 - US-011
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_enemy_dynamic_debuff_reads_feed_old_and_reader_formula_snapshots()` prepares to replace manual review of enemy-side dynamic debuff aggregation with focused characterization for empty enemy state, one enemy debuff, stacked enemy debuffs, and enemy dot non-aggregation.
  - The US-011 matrix entry classifies `_calculate_dynamic_statement()`, `MultiplierData.get_buff_bonus()`, reader snapshots, `CalAnomaly` retained anomaly-state reads, `AnomalyBar` duration reads, and dot/freez-like continuations by formula parity, guarded maintenance, retained compatibility, and blocker-only follow-up.
  - This story adds formula parity evidence only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, enemy debuff single source of truth, dispatch adapter, runtime port, validation profile, guardrail, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `_calculate_dynamic_statement()`, `MultiplierData`, `DynamicStatement`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `MulData`, `AnomalyBar.__get_duration_enemy_buffs()`, dot/freez-like Load/Schedule continuations, copied anomaly / disorder output paths, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this test-only characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-012 by adding migrated reader seam regression samples using this enemy dynamic characterization as compatibility evidence without starting an enemy debuff single-source-of-truth migration.
---
## 2026-06-10 01:33 +08:00 - US-012
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_migrated_reader_seam_regression_sample_scope_is_representative()` and `test_migrated_reader_seam_regression_samples_match_retained_helpers()` prepare to replace manual spot checks of representative P2-A / P2-B migrated reader files with focused formula parity coverage.
  - The US-012 inventory entry records selected samples from `AliceAdditionalAbilityApBonus.py`, `JaneCinema1APTransToDmgBonus.py`, `QingYiAdditionalAbilityStunConvertToATK.py`, `CannonRotor.py`, and `Soldier0AnbyCoreSkillCritDMGBonus.py`, tying each reader seam to the retained Calculator helper it must match.
  - This story adds regression evidence only; it does not replace a live production path, Calculator formula, `MultiplierData`, `DynamicStatement`, dispatch adapter, listener broadcast, runtime port, validation profile, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalculatorBuffAttributeReader`, `MultiplierData`, `DynamicStatement`, P2-A / P2-B migrated BuffXLogic files, P2-C through P2-G guarded buckets, `CalAnomaly.py`, copied anomaly / disorder output paths, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - P2-A through P2-G remain completed guarded buckets and are reopened only by concrete guardrail or validation failure; this story found no new Buff coupling beyond already documented retained formula snapshot, copied-output, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-013 by characterizing any remaining formula parity suite samples from the current PRD without turning migrated reader-seam evidence into production formula replacement.
---
## 2026-06-10 01:50 +08:00 - US-013
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The US-013 behavior-sample decision matrix replaces ad hoc choices about when to run registered main-loop consistency samples with explicit domain rules for damage, stun, anomaly, copied-output, Buff timeline, scheduled event publish timing, and test-only stories.
  - This story adds validation-policy documentation only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered team fixture, or behavior sample.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, scheduled event producers, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, registered-team configs, `scripts/run_buff_refactor_validation.py`, `scripts/run_buff_main_loop_consistency.py`, `zsim/utils/main_loop_consistency.py`, and existing `calculator-reads` / `implicit-events` validation wiring all remain unchanged.
  - No old-coupling review update was needed; this documentation-only story found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-014 by deciding whether formula parity validation wiring remains on `calculator-reads` or gets a scoped named profile; do not add production formula replacement before the named focused pytest, mypy, registered-sample, rollback, and non-goal contract is explicit.
---
## 2026-06-10 02:03 +08:00 - US-014
- Files changed: `scripts/run_buff_refactor_validation.py`, `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `formula-parity` validation profile replaces ad hoc single-file formula characterization runs with a named scoped profile for the current Phase 3 formula parity fixture surface.
  - `FORMULA_PARITY_TYPECHECK_TARGETS` and `FORMULA_PARITY_FOCUSED_TEST_TARGETS` document the exact source, test, and runner targets used by that profile.
  - This story adds validation wiring and typing cleanup only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `calculator-reads` / `implicit-events` validation wiring remain available.
  - `calculator-reads` remains the active retained gate for migrated reader seams, raw-container guardrails, AM/AP guardrails, P2-B guardrails, state sync, and full-crit event-adjacent coverage.
  - No old-coupling review update was needed; this validation-wiring story found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-015 by updating handoff docs and the next candidate pool while keeping production formula replacement blocked until the formula parity suite, registered-sample triggers, rollback plan, and non-goals remain explicit.
---
## 2026-06-10 02:10 +08:00 - US-015
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The updated handoff docs replace provisional post-US-014 planning text with an explicit US-016 final serial validation / Go-No-Go default and a preserved next candidate pool.
  - This story prepares later replacement decisions only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring remain unchanged.
  - No old-coupling review update was needed; this documentation-only handoff found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-016 by running serial validation and writing the final formula replacement Go / No-Go handoff; production formula replacement remains blocked until that story names exact evidence and remaining blockers.
---
## 2026-06-10 02:25 +08:00 - US-016
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The final serial validation and Go / No-Go handoff replaces the provisional US-016 default with a closed validation record and a concrete next default: phase-3 formula oracle gap closure / deterministic parity matrix.
  - This iteration prepares later replacement decisions only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, guardrail, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring remain unchanged.
  - Final Go / No-Go is No-Go for production formula replacement: deterministic table-driven formula oracles, copied-output payload parity, `AnomalyBar.current_ndarray` field matrices, registered behavior sample triggers, rollback plan, retained validation gates, and non-goals must be explicit before any later production formula PRD.
  - No old-coupling review update was needed; this validation / handoff story found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Generate the next PRD for phase-3 formula oracle gap closure / deterministic parity matrix under `docs/Buff重构方案.md`; do not generate production formula replacement until those oracle gaps are closed and the next Go / No-Go explicitly says Go.
---
## 2026-06-10 09:33 +08:00 - US-001
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - This story reconfirms the phase-3 formula oracle gap closure boundary and prepares later replacement decisions; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, anomaly snapshot writer, dispatch adapter, runtime port, validation profile, guardrail, registered-team fixture, behavior sample, or phase-2 guarded bucket.
  - The current default remains deterministic formula oracle gap closure / parity matrix work before any production formula edit.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, `AnomalyBarClass.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - Production formula replacement remains No-Go until deterministic table-driven formula oracles, copied-output payload parity, `AnomalyBar.current_ndarray` field matrices, registered behavior sample triggers, rollback plan, retained validation gates, and non-goals are explicit and passing.
- Next step:
  - Continue with US-002 by inventorying existing formula fixtures and missing oracle targets without changing production formula semantics.
---
## 2026-06-10 09:43 +08:00 - US-002
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `docs/Buff公式候选与测试目标清单.md` now replaces broad repeated source-search handoff for the current phase-3 oracle-gap PRD with a named root-workspace fixture inventory and oracle target map.
  - This story builds documentation and validation routing only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, anomaly snapshot writer, dispatch adapter, runtime port, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, `AnomalyBarClass.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; root-workspace evidence matched already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-003 by stabilizing the table-driven formula oracle harness before adding individual `RegularMul`, `AnomalyMul`, `StunMul`, `CalAnomaly`, copied-output, or `AnomalyBar.current_ndarray` oracle cases.
---
## 2026-06-10 10:03 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_FormulaOracleCase`, `_FormulaOracleExpectation`, `_AnomalySnapshotOracleCase`, and `_CopiedOutputPayloadCase` replace one-off formula oracle setup for the current phase-3 test harness with table-driven retained / reader snapshot / optional reader assertions.
  - `_reset_formula_oracle_caches()` centralizes the cache reset used by formula oracle fixtures and prepares later stories to add deterministic `RegularMul`, `AnomalyMul`, `StunMul`, `CalAnomaly`, copied-output, and `AnomalyBar.current_ndarray` oracle cases without changing production formulas.
  - This story builds test harness infrastructure only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, anomaly snapshot writer, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, `AnomalyBarClass.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; the new table harness matched already documented retained formula snapshot, copied-output payload, enemy dynamic read, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-004 by adding deterministic `RegularMul` base damage and attribute input cases through the new table harness before any production formula replacement.
---
## 2026-06-10 10:15 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `regular-base-dmg-*` `_FORMULA_ORACLE_TABLE_CASES` replace implicit confidence in `Calculator.RegularMul.cal_base_dmg()` / `cal_base_attr()` foundations with executable retained-oracle coverage for neutral ATK, static HP selection, and dynamic ATK / base-damage buff fields.
  - The test fixture now prepares to replace ad hoc base-damage snapshot setup with explicit static ATK / HP / DEF fields and optional `SkillNode` construction, while still using retained `MultiplierData` / reader snapshot comparison only as compatibility evidence.
  - This story adds characterization only; it does not replace a live production path, Calculator formula, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `Calculator.RegularMul`, `MultiplierData`, `DynamicStatement`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - Reader seam evidence remains compatibility evidence only and does not authorize deleting retained `Calculator.RegularMul`, `MultiplierData`, or `DynamicStatement`.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-005 by characterizing `RegularMul` damage bonus, defense, resistance, and vulnerability fields without changing production formulas or widening into crit / anomaly / stun families.
---
## 2026-06-10 10:28 +08:00 - US-005
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `regular-multipliers-*` `_FORMULA_ORACLE_TABLE_CASES` replace implicit confidence in `Calculator.RegularMul.cal_dmg_bonus()` / `cal_defense_mul()` / `cal_res_mul()` / `cal_dmg_vulnerability()` with executable retained-oracle coverage for zero-like neutral, character-side damage-bonus stack, enemy defense / resistance, received resistance reduction / penetration, and vulnerability fields.
  - `_CalculatorReadSnapshot` now carries the minimal `enemy_obj` and `char_level` fields needed for retained defense / resistance formula parity while keeping `enemy_obj` out of dataclass hashing so cached AP reader behavior stays compatible.
  - This story adds characterization and snapshot-readiness only; it does not replace a live production path, Calculator formula semantics, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `Calculator.RegularMul`, `MultiplierData`, `DynamicStatement`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - Reader-snapshot evidence remains compatibility evidence only and does not authorize deleting retained `Calculator.RegularMul`, `MultiplierData`, or `DynamicStatement`.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-006 by characterizing `RegularMul` crit formula families / crit expectation boundaries without widening into anomaly, stun, copied-output, or production formula replacement work.
---
## 2026-06-10 10:42 +08:00 - US-006
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `regular-crit-received-boundary` `_FORMULA_ORACLE_TABLE_CASES` entry replaces implicit confidence in `Calculator.RegularMul.cal_crit_rate()` / `cal_personal_crit_rate()` / `cal_crit_dmg()` / `cal_personal_crit_dmg()` with executable retained-oracle coverage for received crit rate / damage inclusion and personal crit exclusion.
  - The direct crit boundary test now pins full crit damage separately from personal crit damage, but this remains characterization only and does not replace a live production path or retained Calculator formula.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `Calculator.RegularMul`, `MultiplierData`, `DynamicStatement`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - P2-B migrated reader seam samples remain guardrail evidence only and do not authorize deleting retained `Calculator.RegularMul`, `MultiplierData`, or `DynamicStatement`.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-007 by characterizing `AnomalyMul` mastery, proficiency, buildup, and base-damage oracle cases without changing production formulas or widening into copied-output / runtime work.
---
## 2026-06-10 10:55 +08:00 - US-007
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `anomaly-mastery-proficiency-buildup-base-damage` `_FORMULA_ORACLE_TABLE_CASES` entry replaces implicit confidence in `Calculator.AnomalyMul.cal_am()` / `cal_ap()` / `cal_anomaly_buildup()` / `cal_base_damage()` with executable retained-oracle coverage for AM/AP reader parity, fire anomaly buildup, base anomaly damage, enemy anomaly resistance, trigger buildup bonus, and reader-built formula snapshots.
  - This story adds characterization only; it does not replace a live production path, Calculator formula semantics, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `Calculator.AnomalyMul`, `MultiplierData`, `DynamicStatement`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - P2-A migrated AM/AP reader seam samples remain guarded-maintenance evidence only and do not authorize deleting retained `Calculator.AnomalyMul`, `MultiplierData`, or `DynamicStatement`.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-008 by characterizing `AnomalyMul` damage bonus, AP multiplier, extra multiplier, and anomaly crit without widening into production formula replacement, copied-output, or runtime work.
---
## 2026-06-10 11:08 +08:00 - US-008
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `anomaly-dmg-bonus-ratio-fields`, `anomaly-ap-multiplier-conversion`, `anomaly-extra-multiplier-fields`, and `anomaly-crit-retained-fields` `_FORMULA_ORACLE_TABLE_CASES` entries replace implicit confidence in `Calculator.AnomalyMul.cal_dmg_bonus()` / `cal_ap_mul()` / `cal_ap()` / `cal_ano_extra_mul()` / `cal_anomaly_crit()` with executable retained-oracle coverage for anomaly damage fields, AP conversion fields, extra multiplier fields, and the retained anomaly-crit `1` boundary.
  - This story adds characterization only; it does not replace a live production path, Calculator formula semantics, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `Calculator.AnomalyMul`, `MultiplierData`, `DynamicStatement`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - P2-A migrated AM/AP reader seam samples remain guarded-maintenance evidence only; the new table cases are retained-oracle evidence and do not authorize deleting retained `Calculator.AnomalyMul`, `MultiplierData`, or `DynamicStatement`.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-009 by characterizing `StunMul` impact, stun ratio, resistance, bonus, and received formulas without widening into `AnomalyMul.cal_res_pen()`, anomaly vector snapshots, copied-output, or production formula replacement.
---
## 2026-06-10 11:21 +08:00 - US-009
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `stun-impact-reader-parity` and `stun-ratio-res-bonus-received-retained` `_FORMULA_ORACLE_TABLE_CASES` entries replace implicit confidence in `Calculator.StunMul.cal_imp()` / `cal_stun_ratio()` / `cal_stun_res()` / `cal_stun_bonus()` / `cal_stun_received()` with executable retained-oracle coverage for impact, stun ratio, enemy stun resistance, trigger / label stun bonus, and received stun fields.
  - The formula fixture now prepares to replace ad hoc stun snapshot setup with explicit `SkillNode.stun_ratio` and `enemy.stun_resistance_dict` inputs while keeping `read_impact(...)` as the only reader API parity path in this story.
  - This story adds characterization only; it does not replace a live production path, Calculator formula semantics, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `Calculator.StunMul`, `MultiplierData`, `DynamicStatement`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - P2-B migrated impact reader seam samples remain guarded-maintenance evidence only; the new table cases are retained-oracle evidence and do not authorize deleting retained `Calculator.StunMul`, `MultiplierData`, or `DynamicStatement`.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-010 by characterizing `MultiplierData` translation cache and invalid key edges without widening into production formula replacement, copied-output, or runtime work.
---
## 2026-06-10 11:30 +08:00 - US-010
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `test_multiplier_data_dynamic_statement_translates_python_attr_names()`, `test_multiplier_data_dynamic_statement_rejects_invalid_effect_key()`, and `test_multiplier_data_cache_key_stability_and_reset_isolation()` replace implicit confidence in `MultiplierData.DynamicStatement.__read_dynamic_statement()` and `MultiplierData` / `StaticStatement` cache behavior with executable characterization for Python-attribute-name translation through `buff_effect_trans`, invalid key errors, same-key cache reuse, and reset isolation.
  - This story adds characterization only; it does not replace a live production path, Calculator formula semantics, CalAnomaly formula, copied-output formula, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `MultiplierData`, `MultiplierData.mul_data_cache`, `DynamicStatement`, `StaticStatement._instance_cache`, `_calculate_dynamic_statement()`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot and enemy dynamic read boundaries.
- Next step:
  - Continue with US-011 by characterizing `DynamicStatement` enemy debuff and dot cache participation without changing production formulas or widening into copied-output / runtime work.
---
## 2026-06-10 11:43 +08:00 - US-011
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The expanded `test_enemy_dynamic_debuff_reads_feed_old_and_reader_formula_snapshots()` and new `test_multiplier_data_cache_key_distinguishes_enemy_dot_participation()` replace implicit confidence in enemy debuff aggregation / dot cache participation with executable characterization for direct `_calculate_dynamic_statement()`, `MultiplierData.get_buff_bonus()`, reader snapshots, and `MultiplierData.__new__()` cache keys.
  - This story adds characterization only; it does not replace a live production path, Calculator formula semantics, CalAnomaly formula, copied-output formula, `AnomalyBar.__get_duration_enemy_buffs()`, Load/Schedule dot continuation behavior, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py` retained formulas, `_calculate_dynamic_statement()`, `MultiplierData`, `MultiplierData.__new__()`, `MultiplierData.get_buff_bonus()`, `DynamicStatement`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `AnomalyBar.__get_duration_enemy_buffs()`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - Enemy dot entries remain cache-key inputs but are not included in `enabled_buff` aggregation for dynamic statements.
- Next step:
  - Continue with US-012 by adding migrated reader seam regression samples without reopening production formula replacement or migrating anomaly duration / Load-Schedule continuation behavior.
---
## 2026-06-10 12:02 +08:00 - US-012
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The new `test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()` and `_CalAnomalyMultiplierOracleCase` entries replace implicit confidence in `CalAnomaly.cal_active_crit(...)`, `cal_def_mul(...)`, resistance / vulnerability, stun vulnerability, and special multiplier inputs with executable retained `MulData` / settled `AnomalyBar.current_ndarray` characterization.
  - `_make_settled_anomaly_formula_fixture(...)` now prepares live `CalAnomaly` formula tests by constructing a statement-bearing `_make_character(...)` and accepting explicit `element_type`, but this remains test harness support only.
  - This story adds characterization only; it does not replace a live production path, `CalAnomaly.py` formula semantics, `Calculator.py` formula semantics, copied-output formula, anomaly snapshot writer, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `Calculator.py`, `Calculator.RegularMul`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `AnomalyBarClass.py`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-013 by characterizing `CalAnomaly.set_final_multipliers(...)`, snapshot impact / stun ratio treatment, multiplication order, `cal_anomaly_dmg(...)`, and `scaling_factor` placement without changing production formulas.
---
## 2026-06-10 12:14 +08:00 - US-013
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - The `_CAL_ANOMALY_FINAL_MULTIPLIER_ORDER` contract and non-default `scaling_factor` values in `test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()` replace implicit confidence in `CalAnomaly.set_final_multipliers(...)` vector ordering, snapshot impact / stun ratio treatment, and `cal_anomaly_dmg(...)` scaling placement with executable retained formula evidence.
  - This story adds characterization only; it does not replace a live production path, `CalAnomaly.py` formula semantics, `Calculator.py` formula semantics, copied-output formula, anomaly snapshot writer, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `AnomalyBarClass.py`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-014 by characterizing `CalDisorder` base damage, extra multiplier, and stun formulas without widening into `CalPolarityDisorder`, `CalAbloom`, copied-output payloads, or production formula replacement.
---
## 2026-06-10 12:28 +08:00 - US-014
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_CAL_DISORDER_ORACLE_CASES` and `test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()` replace implicit confidence in `CalDisorder.cal_disorder_base_dmg(...)`, `cal_disorder_extra_mul(...)`, and `cal_disorder_stun(...)` with executable element-type retained formula evidence.
  - This story adds characterization only; it does not replace a live production path, `CalAnomaly.py` / `CalDisorder` formula semantics, `Calculator.py` formula semantics, copied-output payload construction, handler report payloads, listener broadcast, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `CalDisorder`, `CalPolarityDisorder`, `CalAbloom`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-015 by characterizing `CalPolarityDisorder` formula inputs and payload boundary without widening into `CalAbloom`, copied-output report payloads, or production formula replacement.
---
## 2026-06-10 12:43 +08:00 - US-015
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_CAL_POLARITY_DISORDER_ORACLE_CASES` and `test_cal_polarity_disorder_formula_inputs_and_payload_boundary()` replace implicit confidence in `CalPolarityDisorder.__init__(...)` with executable retained formula evidence for copied `PolarityDisorder` payload fields, polarity ratio scaling, Yanagi AP additional damage, and settled snapshot inputs.
  - This story adds characterization only; it does not replace a live production path, `CalAnomaly.py` / `CalPolarityDisorder` formula semantics, `Calculator.py` formula semantics, copied-output payload construction, handler report payloads, listener broadcast, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `CalDisorder`, `CalPolarityDisorder`, `CalAbloom`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, `PolarityDisorderEventHandler`, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-016 by characterizing `CalAbloom` formula inputs without widening into copied-output report payloads, listener broadcasts, scheduled publish, runtime ports, or production formula replacement.
---
## 2026-06-10 12:58 +08:00 - US-016
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_CAL_ABLOOM_ORACLE_CASES` and `test_cal_abloom_formula_inputs_and_fixture_blockers()` replace implicit confidence in `CalAbloom.__init__(...)` with executable retained formula evidence for copied `DirgeOfDestinyAnomaly.current_ndarray`, `anomaly_dmg_ratio`, inherited `CalAnomaly` final multiplier vector, `scaling_factor`, and retained `MultiplierData.dynamic` inputs.
  - `schedule_priority`, `rename_tag`, and `accompany_dot` are documented as output-only sentinel / fixture blocker fields for this story; they remain outside formula expectations until a later copied-output report payload parity story.
  - This story adds characterization only; it does not replace a live production path, `CalAnomaly.py` / `CalAbloom` formula semantics, `Calculator.py` formula semantics, copied-output payload construction, Abloom handler report payloads, listener broadcast, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `CalAbloom`, `CalDisorder`, `CalPolarityDisorder`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, `AbloomEventHandler`, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-017 by building the `AnomalyBar.current_ndarray` reset / deepcopy / settlement matrix without widening into production formula replacement, handler report payloads, or runtime write paths.
---
## 2026-06-10 13:13 +08:00 - US-017
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_ANOMALY_CURRENT_NDARRAY_FIELDS`, the expanded `test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility()`, and `test_anomaly_bar_current_ndarray_reset_deepcopy_and_shallow_copy_matrix()` replace implicit confidence in `AnomalyBar.current_ndarray` shape / copy behavior with executable retained-state characterization for 11 snapshot fields, effective-only settlement, copied-output active_by override, shallow aliasing, deepcopy non-aliasing, and reset shapes.
  - This story adds characterization only; it does not replace a live production path, `AnomalyBarClass.py` state semantics, `UpdateAnomaly.py` write behavior, `CalAnomaly.py` formula semantics, `CopyAnomalyForOutput.py` payload construction, handler report payloads, listener broadcast, dispatch adapter, runtime port, validation profile, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `AnomalyBarClass.py`, `AnomalyBar.current_ndarray`, `UpdateAnomaly.py`, `CalAnomaly.py`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `CopyAnomalyForOutput.py`, copied anomaly / disorder output paths, `AnomalyEventHandler`, `AbloomEventHandler`, P2-A through P2-G guarded buckets, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-018 by characterizing the `UpdateAnomaly.py` write-path field matrix without widening into production formula replacement, copied-output report payload parity, or runtime write-path replacement.
---
## 2026-06-10 13:32 +08:00 - US-018
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_update_anomaly_records_new_anomaly_field_matrix_with_runtime_dot()` replaces implicit confidence in `UpdateAnomaly.update_anomaly(...)` new-anomaly write behavior with executable characterization for source snapshot reset, copied `NewAnomaly` fields, active-state flags, listener broadcast, character resource notification, runtime dot replacement, and scheduled publish order.
  - This story adds characterization only; it does not replace a live production path, `UpdateAnomaly.py` branch semantics, copied-output constructors, `ScheduleDispatchPort`, `DotRuntimeStateAdapter`, listener broadcasts, runtime command behavior, validation profile wiring, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `UpdateAnomaly.py`, `anomaly_effect_active(...)`, `remove_dots_cause_disorder(...)`, `spawn_output(...)`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.NewAnomaly`, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-019 by characterizing `CopyAnomalyForOutput.NewAnomaly` payload fields separately from `UpdateAnomaly.py` publish order and without widening into runtime write-path replacement.
---
## 2026-06-10 13:46 +08:00 - US-019
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_new_anomaly_spawn_output_copies_active_payload_without_publish()` replaces implicit confidence in `CopyAnomalyForOutput.NewAnomaly` mode-0 copied payload fields with executable characterization for active `AnomalyBar` settlement copy, `current_ndarray`, `current_effective_anomaly`, `element_type`, `anomaly_dmg_ratio`, `scaling_factor`, duration fields, `active_by`, and no listener publish.
  - This story adds characterization only; it does not replace a live production path, `CopyAnomalyForOutput.py` constructors, `UpdateAnomaly.py` branch semantics, handler report payloads, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, runtime ports, validation profile wiring, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CopyAnomalyForOutput.NewAnomaly`, `UpdateAnomaly.spawn_output(...)`, `UpdateAnomaly.update_anomaly(...)`, `AnomalyBar.current_ndarray`, `AnomalyBar.anomaly_settled()`, `CalAnomaly.py`, `Calculator.py`, copied disorder / polarity disorder output paths, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-020 by characterizing `Disorder` and `PolarityDisorder` copied-output payload parity without widening into production formula replacement or runtime write-path replacement.
---
## 2026-06-10 13:57 +08:00 - US-020
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_COPIED_OUTPUT_PAYLOAD_CASES` and `test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()` replace implicit confidence in `CopyAnomalyForOutput.Disorder` / `PolarityDisorder` copied payload fields with executable characterization for exact copied class, `is_disorder`, `polarity_disorder_ratio`, `additional_dmg_ap_ratio`, `remaining_tick()`, `settled`, `current_effective_anomaly`, and `current_ndarray` non-aliasing.
  - This story adds characterization only; it does not replace a live production path, `CopyAnomalyForOutput.py` constructors, `UpdateAnomaly.py` branch semantics, `spawn_output(...)` listener broadcast, scheduled publish order, handler report payloads, runtime ports, validation profile wiring, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `CopyAnomalyForOutput.Disorder`, `CopyAnomalyForOutput.PolarityDisorder`, `UpdateAnomaly.spawn_output(...)`, `UpdateAnomaly.update_anomaly(...)`, `AnomalyBar.current_ndarray`, `CalDisorder`, `CalPolarityDisorder`, `CalAnomaly.py`, `Calculator.py`, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-021 by characterizing `UpdateAnomaly.spawn_output(...)` mode 0 / 1 / 2 listener-facing fields and publish order while keeping listener broadcast, scheduled publish, dot runtime, and same-tick runtime writes separate.
---
## 2026-06-10 14:09 +08:00 - US-021
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_spawn_output_mode_zero_settles_without_listener_or_scheduled_publish()` and `test_spawn_output_disorder_modes_broadcast_listener_payload_without_publish()` replace implicit confidence in `UpdateAnomaly.spawn_output(...)` mode 0 / 1 / 2 output behavior with executable characterization for active-bar settlement, listener-facing copied payload fields, direct no-publish behavior, and polarity-only fields.
  - This story adds characterization only; it does not replace a live production path, `UpdateAnomaly.py` branch semantics, copied-output constructors, `ScheduleDispatchPort`, listener broadcast, dot runtime registration, runtime command behavior, validation profile wiring, registered-team fixture, behavior sample, or phase-2 guarded bucket.
- Compatibility retained:
  - Old paths still retained in this iteration: `UpdateAnomaly.spawn_output(...)`, `UpdateAnomaly.update_anomaly(...)`, `CopyAnomalyForOutput.NewAnomaly`, `CopyAnomalyForOutput.Disorder`, `CopyAnomalyForOutput.PolarityDisorder`, `AnomalyBar.anomaly_settled()`, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-022 by defining registered-team sample conditions for formula domains without widening into production formula replacement or runtime write-path replacement.
---
## 2026-06-10 14:18 +08:00 - US-022
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-022 行为样本决策矩阵` replaces implicit main-loop sample selection with documented trigger conditions for direct damage / crit, stun / impact, anomaly settlement, copied-output, Buff timeline, and event publish timing.
  - This story defines a boundary only; it does not replace a live production path, production formula, registered-team fixture, validation profile, dispatch adapter, runtime command port, old Buff container, or legacy compatibility path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, copied-output constructors, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - Current registered teams are documented as route candidates only where their APL can realistically reach the target route; Alice / Yuzuha / Jane gaps remain gaps instead of validation-only teams.
- Next step:
  - Continue with US-023 by codifying rollback anchors and retained validation gates without deleting old containers or legacy Buff write paths.
---
## 2026-06-10 14:26 +08:00 - US-023
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-023 rollback plan / retained validation gates` replaces implicit rollback expectations with documented revert-and-validate rules for failed helper, validation profile, or future production formula diffs.
  - This story builds a release-maintenance boundary only; it does not replace a live production path, formula implementation, validation runner contract, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.NewAnomaly`, `Disorder`, `PolarityDisorder`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this documentation story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-024 by confirming whether current `formula-parity` validation targets remain sufficient or need explicit runner-contract updates.
---
## 2026-06-10 14:38 +08:00 - US-024
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-024 formula-parity validation target contract` replaces implicit validation-target assumptions with an explicit retained contract: formula oracle tests stay under `tests/simulator/test_buff_attribute_reader.py`, and `FORMULA_PARITY_FOCUSED_TEST_TARGETS` / `FORMULA_PARITY_TYPECHECK_TARGETS` remain sufficient for the current formula-oracle surface.
  - This story builds a validation-contract boundary only; it does not replace a live production path, formula implementation, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - `tests/simulator/test_update_anomaly_dispatch.py` remains event/runtime copied-output evidence covered by `implicit-events` or story-local focused tests; it is not folded into `formula-parity` without a future formula-oracle source/test split.
  - No old-coupling review update was needed; this documentation story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-025 by running the serial formula oracle validation gate and recording pytest-asyncio / async log shutdown noise separately from command exit status.
---
## 2026-06-10 14:48 +08:00 - US-025
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-025 serial validation gate evidence` replaces implicit trust in branch-level formula oracle readiness with recorded serial `formula-parity`, `calculator-reads`, and conditional `implicit-events` validation outcomes.
  - This story validates retained boundaries only; it does not replace a live production path, production formula, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this validation-gate story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-026 by updating final handoff docs and the formula replacement Go / No-Go decision using the US-025 serial validation evidence.
---
## 2026-06-10 14:55 +08:00 - US-026
- Files changed: `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-026 final handoff / Go-No-Go decision` replaces the previous default `phase-3 formula oracle gap closure / deterministic parity matrix` with a new default `phase-3 replacement blocker closure / bounded-domain eligibility decision`.
  - This story updates handoff boundaries only; it does not replace a live production path, production formula, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `anomaly_snapshot` vector assembly, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly handler report payloads, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this docs-only handoff found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Generate the next PRD from `docs/Buff重构方案.md` and the refreshed next-stage plan, defaulting to `Calculator.AnomalyMul.cal_res_pen()` / `anomaly_snapshot` vector assembly blocker closure before any production formula replacement proposal.
---
## 2026-06-11 09:37 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_anomaly_mul_res_pen()` and the `anomaly-res-pen-fire-positive`, `anomaly-res-pen-default-zero`, and `anomaly-res-pen-frost-uses-ice-field` table rows replace implicit confidence in `Calculator.AnomalyMul.cal_res_pen()` with executable retained / reader-snapshot oracle evidence for positive resistance penetration, default zero behavior, and `element_type=5` reading `ice_res_pen_increase` while ignoring nonmatching / global fields.
  - This story adds characterization only; it does not replace live production formula code, `Calculator.AnomalyMul`, `MultiplierData`, `DynamicStatement`, reader APIs, copied-output payload construction, event dispatch, runtime ports, old containers, or legacy compatibility paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-004 by adding expected vector cases for `Calculator.AnomalyMul.anomaly_snapshot` without widening into copied-output payload, `AnomalyBar.current_ndarray` lifecycle, or production formula replacement.
---
## 2026-06-11 09:51 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_ANOMALY_MUL_SNAPSHOT_FIELDS`, `_ANOMALY_MUL_SNAPSHOT_ORACLE_CASES`, and `test_anomaly_mul_snapshot_vector_matches_expected_retained_fields()` replace implicit confidence in `Calculator.AnomalyMul.anomaly_snapshot` assembly with executable expected-vector evidence for the retained 9-slot snapshot order.
  - This story adds characterization only; it does not replace live production formula code, `Calculator.AnomalyMul`, `MultiplierData`, `DynamicStatement`, reader APIs, copied-output payload construction, `AnomalyBar.current_ndarray`, event dispatch, runtime ports, old containers, or legacy compatibility paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `Calculator.AnomalyMul.anomaly_snapshot`, `Calculator.AnomalyMul.cal_res_pen()`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-005 by characterizing or explicitly preserving `CalAnomaly.cal_k_level()` clamp behavior before any bounded production formula replacement proposal.
---
## 2026-06-11 10:01 +08:00 - US-005
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `_CAL_ANOMALY_LEVEL_CLAMP_ORACLE_CASES` and `test_cal_anomaly_level_clamp_remains_retained_lookup()` replace implicit confidence in `CalAnomaly.cal_k_level()` clamp behavior with executable retained lookup evidence for below-boundary `-1 -> 0.0`, normal `40 -> 1.6610`, and above-boundary `61 -> 2.0` inputs plus the retained log side effects.
  - This story adds characterization only; it does not replace live production formula code, `CalAnomaly.py`, `Calculator.py`, `MultiplierData`, `MulData`, `DynamicStatement`, copied-output payload construction, event dispatch, runtime ports, old containers, or legacy compatibility paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `CalAnomaly.py`, `CalAnomaly.cal_k_level()`, `Calculator.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-006 by characterizing copied-output handler and report payload parity without widening into production formula replacement, registered-route eligibility, or runtime write-path replacement.
---
## 2026-06-11 10:23 +08:00 - US-006
- Files changed: `tests/simulator/test_anomaly_handler_runtime_view.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/investigations/2026-06-11-US-006-copied-output-payload-parity.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `test_copied_anomaly_handler_reports_payload_fields_separate_from_settle_port()`, `test_abloom_copied_output_handler_reports_payload_fields()`, `test_disorder_handler_reports_payload_and_listener_fields()`, and `test_polarity_disorder_handler_reports_payload_and_listener_fields()` replace implicit confidence in copied-output handler report payloads with executable characterization for tick, skill tag, element type, rounded damage, anomaly/disorder flags, stun, buildup, runtime status, UUID, listener broadcast identity, runtime-view reads, and `RuntimeCommandPort` settle separation.
  - This story adds characterization only; it does not replace a live production path, `CopyAnomalyForOutput.py` constructors, `UpdateAnomaly.spawn_output(...)`, `UpdateAnomaly.update_anomaly(...)`, handler production code, `ScheduleDispatchPort`, listener broadcast semantics, dot runtime registration/removal, runtime ports, validation profile wiring, registered-team fixture, behavior sample, or production formula code.
- Compatibility retained:
  - Old paths still retained in this iteration: `CopyAnomalyForOutput.NewAnomaly`, `Disorder`, `PolarityDisorder`, `DirgeOfDestinyAnomaly`, `UpdateAnomaly.spawn_output(...)`, `AnomalyEventHandler`, `DisorderEventHandler`, `PolarityDisorderEventHandler`, `AbloomEventHandler`, `AnomalyBar.current_ndarray`, `CalAnomaly.py`, `Calculator.py`, `ScheduleDispatchPort`, scheduled publish ordering, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this characterization found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-007 by defining registered-route behavior sample eligibility without widening into production formula replacement or runtime write-path replacement.
---
## 2026-06-11 10:46 +08:00 - US-007
- Files changed: `scripts/ralph/investigations/2026-06-11-US-007-registered-route-eligibility.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-007 registered-route eligibility matrix` replaces implicit main-loop sample assumptions with explicit rules: a sample is required only for a future live production formula semantic diff, the team must be registered through `tests.teams.auto_register_teams()`, and anomaly / disorder domains must retain only samples with nonzero relevant event counts.
  - This story builds a validation eligibility boundary only; it does not replace a live production path, formula implementation, copied-output handler, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/copied-output handlers, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-008 by running the serial eligibility validation gate before any final bounded-domain Go / No-Go decision.
---
## 2026-06-11 11:02 +08:00 - US-008
- Files changed: `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-008 serial eligibility validation gate evidence` replaces implicit trust in the current PRD's blocker-closure readiness with recorded focused pytest, `formula-parity`, `calculator-reads`, and `implicit-events` validation outcomes.
  - This story validates retained boundaries only; it does not replace a live production path, production formula, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/copied-output handlers, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this validation-gate story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-009 by updating final handoff docs and the bounded-domain Go / No-Go decision using the US-008 serial validation evidence.
---
## 2026-06-11 11:12 +08:00 - US-009
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/investigations/2026-06-11-US-009-final-handoff-go-no-go.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-009 final bounded-domain Go / No-Go` replaces the previous blocker-closure default with a proposal-only next default: one bounded production replacement proposal for `Calculator.AnomalyMul.cal_res_pen()`.
  - This story updates handoff and eligibility boundaries only; it does not replace a live production path, production formula, validation runner wiring, dispatch adapter, runtime command port, old Buff container, copied-output constructor, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/copied-output handlers, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence handoff found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Generate the next PRD from `docs/Buff重构方案.md` and the refreshed next-stage plan, defaulting to a bounded proposal for `Calculator.AnomalyMul.cal_res_pen()` only while keeping copied-output parity, registered-route eligibility, retained compatibility, and P2-A through P2-G guarded maintenance as same-phase candidate blocks.
---
## 2026-06-11 11:53 +08:00 - US-001
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/investigations/2026-06-11-US-001-proposal-only-scope.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 proposal-only scope reconfirmation` replaces implicit carry-over from the previous PRD with explicit current-PRD evidence that only `Calculator.AnomalyMul.cal_res_pen()` may receive a bounded proposal in this run.
  - This story builds a docs/progress boundary only; it does not replace a live production path, production formula, copied-output constructor, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, copied-output payload handlers, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-002 by mapping existing blocker-closure evidence to the `Calculator.AnomalyMul.cal_res_pen()` proposal contract without implementing production formula changes.
---
## 2026-06-11 12:03 +08:00 - US-002
- Files changed: `scripts/ralph/investigations/2026-06-11-US-002-oracle-evidence-inventory.md`, `scripts/ralph/evidence-ledger.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-002 proposal evidence contract map` replaces implicit reuse of blocker-closure artifacts with an explicit inventory that separates proposal prerequisites from production implementation approval for `Calculator.AnomalyMul.cal_res_pen()`.
  - This story builds a docs/evidence boundary only; it does not replace live production formula code, copied-output constructors, validation runner wiring, dispatch adapters, runtime command ports, old Buff containers, or legacy compatibility write paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, copied-output payload handlers, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Continue with US-003 by drafting the bounded `Calculator.AnomalyMul.cal_res_pen()` proposal using this evidence map, without implementing a production formula diff.
---
## 2026-06-11 12:50 +08:00 - US-006
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 serial proposal validation gate evidence` replaces implicit trust in the current bounded proposal package with recorded `formula-parity` and `calculator-reads` exit-0 validation outcomes.
  - This story validates a docs/evidence boundary only; it does not replace live production formula code, copied-output constructors, validation runner wiring, dispatch adapters, runtime command ports, old Buff containers, or legacy compatibility write paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/copied-output handlers, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - `implicit-events` and full validation were skipped with explicit reasons because this story touched only docs/Ralph artifacts and found no new Buff coupling; no old-coupling review update was needed.
- Next step:
  - Continue with US-007 by updating final handoff docs and the bounded proposal Go / No-Go decision using the current serial validation evidence.
---
## 2026-06-11 13:06 +08:00 - US-007
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/investigations/2026-06-11-US-007-final-proposal-go-no-go.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-007 final proposal Go / No-Go` replaces the current proposal-only default with a later implementation Go for exactly `Calculator.AnomalyMul.cal_res_pen()`.
  - This story updates handoff and validation evidence only; it does not replace a live production path, production formula, validation runner wiring, dispatch adapter, runtime command port, old Buff container, copied-output constructor, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, `CopyAnomalyForOutput.py`, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/copied-output handlers, `ScheduleDispatchPort`, listener broadcasts, dot runtime registration, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, old containers, legacy `buff_add()` / `KickOutBuff()`, P2-A through P2-G guarded buckets, and the existing `formula-parity`, `calculator-reads`, `implicit-events`, and lifecycle validation wiring all remain unchanged.
  - No old-coupling review update was needed; this docs/evidence handoff found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, event/runtime, guarded-maintenance, and blocker-only boundaries.
- Next step:
  - Generate the next PRD from `docs/Buff重构方案.md` and the refreshed next-stage plan, defaulting to a bounded implementation PRD for exactly `Calculator.AnomalyMul.cal_res_pen()` while keeping copied-output parity, registered-route eligibility, retained compatibility, and P2-A through P2-G guarded maintenance as same-phase candidate blocks.
---
## 2026-06-11 14:57 +08:00 - US-001
- Files changed: `scripts/ralph/investigations/2026-06-11-US-001-exact-domain-implementation-scope.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 exact-domain implementation scope reconfirmation` replaces implicit broad implementation approval with explicit current-PRD evidence that only `Calculator.AnomalyMul.cal_res_pen()` may change in production code unless a later story documents a required focused-test or validation-profile adjustment.
  - This story builds a scope/investigation boundary only; it does not replace a live production path, production formula, copied-output constructor, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, copied-output constructors, `MultiplierData`, `MulData`, `DynamicStatement`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade`.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, and runtime boundary layers.
- Next step:
  - Continue with US-002 by expanding focused selector oracle coverage for all supported `cal_res_pen()` branches and invalid-element behavior before production source changes.
---
## 2026-06-11 15:09 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 branch-complete cal_res_pen oracle coverage` prepares to replace the inline `Calculator.AnomalyMul.cal_res_pen()` selector by pinning physical, fire, ice, frost-to-ice, electric, ether, auric-ink, default-zero, and invalid-element behavior before production code moves.
  - This story builds a test/oracle boundary only; it does not replace a live production path, production formula, copied-output constructor, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, copied-output constructors, `MultiplierData`, `MulData`, `DynamicStatement`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade`.
  - `all_res_pen_increase` remains outside `cal_res_pen()` and is pinned as a `RegularMul.cal_res_mul()` resistance-multiplier input.
  - No old-coupling review update was needed; this focused oracle story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, and runtime boundary layers.
- Next step:
  - Continue with US-003 by extracting the bounded `Calculator.AnomalyMul.cal_res_pen()` selector against the new branch-complete oracle coverage.
---
## 2026-06-11 15:19 +08:00 - US-003
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `Calculator.AnomalyMul._select_res_pen_for_element(...)` replaces the inline branch selector inside `Calculator.AnomalyMul.cal_res_pen(data)` while keeping `cal_res_pen(data)` as the public retained formula method.
  - This story implements a bounded behavior-preserving extraction only; it does not replace adjacent production formulas, copied-output constructors, validation runner wiring, dispatch adapters, runtime command ports, old Buff containers, or legacy compatibility write paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen(data)` still asserts `SkillNode` and delegates from the same caller path; `Calculator.AnomalyMul.__init__` still assigns `self.res_pen` from `self.cal_res_pen(data)`.
  - Physical, fire, ice/frost, electric, ether/auric-ink, default-zero, and invalid-element behavior remain covered by focused oracle tests; `MultiplierData`, `MulData`, `DynamicStatement`, `CalculatorBuffAttributeReader`, `_build_formula_snapshot(context)`, `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain unchanged.
  - No old-coupling review update was needed; this focused extraction found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, and runtime boundary layers.
- Next step:
  - Continue with US-004 by verifying retained reader snapshot compatibility and formula-boundary retention around the extracted selector without widening into adjacent formulas or validation-profile rewiring.
---
## 2026-06-11 15:33 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_res_pen_retained_and_reader_snapshot_select_same_dynamic_field()` replaces implicit confidence in retained / reader-snapshot compatibility after the selector extraction with explicit coverage for every supported `cal_res_pen()` branch.
  - This story builds a characterization guardrail only; it does not replace live production formula code, copied-output constructors, validation runner wiring, dispatch adapters, runtime command ports, old Buff containers, or legacy compatibility write paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen(data)` remains the public retained formula method, `Calculator.AnomalyMul._select_res_pen_for_element(...)` remains the private selector, and `Calculator.AnomalyMul.__init__` still assigns `self.res_pen` from `self.cal_res_pen(data)`.
  - Physical, fire, ice/frost, electric, ether/auric-ink, and dynamic-field snapshot compatibility are now covered for both retained `MultiplierData` and `CalculatorBuffAttributeReader._build_formula_snapshot(context)`; `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, copied-output constructors, copied-output report payloads, `MultiplierData`, `MulData`, `DynamicStatement`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain unchanged.
  - No old-coupling review update was needed; this focused compatibility story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, and runtime boundary layers.
- Next step:
  - Continue with US-005 by checking validation profile wiring and scoped typecheck coverage without assuming a production file split occurred.
---
## 2026-06-11 15:41 +08:00 - US-005
- Files changed: `scripts/ralph/investigations/2026-06-11-US-005-validation-profile-wiring.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 formula-parity wiring evidence` replaces implicit trust in the validation profile after the selector extraction with recorded runner introspection, CLI choices, and `formula-parity` output that includes `Calculator.py` plus the focused reader test file.
  - This story validates a guardrail boundary only; it does not replace live production formula code, copied-output constructors, validation runner wiring, dispatch adapters, runtime command ports, old Buff containers, or legacy compatibility write paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen(data)` remains the public retained formula method, `Calculator.AnomalyMul._select_res_pen_for_element(...)` remains the private selector, and `Calculator.AnomalyMul.__init__` still assigns `self.res_pen` from `self.cal_res_pen(data)`.
  - `formula-parity` continues to cover `zsim/sim_progress/ScheduledEvent/Calculator.py`, focused pytest for `tests/simulator/test_buff_attribute_reader.py`, and scoped mypy for the same test file; `calculator-reads`, `implicit-events`, and lifecycle profile choices remain available.
  - No old-coupling review update was needed; this validation-profile story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, and runtime boundary layers.
- Next step:
  - Continue with US-006 by running the focused `formula-parity` and retained `calculator-reads` gates serially.
---
## 2026-06-11 15:52 +08:00 - US-006
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 serial implementation validation evidence` replaces accepting the bounded `cal_res_pen()` selector extraction on local focused tests alone with recorded focused pytest, `formula-parity`, and `calculator-reads` exit-0 outcomes.
  - This story validates the already-extracted boundary only; it does not replace adjacent production formulas, copied-output constructors, validation runner wiring, dispatch adapters, runtime command ports, old Buff containers, or legacy compatibility write paths.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen(data)` remains the public retained formula method, `Calculator.AnomalyMul._select_res_pen_for_element(...)` remains the private selector, and `Calculator.AnomalyMul.__init__` still assigns `self.res_pen` from `self.cal_res_pen(data)`.
  - `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, copied-output constructors, copied-output report payloads, `MultiplierData`, `MulData`, `DynamicStatement`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain unchanged.
  - Known warning/noise was separated from exit status: focused pytest, `formula-parity`, and `calculator-reads` exited `0`; pytest-asyncio loop-scope warnings and async log-writer shutdown `RuntimeError` appeared after successful validation markers.
  - `implicit-events` was skipped because no copied-output, event-adjacent, dispatch, listener, dot runtime, or same-tick runtime-write files changed. No old-coupling review update was needed.
- Next step:
  - Continue with US-007 by deciding registered behavior sample eligibility from the current behavior-preserving extraction evidence without creating a validation-only registered team.
---
## 2026-06-11 16:03 +08:00 - US-007
- Files changed: `scripts/ralph/investigations/2026-06-11-US-007-registered-route-eligibility.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 registered behavior sample eligibility decision` replaces implicit main-loop sample ambiguity with an explicit rule: the current `cal_res_pen()` selector extraction is behavior-preserving, so no registered main-loop consistency sample is required for this story.
  - This story builds a validation eligibility boundary only; it does not replace a live production path, production formula, copied-output constructor, validation runner wiring, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen(data)` remains the public retained formula method, `Calculator.AnomalyMul._select_res_pen_for_element(...)` remains the private selector, and `Calculator.AnomalyMul.__init__` still assigns `self.res_pen` from `self.cal_res_pen(data)`.
  - `scripts/run_buff_main_loop_consistency.py` remains a future live-semantic-diff gate only. Future anomaly/disorder samples must use an already registered route and retain evidence only when both legacy and candidate labels show nonzero relevant event counts.
  - No validation-only registered team was created; no old-coupling review update was needed because this story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, registered-route, and runtime boundary layers.
- Next step:
  - Continue with US-008 by recording rollback anchors and replacement notes without broadening beyond the bounded `cal_res_pen()` extraction.
---
## 2026-06-11 16:19 +08:00 - US-008
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-008 rollback anchor for Calculator.AnomalyMul.cal_res_pen()` records that the completed implementation story replaced only the inline element-to-resistance-penetration selector inside the retained public `Calculator.AnomalyMul.cal_res_pen(data)` path with `Calculator.AnomalyMul._select_res_pen_for_element(...)`.
  - Rollback anchor: `zsim/sim_progress/ScheduledEvent/Calculator.py` keeps the current retained source at `_select_res_pen_for_element(...)` and `cal_res_pen(data)`; rollback should restore the previous inline branch selector inside `cal_res_pen(data)` and remove the private helper/delegation only, without changing `CalAnomaly.py`, copied-output constructors, old Buff containers, or runtime compatibility paths.
  - Required evidence: `formula-parity` and `calculator-reads` were required and passed for this story; `implicit-events`, default lifecycle validation, and registered main-loop sample evidence were not required because this story changed only docs/Ralph artifacts and the implemented production diff is a behavior-preserving selector extraction with no copied-output, event-adjacent, dispatch, listener, dot runtime, same-tick runtime-write, or live semantic diff.
- Compatibility retained:
  - This PRD does not delete `MultiplierData`, `MulData`, `DynamicStatement`, old containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, or `LegacyBuffRuntimeFacade`.
  - Old paths still retained in this iteration: `Calculator.AnomalyMul.cal_res_pen(data)` remains the public retained formula method, `Calculator.AnomalyMul.__init__` still assigns `self.res_pen` from `self.cal_res_pen(data)`, and `CalAnomaly.py`, copied-output constructors, old Buff containers, and runtime compatibility paths remain unchanged.
  - No old-coupling review update was needed; this docs/evidence story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, registered-route, and runtime boundary layers.
- Next step:
  - Continue with US-009 by running final serial validation and refreshing handoff docs without weakening the rollback anchors recorded here.
---
## 2026-06-11 16:31 +08:00 - US-009
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/investigations/2026-06-11-US-009-final-handoff-go-no-go.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-009 final implementation handoff docs` replace proposal-era ambiguity with the final decision that `Calculator.AnomalyMul.cal_res_pen()` is implemented as a behavior-preserving bounded selector extraction.
  - This story does not replace an additional live production path; the actual production replacement for this PRD remains the earlier `_select_res_pen_for_element(...)` extraction inside the retained public `cal_res_pen(data)` path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_res_pen(data)` remains the public retained formula method, and rollback remains limited to `_select_res_pen_for_element(...)` / `cal_res_pen(data)` helper delegation.
  - `Calculator.AnomalyMul.anomaly_snapshot`, `CalAnomaly.cal_k_level()`, copied-output constructors, old containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and P2-A through P2-G guarded buckets remain retained.
  - `implicit-events`, default lifecycle validation, and registered main-loop sample evidence were not required for this final docs story because no copied-output, event-adjacent, dispatch, listener, dot runtime, same-tick runtime-write, lifecycle, validation-runner, or live semantic path changed.
- Next step:
  - Generate the next PRD as Phase-3 next-candidate selection / oracle-gap closure; do not reopen `cal_res_pen()` unless focused regression, guardrail, or validation evidence requires it.
---
## 2026-06-11 18:15 +08:00 - US-001
- Files changed: `scripts/ralph/investigations/2026-06-11-US-001-am-ap-impact-scope.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `2026-06-11-US-001-am-ap-impact-scope.md` replaces implicit AM/AP/impact PRD scope assumptions with evidence-backed scope boundaries, query terms, retained non-goals, and validation evidence.
  - This story builds a boundary only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_res_pen()` remains completed by the previous PRD and out of default scope.
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, and `CalculatorBuffAttributeReader.read_anomaly_mastery()`, `read_anomaly_proficiency()`, `read_impact()` are the current in-scope oracle/readiness symbols for later stories.
  - `CalAnomaly.cal_k_level()`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed; this docs-only scope story found no new Buff coupling beyond already documented retained formula snapshot, copied-output payload, old-container, registered-route, and runtime boundary layers.
- Next step:
  - Continue with US-002 by running the root-workspace AM/AP/impact formula and reader call-path census, excluding `.codex_worktrees/` and generated artifacts from blocker conclusions.
---
## 2026-06-11 18:28 +08:00 - US-002
- Files changed: `scripts/ralph/investigations/2026-06-11-US-002-am-ap-impact-census.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `2026-06-11-US-002-am-ap-impact-census.md` replaces implicit AM/AP/impact call-path assumptions with a root-workspace census that separates retained formulas, reader-backed compatibility, test-only guardrails, docs/task history, and future candidate evidence.
  - This story builds an evidence boundary only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, and `CalculatorBuffAttributeReader.read_anomaly_mastery()`, `read_anomaly_proficiency()`, `read_impact()` remain unchanged.
  - Reader-backed BuffXLogic paths remain compatibility evidence; direct `Cal.AnomalyMul.cal_ap(...)` calls in Vivian cinema/core-passive and `CalAnomaly.py` remain future AP oracle candidate evidence, not changes in this iteration.
  - `.codex_worktrees/`, caches, generated logs, Ralph archives, docs, and historical tasks were excluded from blocker conclusions. No old-coupling review update was needed because this census found no new live Buff coupling beyond already documented retained formula/read-path boundaries.
- Next step:
  - Continue with US-003 by adding explicit numeric retained `MultiplierData` oracle rows for `Calculator.AnomalyMul.cal_am(...)`.
---
## 2026-06-11 18:45 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_am_retained_multiplier_data_oracle_rows` replaces implicit AM retained formula assumptions with explicit retained `MultiplierData` oracle rows for default-zero, base-only, static statement override, dynamic flat increase, and mixed percentage-plus-flat behavior.
  - This story builds oracle coverage only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()` remains unchanged and still computes `static.am * (1 + dynamic.field_anomaly_mastery) + dynamic.anomaly_mastery`.
  - `CalculatorBuffAttributeReader.read_anomaly_mastery()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-004 by adding AM reader snapshot parity rows without changing the retained AM oracle expected values.
---
## 2026-06-11 19:05 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_am_retained_multiplier_data_oracle_rows` now replaces implicit AM reader parity assumptions with executable comparisons across retained `MultiplierData`, reader-built `_build_formula_snapshot(context)`, and `CalculatorBuffAttributeReader.read_anomaly_mastery(...)`.
  - This story builds compatibility evidence only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()` remains unchanged and still computes `static.am * (1 + dynamic.field_anomaly_mastery) + dynamic.anomaly_mastery`.
  - `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-005 by adding explicit numeric retained `MultiplierData` oracle rows for `Calculator.AnomalyMul.cal_ap(...)` before mirroring reader snapshot parity in US-006.
---
## 2026-06-11 19:20 +08:00 - US-005
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_ap_retained_multiplier_data_oracle_rows` replaces implicit AP retained formula assumptions with explicit retained `MultiplierData` oracle rows for default-zero, base-only, static statement override, dynamic flat increase, and mixed percentage-plus-flat behavior.
  - This story builds oracle coverage only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_ap()` remains unchanged and still computes `static.ap * (1 + dynamic.field_anomaly_proficiency) + dynamic.anomaly_proficiency`.
  - `CalAnomaly.cal_k_level()` was observed as a separate retained lookup and remains out of scope for AP oracle rows.
  - `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.cal_am()`, `Calculator.StunMul.cal_imp()`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-006 by adding AP reader snapshot parity rows against the retained AP oracle values without changing production formulas.
---
## 2026-06-11 19:29 +08:00 - US-006
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_ap_retained_multiplier_data_oracle_rows` now replaces implicit AP reader parity assumptions with executable comparisons across retained `MultiplierData`, reader-built `_build_formula_snapshot(context)`, and `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)`.
  - This story builds compatibility evidence only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_ap()` remains unchanged and still computes `static.ap * (1 + dynamic.field_anomaly_proficiency) + dynamic.anomaly_proficiency`.
  - Existing AP state-sync / read-then-writeback guardrails and copied-output anomaly/disorder payload behavior remain unchanged.
  - `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.AnomalyMul.cal_am()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-007 by adding explicit numeric retained `MultiplierData` oracle rows for `Calculator.StunMul.cal_imp(...)` before mirroring impact reader snapshot parity in US-008.
---
## 2026-06-11 19:38 +08:00 - US-007
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_imp_retained_multiplier_data_oracle_rows` replaces implicit impact retained formula assumptions with explicit retained `MultiplierData` oracle rows for default-zero, base-only, static statement override, dynamic in-battle percentage increase, and mixed percentage-plus-flat behavior.
  - This story builds oracle coverage only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.StunMul.cal_imp()` remains unchanged and still computes `static.imp * (1 + dynamic.field_imp_percentage) + dynamic.imp`.
  - Impact/stun formula work remains separate from anomaly formula replacement; `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.AnomalyMul.cal_res_pen()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-008 by adding impact reader snapshot parity rows against the retained impact oracle values without changing production formulas.
---
## 2026-06-11 19:47 +08:00 - US-008
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_cal_imp_retained_multiplier_data_oracle_rows` now replaces implicit impact reader parity assumptions with executable comparisons across retained `MultiplierData`, reader-built `_build_formula_snapshot(context)`, and `CalculatorBuffAttributeReader.read_impact(...)`.
  - This story builds compatibility evidence only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.StunMul.cal_imp()` remains unchanged and still computes `static.imp * (1 + dynamic.field_imp_percentage) + dynamic.imp`.
  - Existing P2-B crit/impact guardrails, event-adjacent dispatch behavior, listener paths, `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.AnomalyMul.cal_res_pen()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-009 by preserving the formula boundary compatibility assertions without broadening AM/AP/impact reader parity into unrelated crit formula replacement.
---
## 2026-06-11 19:57 +08:00 - US-009
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/investigations/2026-06-11-US-009-formula-boundary-test-split.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_calculator_am_ap_impact_formula_boundaries_remain_retained_compatibility` replaces the AM/AP/impact portion of the old mixed formula-boundary table with a dedicated retained formula-family compatibility check.
  - `test_calculator_attribute_formula_boundaries_remain_retained_compatibility` remains as the crit boundary check and now proves full/personal crit rate plus full/personal crit damage retained responsibility boundaries without mixing in AM/AP/impact parity.
  - This story reorganizes compatibility tests only; it does not replace a live production formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility write path.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `Calculator.RegularMul.cal_crit_rate()`, `Calculator.RegularMul.cal_personal_crit_rate()`, `Calculator.RegularMul.cal_crit_dmg()`, and `Calculator.RegularMul.cal_personal_crit_dmg()` remain unchanged.
  - AM/AP/impact reader parity remains compatibility evidence only and does not authorize crit formula replacement.
  - No old-coupling review update was needed because this test-only story found no new Buff coupling.
- Next step:
  - Continue with US-010 by verifying validation profile wiring for AM/AP/impact without editing the runner unless coverage evidence requires it.
---
## 2026-06-11 20:09 +08:00 - US-010
- Files changed: `scripts/ralph/investigations/2026-06-11-US-010-validation-profile-wiring.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-010 validation profile wiring evidence` replaces implicit trust in `formula-parity` / `calculator-reads` coverage with recorded runner source, CodeGraph, import introspection, and `formula-parity` exit-0 evidence.
  - This story verifies an existing boundary only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, or change legacy compatibility paths.
- Compatibility retained:
  - `scripts/run_buff_refactor_validation.py` remains unchanged; existing `formula-parity` and `calculator-reads` profile maps already cover `zsim/sim_progress/ScheduledEvent/Calculator.py` and `tests/simulator/test_buff_attribute_reader.py`.
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this runner-verification story found no new Buff coupling.
- Next step:
  - Continue with US-011 by deciding registered behavior sample eligibility separately from validation profile wiring.
---
## 2026-06-11 20:18 +08:00 - US-011
- Files changed: `scripts/ralph/investigations/2026-06-11-US-011-registered-sample-eligibility.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-011 registered sample eligibility packet` replaces implicit main-loop sample judgment with an explicit rule: run `scripts/run_buff_main_loop_consistency.py` only when a story changes live formula semantics and a real registered route shows nonzero relevant event counts.
  - This story records a decision boundary only; it does not replace live production formula code, add validation-only teams, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, or change legacy compatibility paths.
- Compatibility retained:
  - `scripts/run_buff_main_loop_consistency.py` remains available as a live-behavior comparison tool for future eligible production changes.
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this decision-only story found no new Buff coupling.
- Next step:
  - Continue with US-012 by running serial `formula-parity` and `calculator-reads` gates while still skipping main-loop consistency unless a live semantic diff appears.
---
## 2026-06-11 20:30 +08:00 - US-012
- Files changed: `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-012 serial validation evidence` replaces implicit handoff trust with recorded exit-0 evidence for the focused reader suite, `formula-parity`, and `calculator-reads`.
  - This story is validation evidence only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - `implicit-events`, default lifecycle validation, and main-loop consistency remain conditional gates; US-012 did not run them because no live formula semantics, dispatch/runtime boundaries, or registered-team behavior changed.
  - No old-coupling review update was needed because this validation-only story found no new Buff coupling.
- Next step:
  - Continue with US-013 by updating final handoff docs and deciding the next bounded candidate using the Buff architecture route and current evidence ledger.
---
## 2026-06-11 20:58 +08:00 - US-013
- Files changed: `scripts/ralph/investigations/2026-06-11-US-013-final-handoff-next-candidate.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草稿.md`, `docs/Buff公式候选与测试目标清单.md`
- Replacement note:
  - `US-013 final handoff and next-candidate decision` replaces readiness-only AM/AP/impact wording with an evidence-backed decision that the family is ready for a bounded production proposal PRD.
  - This story updates handoff boundaries only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - `formula-parity` and `calculator-reads` are required serial gates for the next AM/AP/impact proposal; `implicit-events`, default lifecycle validation, and registered main-loop consistency remain conditional on event/runtime/lifecycle or live semantic scope.
  - No old-coupling review update was needed because this docs-only handoff found no new Buff coupling.
- Next step:
  - Generate the next PRD as a bounded AM/AP/impact production proposal, first choosing exact helper scope, rollback anchors, validation profiles, registered-sample conditions, retained boundaries, and non-goals before any implementation story changes production formulas.
---
## 2026-06-12 12:34 +08:00 - US-001
- Files changed: `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/architecture/invariants.md`, `scripts/ralph/plans/slices/us-001-reconfirm-proposal-only-scope-and-controller-state.md`, `scripts/ralph/plans/slices/us-002-map-am-evidence-to-proposal-prerequisites.md`, `scripts/ralph/investigations/2026-06-12-US-001-am-ap-impact-proposal-only-scope.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 proposal-only scope packet` replaces implicit reliance on the previous oracle-gap handoff with an explicit baseline: the current AM/AP/impact PRD is proposal-only and does not implement production formula replacement.
  - This story builds a boundary/evidence baseline only; it does not replace a live formula, copied-output constructor, validation runner, dispatch adapter, runtime command port, old Buff container, or legacy compatibility path.
- Compatibility retained:
  - `cal_res_pen()` remains completed and is not reopened by this PRD.
  - P2-A through P2-G remain guarded maintenance only.
  - `Calculator.py`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied-output constructors, old containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this proposal-scope story found no new Buff coupling.
- Next step:
  - Continue with US-002 by mapping AM evidence to proposal prerequisites without changing production formula code.
---
## 2026-06-12 12:50 +08:00 - US-002
- Files changed: `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-002-map-am-evidence-to-proposal-prerequisites.md`, `scripts/ralph/plans/slices/us-003-map-ap-evidence-to-proposal-prerequisites.md`, `scripts/ralph/investigations/2026-06-12-US-002-am-evidence-proposal-prerequisites.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 AM proposal prerequisite packet` replaces implicit reuse of prior AM oracle/readiness artifacts with an explicit proposal contract map for `Calculator.AnomalyMul.cal_am()`, `_calculate_anomaly_mastery(...)`, `CalculatorBuffAttributeReader.read_anomaly_mastery(...)`, and `test_cal_am_retained_multiplier_data_oracle_rows()`.
  - This story builds a boundary/evidence contract only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()` remains unchanged and still routes through `_calculate_anomaly_mastery(...)`.
  - `CalculatorBuffAttributeReader.read_anomaly_mastery(...)`, reader-built `_build_formula_snapshot(context)`, `MultiplierData`, `MulData`, `DynamicStatement`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this proposal-prerequisite story found no new Buff coupling.
- Next step:
  - Continue with US-003 by mapping AP evidence to the same proposal prerequisite standard and confirming the AM/AP shared helper-family contract before drafting production scope.
---
## 2026-06-12 13:08 +08:00 - US-003
- Files changed: `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-003-map-ap-evidence-to-proposal-prerequisites.md`, `scripts/ralph/investigations/2026-06-12-US-003-ap-evidence-proposal-prerequisites.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 AP proposal prerequisite packet` replaces implicit reuse of prior AP oracle/readiness artifacts with an explicit proposal contract map for `Calculator.AnomalyMul.cal_ap()`, `_calculate_anomaly_proficiency(...)`, `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)`, and `test_cal_ap_retained_multiplier_data_oracle_rows()`.
  - This story builds a boundary/evidence contract only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_ap()` remains unchanged and still directly computes the retained AP expression while the reader path delegates to `_calculate_anomaly_proficiency(...)`.
  - Root-only alias-qualified AP consumers in `CalAnomaly.py`, `VivianCinema6Trigger.py`, and `VivianCorePassiveTrigger.py` remain retained compatibility / future proposal risk surfaces.
  - `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)`, reader-built `_build_formula_snapshot(context)`, `MultiplierData`, `MulData`, `DynamicStatement`, `Calculator.AnomalyMul.cal_am()`, `Calculator.StunMul.cal_imp()`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this proposal-prerequisite story found no new Buff coupling.
- Next step:
  - Continue with US-004 by mapping impact evidence and keeping array-output / copied-output behavior out of the bounded production proposal unless a separate later slice supplies its own evidence and validation contract.
---
## 2026-06-12 13:22 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-map-impact-evidence-and-keep-array-outputs-out-of-scope.md`, `scripts/ralph/investigations/2026-06-12-US-004-impact-evidence-array-scope.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 impact proposal prerequisite packet` replaces implicit reuse of prior impact oracle/readiness artifacts with an explicit proposal contract map for `Calculator.StunMul.cal_imp()`, `CalculatorBuffAttributeReader.read_impact(...)`, `test_cal_imp_retained_multiplier_data_oracle_rows()`, P2-B guardrail coverage, and array-output exclusion.
  - This story builds a boundary/evidence contract only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.StunMul.cal_imp()` remains unchanged and still computes `static.imp * (1 + field_imp_percentage) + imp` through retained `MultiplierData` / `DynamicStatement` inputs.
  - `Calculator.StunMul.get_stun_array()`, `Calculator.cal_stun()`, stun ratio/res/bonus/received helpers, copied-output constructors, registered behavior samples, and broader StunMul formula work remain same-phase formula oracle candidates outside this AM/AP/impact proposal default scope.
  - `CalculatorBuffAttributeReader.read_impact(...)`, reader-built `_build_formula_snapshot(context)`, P2-B exact-file guardrails, `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `CalAnomaly.py`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this proposal-prerequisite story found no new Buff coupling.
- Next step:
  - Continue with US-005 by drafting the bounded AM/AP/impact production proposal, including impact scalar as an explicit reviewed candidate while excluding `get_stun_array()` / array outputs unless a separate oracle, validation, registered-sample, and rollback contract is written.
---
## 2026-06-12 13:40 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-draft-the-bounded-am-ap-impact-production-proposal.md`, `scripts/ralph/investigations/2026-06-12-US-005-bounded-am-ap-impact-production-proposal.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 bounded AM/AP/impact production proposal` replaces broad readiness wording with an exact scalar helper-family proposal: AM remains the already-converged baseline, AP may converge to `_calculate_anomaly_proficiency(...)`, and impact may add a scalar `_calculate_impact(...)` helper.
  - This story builds a proposal boundary only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_res_pen()`, `CalAnomaly.py`, Vivian AP callsites, copied-output constructors, `AnomalyBar.current_ndarray`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and P2-A through P2-G guarded buckets remain retained compatibility / non-goal paths.
  - `Calculator.StunMul.get_stun_array()`, `Calculator.cal_stun()`, stun ratio/res/bonus/received helpers, array outputs, registered behavior samples, and broader StunMul formula work remain outside this proposal's default production diff.
  - No old-coupling review update was needed because this proposal-only story found no new Buff coupling.
- Next step:
  - Continue with US-006 by defining the serial validation, registered-sample eligibility, and rollback contract before any implementation PRD changes production formula code.
---
## 2026-06-12 13:53 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-define-validation-registered-sample-and-rollback-contract.md`, `scripts/ralph/investigations/2026-06-12-US-006-validation-registered-sample-rollback-contract.md`, `scripts/ralph/investigations/2026-06-12-US-005-bounded-am-ap-impact-production-proposal.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 validation / registered-sample / rollback contract` replaces implicit follow-up validation assumptions with an explicit implementation-prerequisite contract for scalar AM/AP/impact production work.
  - This story builds a contract boundary only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, create registered-team fixtures, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.StunMul.cal_imp()`, `CalAnomaly.py`, Vivian AP callsites, copied-output constructors, `AnomalyBar.current_ndarray`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and P2-A through P2-G guarded buckets remain retained compatibility / non-goal paths.
  - Future implementation must run focused pytest plus serial `formula-parity` and `calculator-reads`; `implicit-events`, default lifecycle validation, validation-runner help/runner tests, and main-loop consistency samples remain conditional and require explicit skip rationale.
  - No old-coupling review update was needed because this contract-only story found no new Buff coupling.
- Next step:
  - Continue with US-007 by updating final handoff docs and deciding proposal Go / No-Go without collapsing the same-phase candidate pool to only one narrow follow-up.
---
## 2026-06-12 14:13 +08:00 - US-007
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-007-update-handoff-docs-and-final-proposal-go-no-go.md`, `scripts/ralph/plans/slices/buff-refactor-phase3-am-ap-impact-bounded-production-proposal-next-intake.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-007 final proposal Go / No-Go handoff` replaces proposal-ready wording with a bounded implementation authorization for the scalar AM/AP/impact helper family only.
  - This story updates handoff boundaries only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, create registered-team fixtures, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - Later implementation scope is limited to `Calculator.py`: keep AM as the helper-backed baseline, allow AP helper convergence through `_calculate_anomaly_proficiency(...)`, and allow scalar `_calculate_impact(...)` plus `Calculator.StunMul.cal_imp()` delegation.
  - `Calculator.StunMul.get_stun_array()` / array outputs, `Calculator.RegularMul` remaining branches, copied-output handler/report payload parity, registered-team behavior samples, P2-A through P2-G guarded maintenance, old containers, legacy `buff_add()`, legacy `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, `MultiplierData`, `MulData`, `DynamicStatement`, copied-output constructors, and retained formula snapshots remain retained compatibility / future candidate surfaces.
  - No old-coupling review update was needed because this docs-only final handoff found no new Buff coupling.
- Next step:
  - Generate the next PRD as a bounded AM/AP/impact production implementation, with focused tests plus serial `formula-parity` and `calculator-reads`; run conditional gates only if the implementation touches their boundaries.
---
## 2026-06-12 15:33 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-implementation-scope-and-baseline.md`, `scripts/ralph/plans/slices/us-002-converge-ap-to-the-scalar-proficiency-helper.md`, `scripts/ralph/investigations/2026-06-12-US-001-reconfirm-implementation-scope-baseline.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 implementation scope and baseline packet` replaces chat-only scope assumptions with retained Ralph evidence for the bounded AM/AP/impact production implementation PRD.
  - This story builds a boundary and validation baseline only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_am()` remains the helper-backed baseline; `Calculator.AnomalyMul.cal_ap()` and `Calculator.StunMul.cal_imp()` remain later bounded implementation candidates.
  - `Calculator.AnomalyMul.cal_res_pen()`, `anomaly_snapshot`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, `MultiplierData`, `MulData`, `DynamicStatement`, and validation runner wiring remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this baseline-only story found no new Buff coupling.
- Next step:
  - Continue with US-002 by converging only `Calculator.AnomalyMul.cal_ap()` to `_calculate_anomaly_proficiency(...)`, with focused tests and serial `formula-parity`, without touching the retained exclusion list.
---
## 2026-06-12 15:54 +08:00 - US-002
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-002-converge-ap-to-the-scalar-proficiency-helper.md`, `scripts/ralph/plans/slices/us-003-extract-scalar-impact-calculation.md`, `scripts/ralph/investigations/2026-06-12-US-002-ap-helper-convergence.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `Calculator.AnomalyMul.cal_ap()` now delegates to `_calculate_anomaly_proficiency(data.static, data.dynamic)`, replacing the duplicate in-method AP scalar expression while preserving the public one-argument helper and `@lru_cache(maxsize=16)`.
  - `test_cal_ap_delegates_to_scalar_proficiency_helper_and_keeps_cache()` replaces implicit AP helper-convergence/cache assumptions with executable focused coverage.
- Compatibility retained:
  - Existing AP retained `MultiplierData` oracle rows, reader-built snapshot parity, and `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)` parity remain intact.
  - `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_res_pen()`, `anomaly_snapshot`, `CalAnomaly.py`, Vivian AP callsites, copied-output constructors, `AnomalyBar.current_ndarray`, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, validation runner wiring, and P2-A through P2-G guarded buckets remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this slice found no new Buff coupling.
- Next step:
  - Continue with US-003 by extracting only the scalar impact helper in `Calculator.py`, while keeping `StunMul.get_stun_array()` / array outputs and broader StunMul behavior out of scope.
---
## 2026-06-12 16:13 +08:00 - US-003
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-003-extract-scalar-impact-calculation.md`, `scripts/ralph/investigations/2026-06-12-US-003-impact-helper-extraction.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `Calculator.StunMul.cal_imp()` now delegates to `_calculate_impact(data.static, data.dynamic)`, replacing the duplicate in-method impact scalar expression while preserving the public one-argument helper and existing uncached behavior.
  - `test_cal_imp_delegates_to_scalar_impact_helper_and_remains_uncached()` replaces implicit impact helper-extraction/cache assumptions with executable focused coverage.
- Compatibility retained:
  - Existing impact retained `MultiplierData` oracle rows, reader-built snapshot parity, and `CalculatorBuffAttributeReader.read_impact(...)` parity remain intact.
  - `Calculator.StunMul.get_stun_array()`, `Calculator.cal_stun()`, stun ratio/res/bonus/received helpers, `Calculator.AnomalyMul.cal_am()`, `Calculator.AnomalyMul.cal_ap()`, `Calculator.AnomalyMul.cal_res_pen()`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, validation runner wiring, registered samples, and P2-A through P2-G guarded buckets remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this slice found no new Buff coupling.
- Next step:
  - Continue with US-004 by proving family compatibility and rollback anchors with serial `formula-parity` and `calculator-reads`, without reopening the retained exclusion list.
---
## 2026-06-12 16:24 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-004-preserve-family-compatibility-and-rollback-anchors.md`, `scripts/ralph/plans/slices/us-005-decide-conditional-runtime-event-and-registered-sample-gates.md`, `scripts/ralph/investigations/2026-06-12-US-004-family-compatibility-rollback-anchors.md`, `scripts/ralph/checkpoints/2026-06-12-us-004-family-compatibility-rollback-anchors.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_calculator_am_ap_impact_formula_boundaries_remain_retained_compatibility()` now replaces implicit family rollback assumptions with explicit proof of retained `MultiplierData`, reader snapshot structural compatibility, `MultiplierData.DynamicStatement` translated fields, and `CalculatorBuffAttributeReader` parity for AM, AP, and impact.
  - This story strengthens a test/evidence boundary only; it does not replace live production formula code, edit the validation runner, add a dispatch adapter, alter a runtime command port, delete old Buff containers, create registered-team fixtures, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.RegularMul`, `Calculator.StunMul.get_stun_array()`, copied-output handler/report payloads, registered samples, dispatch/runtime ports, old Buff containers, validation-runner wiring, `CalAnomaly.py`, and broad formula replacement remain retained compatibility / follow-up surfaces.
  - Serial `formula-parity` and `calculator-reads` passed after the boundary test correction; known pytest-asyncio and async log-writer shutdown noise remains separated from verifier failure.
  - No old-coupling review update was needed because this proof slice found no new Buff coupling.
- Next step:
  - Continue with US-005 by deciding conditional runtime, event, implicit-events, default lifecycle, validation-runner help, and registered-sample gates based only on touched surfaces.
---
## 2026-06-12 16:39 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-decide-conditional-runtime-event-and-registered-sample-gates.md`, `scripts/ralph/investigations/2026-06-12-US-005-conditional-validation-gates.md`, `scripts/ralph/checkpoints/2026-06-12-us-005-conditional-validation-gates.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-006-final-serial-verification-and-invariant-review.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 conditional validation gate decision` replaces implicit follow-up assumptions about `implicit-events`, default lifecycle validation, and registered main-loop samples with a touched-surface decision matrix.
  - This story builds a decision/checkpoint boundary only; it does not replace live production formula code, edit validation-runner wiring, add a dispatch adapter, alter a runtime command port, touch lifecycle containers, create registered-team fixtures, or replace copied-output constructors.
- Compatibility retained:
  - Validation runner wiring, `ScheduleDispatchPort`, `RuntimeCommandPort`, lifecycle containers, old Buff containers, copied-output handler/report payloads, registered samples, and live production formula behavior remain untouched.
  - `implicit-events`, default lifecycle validation, and `run_buff_main_loop_consistency.py` remain conditional future gates: run them when a later slice touches the matching event/runtime/lifecycle/semantic surface and use only real registered routes with nonzero relevant evidence.
  - No old-coupling review update was needed because this decision-only slice found no new Buff coupling.
- Next step:
  - Continue with US-006 by running the final serial verification and invariant review, reusing this US-005 skip rationale for conditional event/runtime/main-loop gates unless US-006 uncovers new touched-surface evidence.
---
## 2026-06-12 16:56 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-final-serial-verification-and-invariant-review.md`, `scripts/ralph/plans/slices/us-007-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/investigations/2026-06-12-US-006-final-serial-verification.md`, `scripts/ralph/checkpoints/2026-06-12-us-006-final-serial-verification-invariant-review.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 final serial verification and invariant review` replaces chat-only final-gate confidence with recorded verifier evidence: focused reader pytest, serial `formula-parity`, serial `calculator-reads`, an infrastructure checkpoint, and a reviewer verdict against Ralph/Buff invariants.
  - This story builds a validation/evidence boundary only; it does not replace live production formula code, edit validation-runner wiring, add a dispatch adapter, alter a runtime command port, touch lifecycle containers, create registered-team fixtures, or replace copied-output constructors.
- Compatibility retained:
  - `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.RegularMul`, `Calculator.StunMul.get_stun_array()`, `CalAnomaly.py`, copied-output handler/report payloads, registered samples, old Buff containers, validation-runner wiring, event/dispatch/runtime boundaries, and broad formula replacement remain retained compatibility / future candidate surfaces.
  - `implicit-events`, default lifecycle validation, and main-loop consistency remain conditional future gates tied to actual event/runtime/lifecycle/semantic touch points; this slice skipped them by US-005 touched-surface evidence and its own docs/evidence-only diff.
  - No old-coupling review update was needed because this final-verification story found no new Buff coupling.
- Next step:
  - Continue with US-007 by updating final handoff docs and same-phase candidate pools without collapsing the next-stage plan to only the immediate successor.
---
## 2026-06-12 17:12 +08:00 - US-007
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-007-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/plans/slices/buff-refactor-phase3-am-ap-impact-bounded-production-implementation-next-intake.md`, `scripts/ralph/checkpoints/2026-06-12-us-007-final-handoff-same-phase-candidate-pool.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-007 final handoff docs and same-phase candidate pool` replaces chat-only implementation completion state with documented checklist, next-stage plan, formula-candidate, replacement-note, checkpoint, campaign, and evidence-ledger records.
  - This story builds a documentation and handoff boundary only; it does not replace live production formula code, validation-runner wiring, dispatch/runtime ports, copied-output constructors, old containers, or registered-team fixtures.
- Compatibility retained:
  - AM/AP/impact bounded implementation remains complete; `Calculator.AnomalyMul.cal_res_pen()`, `Calculator.StunMul.get_stun_array()` / array outputs, `Calculator.RegularMul` remaining branches, `CalAnomaly.py`, copied-output handler/report payloads, registered samples, old Buff containers, validation-runner wiring, event/dispatch/runtime boundaries, and broad formula replacement remain retained compatibility / future candidate surfaces.
  - `docs/旧Buff系统耦合审查结果.md` sections `6.6` through `6.9` remain current because this docs-only story did not change runtime, event, Calculator, or validation boundaries.
- Next step:
  - Generate the next Phase-3 PRD from the remaining formula/candidate pool, defaulting to `Calculator.StunMul.get_stun_array()` / array output oracle work or one exact `Calculator.RegularMul` branch while preserving copied-output, registered-route, and P2-A through P2-G guarded-maintenance candidates.
---
## 2026-06-12 17:47 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-array-regularmul-scope-and-baseline.md`, `scripts/ralph/investigations/2026-06-12-US-001-array-regularmul-scope-baseline.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 array / RegularMul scope baseline packet` replaces chat-only Phase-3 scope assumptions with cited docs, CodeGraph source evidence, focused test inventory, verifier evidence, and a next-slice recommendation.
  - This story builds a boundary and validation baseline only; it does not replace live production formula code, edit validation-runner wiring, add a dispatch adapter, alter a runtime command port, delete old Buff containers, replace copied-output constructors, or change legacy compatibility paths.
- Compatibility retained:
  - `Calculator.StunMul.get_stun_array()`, `Calculator.cal_stun()`, and `Calculator.RegularMul` array builders remain retained production code and future characterization targets.
  - `Calculator.AnomalyMul.cal_res_pen()`, AM/AP/impact helper implementation, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and validation runner wiring remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this baseline-only story found no new Buff coupling.
- Next step:
  - Continue with US-002 by adding direct `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` characterization for shape, dtype, order, and product semantics before any RegularMul or production replacement work.
---
## 2026-06-12 18:00 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-002-characterize-stun-array-output-contract.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/context/index.md`, `scripts/ralph/context/codegraph-guide.md`, `scripts/ralph/context/progress-snapshot.md`, `scripts/ralph/context/module-boundaries.md`, `scripts/ralph/context/dependency-graph.md`, `scripts/ralph/context/call-chain-graph.md`, `scripts/ralph/plans/slices/us-003-characterize-regularmul-array-output-boundaries.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_stun_array_output_contract_preserves_field_order_dtype_and_product()` replaces implicit trust in `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array semantics with executable retained `MultiplierData` oracle coverage for five-field order, shape, `np.float64` dtype, and product consumption.
  - This story strengthens a test/evidence boundary only; it does not replace live production formula code, introduce a reader-built Stun array API, edit validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `Calculator.py`, `Calculator.RegularMul` array outputs, `Calculator.AnomalyMul.cal_res_pen()`, AM/AP/impact helper implementation, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and validation-runner wiring remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test-only slice discovered no new Buff coupling.
- Next step:
  - Continue with US-003 by applying the direct array-contract characterization pattern to `Calculator.RegularMul.get_array_expect()`, `get_array_crit()`, and `get_array_not_crit()` without changing production array construction unless a focused failing test proves a defect.
---
## 2026-06-12 18:22 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-003-characterize-regularmul-array-output-boundaries.md`, `scripts/ralph/investigations/2026-06-12-US-003-regularmul-array-fixture.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-004-characterize-regularmul-formula-branches.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_regular_mul_array_outputs_preserve_field_order_dtype_and_crit_split()` replaces implicit trust in `Calculator.RegularMul.get_array_expect()`, `get_array_crit()`, and `get_array_not_crit()` array semantics with executable retained `MultiplierData` oracle coverage for nine-field order, shape, `np.float64` dtype, explicit component mapping, divergent crit-slot semantics, and shared multiplier equality.
  - This story strengthens a test/evidence boundary only; it does not replace live production formula code, introduce a reader-built RegularMul array API, edit validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `Calculator.py`, production `Calculator.RegularMul` array construction, `Calculator.StunMul.get_stun_array()`, `Calculator.AnomalyMul.cal_res_pen()`, AM/AP/impact helper implementation, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and validation-runner wiring remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this test/fixture/evidence slice discovered no new Buff coupling.
- Next step:
  - Continue with US-004 by characterizing bounded `Calculator.RegularMul` branch formulas and rollback anchors without re-proving direct array order/dtype/component mapping.
---
## 2026-06-12 18:42 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-004-characterize-regularmul-formula-branches.md`, `scripts/ralph/plans/slices/us-005-decide-proposal-readiness-and-conditional-gates.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_calculator_regular_mul_branch_matrix_characterizes_selected_methods()` replaces implicit RegularMul branch confidence with executable retained `MultiplierData` oracle coverage for direct damage, crit, defense, resistance, damage vulnerability, stun vulnerability, special multiplier, and sheer damage bonus.
  - This story strengthens a test/evidence boundary only; it does not replace live production formula code, add reader APIs, edit validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - Production `Calculator.RegularMul` methods, `CalculatorBuffAttributeReader` public methods, `MultiplierData`, `DynamicStatement`, `Calculator.StunMul.get_stun_array()`, copied-output constructors, old Buff containers, dispatch/runtime ports, listener paths, same-tick runtime writes, and validation-runner wiring remain untouched.
  - Reader-snapshot parity is proven for the non-sheer branch matrix row; the sheer branch remains retained-only because the current reader snapshot does not carry `char_instance`, which `cal_base_attr(..., base_attr=4)` requires for `sheer_attack_conversion_rate`.
  - No old-coupling review update was needed because this test-only slice found no new Buff coupling.
- Next step:
  - Continue with US-005 by deciding proposal readiness and conditional gates from the now-covered Stun array, RegularMul array, and RegularMul branch evidence without changing production formulas.
---
## 2026-06-12 18:57 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-decide-proposal-readiness-and-conditional-gates.md`, `scripts/ralph/investigations/2026-06-12-US-005-array-regularmul-proposal-readiness.md`, `scripts/ralph/checkpoints/2026-06-12-us-005-array-regularmul-proposal-readiness.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 array / RegularMul proposal readiness packet` replaces implicit production-proposal readiness assumptions with a source-backed No-Go decision and conditional gate matrix.
  - This story builds a decision/checkpoint boundary only; it does not replace live production formula code, edit validation-runner wiring, add a dispatch adapter, alter a runtime command port, touch lifecycle containers, create registered-team fixtures, or replace copied-output constructors.
- Compatibility retained:
  - `Calculator.py`, `Calculator.RegularMul`, `Calculator.StunMul.get_stun_array()`, `Calculator.cal_stun()`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and validation-runner wiring remain untouched.
  - `implicit-events`, default lifecycle validation, and `run_buff_main_loop_consistency.py` remain conditional future gates because this slice touched no copied-output, event, dispatch, runtime, listener, same-tick write, lifecycle, validation wiring, production semantic diff, or registered route with nonzero relevant counts.
  - No old-coupling review update was needed because this decision-only slice found no new Buff coupling.
- Next step:
  - Continue with US-006 final serial verification and invariant review; do not promote array / RegularMul production replacement unless a later packet names one exact candidate with deterministic oracle, rollback anchors, and registered-sample conditions.
---
## 2026-06-12 19:12 +08:00 - US-006
- Files changed: `scripts/ralph/investigations/2026-06-12-US-006-final-serial-verification.md`, `scripts/ralph/checkpoints/2026-06-12-us-006-final-serial-verification-invariant-review.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 final serial verification and invariant review` replaces chat-only final-gate confidence for the current array / RegularMul PRD with recorded focused pytest, serial `formula-parity`, serial `calculator-reads`, checkpoint, and reviewer-verdict evidence.
  - This story builds a validation/evidence boundary only; it does not replace live production formula code, edit validation-runner wiring, add dispatch/runtime adapters, touch lifecycle containers, create registered-team fixtures, or replace copied-output constructors.
- Compatibility retained:
  - `Calculator.py`, `Calculator.RegularMul`, `Calculator.StunMul.get_stun_array()`, `Calculator.cal_stun()`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, and validation-runner wiring remain untouched.
  - `implicit-events`, default lifecycle validation, and `run_buff_main_loop_consistency.py` remain conditional future gates because neither US-005 nor US-006 touched copied-output, event, dispatch, runtime, listener, same-tick write, lifecycle, validation wiring, production semantic diff, or a registered route with nonzero relevant counts.
  - No old-coupling review update was needed because this final-verification story found no new Buff coupling.
- Next step:
  - Continue with US-007 by updating final handoff docs and same-phase candidate pools without collapsing the next-stage plan to only one narrow follow-up.
---
## 2026-06-12 19:30 +08:00 - US-007
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/checkpoints/2026-06-12-us-007-final-handoff-same-phase-candidate-pool.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-007 final handoff docs and same-phase candidate pool` replaces incomplete handoff state for the current array / RegularMul PRD with long-lived checklist, next-stage plan, formula-candidate, replacement-note, checkpoint, campaign, evidence-ledger, PRD, and progress records.
  - This story builds a documentation and handoff boundary only; it does not replace live production formula code, validation-runner wiring, dispatch/runtime ports, copied-output constructors, old containers, registered-team fixtures, listener broadcasts, or same-tick runtime writes.
- Compatibility retained:
  - Stun array, RegularMul arrays, and selected RegularMul branches remain characterization evidence; production proposal remains No-Go for this PRD.
  - `Calculator.py`, `CalAnomaly.py`, `Calculator.AnomalyMul.cal_res_pen()`, AM/AP/impact helper implementation, `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied-output constructors, old Buff containers, validation-runner wiring, event/dispatch/runtime boundaries, registered-team behavior samples, and broad formula replacement remain retained compatibility / future candidate surfaces.
  - `docs/旧Buff系统耦合审查结果.md` sections `6.6` through `6.9` remain current because this docs-only story did not change runtime, event, Calculator production, validation, or copied-output boundaries.
- Next step:
  - Generate the next Phase-3 characterization / proposal-readiness continuation PRD from the broad same-phase pool, choosing one exact candidate such as copied-output handler/report payload parity, registered-team behavior sample eligibility, a remaining `Calculator.RegularMul` / retained-only sheer follow-up, or a named `Calculator.StunMul.get_stun_array()` follow-up while preserving P2-A through P2-G guarded maintenance.
---
## 2026-06-12 22:08 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-sheer-scope-and-baseline.md`, `scripts/ralph/investigations/2026-06-12-US-001-sheer-scope-baseline.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 sheer scope and baseline packet` replaces chat-only retained-only sheer assumptions with cited docs, targeted `rg`, CodeGraph source evidence, focused test inventory, verifier evidence, and a next-slice recommendation.
  - This story builds a boundary/readiness packet only; it does not replace live production formula code, introduce a reader-built sheer API, edit validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `cal_sheer_dmg_bonus()` remains retained production behavior; `cal_base_attr(..., base_attr=4)` remains retained-only because it depends on runtime `char_instance.sheer_attack_conversion_rate`, while `_CalculatorReadSnapshot` currently carries no `char_instance`.
  - `Calculator.py`, production `Calculator.RegularMul`, `CalculatorBuffAttributeReader`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, completed AM/AP/impact work, `cal_res_pen()`, and validation-runner wiring remain retained compatibility / non-goal paths.
  - No old-coupling review update was needed because this evidence-only slice found no new Buff coupling.
- Next step:
  - Continue with US-002 by directly characterizing the retained `base_attr=4` sheer runtime dependency and deciding whether a reader snapshot may carry `char_instance` before any production formula replacement.
---
## 2026-06-12 22:25 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-002-characterize-retained-sheer-runtime-dependency.md`, `scripts/ralph/plans/slices/us-003-decide-reader-snapshot-eligibility.md`, `scripts/ralph/checkpoints/2026-06-12-us-002-regularmul-sheer-runtime-dependency.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_regular_mul_retained_sheer_base_attr_requires_char_instance_conversion_rate()` replaces implicit retained-only sheer conversion confidence with executable `Calculator.RegularMul.cal_base_attr(..., base_attr=4)` oracle coverage and an explicit current reader-snapshot No-Go.
  - This story strengthens a test/evidence boundary only; it does not replace live production formula code, add a reader method, extend `_CalculatorReadSnapshot`, edit validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `Calculator.py`, production `Calculator.RegularMul`, `CalculatorBuffAttributeReader` public methods, `_CalculatorReadSnapshot`, `MultiplierData`, `DynamicStatement`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, completed AM/AP/impact work, `cal_res_pen()`, and validation-runner wiring remain untouched.
  - `cal_base_attr(..., base_attr=4)` remains retained-only because it needs runtime `char_instance.sheer_attack_conversion_rate`; current reader-built snapshots still cannot represent that path.
  - No old-coupling review update was needed because this test-only slice found no new Buff coupling.
- Next step:
  - Continue with US-003 by deciding whether `_CalculatorReadSnapshot` may carry `char_instance` under a bounded oracle/rollback plan or by recording a No-Go without production formula replacement.
---
## 2026-06-12 22:38 +08:00 - US-003
- Files changed: `scripts/ralph/plans/slices/us-003-decide-reader-snapshot-eligibility.md`, `scripts/ralph/investigations/2026-06-12-US-003-reader-snapshot-eligibility.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 reader snapshot eligibility packet` replaces implicit hopes for carrying retained sheer conversion through reader-built snapshots with a recorded No-Go decision.
  - This story builds a decision/evidence boundary only; it does not replace a live production path, add a snapshot field, edit validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, create registered-team fixtures, or touch copied-output constructors.
- Compatibility retained:
  - `_CalculatorReadSnapshot` remains a five-field minimal compatibility object with `static`, `dynamic`, `judge_node`, `enemy_obj`, and `char_level`.
  - `cal_base_attr(..., base_attr=4)` remains retained-only because it requires runtime `char_instance.sheer_attack_conversion_rate`; `cal_sheer_dmg_bonus()` remains reader-snapshot-compatible.
  - `Calculator.py`, production `Calculator.RegularMul`, `CalculatorBuffAttributeReader`, `MultiplierData`, `DynamicStatement`, `CalAnomaly.py`, copied-output constructors, old Buff containers, dispatch/runtime/listener paths, same-tick runtime writes, and validation-runner wiring remain untouched.
  - No old-coupling review update was needed because this decision-only slice found no new Buff coupling.
- Next step:
  - Continue with US-004 by defining registered-route sample conditions for any later sheer production proposal; do not authorize production formula replacement from this No-Go.
---
## 2026-06-12 22:49 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-define-registered-route-sample-conditions.md`, `scripts/ralph/investigations/2026-06-12-US-004-registered-route-sample-conditions.md`, `scripts/ralph/checkpoints/2026-06-12-us-004-registered-route-sample-conditions.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 registered-route sample-condition packet` replaces implicit main-loop sample eligibility for retained sheer conversion with a recorded conditional No-Go and future sample gate.
  - This story builds an evidence/checkpoint boundary only; it does not replace a live production path, add a registered-team fixture, edit APL data, change validation-runner wiring, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - Current registered teams remain `青衣雷属性队`, `席德大安比队`, `莱特火属性队`, and `薇薇安物理队`; none include `仪玄` / `Yixuan`, so no real registered sheer sample is available in this slice.
  - Future sheer main-loop samples must use an existing registered production team and prove nonzero `event_counts.by_element_type["4"]` plus exact route evidence in both snapshots; no validation-only team should be created to satisfy the gate.
  - `Calculator.py`, production `Calculator.RegularMul`, `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, `MultiplierData`, `DynamicStatement`, `CalAnomaly.py`, copied-output constructors, old Buff containers, dispatch/runtime/listener paths, same-tick runtime writes, and validation-runner wiring remain untouched.
  - No old-coupling review update was needed because this evidence-only slice found no new Buff coupling.
- Next step:
  - Continue with US-005 by deciding proposal readiness and conditional gates from this registered-route No-Go; do not authorize production formula replacement without a real registered sheer route, production semantic diff, nonzero counts, and rollback anchors.
---
## 2026-06-12 23:14 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-proposal-readiness-and-conditional-gates.md`, `scripts/ralph/investigations/2026-06-12-US-005-regularmul-sheer-proposal-readiness.md`, `scripts/ralph/checkpoints/2026-06-12-us-005-regularmul-sheer-proposal-readiness.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 regularmul-sheer proposal-readiness packet` replaces chat-only production-readiness assumptions with a recorded No-Go decision, retained verifier evidence, rollback anchors, and the missing registered-route / reader-contract blockers.
  - This story builds a readiness/evidence boundary only; it does not replace live production formula code, add a reader-built sheer API, extend `_CalculatorReadSnapshot`, edit validation-runner wiring, create registered-team fixtures, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `cal_base_attr(..., base_attr=4)` remains retained-only because it needs runtime `char_instance.sheer_attack_conversion_rate`; current reader-built snapshots still cannot represent that path without broadening the reader contract.
  - `Calculator.py`, production `Calculator.RegularMul`, `CalculatorBuffAttributeReader`, `_CalculatorReadSnapshot`, `MultiplierData`, `DynamicStatement`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, registered teams, and validation-runner wiring remain untouched.
  - No old-coupling review update was needed because this evidence-only slice found no new Buff coupling.
- Next step:
  - Continue with US-006 final serial verification and invariant review from the No-Go state; do not promote `RegularMul` sheer conversion to production proposal without real registered-route sample evidence and an architecture-approved reader-contract plan.
---
## 2026-06-12 23:32 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-final-serial-verification-and-invariant-review.md`, `scripts/ralph/checkpoints/2026-06-12-us-006-regularmul-sheer-final-serial-verification.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 final serial verification and invariant checkpoint` replaces incomplete verifier-state assumptions with serial focused pytest, `formula-parity`, `calculator-reads`, `implicit-events`, reviewer verdict, and checkpoint evidence.
  - This story builds a verification/evidence boundary only; it does not replace live production formula code, add a reader-built sheer API, extend `_CalculatorReadSnapshot`, edit validation-runner wiring, create registered-team fixtures, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `cal_base_attr(..., base_attr=4)` remains retained-only because it needs runtime `char_instance.sheer_attack_conversion_rate`; current reader-built snapshots still cannot represent that path without broadening the reader contract.
  - `Calculator.py`, production `Calculator.RegularMul`, `CalculatorBuffAttributeReader`, `_CalculatorReadSnapshot`, `MultiplierData`, `DynamicStatement`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, registered teams, and validation-runner wiring remain untouched.
  - No old-coupling review update was needed because this verifier-only slice found no new Buff coupling.
- Next step:
  - Continue with US-007 final handoff docs and same-phase candidate pool; preserve the broad Phase-3 candidate pool and do not collapse the next PRD to only `RegularMul` sheer conversion.
---
## 2026-06-12 23:47 +08:00 - US-007
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/checkpoints/2026-06-12-us-007-regularmul-sheer-final-handoff-candidate-pool.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/plans/slices/buff-refactor-phase3-regularmul-sheer-reader-snapshot-readiness-next-intake.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-007 final handoff docs and same-phase candidate pool` replaces the US-006 next-slice signal with long-lived docs, checkpoint, campaign, evidence-ledger, PRD and progress records for the RegularMul sheer reader-snapshot readiness PRD.
  - This story builds a documentation and handoff boundary only; it does not replace live production formula code, add a reader-built sheer API, extend `_CalculatorReadSnapshot`, edit validation-runner wiring, create registered-team fixtures, add dispatch/runtime adapters, alter listener broadcasts, delete old Buff containers, or touch copied-output constructors.
- Compatibility retained:
  - `Calculator.RegularMul.cal_base_attr(..., base_attr=4)` remains retained-only for runtime `char_instance.sheer_attack_conversion_rate`; `cal_sheer_dmg_bonus()` remains reader-snapshot-compatible for `diff_multiplier == 4`.
  - `Calculator.py`, production `Calculator.RegularMul`, `CalculatorBuffAttributeReader`, `_CalculatorReadSnapshot`, `MultiplierData`, `DynamicStatement`, `CalAnomaly.py`, copied-output constructors, old Buff containers, legacy `buff_add()`, legacy `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcasts, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, registered teams, and validation-runner wiring remain untouched.
- Next step:
  - Generate the next Phase-3 characterization / proposal-readiness continuation PRD from the broad same-phase pool; do not promote `RegularMul` sheer conversion to production proposal without real registered-route sample evidence and an architecture-approved reader-contract plan.
---
## 2026-06-13 13:38 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-copied-output-scope-and-source-inventory.md`, `scripts/ralph/investigations/2026-06-13-US-001-copied-output-scope-inventory.md`, `scripts/ralph/checkpoints/2026-06-13-us-001-copied-output-scope-inventory.md`, `scripts/ralph/plans/slices/us-002-lock-copied-payload-constructor-field-matrix.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 copied-output root source inventory packet` replaces stale or chat-only copied-output scope assumptions with a root-workspace scan, CodeGraph query evidence, focused target inventory, checkpoint, evidence-ledger, PRD, progress, and next-slice controller state.
  - This story builds a characterization / proposal-readiness boundary only; it does not replace live production formula code, copied-output constructors, event handlers, dispatch/runtime ports, listener broadcasts, same-tick runtime writes, validation-runner wiring, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Root source candidates are limited to `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, and the root anomaly/disorder/polarity-disorder/abloom handlers; old `.codex_worktrees/`, archives, logs, generated output, and run output remain excluded from the authoritative inventory.
  - Completed RegularMul / sheer / AM/AP/impact work and P2 guarded-maintenance compatibility remain separate; this PRD must continue as characterization / proposal-readiness until later stories provide exact payload and handler/report evidence.
  - No old-coupling review update was needed because this evidence-only slice found no new Buff coupling.
- Next step:
  - Continue with US-002 by locking copied payload constructor fields for `NewAnomaly`, `Disorder`, and `PolarityDisorder` without changing production formulas, copied-output constructors, event handlers, dispatch/runtime ports, or retained compatibility paths.
---
## 2026-06-13 13:58 +08:00 - US-002
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-002-lock-copied-payload-constructor-field-matrix.md`, `scripts/ralph/investigations/2026-06-13-US-002-copied-payload-constructor-matrix.md`, `scripts/ralph/checkpoints/2026-06-13-us-002-copied-payload-constructor-field-matrix.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 copied payload constructor field matrix` replaces implicit copied-output constructor assumptions with focused test evidence for `NewAnomaly`, `Disorder`, and `PolarityDisorder` field categories.
  - This story builds characterization coverage only; it does not replace live production constructors, formulas, event handlers, listener broadcasts, dispatch/runtime ports, old Buff containers, validation-runner wiring, or registered behavior samples.
- Compatibility retained:
  - `CopyAnomalyForOutput.py` remains unchanged. Copied-output constructors still deep-copy `AnomalyBar`, `Disorder` still sets `is_disorder`, and `PolarityDisorder` still owns `polarity_disorder_ratio` / `additional_dmg_ap_ratio`.
  - `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/polarity handler report paths, listener broadcasts, scheduled event queue semantics, same-tick runtime writes, old Buff containers, completed RegularMul / sheer / AM/AP/impact work, and P2 guarded-maintenance compatibility remain untouched.
  - No old-coupling review update was needed because this test-only slice found no new Buff coupling.
- Next step:
  - Continue with US-003 by characterizing `UpdateAnomaly.spawn_output(...)` listener boundaries from the locked constructor matrix without changing production event/runtime boundaries.
---
## 2026-06-13 14:07 +08:00 - US-003
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `scripts/ralph/plans/slices/us-003-characterize-updateanomaly-spawn-output-listener-boundaries.md`, `scripts/ralph/investigations/2026-06-13-US-003-spawn-output-listener-boundaries.md`, `scripts/ralph/checkpoints/2026-06-13-us-003-spawn-output-listener-boundaries.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 spawn_output listener-boundary characterization` replaces implicit assumptions about copied-output construction, synchronous listener broadcast, and scheduled publish separation with focused tests and checkpoint evidence.
  - This story builds characterization coverage only; it does not replace live production constructors, formulas, `UpdateAnomaly.py`, event handlers, listener manager implementation, dispatch/runtime ports, old Buff containers, validation-runner wiring, or registered behavior samples.
- Compatibility retained:
  - `spawn_output(...)` mode 0 still constructs `NewAnomaly` after source-bar settlement without direct listener broadcast or scheduled publish.
  - `spawn_output(...)` modes 1 and 2 still synchronously broadcast `LBS.DISORDER_SPAWN`; scheduled publishes remain owned by `update_anomaly(...)`.
  - Mode 2 missing `polarity_ratio` remains a `ValueError` path and now proves no listener broadcast, direct scheduled publish, or source-bar settlement occurs first.
  - No old-coupling review update was needed because this test-only slice found no new Buff coupling.
- Next step:
  - Continue with US-004 by characterizing handler/report payload parity for anomaly, disorder, polarity disorder, and abloom paths without changing constructors, event handlers, dispatch/runtime ports, listener broadcasts, or production formula semantics.
---
## 2026-06-13 14:40 +08:00 - US-004
- Files changed: `tests/simulator/test_anomaly_handler_runtime_view.py`, `scripts/ralph/plans/slices/us-004-characterize-handler-report-payload-parity.md`, `scripts/ralph/investigations/2026-06-13-US-004-handler-report-payload-parity.md`, `scripts/ralph/checkpoints/2026-06-13-us-004-handler-report-payload-parity.md`, `scripts/ralph/plans/slices/us-005-codify-registered-behavior-sample-eligibility.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 handler/report payload parity characterization` replaces implicit report/log-facing payload assumptions with a focused four-path inventory for anomaly, disorder, polarity disorder, and abloom copied-output handlers.
  - This story builds characterization coverage only; it does not replace live production constructors, formulas, `UpdateAnomaly.py`, scheduled event handlers, listener manager implementation, dispatch/runtime ports, old Buff containers, validation-runner wiring, or registered behavior samples.
- Compatibility retained:
  - `NewAnomaly`, `Disorder`, `PolarityDisorder`, and `DirgeOfDestinyAnomaly` copied-output constructors remain retained and unchanged.
  - Handler report fields, calculator event payload identity, `LBS.DISORDER_SETTLED`, disorder stun update, and anomaly `RuntimeCommandPort.settle_buffs(...)` are now focused rollback anchors for future proposal work.
  - No old-coupling review update was needed because this test-only slice found no new Buff coupling.
- Next step:
  - Continue with US-005 by codifying registered behavior sample eligibility; do not run main-loop consistency or create validation-only teams unless a real registered route with relevant nonzero copied-output/anomaly events is found.
---
## 2026-06-13 14:45 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-codify-registered-behavior-sample-eligibility.md`, `scripts/ralph/investigations/2026-06-13-US-005-registered-behavior-sample-eligibility.md`, `scripts/ralph/checkpoints/2026-06-13-us-005-registered-behavior-sample-eligibility.md`, `scripts/ralph/plans/slices/us-006-run-retained-validation-gates-serially.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 registered behavior sample eligibility packet` replaces implicit main-loop sample assumptions with a documented conditional gate for real registered routes, nonzero copied-output/anomaly event counts, matching total damage, unchanged buff timelines, and live production semantic diffs.
  - This story builds an evidence and verifier-policy boundary only; it does not replace live production formula code, copied-output constructors, scheduled event handlers, dispatch/runtime ports, listener broadcasts, same-tick runtime writes, validation-runner wiring, registered teams/APLs, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Current registered teams remain `青衣雷属性队`, `席德大安比队`, `莱特火属性队`, and `薇薇安物理队`; `薇薇安物理队` is the only current anomaly/copied-output route candidate, but no main-loop consistency sample is retained for this docs-only story because there is no live production semantic diff and no JSON report with nonzero relevant counts.
  - Future production semantic diffs must use a real registered route and include team, APL, stop tick, matching total damage, relevant nonzero event count, and unchanged buff timeline differences; validation-only teams remain forbidden.
  - No old-coupling review update was needed because this evidence-only slice found no new Buff coupling.
- Next step:
  - Continue with US-006 by running retained validation gates serially; keep main-loop consistency skipped unless a later production semantic diff satisfies the registered-route sample contract.
---
## 2026-06-13 15:12 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-run-retained-validation-gates-serially.md`, `scripts/ralph/checkpoints/2026-06-13-us-006-retained-validation-gates-serial.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 serial retained validation checkpoint` replaces chat-only or implicit validation confidence with focused pytest plus serial `formula-parity`, `calculator-reads`, and `implicit-events` verifier evidence.
  - This story builds validation evidence only; it does not replace live production formula code, copied-output constructors, scheduled event handlers, dispatch/runtime ports, listener broadcasts, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Focused copied-output/listener/handler pytest passed with `168 passed`; `formula-parity`, `calculator-reads`, and `implicit-events` all exited `0` with scoped mypy success.
  - Full default validation remains conditional and was not run because this slice did not change lifecycle containers, runtime write paths, or validation-runner behavior.
  - No old-coupling review update was needed because this validation-only slice found no new Buff coupling.
- Next step:
  - Continue with US-007 by deciding proposal readiness and rollback anchors from the retained evidence; do not treat passing retained gates as authorization for a broad formula, copied-output, event/listener/runtime, lifecycle, registered-route, or validation-runner rewrite.
---
## 2026-06-13 15:21 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-decide-proposal-readiness-and-rollback-anchors.md`, `scripts/ralph/investigations/2026-06-13-US-007-proposal-readiness-rollback-anchors.md`, `scripts/ralph/checkpoints/2026-06-13-us-007-proposal-readiness-rollback-anchors.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 proposal-readiness and rollback-anchor packet` replaces implicit copied-output production-readiness assumptions with a conditional Go for a later bounded proposal package and an explicit No-Go for immediate implementation or broad `Calculator.py` / `CalAnomaly.py` rewrite.
  - This story builds decision and rollback evidence only; it does not replace live production formula code, copied-output constructors, scheduled event handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Rollback anchors remain `CopyAnomalyForOutput.py` constructors, `UpdateAnomaly.spawn_output(...)`, anomaly/disorder/polarity/abloom handlers, focused constructor/listener/handler tests, Ralph evidence docs, and this replacement note.
  - Listener broadcast, scheduled publish, dot runtime registration, and same-tick runtime writes remain separate retained layers.
  - The same-phase candidate pool remains broad for US-008 handoff; copied-output proposal packaging, registered-sample eligibility, remaining RegularMul / retained-only sheer follow-up, `StunMul.get_stun_array()` / array-output follow-up, and P2-A through P2-G guarded maintenance remain separate candidate blocks when evidence supports them.
  - No old-coupling review update was needed because this docs-only decision found no new Buff coupling.
- Next step:
  - Continue with US-008 final handoff docs and same-phase candidate pool; carry forward the conditional proposal readiness decision without authorizing production implementation or collapsing the candidate pool to one follow-up.
---
## 2026-06-13 15:38 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-final-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/checkpoints/2026-06-13-us-008-final-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-008 final handoff docs and same-phase candidate pool` replaces implicit next-PRD routing with a durable copied-output bounded proposal default plus a broad same-phase candidate pool.
  - This story builds handoff and proposal-routing evidence only; it does not replace live production formula code, copied-output constructors, scheduled event handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Next default PRD is proposal-only for copied-output handler/report parity; immediate implementation, broad `Calculator.py` / `CalAnomaly.py` rewrite, validation-runner rewrite, validation-only registered teams, and retained compatibility deletion remain No-Go.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` / retained-only sheer follow-up, `Calculator.StunMul.get_stun_array()` / array-output follow-up, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - No old-coupling review update was needed because this docs-only handoff found no new Buff coupling beyond already documented copied-output, formula snapshot, event/runtime, guarded-maintenance, and retained compatibility boundaries.
- Next step:
  - Generate the copied-output handler/report bounded proposal package from the default route in `docs/Buff重构下阶段计划草稿.md`; after that proposal, reselect from the same-phase pool instead of auto-collapsing to one implementation path.
---
## 2026-06-14 00:12 +08:00 - US-001
- Files changed: `tasks/prd-buff-refactor-phase3-copied-payload-handler-report-bounded-proposal.md`, `scripts/ralph/plans/slices/us-001-reconfirm-proposal-scope-and-prior-evidence.md`, `scripts/ralph/investigations/2026-06-14-US-001-proposal-scope-evidence.md`, `scripts/ralph/checkpoints/2026-06-14-us-001-proposal-scope-evidence.md`, `scripts/ralph/plans/slices/us-002-define-copied-output-constructor-proposal-contract.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 proposal scope evidence packet` replaces stale or chat-only bounded-proposal scope assumptions with an excluded root scan, exact candidate source inventory, retained evidence targets, checkpoint, evidence-ledger, PRD, progress, and refreshed next-slice controller state.
  - This story builds a proposal-scope evidence boundary only; it does not replace a live production formula path, copied-output constructor, `UpdateAnomaly.py` path, scheduled handler, dispatch/runtime port, listener broadcast, dot runtime registration, same-tick runtime write, validation-runner path, registered team, old Buff container, or retained compatibility path.
- Compatibility retained:
  - Root proposal candidates are limited to `CopyAnomalyForOutput.py`, `UpdateAnomaly.py`, and the root anomaly/disorder/polarity-disorder/abloom handlers; old `.codex_worktrees/`, archives, logs, generated output, and run output remain excluded from authoritative proposal inventory.
  - P2-A through P2-G remain guarded maintenance only and are not part of this default proposal.
  - Immediate production implementation remains out of scope; no old-coupling review update was needed because this docs-only evidence slice found no new Buff coupling.
- Next step:
  - Continue with US-002 by defining the copied-output constructor proposal contract for `NewAnomaly`, `Disorder`, `PolarityDisorder`, and `DirgeOfDestinyAnomaly` without editing production constructors or broadening into implementation.
---
## 2026-06-14 00:25 +08:00 - US-002
- Files changed: `scripts/ralph/plans/slices/us-002-define-copied-output-constructor-proposal-contract.md`, `scripts/ralph/investigations/2026-06-14-US-002-copied-output-constructor-proposal-contract.md`, `scripts/ralph/checkpoints/2026-06-14-us-002-copied-output-constructor-proposal-contract.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 copied-output constructor proposal contract` replaces implicit constructor-scope assumptions with an explicit field-category contract for `_CopiedAnomalyBase`, `NewAnomaly`, `Disorder`, `PolarityDisorder`, and `DirgeOfDestinyAnomaly`.
  - This story builds proposal and rollback evidence only; it does not replace live production constructor code, formulas, event handlers, scheduled publish paths, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `CopyAnomalyForOutput.py` remains unchanged. Copied payload construction remains separate from scheduled publish, listener broadcast, dot registration, and Buff runtime writes.
  - Rollback anchors now require focused constructor/listener/handler/abloom test failure before any later constructor rollback is justified.
  - No old-coupling review update was needed because this docs-only proposal contract found no new Buff coupling.
- Next step:
  - Continue with US-003 by defining the `UpdateAnomaly.spawn_output(...)` and publish-layer proposal contract without editing production `UpdateAnomaly.py` or merging constructor, listener, scheduled publish, dot runtime, and same-tick runtime-write layers.
---
## 2026-06-14 00:39 +08:00 - US-003
- Files changed: `scripts/ralph/plans/slices/us-003-define-updateanomaly-spawn-output-and-publish-layer-proposal-contract.md`, `scripts/ralph/investigations/2026-06-14-US-003-updateanomaly-spawn-output-publish-contract.md`, `scripts/ralph/checkpoints/2026-06-14-us-003-updateanomaly-spawn-output-publish-contract.md`, `scripts/ralph/plans/slices/us-004-define-handler-report-payload-proposal-contract.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 UpdateAnomaly spawn-output and publish-layer proposal contract` replaces implicit assumptions about copied-output construction, synchronous listener broadcast, scheduled publish, dot runtime state, debuff writes, and same-tick runtime writes with an explicit proposal boundary and rollback anchors.
  - This story builds proposal and rollback evidence only; it does not replace live production `UpdateAnomaly.py`, copied-output constructors, formulas, event handlers, dispatch/runtime ports, listener manager implementation, dot runtime adapter implementation, validation-runner wiring, registered teams/APLs, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `spawn_output(...)` mode 0 still constructs `NewAnomaly` without listener broadcast or scheduled publish; modes 1 / 2 still synchronously broadcast `LBS.DISORDER_SPAWN`; missing `polarity_ratio` still fails before side effects.
  - `update_anomaly(...)` still owns scheduled publish ordering through `ScheduleDispatchPort`; dot registration/removal and accompanying debuff writes remain in `anomaly_effect_active(...)` and `remove_dots_cause_disorder(...)`.
  - No old-coupling review update was needed because this docs-only proposal contract found no new Buff coupling.
- Next step:
  - Continue with US-004 by defining the handler/report payload proposal contract without merging report fields, `LBS.DISORDER_SETTLED`, disorder stun update, anomaly `RuntimeCommandPort.settle_buffs(...)`, dispatch/runtime ports, listener broadcasts, dot runtime state, or same-tick runtime writes.
---
## 2026-06-14 00:53 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-define-handler-report-payload-proposal-contract.md`, `scripts/ralph/investigations/2026-06-14-US-004-handler-report-payload-proposal-contract.md`, `scripts/ralph/checkpoints/2026-06-14-us-004-handler-report-payload-proposal-contract.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 handler/report payload proposal contract` replaces implicit handler report/log payload assumptions with an explicit four-handler contract for `AnomalyEventHandler`, `DisorderEventHandler`, `PolarityDisorderEventHandler`, and `AbloomEventHandler`.
  - This story builds proposal and rollback evidence only; it does not replace live production handlers, copied-output constructors, formulas, `Report.report_dmg_result(...)`, dispatch/runtime ports, listener manager implementation, validation-runner wiring, registered teams/APLs, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Handler report fields remain retained: tick, skill tag, element type, damage, stun, buildup, enemy status, UUID, anomaly/disorder flags, and fixed `极性紊乱` / `异放` skill tags where applicable.
  - `LBS.DISORDER_SETTLED` remains a synchronous disorder-family listener broadcast; anomaly `RuntimeCommandPort.settle_buffs(...)` remains the same-tick runtime write boundary and no second write facade is introduced.
  - No old-coupling review update was needed because this docs-only proposal contract found no new Buff coupling.
- Next step:
  - Continue with US-005 by codifying registered-route sample conditions; keep main-loop consistency conditional on a live production semantic diff plus real registered-route JSON evidence with nonzero copied-output/anomaly counts.
---
## 2026-06-14 01:14 +08:00 - US-005
- Files changed: `tasks/prd-buff-refactor-phase3-copied-payload-handler-report-bounded-proposal.md`, `scripts/ralph/plans/slices/us-005-codify-registered-route-sample-conditions.md`, `scripts/ralph/investigations/2026-06-14-US-005-registered-route-sample-conditions.md`, `scripts/ralph/checkpoints/2026-06-14-us-005-registered-route-sample-conditions.md`, `scripts/ralph/plans/slices/us-006-codify-retained-validation-and-typecheck-gates.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 registered-route sample conditions packet` replaces implicit main-loop sample assumptions with an explicit conditional gate for live production semantic diffs, real registered-route JSON evidence, matching total damage, nonzero relevant anomaly/copied-output event counts, and unchanged Buff timeline differences.
  - This story builds proposal/verifier evidence only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Current root registered teams remain `青衣雷属性队`, `席德大安比队`, `莱特火属性队`, and `薇薇安物理队`; `薇薇安物理队` is the current anomaly/copied-output candidate only while it remains in root config and its APL carries anomaly-status predicates.
  - Main-loop consistency remains skipped for docs-only proposal work and cannot be satisfied by validation-only teams, APLs, fake routes, or retained-vs-retained JSON samples.
  - `implicit-events` validation/typecheck exited `0`; JSON sanity and edited Markdown UTF-8 / mojibake scan passed. No old-coupling review update was needed because no new Buff coupling was discovered.
- Next step:
  - Continue with US-006 by codifying retained validation and typecheck gates serially; keep main-loop consistency conditional unless a later production semantic diff satisfies the registered-route sample contract.
---
## 2026-06-14 01:25 +08:00 - US-006
- Files changed: `tasks/prd-buff-refactor-phase3-copied-payload-handler-report-bounded-proposal.md`, `scripts/ralph/plans/slices/us-006-codify-retained-validation-and-typecheck-gates.md`, `scripts/ralph/checkpoints/2026-06-14-us-006-retained-validation-and-typecheck-gates.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 retained validation and typecheck gate contract` replaces vague validation confidence with exact focused pytest, `formula-parity`, `calculator-reads`, `implicit-events`, JSON sanity, UTF-8 / mojibake, and conditional full-default validation rules.
  - This story builds proposal/verifier evidence only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Retained gate commands must run serially; `formula-parity`, `calculator-reads`, and `implicit-events` all exited `0` for this story, with focused pytest `168 passed`.
  - Full default validation remains conditional on lifecycle container, runtime write path, or validation-runner behavior changes; none of those surfaces changed in this docs-only slice.
  - No old-coupling review update was needed because this docs-only gate contract found no new Buff coupling.
- Next step:
  - Continue with US-007 proposal Go / No-Go and reviewer questions; carry this retained gate contract forward without treating it as production implementation authorization.
---
## 2026-06-14 01:35 +08:00 - US-007
- Files changed: `tasks/prd-buff-refactor-phase3-copied-payload-handler-report-bounded-proposal.md`, `scripts/ralph/plans/slices/us-007-decide-proposal-go-no-go-and-reviewer-questions.md`, `scripts/ralph/investigations/2026-06-14-US-007-proposal-go-no-go-reviewer-questions.md`, `scripts/ralph/checkpoints/2026-06-14-us-007-proposal-go-no-go-reviewer-questions.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 proposal Go / No-Go decision packet` replaces implicit implementation-readiness judgment with a conditional Go contract, named blockers, future diff candidates, focused tests, scoped mypy targets, registered-route conditions, rollback anchors, stop conditions, and reviewer questions.
  - This story builds proposal/reviewer evidence only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The later implementation scope, if any, is limited to one coherent copied-output handler/report slice; broad `Calculator.py` / `CalAnomaly.py` rewrite, formula replacement, validation-runner rewrite, registered-team fixture creation, old-container deletion, and layer merging remain excluded.
  - `ScheduleDispatchPort`, synchronous listener broadcast, dot runtime registration/removal, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain separate retained boundaries.
  - No old-coupling review update was needed because this docs-only decision packet found no new Buff coupling.
- Next step:
  - Continue with US-008 final handoff docs and same-phase candidate pool; carry this conditional Go forward without collapsing future PRD generation to only one copied-output implementation path.
---

## 2026-06-14 01:53 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `docs/Buff系统重构Checklist.md`, `scripts/ralph/checkpoints/2026-06-14-us-008-final-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-008 final handoff docs and same-phase candidate pool` replaces proposal-only next-stage wording with the current conditional Go result for one later bounded copied-output handler/report implementation PRD.
  - This story updates handoff / Ralph evidence only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The later implementation scope remains limited to one coherent copied-output handler/report slice selected from copied payload constructors, `UpdateAnomaly.spawn_output(...)`, and anomaly/disorder/polarity/abloom handler report paths.
  - Registered behavior sample eligibility, `Calculator.RegularMul` remaining branches / retained-only sheer follow-up, `Calculator.StunMul.get_stun_array()` / array-output follow-up, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules remain available as same-phase candidates.
  - `ScheduleDispatchPort`, synchronous listener broadcast, dot runtime registration/removal, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain separate retained boundaries.
- Next step:
  - Generate the bounded copied-output handler/report implementation PRD only if it carries exact touched files/symbols, focused tests, scoped mypy targets, retained gates, registered-sample conditions, rollback anchors, stop conditions, and non-goals; after that implementation completes, reselect from the broad same-phase pool.
---
## 2026-06-14 06:24 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-lock-implementation-scope-and-diff-contract.md`, `scripts/ralph/investigations/2026-06-14-US-001-implementation-scope-diff-contract.md`, `scripts/ralph/plans/slices/us-002-implement-copied-payload-constructor-boundary.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 implementation scope and diff contract` prepares to replace implicit implementation-scope assumptions with an explicit copied-payload / handler-report boundary, rollback tests, stop conditions, and reviewer questions.
  - This story builds boundary evidence only; it does not replace live production constructors, `UpdateAnomaly.py`, anomaly-family handlers, formula code, validation-runner wiring, registered teams/APLs, dispatch/runtime ports, listener manager implementation, dot runtime adapter implementation, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Later implementation is limited to `_CopiedAnomalyBase`, `NewAnomaly`, `Disorder`, `PolarityDisorder`, `DirgeOfDestinyAnomaly`, `spawn_output(...)`, optional `UpdateAnomaly.update_anomaly(...)` order assertions only, and anomaly/disorder/polarity/abloom handler report payload boundaries.
  - `Calculator.py`, `CalAnomaly.py`, validation-runner wiring, registered teams/APLs, old Buff containers, dispatch/runtime port implementations, listener manager implementation, dot runtime adapter implementation, lifecycle containers, and retained compatibility deletion remain stop conditions.
  - `implicit-events` validation/typecheck passed; JSON sanity and edited Markdown/progress UTF-8 / mojibake scans passed. No old-coupling review update was needed because no new Buff coupling was discovered.
- Next step:
  - Controller refresh moved the active durable slice to US-002. Continue by implementing copied-payload constructor boundary work only inside `CopyAnomalyForOutput.py`; record implementation No-Go if the diff crosses any US-001 stop condition.
---
## 2026-06-14 06:39 +08:00 - US-002
- Files changed: `zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`, `scripts/ralph/plans/slices/us-002-implement-copied-payload-constructor-boundary.md`, `scripts/ralph/investigations/2026-06-14-US-002-copied-payload-constructor-boundary.md`, `scripts/ralph/checkpoints/2026-06-14-us-002-copied-payload-constructor-boundary.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `CopyAnomalyForOutput.py` copied-payload constructor boundary replaces implicit constructor ownership with explicit source-copy, payload-install, explicit-context override, and subclass-owned field markers.
  - This story implements the constructor boundary only; it does not replace `UpdateAnomaly.spawn_output(...)`, anomaly-family handlers, formulas, dispatch/runtime ports, listener manager implementation, dot runtime adapters, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `_CopiedAnomalyBase` still deep-copies the source `AnomalyBar`, preserves copied `current_ndarray` / `current_effective_anomaly`, and only overrides `sim_instance` or `activated_by` when explicit inputs are provided.
  - `Disorder` still sets `is_disorder=True`; `PolarityDisorder` still owns `polarity_disorder_ratio` and `additional_dmg_ap_ratio`; `DirgeOfDestinyAnomaly` still sets `anomaly_dmg_ratio=1.0`.
  - Focused constructor/spawn-output anchors and `implicit-events` validation/typecheck passed. No old-coupling review update was needed because no new Buff coupling was discovered.
- Next step:
  - Continue with US-003 by implementing `UpdateAnomaly.spawn_output(...)` mode boundary while keeping copied construction, synchronous listener broadcast, scheduled publish, dot runtime state, and same-tick runtime writes separate.
---
## 2026-06-14 06:59 +08:00 - US-003
- Files changed: `zsim/sim_progress/Update/UpdateAnomaly.py`, `tests/simulator/test_update_anomaly_dispatch.py`, `scripts/ralph/plans/slices/us-003-implement-spawn-output-mode-boundary.md`, `scripts/ralph/investigations/2026-06-14-US-003-spawn-output-mode-boundary.md`, `scripts/ralph/checkpoints/2026-06-14-us-003-spawn-output-mode-boundary.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/plans/slices/us-004-preserve-scheduled-publish-dot-runtime-and-debuff-layers.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `UpdateAnomaly.spawn_output(...)` mode boundary replaces implicit `output is None` invalid-mode fallback with an explicit error branch before copied-output construction, listener broadcast, scheduled publish, or source settlement.
  - This story implements only the `spawn_output(...)` mode boundary; it does not replace `UpdateAnomaly.update_anomaly(...)`, copied-output constructors, anomaly-family handlers, formulas, dispatch/runtime ports, listener manager implementation, dot runtime adapters, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Mode 0 still settles the source anomaly bar before `NewAnomaly` construction and does not broadcast listeners or publish scheduled events directly.
  - Modes 1 / 2 still synchronously broadcast `LBS.DISORDER_SPAWN`; mode 2 still requires `polarity_ratio`; invalid mode is now covered by a no-construction/no-side-effect focused test.
  - Focused spawn-output anchors and `implicit-events` validation/typecheck passed. No old-coupling review update was needed because no new Buff coupling was discovered.
- Next step:
  - Continue with US-004 by preserving scheduled publish, dot runtime, and debuff layers without moving those responsibilities into copied-output construction.
---
## 2026-06-14 07:15 +08:00 - US-004
- Files changed: `tests/simulator/test_update_anomaly_dispatch.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `scripts/ralph/plans/slices/us-004-preserve-scheduled-publish-dot-runtime-and-debuff-layers.md`, `scripts/ralph/investigations/2026-06-14-US-004-layer-preservation-boundaries.md`, `scripts/ralph/checkpoints/2026-06-14-us-004-layer-preservation-boundaries.md`, `scripts/ralph/plans/slices/us-005-implement-handler-report-payload-boundary.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 layer-preservation anchors` replace implicit reviewer confidence with focused tests for fresh scheduled dispatch creation, copied-output constructor side-effect boundaries, and handler report layer separation.
  - This story adds characterization tests and Ralph/Buff evidence only; it does not replace live production `UpdateAnomaly.py`, copied-output constructors, anomaly-family handlers, formulas, dispatch/runtime port implementations, listener manager implementation, dot runtime adapters, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `UpdateAnomaly.update_anomaly(...)` still creates a fresh `ScheduleDispatchPort` from the current `sim_instance`; `_publish_scheduled_event(...)` / `ScheduleDispatchPort.publish_scheduled(...)` still own scheduled publish.
  - Dot registration/removal remains in `anomaly_effect_active(...)`, `remove_dots_cause_disorder(...)`, and `DotRuntimeStateAdapter`; accompanying debuff writes remain on `buff_add_strategy(...)`.
  - Handler report modules and copied-output constructors remain guarded from scheduled publish, dot runtime, debuff-write, direct `update_anomaly(...)`, and parallel runtime-write responsibilities.
  - Focused layer anchors and `implicit-events` validation/typecheck passed. No old-coupling review update was needed because no new Buff coupling was discovered.
- Next step:
  - Continue with US-005 handler report payload boundary implementation while preserving the US-004 source guards and the separation between scheduled publish, listener broadcast, dot runtime, debuff writes, and same-tick runtime writes.
---
## 2026-06-14 07:31 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-implement-handler-report-payload-boundary.md`, `scripts/ralph/investigations/2026-06-14-US-005-handler-report-payload-boundary.md`, `scripts/ralph/checkpoints/2026-06-14-us-005-handler-report-payload-boundary.md`, `scripts/ralph/plans/slices/us-006-run-focused-pytest-scoped-typecheck-and-retained-gates.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 handler report payload boundary verification` replaces implicit handler/report payload confidence with focused verifier evidence for anomaly, disorder, polarity disorder, and abloom report fields plus retained listener/runtime boundaries.
  - This story verifies the production boundary but does not replace live production handler code because the root handlers already match the retained contract.
- Compatibility retained:
  - `AnomalyEventHandler.handle(...)` still reports payload fields before routing same-tick Buff settlement through `RuntimeCommandPort.settle_buffs(...)`.
  - `DisorderEventHandler.handle(...)` and `PolarityDisorderEventHandler.handle(...)` still broadcast `LBS.DISORDER_SETTLED` synchronously before damage/report work; `AbloomEventHandler.handle(...)` remains report-only.
  - Copied-output constructors, `UpdateAnomaly.py`, formulas, dispatch/runtime port implementations, listener manager implementation, dot runtime adapters, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, and retained compatibility paths remain unchanged.
- Next step:
  - Continue with US-006 by running focused pytest, scoped typecheck, and retained validation profiles serially; full default validation remains conditional on lifecycle, runtime-write, or validation-runner behavior changes.
---

## 2026-06-14 07:53 +08:00 - US-006
- Files changed: `zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`, `tests/simulator/test_update_anomaly_dispatch.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `scripts/run_buff_refactor_validation.py`, `scripts/ralph/plans/slices/us-006-run-focused-pytest-scoped-typecheck-and-retained-gates.md`, `scripts/ralph/investigations/2026-06-14-US-006-scoped-mypy-copied-output.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `CopyAnomalyForOutput.py` copied-output constructor-owned field annotations prepare the retained copied-payload implementation for scoped mypy coverage by replacing implicit empty-tuple inference with explicit `ClassVar[tuple[str, ...]]` typing.
  - `scripts/run_buff_refactor_validation.py` scoped mypy target coverage now includes the focused `UpdateAnomaly` and anomaly-handler tests required by US-006.
  - This story hardens verifier/typecheck evidence only; it does not replace live copied payload construction, `UpdateAnomaly.py`, anomaly-family production handlers, formula code, dispatch/runtime ports, listener broadcasts, dot runtime, lifecycle containers, old Buff containers, or same-tick runtime writes.
- Compatibility retained:
  - `NewAnomaly`, `Disorder`, `PolarityDisorder`, and `DirgeOfDestinyAnomaly` keep the same runtime constructor behavior and owned-field values; the final change is annotation-only.
  - Focused pytest, serial `formula-parity`, serial `calculator-reads`, serial `implicit-events`, and default validation gates passed after the annotation, focused-test typing, and validation-runner target-list fixes.
  - Known pytest-asyncio warning, mypy untyped-body notes, async log-writer shutdown noise, and wrapper console mojibake were recorded separately from verifier failures.
- Next step:
  - Continue with US-007 registered-route/main-loop eligibility and reviewer verdict; keep full default validation conditional on lifecycle, runtime-write, or validation-runner behavior changes.
---
## 2026-06-14 08:21 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-decide-registered-route-main-loop-eligibility-and-reviewer-verdict.md`, `scripts/ralph/investigations/2026-06-14-US-007-main-loop-eligibility-reviewer-verdict.md`, `scripts/ralph/checkpoints/2026-06-14-us-007-main-loop-eligibility-reviewer-verdict.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 registered-route/main-loop eligibility verdict` replaces implicit live-sample pressure with an explicit No-Go for retained-vs-retained main-loop sampling when there is no live production semantic diff.
  - This story updates reviewer and Ralph evidence only; it does not replace live copied payload construction, `UpdateAnomaly.py`, anomaly-family production handlers, formula code, dispatch/runtime ports, listener broadcasts, dot runtime, lifecycle containers, registered teams/APLs, old Buff containers, or same-tick runtime writes.
- Compatibility retained:
  - `薇薇安物理队` remains a future copied-output/anomaly route candidate only after a later semantic diff preflight proves the target copied payload route with nonzero relevant counts; validation-only teams/APLs/routes remain forbidden.
  - `ScheduleDispatchPort` stayed queue-only, listener broadcasts stayed synchronous, dot runtime stayed separate, anomaly settlement stayed on `RuntimeCommandPort.settle_buffs(...)`, no second write facade was introduced, and retained old-container compatibility remained intact.
  - Focused main-loop tests and `implicit-events` validation/typecheck passed; known pytest-asyncio warning, mypy untyped-body notes, and async log-writer shutdown noise remained separate from verifier failures.
- Next step:
  - Continue with US-008 final handoff docs and same-phase candidate pool; keep registered-route main-loop consistency conditional on future live production semantic diffs plus real route nonzero copied-output/anomaly evidence.
---

## 2026-06-14 08:35 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-final-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/investigations/2026-06-14-US-008-docs-typecheck-scope.md`, `scripts/ralph/checkpoints/2026-06-14-us-008-final-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-008 final handoff docs and same-phase candidate pool` replaces copied-output implementation as the automatic next default with a Phase-3 same-phase candidate selection / bounded proposal PRD.
  - The completed implementation boundary remains `CopyAnomalyForOutput.py` copied-payload constructor ownership, `UpdateAnomaly.spawn_output(...)` mode failure ordering, layer-preservation anchors, handler report payload boundary, scoped mypy coverage, and registered-route No-Go evidence.
- Compatibility retained:
  - `Calculator.py` / `CalAnomaly.py`, `MultiplierData` / `MulData` / `DynamicStatement`, `AnomalyBar.current_ndarray`, old containers, legacy `buff_add()` / `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcast, dot runtime, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, AM/AP/impact helper implementation, `cal_res_pen()` selector extraction, and array / RegularMul / sheer characterization evidence remain retained.
  - Registered behavior sample eligibility, remaining `Calculator.RegularMul` / retained-only sheer follow-up, `Calculator.StunMul.get_stun_array()` / array-output follow-up, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules remain available as same-phase candidates.
  - No old-coupling review update was needed because this final handoff found no new Buff coupling or coupling classification change.
- Next step:
  - Generate one bounded same-phase candidate-selection / proposal PRD from the documented pool; do not directly convert that Markdown PRD into `scripts/ralph/prd.json` until a later explicit Ralph conversion step.
---

## 2026-06-14 09:37 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-phase-3-candidate-pool-and-baseline.md`, `scripts/ralph/investigations/2026-06-14-US-001-phase3-candidate-baseline.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 Phase-3 candidate baseline packet` replaces implicit carry-over assumptions with cited evidence that the same-phase pool remains registered sample eligibility, remaining `Calculator.RegularMul` / retained-only sheer follow-up, `Calculator.StunMul.get_stun_array()` / array-output follow-up, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - This story updates Ralph/Buff evidence only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Copied-payload handler/report implementation, `cal_res_pen()` selector extraction, AM/AP/impact helper implementation, Stun / RegularMul array characterization, selected RegularMul branch matrix, and retained-only sheer No-Go are completed evidence, not automatic implementation authorization.
  - `formula-parity` and `calculator-reads` remain serial retained gates for formula/read candidates; `implicit-events` remains conditional for copied-output, event, dispatch, runtime, or listener boundaries.
  - `scripts/ralph/prd.json` remains unchanged per active story acceptance.
- Next step:
  - Continue with US-002 remaining formula surface matrix; select exact candidate evidence without reopening completed scopes unless new root-workspace source, guardrail, focused-test, validation, or registered-route evidence names a concrete blocker.
---

## 2026-06-14 10:08 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-phase-3-candidate-pool-and-baseline.md`, `scripts/ralph/investigations/2026-06-14-US-001-phase3-candidate-baseline.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 Phase-3 candidate baseline refresh` replaces stale preflight count evidence with the current generated-history-excluded preflight and keeps the candidate-selection packet aligned with controller state.
  - This story remains evidence-only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Copied-payload handler/report implementation, `cal_res_pen()` selector extraction, AM/AP/impact helper implementation, Stun / RegularMul array characterization, selected RegularMul branch matrix, and retained-only sheer No-Go remain completed evidence, not automatic implementation authorization.
  - `formula-parity` and `calculator-reads` remain serial retained gates for formula/read candidates; `implicit-events` remains conditional for copied-output, event, dispatch, runtime, or listener boundaries.
  - `scripts/ralph/prd.json` remains unchanged per active story acceptance.
- Next step:
  - Continue with US-002 remaining formula surface matrix; select exact candidate evidence without reopening completed scopes unless new root-workspace source, guardrail, focused-test, validation, or registered-route evidence names a concrete blocker.
---

## 2026-06-14 10:16 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-phase-3-candidate-pool-and-baseline.md`, `scripts/ralph/investigations/2026-06-14-US-001-phase3-candidate-baseline.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 Phase-3 candidate baseline refresh` updates the evidence packet with the current generated-history-excluded `rg` count, CodeGraph navigation terms, scoped typecheck, JSON sanity, and UTF-8/mojibake evidence.
  - This story remains evidence-only; it does not replace live production formula code, copied-output constructors, `UpdateAnomaly.py`, scheduled handlers, dispatch/runtime ports, listener broadcasts, dot runtime registration, same-tick runtime writes, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Copied-payload handler/report implementation, `cal_res_pen()` selector extraction, AM/AP/impact helper implementation, Stun / RegularMul array characterization, selected RegularMul branch matrix, and retained-only sheer No-Go remain completed evidence, not automatic implementation authorization.
  - `formula-parity` and `calculator-reads` remain serial retained gates for formula/read candidates; `implicit-events` remains conditional for copied-output, event, dispatch, runtime, or listener boundaries.
  - `scripts/ralph/prd.json` remains unchanged per active story acceptance.
- Next step:
  - Continue with US-002 remaining formula surface matrix; select exact candidate evidence without reopening completed scopes unless new root-workspace source, guardrail, focused-test, validation, or registered-route evidence names a concrete blocker.
---

## 2026-06-14 11:40 +08:00 - US-002
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `scripts/ralph/plans/slices/us-002-build-remaining-formula-surface-matrix.md`, `scripts/ralph/investigations/2026-06-14-US-002-remaining-formula-surface-matrix.md`, `scripts/ralph/checkpoints/2026-06-14-us-002-remaining-formula-surface-matrix.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 remaining formula surface matrix` replaces implicit same-phase formula candidate grouping with one exact per-surface matrix for the requested `Calculator.RegularMul` methods, `Calculator.StunMul.get_stun_array()`, and the actual `Calculator.cal_stun()` array-output consumer path.
  - This story updates evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, copied-output constructors, old containers, legacy `buff_add()` / `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcast, dot runtime, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained boundaries.
  - Existing focused oracle evidence stays characterization-only. The matrix does not authorize broad `Calculator.py` / `CalAnomaly.py` rewrite, registered-team fixture creation, old-container deletion, layer merging, or retained compatibility deletion.
- Next step:
  - Continue with US-003 registered behavior sample eligibility using the matrix as input; keep registered samples conditional on future live semantic diffs plus real route evidence.
---

## 2026-06-14 12:01 +08:00 - US-003
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-003-audit-registered-behavior-sample-eligibility.md`, `scripts/ralph/plans/slices/us-004-select-one-exact-bounded-proposal-candidate.md`, `scripts/ralph/investigations/2026-06-14-US-003-registered-behavior-sample-eligibility.md`, `scripts/ralph/checkpoints/2026-06-14-us-003-registered-behavior-sample-eligibility.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-003 registered behavior sample eligibility audit` replaces implicit sample pressure with explicit No-Go / conditional No-Go conditions before any future formula semantic diff.
  - This story updates docs and Ralph evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Retained-only sheer remains blocked because no real registered Yixuan route exists; no validation-only team, fake APL, fixture-only route, or retained-vs-retained main-loop sample was created.
  - Stun/impact and direct RegularMul candidates remain conditional on a later live production semantic diff plus real registered route, relevant nonzero event or formula count, explicit stop tick, runtime labels, total damage comparison, and Buff timeline comparison.
  - `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, old containers, legacy `buff_add()` / `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcast, dot runtime, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained boundaries.
- Next step:
  - Continue with US-004 exact bounded proposal candidate selection; if the selected candidate lacks a real route or nonzero count proof, record No-Go instead of preparing production diff or main-loop sample.
---

## 2026-06-14 12:17 +08:00 - US-004
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-004-select-one-exact-bounded-proposal-candidate.md`, `scripts/ralph/investigations/2026-06-14-US-004-exact-bounded-candidate-selection.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-004 exact bounded candidate selection` replaces the broad same-phase candidate pool for the next proposal-contract stories with one selected surface: `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array output.
  - This story updates docs and Ralph evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, all `Calculator.RegularMul` branches, and retained-only sheer remain separate retained boundaries.
  - Field order, `np.float64` dtype, `Calculator.cal_stun()` product behavior, `MultiplierData` / `DynamicStatement`, old containers, copied-output constructors, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained.
  - Main-loop consistency remains blocked until a future live semantic diff names a real registered route with nonzero relevant stun / impact counts, explicit stop tick, runtime labels, total damage comparison, and Buff timeline comparison.
- Next step:
  - Continue with US-005 focused oracle and typecheck contract for the selected Stun array output only; do not broaden into RegularMul, retained-only sheer, copied-output, registered-team creation, or production implementation.
---

## 2026-06-14 12:32 +08:00 - US-005
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-005-define-focused-oracle-and-typecheck-contract.md`, `scripts/ralph/plans/slices/us-006-define-rollback-anchors-and-stop-conditions.md`, `scripts/ralph/investigations/2026-06-14-US-005-focused-oracle-typecheck-contract.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-005 focused oracle and typecheck contract` prepares to replace implicit proposal-readiness evidence with the exact pytest nodeid `tests/simulator/test_buff_attribute_reader.py::test_stun_array_output_contract_preserves_field_order_dtype_and_product` plus retained `formula-parity` / `calculator-reads` profile gates.
  - This story builds verifier evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.StunMul.get_stun_array()` field order, `np.float64` dtype, `Calculator.cal_stun()` product behavior, `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, all `Calculator.RegularMul` branches, retained-only sheer, `MultiplierData` / `DynamicStatement`, old containers, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade` remain retained.
  - `implicit-events` remains conditional because no copied-output, event, dispatch/runtime, listener-facing, lifecycle, validation-wiring, same-tick runtime, or production semantic surface changed.
- Next step:
  - Continue with US-006 rollback anchors and stop conditions for the selected Stun array output contract; keep production implementation, RegularMul bundling, retained-only sheer expansion, main-loop samples, and old-path deletion out of scope.
---

## 2026-06-14 12:47 +08:00 - US-006
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-006-define-rollback-anchors-and-stop-conditions.md`, `scripts/ralph/investigations/2026-06-14-US-006-rollback-anchors-stop-conditions.md`, `scripts/ralph/checkpoints/2026-06-14-us-006-rollback-anchors-stop-conditions.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-006 rollback anchors and stop conditions` prepares to replace implicit proposal-safety assumptions with explicit retained anchors for `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` and named stop conditions before any future production implementation PRD.
  - This story updates docs and Ralph evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Source anchors, focused Stun array pytest, retained Buff docs, `formula-parity`, `calculator-reads`, and conditional `implicit-events` remain the required rollback / verifier layers.
  - Event queue semantics, synchronous listener broadcasts, dot runtime registration, and same-tick runtime writes remain separate retained layers; `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, old containers, and copied-output constructors remain unchanged.
- Next step:
  - Continue with US-007 final retained gates and reviewer verdict; do not convert this rollback contract into production formula implementation.
---

## 2026-06-14 13:13 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-run-final-retained-gates-and-reviewer-verdict.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/checkpoints/2026-06-14-us-007-final-retained-gates-reviewer-verdict.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 final retained gates and reviewer verdict` prepares to replace implicit proposal-readiness approval with exact retained gate evidence and a bounded reviewer verdict for `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array output.
  - This story verifies evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Focused reader pytest, `formula-parity`, `calculator-reads`, and `implicit-events` all exited `0`; known pytest-asyncio warning, mypy untyped-body notes, and async log-writer shutdown traceback remained non-fatal after success markers.
  - Event queue semantics, synchronous listener broadcasts, dot runtime registration, same-tick runtime writes, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, old containers, and copied-output constructors remain unchanged.
  - Default lifecycle and main-loop consistency validation remain skipped because this docs/verifier slice changed no production semantics, lifecycle container, validation runner, runtime write path, or registered-route behavior.
- Next step:
  - Continue with US-008 handoff docs and same-phase candidate pool; keep any later implementation PRD bounded by the selected Stun array output contract, retained gates, registered-route stop condition, rollback anchors, and invariant checks.
---

## 2026-06-14 13:25 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/checkpoints/2026-06-14-us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/investigations/2026-06-14-US-008-docs-typecheck-scope.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-008 final handoff docs and same-phase candidate pool` replaces implicit next-cycle routing with long-lived docs that name `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` as the selected default bounded proposal / implementation surface.
  - This story updates handoff docs and Ralph evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Focused Stun array oracle, retained `formula-parity` / `calculator-reads` gates, conditional `implicit-events`, registered-route conditional No-Go, rollback anchors, old containers, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, copied-output constructors, and layer-separation invariants remain retained.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, `Calculator.StunMul.get_stun_array()` future follow-up, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - `docs/旧Buff系统耦合审查结果.md` remains unchanged because this handoff found no new Buff coupling or coupling classification change.
- Next step:
  - Generate one bounded `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` proposal / implementation PRD; do not directly convert the Markdown PRD into `scripts/ralph/prd.json` until a later explicit Ralph conversion step.
---

## 2026-06-14 14:02 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconfirm-stun-array-implementation-scope.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-001 Stun array implementation scope reconfirmation` prepares the later bounded implementation by replacing chat-only scope assumptions with saved Ralph evidence for the approved `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` surface.
  - This story updates scope, validation, and reviewer evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Current-root Stun array field order, `np.float64` dtype, `Calculator.cal_stun()` product consumer, focused oracle, `formula-parity` scoped typecheck, `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, all `Calculator.RegularMul` branches, retained-only sheer, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, listener broadcasts, dot runtime, and old containers remain unchanged.
- Next step:
  - Continue to `US-002` to pin the Stun array oracle before any production helper extraction; do not broaden into RegularMul, validation-runner, registered-team, old-container, dispatch/runtime, listener, dot-runtime, or retained compatibility work.
---

## 2026-06-14 14:22 +08:00 - US-002
- Files changed: `scripts/ralph/plans/slices/us-002-pin-the-stun-array-oracle-before-production-diff.md`, `scripts/ralph/investigations/2026-06-14-US-002-formula-parity-rerun.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 focused Stun array oracle pinning` prepares the later bounded helper extraction by replacing implicit oracle assumptions with confirmed focused evidence for `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()`.
  - This story anchors verifier evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The focused oracle already pins field order `imp`, `stun_ratio`, `stun_res`, `stun_bonus`, `stun_received`, shape `(5,)`, dtype `np.float64`, one `get_stun_array()` read by `Calculator.cal_stun()`, `np.float64` return type, and `np.float64(np.prod(expected_array))` product behavior.
  - `Calculator.py`, focused test source, `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, all `Calculator.RegularMul` branches, retained-only sheer, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, listener broadcasts, dot runtime, and old containers remain unchanged.
- Next step:
  - Continue to `US-003` for narrow Stun array helper delegation; keep the diff bounded to the selected array output contract and do not broaden into RegularMul, registered-team, validation-runner, event/runtime, listener, dot-runtime, or retained compatibility work.
---

## 2026-06-14 14:34 +08:00 - US-003
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-003-implement-narrow-stun-array-helper-delegation.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `Calculator.py::_build_stun_multiplier_array(...)` replaces the inline five-field `np.float64` array construction responsibility previously embedded inside `Calculator.StunMul.get_stun_array()`.
  - This story builds a rollbackable module-local boundary only; it does not replace scalar Stun formulas, formula reader APIs, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Field order `imp`, `stun_ratio`, `stun_res`, `stun_bonus`, `stun_received`, shape `(5,)`, dtype `np.float64`, and `Calculator.cal_stun()` product behavior remain pinned by focused tests.
  - `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, `cal_stun_ratio()`, `cal_stun_res()`, `cal_stun_bonus()`, `cal_stun_received()`, all `Calculator.RegularMul` branches, `CalAnomaly.py`, copied-output constructors, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, listener broadcasts, dot runtime, and old containers remain unchanged.
- Next step:
  - Continue to `US-004` to preserve formula/reader compatibility boundaries around this helper extraction; do not broaden into RegularMul, registered samples, validation-runner wiring, event/runtime, listener, dot-runtime, or retained compatibility work.
---

## 2026-06-14 14:48 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-preserve-formula-reader-compatibility-boundaries.md`, `scripts/ralph/plans/slices/us-005-decide-runtime-event-and-registered-sample-gates.md`, `scripts/ralph/investigations/2026-06-14-US-004-formula-reader-compatibility-boundaries.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 formula/reader compatibility evidence` prepares to replace implicit post-helper confidence with saved `rg`, CodeGraph, verifier, and reviewer evidence around `CalculatorBuffAttributeReader`, `_CalculatorReadSnapshot`, `MultiplierData`, `CalAnomaly.MulData`, `DynamicStatement`, and `Calculator.cal_stun()`.
  - This story does not replace a live production path; no production source, focused tests, validation-runner wiring, registered routes/APLs, copied-output constructors/handlers, event/runtime/listener paths, lifecycle containers, old Buff containers, or formula implementations changed.
- Compatibility retained:
  - `Calculator.cal_stun()` still reads `self.stun_multipliers.get_stun_array()`, computes `np.prod(multipliers)`, and returns `np.float64(stun)`.
  - `CalculatorBuffAttributeReader`, `_CalculatorReadSnapshot`, `MultiplierData`, `DynamicStatement`, the `CalAnomaly.py` `MulData` alias, retained formula snapshots, Stun array field order, `np.float64` dtype, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, listener broadcasts, dot runtime, and old containers remain unchanged.
  - Serial gates passed: `formula-parity` and `calculator-reads` exited `0`; known pytest-asyncio and async log-writer shutdown noise remained after success markers.
- Next step:
  - Continue to `US-005` runtime/event/registered-sample gate decision; do not treat this compatibility evidence as proof of copied-output, event/runtime, listener, lifecycle, registered-route, or main-loop semantics.
---

## 2026-06-14 15:03 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-decide-runtime-event-and-registered-sample-gates.md`, `scripts/ralph/plans/slices/us-006-final-serial-verification-and-invariant-review.md`, `scripts/ralph/investigations/2026-06-14-US-005-runtime-event-registered-sample-gates.md`, `scripts/ralph/checkpoints/2026-06-14-us-005-runtime-event-registered-sample-gates.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 runtime/event/registered-sample gate decision` replaces implicit runtime validation assumptions with a recorded conditional gate decision for the Stun array helper extraction PRD.
  - This story does not replace a live production path; no production source, focused tests, validation-runner wiring, registered routes/APLs, copied-output constructors/handlers, event/runtime/listener paths, lifecycle containers, old Buff containers, or formula implementations changed.
- Compatibility retained:
  - The implemented diff is behavior-preserving helper extraction, not a live semantic diff. `Calculator.StunMul.get_stun_array()` field order, `np.float64` dtype, and `Calculator.cal_stun()` product consumer remain governed by the focused Stun oracle and `formula-parity`.
  - `implicit-events`, default lifecycle validation, and main-loop consistency remain conditional and were skipped because US-005 touched no copied-output, event, dispatch/runtime, listener-facing, dot runtime, validation wiring, lifecycle, same-tick runtime write, registered-route, or production semantic behavior.
  - Validation evidence: `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `141 passed`, and mypy `9 source files` clean; known pytest-asyncio and async log-writer shutdown noise remained after success markers.
- Next step:
  - Continue to `US-006` final serial verification and invariant review. Run broader event/lifecycle/main-loop gates only if their trigger surfaces become active in a later story.
---

## 2026-06-14 15:15 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-final-serial-verification-and-invariant-review.md`, `scripts/ralph/plans/slices/us-007-record-rollback-anchors-and-replacement-note.md`, `scripts/ralph/checkpoints/2026-06-14-us-006-final-serial-verification-invariant-review.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 final serial verification and invariant review` replaces chat-only final-gate confidence with recorded focused pytest, serial `formula-parity`, serial `calculator-reads`, an infrastructure checkpoint, and a reviewer verdict against Ralph/Buff invariants.
  - This story does not replace a live production path; no production source, focused tests, validation-runner wiring, registered routes/APLs, copied-output constructors/handlers, event/runtime/listener paths, lifecycle containers, old Buff containers, or formula implementations changed.
- Compatibility retained:
  - `Calculator.StunMul.get_stun_array()` field order, `np.float64` dtype, and `Calculator.cal_stun()` product consumer remain governed by the focused Stun oracle and retained `formula-parity` / `calculator-reads` gates.
  - `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, all `Calculator.RegularMul` branches, retained-only sheer, `MultiplierData`, `MulData`, `DynamicStatement`, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, listener broadcasts, dot runtime, and old containers remain retained or out of scope.
  - Validation evidence: focused reader pytest exited `0` with `141 passed`; `formula-parity` exited `0` with focused reader suite `141 passed` and mypy `9 source files` clean; `calculator-reads` exited `0` with focused reader suite `241 passed` and mypy `22 source files` clean.
  - `implicit-events`, default lifecycle validation, and main-loop consistency remain conditional and were skipped because US-005 and US-006 touched no copied-output, event, dispatch/runtime, listener-facing, dot runtime, validation wiring, lifecycle, same-tick runtime write, registered-route, validation-runner, or production semantic behavior.
- Next step:
  - Continue to `US-007` rollback anchors and replacement note; do not broaden into `Calculator.py` / `CalAnomaly.py` rewrites, old-container deletion, validation-runner rewrites, registered-team fixture creation, or layer merges.
---

## 2026-06-14 15:28 +08:00 - US-007
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-007-record-rollback-anchors-and-replacement-note.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-007 rollback anchors and replacement note` replaces chat-only rollback guidance with this retained handoff entry for the bounded `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` Stun array implementation.
  - Rollback anchors are `Calculator.StunMul.get_stun_array()`, module-local `_build_stun_multiplier_array(...)`, `Calculator.cal_stun()`, focused oracle `tests/simulator/test_buff_attribute_reader.py::test_stun_array_output_contract_preserves_field_order_dtype_and_product`, retained `formula-parity` / `calculator-reads` gates, conditional `implicit-events`, and retained Buff docs.
  - Helper extraction was not a no-op in this PRD: the helper already exists from US-003, and this story records verification/evidence only without manufacturing additional source churn.
- Compatibility retained:
  - `Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`, all `Calculator.RegularMul` branches, retained-only sheer, `MultiplierData`, `MulData`, `DynamicStatement`, old containers, copied-output constructors, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, and `LegacyBuffRuntimeFacade` remain retained or out of scope.
  - `implicit-events` remains conditional because US-007 changed only docs/Ralph evidence and completion bookkeeping; no copied-output, event, dispatch/runtime, listener-facing, dot runtime, validation wiring, lifecycle, same-tick runtime write, registered-route, or production semantic behavior changed.
  - Validation evidence: `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `141 passed`, and mypy success on `9 source files`; `calculator-reads` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `241 passed`, and mypy success on `22 source files`.
  - Known warning/noise remained non-fatal after success markers: pytest-asyncio default fixture loop-scope warning and async log-writer shutdown traceback.
- Next step:
  - Continue to `US-008` handoff docs and same-phase candidate pool; do not broaden this rollback note into `Calculator.py` / `CalAnomaly.py` rewrites, RegularMul bundling, retained-only sheer expansion, copied-output changes, old-container deletion, validation-runner rewrites, registered-team fixture creation, or event/runtime/listener layer merges.
---

## 2026-06-14 15:43 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/checkpoints/2026-06-14-us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-008 final handoff docs and same-phase candidate pool` replaces implicit next-cycle routing with long-lived docs that mark the selected Stun array implementation as implemented / no-op verified at handoff.
  - `Calculator.StunMul.get_stun_array()` now remains anchored to `_build_stun_multiplier_array(...)`; `Calculator.cal_stun()` remains the existing product consumer. This handoff does not replace additional live production code.
- Compatibility retained:
  - Focused Stun array oracle, retained `formula-parity` / `calculator-reads` gates, conditional `implicit-events`, registered-route conditional No-Go, rollback anchors, old containers, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, copied-output constructors, and layer-separation invariants remain retained.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - `docs/旧Buff系统耦合审查结果.md` remains unchanged because this handoff found no new Buff coupling or coupling classification change.
- Next step:
  - Generate a Phase-3 same-phase candidate selection / bounded proposal PRD from the retained pool; do not automatically produce another narrow Stun implementation follow-up or directly convert the Markdown PRD into `scripts/ralph/prd.json` in the same generation step.
---

## 2026-06-14 16:14 +08:00 - US-001
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-001-reconcile-current-route-and-completed-scope.md`, `scripts/ralph/checkpoints/2026-06-14-us-001-route-completed-scope-reconciliation.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-001 route / completed-scope reconciliation` replaces stale next-cycle routing that still treated selected Stun implementation as default backlog with the latest handoff state: Stun is implemented / no-op verified, and current default work is `Calculator.RegularMul` remaining branch proposal-readiness.
  - This story updates docs and Ralph evidence only; it does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.StunMul.get_stun_array()` remains delegated to `_build_stun_multiplier_array(...)`, and `Calculator.cal_stun()` remains the product consumer with retained field order and `np.float64` dtype.
  - Copied-output implementation, `Calculator.AnomalyMul.cal_res_pen()` selector extraction, AM/AP/impact helper implementation, selected Stun implementation, and P2-A through P2-G guarded buckets are completed evidence, not default implementation backlog.
  - Current production conclusions exclude `.codex_worktrees/`, `scripts/ralph/archive/`, `scripts/ralph/run-logs/`, logs, and generated history.
- Next step:
  - Continue with US-002 RegularMul remaining branch matrix refresh; reopen Stun, copied-output, `cal_res_pen()`, AM/AP/impact, or P2 guarded buckets only with named root-workspace source, focused test, guardrail, validation, or proposal-readiness evidence.
---

## 2026-06-14 16:33 +08:00 - US-002
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-002-refresh-regularmul-remaining-branch-matrix.md`, `scripts/ralph/investigations/2026-06-14-US-002-regularmul-branch-matrix.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-003-select-one-exact-candidate-or-record-no-go.md`
- Replacement note:
  - `US-002 RegularMul remaining branch matrix` replaces implicit branch-selection confidence with a durable matrix that names deterministic oracle evidence, missing rows, reader-snapshot dependency, registered-route eligibility, rollback anchors, and current status for the eleven required `Calculator.RegularMul` branches.
  - This story does not replace a live production path; no production formula, reader API, registered team/APL, copied-output constructor, event/runtime/listener path, validation-runner wiring, lifecycle container, old Buff container, or retained compatibility path changed.
- Compatibility retained:
  - Snapshot-compatible RegularMul branches are still retained evidence only until a later story selects one exact candidate and closes branch-specific oracle gaps.
  - Retained-only sheer remains separate: `cal_base_attr(..., base_attr=4)` still depends on runtime `char_instance.sheer_attack_conversion_rate`; `cal_sheer_dmg_bonus()` does not become proposal-ready without an approved reader contract and real registered Yixuan / 仪玄 route.
  - Validation evidence: `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `141 passed`, and scoped mypy success on `9 source files`; known pytest-asyncio and async log-writer shutdown noise stayed non-fatal after success markers.
- Next step:
  - Continue to `US-003` exact RegularMul candidate selection or No-Go. Do not bundle all RegularMul branches, reopen completed Stun/Anomaly/copied-output work by default, create validation-only routes, or broaden into a production `Calculator.py` rewrite.
---

## 2026-06-14 16:43 +08:00 - US-003
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-003-select-one-exact-candidate-or-record-no-go.md`, `scripts/ralph/investigations/2026-06-14-US-003-regularmul-candidate-decision.md`, `scripts/ralph/checkpoints/2026-06-14-us-003-regularmul-candidate-decision.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-004-close-focused-oracle-gaps-for-the-selected-candidate.md`
- Replacement note:
  - `US-003 RegularMul candidate decision` replaces implicit branch-selection discussion with one exact selected candidate: `Calculator.RegularMul.cal_crit_rate(data)`.
  - This story is docs/evidence only. It does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate: full `cal_crit_rate()` includes `crit_rate_received_increase`; personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes received bonus and is retained as a contrast boundary.
  - `Calculator.RegularMul.cal_crit_dmg()`, `cal_personal_crit_dmg()`, `cal_crit_expect()`, damage bonus, defense, resistance, vulnerability, base damage, retained-only sheer, arrays, `_CalculatorReadSnapshot` public fields, validation-runner profiles, registered teams/APLs, old containers, and layer-separation invariants remain unchanged.
- Next step:
  - Continue to `US-004` focused oracle-gap closure for the selected `cal_crit_rate()` candidate only. Stop if closure would require `_CalculatorReadSnapshot` public contract expansion, validation-runner rewiring, retained compatibility deletion, production formula changes, or bundling the broader crit/damage/defense/resistance/vulnerability/shear surfaces.
  - Post-completion controller refresh moved the durable active slice to `US-004`.
---

## 2026-06-14 17:02 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-004-close-focused-oracle-gaps-for-the-selected-candidate.md`, `scripts/ralph/investigations/2026-06-14-US-004-crit-rate-oracle-gap.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-004 focused oracle row` replaces the selected `Calculator.RegularMul.cal_crit_rate(data)` over-100% uncertainty with deterministic reader/retained parity evidence in `test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers[over-one-full-crit-received-boundary]`.
  - This story does not replace live production formula code, reader source, copied-output constructors, CalAnomaly paths, Stun array logic, event/runtime/listener paths, validation-runner wiring, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate: full `cal_crit_rate()` includes `crit_rate_received_increase` and can exceed 1.0; personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes received bonus and remains a retained contrast boundary.
  - `cal_crit_expect()`, crit damage, damage bonus, defense, resistance, vulnerability, base damage, retained-only sheer, arrays, `_CalculatorReadSnapshot` public fields, validation-runner profiles, registered teams/APLs, old containers, and layer-separation invariants remain unchanged.
- Next step:
  - Continue to `US-005` registered behavior sample eligibility audit for the selected `cal_crit_rate()` candidate. Do not create validation-only teams, fake APLs, fixture-only live routes, or retained-vs-retained main-loop samples.
---

## 2026-06-14 17:18 +08:00 - US-005
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-005-audit-registered-behavior-sample-eligibility.md`, `scripts/ralph/investigations/2026-06-14-US-005-crit-rate-registered-sample-eligibility.md`, `scripts/ralph/checkpoints/2026-06-14-us-005-crit-rate-registered-sample-eligibility.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-006-build-the-bounded-proposal-packet.md`
- Replacement note:
  - `US-005 crit-rate registered sample eligibility audit` replaces implicit main-loop-sample assumptions with retained conditional No-Go evidence for the selected `Calculator.RegularMul.cal_crit_rate(data)` candidate.
  - This story does not replace live production formula code, reader source, registered team/APL config, validation-runner behavior, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate: full `cal_crit_rate()` includes `crit_rate_received_increase`; personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes received bonus.
  - `莱特火属性队` / `./zsim/data/APLData/莱特-扳机-雨果.toml` is only a future conditional seed because `雨果` has 4-piece `啄木鸟电音`; current evidence still lacks a real registered nonzero `crit_rate_received_increase` route and current main-loop output does not expose formula-call counts.
  - `scripts/run_buff_main_loop_consistency.py` remains skipped for this docs/evidence story and may only be required by a later live production semantic diff with a real registered route and nonzero relevant counts.
  - Validation evidence: `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `142 passed`, and scoped mypy success on `9 source files`; known pytest-asyncio and async log-writer shutdown noise remained non-fatal after success markers.
- Next step:
  - Continue to `US-006` bounded proposal packet. Keep any future main-loop sample conditional on a later production semantic-diff branch, stop tick `1000`, runtime labels, exact total-damage comparison, unchanged Buff timeline comparison, and nonzero full-crit formula relevance from a real registered route.
---

## 2026-06-14 17:42 +08:00 - US-006
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-006-build-the-bounded-proposal-packet.md`, `scripts/ralph/investigations/2026-06-14-US-006-bounded-proposal-packet.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-007-run-retained-gates-and-reviewer-invariant-check.md`
- Replacement note:
  - `US-006 bounded proposal packet` replaces implicit implementation-readiness assumptions with a durable Conditional Go contract for one later PRD limited to `Calculator.RegularMul.cal_crit_rate(data)`.
  - This story only builds a boundary/proposal packet. It does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner behavior, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate: full `cal_crit_rate()` includes `crit_rate_received_increase`; personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes received bonus and remains the contrast boundary.
  - Rollback anchors retain source methods, focused crit tests, Buff docs, `formula-parity`, `calculator-reads`, and conditional `implicit-events`.
  - Live sample proof remains blocked until `莱特火属性队` / `./zsim/data/APLData/莱特-扳机-雨果.toml` or another real registered route proves nonzero full-crit formula relevance and nonzero `crit_rate_received_increase`; current main-loop output lacks formula-call counts.
  - Validation evidence: focused crit pytest exited `0` with `6 passed`; `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `142 passed`, and scoped mypy success on `9 source files`; `calculator-reads` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused suite `242 passed`, and scoped mypy success on `22 source files`.
- Next step:
  - Continue to `US-007` retained gates and reviewer invariant check. Do not start production implementation, broaden into `cal_crit_expect()` / other `RegularMul` branches, create validation-only routes, delete retained compatibility, rewrite validation-runner behavior, delete old containers, or merge event/runtime/listener layers.
---

## 2026-06-14 17:55 +08:00 - US-007
- Files changed: `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-007-run-retained-gates-and-reviewer-invariant-check.md`, `scripts/ralph/checkpoints/2026-06-14-us-007-retained-gates-reviewer-invariant-check.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool.md`
- Replacement note:
  - `US-007 retained verifier gate` replaces assertion-only proposal readiness with deterministic retained gate evidence and reviewer invariant verdict for the current `Calculator.RegularMul.cal_crit_rate(data)` proposal packet.
  - This story verifies a boundary and does not replace live production formula code, reader source, copied-output constructors, event/runtime/listener paths, validation-runner behavior, registered teams/APLs, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate retained boundaries; full `cal_crit_rate()` includes `crit_rate_received_increase`, while personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes it.
  - Validation evidence: focused reader pytest exited `0` with `142 passed`; `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `142 passed`, and scoped mypy success on `9 source files`; `calculator-reads` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader/guardrail suite `242 passed`, and scoped mypy success on `22 source files`.
  - `implicit-events` and full default validation remain skipped by touched-surface evidence: this PRD branch changed docs/Ralph evidence plus focused formula-oracle test evidence, not copied-output, event, dispatch/runtime, listener, dot-runtime, same-tick runtime write, lifecycle, validation-runner, or old-container surfaces.
- Next step:
  - Continue to `US-008` final handoff docs and same-phase candidate pool. Do not start production implementation or broaden beyond the bounded `Calculator.RegularMul.cal_crit_rate(data)` proposal contract.
---

## 2026-06-14 18:17 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/investigations/2026-06-14-US-008-docs-typecheck-scope.md`, `scripts/ralph/checkpoints/2026-06-14-us-008-regularmul-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-008 final handoff docs and same-phase candidate pool` replaces implicit next-cycle routing with long-lived docs that mark `Calculator.RegularMul.cal_crit_rate(data)` as the only selected candidate for one later bounded implementation PRD.
  - This story does not replace live production code. It records Conditional Go for a future implementation limited to `Calculator.RegularMul.cal_crit_rate(data)` and keeps live sample proof conditional on real registered-route evidence for nonzero selected full-crit relevance and nonzero `crit_rate_received_increase`.
- Compatibility retained:
  - Full crit / personal crit separation remains retained: full `cal_crit_rate()` includes `crit_rate_received_increase`; personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes it.
  - Old containers, `MultiplierData`, `MulData`, `DynamicStatement`, copied-output constructors, `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, listener broadcast, dot runtime registration, old Buff write paths, validation-runner behavior, and retained compatibility paths remain unchanged.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - `docs/旧Buff系统耦合审查结果.md` remains unchanged because this handoff found no new Buff coupling or coupling classification change.
- Next step:
  - Generate one bounded implementation PRD limited to `Calculator.RegularMul.cal_crit_rate(data)` from this packet, unless reviewer chooses another retained same-phase candidate with named evidence. Do not broaden into whole-Calculator rewrites, RegularMul branch bundling, retained-only sheer expansion, validation-runner rewrites, registered-team fixture creation, old-container deletion, or event/runtime/listener layer merges.
---

## 2026-06-14 18:46 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-lock-scope-and-source-baseline.md`, `scripts/ralph/plans/slices/us-002-implement-the-bounded-full-crit-formula-seam.md`, `scripts/ralph/checkpoints/2026-06-14-us-001-lock-scope-source-baseline.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-001 scope/source baseline checkpoint` replaces implicit current-route assumptions with explicit evidence that the active implementation PRD is bounded to `Calculator.RegularMul.cal_crit_rate(data)`.
  - This story does not replace a live production path, formula body, reader implementation, validation runner, registered sample, event/runtime/listener path, lifecycle container, old Buff container, copied-output path, CalAnomaly path, Stun path, retained-only sheer path, or any other `RegularMul` branch.
- Compatibility retained:
  - Root `Calculator.RegularMul.cal_crit_rate(data)` still includes `crit_rate_received_increase`; `CalculatorBuffAttributeReader.read_full_crit_rate(context)` still delegates through the retained formula path.
  - Full crit and personal crit remain separate boundaries; registered behavior sample proof remains conditional.
- Next step:
  - Continue with the next active story only after this baseline is recorded; any production implementation must stay limited to the selected full-crit path and preserve the listed non-goals.
---

## 2026-06-14 19:02 +08:00 - US-002
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-002-implement-the-bounded-full-crit-formula-seam.md`, `scripts/ralph/plans/slices/us-003-preserve-reader-and-personal-crit-contrast-boundaries.md`, `scripts/ralph/checkpoints/2026-06-14-us-002-bounded-full-crit-formula-seam.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `Calculator.RegularMul.cal_crit_rate(data)` helper seam replaces the inline full-crit scalar expression with module-local `_calculate_full_crit_rate(static_statement, dynamic_statement)`.
  - This story replaces only an internal formula-maintenance boundary; it does not replace reader snapshot construction, validation-runner behavior, registered teams/APLs, old Buff containers, copied-output constructors, event/runtime/listener paths, lifecycle containers, or retained compatibility paths.
- Compatibility retained:
  - The exact full crit formula remains `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate + dynamic.crit_rate_received_increase`.
  - `CalculatorBuffAttributeReader.read_full_crit_rate(context)` still delegates to `Calculator.RegularMul.cal_crit_rate(data)`.
  - Personal crit, crit expectation, crit damage, Stun, Anomaly, retained-only sheer, `_CalculatorReadSnapshot`, `MultiplierData`, `MulData`, `DynamicStatement`, and `Calculator.RegularMul.__init__` remain unchanged.
  - Validation evidence: focused crit pytest exited `0` with `8 passed`; `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `143 passed`, and scoped mypy success on `9 source files`.
- Next step:
  - Continue to `US-003` reader and personal-crit contrast verification. Do not broaden into registered-route sampling, validation-runner rewiring, old-container deletion, event/runtime/listener migration, or other `RegularMul` branches unless a later story explicitly authorizes it.
---

## 2026-06-14 19:16 +08:00 - US-003
- Files changed: `scripts/ralph/plans/slices/us-003-preserve-reader-and-personal-crit-contrast-boundaries.md`, `scripts/ralph/plans/slices/us-004-maintain-registered-sample-conditional-no-go.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 reader and personal-crit contrast verification` replaces implicit trust in the helper seam with deterministic focused evidence that the retained reader and formula boundaries still match.
  - This story verifies an existing boundary only. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `CalculatorBuffAttributeReader.read_full_crit_rate(context)` still builds the retained formula snapshot and delegates to `Calculator.RegularMul.cal_crit_rate(data)`.
  - Full crit still includes `crit_rate_received_increase`; `Calculator.RegularMul.cal_personal_crit_rate(data)` and `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` still exclude it.
  - Validation evidence: focused crit pytest exited `0` with `10 passed`; `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `143 passed`, and scoped mypy success on `9 source files`.
- Next step:
  - Continue to `US-004` registered-sample conditional No-Go. Keep main-loop sample evidence conditional on a later live semantic diff with a real registered route and nonzero selected full-crit relevance.
---

## 2026-06-14 19:29 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-maintain-registered-sample-conditional-no-go.md`, `scripts/ralph/checkpoints/2026-06-14-us-004-registered-sample-conditional-no-go.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-005-run-retained-formula-and-reader-gates-serially.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 registered-sample conditional No-Go` replaces implicit live-sample pressure with an explicit retained rule: a live main-loop sample is future-only unless a real production semantic diff and real registered route prove nonzero selected full-crit relevance plus nonzero `crit_rate_received_increase`.
  - This story verifies and records a boundary only. It does not replace live production formula code, reader source, registered teams/APLs, validation-runner behavior, event/runtime/listener paths, lifecycle containers, old Buff containers, copied-output paths, or retained compatibility paths.
- Compatibility retained:
  - `scripts/run_buff_main_loop_consistency.py` remains an explicit future entrypoint, not default evidence for this behavior-preserving slice.
  - `莱特火属性队` with `./zsim/data/APLData/莱特-扳机-雨果.toml` remains a future conditional seed only.
  - No validation-only teams, fake APLs, fixture-only routes, or retained-vs-retained main-loop samples were created.
  - Validation evidence: focused mypy exited `0` with `Success: no issues found in 2 source files`; known non-failure noise was existing `annotation-unchecked` notes.
- Next step:
  - Continue to `US-005` retained formula and reader gates. Keep `implicit-events`, default lifecycle validation, and main-loop consistency conditional on touched surfaces and real registered-route relevance.
---

## 2026-06-14 19:38 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-run-retained-formula-and-reader-gates-serially.md`, `scripts/ralph/checkpoints/2026-06-14-us-005-retained-formula-reader-gates.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-006-review-public-contracts-and-rollback-anchors.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 retained serial gates` replaces implicit post-implementation confidence with deterministic, serial verifier evidence for the selected full-crit formula and calculator reader contracts.
  - This story verifies existing boundaries only. It does not replace live production formula code, reader source, test source, validation-runner behavior, registered teams/APLs, copied-output paths, event/runtime/listener paths, dot runtime, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate retained boundaries; full `cal_crit_rate()` includes `crit_rate_received_increase`, while personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes it.
  - Validation evidence: selected crit nodes exited `0` with `10 passed`; full reader suite exited `0` with `143 passed`; `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `143 passed`, and scoped mypy success on `9 source files`; `calculator-reads` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader/guardrail suite `243 passed`, and scoped mypy success on `22 source files`.
  - `implicit-events` and full default validation remain skipped by touched-surface evidence: this verifier slice touched no copied-output, event, dispatch/runtime, listener, dot-runtime, same-tick runtime write, lifecycle, validation-runner, or old-container surface.
- Next step:
  - Continue to `US-006` public contract and rollback anchor review. Do not broaden into production implementation, validation-runner rewrites, registered-team fixtures, old-container deletion, or event/runtime/listener layer changes unless a later story explicitly authorizes that surface.
---

## 2026-06-14 19:48 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-review-public-contracts-and-rollback-anchors.md`, `scripts/ralph/investigations/2026-06-14-US-006-public-contract-rollback-anchors.md`, `scripts/ralph/checkpoints/2026-06-14-us-006-public-contract-rollback-anchors.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 public contract and rollback-anchor review` replaces implicit reviewer confidence with explicit evidence for the selected full-crit formula seam, personal-crit contrast, reader adapters, private snapshot adapter, focused crit tests, `formula-parity`, and `calculator-reads`.
  - This story verifies and records rollback boundaries only. It does not replace live production formula code, reader source, test source, validation-runner behavior, registered teams/APLs, copied-output paths, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Full crit and personal crit remain separate retained boundaries; full `cal_crit_rate()` includes `crit_rate_received_increase`, while personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes it.
  - `_CalculatorReadSnapshot` remains a private five-field adapter. `formula-parity` and `calculator-reads` remain the retained rollback gates for future formula/read changes.
  - Validation evidence: focused mypy exited `0` with `Success: no issues found in 2 source files`; known `annotation-unchecked` notes remained non-fatal.
- Next step:
  - Continue to `US-007` handoff-doc sync and same-phase candidate-pool preservation. Do not start new production work, validation-runner rewrites, registered-team fixtures, old-container deletion, or event/runtime/listener layer changes from this review slice.
---

## 2026-06-14 20:05 +08:00 - US-007
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-007-sync-buff-handoff-docs-without-collapsing-the-candidate-pool.md`, `scripts/ralph/plans/slices/us-008-record-ralph-evidence-and-prepare-next-intake.md`, `scripts/ralph/investigations/2026-06-14-US-007-docs-typecheck.md`, `scripts/ralph/checkpoints/2026-06-14-us-007-sync-buff-handoff-docs-candidate-pool.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/context_index.py`
- Replacement note:
  - `US-007 handoff-doc sync` replaces stale next-cycle routing with long-lived docs that mark `Calculator.RegularMul.cal_crit_rate(data)` implemented / no-op verified at handoff while preserving the same-phase candidate pool.
  - This story records implementation status and verifier evidence. It does not replace another live production formula path, reader contract, copied-output constructor, event/runtime/listener path, validation-runner behavior, registered team/APL, lifecycle container, old Buff container, or retained compatibility path.
- Compatibility retained:
  - Full crit and personal crit remain separate retained boundaries; full `cal_crit_rate()` includes `crit_rate_received_increase`, while personal `cal_personal_crit_rate()` / `read_personal_crit_rate()` excludes it.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - `docs/旧Buff系统耦合审查结果.md` remains unchanged because this handoff found no new Buff coupling or coupling classification change.
- Next step:
  - Continue to `US-008` Ralph evidence / next-intake preparation. The long-lived default next PRD is Phase-3 same-phase candidate selection / bounded proposal, not another `cal_crit_rate(data)` implementation follow-up unless regression or reviewer-named evidence reopens it.
---

## 2026-06-14 20:23 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-record-ralph-evidence-and-prepare-next-intake.md`, `scripts/ralph/plans/slices/buff-refactor-phase3-regularmul-crit-rate-bounded-production-implementation-next-intake.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/checkpoints/2026-06-14-us-008-record-ralph-evidence-next-intake.md`
- Replacement note:
  - `US-008 Ralph evidence and next-intake record` replaces chat-only completion assumptions with durable Ralph artifact evidence for the current RegularMul crit-rate implementation PRD.
  - This story is docs/evidence/bookkeeping only. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_rate(data)` remains implemented / no-op verified at handoff and is not the next default reopen target.
  - Same-phase candidates remain available only through named evidence: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - Completed copied-output, `cal_res_pen()`, AM/AP/impact, selected Stun, phase-1 surfaces, and P2 guarded buckets remain closed unless root-workspace source, focused regression, guardrail, validation, or reviewer-named evidence reopens them.
- Next step:
  - Generate the next PRD as Phase-3 same-phase candidate selection / bounded proposal. The default should select one exact candidate from the retained pool and must not collapse to broad formula rewrite, validation-runner rewrite, registered-team fixture creation, old-container deletion, event/runtime/listener layer merge, or retained compatibility deletion.
---

## 2026-06-14 21:54 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconcile-route-and-completed-scope.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 route and completed-scope reconciliation` replaces stale backlog assumptions with durable Ralph evidence that previous RegularMul crit-rate, selected Stun, copied-output, phase-1, AM/AP/impact, `cal_res_pen()`, and P2 guarded surfaces remain completed unless concrete guardrail / focused test / validation / root-source evidence reopens them.
  - This story only reconciles the next PRD route and evidence. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.StunMul.get_stun_array()` remains implemented through `_build_stun_multiplier_array(...)`; `Calculator.cal_stun()` remains the product consumer.
  - `Calculator.RegularMul.cal_crit_rate(data)` remains implemented / no-op verified at handoff through `_calculate_full_crit_rate(...)` and is not the default reopen target.
  - Same-phase candidate work remains routed to remaining RegularMul candidate matrix refresh / bounded proposal readiness rather than stale completed backlog.
- Next step:
  - Continue to `US-002` remaining RegularMul branch matrix refresh. Do not start direct production implementation, old-container deletion, validation-runner rewrite, event/runtime/listener layer work, or broad `Calculator.py` / `CalAnomaly.py` rewrite without a named blocker.
---

## 2026-06-14 22:12 +08:00 - US-002
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-002-refresh-regularmul-remaining-branch-matrix.md`, `scripts/ralph/plans/slices/us-003-select-one-exact-bounded-candidate-or-record-no-go.md`, `scripts/ralph/investigations/2026-06-14-US-002-regularmul-branch-matrix.md`, `scripts/ralph/checkpoints/2026-06-14-us-002-regularmul-remaining-branch-matrix-refresh.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-002 RegularMul remaining branch matrix refresh` replaces stale handoff-text branch selection with current-root evidence for each candidate's deterministic oracle coverage, missing rows, `_CalculatorReadSnapshot` dependency, registered-route eligibility, rollback anchors, and status.
  - This story records docs/evidence only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_rate(data)` remains implemented / no-op verified evidence only and is not the selected current next default.
  - Retained-only sheer remains blocked: `cal_base_attr(..., base_attr=4)` still depends on runtime `char_instance.sheer_attack_conversion_rate`, `_CalculatorReadSnapshot` still carries no `char_instance`, and current `tests/teams` registration has no real `仪玄` / Yixuan route.
  - Validation evidence: JSON sanity, Ralph tooling py_compile, and scoped mypy all exited `0`; focused reader pytest and Buff validation profiles were skipped because no production/test/reader/validation-runner source changed.
- Next step:
  - Continue to `US-003` exact candidate selection / No-Go. Do not inherit historical `cal_crit_rate(data)` selection, bundle all RegularMul branches, create validation-only teams, expand `_CalculatorReadSnapshot`, or broaden into production implementation without the active story authorizing it.
---

## 2026-06-14 22:27 +08:00 - US-003
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-003-select-one-exact-bounded-candidate-or-record-no-go.md`, `scripts/ralph/plans/slices/us-004-close-selected-candidate-oracle-gaps.md`, `scripts/ralph/investigations/2026-06-14-US-003-regularmul-candidate-decision.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-003 RegularMul candidate decision` replaces stale historical `cal_crit_rate(data)` selection assumptions with the current exact candidate `Calculator.RegularMul.cal_personal_crit_dmg(data)`.
  - This story records docs/evidence/bookkeeping only. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Implemented `Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` remains closed and no-op verified evidence only.
  - Full-vs-personal crit boundaries remain separate: selected personal crit damage excludes `received_crit_dmg_bonus`, while full `cal_crit_dmg(data)` remains the received-damage contrast branch.
  - Non-selected same-phase candidates remain follow-up pool, including base damage / base attr, damage bonus, personal crit rate, full crit damage, defense, resistance, vulnerability, retained-only sheer, arrays, registered behavior sample eligibility, P2 guarded maintenance, and retained compatibility.
- Next step:
  - Continue to `US-004` focused oracle / proposal-gap closure for `Calculator.RegularMul.cal_personal_crit_dmg(data)` only. Do not broaden into production implementation, full crit damage, `cal_crit_rate(data)`, `cal_crit_expect()`, validation-runner rewrite, registered-team fixture creation, old-container deletion, or event/runtime/listener layer work without an explicit later story.
---

## 2026-06-14 22:42 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-004-close-selected-candidate-oracle-gaps.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `docs/Buff重构替换说明.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-005-define-proposal-boundary-and-rollback-anchors.md`
- Replacement note:
  - `US-004 selected personal crit damage branch-matrix row` replaces the remaining deterministic oracle gap for `Calculator.RegularMul.cal_personal_crit_dmg(data)` with focused branch-matrix evidence alongside the existing full crit damage contrast boundary.
  - This story updates test evidence and Ralph bookkeeping only. It does not replace live production formula code, reader public contracts, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_dmg(data)` still reads `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`; full `cal_crit_dmg(data)` remains the received-damage contrast branch.
  - `_CalculatorReadSnapshot` stays unchanged and no runtime `char_instance` access, registered-route fixture, fake APL, main-loop sample, or retained-vs-retained compensation route was added.
  - Validation evidence: focused oracle / branch-matrix / boundary pytest passed with `27 passed`; retained-only sheer node passed with `1 passed`; `formula-parity` validation passed with base `2 passed`, isolated teams `3 passed`, focused reader `143 passed`, and scoped mypy success on `9 source files`.
- Next step:
  - Continue to `US-005` proposal boundary and rollback anchors for `Calculator.RegularMul.cal_personal_crit_dmg(data)` only. Do not broaden into production implementation, registered-route sample creation, `_CalculatorReadSnapshot` expansion, retained-only sheer, full crit damage, crit-rate reopening, or validation-runner rewrite without a later story authorizing it.
---

## 2026-06-14 22:58 +08:00 - US-005
- Files changed: `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-005-define-proposal-boundary-and-rollback-anchors.md`, `scripts/ralph/plans/slices/us-006-run-retained-gates-serially.md`, `scripts/ralph/investigations/2026-06-14-US-005-proposal-boundary-rollback-anchors.md`, `scripts/ralph/checkpoints/2026-06-14-us-005-proposal-boundary-rollback-anchors.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-005 proposal boundary and rollback anchors` prepares a later bounded implementation PRD to replace only `Calculator.RegularMul.cal_personal_crit_dmg(data)` with an equivalent local scalar helper if authorized.
  - This story is docs/evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The selected personal crit damage formula still reads `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`; full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch.
  - `_CalculatorReadSnapshot` remains private and does not carry `char_instance`; `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` remains the reader anchor.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, copied-output constructors, old Buff containers, `buff_add()`, `KickOutBuff()`, listener broadcast, dot runtime registration/removal, `formula-parity`, and `calculator-reads` remain retained boundaries.
- Next step:
  - Continue to `US-006` retained gate verification. Run selected focused pytest first, then serial `formula-parity` and `calculator-reads`; keep `implicit-events`, default lifecycle validation, and main-loop consistency conditional on future touched surfaces or live registered semantic diff evidence.
---

## 2026-06-14 23:17 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-run-retained-gates-serially.md`, `scripts/ralph/plans/slices/us-007-reviewer-and-invariant-gate.md`, `scripts/ralph/checkpoints/2026-06-14-us-006-retained-gates-serial-verification.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 retained serial gates` replaces implicit proposal-readiness confidence with deterministic serial verifier evidence for the selected `Calculator.RegularMul.cal_personal_crit_dmg(data)` route.
  - This story verifies existing boundaries only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, dot runtime, lifecycle containers, old Buff containers, same-tick runtime writes, or retained compatibility paths.
- Compatibility retained:
  - The selected personal crit damage formula still reads `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`; full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch.
  - `formula-parity` and `calculator-reads` are retained serial gates for a later bounded implementation PRD. `implicit-events`, default validation, and main-loop consistency remain conditional future gates tied to touched surfaces.
  - Known `pytest_asyncio` loop-scope warnings and post-success async log-writer shutdown output remain warning/noise, not verifier failures, when exit status and success markers show the command passed.
- Next step:
  - Continue to `US-007` reviewer and invariant gate. Do not start production implementation, validation-runner rewrite, registered-route fixture creation, old-container deletion, copied-output/event/runtime/listener changes, lifecycle changes, or retained compatibility deletion from this verifier slice.
---

## 2026-06-14 23:30 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-reviewer-and-invariant-gate.md`, `scripts/ralph/investigations/2026-06-14-US-007-reviewer-invariant-gate.md`, `scripts/ralph/checkpoints/2026-06-14-us-007-reviewer-invariant-gate.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 reviewer invariant gate` prepares a later production implementation PRD to replace only the `Calculator.RegularMul.cal_personal_crit_dmg(data)` route if authorized. This story does not replace a live production formula path.
  - The later implementation boundary must preserve `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`, keep `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` as the reader anchor, and preserve the full-vs-personal received-crit contrast.
- Compatibility retained:
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, synchronous listener broadcasts, copied-output constructors, old Buff containers, validation-runner wiring, lifecycle containers, registered routes, and retained compatibility paths remain untouched.
  - Existing raw queue / old-container compatibility surfaces remain retained and documented; this slice introduces no new raw queue or container passthrough.
- Next step:
  - Continue to `US-008` handoff-doc synchronization and same-phase candidate pool preservation. Do not start production implementation until the next PRD explicitly names `Calculator.RegularMul.cal_personal_crit_dmg(data)` and carries the retained validation gates.
---

## 2026-06-14 23:46 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-sync-handoff-docs-and-preserve-candidate-pool.md`, `scripts/ralph/checkpoints/2026-06-14-us-008-handoff-docs-and-same-phase-candidate-pool.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-008 handoff-doc sync` replaces stale current-default / selected-candidate routing with long-lived docs that name `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` as the Conditional Go target for one later bounded implementation PRD.
  - This story is docs/evidence/bookkeeping only. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The selected personal crit damage formula remains `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` and must continue to exclude `received_crit_dmg_bonus`; full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - `docs/旧Buff系统耦合审查结果.md` remains unchanged because this handoff found no new Buff coupling or coupling classification change.
- Next step:
  - Continue to `US-009` Ralph evidence / next-intake preparation. The long-lived default next PRD is a bounded `Calculator.RegularMul.cal_personal_crit_dmg(data)` implementation PRD, not broad RegularMul packaging, retained-only sheer shortcut, validation-runner rewrite, registered-team fixture creation, old-container deletion, event/runtime/listener layer merge, or retained compatibility deletion.
---

## 2026-06-15 01:21 +08:00 - US-009
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-009-record-ralph-evidence-and-prepare-next-intake.md`, `scripts/ralph/plans/slices/buff-refactor-phase3-regularmul-remaining-branch-bounded-proposal-readiness-next-intake.md`, `scripts/ralph/checkpoints/2026-06-15-us-009-record-ralph-evidence-next-intake.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/progress.txt`, `scripts/ralph/prd.json`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-009 Ralph evidence and next-intake closure` replaces chat-only PRD completion assumptions with durable Ralph artifact evidence, verifier commands, reviewer verdict, checkpoint, refreshed campaign state, and PRD completion bookkeeping.
  - This story is docs/evidence/bookkeeping only. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The selected next implementation PRD remains bounded to `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` and must preserve `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` while excluding `received_crit_dmg_bonus`.
  - Same-phase candidates remain available: registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - `docs/旧Buff系统耦合审查结果.md` remains unchanged because this evidence slice found no new Buff coupling or coupling classification change.
- Next step:
  - Generate the next PRD as Phase-3 RegularMul personal crit damage bounded implementation PRD. Do not broaden into full crit damage, `cal_crit_rate(data)`, `cal_crit_expect()`, retained-only sheer, array output, validation-runner rewrite, registered-team fixture creation, old-container deletion, event/runtime/listener layer merge, or retained compatibility deletion.
---

## 2026-06-15 01:43 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-scope-baseline-and-stop-conditions.md`, `scripts/ralph/plans/slices/us-002-personal-crit-damage-helper-seam-implementation.md`, `scripts/ralph/checkpoints/2026-06-15-us-001-scope-baseline-stop-conditions.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 scope baseline` replaces stale candidate-selection routing assumptions with current docs/state/source evidence for one bounded route: `Calculator.RegularMul.cal_personal_crit_dmg(data)` plus `CalculatorBuffAttributeReader.read_personal_crit_damage(context)`.
  - This story is docs/evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The selected personal crit damage formula remains `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` and continues to exclude `received_crit_dmg_bonus`.
  - Full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch, and the same-phase candidate pool remains available after this PRD.
- Next step:
  - Continue to `US-002` for only the personal crit damage helper seam implementation or no-op verification. Stop if the helper would require public interface expansion, `_CalculatorReadSnapshot` expansion, runtime `char_instance`, registered-team fixtures, validation-runner rewrites, old-container deletion, or event/runtime/listener work.
---

## 2026-06-15 01:59 +08:00 - US-002
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-002-personal-crit-damage-helper-seam-implementation.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 personal crit damage helper seam` replaces the inline `Calculator.RegularMul.cal_personal_crit_dmg(data)` sum with module-local `_calculate_personal_crit_damage(static_statement, dynamic_statement)`.
  - The helper computes only `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`; same-story focused coverage proves `cal_personal_crit_dmg(data)` delegates to the helper.
- Compatibility retained:
  - The public `Calculator.RegularMul.cal_personal_crit_dmg(data)` signature and return semantics remain unchanged, and `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` remains the reader anchor.
  - `received_crit_dmg_bonus`, full `Calculator.RegularMul.cal_crit_dmg(data)`, full/personal crit rate, `cal_crit_expect()`, arrays, `_CalculatorReadSnapshot`, `char_instance`, registered teams/APLs, validation-runner wiring, copied-output constructors, old Buff containers, dispatch/runtime/listener paths, lifecycle containers, same-tick runtime writes, and retained compatibility paths remain unchanged.
  - Validation evidence: focused pytest exited `0` with `12 passed, 132 deselected`; scoped mypy exited `0` with `Success: no issues found in 2 source files`. Existing pytest-asyncio and mypy untyped-body notes were non-fatal.
- Next step:
  - Continue to `US-003` reader anchor and full/personal contrast verification. Do not broaden into full crit damage replacement, crit-rate reopening, crit expectation, retained-only sheer, registered-team fixture creation, validation-runner rewrite, old-container deletion, or event/runtime/listener work without an explicit later story.
---

## 2026-06-15 02:14 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-003-reader-anchor-and-full-personal-contrast.md`, `scripts/ralph/checkpoints/2026-06-15-us-003-reader-anchor-full-personal-contrast.md`, `scripts/ralph/plans/slices/us-004-focused-oracle-and-regression-coverage.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 reader anchor guardrail` replaces chat-only confidence in `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` with focused test evidence that the reader still delegates to retained `Calculator.RegularMul.cal_personal_crit_dmg(data)` using reader-built snapshot inputs.
  - This story does not replace a live production formula path; it adds guardrail evidence for the existing reader seam.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_dmg(data)` remains the personal crit damage formula path and preserves `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`.
  - Full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch and continues to include `received_crit_dmg_bonus`.
  - `Soldier0AnbyCoreSkillCritDMGBonus.py`, P2-A through P2-G guardrails, old Buff compatibility paths, event/runtime/listener layers, validation-runner behavior, registered teams/APLs, lifecycle containers, old containers, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-004` focused oracle and regression coverage. Do not broaden into full crit damage replacement, crit-rate reopening, crit expectation, retained-only sheer, registered-team fixture creation, validation-runner rewrite, old-container deletion, or event/runtime/listener work without explicit later-story evidence.
---

## 2026-06-15 02:25 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-focused-oracle-and-regression-coverage.md`, `scripts/ralph/plans/slices/us-005-serial-retained-validation-gates.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 focused oracle coverage` replaces assertion-only confidence in the personal crit damage helper seam with verified deterministic oracle evidence already present in `tests/simulator/test_buff_attribute_reader.py`.
  - This story is a no-op source/test verification slice. It does not replace a live production formula path because existing coverage already proves `regular-crit-received-boundary`, migrated personal crit damage parity, crit-family received-boundary behavior, and the `regular_mul_branch_matrix` contrast.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_dmg(data)` remains delegated to `_calculate_personal_crit_damage(...)` and preserves `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg`.
  - Full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch and continues to include `received_crit_dmg_bonus`.
  - `Calculator.py`, focused reader tests, formula matrix docs, `formula-parity`, `calculator-reads`, event/runtime/listener layers, validation-runner behavior, registered teams/APLs, lifecycle containers, old containers, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-005` serial retained validation gates: run `formula-parity` first, then `calculator-reads`, and keep any known warning/noise separated from failures. Do not broaden into full crit damage replacement, crit-rate reopening, crit expectation, retained-only sheer, registered-team fixture creation, validation-runner rewrite, old-container deletion, or event/runtime/listener work without explicit later-story evidence.
---
## 2026-06-15 02:39 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-serial-retained-validation-gates.md`, `scripts/ralph/plans/slices/us-006-conditional-event-runtime-gate-decision.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 serial retained validation gates` replaces chat-only release-verifier confidence with durable serial validation evidence for the retained `formula-parity` and `calculator-reads` profiles.
  - This story is validation/evidence/bookkeeping only. It does not replace live production formula code, reader source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader suite `145 passed`, scoped mypy clean on `9 source files`, and `[验证完成] 所有步骤通过`.
  - `calculator-reads` ran only after `formula-parity` completed and exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused reader/guardrail suite `245 passed`, scoped mypy clean on `22 source files`, and `[验证完成] 所有步骤通过`.
  - Known pytest-asyncio loop-scope deprecation and post-success async log-writer shutdown traceback remain warning/noise, not validation failures.
- Next step:
  - Continue to `US-006` conditional event/runtime gate decision. Decide `implicit-events` and default validation from the actual touched surface; do not broaden into event/runtime/lifecycle, validation-runner rewrite, registered-team fixture creation, old-container deletion, or retained compatibility cleanup without explicit later-story evidence.
---

## 2026-06-15 02:49 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-conditional-event-runtime-gate-decision.md`, `scripts/ralph/plans/slices/us-007-registered-sample-eligibility-and-reviewer-gate.md`, `scripts/ralph/checkpoints/2026-06-15-us-006-conditional-event-runtime-gate-decision.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 conditional event/runtime gate decision` replaces unconditional validation-profile escalation with a recorded touched-surface decision for the committed personal crit damage implementation diff.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - The branch diff remains bounded to `Calculator.RegularMul.cal_personal_crit_dmg(data)`, `_calculate_personal_crit_damage(...)`, and focused personal-crit-damage reader/formula tests.
  - `implicit-events` remains conditional and was skipped because no copied-output, event queue, dispatch/runtime, listener, dot runtime, same-tick runtime write, old-container, lifecycle, registered-route, or validation-runner surface changed.
  - Default validation remains conditional and was skipped because no lifecycle container, same-tick runtime write path, default validation behavior, or validation-runner contract changed.
- Next step:
  - Continue to `US-007` registered sample eligibility and reviewer gate. Do not create validation-only teams, fake APLs, fixture-only routes, event/runtime/listener merges, validation-runner rewrites, old-container deletion, or retained compatibility cleanup.
---

## 2026-06-15 03:00 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-registered-sample-eligibility-and-reviewer-gate.md`, `scripts/ralph/checkpoints/2026-06-15-us-007-registered-sample-reviewer-gate.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 registered sample / reviewer gate` replaces chat-only eligibility claims with durable evidence that main-loop consistency remains conditional No-Go for the current personal crit damage implementation PRD.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - No validation-only team, fake APL, fixture-only route, retained-vs-retained sample, registered-route config, public contract change, deletion boundary, performance-sensitive path, or phase boundary was created or touched.
  - Event queue semantics, synchronous listener broadcasts, same-tick runtime writes, old containers, copied-output constructors, validation-runner behavior, registered routes, and retained compatibility paths remain unchanged.
  - Focused mypy exited `0` with `Success: no issues found in 2 source files`; existing `annotation-unchecked` notes were non-fatal.
- Next step:
  - Continue to `US-008` final handoff docs and same-phase candidate pool preservation. Do not collapse the future candidate pool to only personal crit damage or invent registered-route evidence without a future live semantic diff and real route relevance.
---

## 2026-06-15 03:09 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool-preservation.md`, `scripts/ralph/plans/slices/buff-refactor-phase3-regularmul-personal-crit-rate-bounded-proposal-readiness-next-intake.md`, `scripts/ralph/checkpoints/2026-06-15-us-008-handoff-docs-same-phase-candidate-pool-preservation.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-008 final handoff docs` replaces stale next-default wording that still treated `Calculator.RegularMul.cal_personal_crit_dmg(data)` as the next implementation PRD with completed implemented / no-op verified handoff evidence.
  - `Calculator.RegularMul.cal_personal_crit_dmg(data)` now delegates to `_calculate_personal_crit_damage(...)`; this handoff records that state and does not replace additional live formula, reader, validation-runner, registered-route, copied-output, event/runtime/listener, lifecycle, old-container, or retained compatibility paths.
- Compatibility retained:
  - The selected personal crit damage formula remains `static.crit_damage + dynamic.crit_dmg + dynamic.field_crit_dmg` and continues to exclude `received_crit_dmg_bonus`; full `Calculator.RegularMul.cal_crit_dmg(data)` remains the received-damage contrast branch.
  - Same-phase pool remains registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - No new Buff coupling or coupling-classification change was found, so `docs/旧Buff系统耦合审查结果.md` remains unchanged.
- Next step:
  - Generate the next PRD as Phase-3 same-phase candidate selection / bounded proposal. Pick one exact retained-pool surface and keep rollback anchors, focused tests, scoped mypy, registered-sample conditions, retained gates, and non-goals; do not continue by default with another personal crit damage implementation PRD.
---

## 2026-06-15 03:34 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-active-route-and-candidate-intake.md`, `scripts/ralph/investigations/2026-06-15-US-001-active-route-candidate-intake.md`, `scripts/ralph/checkpoints/2026-06-15-us-001-active-route-candidate-intake.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-002-personal-crit-rate-source-and-reader-contract-audit.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 active route intake` replaces stale or chat-only routing assumptions with durable evidence that the current default is Phase-3 same-phase candidate selection / bounded proposal.
  - This story is docs/controller evidence only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Copied-output handler/report implementation, `Calculator.AnomalyMul.cal_res_pen()` selector extraction, AM/AP/impact helper implementation, selected Stun implementation, `Calculator.RegularMul.cal_crit_rate(data)`, and `Calculator.RegularMul.cal_personal_crit_dmg(data)` remain closed prior work and are not reopened by this PRD intake.
  - `.codex_worktrees/` remains excluded from current production evidence; CodeGraph historical-worktree hits were treated as navigation noise.
  - Focused Ralph typecheck exited `0` with `Success: no issues found in 2 source files`, and `py_compile` over the same controller scripts exited `0`.
- Next step:
  - Continue to `US-002` personal crit rate source and reader contract audit. Keep the next slice limited to `Calculator.RegularMul.cal_personal_crit_rate(data)`, `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`, focused oracle/reader evidence, rollback anchors, and explicit No-Go conditions.
---

## 2026-06-15 03:47 +08:00 - US-002
- Files changed: `scripts/ralph/plans/slices/us-002-personal-crit-rate-source-and-reader-contract-audit.md`, `scripts/ralph/investigations/2026-06-15-US-002-personal-crit-rate-contract-audit.md`, `scripts/ralph/checkpoints/2026-06-15-us-002-personal-crit-rate-contract-audit.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-003-deterministic-oracle-and-focused-test-gap-review.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 personal crit rate contract audit` replaces chat-only confidence in the selected source / reader boundary with durable evidence for `Calculator.RegularMul.cal_personal_crit_rate(data)` and `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`.
  - This story is audit/evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` still computes only `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate`.
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` still builds `_CalculatorReadSnapshot` through `_build_formula_snapshot(context)` and delegates to the public formula.
  - `crit_rate_received_increase` remains excluded from personal crit rate; `Calculator.RegularMul.cal_crit_rate(data)` and `_calculate_full_crit_rate(...)` remain unchanged full-crit contrast anchors.
  - No `_CalculatorReadSnapshot` public field expansion, `char_instance`, runtime view, array output, copied-output payload, old Buff container access, event/runtime/listener change, lifecycle change, or retained compatibility deletion occurred.
- Next step:
  - Continue to `US-003` deterministic oracle and focused test gap review. Keep the scope limited to personal crit rate oracle/reader evidence; stop if a later slice needs production helper extraction, snapshot expansion, registered routes, validation-runner rewrite, copied-output/event/runtime/lifecycle work, or old-container access.
---

## 2026-06-15 04:00 +08:00 - US-003
- Files changed: `scripts/ralph/plans/slices/us-003-deterministic-oracle-and-focused-test-gap-review.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-004-proposal-boundary-rollback-anchors-and-stop-conditions.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 deterministic oracle review` replaces informal personal crit rate parity confidence with durable focused-test evidence that existing rows are sufficient for later bounded work.
  - This story is review/evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Existing focused rows cover personal-only field/flat crit rate, received-only full-vs-personal contrast, and over-one full crit received-boundary behavior.
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` still excludes `crit_rate_received_increase`; `Calculator.RegularMul.cal_crit_rate(data)` and `_calculate_full_crit_rate(...)` remain unchanged full-crit contrast anchors.
  - No new deterministic row was needed; `cal_crit_rate()`, `cal_crit_dmg()`, `cal_personal_crit_dmg()`, `cal_crit_expect()`, damage bonus, defense, resistance, vulnerability, base damage, retained-only sheer, and Stun arrays remained out of selected scope.
- Next step:
  - Continue to `US-004` proposal boundary, rollback anchors, and stop conditions. Keep any later production proposal limited to personal crit rate helper extraction or record an explicit No-Go if it would touch full crit, crit damage, arrays, runtime/event/lifecycle layers, validation-runner wiring, registered routes, or retained compatibility cleanup.
---

## 2026-06-15 04:10 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-proposal-boundary-rollback-anchors-and-stop-conditions.md`, `scripts/ralph/investigations/2026-06-15-US-004-proposal-boundary-rollback-anchors.md`, `scripts/ralph/checkpoints/2026-06-15-us-004-proposal-boundary-rollback-anchors.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 proposal boundary packet` replaces chat-only bounded-proposal assumptions with durable rollback anchors and stop conditions for `Calculator.RegularMul.cal_personal_crit_rate(data)`.
  - This story does not replace live production formula code. It defines the only later production surface and the only acceptable module-local scalar-helper shape if a future implementation PRD proceeds.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` remains the retained public formula path and still computes only `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate`.
  - Any future `_calculate_personal_crit_rate(static_statement, dynamic_statement)` helper must preserve that exact expression and must not accept received crit, judge, enemy, `char_instance`, runtime views, arrays, copied-output payloads, or full/personal bundled state.
  - Rollback anchors retain the current method body, `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` delegate, focused personal/full crit tests, `formula-parity`, `calculator-reads`, and Buff handoff docs.
  - No production source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths changed.
- Next step:
  - Continue to `US-005` registered behavior sample eligibility audit. Do not create validation-only teams, fake APLs, fixture-only routes, `cal_crit_rate()` reopenings, full/personal crit bundles, validation-runner rewrites, old-container deletion, or event/runtime/listener layer merges.
---

## 2026-06-15 04:24 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-registered-behavior-sample-eligibility-audit.md`, `scripts/ralph/investigations/2026-06-15-US-005-registered-behavior-sample-eligibility.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 registered behavior sample eligibility audit` replaces chat-only main-loop sample assumptions with durable Conditional No-Go evidence for the current personal crit rate proposal-readiness PRD.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, or retained compatibility paths.
- Compatibility retained:
  - Existing registered teams/APLs remain unchanged: `席德大安比队`, `莱特火属性队`, `薇薇安物理队`, and `青衣雷属性队`.
  - Main-loop consistency was skipped because there is no live production semantic diff and no real registered route currently proves nonzero selected `Calculator.RegularMul.cal_personal_crit_rate(data)` relevance inside an explicit stop tick.
  - A future eligible sample must include `team`, `apl`, `stop_tick`, runtime labels, total damage comparison, relevant nonzero count, event counts, Buff timeline comparison, and `matches=true`.
- Next step:
  - Continue to `US-006` retained validation profile gate. Keep validation serial and do not run main-loop consistency without a future live semantic diff plus real registered-route nonzero selected formula relevance.
---

## 2026-06-15 04:35 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-retained-validation-profile-gate.md`, `scripts/ralph/checkpoints/2026-06-15-us-006-retained-validation-profile-gate.md`, `scripts/ralph/plans/slices/us-007-reviewer-and-invariant-go-no-go-decision.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 retained validation profile gate` replaces chat-only validation confidence with durable serial `formula-parity` evidence and exact conditional skip reasons for the current personal crit rate proposal-readiness PRD.
  - This story is validation/evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` remains the retained public formula path and still computes only `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate`.
  - Required `formula-parity` exited `0` with base simulator `2 passed`, isolated teams `3 passed`, focused formula suite `145 passed`, and mypy success on `9 source files`; known async shutdown noise appeared only after success markers.
  - `calculator-reads` was skipped because no reader seams, snapshot construction, reader guardrails, or shared focused reader tests changed.
  - `implicit-events` and default validation were skipped because no copied-output, event/runtime/listener, dot runtime, lifecycle, runtime write path, validation-runner behavior, registered route, old-container, or retained compatibility surface changed.
- Next step:
  - Continue to `US-007` reviewer and invariant Go / No-Go decision. Keep that story to proposal judgment for one later bounded personal crit rate implementation PRD or explicit No-Go; do not introduce production formula, reader, event/runtime, lifecycle, validation-runner, registered-route, or retained compatibility changes.
---

## 2026-06-15 04:56 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-reviewer-and-invariant-go-no-go-decision.md`, `scripts/ralph/investigations/2026-06-15-US-007-personal-crit-rate-go-no-go-decision.md`, `scripts/ralph/checkpoints/2026-06-15-us-007-personal-crit-rate-go-no-go-decision.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool-preservation.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 personal crit rate Go / No-Go packet` replaces chat-only reviewer judgment with durable conditional Go evidence for one later bounded implementation PRD.
  - This story is decision/evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - The only future allowed production surface is `Calculator.RegularMul.cal_personal_crit_rate(data)` plus an optional module-local `_calculate_personal_crit_rate(static_statement, dynamic_statement)` helper that preserves `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate`.
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` remains a retained delegate anchor through `_build_formula_snapshot(context)`.
  - `ScheduleDispatchPort`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `BuffRuntimeReadPort`, `LegacyBuffRuntimeFacade`, old containers, copied-output constructors, listener broadcast, dot runtime registration/removal, and retained compatibility remain untouched anchors.
  - Main-loop registered-route evidence remains conditional on a later live semantic diff plus real registered-route nonzero selected personal-crit-rate relevance.
- Next step:
  - Continue to `US-008` handoff docs and same-phase candidate pool preservation. Carry the conditional Go forward without collapsing the future candidate pool to only personal crit rate.
---

## 2026-06-15 05:13 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-candidate-pool-preservation.md`, `scripts/ralph/checkpoints/2026-06-15-us-008-handoff-docs-same-phase-candidate-pool-preservation.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-008 final handoff docs` replaces stale next-default wording that still stopped at same-phase selection with durable evidence that the current default can be one bounded personal-crit-rate implementation PRD.
  - This handoff does not replace live production formula code. A future implementation may only add an equivalent helper seam for `Calculator.RegularMul.cal_personal_crit_rate(data)` that preserves `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` and excludes `crit_rate_received_increase`.
- Compatibility retained:
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` remains the reader delegate anchor; `_CalculatorReadSnapshot` remains private and does not gain `char_instance`, runtime view, array output, copied-output payload, or public field expansion.
  - Full `Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` remains the received-crit contrast branch; completed personal crit damage, Stun, copied-output, AM/AP/impact, `cal_res_pen()`, and P2-A through P2-G guarded buckets remain closed evidence, not reopened backlog.
  - Same-phase pool remains registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - No new Buff coupling or coupling-classification change was found, so `docs/旧Buff系统耦合审查结果.md` remains unchanged.
- Next step:
  - Generate one bounded personal-crit-rate implementation PRD only if it keeps the exact helper surface, focused personal/full crit tests, scoped mypy, retained `formula-parity`, conditional reader/event gates, registered-sample conditions, rollback anchors, stop conditions, and non-goals. After that PRD, reselect from the same-phase pool instead of chaining another personal-crit-rate follow-up.
---

## 2026-06-15 05:41 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-lock-scope-and-baseline.md`, `scripts/ralph/plans/slices/us-002-personal-crit-rate-helper-seam.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-001 lock-scope baseline` replaces chat-only next-route assumptions with durable evidence that this production-implementation PRD is limited to `Calculator.RegularMul.cal_personal_crit_rate(data)` plus optional module-local `_calculate_personal_crit_rate(static_statement, dynamic_statement)`.
  - This story does not replace live production formula code, reader code, focused tests, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - Root `Calculator.RegularMul.cal_personal_crit_rate(data)` still computes only `static.crit_rate + dynamic.crit_rate + dynamic.field_crit_rate` and excludes `crit_rate_received_increase`.
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` remains the reader delegate anchor through `_build_formula_snapshot(context)`.
  - Full `Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)`, personal crit damage, Stun, AM/AP/impact, copied-output, dispatch/runtime/listener, same-tick write, old-container, and retained compatibility boundaries remain unchanged.
- Next step:
  - Continue to `US-002` only for an equivalent personal crit-rate helper seam or explicit No-Go. Do not broaden into full crit, crit damage, other RegularMul branches, `_CalculatorReadSnapshot` public expansion, registered-route fabrication, validation-runner rewrites, copied-output/event/runtime/lifecycle paths, old-container deletion, or retained compatibility cleanup.
---

## 2026-06-15 05:51 +08:00 - US-002
- Files changed: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `scripts/ralph/plans/slices/us-002-personal-crit-rate-helper-seam.md`, `scripts/ralph/plans/slices/us-003-reader-anchor-and-full-personal-contrast.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `_calculate_personal_crit_rate(static_statement, dynamic_statement)` prepares to replace the inline body of `Calculator.RegularMul.cal_personal_crit_rate(data)` as the bounded local personal-crit-rate formula seam.
  - The helper computes only `static_statement.crit_rate + dynamic_statement.crit_rate + dynamic_statement.field_crit_rate`.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` keeps its public signature and return semantics while delegating to the module-local helper.
  - `_calculate_full_crit_rate(...)` remains the full crit contrast branch and still includes `crit_rate_received_increase`; personal crit, the new helper, crit damage, personal crit damage, reader snapshot contracts, event/runtime/listener paths, validation-runner behavior, copied-output payloads, old containers, and retained compatibility paths were not broadened.
- Next step:
  - Continue to `US-003` reader anchor and full/personal contrast verification. Do not expand `_CalculatorReadSnapshot`, add received-crit state to the personal path, fabricate registered routes, or reopen unrelated RegularMul branches without new evidence.
---

## 2026-06-15 06:00 +08:00 - US-003
- Files changed: `scripts/ralph/plans/slices/us-003-reader-anchor-and-full-personal-contrast.md`, `scripts/ralph/checkpoints/2026-06-15-us-003-reader-anchor-full-personal-contrast.md`, `scripts/ralph/plans/slices/us-004-focused-oracle-and-scoped-typecheck.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-003 reader anchor and full/personal contrast verification` replaces stale crit-damage slice evidence with durable personal-crit-rate reader-boundary evidence.
  - This story is verification/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` still builds `_build_formula_snapshot(context)` and delegates to `Calculator.RegularMul.cal_personal_crit_rate(data)`.
  - `_CalculatorReadSnapshot` remains private and does not gain `char_instance`, runtime view, array output, copied-output payload, or public field expansion.
  - Full crit remains on `_calculate_full_crit_rate(...)` / `Calculator.RegularMul.cal_crit_rate(data)` and includes `crit_rate_received_increase`; personal crit remains on `_calculate_personal_crit_rate(...)` / `Calculator.RegularMul.cal_personal_crit_rate(data)` and excludes it.
- Next step:
  - Continue to `US-004` focused oracle and scoped typecheck without widening into registered-route fabrication, validation-runner rewrites, event/runtime/listener paths, old-container deletion, or unrelated RegularMul branches.
---

## 2026-06-15 06:13 +08:00 - US-004
- Files changed: `scripts/ralph/plans/slices/us-004-focused-oracle-and-scoped-typecheck.md`, `scripts/ralph/plans/slices/us-005-retained-validation-gate-decisions.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-004 focused oracle and scoped typecheck` replaces chat-only confidence in the helper extraction with durable oracle/typecheck evidence and rollback anchors.
  - This story is verification/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - `regular-crit-received-boundary`, full/personal crit parity, and crit-family received-boundary tests already lock full crit as including `crit_rate_received_increase` and personal crit as excluding it; no new oracle row was needed.
  - Focused pytest exited `0` with `35 passed, 110 deselected`; scoped mypy exited `0` with `Success: no issues found in 2 source files`.
  - Rollback anchors remain `Calculator.py`, `test_buff_attribute_reader.py`, `docs/Buff公式候选与测试目标清单.md`, this replacement note, serial `formula-parity`, and conditional `calculator-reads`.
- Next step:
  - Continue to `US-005` retained validation gate decisions. Keep `formula-parity` and `calculator-reads` serial, and only add `implicit-events`, default validation, or main-loop consistency if the active story's touched surfaces justify them.
---

## 2026-06-15 06:21 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-retained-validation-gate-decisions.md`, `scripts/ralph/checkpoints/2026-06-15-us-005-retained-validation-gate-decisions.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-006-registered-sample-eligibility.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 retained validation gate checkpoint` replaces chat-only gate selection with durable serial `formula-parity` evidence and explicit conditional skip rationale for retained reader/event/default validation profiles.
  - This story is verification/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` remains on the bounded helper seam and still excludes `crit_rate_received_increase`.
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` remains the reader delegate anchor through `_build_formula_snapshot(context)`.
  - `_CalculatorReadSnapshot`, event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, old containers, copied-output payloads, validation-runner contracts, registered routes, and retained compatibility paths remain unchanged.
  - `calculator-reads`, `implicit-events`, and default validation remain conditional for later slices whose touched surfaces trigger them.
- Next step:
  - Continue to `US-006` registered sample eligibility. Do not fabricate registered routes or run main-loop consistency unless a later live semantic diff plus a real registered route with nonzero relevant events justifies it.
---

## 2026-06-15 06:35 +08:00 - US-006
- Files changed: `scripts/ralph/plans/slices/us-006-registered-sample-eligibility.md`, `scripts/ralph/checkpoints/2026-06-15-us-006-registered-sample-eligibility.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 registered sample eligibility checkpoint` replaces chat-only main-loop sample assumptions with durable Conditional No-Go evidence for this helper-seam PRD.
  - This story is verification/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `scripts/run_buff_main_loop_consistency.py` remains an explicit sample runner and was not executed by default for this behavior-preserving helper extraction.
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` remains on the bounded helper seam and still excludes `crit_rate_received_increase`.
  - No validation-only team, fake APL, fixture-only route, retained-vs-retained sample, registered-route data, event/runtime/listener path, or validation-runner behavior was created or changed.
- Next step:
  - Continue to `US-007` reviewer invariant and rollback gate. Keep registered behavior sample eligibility in the same-phase pool until a later live production semantic diff plus a real registered direct-crit route proves nonzero selected personal-crit-rate relevance inside an explicit stop tick.
---

## 2026-06-15 06:47 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-reviewer-invariant-and-rollback-gate.md`, `scripts/ralph/investigations/2026-06-15-US-007-reviewer-invariant-rollback-gate.md`, `scripts/ralph/checkpoints/2026-06-15-us-007-reviewer-invariant-and-rollback-gate.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 reviewer invariant and rollback gate` replaces chat-only reviewer confidence with durable invariant, changed-file boundary, compatibility, and rollback-anchor evidence for the current personal crit-rate implementation PRD.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output constructors/payloads, event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` remains the public personal crit-rate formula path and delegates to `_calculate_personal_crit_rate(...)`, which still excludes `crit_rate_received_increase`.
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` remains the reader delegate anchor through `_build_formula_snapshot(context)`, and `_CalculatorReadSnapshot` remains private without runtime view, `char_instance`, array output, copied-output payload, or public field expansion.
  - Full `Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` remains the received-crit contrast branch and still includes `crit_rate_received_increase`.
  - Focused crit tests, retained `formula-parity`, conditional `calculator-reads`, retained Buff docs, event queue semantics, synchronous listener broadcasts, same-tick runtime writes, old containers, copied-output constructors, validation-runner behavior, registered routes, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-008` handoff docs and same-phase pool preservation. Keep that slice docs/evidence-scoped unless it discovers a concrete source/doc mismatch requiring a smaller blocker slice.
---

## 2026-06-15 07:00 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-pool-preservation.md`, `scripts/ralph/checkpoints/2026-06-15-us-008-handoff-docs-and-same-phase-pool-preservation.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`
- Replacement note:
  - `US-008 final handoff docs` replaces stale next-default wording that still pointed to personal crit rate as the next implementation with durable evidence that `Calculator.RegularMul.cal_personal_crit_rate(data)` is already implemented / no-op verified through `_calculate_personal_crit_rate(...)`.
  - This handoff slice does not replace additional live production formula code. The implementation result remains the bounded helper seam added earlier in this PRD: `_calculate_personal_crit_rate(static_statement, dynamic_statement)` computes only `static_statement.crit_rate + dynamic_statement.crit_rate + dynamic_statement.field_crit_rate`.
- Compatibility retained:
  - `Calculator.RegularMul.cal_personal_crit_rate(data)` keeps its public signature and excludes `crit_rate_received_increase`.
  - `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` remains the reader delegate anchor through `_build_formula_snapshot(context)`, and `_CalculatorReadSnapshot` remains private without runtime view, `char_instance`, array output, copied-output payload, or public field expansion.
  - Full `Calculator.RegularMul.cal_crit_rate(data)` / `_calculate_full_crit_rate(...)` remains the received-crit contrast branch; completed personal crit damage, selected Stun, copied-output, AM/AP/impact, `cal_res_pen()`, old containers, event/runtime/listener layers, validation-runner behavior, registered routes, retained compatibility, and P2-A through P2-G guarded buckets remain closed unless new evidence reopens them.
  - Same-phase pool remains registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - No new Buff coupling or coupling-classification change was found, so `docs/旧Buff系统耦合审查结果.md` remains unchanged.
- Next step:
  - Generate the next PRD from Phase-3 same-phase candidate selection / bounded proposal, not another personal-crit-rate follow-up. Select one exact retained candidate, record focused tests, scoped mypy, registered-sample conditions, rollback anchors, retained gates, non-goals, and stop conditions before implementation.
---

## 2026-06-15 07:33 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconcile-current-intake-and-select-exact-candidate.md`, `scripts/ralph/investigations/2026-06-15-US-001-active-route-candidate-intake.md`, `scripts/ralph/checkpoints/2026-06-15-us-001-intake-verdict.md`, `scripts/ralph/plans/slices/us-002-baseline-full-crit-damage-source-and-oracle-coverage.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-001 current intake reconciliation` replaces stale completed-surface route assumptions with current-root evidence that the active default is Phase 3 same-phase candidate selection / bounded proposal for full crit damage proposal-readiness.
  - This story records route and candidate evidence only; it does not replace a live production formula path, reader source, focused test, validation profile, dispatch adapter, runtime port, listener path, registered route, old container, or retained compatibility path.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains open and inline as the full crit-damage candidate for later source / oracle inventory; recent `cal_crit_rate(data)`, `cal_personal_crit_dmg(data)`, and `cal_personal_crit_rate(data)` implementation handoffs remain closed evidence and are not reopened by this slice.
  - Event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, validation-runner behavior, old containers, registered routes, and retained compatibility paths remain unchanged.
  - No new Buff coupling or coupling-classification change was found, so `docs/旧Buff系统耦合审查结果.md` remains unchanged.
- Next step:
  - Continue only to `US-002` for current root source and oracle coverage inventory for `Calculator.RegularMul.cal_crit_dmg(data)`. Do not implement formula helpers, add public full-crit-damage reader APIs, fabricate registered routes, or broaden into unrelated RegularMul / CalAnomaly / Stun / copied-output / event-runtime-listener work in the intake slice.
---

## 2026-06-15 07:45 +08:00 - US-002
- Files changed: `scripts/ralph/plans/slices/us-002-baseline-full-crit-damage-source-and-oracle-coverage.md`, `scripts/ralph/checkpoints/2026-06-15-us-002-baseline-full-crit-damage-source-and-oracle-coverage.md`, `scripts/ralph/plans/slices/us-003-add-focused-label-branch-oracle-evidence.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 full crit damage source and oracle inventory` replaces chat-only baseline assumptions with durable current-root evidence for `Calculator.RegularMul.cal_crit_dmg(data)`.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - Full `Calculator.RegularMul.cal_crit_dmg(data)` still includes `static.crit_damage`, `dynamic.crit_dmg`, `dynamic.field_crit_dmg`, optional `dynamic.aftershock_attack_crit_dmg_bonus`, `dynamic.received_crit_dmg_bonus`, and the `min(5, crit_dmg)` cap.
  - Completed `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `_calculate_personal_crit_damage(...)` remains contrast evidence only and is not bundled into this full crit damage proposal-readiness PRD.
  - `CalculatorBuffAttributeReader.read_full_crit_damage(...)` is not a public root API and is not authorized by this PRD.
  - Event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, old containers, validation-runner behavior, registered routes, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-003` only for focused deterministic label-branch oracle evidence. Do not implement helper extraction, add public full-crit-damage reader APIs, expand `_CalculatorReadSnapshot`, fabricate registered routes, or broaden into unrelated RegularMul / CalAnomaly / Stun / copied-output / event-runtime-listener work.
---

## 2026-06-15 08:00 +08:00 - US-003
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-003-add-focused-label-branch-oracle-evidence.md`, `scripts/ralph/checkpoints/2026-06-15-us-003-focused-label-branch-oracle-evidence.md`, `scripts/ralph/plans/slices/us-004-verify-contrast-boundaries-and-snapshot-contract.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `regular-crit_dmg-aftershock-label-and-received-exact` and `regular-crit_dmg-aftershock-label-and-received-cap` replace inferred label-branch parity with deterministic full crit damage oracle evidence.
  - This story builds test evidence only. It does not replace live production formula code, reader source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains the retained inline production formula and still caps with `min(5, crit_dmg)`.
  - `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `_calculate_personal_crit_damage(...)` remains completed contrast evidence and still excludes label and received full-crit-damage bonuses.
  - `CalculatorBuffAttributeReader.read_full_crit_damage(...)` remains absent and unauthorized by this PRD.
- Next step:
  - Continue to `US-004` contrast-boundary and snapshot-contract verification. Do not implement helper extraction, add public full-crit-damage reader APIs, fabricate registered routes, or broaden into unrelated RegularMul / CalAnomaly / Stun / copied-output / event-runtime-listener work.
---

## 2026-06-15 08:16 +08:00 - US-004
- Files changed: `tests/simulator/test_buff_attribute_reader.py`, `scripts/ralph/plans/slices/us-004-verify-contrast-boundaries-and-snapshot-contract.md`, `scripts/ralph/investigations/2026-06-15-US-004-contrast-boundary-snapshot-contract.md`, `scripts/ralph/checkpoints/2026-06-15-us-004-contrast-boundary-snapshot-contract.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `test_full_crit_damage_reader_api_and_snapshot_contract_stay_bounded` replaces chat-only contrast-boundary review with executable guardrail evidence for full crit damage received-damage inclusion, personal crit damage exclusion, private snapshot field bounds, and absence of `CalculatorBuffAttributeReader.read_full_crit_damage(...)`.
  - This story builds test/evidence only. It does not replace live production formula code, reader source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains the retained inline production formula and still includes `received_crit_dmg_bonus`.
  - `Calculator.RegularMul.cal_personal_crit_dmg(data)` / `_calculate_personal_crit_damage(...)` and `CalculatorBuffAttributeReader.read_personal_crit_damage(context)` remain the personal contrast path and still exclude `received_crit_dmg_bonus`.
  - `_CalculatorReadSnapshot` remains private with only `static`, `dynamic`, `judge_node`, `enemy_obj`, and `char_level`; no `char_instance`, runtime view, array output, copied-output payload, or public field expansion was added.
- Next step:
  - Continue to `US-005` bounded proposal and rollback anchors. Keep the next slice proposal-scoped unless it explicitly permits production helper extraction; do not add a public full-crit-damage reader API or broaden into unrelated RegularMul / CalAnomaly / Stun / copied-output / event-runtime-listener work.
---

## 2026-06-15 08:31 +08:00 - US-005
- Files changed: `scripts/ralph/plans/slices/us-005-define-bounded-proposal-and-rollback-anchors.md`, `scripts/ralph/investigations/2026-06-15-US-005-full-crit-damage-proposal-rollback-anchors.md`, `scripts/ralph/checkpoints/2026-06-15-us-005-full-crit-damage-proposal-rollback-anchors.md`, `scripts/ralph/evidence-ledger.md`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-005 full crit damage proposal packet` replaces chat-only implementation-boundary confidence with a durable proposal / rollback artifact for exactly `Calculator.RegularMul.cal_crit_dmg(data)`.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered routes, copied-output/event/runtime/listener paths, old containers, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains the retained inline production formula and still preserves the `aftershock_attack` label branch, `received_crit_dmg_bonus`, and `min(5, crit_dmg)` cap.
  - Any later helper must be private, module-local, behavior-preserving, and keep the current public method signature plus `SkillNode` assertion. This PRD still does not authorize `CalculatorBuffAttributeReader.read_full_crit_damage(...)`.
  - `Calculator.RegularMul.cal_crit_expect(data)`, damage bonus, defense, resistance, vulnerability, retained-only sheer, public snapshot fields, validation-runner behavior, registered teams/APLs, old containers, event/runtime/listener layers, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-006` registered sample eligibility for this exact full crit damage surface. Keep `US-006` evidence-scoped unless it finds a concrete current-root blocker that needs a smaller reversible slice.
---

## 2026-06-15 09:05 +08:00 - US-006
- Files changed: `tasks/prd-buff-refactor-phase3-regularmul-full-crit-damage-bounded-proposal-readiness.md`, `scripts/ralph/plans/slices/us-006-decide-registered-sample-eligibility.md`, `scripts/ralph/investigations/2026-06-15-US-006-registered-sample-eligibility.md`, `scripts/ralph/checkpoints/2026-06-15-us-006-full-crit-damage-registered-sample-eligibility.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-006 registered sample eligibility decision` replaces chat-only main-loop sample assumptions with durable Conditional No-Go evidence for this full-crit-damage proposal-readiness PRD.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output/event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - Existing registered teams/APLs remain unchanged: `青衣雷属性队`, `席德大安比队`, `莱特火属性队`, and `薇薇安物理队`; `示例冰属性队` remains ineligible because it is not registered and its APL file is missing.
  - Main-loop consistency remains skipped because there is no live production semantic diff and no current registered route proves nonzero selected `Calculator.RegularMul.cal_crit_dmg(data)` relevance inside an explicit stop tick.
  - Event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, old containers, validation-runner behavior, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-007` retained validation gates. Keep validation serial and do not run main-loop consistency unless a later live production semantic diff plus a real registered direct-damage route proves nonzero selected full-crit-damage relevance inside an explicit stop tick.
---

## 2026-06-15 09:09 +08:00 - US-007
- Files changed: `scripts/ralph/plans/slices/us-007-run-retained-validation-gates-serially.md`, `scripts/ralph/checkpoints/2026-06-15-us-007-retained-validation-gates-serial.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-007 retained validation gate checkpoint` replaces chat-only validation confidence with durable serial `formula-parity` evidence plus touched-surface skip rationales for retained profiles.
  - This story is evidence/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output/event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains the retained inline production formula for the full-crit-damage proposal-readiness PRD.
  - `CalculatorBuffAttributeReader`, `_CalculatorReadSnapshot`, `tests/simulator/test_buff_attribute_reader.py`, `scripts/run_buff_refactor_validation.py`, old containers, event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, registered routes, and retained compatibility paths remain unchanged.
  - `calculator-reads`, `implicit-events`, and default validation were skipped by concrete touched-surface criteria, not by omission.
- Next step:
  - Continue to `US-008` handoff docs and same-phase pool preservation. Keep handoff docs broad enough for future PRD generation and do not collapse the same-phase pool to this validation slice.
---

## 2026-06-15 09:17 +08:00 - US-008
- Files changed: `docs/Buff重构下阶段计划草稿.md`, `docs/Buff公式候选与测试目标清单.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/plans/slices/us-008-handoff-docs-and-same-phase-pool-preservation.md`, `scripts/ralph/checkpoints/2026-06-15-us-008-handoff-docs-and-same-phase-pool-preservation.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- Replacement note:
  - `US-008 full crit damage final handoff` replaces single-slice routing assumptions with durable next-intake evidence: Conditional Go for one later bounded implementation PRD limited to `Calculator.RegularMul.cal_crit_dmg(data)` plus an optional behavior-preserving module-local helper.
  - This story is handoff/docs/bookkeeping only. It does not replace live production formula code, reader source, focused test source, validation-runner behavior, registered teams/APLs, copied-output/event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains the retained inline production formula for this proposal-readiness PRD until a later implementation PRD explicitly lands the bounded helper seam.
  - Any later helper must preserve static crit damage, dynamic crit damage, field crit damage, `aftershock_attack` label bonus, `received_crit_dmg_bonus`, `min(5, crit_dmg)` cap, public signature, and current `SkillNode` assumption.
  - `CalculatorBuffAttributeReader.read_full_crit_damage(...)` remains absent and unauthorized; `_CalculatorReadSnapshot`, `CalculatorBuffAttributeReader`, old containers, event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, registered routes, validation-runner behavior, and retained compatibility paths remain unchanged.
  - Same-phase pool remains registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if named evidence appears, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules.
  - No new Buff coupling or coupling-classification change was found, so `docs/旧Buff系统耦合审查结果.md` remains unchanged.
- Next step:
  - Generate one bounded full-crit-damage implementation PRD only if it preserves the documented formula behavior and retained gates. After that PRD completes or records No-Go, reselect from the broader same-phase pool instead of chaining stale single-branch follow-ups.
---

## 2026-06-15 10:26 +08:00 - US-001
- Files changed: `scripts/ralph/plans/slices/us-001-reconcile-intake-and-active-route.md`, `scripts/ralph/checkpoints/2026-06-15-us-001-reconcile-intake-active-route.md`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `scripts/ralph/plans/slices/us-002-lock-the-full-crit-damage-helper-boundary.md`, `docs/Buff重构替换说明.md`, `scripts/ralph/prd.json`
- Replacement note:
  - `US-001 active-route reconciliation checkpoint` replaces stale route assumptions with durable evidence that the current default is one bounded implementation PRD for `Calculator.RegularMul.cal_crit_dmg(data)`.
  - This story is docs/bookkeeping only. It does not replace live production formula code, focused test source, reader source, validation-runner behavior, registered teams/APLs, copied-output/event/runtime/listener paths, lifecycle containers, old Buff containers, same-tick runtime write paths, or retained compatibility paths.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains the retained inline production formula until a later story explicitly implements the bounded helper seam.
  - The prior proposal-readiness PRD remains complete and records Conditional Go only for this exact full-crit-damage implementation surface.
  - `CalculatorBuffAttributeReader.read_full_crit_damage(...)` remains absent and unauthorized; `_CalculatorReadSnapshot`, old containers, event queue semantics, synchronous listener broadcasts, same-tick runtime writes, explicit ports/adapters, registered routes, validation-runner behavior, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-002` to lock the helper boundary from current root source before any production edit. Stop with No-Go if source/docs/state name a different route, a completed implementation, or any public-reader/snapshot/registered-fixture/adjacent-formula/layer-merge requirement.
---

## 2026-06-15 10:43 +08:00 - US-002
- Files changed: `scripts/ralph/plans/slices/us-002-lock-the-full-crit-damage-helper-boundary.md`, `scripts/ralph/investigations/2026-06-15-US-002-full-crit-damage-helper-boundary.md`, `scripts/ralph/checkpoints/2026-06-15-us-002-full-crit-damage-helper-boundary.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`, `scripts/ralph/campaign-dashboard.md`, `scripts/ralph/evidence-ledger.md`, `scripts/ralph/state/migration-board.json`, `scripts/ralph/state/hotspots.json`, `docs/Buff重构替换说明.md`
- Replacement note:
  - `US-002 full crit damage helper boundary packet` replaces chat-only helper-seam confidence with durable source, No-Go, and verifier evidence for the later `_calculate_full_crit_damage(static_statement, dynamic_statement, judge_node)` candidate.
  - This story prepares a boundary only. It does not replace live production formula code and does not add the helper/delegation hunk; `US-003` owns any production implementation.
- Compatibility retained:
  - `Calculator.RegularMul.cal_crit_dmg(data)` remains inline and still includes `static.crit_damage`, `dynamic.crit_dmg`, `dynamic.field_crit_dmg`, optional `dynamic.aftershock_attack_crit_dmg_bonus`, `dynamic.received_crit_dmg_bonus`, and `min(5, crit_dmg)`.
  - The public `Calculator.RegularMul.cal_crit_dmg(data)` signature and current `SkillNode` assertion remain intact.
  - `CalculatorBuffAttributeReader.read_full_crit_damage(...)` remains absent and unauthorized; `_CalculatorReadSnapshot`, registered fixtures, adjacent RegularMul formulas, validation-runner behavior, old containers, event/runtime/listener layers, and retained compatibility paths remain unchanged.
- Next step:
  - Continue to `US-003` only for the bounded helper/delegation production diff if it preserves this exact boundary. Stop with No-Go if implementation requires public reader API expansion, snapshot expansion, registered fixture creation, adjacent formula changes, layer merge, old-container deletion, or retained compatibility cleanup.
---
