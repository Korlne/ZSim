# Buff公式候选与测试目标清单

更新时间：2026-06-13 16:00 +08:00

本清单服务于 Phase 3 公式等价测试设计。当前故事只建立候选面和测试目标证据，不替换 `Calculator.py`、`CalAnomaly.py`、复制异常 / 紊乱输出公式，也不改变 `ScheduleDispatchPort`、`RuntimeCommandPort` 或旧容器兼容路径。

## 扫描边界

- 根工作区扫描排除：`.codex_worktrees/`、`__pycache__/`、`archive/`、`.git/`、生成日志、Ralph 历史归档和历史重复副本。
- 文档预检：`rg --files docs | rg "Buff|XLogic|Checklist|替换|下阶段|耦合|复用|分类|公式|重构"`。
- 源码 / 测试预检：`rg -n -S -g '!**/.codex_worktrees/**' -g '!**/__pycache__/**' -g '!**/archive/**' -g '!**/.git/**' 'MultiplierData|DynamicStatement|CalAnomaly|AnomalyBar\.current_ndarray|current_ndarray|copied.*(anomaly|disorder)|enemy.*dynamic|buff_attribute_reader|calculator-reads|AM|AP|crit|impact' zsim tests scripts docs`。
- US-002 根工作区预检：`rg -n --glob '!.codex_worktrees/**' --glob '!archive/**' --glob '!scripts/ralph/archive/**' --glob '!scripts/ralph/run-logs/**' --glob '!**/*.log' 'RegularMul|AnomalyMul|StunMul|CalAnomaly|CalDisorder|CalPolarityDisorder|CalAbloom|current_ndarray|AnomalyBar' tests/simulator/test_buff_attribute_reader.py tests/simulator zsim/sim_progress/ScheduledEvent zsim/sim_progress/anomaly_bar docs scripts/run_buff_refactor_validation.py`。
- CodeGraph 证据需要按根工作区路径二次筛选；`.codex_worktrees/` 下的重复定义只作为历史导航噪音，不进入候选清单。

## 候选域地图

| 候选域 | 源文件 / 符号 | 已有 focused tests | 缺口 / 后续测试目标 | 验证入口 |
| --- | --- | --- | --- | --- |
| Calculator AM/AP/impact/crit/直伤/失衡公式 | `zsim/sim_progress/ScheduledEvent/Calculator.py`：`CalculatorBuffAttributeReader.read_anomaly_mastery()`、`read_anomaly_proficiency()`、`read_impact()`、`read_full_crit_rate()`、`read_personal_crit_rate()`、`read_personal_crit_damage()`；`Calculator.RegularMul.cal_base_dmg()`、`cal_base_attr()`、`cal_dmg_bonus()`、`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()`、`cal_sheer_dmg_bonus()`；`Calculator.AnomalyMul.cal_am()`、`cal_anomaly_buildup()`、`cal_base_damage()`、`cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ap()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()`；`Calculator.StunMul.cal_imp()`、`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_cal_am_retained_multiplier_data_oracle_rows()`、`test_cal_ap_retained_multiplier_data_oracle_rows()`、`test_cal_imp_retained_multiplier_data_oracle_rows()`、`test_stun_array_output_contract_preserves_field_order_dtype_and_product()`、`test_regular_mul_array_outputs_preserve_field_order_dtype_and_crit_split()`、`test_calculator_regular_mul_branch_matrix_characterizes_selected_methods()`、`test_regular_mul_retained_sheer_base_attr_requires_char_instance_conversion_rate()`、`test_calculator_am_ap_impact_formula_boundaries_remain_retained_compatibility()`、`test_calculator_attribute_formula_boundaries_remain_retained_compatibility()`；`tests/simulator/test_migrated_am_ap_reader_guardrail.py`；`tests/simulator/test_migrated_p2b_reader_guardrail.py`；`tests/simulator/test_full_crit_event_adjacent_reader.py`。 | AM/AP/impact 已完成 bounded implementation；Stun array、RegularMul arrays 与 selected RegularMul branch matrix 已完成 characterization / retained oracle；RegularMul sheer conversion 已有 retained runtime-dependency oracle，但 reader-built `_CalculatorReadSnapshot` contract 和 registered-route sample 条件仍使 production proposal 保持 No-Go。后续仍需从 copied-output handler/report payload parity、registered-team behavior sample eligibility、remaining RegularMul / retained-only sheer follow-up、`StunMul.get_stun_array()` follow-up 或 P2-A through P2-G guarded maintenance 中选择 exact bounded characterization slice；不得外推为 broad `Calculator.py` / `CalAnomaly.py` rewrite。 | `uv run pytest tests/simulator/test_buff_attribute_reader.py -q`；`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity`；retained reader / guardrail gate 为 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`；触达 copied-output / event-runtime 分层时追加 `implicit-events`。 |
| `MultiplierData` / `DynamicStatement` 动态快照 | `zsim/sim_progress/ScheduledEvent/Calculator.py`：`_calculate_dynamic_statement()`、`MultiplierData.__new__()`、`MultiplierData.__init__()`、`MultiplierData.get_buff_bonus()`、`MultiplierData.StaticStatement`、`MultiplierData.DynamicStatement.__read_dynamic_statement()`。`CalAnomaly.py` 中 `MulData` 是 `MultiplierData` 别名。 | `tests/simulator/test_buff_attribute_reader.py`：`test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot()`、`test_multiplier_data_dynamic_statement_translates_python_attr_names()`、`test_multiplier_data_dynamic_statement_rejects_invalid_effect_key()`、`test_multiplier_data_cache_key_stability_and_reset_isolation()`、AM/AP/impact/crit reader parity tests。 | `buff_effect_trans.json` key 翻译、非法 key 报错、缓存 key 稳定性和 cache reset isolation 已有 focused characterization；enemy debuff/dot 参与 cache key 由 enemy dynamic reads 行继续保留后续专项。 | 同 `formula-parity` profile；后续若拆分可提取 `test_multiplier_data_formula_snapshot.py`。 |
| `CalAnomaly` / `CalDisorder` / `CalAbloom` 异常伤害公式 | `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`：`CalAnomaly.__init__()`、`cal_k_level()`、`cal_active_crit()`、`cal_def_mul()`、`set_final_multipliers()`、`cal_anomaly_dmg()`；`CalDisorder.cal_disorder_base_dmg()`、`cal_disorder_extra_mul()`、`cal_disorder_stun()`；`CalPolarityDisorder.__init__()`；`CalAbloom.__init__()`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_cal_anomaly_level_clamp_remains_retained_lookup()`、`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()`、`test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()`、`test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()`、`test_cal_polarity_disorder_formula_inputs_and_payload_boundary()`、`test_cal_abloom_formula_inputs_and_fixture_blockers()`；`tests/simulator/test_anomaly_handler_runtime_view.py` covers handler runtime-view reads without legacy dynamic container. | `CalAnomaly.cal_k_level()` 已锁定 level-boundary retained lookup：`-1 -> 0.0` 并记录低等级日志、`40 -> 1.6610` 且不记录日志、`61 -> 2.0` 并记录高等级日志；`CalAnomaly` 主动暴击、防御、抗性、易伤、失衡易伤、特殊乘区输入、`set_final_multipliers()` 顺序、snapshot impact / stun ratio 处理与 `scaling_factor` 位置已有 retained `MulData` / settled snapshot oracle；`CalDisorder` base damage remaining-tick / floor 分支、extra multiplier 和 stun 公式已有 element-type oracle；`CalPolarityDisorder` ratio + Yanagi AP additional damage 输入已有 deterministic oracle；`CalAbloom` copied `current_ndarray`、`anomaly_dmg_ratio` 与 inherited final multiplier vector 已有 deterministic oracle。 | `uv run pytest tests/simulator/test_buff_attribute_reader.py -q`；异常 handler 变更时追加 `uv run pytest tests/simulator/test_anomaly_handler_runtime_view.py -q`。 |
| `AnomalyBar.current_ndarray` 快照输入 | `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`：`current_ndarray` 字段、`update_snap_shot()`、`change_info_cause_active()`、`reset_current_info_cause_output()`、`reset_myself()`、`create_new_from_existing()`、`__deepcopy__()`；`zsim/sim_progress/ScheduledEvent/CalAnomaly.py` 在构造时读取 `current_ndarray`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility()`、`test_anomaly_bar_current_ndarray_reset_deepcopy_and_shallow_copy_matrix()`、`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()`；`tests/simulator/test_migrated_am_ap_reader_guardrail.py` prevents legacy anomaly reads in migrated AM/AP files. | 字段级快照矩阵已覆盖 11 列字段名、有效 / 无效积蓄、满条结算、复制输出 active_by 覆盖、`create_new_from_existing()` 浅拷贝 alias、`__deepcopy__()` 非 alias、`reset_current_info_cause_output()` / `reset_myself()` 保留 `(1, 1)` 重置形状；仍缺 `UpdateAnomaly.py` 写入路径字段矩阵。 | `test_buff_attribute_reader.py` 当前是最小入口；涉及 handler 时追加 `test_anomaly_handler_runtime_view.py`。 |
| 复制异常 / 紊乱输出 | `zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`：`NewAnomaly`、`Disorder`、`PolarityDisorder`；`zsim/sim_progress/ScheduledEvent/CalAnomaly.py`：`CalDisorder`、`CalPolarityDisorder`、`CalAbloom`；`event_handlers/handlers/anomaly.py` 通过 `CalAnomaly` / copied object 报告输出。 | `tests/simulator/test_buff_attribute_reader.py` copied snapshot compatibility tests、`test_new_anomaly_spawn_output_copies_active_payload_without_publish()`、`test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()`、`test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()`、`test_cal_polarity_disorder_formula_inputs_and_payload_boundary()`、`test_cal_abloom_formula_inputs_and_fixture_blockers()`；`tests/simulator/test_anomaly_handler_runtime_view.py` handler runtime-view and copied-output report payload tests。 | `NewAnomaly` mode 0 copied payload fields、`current_effective_anomaly` / `current_ndarray` settlement copy、duration fields、`active_by` and no listener publish are now locked；`Disorder` / `PolarityDisorder` copied formula inputs and listener-facing payload fields are now locked；`CalDisorder` formula 输入和 copied payload sentinel 已分离；`CalPolarityDisorder` copied payload boundary、polarity ratio、additional AP ratio 与 Yanagi AP 输入已有 deterministic oracle；`CalAbloom` formula 输入与 output-only sentinel 字段已分离；`NewAnomaly`、`Disorder`、`PolarityDisorder` 与 `DirgeOfDestinyAnomaly` handler report payload parity 已由 US-006 锁定（tick / skill_tag / element_type / damage / stun / buildup / status / UUID），并保持 listener broadcast、scheduled publish、dot runtime 与 RuntimeCommandPort 分层。 | `test_buff_attribute_reader.py` + `test_update_anomaly_dispatch.py` + `test_anomaly_handler_runtime_view.py`；触达 event/runtime 分层时追加 `implicit-events`。 |
| enemy dynamic reads | `Calculator.MultiplierData.__new__()` 读取 `enemy.dynamic.dynamic_debuff_list` / `dynamic_dot_list` 参与缓存；`_calculate_dynamic_statement()` / `MultiplierData.get_buff_bonus()` 读取 `enemy.dynamic.dynamic_debuff_list`；`CalculatorBuffAttributeReader._build_statements()` 复用同一聚合入口；`CalAnomaly.py` 通过 `MulData` 读取 enemy dynamic 与结算快照。 | `tests/simulator/test_buff_attribute_reader.py`：`test_enemy_dynamic_debuff_reads_feed_old_and_reader_formula_snapshots()` 覆盖空敌方状态、单个 enemy debuff、堆叠 enemy debuff 和 enemy dot 非聚合边界；`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()` 记录异常结算路径携带 enemy dynamic lists。另有 `test_enemy_context_direct_helpers.py`、`test_anomaly_handler_runtime_view.py`、`test_buff_attribute_state_sync.py`。 | 公式级 enemy debuff 聚合与 anomaly-state read family 已有 focused characterization；仍缺 `AnomalyBar.__get_duration_enemy_buffs()` 的 runtime view / legacy dynamic duration 专项矩阵，以及 dot/freez-like Load/Schedule continuation 的事件路由专项，不在本 PRD 替换。 | `calculator-reads` profile；若触及 direct enemy context，再追加 `test_enemy_context_direct_helpers.py`。 |
| 已迁移 reader seams | `CalculatorBuffAttributeReader`、`create_anomaly_attribute_read_context()` 及迁移后的 XLogic callsites：AM/AP、impact、full crit、personal crit、personal crit damage、direct context helpers。 | `tests/simulator/test_buff_attribute_reader.py`；`tests/simulator/test_full_crit_event_adjacent_reader.py`；`tests/simulator/test_migrated_am_ap_reader_guardrail.py`；`tests/simulator/test_migrated_p2b_reader_guardrail.py`；`tests/simulator/test_migrated_p2g_direct_context_guardrail.py`。 | 还缺统一 formula parity suite profile；后续故事应先新增 fixture / oracle 层，再考虑生产替换。 | `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`。 |

## 当前最小验证入口

- 单文件 focused：`uv run pytest tests/simulator/test_buff_attribute_reader.py -q`。
- Phase-3 oracle gap closure profile：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity`，当前最小 pytest 目标为 `test_buff_attribute_reader.py`。
- 保留的 broader reader seam profile：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`，覆盖 `test_buff_attribute_reader.py`、`test_buff_raw_container_guardrail.py`、`test_migrated_am_ap_reader_guardrail.py`、`test_migrated_p2b_reader_guardrail.py`、`test_buff_attribute_state_sync.py`、`test_full_crit_event_adjacent_reader.py`。

## US-014 formula-parity validation profile 决策

结论：Go，新增窄 `formula-parity` validation profile，但它只代表当前 Phase 3 characterization / parity fixture 最小门禁，不授权生产公式替换、删除 retained formula snapshots、扩大 runtime write facade 或替代 `calculator-reads`。

新增 profile 的 focused pytest 目标：

- `tests/simulator/test_buff_attribute_reader.py`

新增 profile 的 scoped mypy 目标：

- `zsim/sim_progress/ScheduledEvent/Calculator.py`
- `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`
- `zsim/sim_progress/anomaly_bar/__init__.py`
- `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`
- `zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`
- `zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py`
- `zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py`
- `scripts/run_buff_refactor_validation.py`
- `tests/simulator/test_buff_attribute_reader.py`

`calculator-reads` 仍保留为活跃 gate，用来覆盖迁移 reader seam、raw container guardrail、AM/AP guardrail、P2-B guardrail、state sync 与 full-crit event-adjacent reader：

- focused pytest / mypy：`tests/simulator/test_buff_attribute_reader.py`、`tests/simulator/test_buff_raw_container_guardrail.py`、`tests/simulator/test_migrated_am_ap_reader_guardrail.py`、`tests/simulator/test_migrated_p2b_reader_guardrail.py`、`tests/simulator/test_buff_attribute_state_sync.py`、`tests/simulator/test_full_crit_event_adjacent_reader.py`。
- scoped mypy source：`Calculator.py`、P2-A / P2-B reader callsites、`CannonRotor.py`、`TimeweaverDisorderDmgMul.py` 与 `scripts/run_buff_refactor_validation.py`，以 `scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` 的当前配置为准。

仍然阻塞 production formula replacement 的缺口：

- `RegularMul` / `AnomalyMul` / `StunMul` 还需要更完整的表驱动公式 oracle 与边界组合快照。
- `CalAbloom` deterministic formula oracle 已补齐；copied-output report payload parity 已由 US-006 关闭；`CalPolarityDisorder` / `CalAbloom` 现有 oracle 仍未授权 production formula replacement。
- `AnomalyBar.current_ndarray` 仍缺字段级 reset / deepcopy / update path 矩阵。
- registered-team main-loop sample 只在实际 production formula、Buff timeline 或 scheduled event semantics 改动时运行；当前 validation wiring 不需要新增注册队伍样本。

## US-016 final serial validation / production formula Go-No-Go

结论：No-Go。US-016 serial validation 证明当前 characterization surface、`formula-parity` profile、retained `calculator-reads` gate、event-adjacent `implicit-events` gate 与默认 lifecycle gate 可以串行通过；它没有消除 production formula replacement 前必须具备的 deterministic oracle、copied-output payload parity、`AnomalyBar.current_ndarray` 字段矩阵、registered behavior sample 条件和 rollback plan 缺口。

验证证据：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py -q` passed：`60 passed`。
- `uv run pytest tests/simulator/test_vivian_core_passive_trigger_dispatch.py tests/simulator/test_vivian_cinema6_trigger_dispatch.py -q` passed：`3 passed`。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `60 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `160 passed` / mypy `22 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed：base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py` passed：base `2 passed` / isolated teams `3 passed` / focused lifecycle `18 passed` / mypy `9 source files` clean。

下一默认 PRD 不能直接替换 `Calculator.py`、`CalAnomaly.py` 或 copied-output 生产公式。它应先做 phase-3 formula oracle gap closure / deterministic parity matrix，最小候选包括：

- `Calculator.RegularMul` / `Calculator.AnomalyMul` / `Calculator.StunMul` 表驱动公式 oracle 与边界组合。
- `CalAbloom` deterministic formula oracle 已可作为前置证据；`CalPolarityDisorder` / `CalAbloom` 后续仅在 copied-output report parity 或 production replacement gate 中继续使用本轮 oracle。
- `CopyAnomalyForOutput.py` / `UpdateAnomaly.py` report payload parity 与 listener-facing fields。
- `AnomalyBar.current_ndarray` reset / deepcopy / update path 字段矩阵。
- registered-team sample trigger 条件、rollback plan、retained `formula-parity` / `calculator-reads` / `implicit-events` gates 和明确 non-goals。

## US-026 final handoff / production formula Go-No-Go

结论：No-Go。US-025 已证明当前 formula-oracle PRD 的 serial gates 全部通过，但 US-026 只更新 handoff docs、PRD 状态与 Ralph 记录；没有改 `Calculator.py`、`CalAnomaly.py`、copied-output source、tests 或 `scripts/run_buff_refactor_validation.py`，因此本 story 不重跑 `formula-parity` 或 mypy。当前没有单个 production formula domain 获得替换许可。

US-025 复验记录：

- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `95 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `195 passed` / mypy `22 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed：base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `88 source files` clean。

仍阻塞 production formula replacement 的 exact blockers：

- `Calculator.AnomalyMul.cal_res_pen()` 已由 US-003 补齐 deterministic oracle cases：正值火属性抗穿、默认零值、电 / 霜 element-specific 读口（`element_type=5` 读取 `ice_res_pen_increase`，不吸收非匹配或全局字段）。这只关闭该 helper 的 oracle blocker，不授权删除 retained helper 或生产公式替换。
- `Calculator.AnomalyMul.anomaly_snapshot` vector assembly 已由 US-004 补齐 expected vector cases：默认 / no-bonus 物理输入、非默认电属性 dynamic-field 输入、9-slot field order，并证明它与 copied-output `AnomalyBar.current_ndarray` 的 1x11 payload shape / mutation 语义分离。这只关闭 vector assembly oracle blocker，不授权删除 retained helper 或生产公式替换。
- `CalAnomaly.cal_k_level()` clamp 已由 US-005 补齐 level-boundary oracle cases：`-1` 记录低等级日志并 clamp 到 `0 -> 0.0`，`40` 使用 retained lookup `1.6610` 且不记录日志，`61` 记录高等级日志并 clamp 到 `60 -> 2.0`。这只关闭 clamp oracle blocker，不授权替换 `CalAnomaly.py` 生产公式。
- copied-output handler/report payload parity 已由 US-006 单独覆盖 `CopyAnomalyForOutput.py`、`UpdateAnomaly.spawn_output(...)`、anomaly handler report payload 和 listener-facing fields；该证据仍不能授权生产替换。
- registered-team behavior sample 只在未来 production semantic diff 且真实注册队伍可触达目标 route 时运行；不为了 replacement proposal 创建 validation-only team。
- Rollback 仍必须保留 `MultiplierData` / `MulData` / `DynamicStatement`、`AnomalyBar.current_ndarray`、copied-output constructors、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、old containers 和 legacy `buff_add()` / `KickOutBuff()`。

下一默认 PRD 应是 phase-3 replacement blocker closure / bounded-domain eligibility decision。当前 PRD 内下一最小切片转向 registered-route behavior sample eligibility；完成后再用本清单复核是否可以选择单一 bounded formula domain 进入 production replacement proposal。若上述 blockers 仍未关闭，继续 characterization，不提交 production formula replacement。

## Current US-009 final bounded implementation handoff

结论：Implemented。`Calculator.AnomalyMul.cal_res_pen()` 已完成 behavior-preserving bounded selector extraction：public `cal_res_pen(data)` 保留 `SkillNode` assertion 和 caller path，元素分支选择移入 private `_select_res_pen_for_element(...)`。本 handoff 未回滚、未标记 partially blocked，也未授权 broad `Calculator.py` / `CalAnomaly.py` rewrite 或 retained compatibility 删除。

Final validation evidence：

- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `116 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `216 passed` / mypy `22 source files` clean。
- `implicit-events` skipped：current final story 只改 handoff / Ralph artifacts，且该 implementation PRD 没有在最终 story 中触达 copied-output、event-adjacent、dispatch、listener、dot runtime 或 same-tick runtime-write files/tests。
- 默认 `uv run python scripts/run_buff_refactor_validation.py` skipped：未触达 lifecycle container、runtime write path 或 validation-runner behavior。

| Candidate / boundary | Current US-009 status | Next rule |
| --- | --- | --- |
| `Calculator.AnomalyMul.cal_res_pen()` | Implemented as bounded selector extraction. | 不作为下一默认 PRD 重开目标；只有 focused regression、validation failure 或明确语义 follow-up 才重开。 |
| `Calculator.AnomalyMul.anomaly_snapshot` | Supporting retained vector-order / snapshot-shape evidence. | 可作为后续 candidate evidence，但不得在无新 PRD 证据时扩成第二 production domain。 |
| `CalAnomaly.cal_k_level()` | Supporting retained clamp / lookup evidence. | 保留 below / normal / above-boundary clamp 与日志语义；不作为 `cal_res_pen()` rollback 的一部分。 |
| Copied-output handler/report payload parity | Supporting event-adjacent compatibility evidence. | 后续触达 copied-output / handler / listener 字段时追加 `implicit-events`；不合并 scheduled publish、listener broadcast、dot runtime 和 same-tick runtime writes。 |
| Retained compatibility | Must stay intact. | 保留 `MultiplierData`、`MulData`、`DynamicStatement`、`AnomalyBar.current_ndarray`、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade` 与 P2-A through P2-G guarded maintenance。 |

Next default PRD：Phase-3 next-candidate selection / oracle-gap closure。下一轮从 formula/copy-output/registered-route pool 中选择一个 exact bounded candidate，先定义 focused pytest、scoped mypy、rollback、registered sample 条件与 retained validation gates；不得默认重开已完成的 `cal_res_pen()` selector extraction。

## Current implementation PRD US-007 AM/AP/impact bounded implementation handoff

结论：Implemented。AM/AP/impact scalar helper-family 的 bounded implementation 已完成：`Calculator.AnomalyMul.cal_am()` 保持已 helper-backed baseline，`Calculator.AnomalyMul.cal_ap()` 保留 public signature 与 `@lru_cache(maxsize=16)` 并委托 `_calculate_anomaly_proficiency(...)`，`Calculator.StunMul.cal_imp()` 委托新增 scalar `_calculate_impact(...)`。本 handoff 不授权 broad `Calculator.py` / `CalAnomaly.py` rewrite，也不授权删除 retained formula snapshots 或旧 Buff runtime compatibility。

Final validation evidence：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py -q` passed：`134 passed`。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `134 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `234 passed` / mypy `22 source files` clean。
- `implicit-events`、default lifecycle validation 与 main-loop consistency remain conditional future gates：本 implementation 没有触达 copied-output、event-adjacent、dispatch/runtime、listener、dot-runtime、same-tick runtime-write、lifecycle container、validation-runner contract 或 live registered-route semantic diff。

Retained gates and rollback anchors：

- Retained gates：`formula-parity` 继续覆盖 formula oracle / scoped mypy；`calculator-reads` 继续覆盖 reader seam、raw-container guardrail、P2-A / P2-B guardrail、state sync 与 full-crit event-adjacent reader；`implicit-events` 只在后续触达 copied-output / event / dispatch / runtime / listener 分层时追加。
- Rollback anchors：回退失败 helper diff 时只回退 `_calculate_anomaly_proficiency(...)` 委托、`_calculate_impact(...)` 或对应 focused tests；保留 `Calculator.AnomalyMul.cal_am()`, `cal_ap()`, `Calculator.StunMul.cal_imp()`, retained `MultiplierData` / `MulData` / `DynamicStatement` snapshots、`AnomalyBar.current_ndarray`、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 和 `LegacyBuffRuntimeFacade`。

Remaining same-phase candidates：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| `Calculator.StunMul.get_stun_array()` / array outputs | Still oracle candidate; not authorized by `cal_imp()` helper extraction. | Next default PRD may build deterministic array-output oracle / boundary tests before any production proposal. |
| `Calculator.RegularMul` remaining branches | Direct damage / crit / vulnerability / special / sheer multiplier branches remain retained formula candidates. | Characterize exact branch and rollback anchor first; do not mix with broad `Calculator.py` rewrite. |
| Copied-output handler/report payload parity | Supporting event-adjacent compatibility evidence; not touched by AM/AP/impact implementation. | Preserve constructors, listener-facing fields, handler report payloads, scheduled publish, listener broadcast, dot runtime and runtime command separation; add `implicit-events` if touched. |
| Registered-team behavior sample eligibility | Policy retained, no validation-only team created. | Run main-loop consistency only for a real production semantic diff with a registered route and nonzero relevant event count. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol, or gate. |

Next default PRD：Phase-3 array-output / remaining formula oracle closure。Start from `Calculator.StunMul.get_stun_array()` / array outputs or one exact `Calculator.RegularMul` branch, and preserve copied-output, registered-route and P2-A through P2-G candidates in the intake pool.

## Current array / RegularMul PRD US-007 final handoff

结论：No-Go for production proposal；继续 characterization / proposal-readiness。当前 PRD 已完成 `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array contract、`Calculator.RegularMul.get_array_expect()` / `get_array_crit()` / `get_array_not_crit()` array contract，以及 selected RegularMul branch matrix 的 retained oracle characterization；这些证据不授权生产公式替换，也不授权删除 retained compatibility。

Final validation evidence：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py -q` passed：`138 passed`。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `138 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `238 passed` / mypy `22 source files` clean。
- `implicit-events`、default lifecycle validation 与 main-loop consistency skipped：本 PRD 没有触达 copied-output、event-adjacent、dispatch/runtime、listener、dot-runtime、same-tick runtime-write、lifecycle container、validation-runner contract 或 live formula semantics。

Retained gates and rollback anchors：

- Retained gates：`formula-parity` 继续覆盖 formula oracle / scoped mypy；`calculator-reads` 继续覆盖 reader seam、raw-container guardrail、P2-A / P2-B guardrail、state sync 与 full-crit event-adjacent reader；`implicit-events` 只在后续触达 copied-output / event / dispatch / runtime / listener 分层时追加。
- Rollback anchors：保留 `Calculator.StunMul.get_stun_array()`、`Calculator.cal_stun()`、`Calculator.RegularMul` array builders / selected branches、AM/AP/impact helper implementation、`Calculator.AnomalyMul.cal_res_pen()` selector extraction、retained `MultiplierData` / `MulData` / `DynamicStatement` snapshots、`AnomalyBar.current_ndarray`、copied-output constructors、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 和 `LegacyBuffRuntimeFacade`。

Remaining same-phase candidates：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| Copied-output handler/report payload parity | Retained event-adjacent candidate; not touched by current array / RegularMul PRD. | Preserve constructors, listener-facing fields, handler report payloads, scheduled publish, listener broadcast, dot runtime and runtime command separation; add `implicit-events` if touched. |
| Registered-team behavior sample eligibility | Policy retained; no validation-only team created. | Run main-loop consistency only for a real production semantic diff with a registered route and nonzero relevant event count. |
| `Calculator.RegularMul` remaining branches / retained-only sheer follow-up | Selected matrix characterized; sheer branch remains runtime-only / retained-only. | Characterize exact branch and rollback anchor first; do not mix with broad `Calculator.py` rewrite. |
| `Calculator.StunMul.get_stun_array()` follow-up | Array contract characterized; no production replacement authorization. | Reopen only for a named follow-up gap, focused regression, or proposal-readiness packet. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol, or gate. |

Next default PRD：Phase-3 characterization / proposal-readiness continuation。Pick one exact remaining candidate from the table above, preserve retained gates and rollback anchors, and do not generate production replacement unless a later packet names deterministic oracle, rollback, registered-route, and validation evidence for that exact candidate.

## Current sheer reader-snapshot PRD US-007 final handoff

结论：No-Go for production proposal；继续 characterization / proposal-readiness。当前 PRD 已证明 `Calculator.RegularMul.cal_base_attr(..., base_attr=4)` 的 retained sheer conversion 依赖 runtime `char_instance.sheer_attack_conversion_rate`，且 `cal_sheer_dmg_bonus()` 对 `diff_multiplier == 4` 仍可由 reader-built snapshot 表达；这些证据不授权生产公式替换，也不授权扩展 `_CalculatorReadSnapshot` 公共契约。

Final validation evidence：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py -q` passed：`139 passed`。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `139 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `239 passed` / mypy `22 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed：base `2 passed` / isolated teams `3 passed` / focused `242 passed` / mypy `88 source files` clean。
- Current US-007 docs-only handoff validation：JSON sanity、focused typecheck and UTF-8 / mojibake scan must pass before marking the story complete; no broad profile rerun is required because no production, test, validation-runner, copied-output, event/runtime, listener, lifecycle or registered-route files are edited.

Retained gates and rollback anchors：

- Retained gates：`formula-parity` remains the formula oracle / scoped mypy gate；`calculator-reads` remains the reader seam / raw-container guardrail gate；`implicit-events` remains conditional for copied-output, event, dispatch, runtime, listener, dot-runtime or same-tick write changes。
- Rollback anchors：保留 `Calculator.RegularMul.cal_base_attr(...)` / `cal_sheer_dmg_bonus(...)` retained behavior、`_CalculatorReadSnapshot` 当前字段集、`CalculatorBuffAttributeReader` public read methods、`MultiplierData` / `DynamicStatement` snapshots、old containers、copied-output constructors、`ScheduleDispatchPort`、listener broadcasts、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade` 和 validation-runner wiring。

Remaining same-phase candidates：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| Copied-output handler/report payload parity | Retained event-adjacent candidate; not touched by current sheer PRD. | Preserve constructors, listener-facing fields, handler report payloads, scheduled publish, listener broadcast, dot runtime and runtime command separation; add `implicit-events` if touched. |
| Registered-team behavior sample eligibility | Current sheer route has no registered `仪玄` / `Yixuan` team and no validation-only team should be created. | Run main-loop consistency only for a future production semantic diff with an existing registered route and nonzero sheer-relevant or candidate-specific event counts. |
| `Calculator.RegularMul` remaining branches / retained-only sheer follow-up | Sheer conversion is retained-oracle-covered but production proposal No-Go due snapshot-contract and registered-route blockers. | Reopen only for a named exact branch or follow-up gap with deterministic oracle, rollback anchors and registered-sample conditions. |
| `Calculator.StunMul.get_stun_array()` follow-up | Array contract characterized; no production replacement authorization. | Reopen only for a named follow-up gap, focused regression, or proposal-readiness packet. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol, or gate. |

Next default PRD：Phase-3 characterization / proposal-readiness continuation。Pick one exact remaining candidate from the table above; do not promote `RegularMul` sheer conversion to production proposal without a real registered-route sample and an architecture-approved reader-contract plan.

## Current copied-output PRD US-008 final handoff

结论：Conditional Go for later bounded proposal package only。当前 copied-output PRD 已完成 constructor field matrix、`UpdateAnomaly.spawn_output(...)` listener boundary、anomaly / disorder / polarity / abloom handler report payload parity、registered behavior sample eligibility、serial retained gates 和 rollback-anchor decision；这些证据允许下一 PRD 写 bounded proposal contract，但不授权立即 production implementation、broad `Calculator.py` / `CalAnomaly.py` rewrite、validation-runner rewrite、registered-team fixture creation 或 retained compatibility 删除。

US-008 verifier evidence：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py tests/simulator/test_update_anomaly_dispatch.py tests/simulator/test_anomaly_handler_runtime_view.py -q` exited `0` with `168 passed`。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` exited `0`：base simulator `2 passed`、isolated teams `3 passed`、focused implicit-event suite `246 passed`、scoped mypy `Success: no issues found in 88 source files`，并打印 `[验证完成] 所有步骤通过`。
- JSON sanity passed for Ralph controller files；UTF-8 / mojibake scan passed for edited Chinese Markdown docs。
- A raw ad hoc mypy command that included focused test files exposed existing test-fixture typing debt and is not retained as the story gate；the scoped `implicit-events` profile above is the established Buff typecheck/profile gate for this boundary。

Retained gates and compatibility retained：

- Retained gates：proposal / docs-only story 至少保留 JSON sanity、focused typecheck 或 active-story typecheck gate、UTF-8 / mojibake scan；future copied-output source diff 追加 `implicit-events`；future formula / reader diff 继续串行保留 `formula-parity` 与 `calculator-reads`；future live semantic diff 只有真实 registered route 且 nonzero relevant event count 时才追加 main-loop consistency。
- Compatibility retained：`CopyAnomalyForOutput.py` constructors、`UpdateAnomaly.spawn_output(...)`、anomaly / disorder / polarity / abloom handlers、listener broadcast、scheduled publish、dot runtime registration、same-tick runtime writes、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、old containers、legacy `buff_add()` / `KickOutBuff()`、`Calculator.py` / `CalAnomaly.py` retained formula snapshots、`MultiplierData` / `MulData` / `DynamicStatement`、`AnomalyBar.current_ndarray`、AM/AP/impact and `cal_res_pen()` bounded implementations, array / RegularMul / sheer characterization evidence all remain retained.

Same-phase candidate pool：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| Copied-output bounded proposal package | Conditional Go for proposal only. | Next default PRD may write exact touched files / symbols, focused tests, scoped mypy, retained gates, registered-sample condition, rollback plan and non-goals; it must not implement production diff by default. |
| Registered-team behavior sample eligibility | Policy codified; no validation-only team created. | Use a real registered route only for future production semantic diff and require nonzero copied-output / anomaly event count before using the sample as evidence. |
| `Calculator.RegularMul` remaining branches / retained-only sheer follow-up | Characterization / retained oracle evidence remains No-Go for production proposal. | Reopen only for a named branch or sheer contract gap with deterministic oracle, rollback anchors and registered-sample conditions. |
| `Calculator.StunMul.get_stun_array()` follow-up | Array contract characterized; no production replacement authorization. | Reopen only for a named array-output follow-up, focused regression or proposal-readiness packet. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol or gate. |

Next default PRD：write the copied-output handler/report bounded proposal package first. After that proposal is complete, reselect from the same-phase pool instead of automatically collapsing into one copied-output implementation path.

## Current US-007 AM/AP/impact proposal Go / No-Go

结论：Go for a later bounded production implementation PRD。授权范围只限 `zsim/sim_progress/ScheduledEvent/Calculator.py` 内 scalar AM/AP/impact helper-family：`Calculator.AnomalyMul.cal_am()` 作为已 helper-backed baseline 保持不变，除非 focused validation 暴露回归；`Calculator.AnomalyMul.cal_ap()` 可保持 public signature 与 `@lru_cache(maxsize=16)` 并委托 `_calculate_anomaly_proficiency(...)`；`Calculator.StunMul.cal_imp()` 可新增 scalar `_calculate_impact(...)` 后委托该 helper。

本 Go 不授权：broad `Calculator.py` / `CalAnomaly.py` rewrite、`Calculator.StunMul.get_stun_array()` / array outputs、`Calculator.RegularMul` remaining branches、copied-output constructors / handler report payload、registered-team fixture creation、old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、`MultiplierData`、`MulData`、`DynamicStatement` 或 retained formula snapshots 删除。

US-007 复验记录：

- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `132 passed` / mypy 9 source files clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `232 passed` / mypy 22 source files clean。
- `implicit-events`、default lifecycle validation、validation-runner help / runner tests 与 main-loop consistency skipped：本 story 只更新 handoff / Ralph docs，没有触达 copied-output、event-adjacent、dispatch、listener、dot-runtime、same-tick runtime-write、lifecycle container、validation-runner contract 或 live formula semantics。

Next default PRD：生成 AM/AP/impact bounded production implementation PRD。下一 PRD 必须先保存 slice plan，使用 CodeGraph + targeted `rg` 复核 exact helper scope，新增或复用 focused pytest，串行跑 `formula-parity` 与 `calculator-reads`，并在 progress 中记录 retained boundary verdict；只有实际触达事件 / runtime / lifecycle / live behavior 时才追加对应 conditional gate。

## Current US-013 AM/AP/impact final handoff

结论：Ready for bounded production proposal PRD。`Calculator.AnomalyMul.cal_am()`、`Calculator.AnomalyMul.cal_ap()`、`Calculator.StunMul.cal_imp()` 与 `CalculatorBuffAttributeReader.read_anomaly_mastery()`、`read_anomaly_proficiency()`、`read_impact()` 已具备 retained `MultiplierData` oracle、reader-built snapshot parity、独立 AM/AP/impact boundary test、validation profile wiring、registered-sample 条件和 final serial gate 证据。该结论不授权 broad `Calculator.py` / `CalAnomaly.py` rewrite，也不授权删除 old Buff containers、runtime compatibility paths、copied-output constructors 或 retained formula snapshots。

US-013 复验记录：

- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `132 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `232 passed` / mypy `22 source files` clean。
- Known output noise 仍与 exit status 分开记录：pytest-asyncio loop-scope warning 和既有 async log-writer shutdown `RuntimeError` 出现在 successful markers 之后。

Next default PRD：US-007 已完成 bounded production proposal 并给出 Go；下一步默认改为 AM/AP/impact bounded production implementation。实现仍必须选择 exact helper scope（默认只处理 AP helper convergence 与 impact scalar helper extraction，AM 作为 baseline 保持不变）、focused pytest、scoped mypy、rollback anchors、registered behavior sample 条件、retained `formula-parity` / `calculator-reads` gates、触达 event/runtime 时的 `implicit-events` gate 与 non-goals；不得实施 broad formula replacement。

## US-009 final bounded-domain Go / No-Go

结论：bounded proposal Go，仅限 `Calculator.AnomalyMul.cal_res_pen()`。本 PRD 没有修改 `Calculator.py`、`CalAnomaly.py`、`CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、validation runner、old Buff containers 或 runtime compatibility paths；它只关闭 proposal 前置 blocker，并把下一轮默认工作从 blocker closure 转为一个 bounded production replacement proposal。

US-008 / US-009 验证与 handoff 证据：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py tests/simulator/test_update_anomaly_dispatch.py tests/simulator/test_anomaly_handler_runtime_view.py -q` passed：`126 passed`。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` passed：base `2 passed` / isolated teams `3 passed` / focused `103 passed` / mypy `9 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` passed：base `2 passed` / isolated teams `3 passed` / focused `203 passed` / mypy `22 source files` clean。
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` passed：base `2 passed` / isolated teams `3 passed` / focused `242 passed` / mypy `88 source files` clean。
- CodeGraph / source evidence confirms `CalAnomaly.cal_k_level()` clamp remains a retained lookup, `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` remain the only same-tick runtime command boundary, and `LegacyBuffRuntimeFacade` still wraps old container identity by reference.

Final blocker status：

| Blocker / candidate | US-009 status | Future rule |
| --- | --- | --- |
| `Calculator.AnomalyMul.cal_res_pen()` | Closed as the only proposal-eligible bounded domain. | Next PRD may write a bounded replacement proposal with exact focused pytest, scoped mypy, rollback plan, retained gates, and registered sample condition. |
| `Calculator.AnomalyMul.anomaly_snapshot` vector assembly | Closed as supporting retained vector-order evidence. | Do not widen into a second production replacement domain unless a later PRD reopens it with new evidence. |
| `CalAnomaly.cal_k_level()` clamp | Closed as retained lookup / log-side-effect evidence. | Preserve clamp behavior; do not rewrite `CalAnomaly.py` as part of the `cal_res_pen()` proposal. |
| Copied-output handler/report payload parity | Closed as event-adjacent compatibility evidence. | Preserve copied-output constructors, listener-facing fields, handler report payloads, scheduled publish, listener broadcast, dot runtime, and runtime command separation. |
| Registered-route eligibility | Codified for future production semantic diff. | Use `薇薇安物理队` only if JSON proves nonzero anomaly / disorder event counts; do not create validation-only teams. |
| Rollback / retained gates | Closed for proposal intake. | Retain `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, old containers, legacy `buff_add()` / `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, `formula-parity`, `calculator-reads`, and event-specific `implicit-events`. |

Next default PRD：create a bounded proposal for `Calculator.AnomalyMul.cal_res_pen()` only. It must not implement broad formula replacement by default and must keep P2-A through P2-G guarded maintenance, retained compatibility, copied-output parity, registered-route eligibility, and blocker-only reopen rules available as same-phase candidate blocks.

## US-007 final proposal Go / No-Go

结论：later implementation PRD 为 Go，但只限 `Calculator.AnomalyMul.cal_res_pen()`。当前 PRD 完成的是 bounded proposal、validation contract、registered-route 条件、rollback anchors 与 final handoff；它没有修改 `Calculator.py`、`CalAnomaly.py`、copied-output source、validation runner、old Buff containers 或 runtime compatibility paths。

Proposal package evidence：

- `scripts/ralph/investigations/2026-06-11-US-003-bounded-cal-res-pen-proposal.md` 已把 proposed production formula domain 收敛到 `Calculator.AnomalyMul.cal_res_pen()`。
- `scripts/ralph/investigations/2026-06-11-US-004-validation-contract.md` 已记录 future implementation PRD 的 focused pytest、scoped mypy、`formula-parity` 与 retained `calculator-reads` gate。
- `scripts/ralph/investigations/2026-06-11-US-005-sample-rollback-plan.md` 已记录 registered behavior sample 条件、nonzero event-count 规则与 rollback anchors。
- `US-006` serial gate 已通过，且 `US-007` handoff rerun 维持绿色：`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `103 passed` / mypy 9 files clean；`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `203 passed` / mypy 22 files clean。

Final decision matrix：

| candidate / boundary | final decision | next rule |
| --- | --- | --- |
| `Calculator.AnomalyMul.cal_res_pen()` | Go for later implementation PRD only | Implement one bounded selector / extraction diff using the proposal contract, focused pytest targets, scoped mypy targets, retained gates, rollback anchors, and registered sample condition. |
| `Calculator.AnomalyMul.anomaly_snapshot` | Supporting evidence | Keep vector-order / snapshot-shape oracle as guardrail evidence for the `cal_res_pen()` diff; do not promote into a second production domain without a new PRD. |
| `CalAnomaly.cal_k_level()` | Supporting evidence | Preserve retained lookup, clamp, and log side effects; do not rewrite `CalAnomaly.py` as part of the `cal_res_pen()` implementation. |
| Copied-output handler/report payload parity | Supporting event-adjacent evidence | Preserve constructors, report payloads, listener-facing fields, scheduled publish, listener broadcast, dot runtime, and same-tick runtime-write separation. |
| Retained compatibility | Must stay intact | Keep `MultiplierData`, `MulData`, `DynamicStatement`, `AnomalyBar.current_ndarray`, old containers, legacy `buff_add()` / `KickOutBuff()`, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, and `LegacyBuffRuntimeFacade`. |
| P2-A through P2-G guarded maintenance | Same-phase blocker-only pool | Reopen only when focused tests, source guardrails, or validation names a concrete regression. |

Next default PRD：implement exactly `Calculator.AnomalyMul.cal_res_pen()` as a bounded production diff. It must not implement broad `Calculator.py` / `CalAnomaly.py` replacement, copied-output formula replacement, old-container deletion, or validation-runner rewiring by default.

## US-002 fixture inventory / oracle target map

本节属于当前 Phase-3 formula oracle gap closure PRD；同名历史 US-002 不适用。根工作区预检使用上方 US-002 `rg` 命令，显式排除 `.codex_worktrees/`、`archive/`、`scripts/ralph/archive/`、`scripts/ralph/run-logs/` 与 `*.log`。预检命中 727 行；`tests/simulator/test_buff_attribute_reader.py` 因同时作为显式文件和 `tests/simulator` 目录参数出现，清单去重后只按根工作区测试文件计入。

| 现有 focused fixture / test | 已覆盖公式域 | 保留兼容边界 |
| --- | --- | --- |
| `test_create_anomaly_attribute_read_context_preserves_inputs()`、`test_formula_parity_fixture_builds_independent_calculator_inputs()`、`test_migrated_reader_seam_regression_sample_scope_is_representative()` | 公式 parity fixture、reader context 输入、root-workspace 样本来源。 | 只证明 fixture / context 隔离和样本来源；不删除 retained `Calculator`、`MultiplierData`、old containers 或 XLogic callsites。 |
| `test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot()`、`test_multiplier_data_dynamic_statement_translates_python_attr_names()`、`test_multiplier_data_dynamic_statement_rejects_invalid_effect_key()`、`test_multiplier_data_cache_key_stability_and_reset_isolation()`、`test_multiplier_data_cache_key_distinguishes_enemy_dot_participation()`、`test_enemy_dynamic_debuff_reads_feed_old_and_reader_formula_snapshots()` | `MultiplierData` / `DynamicStatement`、`buff_effect_trans` Python 属性名翻译、非法 key 报错、cache key 稳定性 / reset isolation、enemy debuff 聚合、enemy dot 仅参与 cache key 的边界。 | 保留旧 `_calculate_dynamic_statement()`、`MultiplierData.get_buff_bonus()`、`MultiplierData.__new__()` cache key、`MultiplierData.mul_data_cache`、`StaticStatement._instance_cache`、enemy dynamic list 读取与 cache key 语义。 |
| `test_attribute_reader_matches_old_anomaly_mastery_helper()`、`test_attribute_reader_matches_old_anomaly_proficiency_helper()`、`test_calculator_am_ap_impact_formula_family_matches_reader_snapshot_parity()`、`test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[anomaly-mastery-proficiency-buildup-base-damage]`、`[anomaly-dmg-bonus-ratio-fields]`、`[anomaly-ap-multiplier-conversion]`、`[anomaly-extra-multiplier-fields]`、`[anomaly-crit-retained-fields]`、`[anomaly-res-pen-fire-positive]`、`[anomaly-res-pen-default-zero]`、`[anomaly-res-pen-frost-uses-ice-field]`、`test_anomaly_mul_snapshot_vector_matches_expected_retained_fields[physical-default-no-bonus-vector]`、`[electric-dynamic-field-vector]`、`test_branch_blade_song_gate_uses_attribute_reader_with_old_helper_parity()`、`test_timeweaver_disorder_gate_uses_attribute_reader_with_old_helper_parity()` | `Calculator.AnomalyMul.cal_am()` / `cal_ap()`、`cal_anomaly_buildup()`、`cal_base_damage()`、`cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()`、`cal_res_pen()`、`anomaly_snapshot` 9-slot vector assembly、AM/AP reader seam、两个 migrated gate callsite、火属性积蓄 / 基础异常伤害字段、异常增伤字段、AP 转换字段、异常额外倍率字段、异常暴击 retained-1 边界、抗性穿透正值 / 默认零值 / element-specific 霜读冰字段边界、默认 / no-bonus 物理 snapshot vector 与非默认电属性 dynamic-field snapshot vector。 | reader seam、retained `MultiplierData` 与 reader-built snapshot 等价只作为 compatibility evidence；`cal_anomaly_crit()` 当前仍锁定 retained-1 兼容边界，`cal_res_pen()` 与 `anomaly_snapshot` oracle 只关闭各自 deterministic blocker，不把 P2-A reader seam 当作生产公式替换、不删除 retained `AnomalyMul` helper、不新增 runtime 写 facade。 |
| `test_p2b_parity_fixture_matches_old_impact_helper()`、`test_calculator_am_ap_impact_formula_family_matches_reader_snapshot_parity()`、`test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[stun-impact-reader-parity]`、`[stun-ratio-res-bonus-received-retained]` | `Calculator.StunMul.cal_imp()` 与 impact reader seam；`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()` retained / reader-snapshot oracle。 | P2-B impact reader seam 仍只是 compatibility evidence；stun ratio / resistance / bonus / received 目前只锁 retained formula 与 reader-built snapshot，不新增 reader API、不删除 retained `StunMul` helper。 |
| `test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[regular-base-dmg-*]`、`test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[regular-multipliers-neutral-zero-boundary]`、`[regular-dmg-bonus-character-field-stack]`、`[regular-defense-res-vulnerability-received-stack]`、`[regular-crit-received-boundary]`、`test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers()`、`test_p2b_full_crit_rate_includes_received_bonus_but_personal_excludes()`、`test_p2b_parity_fixture_matches_old_personal_crit_damage_helper()`、`test_p2b_personal_crit_damage_excludes_received_crit_damage_bonus()`、`test_calculator_regular_mul_crit_formula_families_preserve_received_boundaries()`、`test_calculator_attribute_formula_boundaries_remain_retained_compatibility()` | `Calculator.RegularMul.cal_base_dmg()`、`cal_base_attr()`、`cal_dmg_bonus()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()`、`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()`、neutral / static-field / dynamic-buff base damage inputs、角色侧增伤、敌方防御 / 抗性、受击抗性降低 / 穿透、易伤字段、received crit inclusion / exclusion。 | base damage / base attribute / damage bonus / defense / resistance / vulnerability / crit families 只作为 retained Calculator oracle 与 reader-snapshot compatibility evidence；full crit 保留 received crit rate / damage；personal crit rate / damage 保留排除 received bonus；仍不覆盖 crit expectation、stun vulnerability、special / sheer multiplier 或 array outputs。 |
| `test_anomaly_formula_fixture_copies_snapshot_inputs_for_copied_output()`、`test_new_anomaly_spawn_output_copies_active_payload_without_publish()`、`test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()`、`test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility()` | copied `AnomalyBar.current_ndarray` 非别名、`NewAnomaly` active-bar payload 字段、`Disorder` / `PolarityDisorder` payload 字段、结算快照输入。 | 只锁 copied-input / payload compatibility；不替换 `CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、listener broadcast、scheduled publish 或 report payload 语义。 |
| `test_cal_anomaly_rejects_unsettled_or_bad_snapshot_shape()`、`test_cal_anomaly_level_clamp_remains_retained_lookup()`、`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()`、`test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()`、`test_cal_abloom_formula_inputs_and_fixture_blockers()` | `CalAnomaly.__init__()` settled / shape guard、`CalAnomaly.cal_k_level()` 低于边界 / 正常 / 高于边界 retained lookup 与日志语义、`MulData` retained snapshot、`CalAnomaly.cal_active_crit()`、`cal_def_mul()`、res / vulnerability / stun / special multiplier inputs、`set_final_multipliers()` 最终向量顺序、snapshot impact / stun ratio 在 `cal_anomaly_dmg()` 中被除回、非默认 `scaling_factor` 乘算位置，以及 `CalAbloom` copied `current_ndarray`、`anomaly_dmg_ratio` 与 inherited final multiplier vector。 | 保留 `CalAnomaly.py` 生产公式、`AnomalyBar.current_ndarray` 直接快照读取、enemy dynamic lists、Abloom handler runtime-view 读口与 copied-output report payload semantics。 |

| Oracle target | 当前状态 | 后续 Ralph-sized测试方向 |
| --- | --- | --- |
| `Calculator.RegularMul` | `cal_base_dmg()` / `cal_base_attr()` 已有 neutral、static-field、dynamic-buff 表驱动 oracle；`cal_base_attr(..., base_attr=4)` 已有 retained runtime-dependency oracle，证明它需要 `char_instance.sheer_attack_conversion_rate`；`cal_sheer_dmg_bonus()` 对 `diff_multiplier == 4` 保持 snapshot-compatible；`cal_dmg_bonus()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()` 已有 zero-like neutral、角色侧增伤堆叠、敌方防御 / 抗性、受击抗性降低 / 穿透、易伤字段堆叠 oracle；`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()` 已有 received-boundary 表驱动 oracle 与 reader seam 兼容证据；`cal_crit_expect()`、`cal_stun_vulnerability()`、`cal_special_mul()` 和部分 array / sheer follow-up 仍缺 proposal-grade oracle / registered-route gate。 | 继续拆成 crit expectation、stun vulnerability、special / sheer multiplier 与 exact array / sheer follow-up 小组；每组继续包含 neutral、static-field、dynamic-buff、enemy-side / received 字段组合。不得绕过 reader-snapshot contract 和 registered-route sample blockers。 |
| `Calculator.AnomalyMul` | `cal_am()` / `cal_ap()` 已有 reader seam、gate callsite parity 与表驱动 retained / reader-snapshot / reader 三路等价证据；US-013 已把 AM/AP 从 readiness-only 推进为 bounded production proposal-ready，US-007 已给出 bounded implementation Go。`cal_am()` 已作为 helper-backed baseline；`cal_ap()` 是下一默认 implementation 中的 behavior-preserving helper convergence 候选。`cal_anomaly_buildup()`、`cal_base_damage()` 已有火属性积蓄 / 基础异常伤害表驱动 oracle，覆盖 static AM/AP/ATK、field bonus、enemy anomaly resistance、trigger buildup bonus 与 reader-built snapshot。US-008 新增 `cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()` deterministic oracle，分别分离异常增伤字段、AP 转换字段、异常额外倍率字段和 retained-1 异常暴击边界。US-003 新增 `cal_res_pen()` deterministic oracle，覆盖正值火属性、默认零值、霜属性复用冰抗穿字段并忽略非匹配 / 全局字段；该 helper 已由后续 PRD 实现为 bounded selector extraction，不再默认重开。US-004 新增 `anomaly_snapshot` expected vector oracle，覆盖默认 / no-bonus 物理输入、非默认电属性 dynamic-field 输入、9-slot field order，并证明它与 copied-output `AnomalyBar.current_ndarray` 的 1x11 payload shape / mutation 语义分离。 | 下一步默认只为 AM/AP 写 bounded production implementation：AM 保持 baseline，AP 委托 `_calculate_anomaly_proficiency(...)`，并用 focused tests / mypy / serial validation 证明 public signature、cache decorator、reader parity 与 rollback anchors；不要把 P2-A migrated reader bucket 重新打开成生产替换任务，也不要把 retained-1 anomaly crit、`cal_res_pen()` 或 `anomaly_snapshot` characterization 当作同一生产公式替换授权。 |
| `Calculator.StunMul` | `cal_imp()` 已完成 scalar `_calculate_impact(...)` helper extraction；`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()` 已有 retained / reader-snapshot deterministic oracle；`get_stun_array()` / `cal_stun()` array contract 已 characterized，但没有 production replacement authorization。 | 不把 P2-B impact reader evidence 或 scalar impact helper extraction 外推成完整 StunMul production replacement；`get_stun_array()` / array output 和注册队伍行为样本条件仍是后续 exact candidate。 |
| `CalAnomaly` | settled snapshot、shape guard、`cal_k_level()` below-boundary / normal / above-boundary clamp、enemy dynamic lists、`CalAnomaly.cal_active_crit()`、`cal_def_mul()`、res / vulnerability / stun / special multiplier 组合、`set_final_multipliers()` vector order、snapshot impact / stun ratio treatment、非默认 `scaling_factor` 位置和 `CalAnomaly.cal_anomaly_dmg()` retained ratio sample 已有。 | 后续只在 copied-output report payload parity、registered-route sample 或 production replacement gate 中复用这些 oracle；不要把 `CalAnomaly` focused characterization 外推成生产公式替换授权。 |
| `CalDisorder` | copied payload compatibility 已有；US-014 新增 element-type formula oracle，覆盖 `cal_disorder_base_dmg()` remaining tick / floor 规则、`cal_disorder_extra_mul()`、`cal_disorder_stun()`，并用 copied payload sentinel 字段证明 listener-facing payload 不参与公式输入。 | 后续只在 handler/report payload 或 production formula replacement PRD 中复用这些 oracle；不要把本 focused characterization 外推成 `CalPolarityDisorder` / `CalAbloom` 覆盖。 |
| `CalPolarityDisorder` | `PolarityDisorder` copied fields、Yanagi lookup success path、`polarity_disorder_ratio`、`additional_dmg_ap_ratio` 与 retained `Calculator.AnomalyMul.cal_ap()` 输入已有 deterministic oracle。 | 后续只补 copied-output report payload parity 或 replacement gate；不要把 formula input oracle 外推成生产公式替换授权。 |
| `CalAbloom` | `test_cal_abloom_formula_inputs_and_fixture_blockers()` 已覆盖 copied `current_ndarray`、`anomaly_dmg_ratio` 组合、inherited final multiplier vector、`scaling_factor` 位置，以及 `schedule_priority` / `rename_tag` / `accompany_dot` output-only sentinel fields 不进入 formula 输入。 | 后续只补 Abloom handler report payload / listener-facing parity 或 replacement gate；不改变 Abloom handler runtime-view 读口。 |
| copied-output payloads | `NewAnomaly` mode 0 active-bar payload fields、no listener publish boundary、`Disorder` / `PolarityDisorder` formula inputs and payload fields 已锁；US-006 已锁 `NewAnomaly`、`Disorder`、`PolarityDisorder`、`DirgeOfDestinyAnomaly` handler report payload fields，并断言 disorder family listener settlement broadcast 与 report payload 分层。 | 继续做 registered-route eligibility / rollback-gate proof；不要把 copied-output handler parity 外推成 scheduled publish migration、runtime write-path replacement 或 production formula replacement。 |
| `AnomalyBar.current_ndarray` | settled / copied snapshot 非别名已有；field-level lifecycle matrix 不完整。 | 覆盖未满条、满条结算、`update_snap_shot()`、`reset_current_info_cause_output()`、`reset_myself()`、`create_new_from_existing()`、`__deepcopy__()`、shape / dtype / aliasing。 |

## US-022 行为样本决策矩阵

本矩阵只定义何时需要 registered-team main-loop consistency sample；它不新增 validation profile，不替换生产公式，不把 `--legacy-runtime` / `--candidate-runtime` label 当作真实 runtime switch。

| 公式 / 行为域 | 默认证据层级 | 语义变更后何时追加 registered-team main-loop sample | 关注输出 |
| --- | --- | --- | --- |
| direct damage / crit / defense / resistance / vulnerability 公式 | focused unit characterization、retained `Calculator.RegularMul` oracle、reader seam parity。 | 实际改变 `Calculator.py` 中会进入 live damage route 的数值公式，且已注册队伍的 APL 能在 stop-tick 内触达对应伤害事件。 | `total_damage` 必须解释为 live behavior 证据；仍需 focused parity suite 先通过。 |
| stun / impact / stun-ratio 公式 | focused impact / stun formula snapshots、P2-B migrated reader guardrail。 | 实际改变 `Calculator.StunMul`、impact reader 或 stun received 语义，且注册队伍能在 stop-tick 内打出该 stun / impact route。 | `total_damage`、相关 `event_counts` 与 Buff timeline 是否随失衡窗口改变。 |
| anomaly buildup / anomaly damage / settlement | focused `CalAnomaly`、`AnomalyBar.current_ndarray`、settlement snapshot tests。 | 实际改变 `CalAnomaly.py`、`AnomalyBar.current_ndarray`、`anomaly_settled()`、active anomaly snapshot 或 buildup filtering，且注册队伍能触发目标异常积蓄 / 结算 route。 | `total_damage`、异常相关 `event_counts`、Buff timeline；无注册 route 时记录缺口。 |
| copied anomaly / disorder output | focused copied-output payload、formula-input、listener-facing field tests。 | 实际改变 `CopyAnomalyForOutput.py`、`UpdateAnomaly.spawn_output(...)`、`CalDisorder` / `CalPolarityDisorder` / `CalAbloom` copied formula semantics，且注册队伍能生成 NewAnomaly / Disorder / PolarityDisorder / copied-output payload。 | `event_counts`、`total_damage`、listener/report payload 可观察差异。 |
| Buff timeline / lifecycle | focused lifecycle、runtime facade、guardrail tests。 | 实际改变 Buff add / refresh / pending-to-active / active removal / duration tick / forced write 顺序，且注册队伍的 live route 会生成该 Buff timeline。 | `buff_timeline` 的 legacy-only / candidate-only 样本必须为零，或差异有明确预期。 |
| scheduled event publish timing | focused dispatch tests、fail-fast queue tests、event payload order tests。 | 实际改变 `execute_tick`、priority、target fan-out、publish-before/after ordering、`mission_start(...)` / `simple_start()` 相对顺序，且注册队伍 live route 会发布该事件。 | `event_counts`、Buff timeline 与总伤；publish timing 不能只靠 CLI label 证明。 |
| 文档 / 分类 / test-only / guardrail-only / retained-compatibility | focused docs / tests / validation profile。 | 不运行，除非同一 story 同时改 production behavior。 | 在 Ralph progress 记录跳过原因，不为了补样本创建 validation-only team。 |

### Registered-team 触发条件

| 触发类别 | 可考虑的真实注册队伍 / APL | 运行 registered sample 的必要条件 | 当前证据 / 缺口 |
| --- | --- | --- | --- |
| direct damage / crit | `莱特火属性队` / `./zsim/data/APLData/莱特-扳机-雨果.toml`；`席德大安比队` / `./zsim/data/APLData/席德-大安比-扳机.toml`。 | 注册队伍配置存在；APL 在 stop-tick 内命中目标技能 / 伤害事件；本 story 改动会改变公式输出或事件进入伤害计算的字段。 | P2-B 已有 `莱特火属性队` 样本，P2-C 已有 `席德大安比队` 样本；phase-3 公式替换仍需按具体公式 route 重新确认。 |
| stun / impact | `青衣雷属性队` / `./zsim/data/APLData/青衣-丽娜-雅.toml`；必要时复核 `席德大安比队` / `./zsim/data/APLData/席德-大安比-扳机.toml`。 | 注册队伍能触发目标 impact / stun bonus / stun received route，并在 stop-tick 内进入可观察失衡窗口。 | 只作为候选；运行前必须先确认 APL 触达目标文件或公式，不能把 direct-damage 样本外推为 stun 证据。 |
| anomaly settlement | `薇薇安物理队` / `./zsim/data/APLData/薇薇安-柳-耀嘉音.toml`。 | 注册队伍能触发目标异常积蓄、结算、紊乱或异常伤害 route；stop-tick 覆盖 active anomaly lifecycle。 | Vivian / Yanagi 可作为 anomaly 候选；Alice / Yuzuha / Jane 当前没有 `tests.teams.TeamRegistry` 注册代表队，不能为了样本临时发明队伍。 |
| copied-output | `薇薇安物理队` / `./zsim/data/APLData/薇薇安-柳-耀嘉音.toml`，仅在 APL 预检证明能生成目标 copied payload 后使用。 | 注册队伍实际生成 NewAnomaly / Disorder / PolarityDisorder / Vivian copied payload，并让 payload 进入 handler、listener 或 report path。 | 若 APL 无法触达 copied-output route，记录缺口并以 focused copied-output tests 收口。 |
| Buff timeline | 已有 `莱特火属性队` 与 `席德大安比队` 成功样本；其他注册队伍需按 touched Buff route 单独确认。 | 改动会影响 Buff / debuff / dot 的 add、refresh、activation、duration 或 removal，且注册队伍 route 会产生这些 timeline entries。 | 已有成功样本只证明对应 route，不可外推到其他 Buff / formula domains。 |
| event publish timing | 从 `青衣雷属性队`、`席德大安比队`、`莱特火属性队`、`薇薇安物理队` 中选择能触达目标 producer 的队伍。 | 改动会影响 scheduled event 的 publish tick、priority、target fan-out 或 producer-local ordering，且注册队伍 route 会发布该事件。 | 先用 focused dispatch tests 锁 order；registered sample 只补 live route evidence，不能只靠 CLI label 证明。 |

US-022 本轮只更新文档矩阵与 Ralph 记录，没有 live semantic change、validation wiring change 或注册队伍 fixture 变更；因此不运行 `--mainloop` 或 `scripts/run_buff_main_loop_consistency.py`，以 focused docs / tests 和 `formula-parity` validation 收口。

## US-023 rollback plan / retained validation gates

本节只 codify rollback 与 gate 保留规则；不改 `Calculator.py`、`CalAnomaly.py`、`CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、`AnomalyBarClass.py`、validation runner 或 production formula 语义。

### Retained rollback anchors

- 公式锚点：`Calculator.py`、`CalAnomaly.py`、`MultiplierData`、`MulData`、`DynamicStatement`、`AnomalyBar.current_ndarray`。
- copied-output 锚点：`CopyAnomalyForOutput.NewAnomaly`、`Disorder`、`PolarityDisorder`，以及 `UpdateAnomaly.spawn_output(...)` / `update_anomaly(...)` 的 listener-facing payload 与 scheduled publish 分层。
- 验证锚点：`formula-parity` 是 Phase 3 formula oracle 最小 gate；`calculator-reads` 保留 reader seam / XLogic helper / dynamic snapshot gate；`implicit-events` 保留 event publish、listener broadcast、dot runtime、same-tick runtime write 和 old Buff runtime compatibility gate。
- runtime 兼容锚点：`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、old containers、legacy `buff_add()` / `KickOutBuff()` 均保留；rollback 不通过删除旧容器、关闭 legacy Buff write path 或新增第二套 runtime write facade 来“修复”失败。

### Rollback 操作规则

| 失败类型 | 回滚动作 | 必须保留 | 复验 gate |
| --- | --- | --- | --- |
| helper / fixture diff 失败 | 只回退本 helper、fixture、oracle case 或测试期 adapter diff；若同 story 改了 source 与 test，按同一 commit 范围一起回退。 | 旧 `MultiplierData` / `MulData` / `DynamicStatement` 快照、`AnomalyBar.current_ndarray` 读取、copied-output 类和旧 Buff runtime compatibility path。 | `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity`。若 helper 触及 reader seam，再串行追加 `calculator-reads`。 |
| validation profile / runner diff 失败 | 回退 `scripts/run_buff_refactor_validation.py` 中新增或改动的 profile target / focused pytest target；不要为了让 profile 通过而删除 retained source anchors。 | `formula-parity`、`calculator-reads`、`implicit-events` 三个命名 gate 的现有职责边界。 | 若 runner contract 改过，先运行 `--help`；随后运行失败 profile 对应的 `--typecheck-profile ...`。 |
| production formula diff 失败（后续 PRD） | 回退生产公式 diff 到上述 retained source anchors；保留 characterization tests 作为失败证据或按同 commit 回退未通过的新增断言。 | `Calculator.py` / `CalAnomaly.py` retained formula snapshots、copied-output constructors、old containers、legacy Buff write paths、dispatch / listener / runtime write 分层。 | 先跑 `formula-parity`；涉及 reader seam 跑 `calculator-reads`；涉及 copied-output event/runtime layering 跑 `implicit-events`；只有实际 production semantic slice 且 registered route 存在时才追加 main-loop sample。 |

### P2-A through P2-G reopen rule

- P2-A through P2-G guarded buckets 保持完成状态；公式 oracle 扩容、rollback 文档、validation profile 保留或 registered-team sample policy 不会自动重开这些 bucket。
- 只有 guardrail、validation、root-workspace source scan 或真实 registered-route 行为证据命名具体失败文件 / 符号 / gate 时，才允许以 blocker-only PRD 重开对应 P2 bucket。
- rollback 的默认动作是撤销失败的 replacement / helper / profile diff，并保留旧兼容边界；不得把 old containers、legacy `buff_add()` / `KickOutBuff()`、`RuntimeCommandPort` / `LegacyRuntimeCommandAdapter` 或 `ScheduleDispatchPort` 当作清理失败 diff 的删除目标。

US-023 本轮只更新 rollback 文档与 Ralph 记录，没有 live semantic change、validation wiring change、registered-team fixture change 或 runtime boundary change；因此以 `formula-parity` validation 收口，不追加 `calculator-reads`、`implicit-events` 或 main-loop sample。

## US-024 formula-parity validation target contract

结论：保持 `scripts/run_buff_refactor_validation.py` 中现有 `formula-parity` target contract，不新增 focused pytest target、scoped mypy target 或 profile wiring。本 PRD 的公式 oracle / retained formula / `AnomalyBar.current_ndarray` 字段矩阵仍集中在 `tests/simulator/test_buff_attribute_reader.py`；US-018 / US-021 的 `tests/simulator/test_update_anomaly_dispatch.py` 样本属于 copied-output listener / scheduled publish / runtime 分层证据，继续由 `implicit-events` 或 story-local focused pytest 覆盖，不扩大 `formula-parity`。

当前 retained contract：

- focused pytest：`FORMULA_PARITY_FOCUSED_TEST_TARGETS = ["tests/simulator/test_buff_attribute_reader.py"]`，已覆盖 `RegularMul` / `AnomalyMul` / `StunMul` table oracle（含 US-003 `Calculator.AnomalyMul.cal_res_pen()` resistance-penetration cases）、`MultiplierData` / `DynamicStatement` cache and translation characterization、`CalAnomaly` / `CalDisorder` / `CalPolarityDisorder` / `CalAbloom` deterministic oracle、copied formula-input payload boundaries 与 `AnomalyBar.current_ndarray` reset / deepcopy matrix。
- scoped mypy：`FORMULA_PARITY_TYPECHECK_TARGETS` 保持 `Calculator.py`、`CalAnomaly.py`、`anomaly_bar/__init__.py`、`AnomalyBarClass.py`、`CopyAnomalyForOutput.py`、`BranchBladeSongCritDamageBonus.py`、`TimeweaverDisorderDmgMul.py` 与 `scripts/run_buff_refactor_validation.py`；`FOCUSED_MYPY_PROFILES["formula-parity"]` 继续追加 `tests/simulator/test_buff_attribute_reader.py`。
- 本轮没有新增或迁移 formula-oracle source / test 文件，也没有修改 runner contract；因此不运行 `--help`。验证仍以 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` 收口。

## US-010 复制紊乱 / 输出边界分类

| 路径 / 符号 | 来源 | 公式输入 / 输出字段 | 发布 / runtime 边界 | 保留兼容 |
| --- | --- | --- | --- | --- |
| `CopyAnomalyForOutput.py`：`NewAnomaly` / `Disorder` / `PolarityDisorder` | 从已激活 `AnomalyBar` 深拷贝；`active_by` 可覆盖 `activated_by`；`sim_instance` 可覆盖运行时引用。 | `current_ndarray`、`current_effective_anomaly`、`element_type`、`anomaly_dmg_ratio`、`scaling_factor`、`max_duration` / `last_active` / `remaining_tick()`、`accompany_dot`、`schedule_priority`；`Disorder.is_disorder=True`；`PolarityDisorder.polarity_disorder_ratio` / `additional_dmg_ap_ratio`。 | 本文件只构造 copied payload，不发布计划事件、不注册 dot、不写 Buff runtime。 | `test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()` 锁定 snapshot 非别名、payload 字段和 `execute_tick` 不存在；生产 copied-output 类仍保留。 |
| `UpdateAnomaly.spawn_output(...)` | `mode_number=0` 使用当前激活条并先 `anomaly_settled()`；`mode_number=1/2` 使用旧激活异常条生成紊乱 / 极性紊乱。 | mode 0 输出 `NewAnomaly`；mode 1/2 输出 `Disorder` / `PolarityDisorder`，并保留 `skill_node` 为 `activated_by`。 | 仅 mode 1/2 触发同步 `listener_manager.broadcast_event(..., DISORDER_SPAWN)`；scheduled queue publish 仍由 `update_anomaly()` 后续 `_publish_scheduled_event(dispatch_port, ...)` 完成。 | `test_update_anomaly_preserves_new_anomaly_then_disorder_order_via_dispatch_port()` 锁定 anomaly broadcast、disorder broadcast、new anomaly publish、`special_resources(disorder)`、disorder publish 的相对顺序。 |
| `UpdateAnomaly.update_anomaly(...)` / `remove_dots_cause_disorder(...)` | SkillEvent 处理阶段从 `enemy.anomaly_bars_dict`、active anomaly state 和 `skill_node` 派生输出。 | 不重算 copied-output 公式；只负责输出对象派生、dot / debuff side effect 和状态清理。 | scheduled publish 走 `ScheduleDispatchPort`；dot 注册 / 替换 / 移除走 `DotRuntimeStateAdapter`；伴随 debuff 仍走旧 `buff_add_strategy(...)` same-tick 写路径；不新增 `RuntimeCommandPort` 写 facade。 | `tests/simulator/test_update_anomaly_dispatch.py` fail-fast legacy queue、listener、dot runtime 和 pending Buff queue probes 保留分层证据。 |
| `TimeweaverDisorderDmgMul.special_judge_logic()` | BuffXLogic 判断路径从 `check_preparation(...)` 取得 enemy / active buff view / character。 | AP gate 通过 `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)`，和旧 `MultiplierData` / `Calculator.AnomalyMul.cal_ap(...)` 等价。 | 无 copied-output publish；无 listener broadcast；无 scheduled queue 或 runtime write。 | `test_timeweaver_disorder_gate_uses_attribute_reader_with_old_helper_parity()` 已锁定 reader seam，不授权删除 retained Calculator formulas。 |
| Alice disorder listeners | `DISORDER_SPAWN` / `DISORDER_SETTLED` 同步广播事件中的 `Disorder` / `PolarityDisorder` payload。 | `AliceCoreSkillDisorderBasicMulBonusListener` 读取 `event.element_type` 与 `remaining_tick()`；`AliceCinema2DisorderDmgBonus` 与 `AliceDisorderListener` 只校验 payload 类型并触发保留效果。 | Listener broadcast 是同步监听层；Buff 添加 / 资源恢复是 listener-owned runtime side effect，不等同 scheduled queue publish。 | 本轮只记录分类；后续若迁移 listener runtime writes，必须沿用 existing runtime facade / caller tests，不能把 listener broadcast 当成 queue publish 替代。 |

## US-011 enemy dynamic / debuff 聚合读分类

| 路径 / 符号 | 读取来源 | 公式 / 状态用途 | 分类 | 保留兼容 |
| --- | --- | --- | --- | --- |
| `Calculator.py`：`_calculate_dynamic_statement()`、`MultiplierData.get_buff_bonus()` | `dynamic_buff[char_name]` + `enemy.dynamic.dynamic_debuff_list`；缺失时保留 `dynamic_buff["enemy"]` fallback。 | 生成 `DynamicStatement`，供 AM/AP、crit、impact、易伤、防御、抗性等公式读取。 | formula parity。 | `test_enemy_dynamic_debuff_reads_feed_old_and_reader_formula_snapshots()` 证明空敌方状态、单 enemy debuff、堆叠 enemy debuff、dot-only cache participation case 在直接 `_calculate_dynamic_statement()`、旧 `MultiplierData`、reader snapshot 和 reader API 中一致；不替换生产聚合入口。 |
| `Calculator.py`：`MultiplierData.__new__()` | `enemy.dynamic.dynamic_debuff_list` 与 `enemy.dynamic.dynamic_dot_list` 进入 cache key。 | 保持旧 `MultiplierData` 缓存按敌方 debuff / dot 输入区分。 | retained compatibility。 | `test_multiplier_data_cache_key_distinguishes_enemy_dot_participation()` 证明只改变 `dynamic_dot_list` 会生成新的 `MultiplierData` cache entry，但 dot 不进入 `enabled_buff` 聚合；cache key 仍保留旧语义，后续若拆缓存需独立 guardrail。 |
| `Calculator.py`：`CalculatorBuffAttributeReader._build_statements()` | 通过 `_calculate_dynamic_statement()` 复用同一 enemy debuff 聚合入口。 | reader seam 构造公式快照，不直接读取或迁移旧容器写入。 | formula parity。 | 新测试证明 reader seam 与旧 helper 对 enemy debuff 聚合结果一致；不授权删除 `MultiplierData` / `DynamicStatement`。 |
| `CalAnomaly.py`：`CalAnomaly.__init__()` / `CalDisorder` / `CalAbloom` | 结算后的 `AnomalyBar.current_ndarray`、`enemy_obj`、`dynamic_buff`、`activated_by.skill.char_obj`；`CalDisorder` 还读取 copied `Disorder.remaining_tick()`、`disorder_basic_mul_map`、`ano_extra_bonus[-1]`、`StunMul` 失衡字段。 | 异常伤害、防御、抗性、易伤、失衡易伤、特殊乘区、主动暴击区输入，以及 `CalDisorder` base / extra / stun 公式输入。 | guarded maintenance。 | `test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()` 记录 enemy dynamic lists 进入 retained `MulData`；`test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()` 锁定 `CalDisorder` formula 输入与 copied payload sentinel 分离；但生产公式和 copied-output/report 语义仍不替换。 |
| `AnomalyBar.__get_duration_enemy_buffs()` / dot、freeze-like duration reads | runtime view 或 legacy enemy dynamic list。 | 异常持续时间和 dot/freeze-like 状态相邻读取。 | guarded maintenance。 | 本 PRD 不迁移异常持续时间读取；后续需要单独覆盖 runtime view、legacy fallback、dot 列表和 freeze-like 分支。 |
| `Load/LoadDamageEvent.py` dot / freez-like continuation | 调用方显式传入当前 Schedule 队列。 | dot 时间触发、命中后 dot、碎冰类效果继续生成伤害事件。 | blocker-only follow-up。 | 属于 Load/Schedule event-router 方向，不是 Buff phase-3 formula parity 替换入口。 |

## 当前 PRD US-021 UpdateAnomaly.spawn_output 输出与监听边界刻画

本节只记录 `UpdateAnomaly.spawn_output(...)` mode 0 / 1 / 2 focused characterization；不改 `UpdateAnomaly.py`、`CopyAnomalyForOutput.py`、scheduled publish、dot runtime、runtime command port、handler report payload 或 production formula 语义。

- `test_spawn_output_mode_zero_settles_without_listener_or_scheduled_publish()` 使用未结算 active `AnomalyBar`，证明 mode 0 先 `anomaly_settled()` 再复制 `NewAnomaly`，并保留 `current_ndarray` / `current_effective_anomaly`、`active_by` / `activate_by`、payload sentinel 字段与无 `execute_tick` 语义。
- `test_spawn_output_disorder_modes_broadcast_listener_payload_without_publish()` 覆盖 mode 1 `Disorder` 与 mode 2 `PolarityDisorder`，证明两者同步广播 `DISORDER_SPAWN`，listener payload 即 copied output 本体，并保留 `is_disorder`、`settled`、duration fields、snapshot 非别名和 polarity-only fields。
- 两个测试均用 recording schedule queue 证明 direct `spawn_output(...)` 不做 scheduled publish；`test_update_anomaly_preserves_new_anomaly_then_disorder_order_via_dispatch_port()` 继续保留 `update_anomaly(...)` 层的 anomaly broadcast、disorder broadcast、new anomaly publish、`special_resources(disorder)`、disorder publish 相对顺序。
- `runtime_command_port` 与 pending Buff queue 仍为 fail-fast boundary；dot runtime 仍由既有 `anomaly_effect_active(...)` / `remove_dots_cause_disorder(...)` tests 覆盖，不把 listener broadcast、scheduled publish、dot runtime 或 same-tick Buff writes 合并。

## 当前 PRD US-020 Disorder / PolarityDisorder copied-output payload 刻画

本节只记录 `CopyAnomalyForOutput.Disorder` / `CopyAnomalyForOutput.PolarityDisorder` copied payload focused characterization；不改 `CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、handler report payload、listener broadcast、scheduled publish、runtime port 或 production formula 语义。

- `_COPIED_OUTPUT_PAYLOAD_CASES` 覆盖 plain `Disorder` 与 `PolarityDisorder` 两个 copied kind，共用 settled `AnomalyBar` fixture 和 payload sentinel 字段。
- `test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()` 断言 exact copied class、`active_by` / `activate_by`、`is_disorder`、`settled`、`element_type`、`accompany_dot`、`anomaly_dmg_ratio`、`scaling_factor`、`max_duration` / `last_active` / `remaining_tick()`、`current_effective_anomaly` 与 `current_ndarray` 非别名。
- `PolarityDisorder` case 锁定 `polarity_disorder_ratio` 与 `additional_dmg_ap_ratio=32`；plain `Disorder` case 明确没有 polarity-only 字段。
- 这些断言只提供 retained copied-output payload evidence；`spawn_output(...)` mode 1 / 2 listener broadcast、`UpdateAnomaly.update_anomaly(...)` scheduled publish order、handler report payload、dot runtime 与 runtime write boundaries 均保留给后续故事。

## 当前 PRD US-019 NewAnomaly copied-output payload 刻画

本节只记录 `CopyAnomalyForOutput.NewAnomaly` / `UpdateAnomaly.spawn_output(..., mode_number=0)` copied payload focused characterization；不改 `CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、handler report payload、listener broadcast、scheduled publish、runtime port 或 production formula 语义。

- `test_new_anomaly_spawn_output_copies_active_payload_without_publish()` 使用未结算的 active `AnomalyBar`，经 `spawn_output(..., mode_number=0)` 触发 `anomaly_settled()` 后复制为 `NewAnomaly`。
- 断言 copied `current_ndarray` 非别名、`current_effective_anomaly`、`element_type`、`anomaly_dmg_ratio`、`scaling_factor`、`max_duration` / `last_active` / `remaining_tick()`、`active_by` / `activate_by`、`accompany_dot` 和 `rename_tag` 均来自 active bar / skill node。
- 断言 mode 0 不触发 listener broadcast，保持 copied payload construction 与 `UpdateAnomaly.update_anomaly(...)` 后续 scheduled publish order 分离。
- 这些断言只提供 retained copied-output payload evidence；`CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、handler report payload、`ScheduleDispatchPort`、listener broadcast、dot runtime 与 runtime write boundaries 均保留。

## 当前 PRD US-016 CalAbloom 公式输入刻画

本节只记录 `CalAbloom.__init__(...)` 的 focused characterization；不改 `CalAnomaly.py`、`Calculator.py`、`CopyAnomalyForOutput.py`、Abloom handler report payload、listener broadcast、scheduled publish 或 runtime port 语义。

- `_CAL_ABLOOM_ORACLE_CASES` 复用当前 `CalAnomaly` physical / fire retained multiplier oracle，分别覆盖物理主动暴击 / 强击防御字段参与和非物理主动暴击 neutral 边界。
- `test_cal_abloom_formula_inputs_and_fixture_blockers()` 使用 live `DirgeOfDestinyAnomaly` copied object，断言 formula 读取 copied `current_ndarray`、retained `MultiplierData.dynamic`、`anomaly_dmg_ratio`、`scaling_factor` 和 inherited final multiplier vector。
- `schedule_priority`、`rename_tag`、`accompany_dot` 只作为 output-only sentinel / fixture blocker 字段保留在 copied payload 上；本 story 不把这些字段纳入 formula 期望，也不覆盖 Abloom handler report payload parity。
- 这些断言只提供 retained formula oracle evidence；`CalAnomaly.py`、`CalAbloom`、`Calculator.py`、`CopyAnomalyForOutput.py`、handler report payload 与事件发布生产语义均保留。

## 当前 PRD US-014 CalDisorder 紊乱公式刻画

本节只记录 `CalDisorder.cal_disorder_base_dmg(...)`、`cal_disorder_extra_mul(...)` 与 `cal_disorder_stun(...)` 的 focused characterization；不改 `CalAnomaly.py`、`Calculator.py`、`CopyAnomalyForOutput.py`、handler broadcast / report payload 或 scheduled publish 语义。

- `_CAL_DISORDER_ORACLE_CASES` 按 `element_type` 0-6 覆盖 physical / fire / ice / electric / ether / auric-ink / auric-ether 的 remaining tick 与 floor 分支，固定 `all_disorder_basic_mul` + element-specific disorder basic multiplier 叠加。
- `test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()` 使用 live `Disorder` copied object，断言 formula 读取 copied `current_ndarray` / `remaining_tick()`、retained `MultiplierData.dynamic` 中的 `disorder_dmg_mul` / `stun_res` / `received_stun_increase`，并用 `schedule_priority`、`rename_tag`、`accompany_dot`、`anomaly_dmg_ratio` sentinel 字段证明 listener-facing copied payload 字段不进入 formula 期望。
- 这些断言只提供 retained formula oracle evidence；`CalAnomaly.py`、`CalDisorder`、`CalPolarityDisorder`、`CalAbloom`、`CopyAnomalyForOutput.py`、handler report payload 与事件发布生产语义均保留。

## 当前 PRD US-013 CalAnomaly 最终乘区与缩放刻画

本节只记录 `CalAnomaly.set_final_multipliers(...)` 与 `cal_anomaly_dmg(...)` 的 focused characterization；不改 `CalAnomaly.py` 公式、不替换 `MulData` / `MultiplierData`、不改 `AnomalyBar.current_ndarray` 写入或 copied-output 路径。

- `_CAL_ANOMALY_FINAL_MULTIPLIER_ORDER` 锁定最终向量顺序：`base_dmg`、`dmg_bonus`、`am_mul`、`k_level`、`anomaly_bonus`、`active_crit`、`def_mul`、`res_mul`、`vulnerability_mul`、`snapshot_impact`、`snapshot_stun_bonus`、`stun_vulnerability`、`special_mul`。
- `test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()` 继续使用 live `CalAnomaly`，同时对物理与火属性 case 使用非默认 `scaling_factor`，证明 `cal_anomaly_dmg()` 先对完整最终乘区取积，再除回 snapshot impact / stun bonus，最后乘上 `AnomalyBar.scaling_factor`。
- 这些断言只提供 retained formula oracle evidence；`CalAnomaly.py`、`CalDisorder`、`CalPolarityDisorder`、`CalAbloom` 和 copied-output 生产语义均保留。

## 当前 PRD US-012 CalAnomaly 乘区输入刻画

本节只记录 `CalAnomaly` 主动暴击、防御、抗性、易伤、失衡易伤与特殊乘区输入的 focused characterization；不改 `CalAnomaly.py` 公式、不替换 `MulData` / `MultiplierData`、不改 `AnomalyBar.current_ndarray` 写入或 copied-output 路径。

| 用例 | settled snapshot 输入 | dynamic statement / enemy 输入 | 本轮证据 |
| --- | --- | --- | --- |
| `physical-active-crit-defense-res-vulnerability-stack` | `virtual_character_level=60`、snapshot 穿透率 / 穿透值 / 抗性穿透、impact、stun bonus。 | 物理抗性、敌方防御、强击暴击率 / 暴伤、强击无视防御、减防、穿透、抗性降低 / 穿透、物理 / 全易伤、失衡易伤、特殊乘区。 | 证明物理异常主动暴击区、`cal_def_mul(...)` 的 snapshot + dynamic 穿透合成、`cal_res_mul(...)` 的 snapshot_res_pen、`cal_dmg_vulnerability(...)` 和 `cal_stun_vulnerability(...)` 继续来自 retained `MulData`。 |
| `fire-res-vulnerability-keeps-active-crit-neutral` | `virtual_character_level=40`、snapshot 穿透率 / 穿透值 / 抗性穿透、impact、stun bonus。 | 火抗性、敌方防御、非物理元素下应被忽略的强击暴击 / 无视防御字段、减防、穿透、火抗性降低 / 穿透、火 / 全易伤、全时段失衡易伤。 | 证明非物理 `CalAnomaly.cal_active_crit(...)` 保持 `1.0`，且防御、抗性和易伤仍按当前元素从 retained dynamic snapshot 取值。 |

`test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()` 同时断言 `calculator.data` 仍是 `MultiplierData`、`judge_node` 仍是当前 `AnomalyBar`、`calculator.dmg_sp is anomaly_bar.current_ndarray`，并显式命名 settled snapshot 字段与 dynamic statement 字段，避免把 reader seam parity 误解为生产公式替换许可。

## US-012 migrated reader seam 回归样本

| 样本 / 文件 | phase-2 来源 | 旧公式 helper | reader seam | 本轮证据 |
| --- | --- | --- | --- | --- |
| `AliceAdditionalAbilityApBonus.py` | P2-A AM/AP migrated reader bucket | `Calculator.AnomalyMul.cal_am(...)` | `CalculatorBuffAttributeReader.read_anomaly_mastery(...)` | `test_migrated_reader_seam_regression_samples_match_retained_helpers[p2a-alice-am]` 证明 reader 输出、reader-built snapshot 和 retained helper 一致。 |
| `JaneCinema1APTransToDmgBonus.py` | P2-A AM/AP migrated reader bucket | `Calculator.AnomalyMul.cal_ap(...)` | `CalculatorBuffAttributeReader.read_anomaly_proficiency(...)` | `test_migrated_reader_seam_regression_samples_match_retained_helpers[p2a-jane-ap]` 证明 AP reader seam 仍匹配 retained helper。 |
| `QingYiAdditionalAbilityStunConvertToATK.py` | P2-B impact / crit migrated reader bucket | `Calculator.StunMul.cal_imp(...)` | `CalculatorBuffAttributeReader.read_impact(...)` | `test_migrated_reader_seam_regression_samples_match_retained_helpers[p2b-qingyi-impact]` 证明 impact reader seam 仍匹配 retained helper。 |
| `CannonRotor.py` | P2-B impact / crit migrated reader bucket | `Calculator.RegularMul.cal_crit_rate(...)` | `CalculatorBuffAttributeReader.read_full_crit_rate(...)` | `test_migrated_reader_seam_regression_samples_match_retained_helpers[p2b-cannon-rotor-full-crit]` 证明 full crit reader seam 仍保留 received crit rate inclusion。 |
| `Soldier0AnbyCoreSkillCritDMGBonus.py` | P2-B impact / crit migrated reader bucket | `Calculator.RegularMul.cal_personal_crit_dmg(...)` | `CalculatorBuffAttributeReader.read_personal_crit_damage(...)` | `test_migrated_reader_seam_regression_samples_match_retained_helpers[p2b-anby-personal-crit-dmg]` 证明 personal crit damage reader seam 仍排除 received crit damage bonus。 |

- `test_migrated_reader_seam_regression_sample_scope_is_representative()` 锁定上述样本文件均来自 root workspace，且不来自 `.codex_worktrees/`。
- P2-A through P2-G 保持已完成 guarded buckets；本节只增加 formula parity suite 回归样本，不重开生产迁移、不删除 `Calculator.py` / `MultiplierData` / `DynamicStatement`，也不替换 runtime write、listener broadcast 或 scheduled publish 边界。

## 后续非目标

- 不在 US-002 替换生产公式、移动计算公式、重写异常结算或删除旧 helper。
- 不把 reader seam 直接推广为新运行时写 facade；same-tick 写仍只走现有 `RuntimeCommandPort` / `LegacyRuntimeCommandAdapter`。
- 不缓存计划事件 dispatch adapter；本清单不改变计划事件发布顺序、同步 listener broadcast 或 runtime write 分层。
