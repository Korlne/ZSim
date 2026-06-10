# Buff公式候选与测试目标清单

更新时间：2026-06-10 12:14 +08:00

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
| Calculator AM/AP/impact/crit/直伤/失衡公式 | `zsim/sim_progress/ScheduledEvent/Calculator.py`：`CalculatorBuffAttributeReader.read_anomaly_mastery()`、`read_anomaly_proficiency()`、`read_impact()`、`read_full_crit_rate()`、`read_personal_crit_rate()`、`read_personal_crit_damage()`；`Calculator.RegularMul.cal_base_dmg()`、`cal_base_attr()`、`cal_dmg_bonus()`、`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()`；`Calculator.AnomalyMul.cal_am()`、`cal_anomaly_buildup()`、`cal_base_damage()`、`cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ap()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()`；`Calculator.StunMul.cal_imp()`、`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_calculator_attribute_formula_boundaries_remain_retained_compatibility()`；`tests/simulator/test_migrated_am_ap_reader_guardrail.py`；`tests/simulator/test_migrated_p2b_reader_guardrail.py`；`tests/simulator/test_full_crit_event_adjacent_reader.py`。 | `RegularMul` / `AnomalyMul` / `StunMul` 已开始表驱动 retained / reader-snapshot oracle；仍缺完整数组乘区、remaining formula branches 与注册队伍行为样本条件。 | `uv run pytest tests/simulator/test_buff_attribute_reader.py -q`；`uv run python scripts/run_buff_refactor_validation.py --typecheck-profile formula-parity`。 |
| `MultiplierData` / `DynamicStatement` 动态快照 | `zsim/sim_progress/ScheduledEvent/Calculator.py`：`_calculate_dynamic_statement()`、`MultiplierData.__new__()`、`MultiplierData.__init__()`、`MultiplierData.get_buff_bonus()`、`MultiplierData.StaticStatement`、`MultiplierData.DynamicStatement.__read_dynamic_statement()`。`CalAnomaly.py` 中 `MulData` 是 `MultiplierData` 别名。 | `tests/simulator/test_buff_attribute_reader.py`：`test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot()`、`test_multiplier_data_dynamic_statement_translates_python_attr_names()`、`test_multiplier_data_dynamic_statement_rejects_invalid_effect_key()`、`test_multiplier_data_cache_key_stability_and_reset_isolation()`、AM/AP/impact/crit reader parity tests。 | `buff_effect_trans.json` key 翻译、非法 key 报错、缓存 key 稳定性和 cache reset isolation 已有 focused characterization；enemy debuff/dot 参与 cache key 由 enemy dynamic reads 行继续保留后续专项。 | 同 `formula-parity` profile；后续若拆分可提取 `test_multiplier_data_formula_snapshot.py`。 |
| `CalAnomaly` / `CalDisorder` / `CalAbloom` 异常伤害公式 | `zsim/sim_progress/ScheduledEvent/CalAnomaly.py`：`CalAnomaly.__init__()`、`cal_k_level()`、`cal_active_crit()`、`cal_def_mul()`、`set_final_multipliers()`、`cal_anomaly_dmg()`；`CalDisorder.cal_disorder_base_dmg()`、`cal_disorder_extra_mul()`、`cal_disorder_stun()`；`CalPolarityDisorder.__init__()`；`CalAbloom.__init__()`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()`、`test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()`、`test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()`；`tests/simulator/test_anomaly_handler_runtime_view.py` covers handler runtime-view reads without legacy dynamic container. | `CalAnomaly` 主动暴击、防御、抗性、易伤、失衡易伤、特殊乘区输入、`set_final_multipliers()` 顺序、snapshot impact / stun ratio 处理与 `scaling_factor` 位置已有 retained `MulData` / settled snapshot oracle；`CalDisorder` base damage remaining-tick / floor 分支、extra multiplier 和 stun 公式已有 element-type oracle；仍缺 `cal_k_level()` clamp，以及 `CalPolarityDisorder` / `CalAbloom` deterministic formula oracle。 | `uv run pytest tests/simulator/test_buff_attribute_reader.py -q`；异常 handler 变更时追加 `uv run pytest tests/simulator/test_anomaly_handler_runtime_view.py -q`。 |
| `AnomalyBar.current_ndarray` 快照输入 | `zsim/sim_progress/anomaly_bar/AnomalyBarClass.py`：`current_ndarray` 字段、`update_snap_shot()`、`change_info_cause_active()`、`reset_current_info_cause_output()`、`reset_myself()`、`create_new_from_existing()`、`__deepcopy__()`；`zsim/sim_progress/ScheduledEvent/CalAnomaly.py` 在构造时读取 `current_ndarray`。 | `tests/simulator/test_buff_attribute_reader.py`：`test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility()`、`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()`；`tests/simulator/test_migrated_am_ap_reader_guardrail.py` prevents legacy anomaly reads in migrated AM/AP files. | 还缺字段级快照矩阵，覆盖未满条、满条结算、复制输出、reset、deepcopy 与 `UpdateAnomaly.py` 写入路径。 | `test_buff_attribute_reader.py` 当前是最小入口；涉及 handler 时追加 `test_anomaly_handler_runtime_view.py`。 |
| 复制异常 / 紊乱输出 | `zsim/sim_progress/anomaly_bar/CopyAnomalyForOutput.py`：`NewAnomaly`、`Disorder`、`PolarityDisorder`；`zsim/sim_progress/ScheduledEvent/CalAnomaly.py`：`CalDisorder`、`CalPolarityDisorder`、`CalAbloom`；`event_handlers/handlers/anomaly.py` 通过 `CalAnomaly` / copied object 报告输出。 | `tests/simulator/test_buff_attribute_reader.py` copied snapshot compatibility tests、`test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()`、`test_cal_disorder_formula_inputs_remain_separate_from_copied_payload()`；`tests/simulator/test_anomaly_handler_runtime_view.py` handler runtime-view tests。 | `Disorder` / `PolarityDisorder` copied formula inputs and listener-facing payload fields are now locked；`CalDisorder` formula 输入和 copied payload sentinel 已分离。仍缺 copied-output report payload parity、`Abloom` 组合测试，以及完整 `CalPolarityDisorder` deterministic formula oracle。 | `test_buff_attribute_reader.py` + `test_anomaly_handler_runtime_view.py`。 |
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
- `CalPolarityDisorder` / `CalAbloom` 还缺 deterministic formula oracle；copied-output report payload parity 仍未覆盖。
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
- `CalPolarityDisorder` / `CalAbloom` deterministic formula oracle。
- `CopyAnomalyForOutput.py` / `UpdateAnomaly.py` report payload parity 与 listener-facing fields。
- `AnomalyBar.current_ndarray` reset / deepcopy / update path 字段矩阵。
- registered-team sample trigger 条件、rollback plan、retained `formula-parity` / `calculator-reads` / `implicit-events` gates 和明确 non-goals。

## US-002 fixture inventory / oracle target map

本节属于当前 Phase-3 formula oracle gap closure PRD；同名历史 US-002 不适用。根工作区预检使用上方 US-002 `rg` 命令，显式排除 `.codex_worktrees/`、`archive/`、`scripts/ralph/archive/`、`scripts/ralph/run-logs/` 与 `*.log`。预检命中 727 行；`tests/simulator/test_buff_attribute_reader.py` 因同时作为显式文件和 `tests/simulator` 目录参数出现，清单去重后只按根工作区测试文件计入。

| 现有 focused fixture / test | 已覆盖公式域 | 保留兼容边界 |
| --- | --- | --- |
| `test_create_anomaly_attribute_read_context_preserves_inputs()`、`test_formula_parity_fixture_builds_independent_calculator_inputs()`、`test_migrated_reader_seam_regression_sample_scope_is_representative()` | 公式 parity fixture、reader context 输入、root-workspace 样本来源。 | 只证明 fixture / context 隔离和样本来源；不删除 retained `Calculator`、`MultiplierData`、old containers 或 XLogic callsites。 |
| `test_multiplier_data_get_buff_bonus_builds_dynamic_statement_snapshot()`、`test_multiplier_data_dynamic_statement_translates_python_attr_names()`、`test_multiplier_data_dynamic_statement_rejects_invalid_effect_key()`、`test_multiplier_data_cache_key_stability_and_reset_isolation()`、`test_multiplier_data_cache_key_distinguishes_enemy_dot_participation()`、`test_enemy_dynamic_debuff_reads_feed_old_and_reader_formula_snapshots()` | `MultiplierData` / `DynamicStatement`、`buff_effect_trans` Python 属性名翻译、非法 key 报错、cache key 稳定性 / reset isolation、enemy debuff 聚合、enemy dot 仅参与 cache key 的边界。 | 保留旧 `_calculate_dynamic_statement()`、`MultiplierData.get_buff_bonus()`、`MultiplierData.__new__()` cache key、`MultiplierData.mul_data_cache`、`StaticStatement._instance_cache`、enemy dynamic list 读取与 cache key 语义。 |
| `test_attribute_reader_matches_old_anomaly_mastery_helper()`、`test_attribute_reader_matches_old_anomaly_proficiency_helper()`、`test_calculator_am_ap_impact_formula_family_matches_reader_snapshot_parity()`、`test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[anomaly-mastery-proficiency-buildup-base-damage]`、`[anomaly-dmg-bonus-ratio-fields]`、`[anomaly-ap-multiplier-conversion]`、`[anomaly-extra-multiplier-fields]`、`[anomaly-crit-retained-fields]`、`test_branch_blade_song_gate_uses_attribute_reader_with_old_helper_parity()`、`test_timeweaver_disorder_gate_uses_attribute_reader_with_old_helper_parity()` | `Calculator.AnomalyMul.cal_am()` / `cal_ap()`、`cal_anomaly_buildup()`、`cal_base_damage()`、`cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()`、AM/AP reader seam、两个 migrated gate callsite、火属性积蓄 / 基础异常伤害字段、异常增伤字段、AP 转换字段、异常额外倍率字段、异常暴击 retained-1 边界。 | reader seam、retained `MultiplierData` 与 reader-built snapshot 等价只作为 compatibility evidence；`cal_anomaly_crit()` 当前仍锁定 retained-1 兼容边界，不把 P2-A reader seam 当作生产公式替换、不删除 retained `AnomalyMul` helper、不新增 runtime 写 facade。 |
| `test_p2b_parity_fixture_matches_old_impact_helper()`、`test_calculator_am_ap_impact_formula_family_matches_reader_snapshot_parity()`、`test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[stun-impact-reader-parity]`、`[stun-ratio-res-bonus-received-retained]` | `Calculator.StunMul.cal_imp()` 与 impact reader seam；`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()` retained / reader-snapshot oracle。 | P2-B impact reader seam 仍只是 compatibility evidence；stun ratio / resistance / bonus / received 目前只锁 retained formula 与 reader-built snapshot，不新增 reader API、不删除 retained `StunMul` helper。 |
| `test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[regular-base-dmg-*]`、`test_formula_oracle_table_cases_drive_expected_fields_and_reader_parity[regular-multipliers-neutral-zero-boundary]`、`[regular-dmg-bonus-character-field-stack]`、`[regular-defense-res-vulnerability-received-stack]`、`[regular-crit-received-boundary]`、`test_p2b_parity_fixture_matches_old_full_and_personal_crit_rate_helpers()`、`test_p2b_full_crit_rate_includes_received_bonus_but_personal_excludes()`、`test_p2b_parity_fixture_matches_old_personal_crit_damage_helper()`、`test_p2b_personal_crit_damage_excludes_received_crit_damage_bonus()`、`test_calculator_regular_mul_crit_formula_families_preserve_received_boundaries()`、`test_calculator_attribute_formula_boundaries_remain_retained_compatibility()` | `Calculator.RegularMul.cal_base_dmg()`、`cal_base_attr()`、`cal_dmg_bonus()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()`、`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()`、neutral / static-field / dynamic-buff base damage inputs、角色侧增伤、敌方防御 / 抗性、受击抗性降低 / 穿透、易伤字段、received crit inclusion / exclusion。 | base damage / base attribute / damage bonus / defense / resistance / vulnerability / crit families 只作为 retained Calculator oracle 与 reader-snapshot compatibility evidence；full crit 保留 received crit rate / damage；personal crit rate / damage 保留排除 received bonus；仍不覆盖 crit expectation、stun vulnerability、special / sheer multiplier 或 array outputs。 |
| `test_anomaly_formula_fixture_copies_snapshot_inputs_for_copied_output()`、`test_disorder_copied_output_preserves_formula_inputs_and_payload_fields()`、`test_anomaly_bar_settlement_and_copied_snapshot_inputs_remain_retained_compatibility()` | copied `AnomalyBar.current_ndarray` 非别名、`Disorder` / `PolarityDisorder` payload 字段、结算快照输入。 | 只锁 copied-input / payload compatibility；不替换 `CopyAnomalyForOutput.py`、`UpdateAnomaly.py`、listener broadcast 或 report payload 语义。 |
| `test_cal_anomaly_rejects_unsettled_or_bad_snapshot_shape()`、`test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()`、`test_cal_anomaly_multiplier_inputs_remain_retained_mul_data_snapshot()` | `CalAnomaly.__init__()` settled / shape guard、`MulData` retained snapshot、`CalAnomaly.cal_active_crit()`、`cal_def_mul()`、res / vulnerability / stun / special multiplier inputs、`set_final_multipliers()` 最终向量顺序、snapshot impact / stun ratio 在 `cal_anomaly_dmg()` 中被除回、非默认 `scaling_factor` 乘算位置，以及 `CalAbloom` scaling sample。 | 保留 `CalAnomaly.py` 生产公式、`AnomalyBar.current_ndarray` 直接快照读取、enemy dynamic lists 与 copied-output formulas。 |

| Oracle target | 当前状态 | 后续 Ralph-sized测试方向 |
| --- | --- | --- |
| `Calculator.RegularMul` | `cal_base_dmg()` / `cal_base_attr()` 已有 neutral、static-field、dynamic-buff 表驱动 oracle；`cal_dmg_bonus()`、`cal_defense_mul()`、`cal_res_mul()`、`cal_dmg_vulnerability()` 已有 zero-like neutral、角色侧增伤堆叠、敌方防御 / 抗性、受击抗性降低 / 穿透、易伤字段堆叠 oracle；`cal_crit_rate()`、`cal_personal_crit_rate()`、`cal_crit_dmg()`、`cal_personal_crit_dmg()` 已有 received-boundary 表驱动 oracle 与 reader seam 兼容证据；`cal_crit_expect()`、`cal_stun_vulnerability()`、`cal_special_mul()`、`cal_sheer_dmg_bonus()` 和 array outputs 仍缺表驱动 oracle。 | 继续拆成 crit expectation、stun vulnerability、special / sheer multiplier 与 array output 小组；每组继续包含 neutral、static-field、dynamic-buff、enemy-side / received 字段组合。 |
| `Calculator.AnomalyMul` | `cal_am()` / `cal_ap()` 已有 reader seam、gate callsite parity 与表驱动 retained / reader-snapshot / reader 三路等价证据；`cal_anomaly_buildup()`、`cal_base_damage()` 已有火属性积蓄 / 基础异常伤害表驱动 oracle，覆盖 static AM/AP/ATK、field bonus、enemy anomaly resistance、trigger buildup bonus 与 reader-built snapshot。US-008 新增 `cal_dmg_bonus()`、`cal_ap_mul()`、`cal_ano_extra_mul()`、`cal_anomaly_crit()` deterministic oracle，分别分离异常增伤字段、AP 转换字段、异常额外倍率字段和 retained-1 异常暴击边界。`cal_res_pen()` 与 `anomaly_snapshot` vector assembly 仍缺 deterministic oracle；这些 remaining branches 需要下一轮以 resistance-penetration / vector snapshot cases 独立覆盖，当前无法由本故事的 damage / AP / extra / crit 字段安全外推。 | 继续补 resistance-penetration cases 与 `anomaly_snapshot` vector assembly；不要把 P2-A AM/AP migrated reader bucket 重新打开成生产替换任务，也不要把 retained-1 anomaly crit characterization 当作生产公式替换授权。 |
| `Calculator.StunMul` | `cal_imp()` 已有 reader seam / family parity 与表驱动 impact reader case；`cal_stun_ratio()`、`cal_stun_res()`、`cal_stun_bonus()`、`cal_stun_received()` 已有 retained / reader-snapshot deterministic oracle；`get_stun_array()` 仍缺 vector assembly oracle。 | 下一步只补 `get_stun_array()` / array output 或注册队伍行为样本条件；不要把 P2-B impact reader evidence 外推成完整 production replacement 授权。 |
| `CalAnomaly` | settled snapshot、shape guard、enemy dynamic lists、`CalAnomaly.cal_active_crit()`、`cal_def_mul()`、res / vulnerability / stun / special multiplier 组合、`set_final_multipliers()` vector order、snapshot impact / stun ratio treatment、非默认 `scaling_factor` 位置和 `CalAnomaly.cal_anomaly_dmg()` retained ratio sample 已有。 | 继续覆盖 `cal_k_level()` clamps；不要把 `CalAnomaly` focused characterization 外推成生产公式替换授权。 |
| `CalDisorder` | copied payload compatibility 已有；US-014 新增 element-type formula oracle，覆盖 `cal_disorder_base_dmg()` remaining tick / floor 规则、`cal_disorder_extra_mul()`、`cal_disorder_stun()`，并用 copied payload sentinel 字段证明 listener-facing payload 不参与公式输入。 | 后续只在 handler/report payload 或 production formula replacement PRD 中复用这些 oracle；不要把本 focused characterization 外推成 `CalPolarityDisorder` / `CalAbloom` 覆盖。 |
| `CalPolarityDisorder` | `PolarityDisorder` copied fields 已锁；生产 formula 只由当前 smoke path 间接触达。 | 覆盖 Yanagi lookup 成功 / 缺失失败、`polarity_disorder_ratio`、`additional_dmg_ap_ratio` 与 retained `Calculator.AnomalyMul.cal_ap()` 输入。 |
| `CalAbloom` | `CalAbloom` scaling sample 已由 `test_cal_anomaly_uses_settled_snapshot_mul_data_and_retained_damage_ratios()` 触达。 | 独立覆盖 `anomaly_dmg_ratio` 组合和 inherited final multiplier vector，不改变 Abloom handler runtime-view 读口。 |
| copied-output payloads | `Disorder` / `PolarityDisorder` formula inputs and payload fields 已锁；`NewAnomaly` / report payload parity 仍不足。 | 补 `NewAnomaly`、`Disorder`、`PolarityDisorder` listener-facing / report fields、`UpdateAnomaly.spawn_output(...)` mode 0 / 1 / 2 输出对象和 handler payload parity。 |
| `AnomalyBar.current_ndarray` | settled / copied snapshot 非别名已有；field-level lifecycle matrix 不完整。 | 覆盖未满条、满条结算、`update_snap_shot()`、`reset_current_info_cause_output()`、`reset_myself()`、`create_new_from_existing()`、`__deepcopy__()`、shape / dtype / aliasing。 |

## US-013 行为样本决策矩阵

本矩阵只定义何时需要 registered-team main-loop consistency sample；它不新增 validation profile，不替换生产公式，不把 `--legacy-runtime` / `--candidate-runtime` label 当作真实 runtime switch。

| 公式 / 行为域 | 默认证据层级 | 语义变更后何时追加 registered-team main-loop sample | 关注输出 |
| --- | --- | --- | --- |
| 直伤 / crit / defense / resistance / vulnerability 公式 | focused unit characterization、retained `Calculator.RegularMul` oracle、reader seam parity。 | 实际改变 `Calculator.py` 中会进入 live damage route 的数值公式，且已注册队伍的 APL 能在 stop-tick 内触达对应伤害事件。 | `total_damage` 必须解释为 live behavior 证据；仍需 focused parity suite 先通过。 |
| stun / impact / stun-ratio 公式 | focused impact / stun formula snapshots、P2-B migrated reader guardrail。 | 实际改变 `Calculator.StunMul`、impact reader 或 stun received 语义，且注册队伍能在 stop-tick 内打出该 stun / impact route。 | `total_damage`、相关 `event_counts` 与 Buff timeline 是否随失衡窗口改变。 |
| anomaly buildup / anomaly damage / settlement | focused `CalAnomaly`、`AnomalyBar.current_ndarray`、settlement snapshot tests。 | 实际改变 `CalAnomaly.py`、`AnomalyBar.current_ndarray`、`anomaly_settled()`、active anomaly snapshot 或 buildup filtering，且注册队伍能触发目标异常积蓄 / 结算 route。 | `total_damage`、异常相关 `event_counts`、Buff timeline；无注册 route 时记录缺口。 |
| copied anomaly / disorder output | focused copied-output payload、formula-input、listener-facing field tests。 | 实际改变 `CopyAnomalyForOutput.py`、`UpdateAnomaly.spawn_output(...)`、`CalDisorder` / `CalPolarityDisorder` / `CalAbloom` copied formula semantics，且注册队伍能生成 NewAnomaly / Disorder / PolarityDisorder / copied-output payload。 | `event_counts`、`total_damage`、listener/report payload 可观察差异。 |
| Buff timeline / lifecycle | focused lifecycle、runtime facade、guardrail tests。 | 实际改变 Buff add / refresh / pending-to-active / active removal / duration tick / forced write 顺序，且注册队伍的 live route 会生成该 Buff timeline。 | `buff_timeline` 的 legacy-only / candidate-only 样本必须为零，或差异有明确预期。 |
| scheduled event publish timing | focused dispatch tests、fail-fast queue tests、event payload order tests。 | 实际改变 `execute_tick`、priority、target fan-out、publish-before/after ordering、`mission_start(...)` / `simple_start()` 相对顺序，且注册队伍 live route 会发布该事件。 | `event_counts`、Buff timeline 与总伤；publish timing 不能只靠 CLI label 证明。 |
| 文档 / 分类 / test-only / guardrail-only | focused docs / tests / validation profile。 | 不运行，除非同一 story 同时改 production behavior。 | 在 Ralph progress 记录跳过原因。 |

### Registered-team 触发条件

| 触发类别 | 运行 registered sample 的必要条件 | 当前证据 / 缺口 |
| --- | --- | --- |
| damage | 注册队伍配置存在；APL 在 stop-tick 内命中目标技能 / 伤害事件；本 story 改动会改变公式输出或事件进入伤害计算的字段。 | P2-B 已有 `莱特火属性队` 样本；phase-3 公式替换仍需按具体公式 route 重新确认。 |
| stun | 注册队伍能触发目标 impact / stun bonus / stun received route，并在 stop-tick 内进入可观察失衡窗口。 | `青衣雷属性队` / `席德大安比队` 可作为候选，但必须先确认 APL 触达目标文件或公式。 |
| anomaly | 注册队伍能触发目标异常积蓄、结算、紊乱或异常伤害 route；stop-tick 覆盖 active anomaly lifecycle。 | `薇薇安物理队` 可作为 Vivian / anomaly 候选；Alice / Yuzuha / Jane 当前没有注册代表队。 |
| copied-output | 注册队伍实际生成 NewAnomaly / Disorder / PolarityDisorder / Vivian copied payload，并让 payload 进入 handler、listener 或 report path。 | 只有确认 APL 触达 copied-output route 后才运行；否则 focused copied-output tests 是当前证据。 |
| Buff timeline | 改动会影响 Buff / debuff / dot 的 add、refresh、activation、duration 或 removal，且注册队伍 route 会产生这些 timeline entries。 | 已有成功样本只证明对应 route，不可外推到其他 Buff / formula domains。 |
| event publish timing | 改动会影响 scheduled event 的 publish tick、priority、target fan-out 或 producer-local ordering，且注册队伍 route 会发布该事件。 | 先用 focused dispatch tests 锁 order；registered sample 只补 live route evidence。 |

US-013 本轮没有 live semantic change、没有 validation wiring change，也没有注册队伍 fixture 变更；因此不运行 `--mainloop` 或 `scripts/run_buff_main_loop_consistency.py`。

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
