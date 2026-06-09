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

## US-003 Calculator / 属性读取分类

生成时间：2026-06-08 09:49 +08:00。本节只分类 `Calculator` 与属性读取耦合，不改动任何 XLogic 生产行为，不新增 `BuffAttributeReader` 方法，也不替换现有 `MultiplierData` / `CalAnomaly` 公式快照。

### 可复现扫描命令

```powershell
rg -n "MultiplierData\s*\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "MultiplierData\s+as\s+Mul" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "\bMul\s*\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "\bMulData\s*\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "dynamic_buff_list" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "cal_am\(|cal_ap\(|cal_imp\(|cal_crit_rate\(|cal_personal_crit_rate\(|cal_personal_crit_dmg\(|CalculatorBuffAttributeReader|BuffAttributeReadContext" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
```

根工作区扫描结果如下；`.codex_worktrees/` 仍按阶段 2 规则视为历史证据，不进入生产分类计数。

| 模式 | 命中文件数 | match 数 | US-003 结论 |
| --- | ---: | ---: | --- |
| `MultiplierData\s*\(` | 11 | 11 | 仍有直接兼容快照构造；按 helper family 分类，不按单个角色拆薄。 |
| `MultiplierData\s+as\s+Mul` | 7 | 7 | 别名入口仍需要 guardrail / 后续 PRD 覆盖；不能只搜字面 `MultiplierData(`。 |
| `\bMul\s*\(` | 7 | 7 | 别名构造多为 read-then-writeback，迁移时必须保留 `simple_start(...)` / `dy.count` / `update_to_buff_0(...)` 顺序。 |
| `\bMulData\s*\(` | 0 | 0 | `BuffXLogic` 当前没有根工作区 `MulData(...)`；`CalAnomaly` 内部 `MulData` 仍是公式快照，留给 US-007 / later classification。 |
| `dynamic_buff_list` | 27 | 70 | 包含属性读取输入、旧容器 service-location、record 字段和已迁移 reader 的 `active_buff_view` 输入；最终分类必须看源码上下文。 |

### CodeGraph 导航证据

- Query seed：`US-003 Classify Calculator And Attribute-Read Couplings`、`MultiplierData`、`Mul`、`MulData`、`dynamic_buff_list`、`BuffAttributeReader`、`Calculator`、`CalAnomaly`、`AliceAdditionalAbilityApBonus`、`JaneCinema1APTransToDmgBonus`、`JanePassionStateAPTransToATK`、`LinaCoreSkillPenRatioBonus`、`TimeweaverDisorderDmgMul`、`TriggerAdditionalAbilityStunBonus`、`Soldier0AnbyCoreSkillCritDMGBonus`。
- `MultiplierData.get_buff_bonus(...)` 在根工作区 `Calculator.py` 通过 `_calculate_dynamic_statement(...)` 聚合角色 active buff view 与 enemy debuff view，再产出 `DynamicStatement`；这是 retained compatibility snapshot，不在 US-003 删除。
- `BuffAttributeReader` / `CalculatorBuffAttributeReader` 当前只覆盖 `read_anomaly_mastery(...)` 与 `read_anomaly_proficiency(...)`；`BranchBladeSongCritDamageBonus` 和 `TimeweaverDisorderDmgMul` 是已迁移 reader-backed 只读样本。
- `Calculator.AnomalyMul.cal_am(...)` 已委托 `_calculate_anomaly_mastery(...)`；`cal_ap(...)`、`cal_imp(...)`、`cal_crit_rate(...)`、`cal_personal_crit_rate(...)`、`cal_personal_crit_dmg(...)` 仍是 `MultiplierData` snapshot helper。
- Representative XLogic evidence confirms the non-exclusive split: `AliceAdditionalAbilityApBonus` / `YuzuhaAdditionalAbility*` read AM then write `dy.count`; `Jane*` alias paths read AP then write count/state; `TriggerAdditionalAbilityStunBonus` and `Soldier0AnbyCoreSkillCritDMGBonus` read crit helpers then write count/state.
- CodeGraph again surfaced `.codex_worktrees/` duplicates for Calculator and XLogic symbols. Those are historical navigation evidence only; root-workspace source and focused validation remain the compatibility basis.

### Helper Family 分类

| helper family | 当前入口 | root-workspace 调用点 / 状态 | 分类 | 后续复用候选 | 默认验证入口 |
| --- | --- | --- | --- | --- | --- |
| 异常掌控 AM | `Calculator.AnomalyMul.cal_am(...)` / `read_anomaly_mastery(...)` | `BranchBladeSongCritDamageBonus.py` 已迁移 reader-backed 只读门禁；`AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`、`YuzuhaAdditionalAbilityAnomalyDmgBonus.py` 仍构造 `MultiplierData(...)` 后写回 count/state。 | `ATTR_READ` + read-only gate 或 `RECORD_COUNT_SYNC`。 | 保留 `read_anomaly_mastery(...)`；后续 PRD 先批量处理 AM read-then-writeback state-sync，而不是重写公式。 | `calculator-reads`；触达 count/state 顺序时加 focused pytest。 |
| 异常精通 AP | `Calculator.AnomalyMul.cal_ap(...)` / `read_anomaly_proficiency(...)` | `TimeweaverDisorderDmgMul.py` 已迁移 reader-backed 只读门禁；`JaneCinema1APTransToDmgBonus.py`、`JaneCoreSkillStrikeCritRateBonus.py`、`JanePassionStateAPTransToATK.py` 仍是 alias `Mul(...)` read-then-writeback；`VivianCorePassiveTrigger.py`、`VivianCinema6Trigger.py` 读 AP 后伴随已迁移 dispatch publish。 | `ATTR_READ` + read-only gate、`RECORD_COUNT_SYNC` 或 `SCHEDULED_PUBLISH`。 | 继续复用 `read_anomaly_proficiency(...)`；事件伴随样本留给 US-004 分类顺序和 payload。 | `calculator-reads`；Vivian / dispatch 伴随路径加 `implicit-events`。 |
| 冲击力 IMP | `Calculator.StunMul.cal_imp(...)` | `LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py` 直接 `MultiplierData(...)` 后按冲击力换算 count / 攻击力层数。 | `ATTR_READ` + `RECORD_COUNT_SYNC`。 | 新增 `read_impact(...)` 的候选 helper，但本 PRD 不实现；迁移前先锁定 count 公式和 `simple_start(...)` 相对顺序。 | `calculator-reads` + later focused state-sync pytest。 |
| 全量暴击率 | `Calculator.RegularMul.cal_crit_rate(...)` | `CannonRotor.py`、`MiyabiCoreSkill_IceFire.py`、`WoodpeckerElectroSet4_NA.py`、`WoodpeckerElectroSet4_E_EX.py`、`WoodpeckerElectroSet4_CA.py` 仍经 `MultiplierData(...)`。 | `ATTR_READ` + event trigger / RNG gate；部分文件同时是已迁移 scheduled publish 样本。 | 新增 `read_full_crit_rate(...)` 候选 helper；不得与个人暴击率合并，因为全量暴击率包含 `crit_rate_received_increase`。 | `calculator-reads`；事件伴随样本由 US-004 加 `implicit-events`。 |
| 个人暴击率 | `Calculator.RegularMul.cal_personal_crit_rate(...)` | `TriggerAdditionalAbilityStunBonus.py` 直接读取个人暴击率后写 `dy.count`；`JaneCoreSkillStrikeCritRateBonus.py` 是 AP-to-crit-rate count 写回，不是直接 personal crit helper。 | `ATTR_READ` + `RECORD_COUNT_SYNC`。 | 新增 `read_personal_crit_rate(...)` 候选 helper；迁移时验证不包含 `crit_rate_received_increase`。 | `calculator-reads` + focused count/state pytest。 |
| 个人暴击伤害 | `Calculator.RegularMul.cal_personal_crit_dmg(...)` | `Soldier0AnbyCoreSkillCritDMGBonus.py` alias `Mul(...)` 后读取个人暴伤并写 `dy.count`。 | `ATTR_READ` + `RECORD_COUNT_SYNC`。 | 新增 `read_personal_crit_damage(...)` 候选 helper；先保持 `simple_start(...)` 在读取前执行的当前顺序证据。 | `calculator-reads` + focused count/state pytest。 |
| CalAnomaly / formula internals | `CalAnomaly`、`MultiplierData` / `MulData` formula snapshots | `BuffXLogic` 本轮未发现 `MulData(...)`，但 `CalAnomaly` 和完整 Calculator 公式仍保留兼容快照。 | `FORMULA_SNAPSHOT` + `RETAINED_COMPAT_ONLY`。 | 不作为 US-003 / first replacement target；后续只做分类或公式专项 PRD。 | `calculator-reads`；公式专项再加 anomaly focused tests。 |

### 只读门禁与读后写回边界

| 分组 | 文件 / 符号 | 当前行为证据 | 后续约束 |
| --- | --- | --- | --- |
| 已迁移 reader-backed 只读门禁 | `BranchBladeSongCritDamageBonus.special_judge_logic()`、`TimeweaverDisorderDmgMul.special_judge_logic()` | 构造 `BuffAttributeReadContext`，调用 `CalculatorBuffAttributeReader.read_anomaly_mastery(...)` / `read_anomaly_proficiency(...)`。 | 作为 parity 样本保留；后续扩 helper 时复用测试形态，不回退到新 `MultiplierData(...)`。 |
| retained 只读 / trigger gate | `WoodpeckerElectroSet4_*`、部分 full crit rate gate | 读取全量暴击率后按 RNG / SkillNode 条件触发，不应和 count 写回样本混为一组。 | US-004 继续检查触发顺序；US-003 只把它们放入 full crit rate helper bucket。 |
| read-then-writeback | `AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomaly*.py`、`Jane*.py`、`LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py` | 读取 helper 结果后执行或围绕 `simple_start(...)`、`dy.count`、`update_to_buff_0(...)`、record 字段写回。 | 未来 PRD 必须同时验证 reader parity 和 state-sync 顺序；不要只替换 read expression。 |
| event-adjacent read | `CannonRotor.py`、`MiyabiCoreSkill_IceFire.py`、`VivianCorePassiveTrigger.py`、`VivianCinema6Trigger.py` | 属性读取与已迁移 `ScheduleDispatchPort` producer 或本地触发语义相邻。 | 保留 scheduled publish / listener / runtime write 分层；事件分类归 US-004，不在属性读取 PRD 中重开 raw queue backlog。 |

### Follow-up PRD 分组

| 候选组 | 候选文件 / 符号 | Ralph-sized 工作方向 | 保留边界 | 验证入口 | 非目标 |
| --- | --- | --- | --- | --- | --- |
| AM/AP reader parity expansion | `AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`、`YuzuhaAdditionalAbilityAnomalyDmgBonus.py`、`JaneCinema1APTransToDmgBonus.py`、`JaneCoreSkillStrikeCritRateBonus.py`、`JanePassionStateAPTransToATK.py` | 先抽可复用 attribute reader call + state-sync harness，批量验证 AM/AP 读取等价和 count 写回顺序。 | `MultiplierData` 公式快照、old containers、`simple_start(...)` / `dy.count` / `update_to_buff_0(...)` 顺序。 | `calculator-reads` + focused state-sync pytest。 | 不删除 `MultiplierData`，不重写 Jane / Yuzuha 公式，不顺手迁移 event producers。 |
| Impact reader candidate | `LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py`、`Calculator.StunMul.cal_imp(...)` | 设计 `read_impact(...)` parity helper，并把两个 count/writeback 样本作为一组。 | `StunMul` formula snapshot 和 count 换算公式。 | `calculator-reads` + focused count pytest。 | 不重写完整 stun formula，不改 lifecycle runtime write path。 |
| Crit reader candidates | `CannonRotor.py`、`MiyabiCoreSkill_IceFire.py`、`WoodpeckerElectroSet4_*`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py` | 分开设计 `read_full_crit_rate(...)`、`read_personal_crit_rate(...)`、`read_personal_crit_damage(...)`，并用代表样本证明全量 / 个人暴击语义差异。 | `crit_rate_received_increase` 只属于 full crit rate；scheduled publish 样本保持 `ScheduleDispatchPort`。 | `calculator-reads`; event-adjacent files add `implicit-events` in US-004. | 不把 crit helper PRD 做成一个单文件 Trigger / Soldier 薄切片。 |
| Formula snapshot classification | `zsim/sim_progress/ScheduledEvent/Calculator.py`、`zsim/sim_progress/ScheduledEvent/CalAnomaly.py` | 只记录 Calculator / CalAnomaly formula internals 和 `MultiplierData.get_buff_bonus()` 聚合责任，等 reader helper 稳定后再评估收缩。 | `FORMULA_SNAPSHOT` / retained compatibility only。 | `calculator-reads`; formula behavior changes require dedicated focused tests. | 不在阶段 2 classification PRD 中替换完整伤害 / 异常公式。 |

### US-003 结论

- 属性读取分类仍是非排他的：一个 XLogic 可同时属于 `ATTR_READ`、`RECORD_COUNT_SYNC`、`EVENT_TRIGGER`、`SCHEDULED_PUBLISH` 和 `SERVICE_LOCATION`。
- 当前可复用方向应按 helper family 分组，而不是按角色文件排序：AM/AP 已有 reader-backed 样本，impact / full crit / personal crit rate / personal crit damage 是下一批候选。
- `Calculator` / `CalAnomaly` 内部公式快照和 `MultiplierData.get_buff_bonus()` 聚合层继续标记为 `FORMULA_SNAPSHOT` / `RETAINED_COMPAT_ONLY`；本故事不删除、不重写。
- 后续实现型 PRD 必须区分 read-only gate 与 read-then-writeback。后者需要同时覆盖 record / count / state-sync 顺序，不能只替换 `MultiplierData(...)` 表达式。
- 事件相邻属性读取样本只在本节归入 helper bucket；`LoadingMission`、`SkillNode`、dispatch payload、publish order 和 listener / runtime 分层留给 US-004。

## US-004 事件触发 / scheduled publish 分类

本节只分类事件触发与计划发布耦合，不编辑 XLogic、handler、adapter 或验证脚本。分类仍为非排他：同一文件可同时属于 `EVENT_TRIGGER`、`SCHEDULED_PUBLISH`、`RECORD_COUNT_SYNC`、`ATTR_READ`、`BYPASS_ANOMALY_DOT_DEBUFF` 和 `RETAINED_COMPAT_ONLY`。

### 可复现扫描命令

```powershell
rg --files zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "create_schedule_dispatch_port|publish_scheduled|ScheduleDispatchPort" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "schedule_preload_event_factory|SchedulePreload" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "event_list" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "find_event_list|record\.event_list|BuffRecordBaseClass\.event_list|event_list\s*\.append|check_preparation\([^\n]*event_list|event_list=True" zsim/sim_progress/Buff/BuffXLogic zsim/sim_progress/Buff/JudgeTools zsim/sim_progress/Buff --glob '*.py' --glob '!__init__.py'
rg -n "LoadingMission|SkillNode|preload_tick|schedule_priority" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "change_process_state" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
```

### 扫描计数

| 扫描项 | files | lines | matches | 结论 |
| --- | ---: | ---: | ---: | --- |
| baseline BuffXLogic files | 149 | n/a | n/a | 继续使用 US-002 root-workspace census，排除 `.codex_worktrees/`。 |
| direct dispatch publish terms | 14 | 45 | 45 | 这些是已迁移 `ScheduleDispatchPort` 生产者或 helper 引用，不作为 raw queue backlog。 |
| `schedule_preload_event_factory` / `SchedulePreload` | 2 | 4 | 4 | `SeedCinema6Trigger.py`、`YuzuhaCinema6SheelTrigger.py` 通过工厂构造 `SchedulePreload`，工厂内部走 dispatch port。 |
| `event_list` text | 4 | 4 | 4 | 仅剩 docstring / 注释旧措辞：`AlicePolarizedAssaultTrigger.py`、`VivianCoattackTrigger.py`、`YanagiPolarityDisorderTrigger.py`、`YixuanCinema1Trigger.py`。 |
| deleted raw surfaces | 0 | 0 | 0 | 未发现 root-workspace production `find_event_list`、`record.event_list`、`event_list.append(...)` 或 `event_list=True` 复开证据。 |
| trigger timing terms | 60 | 190 | 197 | 多数是 `SkillNode` / `LoadingMission` / `preload_tick` 触发门禁，需按语义分类，不等同 scheduled publish。 |
| report process-state helper | 22 | 34 | 34 | `change_process_state()` 是 report / debug 状态更新，不是计划事件发布或 runtime write facade。 |

### CodeGraph 导航证据

- Query seed：`US-004 Classify Event Trigger And Scheduled-Publish Couplings`、`ScheduleDispatchPort`、`create_schedule_dispatch_port`、`publish_scheduled`、`LoadingMission`、`SkillNode`、`preload_tick`、`schedule_priority`、`AlicePolarizedAssaultTrigger`、`CannonRotor`、`HugoCorePassiveTotalizeTrigger`、`MiyabiCoreSkill_IceFire`、`VivianDotTrigger`、`VivianCorePassiveTrigger`、`VivianCinema6Trigger`、`YanagiPolarityDisorderTrigger`、`YixuanCinema1Trigger`、`ScheduleRefreshData`、`PolarizedAssaultEvent`、`StunForcedTerminationEvent`、`DirgeOfDestinyAnomaly`、`PolarityDisorder`、`SchedulePreload`、`schedule_preload_event_factory`。
- Boundary findings：`ScheduleDispatchPort.publish_scheduled(...)` remains queue-only; `create_schedule_dispatch_port(...)` creates a fresh adapter from current `sim_instance` / `schedule_data` and keeps raw `schedule_data.event_list` hidden inside `LegacyEventListScheduleDispatchAdapter`.
- `codegraph_callers("publish_scheduled")` found the 14 root BuffXLogic direct publishers plus adjacent non-Buff producers (`BreakingLegManager.update_decibel(...)`, `DecibelManager.add_decibel_to_char(...)`); `.codex_worktrees/` duplicates were treated as historical navigation evidence only.
- Representative source/callee inspection confirmed ordering-sensitive samples: `CannonRotor`, `HugoCorePassiveTotalizeTrigger`, `YixuanCinema1Trigger`, and `VivianDotTrigger` call `LoadingMission.mission_start(...)` or prepare runtime dot state before publish; `YanagiPolarityDisorderTrigger` clears the record signal after publish; `AlicePolarizedAssaultTrigger` clears `trigger_origin` after publish.
- Nearby payload source confirms timing / priority fields: `SkillNode.preload_tick` drives skill scheduling, `LoadingMission` expands hit/start/end windows, `PolarizedAssaultEvent` sets `execute_tick` and `schedule_priority = 998`, `StunForcedTerminationEvent` sets `execute_tick` and `schedule_priority = 999`, copied anomaly payloads inherit `AnomalyBar.schedule_priority = 999`, and `SchedulePreload.execute_tick` is created from the factory's `preload_tick_list`.

### Scheduled publish buckets

| bucket | files / symbols | expected payload | target / fan-out | timing / priority evidence | retained boundary / validation |
| --- | --- | --- | --- | --- | --- |
| Direct `SkillNode` publish for extra attacks | `CannonRotor.py` `special_hit_logic`、`MiyabiCoreSkill_IceFire.py` `special_exit_logic`、`VivianDotTrigger.py` `special_hit_logic`、`YixuanCinema1Trigger.py` `special_hit_logic`、`HugoCorePassiveTotalizeTrigger.py` `special_hit_logic` | `SkillNode` produced by `spawn_node(...)` or dot-owned `skill_node_data` | Scheduled queue to skill handler / preload execution; target is the generated extra attack node. | Current tick or node `preload_tick`; `CannonRotor`、`Hugo`、`Yixuan`、`VivianDot` preserve `LoadingMission.mission_start(...)` before `publish_scheduled(...)`. | Already migrated to `ScheduleDispatchPort`; validate with `implicit-events` and focused tests `test_cannon_rotor_dispatch.py`、`test_miyabi_core_skill_icefire_dispatch.py`、`test_vivian_dot_trigger_dispatch.py`、`test_yixuan_cinema1_dispatch.py`、`test_hugo_totalize_dispatch.py`. |
| Scheduled resource refresh | `ElegantVanitySpRecover.py`、`LunarNoviluna.py`、`MagneticStormCharlieSpRecover.py`、`SeedAdditionalAbilityTrigger.py`、`SliceofTimeExtraResources.py` | `ScheduleRefreshData(sp_target, sp_value, decibel_target, decibel_value)` | Refresh handler updates named character SP / decibel targets. | Payload has no custom `schedule_priority`; queue order remains adapter append order and handler semantics. `ElegantVanitySpRecover` keeps `simple_start(...)` before publish. | Already migrated to `ScheduleDispatchPort`; validate with `implicit-events`, especially `test_xstart_sp_refresh_dispatch.py`、`test_xhit_sp_refresh_dispatch.py`、`test_slice_of_time_extra_resources_dispatch.py`. |
| Copied anomaly / anomaly event publish | `AlicePolarizedAssaultTrigger.py`、`YanagiPolarityDisorderTrigger.py`、`VivianCorePassiveTrigger.py`、`VivianCinema6Trigger.py` | `PolarizedAssaultEvent`、`PolarityDisorder` from `spawn_output(...)`、`DirgeOfDestinyAnomaly` | Scheduled anomaly / polarized-assault handlers; later listener broadcast remains inside event or handler layer, not the XLogic publish layer. | Alice publishes `execute_tick=tick`, `schedule_priority=998`; Yanagi and Vivian publish copied anomaly payloads that retain anomaly priority semantics. | Already migrated to `ScheduleDispatchPort`; keep Calculator/AP formula snapshots untouched. Validate with `implicit-events` focused tests for Alice, Yanagi, Vivian core passive, Vivian cinema 6. |
| Hugo forced stun termination side payload | `HugoCorePassiveTotalizeTrigger.py` after totalize `SkillNode` publish | Optional `StunForcedTerminationEvent(enemy, feed_back_ratio, execute_tick=tick, event_source="雨果")` | Scheduled event handler terminates / restores enemy stun state. | `schedule_priority=999`; published after the totalize `SkillNode`, preserving source order when the event exists. | Same `ScheduleDispatchPort` boundary; validate with `test_hugo_totalize_dispatch.py` and `implicit-events`. |
| Factory-backed `SchedulePreload` publish | `SeedCinema6Trigger.py`、`YuzuhaCinema6SheelTrigger.py` via `schedule_preload_event_factory(...)` | `SchedulePreload(preload_tick, skill_tag, preload_data, apl_priority, active_generation)` created inside factory | Factory publishes through `create_schedule_dispatch_port(...)`; target is later `PreloadData.external_add_skill(...)` in `SchedulePreload.execute_myself()`. | `execute_tick` comes from `preload_tick_list`; factory rejects past ticks. Seed publishes three same-tick events; Yuzuha publishes one same-tick event after charge gate. | Retained factory helper already uses dispatch port; future work should add focused coverage before changing it. Validate with `implicit-events`; do not rewrite into raw queue append. |

### Trigger-only / retained local event groups

| bucket | files / examples | expected payload | target / fan-out | timing / order evidence | validation / non-goal |
| --- | --- | --- | --- | --- | --- |
| `SkillNode` / `LoadingMission` trigger gates with no scheduled publish | 60 timing-term files, including `AstralVoice.py`、`FlightOfFancy.py`、`FlamemakerShakerDmgBonus.py`、`MagneticStormAlphaAMBonus.py`、`MagneticStormBravoApBonus.py`、`WoodpeckerElectroSet4_*.py`、`ShadowHarmony4.py`、`TriggerAfterShockTrigger.py`、`DawnsBloom4SetTriggerNADmgBonus.py`、`HeartstringNocturne.py`、`PhaethonsMelody.py`、`StreetSuperstar.py`、`QingmingBirdcageCompanion*.py`、`YixuanCinema2StunTimeLimitBonus.py`、`YixuanCinema4Tranquility.py`、`YuzuhaSugarBurst*.py` | Usually no scheduled payload; result is local Buff `simple_start(...)`, `dy.count`, record signal, listener state, or `update_to_buff_0(...)`. | Own Buff state or record state; no fan-out into schedule queue. | Uses current tick, `preload_tick`, `is_hit_now(...)`, first-hit / last-hit windows, or `LoadingMission.mission_node`. | Classify for US-005 state-sync or later helper PRDs. Do not treat as planned-event backlog without concrete `publish_scheduled(...)` / factory source evidence. |
| Direct local preload injection | `VivianCoattackTrigger.py` `special_effect_logic` | `input_tuple = (coattack_skill_tag, False, 0)` | Direct `preload_data.external_add_skill(...)`, not `ScheduleDispatchPort`. | Current source has old `eventlist` docstring wording but no `event_list.append(...)`; report branch calls `change_process_state()`. | Retained local preload boundary; later PRD must decide whether to wrap this separately. Not a raw queue producer in this story. |
| Dot runtime registration plus scheduled skill publish | `VivianDotTrigger.py` | Runtime dot object appended to `enemy.dynamic.dynamic_dot_list`; then dot `skill_node_data` is published. | Runtime dot state and scheduled skill queue are separate layers. | `dot.start(tick)` and `dynamic_dot_list.append(dot)` occur before `publish_scheduled(dot.skill_node_data)`. | Keep dot runtime registration separate from scheduled publish; validate with `test_vivian_dot_trigger_dispatch.py` and later anomaly/dot classification. |
| Report / process-state helpers | 22 files with `change_process_state()` | None | Debug/report process-state update only. | Usually gated by `*_REPORT` flags after local mutation or publish. | Do not map to listener broadcast, runtime immediate write, or scheduled publish. |
| Deleted raw queue surfaces | No root-workspace matches for `find_event_list` / `record.event_list` / `BuffRecordBaseClass.event_list` / `event_list.append(...)` / `event_list=True` | None | None | `event_list` hits are only comments/docstrings in four files. | Do not reopen deleted `JudgeTools.find_event_list()`, `check_preparation(..., event_list=...)`, `BuffRecordBaseClass.event_list`, or `record.event_list.append(...)` surfaces unless future guardrails expose file/function/event/payload/target/order evidence. |

### US-004 结论

- Already-closed scheduled publishers remain closed and dispatch-port-backed; no new root-workspace raw queue producer was found.
- Scheduled queue publish, same-tick runtime write, listener broadcast, report-state mutation, local preload injection, and dot runtime registration remain separate classification buckets.
- Event-trigger follow-up work should be grouped by semantic payload and ordering constraint: extra `SkillNode` publish, resource refresh, anomaly / copied anomaly payload, `SchedulePreload` factory, and trigger-only state-sync gates.
- Future implementation PRDs must preserve source order before replacing any callsite: examples include `LoadingMission.mission_start(...)` before publish, dot runtime registration before skill publish, and `publish_scheduled(...)` before later local state reset where the current file does that.

## US-005 record / count / state-sync 分类

本节只分类 `history.record`、record 字段、`dy.count`、`built_in_buff_box`、`simple_start(...)` 和 `update_to_buff_0(...)` 相关状态同步模式；不编辑 XLogic、Buff lifecycle、runtime port、Calculator 或 scheduled-event 生产行为。分类仍为非排他：同一文件可同时属于 `ATTR_READ`、`EVENT_TRIGGER`、`RECORD_COUNT_SYNC`、`SERVICE_LOCATION`、`SCHEDULED_PUBLISH` 或 retained compatibility。

### 可复现扫描命令

```powershell
rg --files zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "^class\s+\w+Record\b" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "history\.record" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "def\s+check_record_module\b|check_record_module\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "def\s+get_prepared\b|get_prepared\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "\bdy\.count\b" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "\bdy\.count\s*[-+*/]?=" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "built_in_buff_box" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "simple_start\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "simple_exit\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "update_to_buff_0\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "cooldown|last_tick|last_update|last_active_tick|startticks|endticks|active_tick_box|update_info_box|counter|c4_counter|e_counter" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "record\.[A-Za-z_][A-Za-z0-9_]*\.dy\.(count|built_in_buff_box|active|ready)|trigger_buff_0\.dy\.(count|built_in_buff_box|active|ready)" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
```

### 扫描计数

根工作区扫描结果如下；`.codex_worktrees/` 仍按阶段 2 规则视为历史证据，不进入生产分类计数。

| pattern | files | lines | matches | 分类含义 |
| --- | ---: | ---: | ---: | --- |
| root `BuffXLogic` files excluding `__init__.py` | 149 | - | - | US-005 的生产取证全集。 |
| `^class\s+\w+Record\b` | 138 | 138 | 138 | 大多数 leaf XLogic 有自定义 record class，record 复用设计不能只看单个模板。 |
| `history\.record` | 142 | 427 | 427 | record 懒初始化与 `self.record = self.buff_0.history.record` 是主流兼容模式。 |
| `check_record_module` | 142 | 344 | 344 | record / template 定位入口，通常经 `JudgeTools.find_exist_buff_dict(...)` 找 `buff_0`。 |
| `get_prepared` | 142 | 344 | 344 | `check_preparation(...)` 转发入口，用于补齐 char、enemy、sub dict、action stack、trigger buff 等上下文。 |
| `dy.count` read/write | 37 | 54 | 58 | 包含 read-only trigger buff gates、直接 count assignment 和旧 count 调整。 |
| `dy.count` assignment | 33 | 46 | 46 | 需要 state-sync 顺序验证的核心候选。 |
| `built_in_buff_box` | 5 | 8 | 8 | 包含 tuple-box 写回、读取 gate 和历史注释，不等价于统一替换面。 |
| `simple_start(...)` | 43 | 49 | 49 | 主要 lifecycle 激活入口，后续 helper 必须保留与 count / tuple-box 的相对顺序。 |
| `simple_exit(...)` | 0 | 0 | 0 | 当前 BuffXLogic 根工作区没有直接调用；退出语义不作为 US-005 替换目标。 |
| `update_to_buff_0(...)` | 32 | 32 | 32 | 模板 Buff 回写锚点，仍依赖旧 `buff_0` 身份。 |
| cooldown / last-tick / counter state | 34 | 181 | 205 | record 中的限频、去重、持续时间、计数器和信号字段。 |

### CodeGraph 导航证据

- Query seed：`US-005 Classify Record, Count, And State-Sync Patterns`、`history.record`、`record`、`dy.count`、`built_in_buff_box`、`simple_start`、`simple_exit`、`update_to_buff_0`、`check_record_module`、`get_prepared`、`BuffRecordBaseClass`、`BasicComplexBuffClass`、`AstraYaoCorePassiveAtkBonus`、`KaboomTheCannon`、`SeveredInnocenceCritDMGBonus`、`SteamOven`。
- `BasicComplexBuffClass.check_record_module(...)` 是共享模板样本：按 `char_name` 经 `JudgeTools.find_exist_buff_dict(...)` 定位 `buff_0`，懒创建 `RECORD_CLASS()`，然后绑定 `self.record`。
- `_buff_record_base_class.BuffRecordBaseClass.check_cd(...)` 只用 `cd` 与 `last_active_tick` 判断就绪，是 record-state helper 的最小限频样本；它不触达 scheduled publish 或 runtime write。
- Representative source inspection confirmed state-sync order samples:
  - `AstraYaoCorePassiveAtkBonus.special_start_logic()` 先用 `update_info_box` 防同 tick 重复，随后 `simple_start(...)`、写 `startticks` / `endticks`、写 `dy.count`、更新 `record.update_info_box`，最后 `update_to_buff_0(...)`。
  - `KaboomTheCannon.special_hit_logic()` 先更新并清理 `record.active_char_dict`，再 `simple_start(..., not_count=True)`，把 active character tick list 写入 `dy.built_in_buff_box`，最后回写 `buff_0`。
  - `SeveredInnocenceCritDMGBonus.special_start_logic()` 先消费 `record.update_signal` 并刷新 `record.active_tick_box`，再 `simple_start(..., no_count=1)`，重建 `dy.built_in_buff_box`，写 `dy.count = len(...)`，最后 `update_to_buff_0(...)`。
  - `SteamOven.special_effect_logic()` 先按 action / energy 更新 `record.E_EX_started`、`record.last_update_count` 和 `record.last_update_tick`，再 `simple_start(...)`、写 `dy.count`、回写 `buff_0`。
- CodeGraph 同样命中 `.codex_worktrees/` 历史副本；这些结果只作为导航提醒，root-workspace `rg` 与当前源码才是本节分类依据。

### State-sync buckets

| bucket | representative files / symbols | 当前行为证据 | 复用候选 | 验证建议 / 非目标 |
| --- | --- | --- | --- | --- |
| Record initialization and context prep | `BasicComplexBuffClass.py`、`_char_buff_mod.py`、`_euipment_buff_mod.py`、大多数 leaf `check_record_module()` / `get_prepared()` | 142 files hit `history.record` / `check_record_module`; record 创建通常绑定旧 `buff_0.history.record`，上下文由 `check_preparation(...)` 补齐。 | Record initialization helper 或 typed record/context base；先收敛初始化模板，不替换旧容器身份。 | 后续 focused tests 应 patch `JudgeTools.find_exist_buff_dict(...)` / `check_preparation(...)`，证明 record 懒创建和 context 字段不漂移；不复开 `event_list=True`。 |
| Pure record / trigger-buff reads | `AstralVoice.py`、`FlamemakerShakerApBonus.py`、`CordisGerminaSNAAndQIgnoreDefense.py`、`SpectralGazeImpactBonus.py`、`SharpenedStingerAnomalyBuildupBonus.py`、`YangiCinema1ApBonus.py` | P2-C 已把前五个 root 文件迁移到 `read_trigger_buff_state(record)`；`YangiCinema1ApBonus.py` 与剩余 `trigger_buff_0=` pool 仍保留为后续分类输入。 | Completed guarded trigger-state helper for migrated files；remaining candidates must stay outside the P2-C migrated-file guardrail until explicitly migrated. | 已迁移文件由 no-write / count-mirror focused tests 与 P2-C guardrail 维护；剩余 pool 先按 read-only gate / read-then-writeback / event-adjacent 分组，不把读 gate 改成 scheduled publish。 |
| Computed count writeback | `AliceAdditionalAbilityApBonus.py`、`JaneCinema1APTransToDmgBonus.py`、`JaneCoreSkillStrikeCritRateBonus.py`、`JanePassionStateAPTransToATK.py`、`LighterAdditionalAbility_IceFireBonus.py`、`QingYiAdditionalAbilityStunConvertToATK.py`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py`、`YuzuhaAdditionalAbilityAnomaly*.py` | Attribute / formula result is converted into `count`; current order normally includes `simple_start(..., no_count=1)` before `dy.count = count`, then `update_to_buff_0(...)`。 | State-sync helper paired with `BuffAttributeReader` parity, grouped by helper family rather than by role file. | Later tests must assert formula parity plus `simple_start(...) -> dy.count -> update_to_buff_0(...)` order; do not only replace `MultiplierData(...)` expression. |
| Incremental / old-count adjustment | `LinaCoreSkillPenRatioBonus.py`、`LighterUniqueSkillStunBonus.py`、`MiyabiCoreSkill_IceFire.py`、`QingYiCoreSkillStunDMGBonus.py`、`QingYiCoreSkillExtraStunBonus.py`、`FlamemakerShakerDmgBonus.py` | Several files call `simple_start(...)`, then adjust old `buff_0.dy.count` or current `dy.count` before final count assignment and template sync. | Count-adjustment helper with explicit old-count snapshot and final clamp. | High risk: tests must pin whether old `buff_0.dy.count` is decremented before recomputing current `dy.count`; no lifecycle-wide refactor in phase-2 classification stories. |
| `built_in_buff_box` tuple sync | `KaboomTheCannon.py`、`SeveredInnocenceCritDMGBonus.py`、`WeepingGeminiApBonus.py` plus read-only `CordisGerminaSNAAndQIgnoreDefense.py` and comment-only `SteamOven.py` | Active windows are stored as list/tuple boxes; some files write `dy.built_in_buff_box`, some only read trigger buff boxes or document expected shape. | Tuple-box state-sync helper that owns pruning, rebuild, count derivation, and template sync separately from simple count assignment. | Later focused tests should verify expired window pruning, tuple payload shape, derived `dy.count`, and no accidental conversion of read-only gates into writers. |
| Timing / cooldown / per-target ledger state | `AstraYaoCorePassiveAtkBonus.py`、`SteamOven.py`、`YuzuhaHardCandyShotTrigger.py`、`SeedCinema6Trigger.py`、`SliceofTimeExtraResources.py`、`YixuanCinema4Tranquility.py`、`YanagiPolarityDisorderTrigger.py` | 34 files hit cooldown / last-tick / counter terms; patterns include `update_info_box`, `last_update_tick`, `last_active_tick`, `active_tick_box`, `e_counter`, `c4_counter`, and trigger signals. | Ledger / cooldown helper candidates, likely separate from count formula helpers because ordering and reset semantics differ. | Pin no-publish and publish-adjacent branches separately. `YanagiPolarityDisorderTrigger` record reset after publish remains event/anomaly ordering evidence from US-004, not a state-only replacement target. |
| Template sync writeback | 32 files with `update_to_buff_0(...)`; examples above plus `AstraYaoCorePassiveAtkBonus.py`、`SteamOven.py`、`SeveredInnocenceCritDMGBonus.py` | Current Buff instance writes dynamic fields, then `update_to_buff_0(...)` copies them back to old template Buff identity. | Template-sync helper around final writeback only after state value parity is locked. | Retain old `exist_buff_dict` / `buff_0` identity; do not replace old containers, `buff_add()`, `KickOutBuff()`, or lifecycle settle semantics here. |

### High-risk ordering constraints

| constraint | source evidence | later test shape |
| --- | --- | --- |
| `simple_start(...)` before manual `dy.count` write | `AliceAdditionalAbilityApBonus.py`、`Jane*.py`、`YuzuhaAdditionalAbility*.py`、`AstraYaoCorePassiveAtkBonus.py`、`SteamOven.py` | Spy or fake Buff should assert start call precedes count assignment and `update_to_buff_0(...)`; for no-count variants, assert `simple_start(..., no_count=1)` remains unchanged. |
| Old count snapshot/decrement before recompute | `LinaCoreSkillPenRatioBonus.py`、`LighterUniqueSkillStunBonus.py`、`MiyabiCoreSkill_IceFire.py`、`QingYiCoreSkillStunDMGBonus.py` | Tests should seed `buff_0.dy.count` and assert decrement / clamp semantics before final template sync. |
| Record ledger update around state write | `AstraYaoCorePassiveAtkBonus.py` updates `record.update_info_box` after current Buff end/count fields; `SteamOven.py` updates record counters before `simple_start(...)` and count write. | Separate same-tick no-op branch from update branch; assert record ledger state and Buff state both match old behavior. |
| Tuple-box rebuild before derived count | `SeveredInnocenceCritDMGBonus.py` rebuilds `dy.built_in_buff_box` from `active_tick_box` before `dy.count = len(...)`; `KaboomTheCannon.py` writes active tick windows without explicit `dy.count` assignment. | Focused tests should assert tuple box payload and derived / implicit count behavior, not only active flag. |
| Event ordering remains outside state-sync helper | `CannonRotor` / `Hugo` / `Yixuan` `mission_start(...) -> publish` and `Yanagi` reset-after-publish were classified in US-004. | Do not fold scheduled publish order into a generic record helper; event PRDs keep `ScheduleDispatchPort` tests. |

### Follow-up state-sync PRD groups

| candidate group | candidate files / symbols | Ralph-sized work direction | retained boundaries | validation entrypoints | non-goals |
| --- | --- | --- | --- | --- | --- |
| AM/AP computed count state-sync | `AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`、`YuzuhaAdditionalAbilityAnomalyDmgBonus.py`、`JaneCinema1APTransToDmgBonus.py`、`JaneCoreSkillStrikeCritRateBonus.py`、`JanePassionStateAPTransToATK.py` | Pair existing AM/AP `BuffAttributeReader` parity with a focused state-sync harness for count writeback. | `MultiplierData` formula snapshot, old `buff_0` identity, `simple_start(..., no_count=1)` and `update_to_buff_0(...)` order. | `calculator-reads` plus new focused count/state pytest. | Do not delete `MultiplierData`; do not migrate scheduled publishers in the same PRD. |
| Tuple-box state helper | `KaboomTheCannon.py`、`SeveredInnocenceCritDMGBonus.py`、`WeepingGeminiApBonus.py` | Design tuple-box helper for active window pruning / rebuild and derived count, then migrate one coherent bucket after tests exist. | `built_in_buff_box` payload shape and template sync. | `implicit-events` plus focused tuple-box pytest. | Do not treat read-only `CordisGerminaSNAAndQIgnoreDefense.py` as a writer. |
| Incremental old-count adjustment | `LinaCoreSkillPenRatioBonus.py`、`LighterUniqueSkillStunBonus.py`、`MiyabiCoreSkill_IceFire.py`、`QingYiCoreSkillStunDMGBonus.py`、`QingYiCoreSkillExtraStunBonus.py` | Isolate old-count snapshot / decrement / clamp behavior before proposing helper extraction. | Calculator formula snapshots, stun/anomaly runtime state, old `buff_0` count semantics. | `calculator-reads` where formulas are touched; otherwise focused state-sync pytest plus `implicit-events`. | Do not rewrite full lifecycle settle or runtime write facade. |
| Ledger / cooldown helpers | `AstraYaoCorePassiveAtkBonus.py`、`SteamOven.py`、`YuzuhaHardCandyShotTrigger.py`、`SeedCinema6Trigger.py`、`SliceofTimeExtraResources.py`、`YixuanCinema4Tranquility.py` | Classify and test per-target ledgers, last-tick gates, cooldown counters, and no-duplicate same-tick branches before extraction. | Existing `check_record_module()` / `get_prepared()` context, record field names, report-only `change_process_state()`. | `implicit-events`; add branch-focused pytest for no-op vs update. | Do not generalize event publish, dot runtime registration, or listener broadcast into this helper. |

### US-005 结论

- Record/count/state-sync patterns are broad enough to require reusable helper design before replacement: record initialization, pure trigger-state reads, computed count writes, incremental count adjustment, tuple-box sync, ledger/cooldown state, and template sync are separate buckets.
- `simple_start(...)` / `dy.count` / `update_to_buff_0(...)` ordering is the main compatibility risk for later implementation stories; source evidence shows multiple variants, so one generic helper should not be introduced until focused tests pin each variant.
- `simple_exit(...)` has no root-workspace BuffXLogic callsite in this scan; exit/lifecycle refactor should stay out of this PRD unless a future story supplies concrete source evidence.
- Existing phase-1 retained boundaries remain unchanged: no old container deletion, no second runtime write facade, no `BuffRuntimeReadPort` write expansion, no reopened raw queue surfaces, and no live XLogic behavior replacement.

## US-006 runtime container / service-location 分类

本节只分类 `sim_instance`、`JudgeTools.find_*`、旧 runtime 容器和 service-location 耦合；不编辑 `BuffXLogic`、runtime ports、facade、lifecycle 或 validation wiring。分类仍为非排他：同一文件可同时属于 `SERVICE_LOCATION`、`ATTR_READ`、`RECORD_COUNT_SYNC`、`RUNTIME_IMMEDIATE_WRITE` 或 retained compatibility。

### 可复现扫描命令

```powershell
rg --files zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "sim_instance" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "JudgeTools\.find_|find_exist_buff_dict|find_sub_exist_buff_dict|find_dynamic_buff_list|find_loading_buff_dict|find_char_from_|find_tick|find_stack|find_preload_data|find_enemy" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "exist_buff_dict|sub_exist_buff_dict|dynamic_buff_list|DYNAMIC_BUFF_DICT|LOADING_BUFF_DICT|dynamic_buff|loading_buff" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "BuffRuntimeReadPort|LegacyBuffRuntimeFacade|RuntimeCommandPort|LegacyRuntimeCommandAdapter" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -n "buff_add\(|KickOutBuff\(" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
```

### 扫描计数

根工作区扫描结果如下；`.codex_worktrees/` 仍按阶段 2 规则视为历史证据，不进入生产分类计数。

| pattern | files | lines | matches | 分类含义 |
| --- | ---: | ---: | ---: | --- |
| root `BuffXLogic` files excluding `__init__.py` | 149 | - | - | US-006 的生产取证全集。 |
| `sim_instance` | 148 | 421 | 747 | 几乎全部 XLogic 仍从 Buff 实例 service-locate runtime 上下文；后续需按触达面拆分，不可整体替换。 |
| `JudgeTools.find_*` / exported helper terms | 148 | 323 | 323 | `check_record_module()`、`check_preparation(...)` 和直接 helper 调用仍是旧上下文定位主路径。 |
| old container terms | 144 | 355 | 380 | 多数是 record 字段、`check_preparation(...)` 参数和 Calculator 输入，不等价于 raw container write。 |
| runtime boundary names in BuffXLogic | 0 | 0 | 0 | `BuffXLogic` 当前未直接依赖 `RuntimeCommandPort` / `BuffRuntimeReadPort` 名称；边界仍在 handler / simulator / facade 层。 |
| direct `buff_add()` / `KickOutBuff()` in BuffXLogic | 0 | 0 | 0 | 未发现 XLogic 直接调用 legacy lifecycle helpers；它们仍是 retained lifecycle / facade internals。 |
| `find_exist_buff_dict` | 142 | 142 | 142 | 模板 Buff registry 身份定位，通常用于 `buff_0` / `history.record` 懒初始化。 |
| `find_dynamic_buff_list` | 1 | 1 | 1 | 直接 helper 只剩 `IceJadeTeaPotExtraDMGBonus.py`；更多 dynamic reads 通过 `check_preparation(dynamic_buff_list=1)`。 |
| `dynamic_buff_list=1` | 20 | 21 | 21 | Calculator / reader snapshot 输入，优先归 `BuffRuntimeReadPort` 或 attribute reader parity 候选。 |
| `sub_exist_buff_dict=1` | 46 | 47 | 47 | `simple_start(...)` / template sync 所需旧模板子字典，继续标记为 old registry compatibility。 |
| `trigger_buff_0=` | 21 | 42 | 42 | 读取旧模板 Buff 的动态状态；后续可按 trigger-state read-port helper 分类。 |
| direct `sim_instance.tick` | 24 | 37 | 37 | 当前 tick read；通常属于显式 context 候选，不是 runtime write。 |
| direct `sim_instance.schedule_data` | 22 | 36 | 36 | 主要是 `enemy`、report `change_process_state()`、已迁移 dispatch 创建和 local runtime state；需按语义分类。 |
| direct `sim_instance.preload` / `char_data` | 6 | 6 | 6 | local preload / character service-location；不归入 Buff old-container facade。 |
| `listener_manager` / `rng_instance` | 9 | 10 | 10 | listener broadcast / RNG service 仍是独立 service boundary，不应映射到 runtime container helper。 |
| uppercase `DYNAMIC_BUFF_DICT` / `LOADING_BUFF_DICT` in BuffXLogic | 0 | 0 | 0 | XLogic 不直接按全局容器名访问 active / pending store。 |

### CodeGraph 导航证据

- Query seed：`US-006 Classify Runtime Container And Service-Location Couplings`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort`、`LegacyBuffRuntimeFacade`、`BuffAddStrategy`、`buff_add`、`KickOutBuff`、`DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT`、`exist_buff_dict`、`sub_exist_buff_dict`、`dynamic_buff_list`、`JudgeTools.find_*`、`check_preparation`、`BasicComplexBuffClass`、`AliceAdditionalAbilityApBonus`、`IceJadeTeaPotExtraDMGBonus`、`YuzuhaHardCandyShotTrigger`。
- `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 仍是 same-tick command boundary：`update_anomaly(...)` 委托 `legacy_update_anomaly(...)` 并传入当前 `ScheduleData.event_list`、`dynamic_buff`、`BuffRuntimeReadPort` 和 `sim_instance`；`settle_buffs(...)` 委托 retained `ScheduleBuffSettle`，并保留旧 `exist_buff_dict`、`dynamic_buff`、`action_stack` 和 `sim_instance` 身份。
- `BuffRuntimeReadPort` 仍是只读主契约：active Buff view / exist snapshot 是推荐读口；`get_legacy_dynamic_buff_dict()` / `get_legacy_exist_buff_dict()` 是同 tick 兼容读取，不是新写 API。
- `LegacyBuffRuntimeFacade` 按引用包住 `exist_buff_dict`、`LOADING_BUFF_DICT`、`DYNAMIC_BUFF_DICT` 和 `enemy.dynamic.dynamic_debuff_list`；`activate_pending_buffs(...)`、`_activate_pending_buff(...)`、`update_time_related_effects(...)` 证明 pending queue、active store、enemy mirror 和 lifecycle tick sweep 当前都在 adapter / facade 内保留旧容器身份。
- `JudgeTools.FindMain` 仍直接读取 `sim_instance.schedule_data.enemy`、`sim_instance.global_stats.DYNAMIC_BUFF_DICT`、`sim_instance.load_data.exist_buff_dict`、`sim_instance.load_data.action_stack`、`sim_instance.preload.preload_data` 和 `sim_instance.tick`；`check_preparation(...)` 是 leaf XLogic 的主 service-location 转发层。
- Representative XLogic source confirms拆分：`AliceAdditionalAbilityApBonus` 通过 `check_preparation(..., sub_exist_buff_dict=1, enemy=1, dynamic_buff_list=1)` 读 runtime snapshot 并写 count/state；`YuzuhaHardCandyShotTrigger` 直接使用 `sim_instance.preload.preload_data` 做占用检查后执行 local Character action；`IceJadeTeaPotExtraDMGBonus` 是少数直接 `find_dynamic_buff_list(...)` 样本。
- CodeGraph again surfaced `.codex_worktrees/` historical duplicates for runtime and XLogic symbols; root-workspace `rg` counts above exclude them and no blocker conclusion depends on archived worktree evidence.

### Runtime / service-location buckets

| bucket | representative files / symbols | 当前行为证据 | 现有边界 / 未来候选 | 验证建议 / 非目标 |
| --- | --- | --- | --- | --- |
| Static registry / template identity lookup | `BasicComplexBuffClass.py`、`_char_buff_mod.py`、`_euipment_buff_mod.py`、142 files with `find_exist_buff_dict` | `check_record_module()` finds `buff_0` in `load_data.exist_buff_dict` and stores `history.record`; `sub_exist_buff_dict=1` supplies `simple_start(...)` / `update_to_buff_0(...)` identity. | Retained compatibility helper first; later typed record/context helper may hide lookup shape but must keep old `buff_0` identity. | Focused tests should patch `JudgeTools.find_exist_buff_dict(...)`; do not delete old templates or `update_to_buff_0(...)` in phase-2 classification. |
| Runtime read snapshot for formulas and trigger gates | `AliceAdditionalAbilityApBonus.py`、`Jane*.py`、`LighterAdditionalAbility_IceFireBonus.py`、`TriggerAdditionalAbilityStunBonus.py`、`Soldier0AnbyCoreSkillCritDMGBonus.py`、`IceJadeTeaPotExtraDMGBonus.py` | `dynamic_buff_list=1` or direct `find_dynamic_buff_list(...)` feeds Calculator / reader snapshot; `trigger_buff_0` reads old template Buff state. | Future `BuffRuntimeReadPort` read stories or `BuffAttributeReader` parity helpers; keep read-only contract. | `calculator-reads` for formula parity; add state-sync focused tests when count/writeback follows. Do not expand `BuffRuntimeReadPort` into writes. |
| Runtime immediate write / lifecycle command boundary | `RuntimeCommandPort.update_anomaly(...)`、`RuntimeCommandPort.settle_buffs(...)`、`LegacyRuntimeCommandAdapter` | Same-tick writes still call legacy `update_anomaly` / `ScheduleBuffSettle` behind one command port, carrying old container identity inside the adapter. | Existing `RuntimeCommandPort` only; no second write facade. | `implicit-events`; default lifecycle profile only when implementation touches lifecycle wiring. No XLogic replacement in this story. |
| Pending queue / active store facade internals | `LegacyBuffRuntimeFacade.activate_pending_buffs(...)`、`_activate_pending_buff(...)`、`update_time_related_effects(...)`、legacy `buff_add()` / `KickOutBuff()` | Main loop already routes tick sweep and pending activation through facade commands; old `LOADING_BUFF_DICT` and `DYNAMIC_BUFF_DICT` remain source-of-truth containers behind the facade. | Adapter-internal until old containers are removed; future stories can add guardrails or focused facade tests, not XLogic direct writes. | Do not expose new raw queue/container passthroughs; do not treat retained `buff_add()` / `KickOutBuff()` definitions as BuffXLogic backlog. |
| Direct simulator service context | `YuzuhaHardCandyShotTrigger.py`、`YuzuhaCinema4QuickAssistTrigger.py`、`YuzuhaCinema6SheelTrigger.py`、report-only `change_process_state()` files、RNG trigger files | XLogic reads `tick`, `preload.preload_data`, `char_data.find_next_char_obj(...)`, `schedule_data.enemy`, `listener_manager`, or `rng_instance` for local gates and side effects. | Explicit context object, listener gateway, RNG/context helper, or retained compatibility helper depending on service; not `LegacyBuffRuntimeFacade` by default. | Classify by concrete service. Do not collapse local preload, listener broadcast, RNG, report state, scheduled publish, and runtime write into one boundary. |
| Enemy mirror / debuff runtime state | `LegacyBuffRuntimeFacade.sync_enemy_debuff_mirror(...)`、`remove_enemy_debuff_mirror(...)`、debuff XLogic such as `AnomalyDebuffExitJudge.py` | Enemy debuff mirror remains a runtime active-store mirror; `find_enemy(...)` / `schedule_data.enemy` reads in XLogic are usually runtime read or bypass classification, not planned-event publish. | Adapter-internal enemy mirror for writes; `BuffRuntimeReadPort.get_active_buffs("enemy")` for future reads where possible. | Leave enemy debuff single-source-of-truth cleanup out of this PRD; US-007 classifies anomaly/debuff/dot bypasses separately. |
| Retained compatibility / false-positive buckets | uppercase `DYNAMIC_BUFF_DICT` / `LOADING_BUFF_DICT` hits in BuffXLogic = 0; direct `buff_add()` / `KickOutBuff()` in BuffXLogic = 0; runtime boundary names in BuffXLogic = 0 | Current leaf XLogic does not directly call lifecycle helpers or the new runtime boundaries by name. | Keep legacy lifecycle helpers and old containers documented as retained compatibility; future implementation PRDs should start from concrete source evidence, not name-only backlog. | Do not delete old containers, legacy `buff_add()`, legacy `KickOutBuff()`, retained `MultiplierData`, or retained `ScheduleBuffSettle.py` semantics in phase-2 classification. |

### Follow-up runtime / service-location PRD groups

| candidate group | candidate files / symbols | Ralph-sized work direction | retained boundaries | validation entrypoints | non-goals |
| --- | --- | --- | --- | --- | --- |
| Trigger-state read-port candidates | `AstralVoice.py`、`FlamemakerShakerApBonus.py`、`CordisGerminaSNAAndQIgnoreDefense.py`、21 files with `trigger_buff_0=` | Design read-only helper / runtime-view access for old trigger Buff state, starting with pure gates before read-then-writeback files. | Old `exist_buff_dict` identity and `BuffRuntimeReadPort` read-only contract. | `implicit-events` plus focused no-write gate tests. | No write API on `BuffRuntimeReadPort`; no old container deletion. |
| Dynamic snapshot + attribute reader buckets | `AliceAdditionalAbilityApBonus.py`、`YuzuhaAdditionalAbilityAnomaly*.py`、`Jane*.py`、`IceJadeTeaPotExtraDMGBonus.py` | Pair `BuffRuntimeReadPort` snapshot shape with `BuffAttributeReader` parity for formula-read paths, then keep count/state sync in the same tested story only when writeback is adjacent. | `MultiplierData` formula snapshots, old active Buff container identity, state-sync ordering. | `calculator-reads`; add focused state-sync pytest for writeback variants. | Do not migrate event producers or lifecycle facade in the same PRD. |
| Direct simulator context extraction | `YuzuhaHardCandyShotTrigger.py`、`YuzuhaCinema4QuickAssistTrigger.py`、`YuzuhaCinema6SheelTrigger.py`、RNG trigger files | Classify and wrap direct `tick` / preload / char-data / RNG services with explicit context only after branch tests cover no-op vs action branches. | Local preload semantics, Character resource/actions, listener/report/RNG separation. | `implicit-events` plus file-specific focused tests. | Not a `LegacyBuffRuntimeFacade` replacement and not scheduled-publish backlog unless source publishes payloads. |
| Facade-internal lifecycle guardrails | `LegacyBuffRuntimeFacade`、`RuntimeCommandPort`、`Update_Buff.update_time_related_effect(...)`、legacy `buff_add()` / `KickOutBuff()` | Add or refine guardrails / tests only if future code attempts new raw container access; current XLogic census has no direct calls. | Old containers remain source of truth behind facade; one `RuntimeCommandPort` write boundary. | `implicit-events`; default validation only if lifecycle wiring changes. | Do not create a second write facade or promote legacy getters to general write APIs. |

### US-006 结论

- Runtime / service-location 分类必须先区分 static lookup、runtime read snapshot、runtime immediate write、template / registry identity、pending queue、active store、enemy mirror sync 和 direct simulator service context；这些不是一个可一次性替换的耦合面。
- `BuffXLogic` 当前没有直接引用 `RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort`、`LegacyBuffRuntimeFacade`、`buff_add()` 或 `KickOutBuff()`；后续 PRD 不应从这些名字制造 XLogic backlog。
- 可优先形成 future read-port stories 的是 trigger-state reads、dynamic snapshot / attribute-reader paths 和部分 direct context reads；必须留在 adapter-internal 的是 pending queue、active store lifecycle, enemy mirror write sync, retained `buff_add()` / `KickOutBuff()` and `ScheduleBuffSettle` command-adapter internals.
- No live runtime path or XLogic behavior was replaced in this story. Existing `RuntimeCommandPort` remains the sole same-tick write boundary, `BuffRuntimeReadPort` remains read-only, and `LegacyBuffRuntimeFacade` continues to retain old container identity by reference.

## US-007 anomaly / debuff / dot / formula bypass 分类

本节只补阶段 2 分类证据，不改动 `BuffXLogic`、`UpdateAnomaly`、Dot、Calculator、runtime port、guardrail 或验证脚本。分类仍是非排他的：同一个 XLogic 可以同时命中 anomaly gate、scheduled publish、record/state-sync、formula snapshot 或 runtime service-location。

### Root-workspace scan evidence

以下命令均在根工作区执行，路径限定在 `zsim/sim_progress/Buff/BuffXLogic`，不读取 `.codex_worktrees/` 历史副本：

```powershell
rg --files zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "anomaly|Anomaly|异常|紊乱|disorder|Disorder|polarity|Polarity|极性紊乱" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "enemy\.dynamic\.(is_under_anomaly|get_active_anomaly|get_active_anomaly_bar|assault|burn|shock|frozen|frostbite|frost_frostbite|corruption|stun|dynamic_debuff_list|dynamic_dot_list)" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "dot|Dot|find_dot|spawn_normal_dot|dynamic_dot_list|dynamic_dot" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "debuff|Debuff|dynamic_debuff_list" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "buff_add_strategy|BuffAddStrategy" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "Cal\.AnomalyMul|Calculator\.AnomalyMul|AnomalyMul|cal_am\(|cal_ap\(|current_ndarray|anomaly_dmg_ratio|MulData|MultiplierData" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
rg -l "publish_scheduled|create_schedule_dispatch_port|ScheduleDispatchPort|spawn_output|LoadingMission|schedule_priority|preload_tick" zsim/sim_progress/Buff/BuffXLogic --glob '*.py' --glob '!__init__.py'
```

| scan bucket | files | matching lines | classification use |
| --- | ---: | ---: | --- |
| full root-workspace XLogic census | 149 | - | Baseline file count; `__init__.py` excluded. |
| anomaly / disorder / polarity terms | 30 | 216 | Anomaly gates, disorder records, polarity disorder output, anomaly formula / AP / AM terms. |
| `enemy.dynamic.*` state reads | 23 | 42 | Runtime enemy-state gates: anomaly flags, stun/freeze flags, active anomaly lookup, dot/debuff lists. |
| dot terms | 2 | 18 | `VivianDotTrigger` runtime dot registration and `VivianCinema1Debuff` dot presence gate. |
| debuff terms | 6 | 15 | Anomaly debuff exit / enemy debuff mirror read candidates. |
| `buff_add_strategy` | 6 | 18 | Same-tick forced Buff / Debuff write callsites. |
| anomaly formula / snapshot terms | 18 | 45 | AP / AM / anomaly ratio reads and copied-anomaly formula candidates. |
| scheduled-publish terms | 43 | 108 | Already-migrated event publishers and ordering-sensitive trigger samples; not all are anomaly/dot bypasses. |

### CodeGraph boundary evidence

- Query terms used: `US-007 Classify Anomaly Debuff Dot Formula Bypass Couplings`, `BuffAddStrategy`, `UpdateAnomaly`, `AnomalyBar`, `Shock.DotFeature`, `DotFeature`, `CalAnomaly`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `implicit-events`, `calculator-reads`.
- `BuffAddStrategy.buff_add_strategy(...)` now creates `LegacyBuffRuntimeFacade` on demand and `let_buff_start(...)` uses the facade for active-store replacement and `sync_enemy_debuff_mirror(...)`; template lookup through `exist_buff_dict` remains retained compatibility.
- `UpdateAnomaly.update_anomaly(...)` creates `ScheduleDispatchPort` per call and publishes `new_anomaly`, `disorder`, and freeze follow-up payloads through `_publish_scheduled_event(...)`; `spawn_output(...)` keeps listener broadcast separate from scheduled publish.
- `anomaly_effect_active(...)` still routes accompanying debuff through `buff_add_strategy(...)` and accompanying dot through `spawn_anomaly_dot(...)` plus direct `enemy.dynamic.dynamic_dot_list` replacement / append.
- `remove_dots_cause_disorder(...)` still iterates and removes `enemy.dynamic.dynamic_dot_list`; only the freeze follow-up anomaly data is scheduled through the dispatch port.
- `RuntimeCommandPort.update_anomaly(...)` delegates to legacy `update_anomaly(...)` through `LegacyRuntimeCommandAdapter`, carrying `ScheduleData.event_list`, `char_obj_list`, `dynamic_buff`, `buff_runtime_view`, and `sim_instance` inside the one same-tick command boundary.
- `AnomalyBar.change_info_cause_active(...)` passes `buff_runtime_view` into `__get_max_duration(...)`; `__get_duration_enemy_buffs(...)` prefers `buff_runtime_view.get_active_buffs("enemy")` and falls back to legacy `dynamic_buff_dict["enemy"]`.
- `Shock.DotFeature.__post_init__()` still reads `sim_instance.init_data.name_box` and `sim_instance.load_data.exist_buff_dict["丽娜"]` to decide Shock duration. This is a dot initialization read candidate, not a phase-1 blocker.
- `CalAnomaly.__init__()` consumes settled `AnomalyBar.current_ndarray`, constructs `MulData(...)`, and calls Calculator multiplier helpers. It remains a formula snapshot classification target, not an implementation target in this PRD.
- CodeGraph again surfaced `.codex_worktrees/` duplicates; they are historical navigation evidence only and are excluded from the root-workspace counts above.

### Bypass buckets

| bucket | representative files / symbols | 当前行为证据 | retained boundary / future candidate | validation need / non-goal |
| --- | --- | --- | --- | --- |
| Enemy anomaly-state gates | `ElectroLipGlossAtkAndDmgBonus.py`, `JaneAdditionalAbilityPhyBuildupBonus.py`, `MarcatoDesireAtkBonus.py`, `TimeweaverApBonus.py`, `WeepingGeminiApBonus.py`, `HailstormShrineIceBonus.py`, `MiyabiAdditionalAbility_IgnoreIceRes.py` | Reads `enemy.dynamic.is_under_anomaly()`, per-element flags, or edge-detected anomaly maps to allow / deny Buff behavior. | Future read-only enemy-state helper or `BuffRuntimeReadPort`-adjacent view where source proves active Buff reads; keep direct enemy state distinct from Buff container reads. | `implicit-events`; add focused no-op / publish / count branch tests before extraction. Do not treat gates as scheduled publishers. |
| Disorder / polarity disorder outputs | `YanagiPolarityDisorderTrigger.py`, `AlicePolarizedAssaultTrigger.py`, `VivianCorePassiveTrigger.py`, `VivianCinema6Trigger.py` | Copies active `AnomalyBar`, may settle snapshot, constructs `PolarityDisorder` / copied anomaly output, then publishes through `_create_dispatch_port().publish_scheduled(...)`. | Existing `ScheduleDispatchPort` for scheduled payloads; formula / AP reads remain Calculator snapshot candidates. | `implicit-events` plus file-specific dispatch tests such as `test_yanagi_polarity_disorder_dispatch.py`, `test_alice_polarized_assault_trigger_dispatch.py`, `test_vivian_core_passive_trigger_dispatch.py`, `test_vivian_cinema6_trigger_dispatch.py`. Do not reopen raw queue discovery surfaces. |
| Freeze / frost / anomaly-debuff state | `AnomalyDebuffExitJudge.py`, `BranchBladeSongCritRateBonus.py`, `PolarMetalFreezeBonus.py`, `MiyabiCoreSkill_FrostBurn.py`, `MiyabiCoreSkill_IceFire.py`, `LinaAdditionalSkillEleDMGBonus.py` | Reads `enemy.dynamic.frozen`, `frostbite`, `frost_frostbite`, `shock`, or `dynamic_debuff_list`; some files edge-detect state changes before exiting / activating Buffs. | Runtime enemy-state read helper candidate; enemy debuff mirror writes stay adapter-internal through `LegacyBuffRuntimeFacade`. | `implicit-events`; focused edge-detection tests before replacement. Do not attempt enemy debuff single-source-of-truth cleanup in this PRD. |
| Dot runtime registration / dot presence | `VivianDotTrigger.py`, `VivianCinema1Debuff.py`, `UpdateAnomaly.anomaly_effect_active(...)`, `remove_dots_cause_disorder(...)`, `Shock.DotFeature.__post_init__()` | `VivianDotTrigger` starts a dot, appends it to `enemy.dynamic.dynamic_dot_list`, then publishes dot `skill_node_data`; `UpdateAnomaly` replaces / appends anomaly dots and removes dots during disorder; `Shock.DotFeature` reads Rina passive from old template data to adjust duration. | Dot runtime-state / initialization adapter candidate; scheduled publish remains separate and already uses `ScheduleDispatchPort` where applicable. | `implicit-events`; dot behavior changes need focused dot tests and, for duration / tick behavior, main-loop consistency samples. Dot runtime registration is not planned-event backlog. |
| Forced Buff / Debuff same-tick writes | `HugoCorePassiveTotalizeTrigger.py`, `RoaringRideBuffTrigger.py`, `SeedBesiegeBonusTrigger.py`, `SeedCinema2BesiegeIgnoreDefenceTrigger.py`, `SeedCinema4Trigger.py`, `SeedDirectStrikeTrigger.py`, `UpdateAnomaly.anomaly_effect_active(...)` | Calls `buff_add_strategy(...)`; current implementation builds `LegacyBuffRuntimeFacade`, replaces existing active Buff via facade, appends active Buff, and syncs enemy mirror through facade for `enemy`. | Existing `LegacyBuffRuntimeFacade` / runtime write boundary; registry / template identity retained in `exist_buff_dict`. | `implicit-events` and raw-container guardrail; default lifecycle profile only if lifecycle wiring changes. Do not add a second write facade or convert same-tick writes into scheduled publish. |
| Formula / anomaly snapshot reads | `CalAnomaly.py`, `Calculator.py`, `AliceAdditionalAbilityApBonus.py`, `JaneCinema1APTransToDmgBonus.py`, `JaneCoreSkillStrikeCritRateBonus.py`, `JanePassionStateAPTransToATK.py`, `VivianCorePassiveTrigger.py`, `VivianCinema6Trigger.py`, `YuzuhaAdditionalAbilityAnomaly*.py` | `CalAnomaly` reads settled `current_ndarray` and `MulData`; XLogic reads AP / AM or anomaly ratio before count/state sync or copied anomaly publish. | Retained `FORMULA_SNAPSHOT` plus future `BuffAttributeReader` helper-family expansion. | `calculator-reads` for formula/read helper changes; add `implicit-events` when the same story changes scheduled publish or anomaly output. Do not rewrite Calculator / CalAnomaly formula internals in this classification PRD. |

### Follow-up anomaly / dot PRD groups

| candidate group | candidate files / symbols | Ralph-sized direction | retained boundaries | validation entrypoints | non-goals |
| --- | --- | --- | --- | --- | --- |
| Enemy anomaly-state read helpers | `ElectroLipGlossAtkAndDmgBonus.py`, `JaneAdditionalAbilityPhyBuildupBonus.py`, `MiyabiAdditionalAbility_IgnoreIceRes.py`, `HailstormShrineIceBonus.py`, `WeepingGeminiApBonus.py` | Start from read-only gates and edge detection; design a small enemy-state read context only after focused tests prove current tick / previous tick behavior. | Existing enemy dynamic flags and record fields. | `implicit-events` plus file-specific gate tests. | No scheduled publish migration, no enemy debuff SSoT cleanup. |
| Dot runtime-state / initialization reads | `VivianDotTrigger.py`, `VivianCinema1Debuff.py`, `Shock.DotFeature.__post_init__()` | Separate dot presence, dot registration, dot duration initialization, and scheduled dot follow-up publish. | `enemy.dynamic.dynamic_dot_list` remains runtime dot state; `ScheduleDispatchPort` remains scheduled payload boundary. | `implicit-events`; dot duration changes need main-loop consistency sample. | Dot runtime registration is not raw queue backlog. |
| BuffAddStrategy caller classification | `HugoCorePassiveTotalizeTrigger.py`, `RoaringRideBuffTrigger.py`, `Seed*Trigger.py`, `UpdateAnomaly.anomaly_effect_active(...)` | Keep caller taxonomy and, if later replacing, test active-store replacement, enemy mirror sync, selected-target fan-out, and no pending queue writes. | `LegacyBuffRuntimeFacade` active / mirror writes, old template registry identity, one same-tick write boundary. | `implicit-events`, `test_buff_add_strategy_runtime_facade.py`, `test_buff_raw_container_guardrail.py`; lifecycle profile only for lifecycle changes. | No new write facade, no deletion of legacy `buff_add()` / `KickOutBuff()`. |
| Anomaly formula / copied-output reads | `CalAnomaly.py`, `VivianCorePassiveTrigger.py`, `VivianCinema6Trigger.py`, `YanagiPolarityDisorderTrigger.py`, AM / AP XLogic files | Group by helper family and output semantics: AP / AM parity, copied anomaly ratio, polarity disorder ratio, then state-sync order where needed. | `MultiplierData`, `CalAnomaly`, scheduled publish ordering, old active Buff snapshots. | `calculator-reads`; add `implicit-events` when output payload publish changes. | No full formula rewrite and no phase-3 XLogic replacement in this PRD. |

### US-007 结论

- Anomaly / debuff / dot bypass work must continue to classify by runtime layer first: scheduled queue publish, listener broadcast, dot runtime registration / removal, runtime immediate write, formula snapshot, and enemy-state read are separate axes.
- `UpdateAnomaly` scheduled publish is already on `ScheduleDispatchPort`; `spawn_output()` listener broadcast, `anomaly_effect_active()` debuff write, dot runtime registration, `RuntimeCommandPort` same-tick command writes, `AnomalyBar` runtime-view read sample, and `BuffAddStrategy` facade-backed writes remain distinct retained boundaries.
- `Shock.DotFeature` and `CalAnomaly` are valid phase-2 classification targets, but neither is a phase-1 blocker or a live replacement target for this story.
- Dot runtime registration must not be reclassified as planned-event backlog, and enemy debuff single-source-of-truth cleanup remains out of scope.
- No production behavior, validation wiring, Calculator formula, runtime port, facade, listener, or Dot implementation changed in this story.

## US-008 复用模式目录与风险矩阵

本节只把 US-001 到 US-007 的分类结果收敛为复用设计目录、风险矩阵和下一轮 PRD 候选池；不替换 `BuffXLogic`、不扩展 `BuffAttributeReader`、不修改 runtime port / facade / dispatch adapter，也不把分类项直接升级成阶段 3 替换。

### CodeGraph cross-check evidence

- Query seed：`US-008 Produce The Reuse Pattern Catalog And Risk Matrix`、`BuffXLogic`、`Calculator`、`CalAnomaly`、`BuffAttributeReader`、`ScheduleDispatchPort`、`create_schedule_dispatch_port`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort`、`LegacyBuffRuntimeFacade`、`BuffAddStrategy`、`Shock.DotFeature`、`implicit-events`、`calculator-reads`。
- `codegraph_impact("ScheduleDispatchPort", depth=2)` 命中 root `zsim/sim_progress/data_struct/schedule_dispatch.py`、已迁移 `BuffXLogic` planned-event producers、`DecibelManager`、`BreakingLegManager`、`QuickAssistSystem` 和 focused dispatch tests；该 pattern 是高 ordering 风险的 event adapter，不是新的 raw queue backlog。
- `codegraph_callers("create_schedule_dispatch_port")` 命中 root tests、14 个 `BuffXLogic._create_dispatch_port(...)` 样本、`UpdateAnomaly.update_anomaly(...)`、`AliceDotTriggerListener`、`SchedulePreload`、`PolarizedAssaultEventClass`、`QuickAssistSystem`、`DecibelManager` 与 `BreakingLegManager`；后续 PRD 必须按 payload / target / relative order 分组，而不是只挑一个文件。
- `codegraph_node("create_schedule_dispatch_port")` 证明当前工厂按需从 `sim_instance` 或 `schedule_data` 取当前 `schedule_data.event_list` 并创建 adapter；这支持“不缓存长生命周期 adapter”的 retained boundary。
- `codegraph_impact("RuntimeCommandPort", depth=2)` 命中 root `runtime_command.py`、runtime command focused tests、`test_bypass_layer_semantics.py` 和 `.codex_worktrees/` 历史副本；同 tick 写风险集中在 `update_anomaly(...)` / `settle_buffs(...)` 命令边界，不能新增第二套 write facade。
- `codegraph_node("create_runtime_command_port")` 证明 root 工厂返回 `LegacyRuntimeCommandAdapter(...)`，并携带 `ScheduleData`、`exist_buff_dict`、`action_stack`、`sim_instance` 和可选 `buff_runtime_view`；后续 same-tick 写 stories 应继续复用该入口。
- `codegraph_node("check_record_module")` 证明共享 record 初始化仍通过 `JudgeTools.find_exist_buff_dict(...)` 找到 old `buff_0`，按需创建 `RECORD_CLASS()` 并绑定 `history.record`；record helper 设计必须保留 old template identity 和懒初始化时机。
- `codegraph_callers("read_anomaly_mastery")` 只命中 focused reader tests，未完整覆盖 reader-backed XLogic reachability；reader 结论仍必须回到 US-003 root source 分类和 `calculator-reads` 测试。
- `codegraph_callers("buff_add_strategy")` 同时命中 `.codex_worktrees/` 历史 production duplicates 与 root focused tests；root production caller taxonomy 以 US-007 source 分类为准，CodeGraph 在这里仅作导航提醒。
- CodeGraph 仍会聚合 `.codex_worktrees/` 历史副本。本文所有 blocker / backlog / priority 结论只采信根工作区源码、focused tests 和 validation profiles。

### Reuse pattern catalog

| pattern family | reusable target | current representative files / symbols | design direction | retained boundaries | validation entrypoint |
| --- | --- | --- | --- | --- | --- |
| Method helper / stat reader | `BuffAttributeReader` helper family | Existing AM / AP reader samples, `CalculatorBuffAttributeReader`, `Calculator.AnomalyMul.cal_am(...)`, `cal_ap(...)`, future impact / crit helpers | 按 helper family 扩展 parity reader，而不是按单文件改写；区分 read-only gate 与 read-then-writeback。 | `MultiplierData` / `MulData` / `CalAnomaly` formula snapshots retained until parity and state-sync tests exist. | `calculator-reads`; event-adjacent files add `implicit-events`. |
| Record object catalog | `RECORD_CLASS` + `history.record` lazy init | `BasicComplexBuffClass.check_record_module(...)`, `get_prepared(...)`, 138 个 record class census entries | 建立 record 初始化 / ledger / cooldown / trigger-state pattern 表，先做读取和状态分类，后做实现替换。 | Old `buff_0` template identity, `JudgeTools.find_exist_buff_dict(...)`, lazy `history.record` creation. | `implicit-events` plus focused record/state pytest. |
| State-sync helper | formula result -> Buff dynamic count / template sync | `AliceAdditionalAbilityApBonus.py`, `Jane*.py`, `YuzuhaAdditionalAbilityAnomaly*.py`, `TriggerAdditionalAbilityStunBonus.py`, `Soldier0AnbyCoreSkillCritDMGBonus.py` | 复用 `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` 形态，按 AM/AP、impact、crit family 分组。 | `simple_start(...)` ordering, old `dy.count`, old template update semantics, record fields. | `calculator-reads` plus new focused state-sync pytest. |
| Event adapter | scheduled queue publish | `ScheduleDispatchPort`, `create_schedule_dispatch_port(...)`, migrated `CannonRotor`, `MiyabiCoreSkill_IceFire`, `Vivian*`, `Yanagi*`, resource-refresh XLogic | 继续把 scheduled publish 作为 queue-only adapter；按 payload / target / priority / order 设计 stories。 | Adapter-only access to raw queue; no `JudgeTools.find_event_list()` reopen; no long-lived adapter cache. | `implicit-events` and file-specific dispatch tests. |
| Runtime command / facade | same-tick write boundary | `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, `BuffAddStrategy` facade-backed writes | same-tick writes stay behind existing command / facade; future work first adds caller tests and guardrails. | One write facade only; old containers retained behind adapter / facade; `BuffRuntimeReadPort` remains read-only. | `implicit-events`; default lifecycle profile only when lifecycle wiring changes. |
| Handler pattern | runtime-view handler access | `SkillEventHandler`, `AnomalyEventHandler`, `EventContext.buff_runtime_view`, focused handler tests | Handler stories must prove runtime view vs command write separation and avoid raw getter regression. | Handler requeue, `SPUpdateData` panel refresh reads, legacy getters only in documented compatibility paths. | `implicit-events`, handler runtime-view tests. |
| Listener pattern | synchronous broadcast layer | `UpdateAnomaly.spawn_output(...)`, BattleEventListener `buff_add_strategy(...)` callers, listener focused tests | Keep listener broadcast synchronous and separate from scheduled queue publish and runtime writes. | Listener manager semantics; no conversion to planned-event publish without source order proof. | `implicit-events`, `test_bypass_layer_semantics.py`, listener-focused tests. |
| Dot / bypass runtime-state adapter | dot presence / registration / initialization | `VivianDotTrigger.py`, `VivianCinema1Debuff.py`, `Shock.DotFeature.__post_init__()`, `UpdateAnomaly.anomaly_effect_active(...)` | 先分类 dot presence, dot registration, dot duration initialization and scheduled dot follow-up separately. | `enemy.dynamic.dynamic_dot_list` remains runtime dot state; `ScheduleDispatchPort` only covers scheduled payloads. | `implicit-events`; dot duration changes need main-loop consistency samples. |
| Explicit context helper | direct simulator services | `YuzuhaHardCandyShotTrigger.py`, `YuzuhaCinema4QuickAssistTrigger.py`, `YuzuhaCinema6SheelTrigger.py`, RNG / listener / preload users | 只在 focused tests 覆盖 action/no-op branch 后提取 tick / preload / char-data / RNG / listener context。 | Direct service classes stay separate; not a facade replacement and not scheduled-publish backlog by default. | `implicit-events` plus file-specific tests. |

### Risk matrix

| bucket | behavior risk | ordering risk | validation coverage | runtime-boundary risk | rollback complexity | likely follow-up PRD size |
| --- | --- | --- | --- | --- | --- | --- |
| AM/AP reader + computed count state-sync | High: formula parity and count ceilings can drift. | High: `simple_start(...)`, `dy.count`, `update_to_buff_0(...)` order matters. | `calculator-reads` exists; needs focused state-sync tests. | Medium: old dynamic Buff snapshot and template identity retained. | Medium: helper can be feature-limited per family. | Medium-large; should include multiple Jane / Yuzuha / Alice files, not one file. |
| Impact / full-crit / personal-crit reader expansion | Medium-high: helper semantics differ, especially full vs personal crit rate. | Medium: some files are read-then-writeback or event-adjacent. | P2-B now has focused count/event tests, source guardrail, `calculator-reads`, `implicit-events`, and one consistency sample for the nine migrated files. | Medium: Calculator snapshots retained. | Medium. | Completed for the P2-B migrated file set; future work is guardrail maintenance or new-file blocker only. |
| Scheduled publish event adapter order | High: payload target, priority, `mission_start(...)` ordering and reset-after-publish behavior are source-specific. | High. | P2-D now has adapter rebinding, resource refresh, `SkillNode` / `LoadingMission`, stateful anomaly / dot, fan-out / multi-publish focused tests plus exact-file source guardrail in `implicit-events`. | Low-medium: `ScheduleDispatchPort` is established, raw queue reopen and stale adapter caching are guarded. | Low-medium: publisher changes are file-local but order regressions are costly. | Completed for P2-D migrated producer set; future work is guardrail maintenance or new-file blocker only. |
| Trigger-state read-port / old template reads | Medium: read-only gates can silently alter activation. | Low-medium unless paired with writeback. | `implicit-events`; needs no-write gate tests. | Medium: `BuffRuntimeReadPort` must stay read-only. | Low-medium. | Medium; start with pure gates before read-then-writeback. |
| BuffAddStrategy / facade-backed forced writes | High: active-store replacement, selected target, enemy mirror sync and same-tick writes are live behavior. | Medium-high: write timing must not become scheduled publish or listener broadcast. | `implicit-events`, raw-container guardrail and facade tests exist; lifecycle profile only for lifecycle changes. | High: one write facade rule and old container identity are critical. | High. | Later medium-large phase-2 design/test package before replacement. |
| Dot runtime registration / dot init reads | High: duration, tick behavior and dot replacement are gameplay-visible. | High: dot registration/removal is not scheduled queue publish. | `implicit-events`; main-loop consistency needed for duration/tick changes. | Medium: direct enemy dynamic state retained. | High. | Current default P2-E; keep runtime-state and scheduled follow-up stories separate. |
| Direct simulator context extraction | Medium: action/no-op branch and report state can drift. | Medium: preload / char-data / RNG side effects are service-specific. | P2-G focused tests and exact-file / selected-symbol guardrail now cover selected representatives in `implicit-events`; future work is guardrail maintenance or blocker-only. | Medium: not all services belong to facade / runtime read port. | Medium. | Completed for selected P2-G service-family representatives; no default helper-extraction backlog remains. |
| Formula snapshots / `CalAnomaly` internals | High if changed, because formulas define damage. | Low-medium for classification; high for implementation. | `calculator-reads` only covers reader seams, not full formula rewrite. | Low for classification; high if old snapshots are removed. | High. | Phase-3 or retained compatibility until formula parity suite exists. |

### Ranked follow-up pool

| rank | bucket | candidate files / symbols | known coupling | Ralph-sized story direction | retained boundaries | validation entrypoints | non-goals |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Completed phase-2 bucket | AM/AP reader + computed count state-sync family | `AliceAdditionalAbilityApBonus.py`, `YuzuhaAdditionalAbilityAnomalyBuildupBonus.py`, `YuzuhaAdditionalAbilityAnomalyDmgBonus.py`, `JaneCinema1APTransToDmgBonus.py`, `JaneCoreSkillStrikeCritRateBonus.py`, `JanePassionStateAPTransToATK.py`, existing AM/AP reader samples | Direct `MultiplierData` / alias reads have been replaced in the six root files; `dynamic_buff_list` remains only as reader context input; computed count writeback order is guarded. | Maintain source guardrail and parity/order tests; open blocker only if validation proves a regression. | `MultiplierData` snapshots, old `buff_0` identity, record fields, state-sync order. | Focused reader/state-sync/guardrail tests plus `calculator-reads` and `implicit-events` profiles are passing. | Do not reopen P2-A as default backlog unless a concrete guardrail or validation failure names a migrated file. |
| Completed phase-2 bucket | Crit / impact reader family package | `LighterAdditionalAbility_IceFireBonus.py`, `QingYiAdditionalAbilityStunConvertToATK.py`, `CannonRotor.py`, `MiyabiCoreSkill_IceFire.py`, `WoodpeckerElectroSet4_NA.py`, `WoodpeckerElectroSet4_E_EX.py`, `WoodpeckerElectroSet4_CA.py`, `TriggerAdditionalAbilityStunBonus.py`, `Soldier0AnbyCoreSkillCritDMGBonus.py` | Impact / full crit / personal crit direct `MultiplierData` and Calculator reads have been replaced in the nine root files; event-adjacent branches keep dispatch ordering tests. | Maintain P2-B source guardrail, reader parity, state-sync, full-crit event-adjacent and dispatch tests; open blocker only if validation proves a migrated-file regression. | Full crit includes received crit; personal crit helpers exclude received crit; retained Calculator / CalAnomaly formula snapshots, old `buff_0` identity, `ScheduleDispatchPort` ordering. | Focused P2-B pytest, `calculator-reads`, `implicit-events`, file-specific dispatch tests, and one `莱特火属性队` consistency sample are passing. | Do not reopen P2-B as default backlog or expand its guardrail to block P2-C/P2-D/P2-E/P2-F candidates. |
| Completed phase-2 bucket | Trigger-state read-only gate package | `AstralVoice.py`, `FlamemakerShakerApBonus.py`, `CordisGerminaSNAAndQIgnoreDefense.py`, `SpectralGazeImpactBonus.py`, `SharpenedStingerAnomalyBuildupBonus.py` | Direct old-template `record.trigger_buff_0.dy.active` / `.count` / `.built_in_buff_box` reads have been replaced in the five root migrated files; `AstralVoice` count mirror preserves old writeback order. | Maintain P2-C source guardrail, no-write gate tests, count-mirror order tests and behavior-sample evidence; open blocker only if validation proves a migrated-file regression. | `BuffRuntimeReadPort` remains read-only; old template identity, `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, `JudgeTools.find_exist_buff_dict(...)` retained. | `test_trigger_state_read_only_gates.py`, `test_migrated_p2c_trigger_state_guardrail.py`, `implicit-events`, and one `席德大安比队` consistency sample are passing. | Do not broaden P2-C guardrail to remaining `trigger_buff_0=` pool; no write API on `BuffRuntimeReadPort`, no old container deletion. |
| Completed phase-2 bucket | Scheduled publish ordering and adapter parity package | `CannonRotor.py`, `HugoCorePassiveTotalizeTrigger.py`, `YixuanCinema1Trigger.py`, `VivianDotTrigger.py`, `YanagiPolarityDisorderTrigger.py`, `ElegantVanitySpRecover.py`, `SliceofTimeExtraResources.py`, `UpdateAnomaly.update_anomaly(...)`, `DecibelManager`, `BreakingLegManager`, `Character/Yuzuha` cinema-6 energy | P2-D migrated `ScheduleDispatchPort` producers now have focused coverage for payload / target / priority / order, adapter event-list rebinding, no-publish branches and exact-file guardrail coverage. | Maintain source guardrail and file-specific dispatch tests; open blocker only if validation proves a migrated-file regression. | `ScheduleDispatchPort` queue-only boundary; listener broadcast, dot runtime registration and runtime writes stay separate; create adapters on demand from current `sim_instance` / `schedule_data`. | `implicit-events`, file-specific dispatch tests, and `test_migrated_p2d_scheduled_publish_guardrail.py` are passing. | No raw queue reopen, no dot runtime registration rewrite, no same-tick runtime write facade, no guardrail expansion into P2-E/P2-F/P2-G. |
| Completed phase-2 bucket | Dot runtime-state and initialization package | `VivianDotTrigger.py`, `VivianCinema1Debuff.py`, `Shock.DotFeature.__post_init__()`, `UpdateAnomaly.anomaly_effect_active(...)`, `remove_dots_cause_disorder(...)`, `DotRuntimeStateAdapter`, `DotInitializationReadContext` | Dot presence, registration, duration initialization, replacement, removal and scheduled follow-up are separate runtime layers; migrated root files now route runtime-list work through explicit helpers or guarded caller-owned follow-up payloads. | Maintain helper parity, focused dot tests and exact-file guardrail; open blocker only if validation proves a migrated-file regression. | `enemy.dynamic.dynamic_dot_list` remains runtime state; `ScheduleDispatchPort` only owns scheduled payloads; Buff / Debuff writes remain on `buff_add_strategy(...)` / facade paths. | `implicit-events`, `test_dot_runtime_state_adapter.py`, `test_dot_runtime_initialization.py`, Vivian / UpdateAnomaly focused tests, and `test_migrated_p2e_dot_runtime_guardrail.py` are passing. | Do not reopen P2-E as default backlog, convert dot runtime registration to planned-event backlog, add a second write facade, or rewrite Shock / CalAnomaly formulas. |
| Completed phase-2 bucket | BuffAddStrategy caller and facade-write design package | `zsim/sim_progress/Buff/BuffAddStrategy.py`, `HugoCorePassiveTotalizeTrigger.py`, `RoaringRideBuffTrigger.py`, `Seed*Trigger.py`, `UpdateAnomaly.anomaly_effect_active(...)`, BattleEventListener callers, Character manager callers | Forced same-tick Buff / Debuff writes still route through `buff_add_strategy(...)` and `LegacyBuffRuntimeFacade`; caller taxonomy, active replacement, enemy mirror sync, selected target fan-out, template identity, no pending queue write, cross-layer semantics and exact-file guardrail are covered. | Maintain P2-F caller tests, facade tests, boundary semantics and exact-file guardrail; open blocker only if validation proves a migrated-boundary regression. | Existing `LegacyBuffRuntimeFacade`, old registry/template identity, one same-tick facade write boundary; scheduled publish, listener broadcast, `RuntimeCommandPort` and `BuffRuntimeReadPort` remain separate. | P2-F focused caller pytest, `test_buff_add_strategy_runtime_facade.py`, `test_bypass_layer_semantics.py`, `test_migrated_p2f_buff_add_strategy_guardrail.py`, raw-container guardrail, and `implicit-events` are passing. | No second write facade, no scheduled-publish conversion, no legacy `buff_add()` / `KickOutBuff()` deletion, no P2-G direct context helper replacement. |
| Completed phase-2 bucket | Direct simulator context extraction | `YuzuhaHardCandyShotTrigger.py`, `YuzuhaCinema4QuickAssistTrigger.py`, `YuzuhaCinema6SheelTrigger.py`, `YuzuhaCinema2Trigger.py`, `YuzuhaSugarBurstAnomalyBuildupBonus.py`, `YixuanAdditionalAbilityDmgBonus.py`, `HeartstringNocturne.py`, `CannonRotor.special_judge_logic()`, `WoodpeckerElectroSet4_*`, `AstraYaoCorePassiveAtkBonus.py`, report-only `change_process_state()` files | XLogic reads local tick, preload, char-data, enemy, listener, RNG or report-state services directly through `sim_instance`; the completed evidence keeps them service-specific instead of merging them into one Buff runtime facade target. | Maintain service-family focused tests and the P2-G source guardrail; open a blocker only if validation proves a migrated representative regressed. No universal simulator context helper is the current default. | Local preload, Character action/resource, listener/report/RNG and scheduled publish/runtime write boundaries stay separate. | P2-G focused tests, `tests/simulator/test_migrated_p2g_direct_context_guardrail.py`, `implicit-events`, and final `calculator-reads` handoff validation are passing. | Not raw queue backlog, not `LegacyBuffRuntimeFacade` replacement, no Calculator formula rewrite, no forced Buff write rewrite, no helper extraction without repeated service-specific evidence. |
| Phase-3 only | Formula snapshot replacement | `CalAnomaly.py`, `Calculator.py`, anomaly/disorder formula helper calls | Formula internals and settled anomaly snapshots define damage behavior. | Only after phase-2 reader/state/event adapters have parity suites, design formula-specific replacement PRD. | `MultiplierData`, `MulData`, `AnomalyBar.current_ndarray`, Calculator formulas retained. | Future formula parity suite plus `calculator-reads`; current PRD does not provide enough coverage. | No phase-2 formula rewrite. |
| Retained compatibility | Old containers and deleted discovery surfaces | `exist_buff_dict`, `LOADING_BUFF_DICT`, `DYNAMIC_BUFF_DICT`, legacy `buff_add()`, legacy `KickOutBuff()`, deleted `JudgeTools.find_event_list()` surfaces | Some are retained source-of-truth containers; some are deleted/guarded surfaces. | Keep as compatibility boundaries until explicit deletion PRD has source/test evidence. | `LegacyBuffRuntimeFacade`, `RuntimeCommandPort`, `ScheduleDispatchPort` adapter-only queue access. | Existing guardrails and `implicit-events`; default profile for lifecycle. | Do not manufacture phase-2 replacement backlog from retained container names. |
| Blocker-only phase-1 reopen | New raw queue / raw runtime write evidence | Any future root-workspace file with raw queue producer or new raw old-container write | Only reopen phase 1 if scan gives file, function, expression, event type, payload, target and relative order or raw write classification. | Open a narrow blocker PRD; do not merge into phase-2 replacement planning. | Existing phase-1 ports/adapters remain the expected route. | Failing guardrail / focused test / validation command must be recorded. | `.codex_worktrees/` hits alone are not blockers. |

### 2026-06-08 P2-A completion update

本节记录 AM/AP reader + computed count state-sync PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 US-003 / US-005 的历史扫描证据。

| file | previous P2-A coupling | current migration evidence | retained behavior / test evidence |
| --- | --- | --- | --- |
| `AliceAdditionalAbilityApBonus.py` | AM direct `MultiplierData(...)` + `Calculator.AnomalyMul.cal_am(...)` then count writeback. | Uses `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_anomaly_mastery(...)`. | AM threshold, count expression, old `buff_0` identity, and `simple_start(..., no_count=1) -> dy.count -> update_to_buff_0(...)` are covered by focused state-sync tests. |
| `YuzuhaAdditionalAbilityAnomalyBuildupBonus.py` | AM direct `MultiplierData(...)` + `cal_am(...)`, cinema ratio and threshold writeback. | Uses the same AM reader/context shape as Alice. | Below-threshold no-op, cinema 0 / cinema 1+ ratio, aggregation shape, and state-sync order are covered. |
| `YuzuhaAdditionalAbilityAnomalyDmgBonus.py` | AM direct `MultiplierData(...)` + `cal_am(...)`, report-gated count writeback. | Uses the same AM reader/context shape as Yuzuha buildup. | Below-threshold no-op, cinema ratios, `YUZUHA_REPORT` / `change_process_state()` ordering, and state-sync order are covered. |
| `JaneCinema1APTransToDmgBonus.py` | `MultiplierData as Mul` / `Mul(...)` + `Calculator.AnomalyMul.cal_ap(...)`, trigger-gated AP damage count. | Uses `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)`. | Inactive trigger, active AP count parity, cap behavior, `find_tick(...)`, old `buff_0` identity, and state-sync order are covered. |
| `JaneCoreSkillStrikeCritRateBonus.py` | AP alias read feeding crit-rate count writeback. | Uses the AP reader seam; remains AP-reader work, not full / personal crit-reader work. | Trigger gate, `min(40 + ap * 0.16, 100)`, cap behavior, and state-sync order are covered. |
| `JanePassionStateAPTransToATK.py` | AP alias read feeding passion-state ATK count writeback. | Uses the AP reader seam. | Inactive trigger, AP under 120, fractional AP above 120, higher AP parity, floor behavior, and state-sync order are covered. |

- Source guardrail: `tests/simulator/test_migrated_am_ap_reader_guardrail.py` scans exactly these six root files, excludes `.codex_worktrees/`, and fails on direct `MultiplierData` imports / construction, alias `Mul(...)`, or direct AM/AP Calculator reads.
- Validation evidence: focused reader/state-sync/guardrail pytest passed with `45 passed`; `calculator-reads` profile passed with base `2 passed`, isolated teams `3 passed`, focused `63 passed`, and mypy `20 source files` clean; `implicit-events` profile passed with base `2 passed`, isolated teams `3 passed`, focused `105 passed`, and mypy `76 source files` clean.
- Behavior sample note: current registered teams do not include Alice / Yuzuha / Jane, so no main-loop sample was run for P2-A; future samples should use a real registered team rather than inventing a validation-only fixture.
- Next pool state at that handoff: P2-B crit / impact reader family, P2-C trigger-state gates, P2-D scheduled publish ordering / adapter parity, P2-E dot runtime-state / initialization and P2-F BuffAddStrategy facade-write design have completed after follow-up PRDs. P2-G direct simulator context extraction was the then-default same-phase PRD candidate; phase-3 formula snapshot replacement, retained compatibility, P2-F guarded maintenance and blocker-only phase-1 reopen rows remained available.

### 2026-06-08 P2-B completion update

本节记录 crit / impact reader family PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 US-003 / US-007 的历史扫描证据。

| file | previous P2-B coupling | current migration evidence | retained behavior / test evidence |
| --- | --- | --- | --- |
| `LighterAdditionalAbility_IceFireBonus.py` | `Calculator.StunMul.cal_imp(...)` impact read then count writeback. | Uses `create_anomaly_attribute_read_context(...)` and `CalculatorBuffAttributeReader.read_impact(...)`. | Base / normal / high impact count parity, aggregation shape, old `buff_0` identity, and source-level order are covered by state-sync tests. |
| `QingYiAdditionalAbilityStunConvertToATK.py` | Direct impact read then old-count adjustment and ATK count writeback. | Uses the same impact reader/context shape as Lighter. | Inactive/no-op, normal impact, max-count cap, aggregation shape, old `buff_0` identity, and source guard assertions are covered. |
| `TriggerAdditionalAbilityStunBonus.py` | Direct personal crit rate read then aftershock count writeback. | Uses `CalculatorBuffAttributeReader.read_personal_crit_rate(...)`. | Aftershock gate, active count parity, cap behavior, no received-crit inclusion, aggregation shape, old `buff_0` identity, and read-before-start order are covered. |
| `Soldier0AnbyCoreSkillCritDMGBonus.py` | `MultiplierData as Mul` / direct personal crit damage read then count writeback. | Uses `CalculatorBuffAttributeReader.read_personal_crit_damage(...)`. | Inactive gate, active count parity, cap behavior, no received-crit-damage inclusion, exit behavior, old `buff_0` identity, and simple-start-before-read order are covered. |
| `CannonRotor.py` | Direct full crit rate read in RNG gate with scheduled publish. | Uses `CalculatorBuffAttributeReader.read_full_crit_rate(...)` while retaining dispatch port publish. | Publish/no-publish branches, RNG threshold, payload fields, `LoadingMission.mission_start(...)` / publish ordering, and source guard assertions are covered. |
| `MiyabiCoreSkill_IceFire.py` | Direct full crit rate read around IceFire count adjustment and dispatch follow-up. | Uses `CalculatorBuffAttributeReader.read_full_crit_rate(...)`. | No-skill / no-element / no-debuff branches, full crit count parity, old-count adjustment, dispatch publish branch, old `buff_0` identity, and source order are covered. |
| `WoodpeckerElectroSet4_NA.py` | Direct full crit rate RNG gate for NA label. | Uses `CalculatorBuffAttributeReader.read_full_crit_rate(...)`. | No SkillNode / wrong label, crit-fail or RNG-fail, crit-success, aggregation shape, and source guard assertions are covered. |
| `WoodpeckerElectroSet4_E_EX.py` | Direct full crit rate RNG gate for E/EX label. | Uses the same full-crit reader/context pattern as NA. | E/EX branch coverage, crit/RNG fail, success, aggregation shape, and source guard assertions are covered. |
| `WoodpeckerElectroSet4_CA.py` | Direct full crit rate RNG gate for CA label. | Uses the same full-crit reader/context pattern as NA and E/EX. | CA branch coverage, crit/RNG fail, success, aggregation shape, and source guard assertions are covered. |

- Source guardrail: `tests/simulator/test_migrated_p2b_reader_guardrail.py` scans exactly these nine root files, excludes `.codex_worktrees/`, and fails on direct `MultiplierData` imports / construction, alias `Mul(...)`, direct `Calculator.StunMul.cal_imp(...)`, direct `Calculator.RegularMul.cal_crit_rate(...)`, direct `Calculator.RegularMul.cal_personal_crit_rate(...)`, direct `Calculator.RegularMul.cal_personal_crit_dmg(...)`, or `Cal.*` aliases for migrated reads.
- Validation evidence: focused P2-B pytest passed with `107 passed`; `calculator-reads` profile passed with base `2 passed`, isolated teams `3 passed`, focused `129 passed`, and mypy `22 source files` clean; `implicit-events` profile passed with base `2 passed`, isolated teams `3 passed`, focused `136 passed`, and mypy `77 source files` clean.
- Behavior sample evidence: `莱特火属性队` stop-tick 600 consistency sample passed with `matches=true`, total damage `646446.67` vs `646446.67`, event count total `19` vs `19`, event-count differences all zero, and buff timeline `legacy_only_count=0` / `candidate_only_count=0`.
- Next pool state at that handoff: P2-C trigger-state read-only gates, P2-D scheduled publish ordering / adapter parity, P2-E dot runtime-state / initialization and P2-F BuffAddStrategy facade-write design have completed after follow-up PRDs. P2-G direct simulator context extraction was the then-default same-phase PRD candidate. Phase-3 formula snapshot replacement, retained compatibility, P2-F guarded maintenance and blocker-only phase-1 reopen rows remained available.

### 2026-06-08 P2-C completion update

本节记录 trigger-state read-only gates PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 US-003 / US-005 / US-007 的历史扫描证据。

| file | previous P2-C coupling | current migration evidence | retained behavior / test evidence |
| --- | --- | --- | --- |
| `FlamemakerShakerApBonus.py` | Direct old-template `record.trigger_buff_0.dy.active` / `.count` gate for `灼心摇壶` AP threshold. | Uses `read_trigger_buff_state(self.record)` after existing `get_prepared(equipper="灼心摇壶", trigger_buff_0=(...))`. | Inactive false, count `< 5` false, count `>= 5` true, no-write behavior and old trigger identity are covered. |
| `SpectralGazeImpactBonus.py` | Direct old-template active / exact-count gate for `索魂影眸` impact bonus. | Uses `read_trigger_buff_state(self.record)` after existing `get_prepared(equipper="索魂影眸", trigger_buff_0=(...))`. | Inactive false, count `!= 3` false, count `== 3` true, `xexit` behavior and no-write behavior are covered. |
| `SharpenedStingerAnomalyBuildupBonus.py` | Direct old-template count gate with preload-assisted preparation for `淬锋钳刺`. | Uses `read_trigger_buff_state(self.record).count` after existing `get_prepared(equipper="淬锋钳刺", preload_data=1, trigger_buff_0=(...))`. | Counts `0`, `2`, `3`, `4`, inverse exit behavior, no scheduled publish / runtime write and lazy record identity are covered. |
| `CordisGerminaSNAAndQIgnoreDefense.py` | Direct old-template `built_in_buff_box` length read for `机巧心种` read-only tuple gate. | Uses `read_trigger_buff_state(self.record).built_in_buff_box` after existing `get_prepared(equipper="机巧心种", trigger_buff_0=(...))`. | Tuple-box lengths `0`, `1`, `2`, `3`, inverse exit behavior, and no tuple-box writer / rebuild / sync behavior are covered. |
| `AstralVoice.py` | Direct old-template active read in judge gate and direct count read in effect mirror. | Judge and effect paths use `read_trigger_buff_state(self.record)` while preserving `SkillNode` / `LoadingMission` normalization and `simple_start(...) -> current dy.count -> update_to_buff_0(self.buff_0)` order. | Judge no-write branches, trigger counts `0`, normal and high sample, old template passed to `update_to_buff_0(...)`, no `RuntimeCommandPort` / scheduled publish and registered `青衣雷属性队` / `席德大安比队` evidence are covered. |

- Source guardrail: `tests/simulator/test_migrated_p2c_trigger_state_guardrail.py` scans exactly these five root files, excludes `.codex_worktrees/`, and fails on direct `record.trigger_buff_0.dy.active`, `.dy.count`, or `.dy.built_in_buff_box` chains.
- Validation evidence: `implicit-events` profile passed with base `2 passed`, isolated teams `3 passed`, focused `181 passed`, and mypy `80 source files` clean.
- Behavior sample evidence: `席德大安比队` stop-tick 1000 consistency sample passed with `matches=true`, total damage `5744827.24` vs `5744827.24`, event count total `50` vs `50`, event-count differences all zero, and buff timeline `legacy_only_count=0` / `candidate_only_count=0`.
- Next pool state at that handoff: P2-D scheduled publish ordering / adapter parity, P2-E dot runtime-state / initialization and P2-F BuffAddStrategy facade-write design have completed after follow-up PRDs. P2-G direct simulator context extraction was the then-default same-phase PRD candidate. Phase-3 formula snapshot replacement, retained compatibility, P2-F guarded maintenance and blocker-only phase-1 reopen rows remained available.

### 2026-06-08 P2-D completion update

本节记录 scheduled publish ordering / adapter parity PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 event adapter / listener / dot / runtime write 分层证据。

| coverage family | current evidence | retained behavior / boundary |
| --- | --- | --- |
| Dispatch adapter rebinding | `tests/simulator/test_schedule_dispatch.py` covers `create_schedule_dispatch_port(schedule_data=...)`, `create_schedule_dispatch_port(sim_instance=...)`, event-list rebinding after replacement, and queue-only public API. | Dispatch ports are created on demand from current `sim_instance` / `schedule_data`; raw queue access remains internal to `LegacyEventListScheduleDispatchAdapter`. |
| Resource refresh payloads | `test_xstart_sp_refresh_dispatch.py` and `test_xhit_sp_refresh_dispatch.py` cover `ElegantVanitySpRecover`, `LunarNoviluna`, `MagneticStormCharlieSpRecover`, `SeedAdditionalAbilityTrigger` and existing `SliceofTimeExtraResources` behavior for exact `ScheduleRefreshData` fields, target/order and no raw queue. | Report-only `change_process_state()` / print behavior remains report state, not a scheduled payload. |
| `SkillNode` / `LoadingMission` order | `test_cannon_rotor_dispatch.py`, `test_yixuan_cinema1_dispatch.py`, `test_yanagi_polarity_disorder_dispatch.py` and `test_hugo_totalize_dispatch.py` cover payload identity, `mission_start(...)` before publish, publish-before-reset behavior and no-publish branches. | Existing producer order is retained; Calculator reader, trigger-state helper and runtime write boundaries are not reopened. |
| Stateful anomaly / dot layers | `test_update_anomaly_dispatch.py`, `test_alice_dot_trigger_dispatch.py` and `test_vivian_dot_trigger_dispatch.py` cover scheduled publish payloads and order while proving listener broadcast, dot runtime registration/removal and runtime immediate writes remain separate layers. | `listener_manager.broadcast_event(...)` stays synchronous, `enemy.dynamic.dynamic_dot_list` stays runtime dot state, and `RuntimeCommandPort` remains the same-tick write boundary. |
| Fan-out / multi-publish / priority | `test_decibel_manager_dispatch.py` adds no-publish branches and producer-level event-list rebinding; existing Yuzuha, Hugo, BreakingLegManager and Vivian focused tests remain sufficient for their covered branches. | `ScheduleDispatchPort` remains queue-only; handler requeue and core Load/Schedule append are not producer publish backlog. |
| Exact-file guardrail | `test_migrated_p2d_scheduled_publish_guardrail.py` scans only the P2-D migrated root producer set, excludes `.codex_worktrees/`, and blocks raw queue access, legacy event-list discovery, event-list preparation requests and long-lived cached dispatch adapters. | Guardrail does not scan core scheduler internals, local Character event groups, dot runtime registration, listener broadcast, runtime command writes, or P2-E / P2-F / P2-G candidates. |

- Validation evidence: `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed serially with base simulator `2 passed`, isolated teams `3 passed`, focused implicit-events pytest `194 passed`, and mypy `Success: no issues found in 81 source files`.
- Behavior sample decision: skipped for P2-D because the PRD branch changed focused tests, exact-file guardrails, validation wiring, docs and Ralph artifacts only; no root production behavior file or live scheduled-publish order changed relative to `ralph/buff-refactor-phase2-trigger-state-read-only-gates`.
- Old-coupling review decision: no update to `docs/旧Buff系统耦合审查结果.md` was needed; no new coupling was found beyond existing scheduled publish / listener / dot / runtime write retained boundaries.
- Next pool state at that handoff: P2-E dot runtime-state / initialization and P2-F BuffAddStrategy facade-write design have completed guarded scope after follow-up PRDs. P2-G direct simulator context extraction was the then-default same-phase PRD candidate. Phase-3 formula snapshot replacement, retained compatibility, P2-F guarded maintenance and blocker-only phase-1 reopen rows remained available.

### 2026-06-09 P2-E completion update

本节记录 dot runtime-state / initialization PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 anomaly / debuff / dot bypass、scheduled publish 或 runtime write 分层证据。

| coverage family | current evidence | retained behavior / boundary |
| --- | --- | --- |
| Runtime dot-state helper | `zsim/sim_progress/Dot/runtime_state.py` adds `DotRuntimeStateAdapter` with snapshot, index / active-index find, duplicate-safe registration, same-index replacement, predicate removal and explicit collection removal; `tests/simulator/test_dot_runtime_state_adapter.py` covers order and forbidden scheduled / listener / runtime-command side effects. | Runtime dot list state remains `enemy.dynamic.dynamic_dot_list`; helper does not publish scheduled events, broadcast listeners, call `RuntimeCommandPort`, or access old Buff containers. |
| Vivian dot gates | `VivianDotTrigger.py` and `VivianCinema1Debuff.py` use `DotRuntimeStateAdapter.find_active_by_index(...)` / `register(...)`; `tests/simulator/test_vivian_dot_trigger_dispatch.py` covers active-dot duplicate prevention, `dot.start(...) -> LoadingMission.mission_start(...) -> register -> publish_scheduled(...)` order, and cinema-1 presence / absence. | Scheduled dot `SkillNode` publish remains on `ScheduleDispatchPort`; old `buff_0.history.record` lazy init and template identity remain intact. |
| UpdateAnomaly replacement / removal | `UpdateAnomaly.anomaly_effect_active(...)` uses `DotRuntimeStateAdapter.replace_by_index(...)` after `spawn_anomaly_dot(...)`; `remove_dots_cause_disorder(...)` uses the helper for runtime-list removal while keeping freeze follow-up `_publish_scheduled_event(dispatch_port, _dot.anomaly_data)` caller-owned. Focused tests cover replacement, spawn-false no-op, debuff branch separation, non-freeze removal, freeze mutations and invalid entries. | `buff_add_strategy(...)` debuff writes remain outside the dot helper; listener broadcast, scheduled publish, report/process-state behavior and runtime dot removal remain separate layers. |
| Shock initialization read | `zsim/sim_progress/Dot/initialization.py` adds `DotInitializationReadContext`; `Shock.DotFeature.__post_init__()` uses it for `init_data.name_box` and Rina passive presence while preserving `sim_instance is None` validation and `600` / `600` / `780` outcomes. | No dependency on `ScheduleDispatchPort`, `RuntimeCommandPort`, `BuffRuntimeReadPort` writes, Calculator, CalAnomaly or `dynamic_dot_list`. |
| Exact-file guardrail | `tests/simulator/test_migrated_p2e_dot_runtime_guardrail.py` scans only the migrated root P2-E files and excludes `.codex_worktrees/`; it blocks raw scheduler queue writes / deleted discovery surfaces, invalid scheduled publish of runtime dot registration / removal, second write facades, write methods on `BuffRuntimeReadPort`, and direct Shock retained reads outside the helper. | Guardrail intentionally excludes P2-F `BuffAddStrategy`, P2-G direct simulator context helpers, `LoadDamageEvent`, `Update_Buff.update_dot()`, and Alice dot listener retained boundaries. |

- Validation evidence: `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed serially with base simulator `2 passed`, isolated teams `3 passed`, focused implicit-events pytest `217 passed`, and mypy `Success: no issues found in 86 source files`.
- Behavior sample decision: skipped for P2-E because production callsites were migrated through parity-tested helpers / guardrails without changing live duration, tick, damage, or timeline semantics; focused dot tests, exact-file source guardrails and serial validation are the relevant evidence.
- Old-coupling review decision: no update to `docs/旧Buff系统耦合审查结果.md` was needed; root-source evidence found no new coupling beyond the guarded P2-E migrated file set and retained P2-F / P2-G candidates.
- Next pool state at that handoff: P2-F BuffAddStrategy caller / facade-write design has completed guarded scope after the follow-up PRD. P2-G direct simulator context extraction was the then-default same-phase PRD candidate. P2-D / P2-E / P2-F guarded maintenance, phase-3 formula snapshot replacement, retained compatibility and blocker-only phase-1 reopen rows remained available.

### 2026-06-09 P2-F completion update

本节记录 BuffAddStrategy caller / facade-write design PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 same-tick write、listener、scheduled publish、dot runtime-state 或 direct context 分层证据。

| coverage family | current evidence | retained behavior / boundary |
| --- | --- | --- |
| Facade contract | `tests/simulator/test_buff_add_strategy_runtime_facade.py` covers active replacement, enemy mirror sync, selected target fan-out, explicit `benifit_list`, template identity, `specified_count`, and no pending queue writes. | `buff_add_strategy(...)` still creates / uses the existing `LegacyBuffRuntimeFacade`; old registry/template identity and facade-backed active-store / mirror writes remain retained behavior. |
| Caller families | Focused tests cover Hugo Totalize, Roaring Ride, Seed, `UpdateAnomaly.anomaly_effect_active(...)`, BattleEventListener and Character manager representatives, including exact arguments, no-op branches, target forwarding and `sim_instance` forwarding. | Production caller formulas, source gates, listener activation, Character state transitions and scheduled publish / preload side effects remain unchanged. |
| Cross-layer semantics | `tests/simulator/test_bypass_layer_semantics.py` proves forced Buff / Debuff writes stay separate from `ScheduleDispatchPort`, listener broadcast, `RuntimeCommandPort`, `BuffRuntimeReadPort`, and pending queue mutation. | Runtime immediate write, planned-event queue publish, synchronous listener broadcast, scheduled-handler command writes and read-only runtime views remain separate layers. |
| Exact-file guardrail | `tests/simulator/test_migrated_p2f_buff_add_strategy_guardrail.py` scans only `zsim/sim_progress/Buff/BuffAddStrategy.py` and `zsim/sim_progress/ScheduledEvent/buff_runtime.py`, excludes `.codex_worktrees/`, `__pycache__/` and archives, and is wired into `implicit-events` focused pytest / scoped mypy. | Guardrail blocks raw pending / active / mirror writes, deleted event-list discovery, scheduled queue conversion, listener broadcast conversion, second write facades and `BuffRuntimeReadPort` write APIs while preserving documented facade construction and registry/template compatibility. |

- Validation evidence: uncovered P2-F caller focused pytest passed serially (`Roaring Ride 5 passed`, `Seed 6 passed`, `UpdateAnomaly 10 passed`, `listener 4 passed`, `Character 4 passed`), and `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed with base simulator `2 passed`, isolated teams `3 passed`, focused implicit-events `229 passed`, and typecheck clean.
- Behavior sample decision: skipped for P2-F because this PRD completed caller / guardrail / validation evidence without production behavior changes, lifecycle wiring changes, live Buff write semantic changes, main-loop tick sweep changes, pending activation changes, active removal changes, or enemy mirror behavior changes.
- Old-coupling review decision: no update to `docs/旧Buff系统耦合审查结果.md` was needed; root-source evidence matched already documented P2-F forced-write coupling and no new materially changed Buff coupling was discovered.
- Next pool state at that handoff: P2-G direct simulator context extraction was the then-default same-phase PRD candidate. P2-D / P2-E / P2-F guarded maintenance, phase-3 formula snapshot replacement, retained compatibility and blocker-only phase-1 reopen rows remained available.

### 2026-06-09 P2-G completion update

本节记录 direct simulator context helpers PRD 收口状态；它更新 ranked pool 的当前状态，不覆盖前面 scheduled publish、listener、same-tick runtime write、dot runtime-state、BuffAddStrategy facade-write 或 formula snapshot 分层证据。

| coverage family | current evidence | retained behavior / boundary |
| --- | --- | --- |
| Yuzuha tick / preload / next-character / report-state | `tests/simulator/test_yuzuha_direct_context_helpers.py` covers Hard Candy tick / preload action and no-op branches, Cinema4 quick-assist next-character lookup, Cinema6 Sheel preload/report-state ordering, Cinema2 report-state mutation, and Sugar Burst preload-tick gating. | `sim_instance.tick`, `preload.preload_data`, `char_data.find_next_char_obj(...)`, local Character action/resource behavior, `schedule_preload_event_factory(...)`, and `schedule_data.change_process_state()` remain separate service boundaries. |
| Enemy context | `tests/simulator/test_enemy_context_direct_helpers.py` covers `YixuanAdditionalAbilityDmgBonus` positive and no-stun branches with old-container / queue / listener / runtime guards. | Direct `schedule_data.enemy` reads remain enemy-context fact reads, not scheduled publish, runtime write, dot/anomaly consolidation, or old-container deletion work. |
| Listener lookup | `tests/simulator/test_listener_manager_direct_context.py` covers `HeartstringNocturne.special_judge_logic()` listener lookup, cached-listener reuse, and no-op mismatch behavior. | `listener_manager.get_listener(...)` remains direct listener context lookup; `listener_manager.broadcast_event()` remains a separate synchronous broadcast boundary. |
| RNG service and crit-adjacent contrast | `tests/simulator/test_full_crit_event_adjacent_reader.py` covers `CannonRotor.special_judge_logic()` and Woodpecker full-crit RNG gates with deterministic fake RNG and fail-fast forbidden-layer probes. | RNG service reads remain separate from `CannonRotor.special_hit_logic()` scheduled publish, P2-F Roaring Ride forced writes, Calculator formula snapshots, and received-crit semantics. |
| Report-state representative | `tests/simulator/test_report_state_direct_context.py` covers `AstraYaoCorePassiveAtkBonus.special_start_logic()` positive report-state change, same-tick no-op gate, and dispatch/listener/runtime/raw-queue separation. | `schedule_data.change_process_state()` remains report-state / process-state behavior, not scheduled payload publication, listener broadcast, runtime immediate write, or old-container deletion. |
| Exact-file / selected-symbol guardrail | `tests/simulator/test_migrated_p2g_direct_context_guardrail.py` scans selected root P2-G representatives and symbols, excludes `.codex_worktrees/`, `__pycache__/`, generated logs and Ralph archives, and is wired into `implicit-events` focused pytest / scoped mypy. | Guardrail preserves P2-A through P2-F completed buckets and only blocks raw queue passthroughs, deleted discovery, second runtime write facades, listener/scheduled/runtime conflation, and service-family-specific regressions in the selected P2-G scope. |

- Validation evidence: final focused P2-G pytest passed with `67 passed`; `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed serially with base simulator `2 passed`, isolated teams `3 passed`, focused implicit-events `238 passed`, and mypy `Success: no issues found in 88 source files`; `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed serially with base simulator `2 passed`, isolated teams `3 passed`, focused calculator-reads `133 passed`, and mypy `Success: no issues found in 22 source files`.
- Behavior sample decision: skipped for P2-G because the PRD branch changed focused tests, guardrail, validation wiring, docs and Ralph artifacts only; no root production behavior file or live registered-team semantics changed.
- Old-coupling review decision: no update to `docs/旧Buff系统耦合审查结果.md` was needed; root-source evidence found no new direct-context coupling beyond the already documented P2-G candidates.
- Next pool state: P2-A through P2-G are completed guarded phase-2 buckets. The next default PRD should be a phase-2 closure / phase-3 formula snapshot readiness decision following `docs/Buff重构方案.md`; same-phase work is limited to guarded maintenance or blocker-only fixes backed by validation / source evidence.

### US-008 结论

- 第一推荐 follow-up 已从完成的 P2-G 转为 phase-2 closure / phase-3 formula snapshot readiness decision；未来 PRD 仍应沿 `docs/Buff重构方案.md` 的路线推进，而不是制造新的 phase-2 helper backlog。
- Immediate follow-ups should group by phase-2 closure evidence, guarded maintenance regressions or validation profile failures. Formula snapshot replacement should move only after the readiness PRD names the formula parity suite, source scope and non-goals.
- Formula snapshots, old containers, legacy `buff_add()` / `KickOutBuff()` and deleted raw queue discovery surfaces remain retained compatibility or phase-3 / blocker-only targets, not phase-2 replacement work.
- CodeGraph evidence was used to cross-check fan-out and contract risk, but `.codex_worktrees/` duplicates and incomplete dynamic caller coverage mean final conclusions still depend on the root-workspace source classifications from US-001 through US-007 plus validation output.
- P2-F added test / guardrail / validation wiring only; it did not replace live XLogic behavior, change the runtime boundary, delete old containers, or change production behavior.

### 2026-06-09 US-002 根工作区公式快照 Census

本节补 phase-2 closure / phase-3 formula snapshot readiness 的根工作区复扫结果。它只更新 census 证据和后续分桶，不修改 `Calculator.py`、`CalAnomaly.py`、XLogic 行为、runtime port、dispatch adapter 或验证脚本。

#### 可复现扫描命令

以下命令在根工作区执行，默认排除 `.codex_worktrees/**`、`__pycache__/**`、`*.log` 和 `scripts/ralph/archive/**`。根工作区总数保留 docs / tasks / scripts 命中，用于确认历史材料和当前 PRD 自身不会被误当成生产 blocker；生产结论只采信 root `zsim/`、focused tests 和当前验证入口。

```powershell
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "Calculator" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "CalAnomaly" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "MultiplierData" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "MulData" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "current_ndarray" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "DynamicStatement" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "cal_am" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "cal_ap" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "cal_imp" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "cal_crit_rate" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "cal_personal_crit_rate" .
rg -n --hidden --glob '!.codex_worktrees/**' --glob '!__pycache__/**' --glob '!**/__pycache__/**' --glob '!*.log' --glob '!scripts/ralph/archive/**' "cal_personal_crit_dmg" .
```

#### Census 结果

| term | total matches / files | group split | representative root source | representative tests |
| --- | ---: | --- | --- | --- |
| `Calculator` | 706 / 71 | zsim=86, tests=96, docs=327, tasks=183, scripts=12, other=2 | `zsim/sim_progress/ScheduledEvent/Calculator.py`, `zsim/sim_progress/Character/utils/filters.py`, `zsim/sim_progress/Buff/BuffXLogic/CannonRotor.py` | `tests/simulator/test_buff_attribute_reader.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_buff_raw_container_guardrail.py` |
| `CalAnomaly` | 213 / 29 | zsim=9, tests=7, docs=145, tasks=42, scripts=10 | `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, `zsim/sim_progress/ScheduledEvent/event_handlers/handlers/anomaly.py` | `tests/simulator/test_dot_runtime_initialization.py`, `tests/simulator/test_anomaly_handler_runtime_view.py`, `tests/simulator/test_enemy_context_direct_helpers.py` |
| `MultiplierData` | 425 / 40 | zsim=51, tests=106, docs=157, tasks=103, scripts=6, other=2 | `zsim/sim_progress/ScheduledEvent/Calculator.py`, `zsim/sim_progress/Character/utils/filters.py`, `zsim/sim_progress/ScheduledEvent/CalAnomaly.py` | `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_buff_attribute_reader.py`, `tests/simulator/test_full_crit_event_adjacent_reader.py` |
| `MulData` | 36 / 10 | zsim=5, tests=3, docs=20, tasks=6, scripts=2 | `zsim/sim_progress/ScheduledEvent/CalAnomaly.py` | `tests/simulator/test_buff_raw_container_guardrail.py` |
| `current_ndarray` | 36 / 9 | zsim=25, docs=6, tasks=3, scripts=2 | `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`, `zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py`, `zsim/sim_progress/Update/UpdateAnomaly.py`, `zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py` | none |
| `DynamicStatement` | 19 / 5 | zsim=3, docs=6, tasks=5, scripts=5 | `zsim/sim_progress/ScheduledEvent/Calculator.py` | none |
| `cal_am` | 47 / 12 | zsim=2, tests=11, docs=24, tasks=7, scripts=2, other=1 | `zsim/sim_progress/ScheduledEvent/Calculator.py` | `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_migrated_am_ap_reader_guardrail.py`, `tests/simulator/test_buff_attribute_reader.py` |
| `cal_ap` | 57 / 16 | zsim=7, tests=24, docs=17, tasks=7, scripts=2 | `zsim/sim_progress/ScheduledEvent/Calculator.py`, `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, `zsim/sim_progress/Buff/BuffXLogic/VivianCorePassiveTrigger.py`, `zsim/sim_progress/Buff/BuffXLogic/VivianCinema6Trigger.py` | `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_vivian_core_passive_trigger_dispatch.py`, `tests/simulator/test_vivian_cinema6_trigger_dispatch.py` |
| `cal_imp` | 43 / 11 | zsim=3, tests=8, docs=14, tasks=11, scripts=7 | `zsim/sim_progress/ScheduledEvent/Calculator.py` | `tests/simulator/test_migrated_p2b_reader_guardrail.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_buff_attribute_reader.py` |
| `cal_crit_rate` | 50 / 11 | zsim=3, tests=11, docs=21, tasks=13, scripts=2 | `zsim/sim_progress/ScheduledEvent/Calculator.py` | `tests/simulator/test_full_crit_event_adjacent_reader.py`, `tests/simulator/test_migrated_p2b_reader_guardrail.py`, `tests/simulator/test_buff_attribute_reader.py` |
| `cal_personal_crit_rate` | 30 / 10 | zsim=2, tests=7, docs=11, tasks=8, scripts=2 | `zsim/sim_progress/ScheduledEvent/Calculator.py` | `tests/simulator/test_migrated_p2b_reader_guardrail.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_buff_attribute_reader.py` |
| `cal_personal_crit_dmg` | 30 / 10 | zsim=2, tests=8, docs=10, tasks=8, scripts=2 | `zsim/sim_progress/ScheduledEvent/Calculator.py` | `tests/simulator/test_migrated_p2b_reader_guardrail.py`, `tests/simulator/test_buff_attribute_state_sync.py`, `tests/simulator/test_buff_attribute_reader.py` |

#### CodeGraph 导航证据

- Query terms used: `US-002 Build Root Formula Snapshot Census`, `docs/BuffXLogic阶段2全量分类与复用矩阵.md`, `Calculator.py`, `CalAnomaly.py`, `AnomalyBarClass.py`, `UpdateAnomaly.py`, `VivianCinema6Trigger.py`, `VivianCorePassiveTrigger.py`, `Calculator`, `CalAnomaly`, `MultiplierData`, `MulData`, `current_ndarray`, `DynamicStatement`, `cal_am`, `cal_ap`, `cal_imp`, `cal_crit_rate`, `cal_personal_crit_rate`, `cal_personal_crit_dmg`, `calculator-reads`.
- CodeGraph again surfaced `.codex_worktrees/` duplicates for Calculator / CalAnomaly helpers. Those hits remain historical navigation evidence only and are excluded from blocker conclusions.
- Root `Calculator.py` owns `MultiplierData`, `DynamicStatement`, `_calculate_anomaly_mastery(...)`, `_calculate_anomaly_proficiency(...)`, `AnomalyMul.cal_am(...)`, `AnomalyMul.cal_ap(...)`, `StunMul.cal_imp(...)`, and `RegularMul` crit helpers. Existing `CalculatorBuffAttributeReader` is a parity seam, not a formula replacement.
- Root `CalAnomaly.__init__(...)` consumes settled `AnomalyBar.current_ndarray`, asserts `(1, 11)`, builds `MulData(...)`, and calls Calculator multiplier helpers before `cal_anomaly_dmg(...)` multiplies `final_multipliers` with `anomaly_obj.scaling_factor`.
- Root `AnomalyBar.current_ndarray` is the settled anomaly snapshot field; `UpdateAnomaly` and Vivian trigger comments are adjacent evidence, but they do not create a new phase-2 implementation target by themselves.

#### Formula snapshot buckets

| bucket | current representative files / symbols | readiness conclusion | retained boundary | validation entrypoint / non-goal |
| --- | --- | --- | --- | --- |
| Calculator formula core | `zsim/sim_progress/ScheduledEvent/Calculator.py`, `MultiplierData`, `DynamicStatement`, `AnomalyMul.cal_am(...)`, `AnomalyMul.cal_ap(...)`, `StunMul.cal_imp(...)`, `RegularMul.cal_crit_rate(...)`, `RegularMul.cal_personal_crit_rate(...)`, `RegularMul.cal_personal_crit_dmg(...)` | Current source has one central formula snapshot module. Future phase-3 work must define formula parity before shrinking it. | Keep `MultiplierData` cache, dynamic statement aggregation, static/dynamic formula fields, and current helper semantics. | `calculator-reads`; no formula rewrite, cache deletion, or helper expansion in this story. |
| CalAnomaly settled snapshot | `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, `MulData`, `AnomalyBar.current_ndarray`, `cal_anomaly_dmg(...)` | This is a damage-defining anomaly snapshot path, not a phase-2 reader-helper candidate. | Keep settled snapshot shape `(1, 11)`, virtual level extraction, Calculator multiplier calls, final multiplier product, and scaling factor behavior. | Future formula parity suite plus anomaly focused tests; no `CalAnomaly` behavior edit in this story. |
| Anomaly copied-output / current array adjacency | `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`, `zsim/sim_progress/Update/UpdateAnomaly.py`, `VivianCorePassiveTrigger.py`, `VivianCinema6Trigger.py` | `current_ndarray` appears in runtime anomaly state and copied-output comments; it supports phase-3 inventory but is not new raw queue, dot runtime, or same-tick write evidence. | Keep anomaly runtime state, scheduled publish, listener broadcast, dot runtime registration and runtime immediate writes as separate layers. | Use `implicit-events` only when a later story changes publish/runtime behavior; no phase-2 replacement from comments alone. |
| BuffXLogic reader-family remnants | AM/AP, impact, full-crit, personal-crit and personal-crit-damage XLogic families already documented under US-003 / P2-A / P2-B completion rows. | Completed P2-A / P2-B guardrails are maintenance evidence; new phase-3 work should start from root formula scope and parity, not reopen completed XLogic helper buckets. | Retain old `buff_0` identity, state-sync order, scheduled publish order and Calculator formulas. | Open blocker only on focused guardrail or validation failure; no broad XLogic migration in this readiness census. |
| Docs / PRD / scripts hits | `docs/Buff重构替换说明.md`, this matrix, current task PRD, `scripts/ralph/prd.json`, `scripts/ralph/context_index.py` | These hits explain high root total counts and should not be treated as production callsites. | Root-source and focused-test evidence remain the compatibility basis. | Do not create backlog from planning-text matches. |

#### US-002 readiness conclusion

- The root census names current formula snapshot surfaces without editing formula behavior: `Calculator.py`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`, and completed reader-family guardrails are the evidence base for later phase-3 planning.
- `.codex_worktrees/`, generated logs, `__pycache__` and `scripts/ralph/archive/` remain excluded from blocker conclusions.
- Current default route remains phase-2 closure / phase-3 readiness following `docs/Buff重构方案.md`; the next formula story should define parity scope and tests before touching damage formulas.

### 2026-06-09 US-003 P2-A 到 P2-G Guardrail Closure Matrix

本节审计已完成的 P2-A through P2-G guardrail evidence，只收口 closure 证据，不扩大任何 migrated-file 扫描范围，也不修改 production formula、dispatch、runtime-write 或 direct-context 行为。

| bucket | source guardrail / focused evidence | validation profile | retained boundary | blocker-only reopen condition |
| --- | --- | --- | --- | --- |
| P2-A AM/AP reader + computed count state-sync | `tests/simulator/test_migrated_am_ap_reader_guardrail.py` 锁定六个 root migrated files，阻断 direct `MultiplierData` / `Mul(...)` / direct AM/AP Calculator reads；reader parity 与 state-sync tests 保护 `simple_start(...) -> dy.count -> update_to_buff_0(...)` 顺序。 | `calculator-reads`; event-adjacent maintenance also runs `implicit-events`. | `MultiplierData` formula snapshot、old `buff_0` identity、record fields、state-sync order retained. | Only reopen if P2-A guardrail, reader parity, state-sync order test, or validation profile names a concrete migrated-file regression. |
| P2-B crit / impact reader family | `tests/simulator/test_migrated_p2b_reader_guardrail.py` 锁定九个 root files，阻断 direct impact / full-crit / personal-crit Calculator reads；full-crit event-adjacent tests pin received-crit and dispatch contrast. | `calculator-reads`; dispatch-adjacent maintenance also runs `implicit-events`. | Full crit includes received crit; personal crit rate / damage exclude received crit; Calculator / CalAnomaly formula snapshots and existing scheduled publish order retained. | Only reopen on migrated-file guardrail failure, reader/state-sync/full-crit test failure, file-specific dispatch failure, or validation failure. |
| P2-C trigger-state read-only gates | `tests/simulator/test_migrated_p2c_trigger_state_guardrail.py` plus `test_trigger_state_read_only_gates.py` guard five root migrated files and no-write / count mirror behavior. | `implicit-events`. | `BuffRuntimeReadPort` remains read-only; old template identity, `check_preparation(..., trigger_buff_0=...)`, `trigger_buff_0_handler(...)`, and `JudgeTools.find_exist_buff_dict(...)` retained. | Only reopen if migrated trigger-state files regain direct writable old-template access or validation names a read-only gate/order regression. |
| P2-D scheduled publish ordering / adapter parity | `tests/simulator/test_migrated_p2d_scheduled_publish_guardrail.py` locks exact migrated producer set, raw queue absence, deleted discovery absence, event-list preparation absence, and no long-lived cached dispatch adapters; file-specific tests cover payload, target fan-out, priority, execute tick, and no-publish branches. | `implicit-events`. | `ScheduleDispatchPort` is queue-only; adapters are created on demand from current `sim_instance` / `schedule_data`; listener broadcast, dot runtime registration, and same-tick runtime writes stay separate. | Only reopen if exact-file guardrail or file-specific dispatch tests expose raw queue regression, stale adapter caching, payload/order drift, or validation failure. |
| P2-E dot runtime-state / initialization | `tests/simulator/test_migrated_p2e_dot_runtime_guardrail.py`, dot runtime-state tests, dot initialization tests, Vivian / UpdateAnomaly focused tests guard runtime list mutation, scheduled follow-up payloads, Shock duration reads, and no second write facade. | `implicit-events`. | `enemy.dynamic.dynamic_dot_list` remains runtime state; only scheduled `SkillNode` / `anomaly_data` payloads publish through `ScheduleDispatchPort`; Buff / Debuff writes stay on existing facade paths. | Only reopen if P2-E guardrail or focused dot tests show runtime dot registration/removal converted to scheduled backlog, invalid scheduled payloads, direct Shock read regression, second write facade, or validation failure. |
| P2-F BuffAddStrategy caller / facade-write design | `tests/simulator/test_migrated_p2f_buff_add_strategy_guardrail.py`, facade contract tests, caller-family tests, raw-container guardrail, and bypass-layer tests guard active replacement, enemy mirror sync, selected-target fan-out, no pending queue write, and no scheduled/listener conversion. | `implicit-events`; default lifecycle profile only when lifecycle/runtime wiring changes. | `buff_add_strategy(...)` / `LegacyBuffRuntimeFacade` remain the forced same-tick Buff / Debuff write boundary; old registry/template identity retained; `BuffRuntimeReadPort`, `RuntimeCommandPort`, listener broadcast, and scheduled publish remain separate layers. | Only reopen if P2-F guardrail, facade/caller tests, raw-container guardrail, bypass-layer tests, or validation expose a concrete same-tick write boundary regression. |
| P2-G direct simulator context helpers | `tests/simulator/test_migrated_p2g_direct_context_guardrail.py` and service-family tests cover Yuzuha tick/preload/next-character/report-state, enemy context, listener lookup, RNG service, and report-state representatives without introducing a universal context helper. | `implicit-events`; `calculator-reads` remains contrast evidence for RNG / crit-adjacent reader seams. | Tick, preload, char-data, enemy, listener, RNG, report-state, scheduled publish, runtime write, and formula snapshot boundaries stay service-specific. | Only reopen if P2-G guardrail or service-family focused tests name a selected root representative regression; do not reopen for generic `sim_instance` text or `.codex_worktrees/` hits alone. |

Closure decision: P2-D scheduled publish, P2-E dot runtime-state, P2-F same-tick facade write, and P2-G direct simulator services remain four different boundary families. Future PRDs should open a narrow blocker only when root-workspace source, focused tests, or validation profiles provide a concrete file / expression / behavior failure; otherwise P2-A through P2-G stay completed guarded-maintenance buckets.

### 2026-06-09 US-004 Validation Profile / Formula Readiness Gap Audit

本节只审计 `scripts/run_buff_refactor_validation.py` 当前 profile wiring 与 phase-3 formula readiness 缺口；不修改验证脚本，不新增 profile，不编辑 `Calculator.py`、`CalAnomaly.py` 或任何 live XLogic 行为。

#### Runner wiring snapshot

`BuffRefactorValidationRunner.build_steps()` 当前固定先跑 `tests/simulator/test_basic_simulator.py` 与 `tests/simulator/test_isolated_teams.py`，再按 `FOCUSED_PYTEST_PROFILES[typecheck_profile]` 追加 focused pytest，最后把 `TYPECHECK_PROFILES[typecheck_profile]` 与 `FOCUSED_MYPY_PROFILES[typecheck_profile]` 合并为 scoped mypy 目标。`DEFAULT_TYPECHECK_PROFILE` 仍是 `lifecycle`；`--mainloop` 只追加 `tests/test_simulator.py`，不会自动替代 profile-specific focused coverage。

| profile | current wiring | coverage this profile proves | formula-readiness limit |
| --- | --- | --- | --- |
| `lifecycle` (default) | 8 production / script mypy targets plus `test_buff_raw_container_guardrail.py` focused pytest and focused mypy. | Buff lifecycle / old-container guardrail smoke; useful when lifecycle or same-tick runtime write wiring changes. | It does not prove Calculator formula parity, CalAnomaly settled snapshot parity, scheduled publish ordering, or direct context branch behavior. |
| `implicit-events` | 50 production / script mypy targets, 39 focused pytest targets, and 38 focused mypy targets. | Shared planned-event, listener/runtime boundary, dot runtime, BuffAddStrategy, retained semantics, and P2-C through P2-G guardrail coverage. | It is the right broad gate for event/runtime maintenance, but it only carries formula-adjacent evidence indirectly; it must not be treated as permission to replace Calculator / CalAnomaly formulas. |
| `calculator-reads` | 16 typecheck targets, 6 focused pytest targets, and the same 6 focused mypy targets: `test_buff_attribute_reader.py`, `test_buff_raw_container_guardrail.py`, `test_migrated_am_ap_reader_guardrail.py`, `test_migrated_p2b_reader_guardrail.py`, `test_buff_attribute_state_sync.py`, `test_full_crit_event_adjacent_reader.py`. | Current reader seams, AM/AP + crit/impact migrated-source guardrails, read-then-writeback order, raw-container contrast, and full-crit event-adjacent behavior. | This is necessary but not sufficient for phase-3 formula replacement: it proves selected reader parity and migrated-file guardrails, not full damage / anomaly formula equivalence. |

#### Existing focused-test coverage map

| risk surface | existing coverage | current readiness decision |
| --- | --- | --- |
| Reader seams | `test_buff_attribute_reader.py`, `test_migrated_am_ap_reader_guardrail.py`, `test_migrated_p2b_reader_guardrail.py`, `test_buff_raw_container_guardrail.py`, plus `calculator-reads`. | Sufficient for current `BuffAttributeReader` helper families and migrated-source guardrails; not sufficient to delete `MultiplierData` or formula internals. |
| State-sync order | `test_buff_attribute_state_sync.py` and P2-A guardrails cover `simple_start(...) -> dy.count -> update_to_buff_0(...)` style read-then-writeback order. | Keep future helper work paired with order assertions; never replace only the read expression when `dy.count`, record fields, or `buff_0` identity are involved. |
| Scheduled publish order | `test_schedule_dispatch.py`, resource refresh dispatch tests, `test_cannon_rotor_dispatch.py`, `test_miyabi_core_skill_icefire_dispatch.py`, `test_yixuan_cinema1_dispatch.py`, Vivian / Yanagi / Hugo / Decibel dispatch tests, and `test_migrated_p2d_scheduled_publish_guardrail.py` under `implicit-events`. | P2-D remains guarded maintenance; dispatch adapter parity is not a formula-readiness blocker unless a later formula story changes event production or ordering. |
| Dot runtime state | `test_dot_runtime_initialization.py`, `test_dot_runtime_state_adapter.py`, Vivian dot / UpdateAnomaly focused tests, and `test_migrated_p2e_dot_runtime_guardrail.py` under `implicit-events`. | Runtime dot registration/removal remains separate from scheduled publish and formula snapshots; no phase-3 formula profile should absorb dot runtime writes. |
| Direct context services | P2-G focused tests cover Yuzuha tick/preload/next-character/report-state, enemy context, listener lookup, RNG service, report-state, and factory-backed preload contrast; `implicit-events` currently carries `test_migrated_p2g_direct_context_guardrail.py`. | Existing branch tests are service-specific evidence, while the shared profile only gates selected-symbol regressions; future formula parity work should not turn direct context services into a universal adapter backlog. |
| Formula-adjacent behavior | `test_full_crit_event_adjacent_reader.py`, `test_buff_attribute_reader.py`, `test_buff_attribute_state_sync.py`, `test_anomaly_handler_runtime_view.py`, `test_dot_runtime_initialization.py`, and the formula census rows for `Calculator.py`, `CalAnomaly.py`, `AnomalyBar.current_ndarray`. | Existing tests identify seams and retained snapshots. They do not yet form a full Calculator / CalAnomaly formula parity suite. |

#### Formula parity suite gaps before replacement

Before any phase-3 PRD replaces Calculator / CalAnomaly formula internals, the suite still needs explicit coverage for:

- `Calculator.py` formula-core parity across `MultiplierData`, `DynamicStatement`, static statement fields, active Buff view, enemy debuff view, and the named AM / AP / impact / crit helper families.
- `CalAnomaly.py` settled anomaly snapshot parity: `AnomalyBar.current_ndarray` shape `(1, 11)`, virtual level extraction, `MulData(...)`, Calculator multiplier calls, `final_multipliers`, `scaling_factor`, disorder / polarity / abloom subclasses, and element-specific anomaly behavior.
- Copied-output and anomaly-bar adjacency: Vivian / Yanagi copied anomaly payloads and `current_ndarray` usage must stay separated from scheduled publish, listener broadcast, dot runtime registration, and same-tick runtime writes.
- Behavior-sample criteria: a live registered-team main-loop consistency sample is required only when formula or live runtime semantics change; doc-only, guardrail-only, or profile-wiring-only stories should keep serial validation profiles as the gate.
- Rollback and non-goals: phase-3 formula PRDs must name retained `MultiplierData` / `MulData` responsibilities, the exact candidate files, and which old containers / dispatch / runtime / listener boundaries remain out of scope.

No new validation profile is wired in this story. If a later PRD introduces a `formula-parity` profile, its intended test set should be documented before wiring and should start from the existing `calculator-reads` focused tests plus new formula-specific pytest targets for Calculator formula parity, CalAnomaly settled snapshot parity, and anomaly `current_ndarray` / copied-output parity; the profile must also name scoped mypy targets before it is added to `run_buff_refactor_validation.py`.

#### US-004 readiness conclusion

- Current validation profiles are adequate for phase-2 guarded maintenance: `implicit-events` protects event/runtime/service boundaries and `calculator-reads` protects current reader seams and migrated-source guardrails.
- They are not yet a phase-3 formula replacement gate. Formula replacement must wait until the parity suite above exists and the PRD explicitly decides whether to wire a new profile or continue using `calculator-reads` plus focused formula tests.
- No new old-Buff coupling was discovered; `docs/旧Buff系统耦合审查结果.md` does not need a new entry for this audit.

### 2026-06-09 US-005 Formula Parity Suite Contract

本节定义 phase-3 公式替换前必须满足的 parity suite contract。本 story 只写 contract，不实现公式替换、不改 `Calculator.py`、`CalAnomaly.py`、`AnomalyBarClass.py`、handler、dispatch adapter、runtime port 或验证脚本。

#### Candidate input domains

| domain | candidate inputs that must vary | expected retained output / boundary | comparison policy | suite shape |
| --- | --- | --- | --- | --- |
| AM anomaly mastery | static AM, dynamic `field_anomaly_mastery`, dynamic `anomaly_mastery`, active Buff aggregation, empty / non-empty dynamic buff snapshot. | `Calculator.AnomalyMul.cal_am(...)` and `CalculatorBuffAttributeReader.read_anomaly_mastery(...)` stay numerically equivalent. | Float helper output uses exact equality when both paths call the same formula; otherwise `pytest.approx(abs=1e-9, rel=1e-9)`. No event or timeline mutation is allowed. | Focused unit characterization is enough unless the later PRD changes live damage / anomaly output. |
| AP anomaly proficiency | static AP, dynamic `field_anomaly_proficiency`, dynamic `anomaly_proficiency`, AP-to-count callsites, cap / floor behavior where XLogic writes `dy.count`. | `cal_ap(...)`, reader AP result, count writeback value, old `buff_0` identity, and `simple_start(...) -> dy.count -> update_to_buff_0(...)` order stay stable. | Helper value uses exact / `1e-9` float parity; count, cap, floor, branch selection, and state-sync order use exact equality. | Focused unit plus state-sync characterization; registered main-loop sample only if final output or registered Buff timeline changes. |
| Impact | static impact, dynamic impact fields, stun-related active Buff aggregation, representative low / normal / high impact values. | `Calculator.StunMul.cal_imp(...)`, `read_impact(...)`, converted count, and retained stun formula snapshot stay stable. | Float parity at `1e-9`; count conversion and old template sync order exact. Event count must remain unchanged. | Focused unit plus count/state-sync characterization. |
| Full crit rate | static crit rate, dynamic crit rate, field crit rate, `crit_rate_received_increase`, RNG / SkillNode trigger branches, event-adjacent full-crit samples. | Full crit includes received crit and remains distinct from personal crit rate; dispatch-adjacent branches keep current publish / no-publish behavior. | Numeric crit value exact / `1e-9`; RNG branch, scheduled event count, event type, target, priority, execute tick, and payload fields exact. | Focused reader and event-adjacent characterization; registered main-loop only if the later PRD changes live damage or publish timing. |
| Personal crit rate | static crit rate, dynamic crit rate, field crit rate, explicit absence of received-crit fields, aftershock / trigger state branches. | Personal crit rate excludes `crit_rate_received_increase`; resulting count / state writes keep existing cap and old identity semantics. | Numeric value exact / `1e-9`; received-crit exclusion, branch selection, cap, and state order exact. | Focused unit plus state-sync characterization. |
| Personal crit damage | static crit damage, dynamic crit damage, field crit damage, explicit absence of received-crit-damage fields, label-specific crit damage when relevant. | Personal crit damage excludes received crit damage; count conversion, exit behavior, and `simple_start(...)` ordering stay stable. | Numeric value exact / `1e-9`; cap, exit branch, old identity, and state-sync order exact. | Focused unit plus state-sync characterization. |
| Anomaly buildup | element type `0/1/2/3/4/5/6`, `anomaly_accumulation`, `hit_times`, `element_damage_percent`, AM, element buildup bonus, trigger buildup bonus, enemy anomaly resistance, element-specific resistance decrease. | `Calculator.AnomalyMul.cal_anomaly_buildup(...)` retains per-hit accumulation behavior and does not change scheduled publish, listener broadcast, or dot runtime registration. | `np.float64` buildup parity uses `pytest.approx(abs=1e-9, rel=1e-9)`; invalid element / trigger branches keep exact exception behavior. Event count and buff timeline exact. | Focused formula characterization first; registered main-loop sample only if buildup changes registered anomaly timing or output. |
| Anomaly damage ratio / settled snapshot | `AnomalyBar.current_ndarray` shape `(1, 11)`, virtual level, `MulData(...)`, Calculator anomaly snapshot order, `final_multipliers`, `scaling_factor`, element-specific anomaly damage constants. | `CalAnomaly` settled damage, snapshot shape, multiplier order, and scaling factor behavior remain stable. | Snapshot shape, column order, class selection, and copied metadata exact; intermediate floats use `1e-9`; final damage scalar uses `pytest.approx(abs=1e-6, rel=1e-9)` unless the legacy path rounds earlier. | Focused CalAnomaly characterization plus registered main-loop consistency when final damage output is changed. |
| Disorder / polarity disorder copied outputs | disorder, polarity disorder, abloom subclass selection, copied anomaly output payloads, source anomaly bar metadata, target enemy, schedule / handler fan-out. | Copied output fields, target fan-out, handler semantics, and publish-vs-runtime layering remain unchanged. | Event count, event type, target, payload field names, copied values, and relative order exact; final copied damage uses final-damage tolerance above. | Focused handler / copied-output characterization; registered main-loop sample required if a later PRD changes live disorder damage or registered event timeline. |
| Enemy debuff / active buff aggregation | `DynamicStatement`, `MultiplierData.get_buff_bonus()`, active Buff view, enemy dynamic debuffs, empty / single / stacked Buff snapshots, retained old containers. | Static statement fields, active Buff aggregation, enemy debuff aggregation, and retained compatibility snapshots stay equivalent before formula internals are moved. | Aggregated scalar fields exact / `1e-9`; set of active Buff keys, enemy debuff keys, timeline ticks, and old-container identity exact. | Focused aggregation characterization first; registered sample only when aggregation changes can affect live damage, anomaly timing, or Buff timeline. |

#### Cross-suite comparison policy

- Exact equality is required for event count, event type, target fan-out, payload keys, payload copied metadata, exception branch, Buff active / inactive timeline, old `buff_0` identity, state-sync order, and source-level no-new-boundary guardrails.
- Floating helper outputs should be exact when the candidate still delegates to the same legacy formula. When separate implementations compare independent float products, use `pytest.approx(abs=1e-9, rel=1e-9)` for intermediate multipliers and `pytest.approx(abs=1e-6, rel=1e-9)` for final damage output, unless an existing legacy rounding / truncation rule defines a stricter expected value.
- Rounding, floors, caps, and integer count conversions must assert the post-rounding value exactly and also keep representative boundary inputs around zero, cap, high, and fractional values.
- Damage-output comparisons must include both the numeric output and the contextual invariants that make the number meaningful: event count, schedule / handler order, Buff timeline, active Buff aggregation, enemy debuff aggregation, and copied anomaly metadata.

#### Unit characterization vs registered main-loop samples

| suite part | focused unit characterization | registered main-loop consistency sample |
| --- | --- | --- |
| AM / AP / impact / crit helper parity | Required first; use direct Calculator / reader fixtures and representative state-sync callsites. | Not required for doc-only, reader-only, or guardrail-only stories. Required only when a later formula change can alter registered damage, stun, anomaly, Buff timeline, or event publish timing. |
| Anomaly buildup and `CalAnomaly` settled snapshot | Required before editing formula internals; fixtures must lock element branches, snapshot shape, virtual level, multiplier order, and copied metadata. | Required when final anomaly / disorder damage or registered anomaly timing changes. |
| Enemy debuff / active Buff aggregation | Required before moving `DynamicStatement` / `MultiplierData.get_buff_bonus()` responsibility; cover empty, single, stacked, and enemy-debuff inputs. | Required when aggregation movement can alter a registered team's damage output or Buff timeline. |
| Validation profile wiring | A later story may add focused pytest / scoped mypy targets after this contract is backed by tests. | Profile wiring alone does not require main-loop samples; live semantic formula changes do. |

#### US-005 readiness conclusion

- The formula parity suite contract now names candidate input domains, output invariants, comparison policy, and the boundary between focused characterization and registered main-loop samples.
- `calculator-reads` remains the current validation entrypoint for this doc-only story. A future `formula-parity` profile must be introduced only after the focused Calculator / CalAnomaly / copied-output tests are implemented and scoped mypy targets are named.
- No phase-3 formula replacement, validation-profile wiring, old-container deletion, dispatch rewrite, listener rewrite, runtime-write facade change, or broad XLogic migration is performed in this story.
- No new old-Buff coupling was discovered; `docs/旧Buff系统耦合审查结果.md` does not need a new entry for this contract.

### 2026-06-09 US-006 MultiplierData / DynamicStatement Snapshot Characterization

本节只记录 `MultiplierData.get_buff_bonus(...)` 与 `DynamicStatement` 的 focused characterization，不修改 `Calculator.py` 公式、不删除 `MultiplierData` cache，也不扩展 `BuffAttributeReader` helper family。

| surface | characterization evidence | retained compatibility / non-goal |
| --- | --- | --- |
| `MultiplierData.get_buff_bonus(...)` fan-in | `tests/simulator/test_buff_attribute_reader.py::test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot` 覆盖 no-buff / no-debuff baseline 与 active Buff + enemy debuff aggregation；断言传给 `cal_buff_total_bonus(...)` 的 `enabled_buff` 仍是角色 active Buff view 加 `enemy.dynamic.dynamic_debuff_list`，并保留 `sim_instance` 与 `char_name`。 | `_calculate_dynamic_statement(...)` 与 `cal_buff_total_bonus(...)` 仍是当前聚合入口；本 story 不移动聚合职责、不改 cache key、不替换公式输入路径。 |
| `DynamicStatement` translated snapshot fields | 同一 focused test 断言中文动态字段继续翻译到 `field_anomaly_mastery`、`anomaly_mastery`、`field_anomaly_proficiency`、`anomaly_proficiency`，且未出现的字段保持默认 `0.0`。 | `DynamicStatement` 仍是 retained formula snapshot object；后续 phase-3 必须先有 parity suite 才能移动或替换它。 |
| `BuffAttributeReader` seam separation | 本 story 复用现有 reader test module，但 characterization 直接锁定 legacy `MultiplierData` snapshot，不新增 reader 方法。 | `CalculatorBuffAttributeReader` 继续只是当前 helper parity seam；reader seam evidence 不能单独证明 `MultiplierData` / `DynamicStatement` 可删除。 |

US-006 结论：当前证据把 active Buff view、enemy debuff view 与 translated dynamic fields 纳入 `calculator-reads` focused coverage；phase-3 formula replacement 仍需后续 story 继续补齐 Calculator attribute formula boundaries、CalAnomaly snapshot boundaries、copied-output reads 与 go / no-go decision。

### 2026-06-09 US-007 Calculator Attribute Formula Boundary Characterization

本节只记录 `Calculator.py` attribute formula boundary 的 focused characterization，不改 `Calculator.py` 公式、不移动 `MultiplierData` / `DynamicStatement` 职责，也不把 P2-A / P2-B reader helper parity 解释为公式可删除证据。

| formula family | characterization evidence | retained compatibility / non-goal |
| --- | --- | --- |
| AM / AP / impact | `tests/simulator/test_buff_attribute_reader.py::test_calculator_attribute_formula_boundaries_remain_retained_compatibility` 直接调用 `Calculator.AnomalyMul.cal_am(...)`、`cal_ap(...)`、`Calculator.StunMul.cal_imp(...)`，并与 `CalculatorBuffAttributeReader` 读口保持同一组 snapshot 输入的数值等价。 | `Calculator.py` formula internals、`MultiplierData` cache、static / dynamic statement fields 与 reader seam 全部保留；本 story 不抽新 helper、不替换公式。 |
| full crit rate | 同一 focused test 锁定 `Calculator.RegularMul.cal_crit_rate(...) = static crit + dynamic crit + field crit + crit_rate_received_increase`。 | Full crit rate 继续包含 received crit；event-adjacent P2-B 证据仍只是兼容 / guardrail 证据，不代表可删除 full crit formula。 |
| personal crit rate / damage | 同一 focused test 锁定 `cal_personal_crit_rate(...)` 与 `cal_personal_crit_dmg(...)` 不计入 received crit / received crit damage 字段，同时保留动态 snapshot 中的 received 字段可见性。 | Personal crit reader parity 继续排除 received fields；后续 phase-3 必须先补齐 formula parity suite 与 go / no-go decision，不能从 P2-A / P2-B migrated-file guardrail 直接推导公式删除。 |

US-007 结论：`calculator-reads` 现在覆盖 `MultiplierData` / `DynamicStatement` fan-in 与六个 Calculator attribute formula helper 的 focused boundary characterization；它仍不是完整 Calculator / CalAnomaly formula replacement gate。
