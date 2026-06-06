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
---
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
