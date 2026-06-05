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
