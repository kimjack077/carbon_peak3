"""最终测试：验证所有问题都已修复"""
import sys
sys.path.insert(0, 'backend')

from model.data_processor import DataProcessor
from model.scenario_runner import run_scenario
import pandas as pd

# 加载数据
processor = DataProcessor('backend/data/sample_data.csv')
processor.load_data()
base = processor.prepare_base_dict_for_models()

# 测试情景
scenario = {
    'model_type': 'leap',
    'gdp_growth_rate': 0.05,
    'population_growth_rate': -0.0099,
    'efficiency_improvement_rate': 0.02,
    'coal_reduction_rate': 0.02,
    'power_share_increase': 0.02,
    'ren_share_increase': 0.015,
    'grid_cf_decline': 0.05
}

# 运行预测到2054年
results = run_scenario(base, scenario, 2054)

print('=' * 100)
print('最终测试报告')
print('=' * 100)

# 测试1: 能源消费连续性
print('\n【测试1】能源消费连续性检查')
print('-' * 100)

# 计算历史能源消费
EMISSION_FACTORS = {'coal': 2.5, 'oil': 2.1, 'gas': 1.6, 'ren': 0.0}
EF_grid = 0.65

hist_energy = []
for i in range(len(base['years'])):
    ci = base['co2'][i] / base['gdp'][i]
    mix = {f: base['mix'][f][i] for f in ['coal', 'oil', 'gas', 'ren']}
    p = base['power_share'][i]
    cf_dir = sum(mix[f] * EMISSION_FACTORS[f] for f in mix)
    cf = (1 - p) * cf_dir + p * EF_grid
    ei = ci / cf
    energy = base['gdp'][i] * ei
    hist_energy.append(energy)
    print(f'{base["years"][i]}年（历史）: 能源消费 = {energy:.2f} 万吨标煤')

# 2024-2025过渡
energy_2024 = hist_energy[-1]
energy_2025 = results.iloc[0]['energy_consumption']
transition_growth = (energy_2025 / energy_2024 - 1) * 100

print(f'\n2024-2025过渡:')
print(f'  2024年: {energy_2024:.2f} 万吨标煤')
print(f'  2025年: {energy_2025:.2f} 万吨标煤')
print(f'  增长率: {transition_growth:.2f}%')

if -5 <= transition_growth <= 10:
    print('  ✅ 通过: 过渡平滑，增长率合理')
else:
    print(f'  ❌ 失败: 过渡不平滑，增长率异常')

# 检查前10年能源消费趋势
print(f'\n前10年能源消费趋势:')
prev_energy = energy_2024
all_smooth = True
for i in range(min(10, len(results))):
    year = int(results.iloc[i]['year'])
    energy = results.iloc[i]['energy_consumption']
    growth = (energy / prev_energy - 1) * 100
    print(f'  {year}年: {energy:.2f} 万吨标煤 (增长: {growth:+.2f}%)')
    
    if growth < -5:  # 下降超过5%视为异常
        all_smooth = False
    
    prev_energy = energy

if all_smooth:
    print('  ✅ 通过: 能源消费保持平滑增长')
else:
    print('  ❌ 失败: 能源消费出现异常下降')

# 测试2: 碳排放达峰检查
print('\n【测试2】碳排放达峰检查')
print('-' * 100)

# 找出峰值
peak_idx = results['total_emission'].idxmax()
peak_year = int(results.iloc[peak_idx]['year'])
peak_value = results.iloc[peak_idx]['total_emission']

print(f'达峰年份: {peak_year}年')
print(f'峰值: {peak_value:.2f} 万吨CO2')

# 检查峰值前后的趋势
print(f'\n峰值前后5年趋势:')
start_idx = max(0, peak_idx - 5)
end_idx = min(len(results), peak_idx + 6)

for i in range(start_idx, end_idx):
    year = int(results.iloc[i]['year'])
    co2 = results.iloc[i]['total_emission']
    marker = ' ← 峰值' if i == peak_idx else ''
    print(f'  {year}年: {co2:.2f} 万吨CO2{marker}')

# 检查是否有跳跃
print(f'\n检查碳排放跳跃:')
has_jump = False
for i in range(1, len(results)):
    prev_co2 = results.iloc[i-1]['total_emission']
    curr_co2 = results.iloc[i]['total_emission']
    change_pct = (curr_co2 / prev_co2 - 1) * 100
    
    # 检查是否有超过3%的跳跃（上升或下降）
    if abs(change_pct) > 3:
        year = int(results.iloc[i]['year'])
        print(f'  ⚠️  {year}年: 变化 {change_pct:+.2f}% (可能异常)')
        has_jump = True

if not has_jump:
    print('  ✅ 通过: 碳排放曲线平滑，无异常跳跃')
else:
    print('  ❌ 失败: 碳排放曲线存在跳跃')

# 测试3: 能源结构变化
print('\n【测试3】能源结构变化检查')
print('-' * 100)

print(f'年份\t煤炭占比\t电力占比\t清洁能源占比')
for i in [0, 4, 9, 14, 19, 29]:
    if i < len(results):
        year = int(results.iloc[i]['year'])
        coal = results.iloc[i]['mix_coal'] * 100
        power = results.iloc[i]['power_share'] * 100
        ren = results.iloc[i]['mix_ren'] * 100
        print(f'{year}\t{coal:.1f}%\t\t{power:.1f}%\t\t{ren:.1f}%')

# 检查趋势
coal_start = results.iloc[0]['mix_coal']
coal_end = results.iloc[-1]['mix_coal']
power_start = results.iloc[0]['power_share']
power_end = results.iloc[-1]['power_share']
ren_start = results.iloc[0]['mix_ren']
ren_end = results.iloc[-1]['mix_ren']

print(f'\n趋势检查:')
if coal_end < coal_start:
    print(f'  ✅ 煤炭占比下降: {coal_start*100:.1f}% → {coal_end*100:.1f}%')
else:
    print(f'  ❌ 煤炭占比未下降')

if power_end > power_start:
    print(f'  ✅ 电力占比上升: {power_start*100:.1f}% → {power_end*100:.1f}%')
else:
    print(f'  ❌ 电力占比未上升')

if ren_end > ren_start:
    print(f'  ✅ 清洁能源占比上升: {ren_start*100:.1f}% → {ren_end*100:.1f}%')
else:
    print(f'  ❌ 清洁能源占比未上升')

# 总结
print('\n' + '=' * 100)
print('测试总结')
print('=' * 100)

issues = []
if not (-5 <= transition_growth <= 10):
    issues.append('能源消费过渡不平滑')
if not all_smooth:
    issues.append('能源消费趋势异常')
if has_jump:
    issues.append('碳排放曲线有跳跃')
if coal_end >= coal_start:
    issues.append('煤炭占比未下降')
if power_end <= power_start:
    issues.append('电力占比未上升')

if not issues:
    print('✅ 所有测试通过！模型运行正常。')
else:
    print('❌ 发现以下问题:')
    for issue in issues:
        print(f'  - {issue}')

print('\n建议:')
print('1. 能源消费应该随GDP增长而增长（考虑能效改善）')
print('2. 碳排放应该平滑达峰，不应有跳跃')
print('3. 煤炭占比应该逐年下降')
print('4. 电力和清洁能源占比应该逐年上升')
