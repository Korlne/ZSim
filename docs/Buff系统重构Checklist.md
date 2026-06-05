# Buff系统重构Checklist

## 使用规则

- 本文档是 Buff 重构的总 checklist。
- 每个 `scripts/ralph/prd.json` 全部完成后，必须更新本文档。
- 更新时要同时标记“已完成项”“进行中项”“阻塞项”。
- 任何新增耦合块、验证要求、删除计划，都要先落本文档，再进入下一轮 PRD。

## 阶段 0：重规划与基线

- [x] 回到 `main` 分支重新规划。
- [x] 保留 `scripts/ralph` 和 `scripts/ralph/prompts`。
- [x] 重写总计划文档。
- [x] 建立旧 Buff 系统耦合审查结果文档。
- [x] 建立下阶段计划草稿文档。
- [x] 重置 Ralph loop 的 PRD 基线。

## 阶段 1：基础设施解耦

- [x] 完成阶段 1 的调查型 PRD，产出生命周期、事件模型、Calculator seam、验证入口与交接包。
- [x] 为 Buff runtime 建立抽象接口与适配层。
- [ ] 隔离 `exist_buff_dict`、`DYNAMIC_BUFF_DICT`、`LOADING_BUFF_DICT`。
- [ ] 建立事件驱动基础设施边界，明确事件对象、事件上下文、事件分发入口与订阅入口。
- [ ] 让 `Simulator` 不再直接控制旧 Buff 运行细节。
- [ ] 让 `ScheduledEvent` 改为依赖 Buff runtime facade。
- [ ] 让 `Update_Buff` 改为依赖 Buff runtime facade。
- [ ] 为 `Calculator` 建立属性读取接口，隔离 `MultiplierData` 直读。
- [ ] 为基础设施解耦新增单元测试。
- [ ] 为事件分发边界与事件顺序新增单元测试。
- [x] 为主循环一致性与性能验证补齐真实命令入口。

## 阶段 2：XLogic 全量分析与复用收敛

- [ ] 输出 XLogic 全量分类结果。
- [ ] 输出可复用方法清单。
- [ ] 输出可复用记录对象清单。
- [ ] 输出可复用 stat reader / event adapter / state sync 模式清单。
- [ ] 输出可复用事件类型 / 事件处理器 / 事件订阅模式清单。
- [ ] 明确 XLogic 替换优先级。
- [ ] 明确高风险耦合桶和回归风险点。

## 阶段 3：XLogic 全面替换

- [ ] 替换属性读取类 XLogic。
- [ ] 替换事件触发类 XLogic。
- [ ] 替换 count 写回类 XLogic。
- [ ] 替换异常附带 debuff 类 XLogic。
- [ ] 替换直接依赖 `sim_instance` 服务定位的 XLogic。
- [ ] 将旧触发链收口到统一事件驱动分发链路。
- [ ] 每个切片都有对应单元测试。
- [ ] 每个切片都有主循环一致性验证。

## 阶段 4：旧 Buff 残余删除

- [ ] 删除不再使用的旧 Buff 入口。
- [ ] 删除不再使用的旧适配器。
- [ ] 删除旧 `MultiplierData` 直连路径。
- [ ] 删除旧容器同步残余逻辑。
- [ ] 删除无用文档和无用兼容说明。

## 阶段 5：一致性与性能收口

- [ ] 新旧 Buff 系统 `main_loop` 结果一致。
- [ ] 对应角色配队 APL 结果一致。
- [ ] 关键 Buff 生效时序一致。
- [ ] 关键事件分发顺序一致。
- [ ] 异常 / debuff 关键结果一致。
- [ ] 总耗时优于旧系统。
- [ ] 事件分发热点性能优于旧系统。
- [ ] 输出最终验证结论。

## 每个 PRD 完成后的必做项

- [ ] 更新本 checklist 的状态。
- [ ] 更新 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)。
- [ ] 回写 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md) 中新增或已消解的耦合项。
- [ ] 记录本轮验证命令与结果。
- [ ] 确认下一轮 PRD 的调查范围和非目标。

## 本轮调查 PRD 收口状态（2026-06-05）

- [x] 更新本 checklist 的状态。
- [x] 更新 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)。
- [x] 回写 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md) 中新增或已消解的耦合项，并补入验证入口与交接要求。
- [x] 记录本轮验证命令与结果。
- [x] 确认下一轮 PRD 的实现范围和非目标。

## 本轮阶段 1 实现基线 PRD 收口状态（2026-06-05）

- [x] `ScheduleDispatchPort` 已落地，`SchedulePreload` 与 `QuickAssistSystem` 已改经 dispatch gateway。
- [x] `BuffRuntimeReadPort` / `EventContext.buff_runtime_view` 已落地，`anomaly`、`abloom`、`disorder`、`polarity_disorder` 已改走 runtime view。
- [x] `scripts/run_buff_main_loop_consistency.py` 与 `scripts/run_buff_runtime_benchmark.py` 已提供真实 CLI 入口与稳定输出字段约定。
- [x] 更新 [Buff重构下阶段计划草稿.md](./Buff重构下阶段计划草稿.md)、[Buff重构替换说明.md](./Buff重构替换说明.md) 与 [旧Buff系统耦合审查结果.md](./旧Buff系统耦合审查结果.md)，同步阶段 1 当前基线。
- [x] `UpdateAnomaly` 计划事件发布路径与 `BattleEventListener` 中 `AliceDotTriggerListener` 样本已改经 dispatch gateway，当前不再把这两条入口列为阶段 1 主缺口。
- [x] 高风险 `SkillEventHandler` 已把 `Calculator` / `update_anomaly()` 的主 Buff 读口迁到 runtime view。
- [ ] 代表性 `BuffXLogic` / `PolarizedAssaultEvent` 计划事件生产者、其余 `BattleEventListener` 旁路入口与同 tick runtime write facade 仍待后续阶段 1 切片推进。

## 当前默认下一步

- [ ] 启动下一轮仍属于“阶段 1：基础设施解耦”的实现型 PRD，优先收口代表性 `BuffXLogic` / `PolarizedAssaultEvent` 等剩余计划事件生产者的旧直写入口，并保持 `event_list`、`listener_manager.broadcast_event()` 与 runtime command 三层语义分离。
- [ ] 在 `SkillEventHandler` 已迁到 runtime view 主读口的基础上，继续把 `ScheduleBuffSettle()`、`update_anomaly()` 等同 tick 写边界收口到最小 write facade / command port，不扩到 `Calculator` 全量迁移或旧容器删除。
- [ ] 仅在 live simulator 真正消费 `config.buff_runtime.mode` 后，再把一致性 / benchmark 命令升级为真实 runtime switch 证据。
