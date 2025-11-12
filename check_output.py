"""检查模型输出的实际数据"""
import sys
sys.path.insert(0, 'backend')

from model.data_processor import DataProcessor
from model.scenario_runner import run_scenario
import pandas as pd

# 加载数据
processor = DataProcessor('backend/data/sample_data.csv')
processor.load_data()
base = processor.prepare_base_dict_for_models()

print('=' * 80)
print('历史数据')
print('=' * 80)
print(f'年份: {base["years"]}')
print(f'GDP: {base["gdp"]}')
print(f'CO2: {base["co2"]}')

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

# 运行预测
results = run_scenario(base, scenario, 2035)

print('\n' + '=' * 80)
print('预测结果字段')
print('=' * 80)
print(f'列名: {results.columns.tolist()}')

print('\n' + '=' * 80)
print('前10年预测数据')
print('=' * 80)
print(results.head(10).to_string())

print('\n' + '=' * 80)
print('能源消费检查')
print('=' * 80)

# 检查是否有Energy字段
if 'Energy' in results.columns:
    print('✓ 找到Energy字段')
    print(f'前5年Energy: {results["Energy"].head().tolist()}')
elif 'energy_consumption' in results.columns:
    print('✓ 找到energy_consumption字段')
    print(f'前5年energy_consumption: {results["energy_consumption"].head().tolist()}')
else:
    print('✗ 未找到能源消费字段！')
    print(f'可用字段: {results.columns.tolist()}')

# 检查2024-2025的连续性
print('\n' + '=' * 80)
print('2024-2025连续性检查')
print('=' * 80)

# 计算2024年的能源消费（从历史数据）
ci_2024 = base['co2'][-1] / base['gdp'][-1]
mix_2024 = {f: base['mix'][f][-1] for f in ['coal', 'oil', 'gas', 'ren']}
p_2024 = base['power_share'][-1]

# 排放因子
ef = {'coal': 2.5, 'oil': 2.1, 'gas': 1.6, 'ren': 0.0}
cf_dir = sum(mix_2024[f] * ef[f] for f in mix_2024)
cf_2024 = (1 - p_2024) * cf_dir + p_2024 * 0.65

ei_2024 = ci_2024 / cf_2024
energy_2024 = base['gdp'][-1] * ei_2024

print(f'2024年能源消费（历史）: {energy_2024:.2f}')

# 2025年预测
if 'Energy' in results.columns:
    energy_2025 = results.iloc[0]['Energy']
elif 'energy_consumption' in results.columns:
    energy_2025 = results.iloc[0]['energy_consumption']
else:
    energy_2025 = 0

print(f'2025年能源消费（预测）: {energy_2025:.2f}')
print(f'增长率: {(energy_2025 / energy_2024 - 1) * 100:.2f}%')

# 检查碳排放趋势
print('\n' + '=' * 80)
print('碳排放趋势检查（前15年）')
print('=' * 80)

if 'CO2' in results.columns:
    co2_col = 'CO2'
elif 'total_emission' in results.columns:
    co2_col = 'total_emission'
else:
    co2_col = None

if co2_col:
    for i in range(min(15, len(results))):
        year = int(results.iloc[i]['year'])
        co2 = results.iloc[i][co2_col]
        if i > 0:
            prev_co2 = results.iloc[i-1][co2_col]
            change = co2 - prev_co2
            pct = (co2 / prev_co2 - 1) * 100
            print(f'{year}: {co2:.2f} (变化: {change:+.2f}, {pct:+.2f}%)')
        else:
            print(f'{year}: {co2:.2f}')
