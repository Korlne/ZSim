# BuffXLogic阶段2全量分类与复用矩阵

## 用途

本文是阶段 2 `BuffXLogic` 全量分类与复用收敛的主交接产物。`US-001` 只建立分类 schema 和边界规则，不改动任何 XLogic 生产行为，也不开始阶段 3 的具体替换。

后续故事应在本文中追加全量 census、耦合分类、复用模式目录、风险矩阵和下一轮 PRD 候选池。每条分类结论必须能回到根工作区源码、聚焦测试或验证命令；CodeGraph 只作为导航证据。

## 取证范围

本 schema 基于以下当前交接材料：

- `docs/Buff重构下阶段计划草稿.md`：阶段 2 默认入口、PRD 取材原则、`.codex_worktrees/` 历史证据规则、阶段 2 第一轮范围和非目标。
- `docs/Buff系统重构Checklist.md`：阶段 1 已关闭项、阶段 2 未完成项、当前默认下一步。
- `docs/Buff重构方案.md`：事件与计划事件区别、Buff 只保留状态管理、触发判定外移、增减益 Buff / 触发器 Buff 的业务分类原则。
- `docs/旧Buff系统耦合审查结果.md`：重点读取 `6.6`、`6.7`、`6.8`、`6.9` 与 `7`，确认 runtime、事件、Calculator、验证和 XLogic 服务定位边界。
- `scripts/ralph/progress.txt`：当前没有 `## Codebase Patterns` 章节；本轮不从空历史中推导额外通用模式。

本轮 CodeGraph 查询项：

- `BuffXLogic`
- `BuffAttributeReader`
- `ScheduleDispatchPort`
- `RuntimeCommandPort`
- `LegacyRuntimeCommandAdapter`
- `BuffRuntimeReadPort`
- `LegacyBuffRuntimeFacade`
- `Calculator`
- `CalAnomaly`
- `sim_instance`

CodeGraph 当前导航结论：

- 根工作区 `zsim/sim_progress/Buff/BuffXLogic/` 当前索引到 150 个 Python 文件；后续 census 必须用根工作区扫描复算，并默认排除 `.codex_worktrees/`。
- `BuffAttributeReader` 已是 `Calculator.py` 中的最小高频属性读取协议，目前覆盖 AM / AP 代表性读取样本；后续扩展应按 helper family 归类，不在本 story 新增接口。
- `ScheduleDispatchPort` / `create_schedule_dispatch_port(...)` 仍是计划事件发布入口；底层 `LegacyEventListScheduleDispatchAdapter` 只保留 append 兼容语义，不把 raw `event_list` 暴露给生产者。
- `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 仍是同 tick runtime 写边界；`update_anomaly(...)` 和 `settle_buffs(...)` 委托旧实现时保留当前 `ScheduleData`、旧容器身份和 same-tick 写语义。
- `BuffRuntimeReadPort` 保持只读主契约；其中的 legacy getter 仅是过渡兼容读口，不是新写口。
- `LegacyBuffRuntimeFacade` 包住旧模板、pending queue、active store 和 enemy debuff mirror 的兼容写侧；旧容器身份仍保留，不代表容器删除。
- CodeGraph 会命中 `.codex_worktrees/` 中的历史定义；除非后续故事明确审计归档分支，否则这些命中只作为历史快照，不作为当前生产 blocker。

## 分类记录 Schema

每个 XLogic 文件后续应按下面字段记录。分类是非排他的：同一个 XLogic 可以同时属于多个桶。

| 字段 | 填写要求 |
| --- | --- |
| 文件 | 根工作区相对路径，默认排除 `.codex_worktrees/`。 |
| 主类 / 记录类 | 记录主要 XLogic class、record class、公共入口方法，例如 `xjudge`、`xstart`、`xhit`、`xexit`。 |
| 源码证据 | 记录可复现的 `rg` / CodeGraph / line evidence；最终结论必须回到根工作区源码。 |
| 非排他分类轴 | 从下方分类轴中列出全部命中项，不只选一个“主类”。 |
| 旧耦合面 | 说明命中的旧容器、旧 helper、旧公式、事件入口或服务定位路径。 |
| 现有边界 / 未来候选 | 映射到 `BuffAttributeReader`、`ScheduleDispatchPort`、`RuntimeCommandPort`、`BuffRuntimeReadPort`、`LegacyBuffRuntimeFacade`、listener gateway、state-sync helper 或 retained compatibility。 |
| 顺序 / 时机约束 | 记录 `simple_start(...)`、`mission_start(...)`、publish、record reset、`dy.count` 写回、same-tick 写入等必须保留的相对顺序。 |
| 验证入口 | 记录 `implicit-events`、`calculator-reads`、默认 lifecycle profile、focused pytest 或 main-loop consistency 样本。 |
| 后续 PRD 分组 | 按 helper family、事件语义、state-sync 模式或验证入口分组，避免按单个角色文件拆薄故事。 |
| 非目标 / 兼容保留 | 说明本轮不删除、不替换或只作为兼容快照保留的旧路径。 |

## 非排他分类轴

| 代码 | 分类轴 | 命中证据 | 目标边界 / 复用方向 | 默认验证入口 |
| --- | --- | --- | --- | --- |
| `ATTR_READ` | 属性读取 | `MultiplierData(...)`、`MultiplierData as Mul`、`Mul(...)`、`MulData(...)`、直接读 `dynamic_buff_list` 或等价旧聚合快照。 | `BuffAttributeReader` helper family，例如 AM、impact、full crit rate、personal crit rate、personal crit damage。 | `calculator-reads`；若伴随事件副作用再加 `implicit-events`。 |
| `EVENT_TRIGGER` | 事件触发 | `xjudge`、`xstart`、`xhit`、`xexit` 中按技能、异常、监听器或状态条件触发后续行为。 | 事件 handler / listener pattern；只把需要排序的后续载荷映射到 scheduled publish。 | `implicit-events` 或对应 focused pytest。 |
| `RECORD_COUNT_SYNC` | record / count 写回 | `history.record`、自定义 record class、`dy.count`、`built_in_buff_box`、`simple_start(...)`、`simple_exit(...)`、`update_to_buff_0(...)`。 | record helper、state-sync helper、template sync pattern；本 PRD 不替换记录实现。 | `implicit-events`；触达 lifecycle 写路径时加默认 profile。 |
| `BYPASS_ANOMALY_DOT_DEBUFF` | anomaly / debuff / dot 旁路 | anomaly buildup、disorder、polarity disorder、freeze、dot、debuff、enemy dynamic state、`BuffAddStrategy` 等。 | 保持 scheduled publish、listener broadcast、dot runtime registration、runtime immediate write 四层分离。 | `implicit-events`；公式读取变化加 `calculator-reads`。 |
| `SERVICE_LOCATION` | `sim_instance` service-location | `self.buff_instance.sim_instance`、`enemy.sim_instance`、`JudgeTools.find_*`、从旧 runtime 临时抓 `exist_buff_dict` / `dynamic_buff_list`。 | 映射到 `BuffRuntimeReadPort`、`LegacyBuffRuntimeFacade`、显式 context 或 retained compatibility helper。 | 依触达面选择；通常先用 `implicit-events`。 |
| `FORMULA_SNAPSHOT` | Calculator / CalAnomaly 公式快照 | `Calculator`、`CalAnomaly`、`MultiplierData.get_buff_bonus()`、`DynamicStatement` 或完整公式内部。 | Retained compatibility snapshot；先设计读取 helper，不重写公式。 | `calculator-reads`；异常公式变化时加相关 focused pytest。 |
| `LISTENER_BROADCAST` | listener broadcast | `listener_manager.broadcast_event(...)`、`ListenerBroadcastSignal` 或同步订阅通知。 | listener gateway / synchronous notification；不能替代计划队列。 | `implicit-events` 或 listener focused pytest。 |
| `SCHEDULED_PUBLISH` | scheduled publish | `ScheduleDispatchPort`、`create_schedule_dispatch_port(...)`、`publish_scheduled(...)`、`LoadingMission`、`SkillNode`、`preload_tick`、`schedule_priority`、`execute_tick`。 | `ScheduleDispatchPort`；保留排序、延迟、同 tick 尾部执行和文件内相对顺序。 | `implicit-events` 与具体 producer focused pytest。 |
| `RUNTIME_IMMEDIATE_WRITE` | runtime immediate write | `RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`ScheduleBuffSettle`、`update_anomaly`、active-store / pending / enemy mirror 立即写。 | 继续复用唯一 same-tick 写边界；不得新增第二套 write facade。 | `implicit-events`；触达 lifecycle 时加默认 profile。 |
| `RETAINED_COMPAT_ONLY` | retained compatibility only | 旧容器身份、legacy `buff_add()`、legacy `KickOutBuff()`、handler requeue、Load-stage continuation、`ScheduleBuffSettle.py` adapter internals、`.codex_worktrees/` 历史证据。 | 只记录保留原因和删除条件；不作为阶段 2 首轮替换目标。 | guardrail / validation 失败时才开 blocker。 |

## 阶段 1 保留边界

阶段 2 分类必须保留以下边界，不得在分类故事中顺手改写：

- `ScheduleDispatchPort` 只负责计划事件入队；adapter 对 `schedule_data.event_list` 的访问是当前允许的兼容触点。发布者应按需从当前 `sim_instance` 或 `schedule_data` 创建 dispatch port，不缓存长生命周期 adapter。
- `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 是唯一 same-tick runtime 写边界。后续分类不得新增第二套写 facade，也不得把 `BuffRuntimeReadPort` 扩成写 API。
- `BuffRuntimeReadPort` 是只读主契约；legacy dynamic / exist getter 只是过渡兼容读口，不是推荐的新主读口。
- `LegacyBuffRuntimeFacade` 继续按引用包住旧模板、pending queue、active store 和 enemy debuff mirror；旧容器身份仍是 retained compatibility boundary。
- `JudgeTools.find_event_list()`、`check_preparation(..., event_list=...)` 缓存分支和 `BuffRecordBaseClass.event_list` 已删除或关闭；除非 guardrail 给出新的生产证据，否则不重开这些 surface。
- `exist_buff_dict`、`DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT`、legacy `buff_add()`、legacy `KickOutBuff()`、Calculator / CalAnomaly `MultiplierData` 公式快照仍保留，阶段 2 首轮不删除。
- `listener_manager.broadcast_event()`、scheduled queue publish、dot runtime registration、runtime immediate write 是四层不同语义，不得合并为一个总线。
- `ScheduledEvent` handler not-yet-executable requeue、`LoadDamageEvent` damage-effect continuation、本地事件组和 dot runtime registration 是 retained boundary，不重新归类为 raw planned-event backlog。
- `--legacy-runtime` / `--candidate-runtime` 当前仍只是 consistency / benchmark 报告标签，不是 live runtime switch。
- `.codex_worktrees/` 是历史 worktree 快照；阶段 2 源码复扫默认排除，除非故事明确要求审计归档分支。

## 后续填写占位

后续故事从这里开始追加。`US-002` 应先复算完整文件清单和模式计数，然后再填分类表；`US-003` 之后按轴补细分矩阵、复用模式和风险分组。

| 文件 | 主类 / 记录类 | 非排他分类轴 | 旧耦合面 | 现有边界 / 未来候选 | 验证入口 | 后续 PRD 分组 |
| --- | --- | --- | --- | --- | --- | --- |
| 待 `US-002` 填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |
