import pandas as pd
import json
import os
import sys
import numpy as np

# ================= 配置区域 =================
# 定位到 zsim 包的根目录
# 假设脚本位于 zsim/script/data_compiler/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ZSIM_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))) # .../zsim
DATA_DIR = os.path.join(ZSIM_ROOT, 'zsim', 'data')

# 此时修正路径逻辑：如果 CURRENT_DIR 是 .../zsim/script/data_compiler
# up1 -> script, up2 -> zsim, up3 -> 项目根目录?
# 让我们使用相对路径更稳健的方式：
# 目标是找到 zsim/data
# 如果脚本在 zsim/script/data_compiler/
# os.path.dirname(__file__) -> data_compiler
# .parent -> script
# .parent -> zsim
# .parent -> 项目根 (如果是) 或 zsim (如果是包内运行)

# 简单起见，我们向上查找直到找到 'data' 文件夹
def find_data_dir(start_path):
    path = start_path
    for _ in range(4): # 最多找4层
        if os.path.exists(os.path.join(path, 'data')):
            return os.path.join(path, 'data')
        path = os.path.dirname(path)
    return None

DATA_DIR = find_data_dir(CURRENT_DIR)
if not DATA_DIR:
    # 回退硬编码
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))), 'zsim', 'data')

SOURCE_DIR = os.path.join(DATA_DIR, 'buff_config_source')
OUTPUT_DIR = os.path.join(DATA_DIR, 'generated')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'buff_db.json')

# ===========================================

def safe_json_load(json_str):
    """解析 CSV 中的 JSON 字符串，处理空值和格式错误"""
    if pd.isna(json_str) or str(json_str).strip() == "":
        return None
    try:
        return json.loads(str(json_str))
    except json.JSONDecodeError:
        # 尝试修复常见的单引号错误
        try:
            return json.loads(str(json_str).replace("'", '"'))
        except:
            return None

def convert_value(val):
    """智能转换数值类型"""
    if pd.isna(val):
        return 0
    try:
        f_val = float(val)
        if f_val.is_integer():
            return int(f_val)
        return f_val
    except ValueError:
        return str(val)

def compile_buffs():
    print(f"🚀 [ZSim] 开始编译 Buff 数据...")
    print(f"   源目录: {SOURCE_DIR}")
    
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 错误: 源目录不存在。请先运行 migrate_legacy_csv.py")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. 读取 CSV
    reg_path = os.path.join(SOURCE_DIR, 'buff_registry.csv')
    eff_path = os.path.join(SOURCE_DIR, 'buff_effects.csv')
    
    try:
        # dtype=str 保证 ID 不会被读成数字从而丢失前导零（如果有）
        df_reg = pd.read_csv(reg_path, dtype={'buff_id': str})
        df_eff = pd.read_csv(eff_path, dtype={'buff_id': str})
    except Exception as e:
        print(f"❌ 读取 CSV 失败: {e}")
        return

    buff_db = {}
    
    # 2. 处理基础配置 (Registry)
    print("   正在构建 Buff 对象树...")
    for _, row in df_reg.iterrows():
        buff_id = row['buff_id']
        if pd.isna(buff_id): continue

        # 处理 tags
        tags = []
        if not pd.isna(row.get('tags')):
            tags = [t.strip() for t in str(row['tags']).split(',') if t.strip()]

        feature = {
            "buff_id": buff_id,
            "name": str(row.get('buff_name', f"Buff_{buff_id}")),
            "max_stacks": int(row.get('max_stacks', 1)),
            "max_duration": float(row.get('max_duration', -1)),
            "stack_increment": int(row.get('stack_increment', 1)),
            "independent_stacks": str(row.get('independent_stacks')).lower() == 'true',
            "allows_refresh": str(row.get('allows_refresh')).lower() != 'false', # 默认为 True
            "tags": tags
        }
        
        buff_db[buff_id] = {
            "feature": feature,
            "effects": []
        }

    # 3. 处理效果 (Effects)
    print("   正在注入 Effects 逻辑...")
    orphan_count = 0
    
    for idx, row in df_eff.iterrows():
        buff_id = row['buff_id']
        if pd.isna(buff_id): continue
        
        if buff_id not in buff_db:
            orphan_count += 1
            continue

        # 基础 Effect 数据
        effect_data = {
            "type": row.get('effect_type', 'bonus'),
        }

        # Bonus 特有字段
        if not pd.isna(row.get('target_key')):
            effect_data['target_key'] = str(row['target_key'])
            
        if not pd.isna(row.get('value')):
            effect_data['value'] = convert_value(row['value'])

        # Trigger 特有字段
        if not pd.isna(row.get('trigger_event')):
            effect_data['trigger_event'] = str(row['trigger_event'])

        # 通用 JSON 字段
        conditions = safe_json_load(row.get('conditions'))
        if conditions: 
            effect_data['conditions'] = conditions
            
        actions = safe_json_load(row.get('actions'))
        if actions: 
            effect_data['actions'] = actions

        buff_db[buff_id]['effects'].append(effect_data)

    # 4. 输出 JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(buff_db, f, indent=2, ensure_ascii=False)

    print(f"✅ 编译成功!")
    print(f"   - Buff 总数: {len(buff_db)}")
    print(f"   - 输出文件: {OUTPUT_FILE}")
    if orphan_count > 0:
        print(f"   ⚠️ 跳过了 {orphan_count} 个没有对应基础配置的效果条目")

if __name__ == "__main__":
    compile_buffs()