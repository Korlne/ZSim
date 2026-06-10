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
