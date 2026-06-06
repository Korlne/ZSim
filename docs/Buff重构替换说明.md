# Buff重构替换说明

## 用�?

- 记录每一�?Ralph �?Buff 重构里实际新增的边界、适配层或运行路径替换�?
- 只做增量追加，不重写历史结论�?
- 每轮都要更新；如果本轮还没有直接替换旧运行路径，也要明确写出“本轮仅铺边界，尚未正式替换”�?

## 追加格式

```text
## [日期时间] - [Story ID / PRD 切片]
- 本轮文件：`file_a`, `file_b`
- 替换说明�?
  - `新文�?/ 新入�?/ 新边界` 替换或准备替�?`旧文�?/ 旧入�?/ 旧字�?/ 旧职责`
- 兼容保留�?
  - 本轮仍保留的旧路径、旧容器或旧副作�?
- 下一步：
  - 下一轮应继续收口的旧路径
---
```

## 2026-06-05 - 调查�?PRD 收口基线

- 本轮文件：`docs/旧Buff系统耦合审查结果.md`, `docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草�?md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明�?
  - 本轮未直接替换旧 Buff 运行路径；当前交付的是生命周期、事件模型、runtime seam、Calculator seam 与验证入口的调查结论，用来约束下一轮实现型 PRD 的真实替换动作�?
- 兼容保留�?
  - `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` 仍是计划事件的旧发布入口�?
  - `exist_buff_dict` / `DYNAMIC_BUFF_DICT` / `LOADING_BUFF_DICT` 仍是�?runtime 容器主事实源�?
  - `Calculator` �?`MultiplierData` 的直接依赖仍保留，尚未切到独立属性读取接口�?
- 下一步：
  - 下一轮优先落地事件发布入口、`EventContext` runtime view 与最小适配层，并从该轮开始在本文档记录真实的新旧路径替换关系�?
---
## 2026-06-05 13:28:48 - US-001
- 本轮文件：`zsim/sim_progress/data_struct/schedule_dispatch.py`, `tests/simulator/test_schedule_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?
  - `ScheduleDispatchPort / LegacyEventListScheduleDispatchAdapter / create_schedule_dispatch_port()` �?`JudgeTools.find_event_list()` �?`schedule_data.event_list.append(...)` 之间先铺一层计划事件发布边界，但本轮尚未改写具体生产者�?
- 兼容保留�?
  - `schedule_data.event_list` 仍是底层计划队列，适配器继续沿用原�?`append` 顺序语义�?
  - `JudgeTools.find_event_list()`、`SchedulePreload`、`QuickAssistSystem` 等旧发布路径仍保留，等待后续逐个迁移�?
- 下一步：
  - 优先�?`SchedulePreload` 改为通过 dispatch gateway 发布，再继续收拢 `QuickAssistSystem` 等低风险生产者�?
---
## 2026-06-05 13:45:10 - US-002
- 本轮文件：`zsim/sim_progress/data_struct/SchedulePreload.py`, `tests/simulator/test_schedule_preload_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?
  - `schedule_preload_event_factory()` 现通过 `create_schedule_dispatch_port()` 发布 `SchedulePreload`，替�?`JudgeTools.find_event_list()` + `event_list.append(...)` 的计划事件直写入口�?
- 兼容保留�?
  - `schedule_data.event_list` 仍是底层计划队列，`LegacyEventListScheduleDispatchAdapter` 继续保持原有 `append` 顺序语义�?
  - `QuickAssistSystem` 等其他计划事件生产者仍保留旧直写路径，本轮只迁�?`SchedulePreload`�?
- 下一步：
  - 继续�?`QuickAssistSystem` 等低风险计划事件生产者迁�?dispatch gateway�?
---
## 2026-06-05 13:55:24 - US-003
- 本轮文件：`zsim/sim_progress/data_struct/QuickAssistSystem/__init__.py`, `tests/simulator/test_quick_assist_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?
  - `QuickAssistSystem.answer_assist()` / `spawn_event_group()` 现通过 `create_schedule_dispatch_port()` 发布 `QuickAssistEvent`，替�?QuickAssistSystem 内部直写 `JudgeTools.find_event_list()` + `event_list.append(...)` 的计划事件入口�?
- 兼容保留�?
  - `schedule_data.event_list` 仍是底层计划队列，`QuickAssistEventHandler` 与既有调度排序逻辑保持不变�?
  - `UpdateAnomaly`、`PolarizedAssaultEvent` 等其他计划事件生产者仍保留旧直写路径，本轮只迁�?`QuickAssistSystem`�?
- 下一步：
  - �?`ScheduledEvent` / `EventContext` 上接�?`buff_runtime_view`，开始替�?raw `dynamic_buff` / `exist_buff_dict` 读口�?
---
## 2026-06-05 14:08:10 - US-004
- 本轮文件：`zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/sim_progress/ScheduledEvent/__init__.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `tests/simulator/test_buff_runtime_view.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?
  - `BuffRuntimeReadPort / LegacyBuffRuntimeReadAdapter / create_buff_runtime_read_port()` �?`EventContext.buff_runtime_view` 开始替�?`EventContext.dynamic_buff` / `exist_buff_dict` 作为 handler 主读口；兼容 getter 现改为经�?runtime view 委托�?
- 兼容保留�?
  - `ScheduleData.dynamic_buff`、`exist_buff_dict` �?`sim_instance` 仍保留在调度链路中，`SkillEventHandler`、`ScheduleBuffSettle()`、`update_anomaly()` 仍通过兼容 getter 读取旧容器�?
  - 本轮尚未迁移具体 anomaly-family handler �?runtime view 的细粒度读方法，只先完成上下文接线与兼容适配�?
- 下一步：
  - �?`anomaly`、`abloom`、`disorder`、`polarity_disorder` 这组低风�?handler 直接通过 `buff_runtime_view` 读取所需 Buff 数据，减少对 raw dict 兼容 getter 的依赖�?
---
## 2026-06-05 14:31:15 - US-005
- 本轮文件：`zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/abloom.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/disorder.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/polarity_disorder.py`, `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, `zsim/sim_progress/ScheduledEvent/Calculator.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?
  - `BaseEventHandler / EventContext` 新增 active-buff read view accessor，开始替�?anomaly-family handler �?raw `dynamic_buff` / `exist_buff_dict` 的主读口�?
  - `AnomalyEventHandler / AbloomEventHandler / DisorderEventHandler / PolarityDisorderEventHandler` 现通过 `buff_runtime_view` 读取 active Buff；仅 `AnomalyEventHandler -> ScheduleBuffSettle()` 保留 legacy 容器作为�?tick 写边界�?
- 兼容保留�?
  - `ScheduleBuffSettle()`、`update_anomaly()` 与其他会原地修改容器的旧路径仍通过 legacy getter 读取原始容器，本轮未替换 live write path�?
- 下一步：
  - 继续把更高风险的 `skill` handler �?read path �?legacy getter 收口�?runtime view，并评估是否需要后�?write facade�?
---
## 2026-06-05 18:09:00 - US-006
- 本轮文件：`zsim/utils/main_loop_consistency.py`, `scripts/run_buff_main_loop_consistency.py`, `tests/simulator/test_main_loop_consistency.py`, `scripts/run_buff_refactor_validation.py`, `zsim/define.py`
- 替换说明�?  - `scripts/run_buff_main_loop_consistency.py` / `zsim.utils.main_loop_consistency` 把文档中的主循环一致性占位命令替换成真实可运行入口，并固�?`team / apl / total_damage / event_counts / buff_timeline / differences` 输出契约�?  - `implicit-events` typecheck profile 现纳入该入口与其 utility，开始把“主循环一致性验证命令”本身也收进当前 Buff 基础设施切片的验证边界�?
- 兼容保留�?
  - 当前 `--legacy-runtime` / `--candidate-runtime` 仅作为报告标签记录；live simulator 仍未消费 `config.buff_runtime.mode`，本轮尚未实现真正的新旧 runtime 切换�?
  - 比对命令继续复用现有 `Simulator`、`prepare_dmg_data_and_cache()` �?`prepare_buff_data_and_cache()` 结果链路，因�?session/result id 仍需保持旧链路兼容的纯数字格式�?
- 下一步：
  - 为后�?runtime 切换落地真实�?`legacy/candidate` 执行开关，再让该入口输出真正的新旧 runtime 一致性证据，而不只是同一 runtime 的双跑比较骨架�?---

## 2026-06-05 20:33:37 - US-001
- 本轮文件：`zsim/sim_progress/Update/UpdateAnomaly.py`, `tests/simulator/test_update_anomaly_dispatch.py`
- 替换说明�?  - `UpdateAnomaly.update_anomaly()` / `remove_dots_cause_disorder()` 现通过 `create_schedule_dispatch_port()` 发布 `new_anomaly`、`disorder` �?freeze follow-up 计划事件，替换该路径里对 `event_list.append(...)` 的直接依赖�?- 兼容保留�?  - `spawn_output()` 仍只负责构造异常对象并触发同步 listener broadcast，本轮没有把广播、计划入队与 runtime 立即写混成单一入口�?  - `PolarizedAssaultEvent`、`YanagiPolarityDisorderTrigger`、`BattleEventListener` 等其�?producer 仍保�?raw 队列写法，等待后续故事继续迁移�?- 下一步：
  - 继续收口 `BattleEventListener` 与其他剩�?producer �?raw 队列写入口，并评估是否需要让 `spawn_output()` 的其他调用方也统一�?dispatch gateway�?---
## 2026-06-05 18:49:32 - US-007
- 本轮文件：`zsim/utils/runtime_benchmark.py`, `scripts/run_buff_runtime_benchmark.py`, `tests/simulator/test_runtime_benchmark.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?  - `scripts/run_buff_runtime_benchmark.py` / `zsim.utils.runtime_benchmark` 把文档中�?Buff runtime 性能验证占位命令替换成真实可运行入口，并固化 `team / apl / stop_tick / total_runtime_ms / hotspots / comparisons` 输出契约�?  - `implicit-events` typecheck profile 现纳�?benchmark 入口与其 utility，开始把“性能验证命令”本身也收进当前 Buff 基础设施切片的验证边界�?- 兼容保留�?  - 当前 `--legacy-runtime` / `--candidate-runtime` 仍仅作为报告标签记录；live simulator 仍未消费 `config.buff_runtime.mode`，本轮尚未实现真正的新旧 runtime 切换�?  - 本轮 `hotspots` �?`simulator_run`、damage 报表后处理与 buff 报表后处理三段阶段级计时，不�?live runtime 内部细粒度探针�?- 下一步：
  - 为后�?runtime 切换落地真实�?`legacy/candidate` 执行开关，并在需要时把阶段级 hotspot 继续下钻�?live simulator 内部的真实热点探针�?---
## 2026-06-05 18:57:20 - US-008
- 本轮文件：`docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草�?md`, `docs/Buff重构替换说明.md`, `docs/旧Buff系统耦合审查结果.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明�?  - 文档基线现明确记�?`SchedulePreload` / `QuickAssistSystem` 已改�?`ScheduleDispatchPort`，`anomaly` / `abloom` / `disorder` / `polarity_disorder` 已改�?`buff_runtime_view`，以�?`scripts/run_buff_main_loop_consistency.py` / `scripts/run_buff_runtime_benchmark.py` 已替换旧的占位验证入口�?- 兼容保留�?  - 本轮仅同步阶�?1 基线文档�?PRD 状态，未新�?live runtime 替换路径�?  - `UpdateAnomaly`、`BattleEventListener`、部�?`BuffXLogic` / `PolarizedAssaultEvent` 计划事件生产者仍保留旧直写路径；高风�?`skill` handler �?runtime write facade 仍未收口�?- 下一步：
  - 下一轮继续留在阶�?1，收口剩余计划事件生产者与高风�?read/write 边界，不扩到 `Calculator` 全量迁移或旧容器删除�?---
## 2026-06-05 20:50:55 - US-002
- 本轮文件：`zsim/sim_progress/data_struct/BattleEventListener/AliceDotTriggerListener.py`, `tests/simulator/test_alice_dot_trigger_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?  - `AliceDotTriggerListener._create_dispatch_port()` / `dispatch_port.publish_scheduled(dot.anomaly_data)` 开始替�?`BattleEventListener` 内部 Alice 强击 Dot �?`schedule_data.event_list.append(...)` 的直接计划事件发布入�?- 兼容保留�?  - �?tick �?Dot 替换、旧 Dot 移除以及 `listener_manager` 同步广播触发链保持不变；底层计划队列仍由 `LegacyEventListScheduleDispatchAdapter` 追加
- 下一步：
  - 继续收口 `PolarizedAssaultEvent`、代表�?`BuffXLogic` 等剩�?raw 队列 producer；本轮尚未替�?live runtime 写边�?---
## 2026-06-05 21:29:15 - US-003
- 本轮文件：`zsim/sim_progress/ScheduledEvent/buff_runtime.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/context.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/base.py`, `tests/simulator/test_buff_runtime_view.py`
- 替换说明�?  - `EventContext.get_runtime_*()` / `BaseEventHandler._get_context_runtime_*()` 开始把 `buff_runtime_view` �?active-buff �?snapshot 读口显式提升为高风险 handler 可直接依赖的主读契约，减少后续迁移继续默认使�?`dynamic_buff` / `exist_buff_dict` 兼容 getter�?- 兼容保留�?  - `get_dynamic_buff()`、`get_exist_buff_dict()` �?`get_legacy_*()` 仍保留旧容器身份，仅标记为同 tick 写边界兼容口；本轮没有引入新�?write facade，也没有替换 `ScheduleBuffSettle()`、`update_anomaly()` �?live write path�?- 下一步：
  - 继续挑选一个高风险 `skill` handler 切到 `get_runtime_*()` 读口，并只在确实需要同 tick 原地写旧容器时保�?legacy getter�?---

## 2026-06-05 21:45:20 - US-004
- 本轮文件：`zsim/sim_progress/ScheduledEvent/event_handlers/handlers/skill.py`, `tests/simulator/test_skill_handler_runtime_view.py`, `scripts/run_buff_refactor_validation.py`
- 替换说明�?  - `SkillEventHandler` 现在�?`buff_runtime_view.get_active_buff_view()` 作为 `Calculator` �?`update_anomaly()` 的主 Buff 读口，准备替换技能事件处理路径对 raw `dynamic_buff` 的默认依赖�?- 兼容保留�?  - `ScheduleBuffSettle()` 仍通过 `get_legacy_dynamic_buff_dict()` / `get_legacy_exist_buff_dict()` 拿旧容器身份；本轮没有引入新�?write facade，也尚未替换�?tick 写边界�?- 下一步：
  - 继续收口剩余高风�?skill-side read/write 边界，只在确实需要同 tick 写旧容器的地方再评估最�?write facade�?---
## 2026-06-05 22:25:00 - US-005
- 本轮文件：`docs/Buff系统重构Checklist.md`, `docs/Buff重构下阶段计划草�?md`, `docs/Buff重构替换说明.md`, `docs/旧Buff系统耦合审查结果.md`, `scripts/ralph/prd.json`, `scripts/ralph/progress.txt`
- 替换说明�?  - 本轮没有新增 live runtime 替换路径；只同步阶段 1 交接基线，明�?`UpdateAnomaly` �?`BattleEventListener` 中的 `AliceDotTriggerListener` 已改�?`ScheduleDispatchPort`，`SkillEventHandler` 已把 runtime view 作为�?Buff 读口�?- 兼容保留�?  - 代表�?`BuffXLogic` / `PolarizedAssaultEvent` 与其余未迁移监听器入口仍保留 raw 队列发布；`ScheduleBuffSettle()`、`update_anomaly()` 等同 tick 写边界仍依赖 legacy 容器身份，本轮没有引入新�?write facade�?  - `--legacy-runtime` / `--candidate-runtime` 仍只是报告标签，live simulator 尚未消费 `config.buff_runtime.mode`�?- 下一步：
  - 继续�?[Buff重构方案.md](./Buff重构方案.md) 的阶�?1 路线，优先收口代表�?`BuffXLogic` / `PolarizedAssaultEvent` producer 与同 tick 写边界的最�?write facade / command port�?---
## 2026-06-05 23:39:09 - US-001
- 本轮文件：`zsim/sim_progress/Buff/BuffXLogic/AlicePolarizedAssaultTrigger.py`、`tests/simulator/test_alice_polarized_assault_trigger_dispatch.py`、`scripts/run_buff_refactor_validation.py`
- 替换说明�?  - `AlicePolarizedAssaultTrigger._create_dispatch_port()` / `dispatch_port.publish_scheduled(event)` 替换 `AlicePolarizedAssaultTrigger.special_effect_logic()` 内对 `schedule_data.event_list.append(...)` 的直�?planned-event 写入�?- 兼容保留�?  - `PolarizedAssaultEvent.execute()` 里的 anomaly / disorder follow-up planned events 仍直接写 `event_list.append(...)`�?  - `listener_manager.broadcast_event()` 的同步广播语义未改动，本轮只收口 planned-event 入队边界�?- 下一步：
  - 继续�?`PolarizedAssaultEvent` �?follow-up producer 迁到 dispatch gateway，完成这条代表性事件链的收口�?---
## 2026-06-05 23:51:20 - US-002
- 本轮文件：`zsim/sim_progress/data_struct/PolarizedAssaultEventClass.py`、`tests/simulator/test_polarized_assault_event_dispatch.py`、`scripts/run_buff_refactor_validation.py`
- 替换说明�?  - `PolarizedAssaultEvent._create_dispatch_port()` / `dispatch_port.publish_scheduled(...)` 替换 `PolarizedAssaultEvent.execute()` �?anomaly �?disorder follow-up planned-event �?`schedule_data.event_list.append(...)` 的直写入�?- 兼容保留�?  - `listener_manager.broadcast_event()` 的同步广播语义与 `anomaly_effect_active()` 的同 tick 状态更新顺序保持不�?  - `schedule_data.event_list` 仍由 `LegacyEventListScheduleDispatchAdapter` 作为底层计划队列承接
- 下一步：
  - 继续�?`SkillEventHandler` 引入最�?write facade / command port，收�?`update_anomaly()` �?`ScheduleBuffSettle()` 的同 tick 写边�?---
## 2026-06-06 00:22:24 - US-003
- 本轮文件：`zsim/sim_progress/ScheduledEvent/runtime_command.py`、`zsim/sim_progress/ScheduledEvent/__init__.py`、`zsim/sim_progress/ScheduledEvent/event_handlers/context.py`、`zsim/sim_progress/ScheduledEvent/event_handlers/base.py`、`tests/simulator/test_runtime_command_port.py`、`scripts/run_buff_refactor_validation.py`
- 替换说明�?  - `RuntimeCommandPort / LegacyRuntimeCommandAdapter / create_runtime_command_port()` 先把 `update_anomaly()` �?`ScheduleBuffSettle()` 包进显式 same-tick 写边界，为后续替�?`SkillEventHandler` �?`get_legacy_*()` 的默认写协作做准�?- 兼容保留�?  - `SkillEventHandler`、`AnomalyEventHandler` 目前仍通过 legacy getter 间接走旧写路径，本轮只新增边界并把它接进 `ScheduledEvent` / `EventContext`
  - `event_list`、`dynamic_buff`、`exist_buff_dict` 仍由旧容器承载；新端口只保持对象身份并避免缓存过期队列引�?- 下一步：
  - �?`US-004` �?`SkillEventHandler` �?same-tick `update_anomaly()` / `ScheduleBuffSettle()` 调用改为显式�?`runtime_command_port`
---
## 2026-06-06 00:42:45 - US-004
- 本轮文件：`zsim/sim_progress/ScheduledEvent/event_handlers/handlers/skill.py`、`zsim/sim_progress/ScheduledEvent/runtime_command.py`、`tests/simulator/test_skill_handler_runtime_view.py`、`tests/simulator/test_runtime_command_port.py`
- 替换说明�?  - `SkillEventHandler` 现通过 `RuntimeCommandPort.update_anomaly()` / `RuntimeCommandPort.settle_buffs()` 替换处理器内部默认依�?legacy getter 再直�?`update_anomaly()` / `ScheduleBuffSettle()` �?same-tick 写协作路�?- 兼容保留�?  - `RuntimeCommandPort` 仍由 `LegacyRuntimeCommandAdapter` 承接�?`event_list`、`dynamic_buff`、`exist_buff_dict` 身份，只在适配器内部保留旧写路径兼�?  - 本轮没有替换 live runtime 容器本身，只�?`SkillEventHandler` 的读写分层显式化
- 下一步：
  - 继续补强代表�?producer �?write-boundary 组合�?focused validation，并保持后续 handler 迁移沿用 `runtime view` 读、`runtime command` 写的边界
---
## 2026-06-06 00:59:56 - US-005
- �����ļ���`scripts/run_buff_refactor_validation.py`, `tests/simulator/test_skill_handler_runtime_view.py`, `tests/simulator/test_basic_simulator.py`
- �滻˵����
  - `scripts/run_buff_refactor_validation.py` ��� `implicit-events` focused pytest ��Ƭ��ʼ�滻 `progress.txt` ����ɢ��һ���������Ϊ������ `BuffXLogic` producer / `PolarizedAssaultEvent` producer / same-tick write-boundary �Ĺ�����֤��ڡ�
  - `test_skill_handler_runtime_view.py` ���� `SkillEventHandler -> RuntimeCommandPort -> legacy containers` ���ݶ��ԣ���ʼ�滻��ֻ֤�����÷���������֤�������������Ա����������������衣
  - `test_basic_simulator.py` �ѵ���� `TestSimulator` helper �ĳɷ� `Test*` �������滻 pytest �� `tests/test_simulator.py` �����첽���� / �ڴ����������ռ�·����
- ���ݱ�����
  - ����û������ live runtime ·���滻��`ScheduleDispatchPort` �� `RuntimeCommandPort` ��ͨ�� legacy adapters �нӾɶ��к;��������ݡ�
  - ��֤�ű�ֻ�������� `sessions` ���������ظ� `session_id` ������û�иĶ� simulator ��ʵ����ʱ�����ݽṹ��ҵ��˳��
- ��һ����
  - `US-006` Ӧ�ѡ������� producer ���ѱպϡ�same-tick write facade ����ء�focused validation �ѹ̻������� gate��ͬ�����׶� 1 handoff �ĵ���
---
## 2026-06-06 01:17:59 - US-006
- 本轮文件：docs/Buff系统重构Checklist.md, docs/Buff重构下阶段计划草�?md, docs/Buff重构替换说明.md, docs/旧Buff系统耦合审查结果.md, scripts/ralph/prd.json, scripts/ralph/progress.txt
- 替换说明�?
  - 阶段 1 handoff 文档现已明确把代表�?AlicePolarizedAssaultTrigger -> PolarizedAssaultEvent planned-event 链标记为“已改经 ScheduleDispatchPort 的真实替换边界”，替换此前“代表�?producer 仍待后续收口”的旧基线表述�?
  - 阶段 1 handoff 文档现已明确�?SkillEventHandler -> RuntimeCommandPort -> LegacyRuntimeCommandAdapter 标记为“已落地�?same-tick 显式写边界”，替换此前“ScheduleBuffSettle() / update_anomaly() 仍未引入�?write facade”的旧基线表述�?
  - scripts/ralph/prd.json、docs/*handoff �?scripts/ralph/progress.txt 现已统一�?implicit-events 视为这组代表�?producer / write-boundary 样本的共享验证入口，而不是散落在进度记录里的临时命令集合�?
- 兼容保留�?
  - 本轮只同�?handoff 基线，没有新�?live runtime 路径替换；ScheduleDispatchPort �?RuntimeCommandPort 仍通过 legacy adapters 承接旧队列和旧容器身份�?
  - --legacy-runtime / --candidate-runtime 仍只是报告标签；�?live simulator 真正消费 config.buff_runtime.mode 前，文档与后�?PRD 仍不得把它们写成真实 runtime 切换开关�?
  - 其余未迁移的 BuffXLogic、BattleEventListener、Character 旁路 producer 与相�?same-tick 高风险写路径仍保留旧入口，本轮没有假装这些边界已经替换完成�?
- 下一步：
  - 下一轮继续沿阶段 1 路线，收口其�?raw event_list bypass 与必要的相邻 RuntimeCommandPort 样本，不扩到 Calculator 全量迁移或旧容器删除�?
---
## 2026-06-06 08:40:07 - US-001
- �����ļ���`zsim/sim_progress/Buff/BuffXLogic/ElegantVanitySpRecover.py`, `zsim/sim_progress/Buff/BuffXLogic/LunarNoviluna.py`, `tests/simulator/test_xstart_sp_refresh_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- �滻˵����
  - `ElegantVanitySpRecover._create_dispatch_port()` / `LunarNoviluna._create_dispatch_port()` ��ʼ�滻������ xstart SP refresh producer �� `JudgeTools.find_event_list()` �� `event_list.append(...)` �� planned-event ֱд��ڡ�
  - `tests/simulator/test_xstart_sp_refresh_dispatch.py` ��ʼ�滻������ͷ��� SP refresh producer ˳��һ�������������裬��ʽ�̶� `ElegantVanitySpRecover` �� `simple_start() -> publish` �� `LunarNoviluna` �� `publish -> simple_start()` ����˳��
- ���ݱ�����
  - `schedule_data.event_list` ���� `LegacyEventListScheduleDispatchAdapter` �нӣ��ײ� planned-event ���к� append ����û�б���д��
  - ����ֻ�ر� xstart SP refresh producer �� raw queue bypass��`MagneticStormCharlieSpRecover`��`SeedAdditionalAbilityTrigger` �Ⱥ��� producer �Ա�������ڣ���δ�滻 live runtime ·����
- ��һ����
  - ������ͬ��ģʽ�տ� `US-002` �� xhit SP refresh producer�������µ� focused regression �������� `implicit-events` ������֤��ڡ�
---
## 2026-06-06 08:56:11 - US-002
- Files: `zsim/sim_progress/Buff/BuffXLogic/MagneticStormCharlieSpRecover.py`, `zsim/sim_progress/Buff/BuffXLogic/SeedAdditionalAbilityTrigger.py`, `tests/simulator/test_xhit_sp_refresh_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- Replacement note:
  - `MagneticStormCharlieSpRecover._create_dispatch_port()` and `SeedAdditionalAbilityTrigger._create_dispatch_port()` now replace the xhit SP refresh producers' raw `JudgeTools.find_event_list()` / `schedule_data.event_list.append(...)` publishing path.
  - `tests/simulator/test_xhit_sp_refresh_dispatch.py` now proves both legacy queue bypass styles are blocked while preserving `simple_start()`, vanguard targeting, and `last_active_tick` semantics.
- Compatibility kept:
  - `schedule_data.event_list` is still owned by `LegacyEventListScheduleDispatchAdapter`, so the underlying planned-event queue and append semantics are unchanged.
  - This slice only closes the xhit SP refresh raw-queue bypass; `SliceofTimeExtraResources`, `CannonRotor`, and later producers still use the old entry path.
- Next:
  - Reuse the same focused no-raw-queue regression shape for `US-003`, while preserving the mixed SP/decibel payload contract.
---
## 2026-06-06 09:28:11 - US-003
- �����ļ���`zsim/sim_progress/Buff/BuffXLogic/SliceofTimeExtraResources.py`, `tests/simulator/test_slice_of_time_extra_resources_dispatch.py`, `scripts/run_buff_refactor_validation.py`
- �滻˵����
  - `SliceofTimeExtraResources._create_dispatch_port()` / `dispatch_port.publish_scheduled(refresh_data)` �����滻�� mixed refresh producer �� `JudgeTools.find_event_list()` �� `event_list.append(...)` �� planned-event ֱд��ڡ�
  - `tests/simulator/test_slice_of_time_extra_resources_dispatch.py` ��ʽ�̶� `simple_start() -> publish` ˳�򣬲�ͬʱ��֤ͬһ�� `ScheduleRefreshData` ��� `sp_target / sp_value / decibel_target / decibel_value` û���� gateway Ǩ���ж�ʧ��
- ���ݱ�����
  - `schedule_data.event_list` ���� `LegacyEventListScheduleDispatchAdapter` �нӣ��ײ� planned-event ���к� append ����û�б仯��
  - ����ֻ�ر� `SliceofTimeExtraResources` �� raw queue bypass��`CannonRotor`��`YanagiPolarityDisorderTrigger`��`HugoCorePassiveTotalizeTrigger` �� `DecibelManager` �Ա�������ڡ�
- ��һ����
  - ������ͬ���� focused no-raw-queue Ǩ��ģʽ�տ� `US-004` �� `CannonRotor`����Ҫ�л��� follow-up `SkillNode` ��������˳����Զ����� refresh payload ���ԡ�
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
