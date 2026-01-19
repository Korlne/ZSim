import pandas as pd
import json
import os
import sys

# ================= 配置区域 =================

# 路径设置：自动定位到 zsim/data 目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR)) # 回退到 zsim 根目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# 输入文件 (旧版 CSV)
OLD_EFFECTS_FILE = os.path.join(DATA_DIR, 'buff_effect.csv')
OLD_ACTIVE_FILE = os.path.join(DATA_DIR, '激活判断.csv')
OLD_TRIGGER_FILE = os.path.join(DATA_DIR, '触发判断.csv')

# 输出目录
OUTPUT_DIR = os.path.join(DATA_DIR, 'buff_config_source')
NEW_REGISTRY_FILE = os.path.join(OUTPUT_DIR, 'buff_registry.csv')
NEW_EFFECTS_FILE = os.path.join(OUTPUT_DIR, 'buff_effects.csv')

# --- [核心] 属性名映射字典 (中文 CSV Header -> Character.py 类属性名 或 标准化Key) ---
ATTRIBUTE_MAP = {
    # ================= 1. 基础面板 (Stat Panel) =================
    # --- 攻击力 ---
    "攻击力": "ATK_percent",
    "攻击力百分比": "ATK_percent",
    "固定攻击力": "ATK_numeric",
    "攻击力数值": "ATK_numeric",
    "局内攻击力%": "overall_ATK_percent", # [新增] 对应 self.overall_ATK_percent

    # --- 防御力 ---
    "防御力": "DEF_percent",
    "防御力百分比": "DEF_percent",
    "固定防御力": "DEF_numeric",
    "百分比减防": "def_reduction_percentage", # [新增] 敌方防御乘区

    # --- 生命值 ---
    "生命值": "HP_percent",
    "生命值百分比": "HP_percent",
    "固定生命值": "HP_numeric",

    # --- 冲击力 ---
    "冲击力": "IMP_percent",
    "冲击力百分比": "IMP_percent",
    "固定冲击力": "IMP_numeric",
    "局内冲击力%": "overall_IMP_percent", # [新增]

    # --- 暴击 (Critical) ---
    "暴击率": "CRIT_rate_numeric",
    "固定暴击率": "CRIT_rate_numeric",    # [新增]
    "局内暴击率": "CRIT_rate_numeric",    # [新增]
    "暴击伤害": "CRIT_damage_numeric",
    "固定暴击伤害": "CRIT_damage_numeric",
    "局内暴击伤害": "CRIT_damage_numeric", # [新增]
    "受暴击伤害增加": "crit_dmg_taken_bonus", # [新增] 敌方易伤

    # --- 穿透 (Penetration) ---
    "穿透率": "PEN_ratio",
    "局内穿透率": "PEN_ratio", # [新增]
    "穿透值": "PEN_numeric",
    "固定贯穿力": "PEN_numeric", # [新增] 旧称呼

    # --- 异常属性 (Anomaly) ---
    "异常精通": "AP_numeric",
    "固定异常精通": "AP_numeric", # [新增]
    "局内异常精通": "AP_numeric", # [新增] (通常直接加数值)
    "异常掌控": "AM_percent",
    "固定异常掌控": "AM_percent", # [新增]
    "局内异常掌控": "overall_AM_percent", # [新增]

    # --- 能量 (Energy) ---
    "能量自动回复": "sp_regen_numeric",
    "能量自动恢复": "sp_regen_numeric", # [新增] 错别字兼容
    "局内能量自动恢复": "sp_regen_numeric", # [新增]
    "能量获取效率": "sp_get_ratio",
    "能量获得效率": "sp_get_ratio", # [新增]
    
    # --- 喧响 (Decibel) ---
    "喧响获得效率": "decibel_generation_ratio", # [新增] 

    # ================= 2. 伤害加成 (DMG Bonus) =================
    # --- 通用 ---
    "造成伤害": "ALL_DMG_bonus",
    "全属性伤害": "ALL_DMG_bonus",
    "全增伤": "ALL_DMG_bonus", # [新增]
    "额外伤害倍率": "extra_dmg_multiplier", # [新增] 独立乘区

    # --- 属性伤害 ---
    "冰属性伤害": "ICE_DMG_bonus",
    "火属性伤害": "FIRE_DMG_bonus",
    "电属性伤害": "ELECTRIC_DMG_bonus",
    "物理属性伤害": "PHY_DMG_bonus",
    "以太属性伤害": "ETHER_DMG_bonus",

    # --- 技能特定增伤 (Skill Type Bonus) ---
    # 这些Key需要计算器(Calculator)支持
    "普通攻击伤害": "normal_attack_dmg_bonus",
    "普攻增伤": "normal_attack_dmg_bonus", # [新增]
    
    "冲刺攻击增伤": "dash_attack_dmg_bonus", # [新增]
    "闪避反击增伤": "dodge_counter_dmg_bonus", # [新增]
    "闪避反击伤害": "dodge_counter_dmg_bonus",
    
    "特殊技伤害": "special_attack_dmg_bonus",
    "强化特殊技伤害": "ex_special_attack_dmg_bonus",
    "强化特殊技增伤": "ex_special_attack_dmg_bonus", # [新增]
    
    "连携技伤害": "chain_attack_dmg_bonus",
    "连携技增伤": "chain_attack_dmg_bonus", # [新增]
    
    "终结技伤害": "ultimate_dmg_bonus",
    "终结技增伤": "ultimate_dmg_bonus", # [新增]
    
    "支援技伤害": "assist_attack_dmg_bonus",
    "支援突击增伤": "assist_attack_dmg_bonus", # [新增]
    
    "追加攻击增伤": "follow_up_dmg_bonus", # [新增]
    "追加攻击暴伤": "follow_up_crit_dmg_bonus", # [新增]

    # ================= 3. 抗性与穿透 (Res & Pen) =================
    # "抗性穿透" 通常指直接减少怪物抗性乘区
    "全属性抗性穿透": "all_res_pen", # [新增]
    "物理抗性穿透": "phy_res_pen", # [新增]
    "火抗性穿透": "fire_res_pen", # [新增]
    "冰抗性穿透": "ice_res_pen", # [新增]
    "电抗性穿透": "electric_res_pen", # [新增]
    "以太抗性穿透": "ether_res_pen", # [新增]

    # "抗性降低" 也是作用于怪物抗性乘区，效果同上
    "全属性伤害抗性降低": "all_res_reduction", # [新增]
    "物理伤害抗性降低": "phy_res_reduction", # [新增]
    "火伤害抗性降低": "fire_res_reduction", # [新增]
    "冰伤害抗性降低": "ice_res_reduction", # [新增]
    "冰伤害抗性降 低": "ice_res_reduction", # [新增] (处理旧表错别字)
    "电伤害抗性降低": "electric_res_reduction", # [新增]
    "以太伤害抗性降低": "ether_res_reduction", # [新增]
    
    # 异常抗性
    "全属性异常额外伤害增幅": "anomaly_damage_taken_bonus", # [新增]
    "物理异常抗性降低": "phy_anomaly_res_reduction", # [新增]
    "火异常抗性降低": "fire_anomaly_res_reduction", # [新增]
    "冰异常抗性降低": "ice_anomaly_res_reduction", # [新增]

    # ================= 4. 失衡与机制 (Stun & Mechanics) =================
    # --- 失衡 (Stun/Daze) ---
    "失衡值造成的伤害": "daze_bonus", 
    "失衡增幅": "daze_bonus", # [新增]
    "失衡易伤倍率": "stun_damage_taken_multiplier",
    "失衡易伤增加": "stun_damage_taken_multiplier", # [新增]
    "全时段失衡易伤增加": "stun_damage_taken_multiplier", # [新增]
    "受失衡增加": "daze_taken_ratio", # [新增] 敌方承伤增加
    "失衡延长": "stun_duration_extension", # [新增]
    
    # 特定技能失衡值
    "普攻失衡值增加": "normal_attack_daze_bonus", # [新增]
    "冲刺攻击失衡值增加": "dash_attack_daze_bonus", # [新增]
    "强化特殊技失衡值增加": "ex_special_attack_daze_bonus", # [新增]
    "连携技失衡值增加": "chain_attack_daze_bonus", # [新增] (旧表未出现但预留)
    "终结技失衡值增加": "ultimate_daze_bonus", # [新增]
    "闪避反击失衡值增加": "dodge_counter_daze_bonus", # [新增]
    "追加攻击失衡值增加": "follow_up_daze_bonus", # [新增]

    # --- 积蓄 (Buildup) ---
    "积蓄效率": "anomaly_buildup_rate", 
    "全积蓄效率增加": "anomaly_buildup_rate", # [新增]
    "物理积蓄效率增加": "phy_buildup_rate", # [新增]
    "火积蓄效率增加": "fire_buildup_rate", # [新增]
    "冰积蓄效率增加": "ice_buildup_rate", # [新增]
    "电积蓄效率增加": "electric_buildup_rate", # [新增]
    "以太积蓄效率增加": "ether_buildup_rate", # [新增]
    "烈霜积蓄效率增加": "frost_buildup_rate", # [新增]
    "普攻积蓄效率增加": "normal_attack_buildup_rate", # [新增]

    # --- 状态/Dot (Status) ---
    "强击无视防御": "assault_ignore_def", # [新增]
    "强击暴击率增加": "assault_crit_rate", # [新增]
    "强击暴击伤害增加": "assault_crit_dmg", # [新增]
    "强击额外伤害增幅": "assault_dmg_bonus", # [新增]
    "紊乱倍率增加": "disorder_multiplier", # [新增]
    "紊乱额外伤害增幅": "disorder_dmg_bonus", # [新增]
    "侵蚀额外伤害增幅": "corruption_dmg_bonus", # [新增]
    "贯穿伤害增加": "pierce_dmg_bonus", # [新增]
    
    # 时间延长
    "感电时间延长": "shock_duration_extension", # [新增]
    "灼烧时间延长": "burn_duration_extension", # [新增]
    "畏缩时间延长": "cower_duration_extension", # [新增]
}

# ===========================================

def load_csv_safe(path):
    """尝试不同编码读取 CSV"""
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}")
        return None
    
    encodings = ['utf-8', 'gbk', 'utf-8-sig', 'gb18030']
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            # 简单的验证：如果读出来只有一列且包含逗号，说明分隔符不对或者编码严重错误，但在CSV read中通常会报错
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"   读取出错 {path}: {e}")
            return None
    print(f"❌ 无法识别文件编码: {path}")
    return None

def safe_bool(val):
    """转换各种布尔值表达"""
    s = str(val).strip().upper()
    if s in ['TRUE', '1', 'YES', 'T']:
        return True
    return False

def clean_string(val):
    if pd.isna(val): return ""
    return str(val).strip()

def main():
    print("🚀 [ZSim] 开始迁移 Buff 数据...")
    print(f"   数据源目录: {DATA_DIR}")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. 读取旧数据
    df_effect = load_csv_safe(OLD_EFFECTS_FILE) 
    df_active = load_csv_safe(OLD_ACTIVE_FILE)
    df_trigger = load_csv_safe(OLD_TRIGGER_FILE)

    if df_effect is None or df_active is None:
        print("❌ 缺少必要的核心文件 (buff_effects 或 激活判断)，无法继续。")
        return

    # 预处理 Trigger 表索引，防止重复
    trigger_map = {}
    if df_trigger is not None:
        df_trigger.columns = df_trigger.columns.str.strip()
        for _, row in df_trigger.iterrows():
            name = clean_string(row.get('BuffName'))
            if name:
                trigger_map[name] = row

    # 预处理 Effect 表索引
    effect_map = {}
    if df_effect is not None:
        df_effect.columns = df_effect.columns.str.strip()
        # 建立 Name -> Row 的字典，处理可能得重复
        for _, row in df_effect.iterrows():
            name = clean_string(row.get('名称'))
            if name:
                effect_map[name] = row

    registry_rows = []
    effect_rows = []
    unknown_keys = set()

    print("   正在合并与转换数据...")

    # 2. 遍历主表 (激活判断.csv)
    for idx, row in df_active.iterrows():
        buff_name = clean_string(row.get('BuffName'))
        if not buff_name: continue

        # --- 获取关联的 Trigger 信息 ---
        trigger_info = trigger_map.get(buff_name, {})
        
        # 确定 Buff ID
        raw_id = trigger_info.get('id')
        if pd.notna(raw_id) and str(raw_id).strip() != "":
            try:
                buff_id = str(int(float(raw_id))) # 处理 1001.0
            except:
                buff_id = str(raw_id)
        else:
            buff_id = buff_name # 降级方案

        # --- A. 构建 Registry (基础配置) ---
        tags = []
        if safe_bool(row.get('is_weapon')): tags.append("Weapon")
        if safe_bool(row.get('is_debuff')): tags.append("Debuff")
        if safe_bool(row.get('is_additional_ability')): tags.append("AdditionalAbility")
        if safe_bool(row.get('is_cinema')): tags.append("Cinema") 
        
        from_char = clean_string(row.get('from'))
        if from_char and from_char != 'nan':
            tags.append(from_char)

        registry_rows.append({
            "buff_id": buff_id,
            "buff_name": buff_name,
            "max_stacks": int(row.get('maxcount', 1)) if pd.notna(row.get('maxcount')) else 1,
            "max_duration": float(row.get('maxduration', -1)) if pd.notna(row.get('maxduration')) else -1,
            "stack_increment": int(row.get('incrementalstep', 1)) if pd.notna(row.get('incrementalstep')) else 1,
            "independent_stacks": safe_bool(row.get('individual_settled')),
            "allows_refresh": safe_bool(row.get('freshtype')),
            "tags": ",".join(tags)
        })

        # --- B. 构建 Effects (数值加成) ---
        if buff_name in effect_map:
            eff_data = effect_map[buff_name]
            
            # 遍历 key1-value1 到 key4-value4
            for i in range(1, 5):
                k_col = f'key{i}'
                v_col = f'value{i}'
                
                raw_key = eff_data.get(k_col)
                raw_val = eff_data.get(v_col)

                if pd.isna(raw_key) or str(raw_key).strip() == "":
                    continue
                
                raw_key = str(raw_key).strip()
                
                # 映射属性名
                target_key = ATTRIBUTE_MAP.get(raw_key)
                
                if target_key is None:
                    # 记录未知 Key
                    unknown_keys.add(raw_key)
                    target_key = raw_key # 暂时保留中文
                
                # 添加到列表
                effect_rows.append({
                    "buff_id": buff_id,
                    "effect_type": "bonus",
                    "trigger_event": "",
                    "conditions": "{}", 
                    "actions": "",
                    "target_key": target_key,
                    "value": raw_val
                })

        # --- C. 构建 Logic (触发器迁移) ---
        conditions = {}
        
        # 1. 技能类型
        skill_type = trigger_info.get('SkillType')
        if pd.notna(skill_type) and str(skill_type).strip() != "":
            conditions['skill_type'] = str(skill_type)
            
        # 2. 元素类型
        elem_type = trigger_info.get('ElementType')
        if pd.notna(elem_type) and str(elem_type).strip() != "":
            conditions['element'] = str(elem_type)
            
        # 3. 命中次数
        hit_num = trigger_info.get('HitNumber')
        if pd.notna(hit_num) and int(hit_num) > 0:
            conditions['hit_count'] = int(hit_num)

        # 检查是否需要生成 Trigger 条目
        logic_id = trigger_info.get('logic_id')
        trigger_type = trigger_info.get('trigger_type')
        
        has_logic = (pd.notna(logic_id) and str(logic_id) != "") or \
                    (pd.notna(trigger_type) and str(trigger_type) != "")

        if has_logic:
            legacy_data = {
                "legacy_logic_id": str(logic_id) if pd.notna(logic_id) else None,
                "legacy_trigger_type": str(trigger_type) if pd.notna(trigger_type) else None
            }
            legacy_data.update(conditions)
            
            effect_rows.append({
                "buff_id": buff_id,
                "effect_type": "trigger",
                "trigger_event": "legacy_migration_check", 
                "conditions": json.dumps(legacy_data, ensure_ascii=False),
                "actions": json.dumps([{"func": "NOT_IMPLEMENTED"}]),
                "target_key": "",
                "value": 0
            })

    # 3. 输出文件
    df_new_reg = pd.DataFrame(registry_rows)
    reg_cols = ["buff_id", "buff_name", "max_stacks", "max_duration", "stack_increment", "independent_stacks", "allows_refresh", "tags"]
    # 补全缺少的列
    for c in reg_cols: 
        if c not in df_new_reg.columns: df_new_reg[c] = ""
    df_new_reg = df_new_reg[reg_cols]
    
    df_new_reg.to_csv(NEW_REGISTRY_FILE, index=False, encoding='utf-8-sig')

    df_new_eff = pd.DataFrame(effect_rows)
    if not df_new_eff.empty:
        eff_cols = ["buff_id", "effect_type", "trigger_event", "conditions", "actions", "target_key", "value"]
        for c in eff_cols:
            if c not in df_new_eff.columns: df_new_eff[c] = ""
        df_new_eff = df_new_eff[eff_cols]
        df_new_eff.to_csv(NEW_EFFECTS_FILE, index=False, encoding='utf-8-sig')

    print("\n✅ 迁移完成!")
    print(f"   - 基础配置表: {NEW_REGISTRY_FILE} ({len(df_new_reg)} 行)")
    print(f"   - 效果配置表: {NEW_EFFECTS_FILE} ({len(df_new_eff)} 行)")

    if unknown_keys:
        print("\n⚠️  警告: 发现以下未知的中文属性名 (已保留原名，请检查 migrate_legacy_csv.py 中的 ATTRIBUTE_MAP):")
        print("   " + ", ".join(sorted(list(unknown_keys))))
    else:
        print("\n✨ 完美！所有属性名都已成功映射到 Character.py 的变量名。")

if __name__ == "__main__":
    main()