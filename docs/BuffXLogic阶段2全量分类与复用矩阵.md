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

## US-002 全量 Census

生成时间：2026-06-08 09:38 +08:00。本文节只更新分类证据和交接信息，不改动任何 XLogic 生产行为。

### 可复现扫描命令

```powershell
rg --files zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "MultiplierData|Mul\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "sim_instance" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "JudgeTools\.find_|exist_buff_dict|sub_exist_buff_dict|dynamic_buff_list|DYNAMIC_BUFF_DICT|LOADING_BUFF_DICT|dynamic_buff|loading_buff" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "history\.record|dy\.count|record|count|update_to_buff_0|simple_start|simple_exit|built_in_buff_box" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "create_schedule_dispatch_port|publish_scheduled|ScheduleRefreshData|LoadingMission|SkillNode|preload_tick|schedule_priority|Anomaly|anomaly|disorder|polarity|freeze|frozen|Dot|dot|Debuff|debuff|BuffAddStrategy" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
```

根工作区扫描默认排除 `.codex_worktrees/`，并排除 `__init__.py`，本次全量 census 口径为 149 个 XLogic 模块。CodeGraph `codegraph_files` 同时索引到 150 个 Python 文件，因为它包含 `__init__.py`。

### 模式计数

| 模式 | 命中文件数 | 命中行数 | match 数 |
| --- | ---: | ---: | ---: |
| `MultiplierData|Mul\(` | 19 | 37 | 37 |
| `sim_instance` | 148 | 421 | 747 |
| old container terms | 149 | 446 | 614 |
| record/count terms | 143 | 1830 | 2249 |
| event/anomaly/dot/debuff terms | 89 | 432 | 506 |

US-002 粗桶用于 census 定位，不等同于 US-003 之后的最终非排他分类结论：

| 粗桶 | 命中文件数 | 命中行数 | match 数 |
| --- | ---: | ---: | ---: |
| `ATTR_READ` | 20 | 40 | 40 |
| `SERVICE_LOCATION` | 148 | 626 | 981 |
| `OLD_CONTAINER` | 149 | 446 | 614 |
| `RECORD_COUNT_SYNC` | 143 | 2174 | 2593 |
| `EVENT_TRIGGER_OR_BYPASS` | 89 | 432 | 506 |
| `SCHEDULED_PUBLISH` | 25 | 93 | 93 |

### 汇总计数

| 指标 | 数量 | 说明 |
| --- | ---: | --- |
| census modules | 149 | `rg --files ... --glob '*.py' --glob '!__init__.py'` 的根工作区口径。 |
| infrastructure files | 5 | `_buff_record_base_class.py`、`_char_buff_mod.py`、`_euipment_buff_mod.py`、`BasicComplexBuffClass.py`、`BackendJudge.py`。 |
| leaf files | 144 | census modules 减 infrastructure files。 |
| files with multiple coarse coupling buckets | 148 | 排除 `INFRA` 后，命中至少两个 US-002 粗桶的文件；阶段 2 分类必须保持非排他。 |
| already migrated scheduled-publish samples | 14 | 通过 `create_schedule_dispatch_port(...)` / `publish_scheduled(...)` 走 `ScheduleDispatchPort` 的样本，记录为已迁移样本，不作为新 backlog。 |

### CodeGraph 导航证据

- Query seed：`US-002 Build The Full BuffXLogic Census`、`zsim/sim_progress/Buff/BuffXLogic`、`BasicComplexBuffClass`、`BackendJudge`、`_buff_record_base_class`、`_char_buff_mod`、`_euipment_buff_mod`、`MultiplierData`、`sim_instance`、`xjudge`、`xstart`、`xhit`、`xexit`。
- Representative leaf query：`SeedAdditionalAbilityTrigger`、`CannonRotor`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger`、`AliceAdditionalAbilityApBonus`、`create_schedule_dispatch_port`、`publish_scheduled`、`dy.count`、`update_to_buff_0`。
- Boundary findings：`BasicComplexBuffClass` / `BackendJudge` own shared record and backend-helper patterns; `ScheduleDispatchPort` remains the planned queue publish boundary; `SeedAdditionalAbilityTrigger` publishes `ScheduleRefreshData`; `CannonRotor` preserves `LoadingMission.mission_start(...)` before dispatch publish; `VivianCorePassiveTrigger` / `VivianCinema6Trigger` publish copied anomaly payloads through the dispatch port while still retaining `MultiplierData` formula snapshots.
- CodeGraph may surface duplicate `.codex_worktrees/` definitions. Those are historical navigation evidence only; production census conclusions in this section use root-workspace paths.

### Infrastructure Files

| 文件 | 当前角色 | 后续分类处理 |
| --- | --- | --- |
| `_buff_record_base_class.py` | `BuffRecordBaseClass` 基础 record 字段和 `check_cd(...)`。 | 作为 record/state-sync helper 基线，不当作普通 leaf 替换目标。 |
| `_char_buff_mod.py` | 角色模板 XLogic，展示 `BuffRecordBaseClass` 模板化 record 初始化。 | 保留为模板/示例，后续只在模板职责变化时触达。 |
| `_euipment_buff_mod.py` | 装备模板 XLogic，展示装备 `check_record_module()` 模板。 | 保留为模板/示例，注意文件名沿用当前拼写 `_euipment`。 |
| `BasicComplexBuffClass.py` | 共享复杂 Buff 基类，集中 `get_prepared(...)` / `check_record_module(...)`。 | 后续 record/state-sync 复用设计的首要输入，不在 census story 修改。 |
| `BackendJudge.py` | 后台判定通用逻辑，依赖 `JudgeTools.find_equipper(...)` / `find_init_data(...)`。 | service-location 分类样本，后续映射到 read-port 或 retained helper。 |

### 已迁移计划发布样本

以下 leaf 文件已经通过 `ScheduleDispatchPort` / `create_schedule_dispatch_port(...)` 发布计划事件或刷新数据，本 census 只记录为已迁移样本，不把它们重开为 raw queue backlog：

- `AlicePolarizedAssaultTrigger.py`
- `CannonRotor.py`
- `ElegantVanitySpRecover.py`
- `HugoCorePassiveTotalizeTrigger.py`
- `LunarNoviluna.py`
- `MagneticStormCharlieSpRecover.py`
- `MiyabiCoreSkill_IceFire.py`
- `SeedAdditionalAbilityTrigger.py`
- `SliceofTimeExtraResources.py`
- `VivianCinema6Trigger.py`
- `VivianCorePassiveTrigger.py`
- `VivianDotTrigger.py`
- `YanagiPolarityDisorderTrigger.py`
- `YixuanCinema1Trigger.py`

补充说明：`AstralVoice.py`、`FlightOfFancy.py`、`FlamemakerShakerDmgBonus.py`、`MagneticStormAlphaAMBonus.py`、`MagneticStormBravoApBonus.py`、`ShadowHarmony4.py`、`TriggerAfterShockTrigger.py`、`VivianCoattackTrigger.py`、`WoodpeckerElectroSet4_*` 等文件命中 `LoadingMission` / `SkillNode` 触发语义，但本 story 没发现新的 `record.event_list.append(...)` 或 `find_event_list()` 生产发布面；这些留给 US-004 按事件语义细分。

### 全量模块清单

以下表格逐文件记录 root-workspace census 元数据。`入口绑定` 来自 `self.xjudge` / `self.xstart` / `self.xhit` / `self.xexit` / `self.xeffect` 等赋值；`public methods` 记录非 `__dunder__` 方法名。`US-002 粗桶` 只用于后续故事路由，最终分类仍按本文 schema 的非排他轴补细分证据。

| 文件 | 类型 | 主类 | 记录类 | 入口绑定 | public methods | helper/base | US-002 粗桶 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| _buff_record_base_class.py | infra | - | BuffRecordBaseClass | - | check_cd | BuffRecordBaseClass | INFRA, OLD_CONTAINER |
| _char_buff_mod.py | infra | CharBuffXLogicName | CharBuffXLogicNameRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | INFRA, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| _euipment_buff_mod.py | infra | BuffXLogicName | BuffXLogicNameRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | INFRA, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| AliceAdditionalAbilityApBonus.py | leaf | AliceAdditionalAbilityApBonus | AliceAdditionalAbilityApBonusRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| AliceCinema6Trigger.py | leaf | AliceCinema6Trigger | AliceCinema6TriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| AlicePolarizedAssaultTrigger.py | leaf | AlicePolarizedAssaultTrigger | AlicePolarizedAssaultTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| AnomalyDebuffExitJudge.py | leaf | AnomalyDebuffExitJudge | - | xexit->special_exit_logic | special_exit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, EVENT_TRIGGER_OR_BYPASS |
| AstralVoice.py | leaf | AstralVoice | AstralVoiceRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| AstraYaoChordManagerTrigger.py | leaf | AstraYaoChordManagerTrigger | AstraYaoChordManagerTriggerRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| AstraYaoCorePassiveAtkBonus.py | leaf | AstraYaoCorePassiveAtkBonus | AstraYaoCorePassiveAtkBonusRecord | xstart->special_start_logic | check_record_module, get_prepared, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| AstraYaoIdyllicCadenza.py | leaf | AstraYaoIdyllicCadenza | AstraYaoIdyllicCadenzaRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| AstraYaoQuickAssistManagerTrigger.py | leaf | AstraYaoQuickAssistManagerTrigger | AstraYaoQuickAssistManagerTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| BackendJudge.py | infra | BackendJudge | - | xexit->special_exit_logic, xjudge->special_judge_logic | special_exit_logic, special_judge_logic | Buff.BuffLogic | INFRA, SERVICE_LOCATION, OLD_CONTAINER |
| BasicComplexBuffClass.py | infra | BasicComplexBuffClass | BaseBuffRecord | xeffect->special_effect_logic, xexit->special_exit_logic, xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_hit_logic, special_judge_logic, special_start_logic | BasicComplexBuffClass, Buff.BuffLogic | INFRA, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| BranchBladeSongCritDamageBonus.py | leaf | BranchBladeSongCritDamageBonus | BranchBladeSongRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| BranchBladeSongCritRateBonus.py | leaf | BranchBladeSongCritRateBonus | BranchBladeSongCritRateBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| CannonRotor.py | leaf | CannonRotor | CannonRotorRecord | xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| CinderCobaltAtkBonus.py | leaf | CinderCobaltAtkBonus | CinderCobaltAtkBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| CordisGerminaCritRateBonus.py | leaf | CordisGerminaCritRateBonus | CordisGerminaCritRateBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| CordisGerminaEleDmgBonus.py | leaf | CordisGerminaEleDmgBonus | CordisGerminaEleDmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| CordisGerminaSNAAndQIgnoreDefense.py | leaf | CordisGerminaSNAAndQIgnoreDefense | CordisGerminaSNAAndQIgnoreDefenseRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| DawnsBloom4SetTriggerNADmgBonus.py | leaf | DawnsBloom4SetTriggerNADmgBonus | DawnsBloom4SetTriggerNADmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| ElectroLipGlossAtkAndDmgBonus.py | leaf | ElectroLipGlossAtkAndDmgBonus | ElectroLipGlossAtkAndDmgBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| ElegantVanityDmgBonus.py | leaf | ElegantVanityDmgBonus | ElegantVanityDmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| ElegantVanitySpRecover.py | leaf | ElegantVanitySpRecover | ElegantVanitySpRecoverRecord | xstart->special_start_logic | _create_dispatch_port, check_record_module, get_prepared, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| FlamemakerShakerApBonus.py | leaf | FlamemakerShakerApBonus | FlamemakerShakerApBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| FlamemakerShakerDmgBonus.py | leaf | FlamemakerShakerDmgBonus | FlamemakerShakerDmgBonusRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| FlightOfFancy.py | leaf | FlightOfFancy | FlightOfFancyRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| FreedomBlues.py | leaf | FreedomBlues | FreedomBluesRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| HailstormShrineIceBonus.py | leaf | HailstormShrineIceBonus | HailstormShrineIceBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| HeartstringNocturne.py | leaf | HeartstringNocturne | HeartstringNocturneRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| HellfireGearsSpRBonus.py | leaf | HellfireGearsSpRBonus | - | xexit->special_exit_logic, xjudge->special_judge_logic | special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER |
| HormonePunkAtkBonus.py | leaf | HormonePunkAtkBonus | HormonePunkAtkBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| HugoAdditionalAbilityExtraQTEDmgBonus.py | leaf | HugoAdditionalAbilityExtraQTEDmgBonus | HugoAdditionalAbilityExtraQTEDmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| HugoCorePassiveDoubleStunAtkBonus.py | leaf | HugoCorePassiveDoubleStunAtkBonus | HugoCorePassiveDoubleStunAtkBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| HugoCorePassiveEXStunBonus.py | leaf | HugoCorePassiveEXStunBonus | HugoCorePassiveEXStunBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| HugoCorePassiveSingleStunAtkBonus.py | leaf | HugoCorePassiveSingleStunAtkBonus | HugoCorePassiveSingleStunAtkBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| HugoCorePassiveTotalizeTrigger.py | leaf | HugoCorePassiveTotalizeTrigger | HugoCorePassiveTotalizeTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| IceJadeTeaPotExtraDMGBonus.py | leaf | IceJadeTeaPotExtraDMGBonus | - | xjudge->special_judge_logic | special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| JaneAdditionalAbilityPhyBuildupBonus.py | leaf | JaneAdditionalAbilityPhyBuildupBonus | JaneAdditionalAbilityPhyBuildupBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| JaneCinema1APTransToDmgBonus.py | leaf | JaneCinema1APTransToDmgBonus | JaneCinema1APTransToDmgBonusRecord | xexit->special_exit_logic, xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| JaneCoreSkillStrikeCritDmgBonus.py | leaf | JaneCoreSkillStrikeCritDmgBonus | JaneCoreSkillStrikeCritDmgBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| JaneCoreSkillStrikeCritRateBonus.py | leaf | JaneCoreSkillStrikeCritRateBonus | JaneCoreSkillStrikeCritRateBonusRecord | xexit->special_exit_logic, xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| JanePassionStateAPTransToATK.py | leaf | JanePassionStateAPTransToATK | JanePassionStateAPTransToATKRecord | xexit->special_exit_logic, xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| JanePassionStatePhyBuildupBonus.py | leaf | JanePassionStatePhyBuildupBonus | JanePassionStatePhyBuildupBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| JanePassionStateTrigger.py | leaf | JanePassionStateTrigger | JanePassionStateTriggerRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| KaboomTheCannon.py | leaf | KaboomTheCannon | KaboomTheCannonRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_hit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| LighterAdditionalAbility_IceFireBonus.py | leaf | LighterExtraSkill_IceFireBonus | LighterExtraSkillRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_hit_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| LighterUniqueSkillStunBonus.py | leaf | LighterUniqueSkillStunBonus | LighterUniqueSkillStunBonusRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| LighterUniqueSkillStunTimeLimitBonus.py | leaf | LighterUniqueSkillStunTimeLimitBonus | LighterUniqueSkillStunTimeRecord | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| LinaAdditionalSkillEleDMGBonus.py | leaf | LinaAdditionalSkillEleDMGBonus | LinaAdditionalSkillRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| LinaCoreSkillPenRatioBonus.py | leaf | LinaCoreSkillPenRatioBonus | LinaCoreSkillRecord | xexit->special_exit_logic, xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic, special_start_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| LunarNoviluna.py | leaf | LunarNoviluna | LunarNovilunaRecord | xstart->special_start_logic | _create_dispatch_port, check_record_module, get_prepared, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| LyconAdditionalAbilityStunVulnerability.py | leaf | LyconAdditionalAbility, LyconAdditionalAbilityStunVulnerability | - | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| MagneticStormAlphaAMBonus.py | leaf | MagneticStormAlphaAMBonus | MagneticStormAlphaAMBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| MagneticStormBravoApBonus.py | leaf | MagneticStormBravoApBonus | MagneticStormBravoApBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| MagneticStormCharlieSpRecover.py | leaf | MagneticStormCharlieSpRecover | MagneticStormCharlieSpRecoverRecord | xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| MarcatoDesireAtkBonus.py | leaf | MarcatoDesireAtkBonus | MarcatoDesireRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| MetanukiMorphosisAPBonus.py | leaf | MetanukiMorphosisAPBonus | MetanukiMorphosisAPBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| MiyabiAdditionalAbility_IgnoreIceRes.py | leaf | MiyabiAdditionalAbility, MiyabiAdditionalAbility_IgnoreIceRes | - | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| MiyabiCoreSkill_FrostBurn.py | leaf | MiyabiCoreSkillFB, MiyabiCoreSkill_FrostBurn | - | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| MiyabiCoreSkill_IceFire.py | leaf | MiyabiCoreSkillIF, MiyabiCoreSkill_IceFire | - | xexit->special_exit_logic, xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_exit_logic, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| MoonlightLullabyAllTeamDmgBonus.py | leaf | MoonlightLullabyAllTeamDmgBonus | MoonlightLullabyAllTeamDmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| NikoleCoreSkillDefReduction.py | leaf | NicoleCoreSkillDefReduction | NicoleCoreSkillRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| PhaethonsMelody.py | leaf | PhaethonsMelody | PhaethonsMelodyRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| PolarMetalFreezeBonus.py | leaf | PolarMetalFreezeBonus | PolarMetalRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| PreciousFossilizedCoreStunBonusOver50Hp.py | leaf | PreciousFossilizedCoreStunBonusOver50Hp | - | xjudge->special_judge_logic | special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER |
| PreciousFossilizedCoreStunBonusOver75Hp.py | leaf | PreciousFossilizedCoreStunBonusOver75Hp | - | xjudge->special_judge_logic | special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER |
| PuzzleSphereExDmgBonus.py | leaf | PuzzleSphereExDmgBonus | PuzzleSphereExDmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| QingmingBirdcageCompanionEthDmgBonus.py | leaf | QingmingBirdcageCompanionEthDmgBonus | QingmingBirdcageCompanionEthDmgBonusRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| QingmingBirdcageCompanionSheerAtkBonus.py | leaf | QingmingBirdcageCompanionSheerAtkBonus | QingmingBirdcageCompanionSheerAtkBonusRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| QingYiAdditionalAbilityStunConvertToATK.py | leaf | QingYiAdditionalAbilityStunConvertToATK | QingYiAdditionalSkillRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| QingYiCoreSkillExtraStunBonus.py | leaf | QingYiCoreSkillExtraStunBonus | QintYiCoreSkillExtraStunRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| QingYiCoreSkillStunDMGBonus.py | leaf | QingYiCoreSkillStunDMGBonus | QintYiCoreSkillRecord | xexit->special_exit_logic, xstart->special_start_logic | check_record_module, get_prepared, special_exit_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| RainforestGourmetATKBonus.py | leaf | RainforestGourmetATKBonus | RainforestGourmetATKBonusRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| RiotSuppressorMarkVI.py | leaf | RiotSuppressorMarkVI | RiotSuppressorMarkVIRecord | xeffect->special_effect_logic, xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| RoaringRideBuffTrigger.py | leaf | RoaringRideBuffTrigger | RoaringRideBuffTriggerRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_hit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeedAdditionalAbilityTrigger.py | leaf | SeedAdditionalAbilityTrigger | SeedAdditionalAbilityTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| SeedBesiegeBonus.py | leaf | SeedBesiegeBonus | SeedBesiegeBonusRecord | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SeedBesiegeBonusTrigger.py | leaf | SeedBesiegeBonusTrigger | SeedBesiegeBonusTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeedCinema2BesiegeIgnoreDefenceTrigger.py | leaf | SeedCinema2BesiegeIgnoreDefenceTrigger | SeedCinema2BesiegeIgnoreDefenceTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeedCinema2BesiegeIgnoreDefense.py | leaf | SeedCinema2BesiegeIgnoreDefense | SeedCinema2BesiegeIgnoreDefenseRecord | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SeedCinema4Bonus.py | leaf | SeedCinema4Bonus | SeedCinema4BonusRecord | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SeedCinema4Trigger.py | leaf | SeedCinema4Trigger | SeedCinema4TriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeedCinema6Trigger.py | leaf | SeedCinema6Trigger | SeedCinema6TriggerRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeedDirectStrikeBonus.py | leaf | SeedDirectStrikeBonus | SeedDirectStrikeBonusRecord | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SeedDirectStrikeTrigger.py | leaf | SeedDirectStrikeTrigger | SeedDirectStrikeTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeedOnslaughtBonus.py | leaf | SeedOnslaughtBonus | SeedOnslaughtBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic, BuffRecordBaseClass | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SeveredInnocenceCritDMGBonus.py | leaf | SeveredInnocenceCritDMGBonus | SeveredInnocenceCritDMGBonusRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SeveredInnocencELEDMGBonus.py | leaf | SeveredInnocencELEDMGBonus | SeveredInnocencELEDMGBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| ShadowHarmony4.py | leaf | ShadowHarmony4 | ShadowHarmony4Record | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| SharpenedStingerAnomalyBuildupBonus.py | leaf | SharpenedStingerAnomalyBuildupBonus | SharpenedStingerAnomalyBuildupBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SharpenedStingerPhyDmgBonus.py | leaf | SharpenedStingerPhyDmgBonus | SharpenedStingerPhyDmgBonusRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SliceofTimeExtraResources.py | leaf | SliceofTimeExtraResources | SliceofTimeExtraResourcesRecord | xjudge->special_judge_logic, xstart->special_start_logic | _create_dispatch_port, check_record_module, check_update_cd, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| SokakuAdditionalAbilityICEBonus.py | leaf | SokakuAdditionalAbilityICEBonus | SokakuAdditionalAbilityIBRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SokakuUniqueSkillMajorATKBonus.py | leaf | SokakuUniqueSkillMajorATKBonus | SokakuAdditionalAbilityATKRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SokakuUniqueSkillMinorATKBonus.py | leaf | SokakuUniqueSkillMinorATKBonus | SokakuUniqueSkillMinorATKRecord | xstart->special_start_logic | check_record_module, get_prepared, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| Soldier0AnbyAdditionalSkillDMGBonus.py | leaf | Soldier0AnbyAdditionalSkillDMGBonus | Soldier0AnbyAdditionalSkillDMGBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| Soldier0AnbyCinema4EleResReduce.py | leaf | Soldier0AnbyCinema4EleResReduce | Soldier0AnbyCinema4EleResReduceRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| Soldier0AnbyCoreSkillCritDMGBonus.py | leaf | Soldier0AnbyCoreSkillCritDMGBonus | Soldier0AnbyCoreSkillCritDMGBonusRecord | xexit->special_exit_logic, xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| Soldier0AnbyCoreSkillDMGBonus.py | leaf | Soldier0AnbyCoreSkillDMGBonus | Soldier0AnbyCoreSkillDMGBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| Soldier0AnbySilverStarTrigger.py | leaf | Soldier0AnbySilverStarTrigger | Soldier0AnbySilverStarTriggerRecord | xexit->special_exit_logic | check_record_module, get_prepared, special_exit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| Soldier11AdditionalSkillExtraFireDMGBonus.py | leaf | Soldier11AdditionalSkillExtraFireDMGBonus | Slodier11AdditionalSkillRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SpectralGazeDefReduce.py | leaf | SpectralGazeDefReduce | SpectralGazeDefReduceRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SpectralGazeImpactBonus.py | leaf | SpectralGazeImpactBonus | SpectralGazeImpactBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| SpectralGazeSpiritLock.py | leaf | SpectralGazeSpiritLock | SpectralGazeSpiritLockRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| SteamOven.py | leaf | SteamOven | SteamOvenRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| StreetSuperstar.py | leaf | StreetSuperstar | StreetSuperstarRecord | xjudge->special_judge_logic, xstart->special_start_logic | check_record_module, get_prepared, special_judge_logic, special_start_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| TheVault.py | leaf | TheVault | TheVaultRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| TimeweaverApBonus.py | leaf | TimeweaverApBonus | TimeweaverApBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| TimeweaverDisorderDmgMul.py | leaf | TimeweaverDisorderDmgMul | TimeweaverDisorderDmgMulRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| TriggerAdditionalAbilityStunBonus.py | leaf | TriggerAdditionalAbilityStunBonus | TriggerAdditionalAbilityStunBonusRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| TriggerAfterShockTrigger.py | leaf | TriggerAfterShockTrigger | TriggerAfterShockTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| TriggerCoreSkillStunDMGBonus.py | leaf | TriggerCoreSkillStunDMGBonus | TriggerCoreSkillStunDMGBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| VivianAdditionalAbilityCoAttackTrigger.py | leaf | VivianAdditionalAbilityCoAttackTrigger | VivianAdditionalAbilityCoAttackTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| VivianCinema1Debuff.py | leaf | VivianCinema1Debuff | VVivianCinema1DebuffRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| VivianCinema6Trigger.py | leaf | VivianCinema6Trigger | VivianCinema6TriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | _create_dispatch_port, c6_pre_active, c6_ratio, check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| VivianCoattackTrigger.py | leaf | VivianCoattackTrigger | VivianCoattackTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| VivianCorePassiveTrigger.py | leaf | VivianCorePassiveTrigger | VivianCorePassiveTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| VivianDotTrigger.py | leaf | VivianDotTrigger | VivianDotTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| VivianFeatherTrigger.py | leaf | VivianFeatherTrigger | VivianFeatherTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| WeepingCradleDMGBonusIncrease.py | leaf | WeepingCradleDMGBonusIncrease | WeepingCradleDMGBRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, increase_cd_judge, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| WeepingGeminiApBonus.py | leaf | WeepingGeminiApBonus | WeepingGeminiApBonusRecord | xeffect->special_effect_logic, xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| WoodpeckerElectroSet4_CA.py | leaf | WoodpeckerElectroSet4_CA | WoodpeckerElectroCARecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| WoodpeckerElectroSet4_E_EX.py | leaf | WoodpeckerElectroSet4_E_EX | WoodpeckerElectroEXRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| WoodpeckerElectroSet4_NA.py | leaf | WoodpeckerElectroSet4_NA | WoodpeckerElectroNARecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| YanagiCinema6EXDmgBonus.py | leaf | YanagiCinema6EXDmgBonus | YanagiCinema6EXDmgBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| YanagiPolarityDisorderTrigger.py | leaf | YanagiPolarityDisorderTrigger | YanagiPolarityDisorderTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| YanagiStanceJougen.py | leaf | YanagiStanceJougen | YanagiStanceJougenRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| YanagiStanceKagen.py | leaf | YanagiStanceKagen | YanagiStanceKagenRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| YangiCinema1ApBonus.py | leaf | YangiCinema1ApBonus | YangiCinema1ApBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| YixuanAdditionalAbilityDmgBonus.py | leaf | YixuanAdditionalAbilityDmgBonus | YixuanAdditionalAbilityDmgBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YixuanCinema1Trigger.py | leaf | YixuanCinema1Trigger | YixuanCinema1TriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | _create_dispatch_port, check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS, SCHEDULED_PUBLISH |
| YixuanCinema2StunTimeLimitBonus.py | leaf | YixuanCinema2StunTimeLimitBonus | YixuanCinema2StunTimeLimitBonusRecord | xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YixuanCinema4Tranquility.py | leaf | YixuanCinema4Tranquility | YixuanCinema4TranquilityRecord | xeffect->special_effect_logic, xexit->special_exit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_exit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YunkuiTalesSheerAtkBonus.py | leaf | YunkuiTalesSheerAtkBonus | YunkuiTalesSheerAtkBonusRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| YuzuhaAdditionalAbilityAnomalyBuildupBonus.py | leaf | YuzuhaAdditionalAbilityAnomalyBuildupBonus | YuzuhaAdditionalAbilityAnomalyBuildupBonusRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_hit_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaAdditionalAbilityAnomalyDmgBonus.py | leaf | YuzuhaAdditionalAbilityAnomalyDmgBonus | YuzuhaAdditionalAbilityAnomalyDmgBonusRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_hit_logic | Buff.BuffLogic | ATTR_READ, SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaCinem1EleResReduce.py | leaf | YuzuhaCinem1EleResReduce | YuzuhaCinem1EleResReduceRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaCinema2Trigger.py | leaf | YuzuhaCinema2Trigger | YuzuhaCinema2TriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, ready, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaCinema4QuickAssistTrigger.py | leaf | YuzuhaCinema4QuickAssistTrigger | YuzuhaCinema4QuickAssistTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaCinema6SheelTrigger.py | leaf | YuzuhaCinema6SheelTrigger | YuzuhaCinema6SheelTriggerRecord | xeffect->special_effect_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_effect_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaCinema6SugarBurstMaxTrigger.py | leaf | YuzuhaCinema6SugarBurstMaxTrigger | YuzuhaCinema6SugarBurstMaxTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| YuzuhaCorePassiveSweetScare.py | leaf | YuzuhaCorePassiveSweetScare | YuzuhaCorePassiveSweetScareRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaHardCandyShotTrigger.py | leaf | YuzuhaHardCandyShotTrigger | YuzuhaHardCandyShotTriggerRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, ready, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaSugarBurstAnomalyBuildupBonus.py | leaf | YuzuhaSugarBurstAnomalyBuildupBonus | YuzuhaSugarBurstAnomalyBuildupBonusRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaSugarBurstMaxAnomalyBuildupBonus.py | leaf | YuzuhaSugarBurstMaxAnomalyBuildupBonus | YuzuhaSugarBurstMaxAnomalyBuildupBonusRecord | xhit->special_hit_logic, xjudge->special_judge_logic | check_record_module, get_prepared, special_hit_logic, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC, EVENT_TRIGGER_OR_BYPASS |
| YuzuhaTanukiWishAtkBonus.py | leaf | YuzuhaTanukiWishAtkBonus | YuzuhaTanukiWishAtkBonusRecord | xhit->special_hit_logic | check_record_module, get_prepared, special_hit_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |
| ZanshinHerbCase.py | leaf | ZanshinHerbCase | ZanshinHerbCaseRecord | xjudge->special_judge_logic | check_record_module, get_prepared, special_judge_logic | Buff.BuffLogic | SERVICE_LOCATION, OLD_CONTAINER, RECORD_COUNT_SYNC |

## 后续填写占位

`US-003` 之后应基于上面的 census 表按 helper family、事件语义、state-sync 模式和验证入口继续补细分矩阵、复用模式目录、风险矩阵和下一轮 PRD 候选池。不要把本节粗桶直接当成阶段 3 替换清单。
