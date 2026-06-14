# Buff公式候选与测试目标清单

更新时间：2026-06-14 13:25 +08:00

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
| Calculator AM/AP/impact/crit/直伤/失衡公式 | `zsim/sim_progress/ScheduledEvent/Calculator.py`：`CalculatorBuffAttributeReader.read_anomaly_mastery()`、`read_anomaly_proficiency()`、`read_impact()`、`read_full_crit_rate()`、`read_personal_crit_rate()`、`read_personal_crit_damage()`；`Calculator.RegularMul.cal_base_dmg()`、`cal_base_attr()`、`cal_dmg_bonus()`、`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()`、`cal_sheer_dmg_bonus()`；`Calculator.AnomalyMul.cal_am()`、`cal_anomaly_buildup()`、`cal_base_damage()`、`cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ap()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()`；`Calculator.StunMul.cal_imp()`、`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_cal_am_retained_multiplier_data_oracle_rows()`、`test_cal_ap_retained_multiplier_data_oracle_rows()`、`test_cal_imp_retained_multiplier_data_oracle_rows()`、`test_stun_array_output_contract_preserves_field_order_dtype_and_product()`、`test_regular_mul_array_outputs_preserve_field_order_dtype_and_crit_split()`、`test_calculator_regular_mul_branch_matrix_characterizes_selected_methods()`、`test_regular_mul_retained_sheer_base_attr_requires_char_instance_conversion_rate()`、`test_calculator_am_ap_impact_formula_boundaries_remain_retained_compatibility()`、`test_calculator_attribute_formula_boundaries_remain_retained_compatibility()`；`tests/simulator/test_migrated_am_ap_reader_guardrail.py`；`tests/simulator/test_migrated_p2b_reader_guardrail.py`；`tests/simulator/test_full_crit_event_adjacent_reader.py`。 | AM/AP/impact 已完成 bounded implementation；`Calculator.RegularMul.cal_crit_rate(data)` 已完成 behavior-preserving helper-seam implementation / handoff no-op verification；Stun array、RegularMul arrays 与 selected RegularMul branch matrix 已完成 characterization / retained oracle；RegularMul sheer conversion 已有 retained runtime-dependency oracle，但 reader-built `_CalculatorReadSnapshot` contract 和 registered-route sample 条件仍使 production proposal 保持 No-Go。后续仍需从 copied-output handler/report payload parity、registered-team behavior sample eligibility、remaining RegularMul branches / retained-only sheer follow-up、`StunMul.get_stun_array()` follow-up 或 P2-A through P2-G guarded maintenance 中选择 exact bounded characterization / proposal slice；不得外推为 broad `Calculator.py` / `CalAnomaly.py` rewrite。 | `uv run pytest tests/simulator/test_buff_attribute_reader.py -q`；`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity`；retained reader / guardrail gate 为 `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads`；触达 copied-output / event-runtime 分层时追加 `implicit-events`。 |
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

## Current copied-output bounded proposal PRD US-008 final handoff

结论：Conditional Go with named blockers for one later bounded copied-output handler/report implementation PRD。当前 proposal package 已命名 exact future production diff candidates、focused tests、scoped mypy targets、registered-route sample conditions、rollback anchors、stop conditions 和 reviewer questions；它不授权 immediate broad production rewrite。

US-008 retained gates and validation expectations：

- Current docs-only handoff gate：edited Chinese Markdown UTF-8 / mojibake scan、Ralph JSON sanity、active story typecheck gate，以及 progress / checkpoint reviewer verdict。
- Future implementation PRD gate：focused copied-output pytest `uv run pytest tests/simulator/test_buff_attribute_reader.py tests/simulator/test_update_anomaly_dispatch.py tests/simulator/test_anomaly_handler_runtime_view.py -q`，并串行保留 `formula-parity`、`calculator-reads`、`implicit-events`。
- Future scoped mypy targets：`CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、anomaly / disorder / polarity / abloom handlers、`test_buff_attribute_reader.py`、`test_update_anomaly_dispatch.py` 和 `test_anomaly_handler_runtime_view.py`，以 validation profile 的当前配置为准。
- Main-loop consistency remains conditional：只有 live production semantic diff、真实 registered-route JSON、nonzero relevant anomaly/copied-output event count、matching total damage 和 unchanged Buff timeline differences 同时存在时才作为证据；validation-only team / APL 仍禁止。

Compatibility retained：

- `CopyAnomalyForOutput.py` constructors、`UpdateAnomaly.spawn_output(...)`、`UpdateAnomaly.update_anomaly(...)` scheduled publish order、anomaly / disorder / polarity / abloom handler paths、listener broadcast、scheduled publish、dot runtime registration/removal、same-tick runtime writes、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`LegacyBuffRuntimeFacade`、old containers、legacy `buff_add()` / `KickOutBuff()`、`Calculator.py` / `CalAnomaly.py` retained formula snapshots、`MultiplierData` / `MulData` / `DynamicStatement`、`AnomalyBar.current_ndarray`、AM/AP/impact helper implementation、`cal_res_pen()` selector extraction、array / RegularMul / sheer characterization evidence remain retained unless a later PRD explicitly proves an exact bounded diff.

Rollback anchors：

- Source anchors：`CopyAnomalyForOutput.py` copied payload constructors、`UpdateAnomaly.spawn_output(...)` modes 0 / 1 / 2 and missing-`polarity_ratio` failure path、`UpdateAnomaly.update_anomaly(...)` retained publish order、anomaly / disorder / polarity / abloom handlers。
- Test anchors：copied payload constructor tests, spawn-output listener/publish separation tests, update-anomaly dispatch order tests, handler report payload parity tests, focused copied-output pytest, serial retained validation profiles, Ralph proposal packet, evidence ledger, campaign dashboard and replacement notes。

Same-phase candidate pool：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| Copied-output bounded implementation PRD | Conditional Go with named blockers. | May be the current default next PRD, but must select one coherent handler/report slice and stop on formula, validation-runner, registered-team fixture, old-container deletion, port/facade implementation, or layer-merge needs. |
| Registered-team behavior sample eligibility | Policy retained. | Use only for a future live semantic diff with real registered route and nonzero relevant copied-output/anomaly counts. |
| `Calculator.RegularMul` remaining branches / retained-only sheer follow-up | Characterization evidence remains No-Go for production proposal. | Reopen only for a named branch or sheer contract gap with deterministic oracle, rollback anchors and registered-sample conditions. |
| `Calculator.StunMul.get_stun_array()` / array-output follow-up | Array contract characterized; no production replacement authorization. | Reopen only for a named array-output follow-up, focused regression or proposal-readiness packet. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol or gate. |

Next default PRD：generate one later bounded copied-output handler/report implementation PRD from the proposal package. After that implementation completes, reselect from the same-phase candidate pool instead of automatically producing another copied-output follow-up.

## Current copied-payload handler/report bounded implementation PRD US-008 final handoff

结论：Implemented with retained boundaries。当前 implementation PRD 已完成 copied-payload constructor boundary、`UpdateAnomaly.spawn_output(...)` mode boundary、scheduled publish / dot runtime / debuff layer-preservation anchors、handler report payload boundary、scoped mypy coverage 和 registered-route No-Go verdict；它不授权 broad `Calculator.py` / `CalAnomaly.py` rewrite、validation-runner rewrite、registered-team fixture creation、old-container deletion、listener / scheduled publish / dot runtime / same-tick runtime write layer merge 或 retained compatibility 删除。

Implementation result：

- `CopyAnomalyForOutput.py` copied-payload constructors now have explicit source-copy / payload-install / explicit-context override / subclass-owned field boundaries, while retaining copied `current_ndarray`, `current_effective_anomaly`, `Disorder.is_disorder`, `PolarityDisorder` polarity fields, and `DirgeOfDestinyAnomaly.anomaly_dmg_ratio` behavior.
- `UpdateAnomaly.spawn_output(...)` now keeps invalid mode / missing `polarity_ratio` failure before copied-output construction, listener broadcast, scheduled publish, or source settlement side effects.
- Layer-preservation tests keep direct `spawn_output(...)` separated from scheduled publish, synchronous listener broadcast, dot runtime registration/removal, debuff writes, pending Buff queue writes, and same-tick runtime command writes.
- Handler report payload evidence keeps anomaly, disorder, polarity disorder, and abloom report fields separate from listener settlement broadcast, disorder stun update, and anomaly `RuntimeCommandPort.settle_buffs(...)`.

US-008 verifier evidence：

- `uv run pytest tests/simulator/test_buff_attribute_reader.py tests/simulator/test_update_anomaly_dispatch.py tests/simulator/test_anomaly_handler_runtime_view.py -q` exited `0` with `172 passed`.
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` exited `0`：base simulator `2 passed`、isolated teams `3 passed`、focused formula-parity suite `140 passed`、scoped mypy `Success: no issues found in 9 source files`.
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile calculator-reads` exited `0`：base simulator `2 passed`、isolated teams `3 passed`、focused calculator-reads suite `240 passed`、scoped mypy `Success: no issues found in 22 source files`.
- `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile implicit-events` exited `0`：base simulator `2 passed`、isolated teams `3 passed`、focused implicit-event suite `247 passed`、scoped mypy `Success: no issues found in 90 source files`.
- `uv run python scripts/run_buff_refactor_validation.py` exited `0`：base simulator `2 passed`、isolated teams `3 passed`、focused lifecycle suite `18 passed`、scoped mypy `Success: no issues found in 9 source files`.
- `uv run pytest tests/simulator/test_main_loop_consistency.py -q` exited `0` with `6 passed`; retained-vs-retained main-loop sample remains skipped because there is no live production semantic diff and no target copied-output payload route to prove.

Retained gates and compatibility retained：

- Retained gates：future formula / reader work continues to run `formula-parity` / `calculator-reads` serially；future copied-output / event / dispatch / runtime / listener work runs `implicit-events`；future lifecycle / runtime-write / validation-runner behavior changes run the default profile；future live semantic diff only adds main-loop consistency when a real registered route has nonzero relevant copied-output/anomaly counts.
- Compatibility retained：`Calculator.py` / `CalAnomaly.py` formulas, `MultiplierData` / `MulData` / `DynamicStatement`, `AnomalyBar.current_ndarray`, old containers, legacy `buff_add()` / `KickOutBuff()`, `ScheduleDispatchPort`, listener broadcast, dot runtime registration/removal, `RuntimeCommandPort`, `LegacyRuntimeCommandAdapter`, `LegacyBuffRuntimeFacade`, AM/AP/impact helper implementation, `cal_res_pen()` selector extraction, and array / RegularMul / sheer characterization evidence all remain retained.

Same-phase candidate pool：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| Registered-team behavior sample eligibility | Policy retained; `薇薇安物理队` remains only a future copied-output/anomaly candidate after route preflight. | Use only for future live semantic diff with real registered-route JSON and nonzero relevant copied-output/anomaly counts; do not create validation-only teams/APLs. |
| `Calculator.RegularMul` remaining branches / retained-only sheer follow-up | Characterization evidence remains No-Go for production proposal. | Reopen only for a named branch or sheer contract gap with deterministic oracle, rollback anchors and registered-sample conditions. |
| `Calculator.StunMul.get_stun_array()` / array-output follow-up | Array contract characterized; no production replacement authorization. | Reopen only for a named array-output follow-up, focused regression or proposal-readiness packet. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol or gate. |
| Retained compatibility / blocker-only reopen | No new coupling classification in this implementation handoff. | Reopen only with root-workspace source, guardrail, focused test, validation, or real registered-route blocker evidence. |

Next default PRD：Phase-3 same-phase candidate selection / bounded proposal PRD。Choose one exact bounded slice from the same-phase pool, record focused tests, scoped mypy, rollback anchors, registered sample conditions, retained gates and non-goals, and do not directly convert the new Markdown PRD into `scripts/ralph/prd.json` in the same generation step.

## Current candidate-selection PRD US-004 exact bounded candidate decision

结论：选择 `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array output 作为下一步 bounded proposal contract 的唯一候选面；production implementation 与 main-loop sample 仍为 No-Go，直到后续 live semantic diff 证明真实注册路线、相关 stun / impact 非零事件或公式计数、显式 stop tick、runtime labels、total damage comparison 与 Buff timeline comparison。

Selected files / symbols：

- `zsim/sim_progress/ScheduledEvent/Calculator.py`：`Calculator.StunMul.get_stun_array()`、`Calculator.cal_stun()`。
- `tests/simulator/test_buff_attribute_reader.py`：`test_stun_array_output_contract_preserves_field_order_dtype_and_product()`。
- 明确分离：`Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`、所有 `Calculator.RegularMul` branch、retained-only sheer runtime conversion。

Focused tests / scoped mypy / retained gates：

- Focused pytest：`uv run pytest tests/simulator/test_buff_attribute_reader.py::test_stun_array_output_contract_preserves_field_order_dtype_and_product -q`。
- Scoped mypy / formula gate：`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity`，沿用该 profile 中的 `Calculator.py`、`CalAnomaly.py`、anomaly-bar files、selected reader callsites、validation runner 与 `test_buff_attribute_reader.py` scope。
- Retained gates：formula / reader work 继续保留 `formula-parity` 与 `calculator-reads`；触达 copied-output、event、dispatch/runtime 或 listener 分层时才追加 `implicit-events`。

Rollback anchors / stop conditions：

- Rollback anchors：当前 `get_stun_array()` 五字段顺序、`np.float64` dtype、`Calculator.cal_stun()` 的 `np.prod(...)` consumer、当前 `cal_imp()` helper implementation、`MultiplierData` / `DynamicStatement`、focused test、validation profile wiring、old containers、copied-output constructors、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 与 `LegacyBuffRuntimeFacade`。
- Stop conditions：字段顺序 / dtype / product 行为不匹配、合并 `cal_imp()` helper、扩大 public contract、broad `Calculator.py` / `CalAnomaly.py` rewrite、RegularMul branch 打包、为 sheer 强行加 `_CalculatorReadSnapshot` 或 `char_instance` passthrough、validation-runner rewrite need、缺少真实路线 / 非零计数的 live diff、或 retained gate failure，均产生 No-Go 并停止进入 implementation。

RegularMul / sheer 保留决定：

- 本轮不选择 `RegularMul` branch；full crit、personal crit、personal crit damage、damage vulnerability、stun vulnerability、special multiplier 与 sheer 差异继续分开。
- Retained-only sheer 仍为 No-Go；不得为了 Go 而给 `_CalculatorReadSnapshot` 增加 runtime-only 字段。

## Current candidate-selection PRD US-005 focused oracle / typecheck contract

结论：`Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` 的 verifier contract 已固定为现有本地 oracle nodeid 与 retained validation profiles；本 story 不新增 broad suite、不改 validation runner、不触达 production formula / reader / event-runtime 分层。

Focused pytest contract：

- Exact nodeid：`uv run pytest tests/simulator/test_buff_attribute_reader.py::test_stun_array_output_contract_preserves_field_order_dtype_and_product -q`。
- 该用例锁定 `get_stun_array()` 五字段顺序 `imp`, `stun_ratio`, `stun_res`, `stun_bonus`, `stun_received`，shape `(5,)`，`np.float64` dtype，以及 `Calculator.cal_stun()` 对数组的一次读取和 `np.prod(...)` consumer 行为。
- Runner retained profile 中的 `FORMULA_PARITY_FOCUSED_TEST_TARGETS = ["tests/simulator/test_buff_attribute_reader.py"]` 保持不变；它是 formula oracle profile 的文件级最小门禁，不替代上面的 story-local exact nodeid。

Scoped typecheck / retained gates：

- `formula-parity` 仍通过 `scripts/run_buff_refactor_validation.py` 维护 scoped mypy target：`Calculator.py`、`CalAnomaly.py`、anomaly-bar files、selected BuffXLogic reader files 与 validation runner；该 profile 还追加 focused reader test file。
- `calculator-reads` 仍保留 reader seam、raw-container guardrail、AM/AP guardrail、P2-B guardrail、state sync 与 full-crit event-adjacent reader coverage。
- 本 slice 未改 copied-output、event、dispatch/runtime、listener、lifecycle、same-tick runtime write 或 validation wiring，因此不追加 `implicit-events`；后续若触达这些分层必须串行追加。

Reviewer verdict / non-goals：

- Changed surface 仅限 docs/Ralph evidence/bookkeeping；`Calculator.py`、reader source、copied-output constructors、registered teams/APLs、old Buff containers、dispatch/runtime ports、listener broadcast 与 retained compatibility paths 均保持不变。
- 该 contract 只准备后续 bounded proposal / rollback slice；不授权 production formula replacement、RegularMul 打包、retained-only sheer `_CalculatorReadSnapshot` 扩容或 main-loop sample。

## Current candidate-selection PRD US-006 rollback anchors / stop conditions

结论：`Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` 的 rollback anchors 和 stop conditions 已固定；本 story 仍为 docs-only / Guardrail-first，不改 production formula、reader source、validation runner、registered teams/APLs、copied-output constructors、old containers 或 event/runtime/listener/dot 分层。

Rollback anchors：

- Source methods：`zsim/sim_progress/ScheduledEvent/Calculator.py::Calculator.StunMul.get_stun_array()` 与 `Calculator.cal_stun()`；`Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`、所有 `Calculator.RegularMul` branch 与 retained-only sheer runtime conversion 继续作为分离的 retained boundaries。
- Focused test：`tests/simulator/test_buff_attribute_reader.py::test_stun_array_output_contract_preserves_field_order_dtype_and_product`，锁定五字段顺序、shape、`np.float64` dtype、一次 `get_stun_array()` 调用、`np.prod(...)` product consumer 与 aggregation count。
- Retained docs：本清单、`docs/Buff重构替换说明.md`、`docs/Buff系统重构Checklist.md`、`docs/旧Buff系统耦合审查结果.md`、`docs/Buff重构下阶段计划草稿.md`。
- Validation profiles：focused pytest nodeid、serial `formula-parity`、serial `calculator-reads`，以及未来触达 copied-output / event / dispatch-runtime / listener / dot-runtime / same-tick runtime write 时的 `implicit-events`。

Stop conditions：

- Formula mismatch：数组字段顺序、shape、dtype、字段语义或 `Calculator.cal_stun()` product 行为与 focused oracle 不一致。
- Missing deterministic oracle：未来 diff 没有 exact focused test 锁定 changed field、branch、consumer path、neutral/default row 或 product behavior。
- Missing registered route for live semantic diff：真实注册队伍 / APL 没有在 explicit stop tick 内产生 nonzero relevant stun / impact count；不得创建 validation-only team 或 retained-vs-retained sample。
- Broad interface change / public contract expansion：需要改 public signature、`_CalculatorReadSnapshot`、`BuffRuntimeReadPort`、copied-output payload、report/runtime surface 或 reader/runtime view 才能通过。
- Validation-runner rewrite need：需要重写 runner behavior、help text 或 profile orchestration，而不是复用 focused tests 与 retained profiles。
- Old-container deletion：需要删除 / 绕过 old Buff containers、legacy `buff_add()` / `KickOutBuff()`、`MultiplierData`、`MulData` 或 `DynamicStatement` 才能通过。
- Layer merge：event queue semantics、synchronous listener broadcasts、dot runtime registration 与 same-tick runtime writes 被合并，或在未被未来 PRD 命名时编辑 `ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort`。

## Current Stun array bounded implementation PRD US-008 final handoff

结论：Implemented / no-op verified at handoff。生产实现已在 US-003 完成：`Calculator.StunMul.get_stun_array()` 委托 `_build_stun_multiplier_array(...)` 负责五字段 `np.float64` array construction，`Calculator.cal_stun()` 仍按原路径读取数组、执行 `np.prod(...)`，并返回 `np.float64`。US-008 只同步 handoff docs、Ralph evidence、checkpoint 和 completion bookkeeping，不再制造额外 source churn，也不回滚该 helper。

Implementation outcome / verifier evidence：

- Source outcome：`zsim/sim_progress/ScheduledEvent/Calculator.py::Calculator.StunMul.get_stun_array()` -> `_build_stun_multiplier_array(...)` -> `Calculator.cal_stun()` 的 flow 保持单一 bounded surface；`Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`、所有 `Calculator.RegularMul` branch 与 retained-only sheer runtime conversion 继续分离。
- Retained verifier evidence：focused reader pytest exited `0` with `141 passed`；`formula-parity` exited `0` with focused reader suite `141 passed` and mypy clean on `9 source files`；`calculator-reads` exited `0` with focused reader suite `241 passed` and mypy clean on `22 source files`。
- Current US-008 docs-only gate：story-scoped typecheck, JSON sanity, UTF-8 / mojibake scan, `git diff --check`, and campaign dashboard refresh must pass before `passes=true`。

Retained gates / registered sample decision：

- Formula / reader follow-up gates：future formula or reader work keeps serial `formula-parity` then `calculator-reads` unless the active story proves a narrower docs-only gate is sufficient。
- Event/runtime follow-up gate：future copied-output / event / dispatch / runtime / listener / dot-runtime / same-tick write work adds `implicit-events`。
- Registered behavior sample：still conditional No-Go for this implementation handoff。Run main-loop consistency only for a future live production semantic diff with real registered route JSON, explicit stop tick, runtime labels, matching total damage, unchanged Buff timeline differences, and nonzero relevant stun / formula / event counts；do not create validation-only teams/APLs。

Rollback anchors：

- Source anchors：`Calculator.StunMul.get_stun_array()`、`_build_stun_multiplier_array(...)`、`Calculator.cal_stun()`、focused Stun array oracle、retained Buff handoff docs、`formula-parity`、`calculator-reads`、conditional `implicit-events`。
- Retained compatibility anchors：`Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`、all `Calculator.RegularMul` branches、retained-only sheer、`MultiplierData`、`MulData`、`DynamicStatement`、old containers、copied-output constructors、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort`、`LegacyBuffRuntimeFacade`。

Stop conditions：

- Reopen or rollback only if focused Stun array oracle, retained profile, story-scoped typecheck, or root-workspace source evidence names a concrete regression in field order, dtype, shape, product consumer, helper delegation, or validation profile scope。
- Stop and split if the next proposal needs broad `Calculator.py` / `CalAnomaly.py` rewrite、RegularMul bundling、retained-only sheer `_CalculatorReadSnapshot` expansion、registered-team fixture creation、validation-runner rewrite、old-container deletion、layer merge, or retained compatibility deletion。

Same-phase candidate pool：

| Candidate / boundary | Current status | Next rule |
| --- | --- | --- |
| Registered behavior sample eligibility | Policy retained; no live semantic diff in this PRD. | Use only for future real registered-route evidence with nonzero relevant counts. |
| `Calculator.RegularMul` remaining branches / retained-only sheer follow-up | Still retained / characterized; not resolved by Stun helper implementation. | Reopen only for named exact branch or sheer contract gap with deterministic oracle, rollback anchors, registered-sample conditions, and retained gates. |
| Future `Calculator.StunMul.get_stun_array()` follow-up | Current helper extraction implemented and verified. | Reopen only if future evidence names a new array-output gap, focused regression, or proposal-readiness packet. |
| P2-A through P2-G guarded maintenance | Completed guarded buckets. | Reopen only on concrete guardrail / focused test / validation evidence naming the failed file, symbol, or gate. |
| Retained compatibility / blocker-only reopen | No new coupling classification in this implementation handoff. | Reopen only with root-workspace source, guardrail, focused test, validation, or real registered-route blocker evidence. |

Next default PRD：Phase-3 same-phase candidate selection / bounded proposal PRD。Choose one exact bounded slice from the retained pool, record focused tests, scoped mypy, rollback anchors, registered-sample conditions, retained gates and non-goals, and do not directly convert the new Markdown PRD into `scripts/ralph/prd.json` in the same generation step。

## Current route reconciliation PRD US-001

结论：stale Stun default 已关闭。`Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` selected implementation 的 handoff 状态是 implemented / no-op verified；它只在新证据命名 focused oracle gap、validation failure、root-workspace source regression 或 proposal-readiness packet 时重开。当前默认路线改为 `Calculator.RegularMul` remaining branch bounded proposal-readiness：先刷新 branch matrix，再选择一个 exact candidate 或记录 No-Go。

Completed evidence / retained pool：

| Surface | Current status | Reopen rule |
| --- | --- | --- |
| Copied-output handler/report implementation | Implemented with retained copied-payload / listener / scheduled-publish / dot-runtime boundaries. | 只有 copied-output focused regression、guardrail failure、validation failure 或 named production semantic diff 才重开。 |
| `Calculator.AnomalyMul.cal_res_pen()` | Implemented as behavior-preserving selector extraction. | 不作为下一默认 PRD 重开；只有 focused regression、validation failure 或明确语义 follow-up 才重开。 |
| AM/AP/impact helper implementation | AM baseline retained；AP 委托 `_calculate_anomaly_proficiency(...)`；impact 委托 `_calculate_impact(...)`。 | 不因 RegularMul work 回滚；只有 named helper-family evidence 才重开。 |
| Selected Stun implementation | Implemented / no-op verified at handoff；`get_stun_array()` 委托 `_build_stun_multiplier_array(...)`。 | 只按 named Stun evidence 重开，不作为默认 backlog。 |
| P2-A through P2-G guarded buckets | Completed guarded maintenance buckets. | 只由 concrete guardrail / focused test / validation evidence naming failed file, symbol, or gate 触发。 |

Current production conclusions exclude `.codex_worktrees/`, `scripts/ralph/archive/`, `scripts/ralph/run-logs/`, logs, and generated history; use root-workspace source, focused tests, and retained validation profiles for future decisions.

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

## Current RegularMul Remaining Branch Matrix

本矩阵属于当前 RegularMul remaining-branch bounded proposal PRD。它只把 `Calculator.RegularMul` 剩余候选绑定到现有 deterministic oracle、缺口、reader-snapshot 依赖、registered-route 条件和 rollback anchors；不新增生产公式替换授权。每一行都必须作为独立候选审查，除非后续证据证明它们共享同一个 validation profile、rollback path 和 failure mode。保留边界继续包括 `MultiplierData`、`MulData`、`DynamicStatement`、`AnomalyBar.current_ndarray`、copied-output constructors、old Buff containers、`buff_add()`、`KickOutBuff()`、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter` 和 `LegacyBuffRuntimeFacade`。已完成的 Stun array / `Calculator.cal_stun()` 证据不属于本表候选。

### Snapshot-Compatible Branches

| Candidate | Current deterministic oracle evidence | Missing deterministic oracle rows | Reader-snapshot dependency | Registered-route eligibility | Rollback anchors | Current status |
| --- | --- | --- | --- | --- | --- | --- |
| `Calculator.RegularMul.cal_base_dmg()` | `test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[regular-base-dmg-neutral-atk]`、`[regular-base-attr-static-hp]`、`[regular-base-dmg-dynamic-atk]`；`test_calculator_regular_mul_branch_matrix_characterizes_selected_methods[fire-stunned-reader-snapshot]`。 | Production proposal 前仍需补 `base_attr=2` defense、`base_attr=3` AP、非 ATK/HP 的 `extra_damage_ratio` / base damage increase 组合；`base_attr=4` sheer path 必须使用 retained-only table 单独审。 | ATK/HP/DEF/AP 普通直伤可由 `_CalculatorReadSnapshot` 的 static / dynamic / judge node / enemy fields 表达；不得把 `base_attr=4` 混入本行。 | 仅 live production semantic diff 且真实 registered route 命中 direct damage 时运行；docs-only matrix 不运行样本。 | `Calculator.py::RegularMul.cal_base_dmg()` / `cal_base_attr()`、`test_buff_attribute_reader.py` formula table、branch matrix、`formula-parity` / `calculator-reads`。 | Characterized for representative retained oracle；production proposal blocked until exact branch, route, and snapshot plan are named. |
| `Calculator.RegularMul.cal_base_attr()` | `regular-base-dmg-neutral-atk` 覆盖 `base_attr=0`，`regular-base-attr-static-hp` 覆盖 `base_attr=1`；`test_regular_mul_retained_sheer_base_attr_requires_char_instance_conversion_rate()` covers the retained-only `base_attr=4` blocker but does not make it snapshot-compatible. | 缺 `base_attr=2` defense 和 `base_attr=3` AP deterministic rows；`base_attr=4` 还缺 reader-contract solution and real route, not just another numeric row. | `base_attr=0/1/2/3` 可由 snapshot 字段表达；`base_attr=4` 依赖 runtime `char_instance.sheer_attack_conversion_rate` and is excluded from snapshot-compatible proposal rows. | Direct damage route 条件同上；`base_attr=4` sheer conversion 当前没有可用 registered `仪玄` / Yixuan route，禁止创建 validation-only team。 | `cal_base_attr(...)`、`_regular_mul_base_attr()` helper、retained sheer test、`_CalculatorReadSnapshot` field set。 | Partly characterized；only `base_attr=0/1/2/3` may enter a future snapshot-compatible candidate after oracle gaps close. |
| `Calculator.RegularMul.cal_dmg_bonus()` | `regular-multipliers-neutral-zero-boundary`、`regular-dmg-bonus-character-field-stack`、branch matrix rows覆盖 element / trigger / label / all damage bonus 的当前代表组合。 | 若选为 production candidate，需要补 physical / ice / electric / ether element rows、主要 trigger 类型和 label branch 的最小 cross-product；不要一次展开成全组合爆炸。 | Snapshot-compatible，依赖 `judge_node.element_type`、`trigger_buff_level`、skill labels 和 dynamic bonus fields。 | 只在 production diff 改变 live damage multiplier 且已注册队伍命中对应 element / trigger route 时追加 main-loop sample。 | `cal_dmg_bonus()`、formula table cases、branch matrix、`CalculatorBuffAttributeReader` read context。 | Characterized as retained oracle；proposal still needs one exact branch selection. |
| `Calculator.RegularMul.cal_crit_rate()` | `regular-crit-received-boundary`、`test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers[over-one-full-crit-received-boundary]`、`test_p2b_full_crit_rate_includes_received_bonus_but_personal_excludes()`、`test_calculator_regular_mul_crit_formula_families_preserve_received_boundaries()`。 | US-004 已补 over-100% full crit focused row；current implementation PRD 已把 `cal_crit_rate(data)` 收敛到 `_calculate_full_crit_rate(...)` helper seam；`cal_crit_expect()` / crit-balancing caller semantics 仍不在本行授权范围内。 | Snapshot-compatible，必须保留 full crit 包含 `crit_rate_received_increase`。 | Direct damage / crit route 条件成立才运行；样本不得替代 focused oracle。 | `cal_crit_rate()`、`_calculate_full_crit_rate(...)`、P2-B crit reader tests、formula table `regular-crit-received-boundary`。 | Implemented / no-op verified at current handoff; no longer default implementation backlog. Live sample remains conditional No-Go until future live semantic diff and real route evidence prove nonzero selected full-crit formula relevance and nonzero `crit_rate_received_increase`. |
| `Calculator.RegularMul.cal_personal_crit_rate()` | `regular-crit-received-boundary`、P2-B full / personal crit parity tests、crit family boundary test。 | 若要替换生产公式，需补 personal-only rows 与 full crit 对照，证明永远排除 received crit rate。 | Snapshot-compatible，必须保留 personal crit 排除 received bonus。 | 同 direct crit route；只有生产语义 diff 才需要。 | `cal_personal_crit_rate()`、reader `read_personal_crit_rate()` parity tests。 | Characterized；retained boundary. |
| `Calculator.RegularMul.cal_crit_dmg()` | `regular-crit-received-boundary` 和 crit family boundary test覆盖 full crit damage 包含 received damage bonus。 | 缺 trigger-label crit damage branch 的 deterministic row；若候选触及 label branch，先补最小 row。 | Snapshot-compatible；full crit damage must include `received_crit_dmg_bonus`。 | Direct crit route 条件成立才运行。 | `cal_crit_dmg()`、`regular-crit-received-boundary`、crit family boundary tests。 | Characterized for received boundary；label branch remains oracle gap. |
| `Calculator.RegularMul.cal_personal_crit_dmg()` | `regular-crit-received-boundary`、`test_p2b_parity_fixture_matches_old_personal_crit_damage_helper()`、`test_p2b_personal_crit_damage_excludes_received_crit_damage_bonus()`、crit family boundary test。 | 若生产替换，需补 field / flat / received 对照 rows，且保留 personal 排除 received damage bonus。 | Snapshot-compatible；reader path already asserts personal crit damage parity。 | Direct crit route 条件成立才运行。 | `cal_personal_crit_dmg()`、reader `read_personal_crit_damage()` parity tests。 | Characterized；retained boundary. |
| `Calculator.RegularMul.cal_defense_mul()` | `regular-multipliers-neutral-zero-boundary`、`regular-defense-res-vulnerability-received-stack`、branch matrix rows覆盖 normal defense / pen / reduction；sheer `diff_multiplier=4` returns `1.0` but remains tied to the retained-only sheer path. | Production proposal 前需补 attacker-level clamp / representative level row；`cal_recipient_def()` addon parameters 不在本 surface 替换范围内，除非另开候选。 | Snapshot-compatible for non-sheer；sheer route skips defense multiplier but still couples through `base_attr=4` elsewhere。 | Direct damage route 条件成立才运行；registered sample 必须能观察 defense-affecting damage route。 | `cal_defense_mul()`、`cal_recipient_def()` source anchor、formula table defense stack row、branch matrix。 | Characterized；proposal needs exact defense candidate and rollback scope. |
| `Calculator.RegularMul.cal_res_mul()` | `regular-multipliers-neutral-zero-boundary`、`regular-defense-res-vulnerability-received-stack`、branch matrix rows覆盖 fire / ether representative resistance、all decrease / all pen。 | 仍缺 physical / ice / electric deterministic rows and `snapshot_res_pen` override row；frost / element aliasing 不得从 anomaly `cal_res_pen()` 外推。 | Snapshot-compatible，依赖 `enemy_obj` element resistance fields and dynamic res decrease / pen fields。 | Direct damage route 条件成立才运行；必须证明 route 命中目标 element。 | `cal_res_mul()`、formula table res stack rows、branch matrix、registered-route decision matrix。 | Characterized for representative elements；blocked for broad production replacement. |
| `Calculator.RegularMul.cal_dmg_vulnerability()` | `regular-multipliers-neutral-zero-boundary`、`regular-defense-res-vulnerability-received-stack`、branch matrix rows覆盖 element vulnerability + all vulnerability。 | 仍缺 physical / ice / electric deterministic rows；若候选只选一个 element，应只补该 element。 | Snapshot-compatible，依赖 `dynamic.<element>_vulnerability` and `all_vulnerability`。 | Direct damage route 条件成立才运行；必须绑定 element / skill route。 | `cal_dmg_vulnerability()`、formula table vulnerability rows、branch matrix。 | Characterized for representative rows；proposal needs named element / route. |

### Retained-Only Sheer Branch

| Candidate | Current deterministic oracle evidence | Missing deterministic oracle rows | Reader-snapshot dependency | Registered-route eligibility | Rollback anchors | Current status |
| --- | --- | --- | --- | --- | --- | --- |
| `Calculator.RegularMul.cal_sheer_dmg_bonus()` with companion `cal_base_attr(..., base_attr=4)` | Branch matrix `[sheer-retained-only]` expects `1.45` for `diff_multiplier=4`；`test_regular_mul_retained_sheer_base_attr_requires_char_instance_conversion_rate()` proves `cal_base_attr(..., 4)` depends on `char_instance.sheer_attack_conversion_rate` while `cal_sheer_dmg_bonus()` itself remains a simple snapshot-compatible multiplier. | Production proposal 仍缺 architecture-approved reader-contract plan for runtime `char_instance.sheer_attack_conversion_rate` and real registered sheer route；do not close by adding only another numeric row. | `cal_sheer_dmg_bonus()` alone is snapshot-compatible；the surrounding sheer damage path is retained-only because base attr conversion requires runtime `char_instance`, which `_CalculatorReadSnapshot` does not carry. | 当前 No-Go：无真实 registered `仪玄` / Yixuan route evidence；禁止 validation-only team。 | `cal_sheer_dmg_bonus()`、`cal_base_attr(..., 4)`、retained sheer test、branch matrix、reader snapshot field set、registered-route audit docs。 | Characterized but not proposal-ready; remains retained-only until both reader-contract and registered-route blockers close. |

## US-003 selected RegularMul candidate decision

结论：选择 `Calculator.RegularMul.cal_crit_rate()` 作为唯一 exact candidate，供后续 bounded proposal / oracle-gap slice 继续推进。本结论只选择候选，不授权生产公式替换；`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()`、`cal_crit_expect()`、damage bonus / defense / resistance / vulnerability / base damage / retained-only sheer / array output 都保持分离边界。

| Contract area | US-003 decision |
| --- | --- |
| Exact source symbols | Selected source: `zsim/sim_progress/ScheduledEvent/Calculator.py::Calculator.RegularMul.cal_crit_rate(data)`；reader anchor: `CalculatorBuffAttributeReader.read_full_crit_rate(context)`；snapshot anchor: `_CalculatorReadSnapshot` carrying `static.crit_rate`, `dynamic.crit_rate`, `dynamic.field_crit_rate`, and `dynamic.crit_rate_received_increase` through `MultiplierData`-compatible fields. |
| Full vs personal crit boundary | Full crit rate must include `crit_rate_received_increase`。Personal crit rate remains a retained contrast boundary through `Calculator.RegularMul.cal_personal_crit_rate(data)` / `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` and must continue to exclude received crit rate. This story does not select personal crit as a production candidate. |
| Focused tests | Retain `tests/simulator/test_buff_attribute_reader.py::test_migrated_reader_seam_regression_samples_match_retained_helpers[regular-crit-received-boundary]`, `::test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers[baseline]`, `[field-buff]`, `[flat-buff]`, `[received-enemy-debuff]`, `[over-one-full-crit-received-boundary]`, `[no-buff]`, `::test_p2b_full_crit_rate_includes_received_bonus_but_personal_excludes`, and `::test_calculator_regular_mul_crit_formula_families_preserve_received_boundaries[received-fields-excluded-from-personal-values]` as the focused oracle / reader proof set. |
| Scoped typecheck targets | Retain `formula-parity` scoped mypy targets: `zsim/sim_progress/ScheduledEvent/Calculator.py`, `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`, `zsim/sim_progress/anomaly_bar/__init__.py`, `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`, `zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`, `zsim/sim_progress/Buff/BuffXLogic/BranchBladeSongCritDamageBonus.py`, `zsim/sim_progress/Buff/BuffXLogic/TimeweaverDisorderDmgMul.py`, `scripts/run_buff_refactor_validation.py`, and focused mypy for `tests/simulator/test_buff_attribute_reader.py`. |
| Retained validation gates | `uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity` is the required current retained gate. `calculator-reads` remains required if a later story changes reader seams, snapshot construction, or P2-A / P2-B reader guardrails. `implicit-events`, lifecycle, and main-loop consistency remain conditional and are not evidence for this docs-only candidate decision. |
| Rollback anchors | Current bodies of `Calculator.RegularMul.cal_crit_rate(data)`, `Calculator.RegularMul.cal_personal_crit_rate(data)`, `CalculatorBuffAttributeReader.read_full_crit_rate(context)`, `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`, `_CalculatorReadSnapshot`, the `regular-crit-received-boundary` formula table row, and this section. |
| Registered sample conditions | Do not run a sample in US-003. A later live sample is allowed only after a production semantic diff exists and a real registered team / APL route proves a direct-damage crit path with explicit `stop_tick`, runtime labels, total damage comparison, relevant nonzero formula or damage count, event counts, and Buff timeline comparison. No validation-only team, fake APL, fixture-only route, or retained-vs-retained sample. |
| Stop conditions | Stop and record No-Go if the candidate requires `_CalculatorReadSnapshot` public contract expansion, validation-runner rewiring, retained compatibility deletion, `cal_crit_expect()` semantics, personal crit replacement, crit damage replacement, damage bonus / defense / resistance / vulnerability cross-product expansion, retained-only sheer route work, old Buff container deletion, or event/runtime/listener layer merge. |

## US-005 selected crit-rate registered sample eligibility audit

本审计属于当前 RegularMul remaining-branch bounded proposal PRD。US-003 已选择 `Calculator.RegularMul.cal_crit_rate(data)`，US-004 已补 focused oracle row；US-005 只审查真实注册队伍 / APL 是否足以支撑 live main-loop consistency sample。结论是 conditional No-Go：当前有真实 direct crit route seed，但没有可证明 `crit_rate_received_increase` 非零的注册路线；本 story 也没有生产语义 diff，因此不运行 `scripts/run_buff_main_loop_consistency.py`。

| Evidence source | Current registered route evidence | Candidate relevance | Verdict |
| --- | --- | --- | --- |
| `tests.teams.TeamRegistry` / `auto_register_teams()` | 直接 registry 命令返回 `青衣雷属性队`、`席德大安比队`、`莱特火属性队`、`薇薇安物理队`；`示例冰属性队` 仍未注册。 | 真实注册路线存在，但不能自动证明 selected full crit 的 received-crit 分量非零。 | 仅作为 route pool；禁止 validation-only team / fake APL。 |
| `莱特火属性队` / `./zsim/data/APLData/莱特-扳机-雨果.toml` | `雨果` 使用 `equip_set4="啄木鸟电音"`；APL 包含 `1291` 行和 `1291|action+=|auto_NA`。`WoodpeckerElectroSet4_NA.special_judge_logic()` 对 trigger level `0` 通过 `CalculatorBuffAttributeReader.read_full_crit_rate(context)` 读取 full crit 后再 RNG。 | 是当前最合适的 future seed；但 `main_loop_consistency` 当前不输出 formula-call count，且 `rg` 未发现生产数据 / 配置会写入非零 `被暴击几率增加` / `crit_rate_received_increase`。 | Conditional No-Go now；只有后续生产语义 diff 和非零相关计数证据同时存在时才可采样。 |
| `青衣雷属性队` / `席德大安比队` | direct damage / stun / buff 路线存在，部分角色有 2-piece `啄木鸟电音` 或其他 crit-adjacent 装备。 | 未发现当前 4-piece Woodpecker full-crit route 或非零 received-crit route。 | No-Go for this selected candidate sample. |
| `薇薇安物理队` | anomaly / physical route，已用于其他 copied-output / anomaly sample discussions。 | 不绑定当前 selected `cal_crit_rate()` received-boundary。 | No-Go for this selected candidate sample. |

如果后续生产实现 PRD 真的触碰 `Calculator.RegularMul.cal_crit_rate(data)` 或 `CalculatorBuffAttributeReader.read_full_crit_rate(context)`，并且能证明真实注册路线产生非零相关计数，首选 future sample contract 为：

- Team: `莱特火属性队`
- APL: `./zsim/data/APLData/莱特-扳机-雨果.toml`
- Explicit stop tick: `1000`
- Target branch: 后续 live production semantic-diff branch；当前 docs/proposal branch 不合格。
- Runtime labels: `retained-cal-crit-rate` vs `candidate-cal-crit-rate`，或由后续 implementation PRD 命名的更具体 labels。
- Expected nonzero count: `CalculatorBuffAttributeReader.read_full_crit_rate(context)` / selected full-crit formula count `> 0`；若要证明 received-crit 语义，必须额外证明 `crit_rate_received_increase > 0`。当前 `event_counts` 不能替代 formula-call count。
- Total damage comparison: behavior-preserving replacement 需要 `legacy.total_damage == candidate.total_damage`；非零差异必须阻塞，除非另有语义变更 story 批准。
- Buff timeline comparison: `differences.buff_timeline.legacy_only_count == 0` 且 `candidate_only_count == 0`。

## US-008 selected crit-rate handoff / same-phase pool

本 handoff 属于当前 RegularMul remaining-branch bounded proposal PRD。US-008 不改 production source；它把 US-003 至 US-007 的 selected candidate、retained gates、registered-sample decision、rollback anchors 和 reviewer verdict 同步到 long-lived Buff docs。结论：Conditional Go for one later bounded implementation PRD limited to `Calculator.RegularMul.cal_crit_rate(data)`；该 Go 不授权 broad `Calculator.py` / `CalAnomaly.py` rewrite、RegularMul branch bundling、retained-only sheer shortcut、registered-team fixture creation、validation-runner rewrite、old-container deletion、layer merge 或 retained compatibility deletion。

| Contract area | US-008 final handoff |
| --- | --- |
| Selected candidate outcome | `Calculator.RegularMul.cal_crit_rate(data)` remains the only selected implementation candidate. Full crit keeps `crit_rate_received_increase`; personal crit remains a retained contrast boundary through `Calculator.RegularMul.cal_personal_crit_rate(data)` / `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`. |
| Retained gates | Focused selected-crit pytest remains the first proof layer. Retained validation gates are `formula-parity` and `calculator-reads`; `implicit-events` is conditional on copied-output / event / dispatch / runtime / listener surfaces; default validation is conditional on lifecycle / runtime-write / validation-runner behavior changes. |
| Registered-sample decision | Conditional No-Go. `莱特火属性队` / `./zsim/data/APLData/莱特-扳机-雨果.toml` remains the only current future seed, but current evidence still lacks nonzero selected full-crit formula relevance and nonzero `crit_rate_received_increase`; current main-loop output lacks formula-call counts. |
| Rollback anchors | `Calculator.RegularMul.cal_crit_rate(data)`, `Calculator.RegularMul.cal_personal_crit_rate(data)`, `CalculatorBuffAttributeReader.read_full_crit_rate(context)`, `CalculatorBuffAttributeReader.read_personal_crit_rate(context)`, `_CalculatorReadSnapshot`, `regular-crit-received-boundary`, `test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers`, retained Buff docs, old containers, and layer-separation invariants. |
| Go / No-Go verdict | Conditional Go for one bounded implementation PRD only. Stop and split if implementation needs `_CalculatorReadSnapshot` public contract expansion, `cal_crit_expect()` semantics, personal crit replacement, crit damage / damage bonus / defense / resistance / vulnerability bundling, retained-only sheer route work, validation-runner rewrite, registered-team fixture creation, old-container deletion, event/runtime/listener layer merge, or retained compatibility deletion. |
| Same-phase pool retained | Registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules. |

## Current implementation PRD US-007 selected crit-rate implementation handoff

本 handoff 属于当前 RegularMul crit-rate bounded implementation PRD。结论：`Calculator.RegularMul.cal_crit_rate(data)` is implemented / no-op verified at handoff through the behavior-preserving `_calculate_full_crit_rate(...)` helper seam；本 story 不授权 `cal_crit_expect()`、personal crit、crit damage、damage bonus、defense、resistance、vulnerability、base damage、retained-only sheer、Stun array、copied-output、CalAnomaly 或 validation-runner rewrite。

| Contract area | US-007 implementation handoff |
| --- | --- |
| Implemented / no-op verified surface | `Calculator.RegularMul.cal_crit_rate(data)` delegates to `_calculate_full_crit_rate(data.static, data.dynamic)` and remains the full-crit path used by `CalculatorBuffAttributeReader.read_full_crit_rate(context)`. |
| Retained contrast boundaries | Full crit keeps `crit_rate_received_increase`; `Calculator.RegularMul.cal_personal_crit_rate(data)` / `CalculatorBuffAttributeReader.read_personal_crit_rate(context)` continue to exclude received crit. |
| Verifier evidence | Focused typecheck `uv run python -m mypy scripts/ralph/campaign_status.py scripts/ralph/context_index.py` exited `0`; retained formula/read evidence remains the current PRD US-005 serial gate: selected crit nodes `10 passed`, full reader suite `143 passed`, `formula-parity` focused `143 passed` / mypy `9 source files` clean, and `calculator-reads` focused `243 passed` / mypy `22 source files` clean. |
| Same-phase pool retained | Registered behavior sample eligibility, remaining `Calculator.RegularMul` branches / retained-only sheer follow-up, future `Calculator.StunMul.get_stun_array()` follow-up if evidence names one, P2-A through P2-G guarded maintenance, retained compatibility, and blocker-only reopen rules. |
| Reopen rule | Reopen `cal_crit_rate(data)` only on focused regression, validation failure, root-workspace source evidence, or reviewer-named follow-up. Do not create validation-only registered teams or broaden into other RegularMul branches. |

## US-003 registered behavior sample eligibility audit

本审计属于当前 candidate-selection PRD 的 docs-only / Guardrail-first slice。US-003 已选择唯一 proposal candidate `Calculator.RegularMul.cal_crit_rate()`，但没有生产语义 diff，因此本节只给出当前 registered team / APL evidence、No-Go / conditional No-Go、以及未来 main-loop sample 的必要条件；不新增 validation-only team、fake APL、fixture-only route，也不运行 retained-vs-retained main-loop sample。

| Evidence source | Current registered route evidence | Candidate relevance | Verdict |
| --- | --- | --- | --- |
| `tests.teams.TeamRegistry` / `auto_register_teams()` | `tests/teams/__init__.py` imports electric / fire / physical configs；current registered teams are `青衣雷属性队` (`./zsim/data/APLData/青衣-丽娜-雅.toml`), `席德大安比队` (`./zsim/data/APLData/席德-大安比-扳机.toml`), `莱特火属性队` (`./zsim/data/APLData/莱特-扳机-雨果.toml`), and `薇薇安物理队` (`./zsim/data/APLData/薇薇安-柳-耀嘉音.toml`)。`示例冰属性队` remains commented out and its APL file is missing, so it is ineligible. | Real registered route pool exists for direct damage / stun / anomaly-family audits, but exact formula candidate branch and nonzero counts are not selected in US-003. | Conditional No-Go for live sample until US-004+ names one production semantic diff and a matching registered route. |
| Sheer / `Calculator.RegularMul.cal_base_attr(..., base_attr=4)` / `cal_sheer_dmg_bonus()` | No registered `仪玄` / Yixuan team or APL was found in current `tests/teams` registration evidence. | Sheer route depends on runtime `char_instance.sheer_attack_conversion_rate`; numeric retained oracle alone cannot prove a live route. | No-Go for registered live sample and production proposal unless a future real registered Yixuan route already exists; do not create one only for validation. |
| Stun / impact / `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` | `青衣雷属性队`, `席德大安比队`, and `莱特火属性队` APLs contain stun-window predicates or impact/stun-related conditions. | They are plausible live routes only after the candidate diff touches stun / impact semantics and preflight proves nonzero relevant stun / impact formula or event counts. Direct-damage samples cannot be reused as stun evidence. | Conditional No-Go in this docs-only slice; future sample must prove route relevance first. |
| Direct damage / crit / defense / resistance / vulnerability RegularMul branches | Registered fire/electric/physical APLs exist and can be candidate route seeds. US-003 selects only the crit-rate branch, so no element / trigger / label / level cross-product is expanded here. | Future route must bind `Calculator.RegularMul.cal_crit_rate()` to a real direct-damage APL skill route and relevant nonzero crit-rate / damage formula count inside an explicit stop tick. | Conditional No-Go for live sample in US-003 because there is no production semantic diff. Future sample must name the route, nonzero count, and rollback anchors before it runs. |
| `zsim/utils/main_loop_consistency.py` report contract | Current report includes team, APL, explicit `stop_tick`, legacy/candidate runtime labels, total damage, event counts, Buff timeline, and differences. | The report has the required output fields, but CLI runtime labels are not a live runtime switch and cannot by themselves prove semantic coverage. | Main-loop consistency remains skipped unless a future live production semantic diff plus real registered route with nonzero relevant counts exists. |

Future main-loop sample requirements, if a later story proposes one:

- Use only a real registered team / APL route from `tests.teams.TeamRegistry` or another already-production registered source; no validation-only teams, fake APLs, fixture-only routes, or retained-vs-retained samples.
- Name the exact production semantic diff, formula branch, route, stop tick, legacy/candidate runtime labels, total damage comparison, relevant nonzero event or formula count, and Buff timeline comparison.
- Keep focused formula oracle / reader tests and retained validation profiles as the primary proof; main-loop consistency is supplemental live-route evidence only.
- If no eligible route exists for the selected candidate, record No-Go or conditional No-Go and keep the later production diff blocked.

## US-006 selected Stun rollback / stop contract

本 contract 属于当前 candidate-selection PRD。它只定义 selected Stun array candidate 的 rollback anchors 和 stop conditions，不新增 production implementation authorization。

| Contract area | Retained rule |
| --- | --- |
| Source anchors | 保留 `Calculator.StunMul.get_stun_array()` 与 `Calculator.cal_stun()` 当前 body；`Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`、`RegularMul` branches、retained-only sheer、`MultiplierData` / `DynamicStatement`、old containers、copied-output constructors、dispatch/runtime/listener/dot layers 均不与本候选合并。 |
| Focused oracle | `test_stun_array_output_contract_preserves_field_order_dtype_and_product()` 是 exact nodeid；缺少 deterministic oracle、字段顺序 / dtype / product mismatch 或 aggregation count drift 都是 stop condition。 |
| Retained docs | 本清单、`docs/Buff重构替换说明.md`、`docs/Buff系统重构Checklist.md`、`docs/旧Buff系统耦合审查结果.md`、`docs/Buff重构下阶段计划草稿.md` 继续作为 rollback 证据；后续 PRD 不得只改 Ralph bookkeeping 而删除这些 retained references。 |
| Validation profiles | Future proposal / implementation 必须串行保留 focused pytest、`formula-parity`、`calculator-reads`；触达 copied-output、event、dispatch/runtime、listener、dot runtime 或 same-tick write 时追加 `implicit-events`。 |
| Registered route | 只有 future live semantic diff 且真实注册队伍 / APL 在 explicit stop tick 内有 nonzero relevant stun / impact counts 时才运行 main-loop sample；缺 route、缺 count 或只靠 runtime label 都是 No-Go。 |
| Interface and layer stops | Broad interface change、validation-runner rewrite need、public contract expansion、old-container deletion、layer merge，或未被未来 PRD 命名而编辑 `ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort`，均必须停止并拆出新 slice。 |

## Current candidate-selection PRD US-008 final handoff

结论：Go for one later bounded proposal / implementation PRD only。当前 candidate-selection PRD 选择 `Calculator.StunMul.get_stun_array()` / `Calculator.cal_stun()` array output 作为下一默认 bounded surface，并完成 handoff docs；它不替换 production formula、不新增 registered team/APL、不改 validation runner、不删除 old containers，也不合并 scheduled queue、listener broadcast、dot runtime registration 或 same-tick runtime write 分层。

Selected candidate outcome：

- Selected files / symbols：`zsim/sim_progress/ScheduledEvent/Calculator.py::Calculator.StunMul.get_stun_array()`、`Calculator.cal_stun()`；focused oracle 为 `tests/simulator/test_buff_attribute_reader.py::test_stun_array_output_contract_preserves_field_order_dtype_and_product`。
- Scope boundary：`Calculator.StunMul.cal_imp()` / `_calculate_impact(...)`、all `Calculator.RegularMul` branches、retained-only sheer runtime conversion、copied-output constructors、old containers、dispatch/runtime ports 和 retained compatibility 均保持分离。
- Next default PRD：只围绕 selected Stun array output 写 one bounded proposal / implementation package；不得扩大为 broad `Calculator.py` / `CalAnomaly.py` rewrite、RegularMul branch bundle、retained-only sheer shortcut、registered-team fixture creation、validation-runner rewrite、old-container deletion 或 layer merge。

Retained gates / verifier evidence：

- Exact focused nodeid、serial `formula-parity`、serial `calculator-reads` 是后续 proposal / implementation 的必备 retained gates；触达 copied-output、event、dispatch/runtime、listener、dot runtime 或 same-tick write 时才追加 `implicit-events`。
- US-007 final retained gates 已通过：focused reader pytest `140 passed`；`formula-parity` base `2 passed` / isolated teams `3 passed` / focused `140 passed` / mypy `9 source files` clean；`calculator-reads` base `2 passed` / isolated teams `3 passed` / focused `240 passed` / mypy `22 source files` clean；`implicit-events` base `2 passed` / isolated teams `3 passed` / focused `247 passed` / mypy `90 source files` clean。
- 本 US-008 为 docs-only handoff；typecheck 使用 Ralph docs/tooling scoped mypy，另做 PRD JSON sanity 和 UTF-8 / mojibake scan。

Registered-sample decision：

- Current decision：conditional No-Go。US-008 没有 live semantic diff，因此不运行 `scripts/run_buff_main_loop_consistency.py`，也不创建 validation-only team、fake APL、fixture-only route 或 retained-vs-retained sample。
- Future sample 只在 later live semantic diff 且真实 registered stun / impact route 在 explicit stop tick 内有 nonzero relevant counts 时运行；必须记录 runtime labels、total damage comparison、relevant event/formula count 和 Buff timeline comparison。

Rollback anchors / same-phase pool：

- Rollback anchors：source methods、focused Stun array oracle、retained Buff docs、本清单、`formula-parity`、`calculator-reads`、conditional `implicit-events`、`MultiplierData` / `DynamicStatement`、old containers、`ScheduleDispatchPort`、`RuntimeCommandPort`、`LegacyRuntimeCommandAdapter`、`BuffRuntimeReadPort` 与 `LegacyBuffRuntimeFacade`。
- Same-phase pool retained：registered behavior sample eligibility、remaining `Calculator.RegularMul` branches / retained-only sheer follow-up、`Calculator.StunMul.get_stun_array()` future follow-up、P2-A through P2-G guarded maintenance、retained compatibility 和 blocker-only reopen rules。

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
