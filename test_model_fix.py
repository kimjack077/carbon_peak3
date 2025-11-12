"""测试修复后的模型是否能保持能源消费的连续性"""
import sys
sys.path.insert(0, 'backend')

from model.data_processor import DataProcessor
from model.scenario_runner import run_scenario

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

# 运行预测
print('=' * 80)
print('测试LEAP模型 - 能源消费连续性检查')
print('=' * 80)

results = run_scenario(base, scenario, 2030)

print('\n历史数据（2022-2024）:')
print(f'年份\tGDP\t\t碳排放\t\t能源消费（估算）')
for i in range(len(base['years'])):
    year = base['years'][i]
    gdp = base['gdp'][i]
    co2 = base['co2'][i]
    # 简化估算能源消费
    energy_est = co2 / 2.0
    print(f'{year}\t{gdp:.2f}\t\t{co2:.2f}\t\t{energy_est:.2f}')

print('\n预测数据（2025-2030）:')
print(f'年份\tGDP\t\t碳排放\t\t能源消费')
for i in range(min(6, len(results))):
    year = results.iloc[i]['year']
    gdp = results.iloc[i]['gdp']
    co2 = results.iloc[i]['total_emission']
    energy = results.iloc[i]['energy_consumption']
    print(f'{int(year)}\t{gdp:.2f}\t\t{co2:.2f}\t\t{energy:.2f}')

print('\n能源消费增长率分析:')
# 历史增长率
hist_energy = [base['co2'][i] / 2.0 for i in range(len(base['years']))]
for i in range(1, len(hist_energy)):
    growth = (hist_energy[i] / hist_energy[i-1] - 1) * 100
    print(f'{base["years"][i-1]}-{base["years"][i]}: {growth:.2f}%')

# 预测增长率
print('\n预测期增长率:')
prev_energy = hist_energy[-1]
for i in range(min(6, len(results))):
    energy = results.iloc[i]['energy_consumption']
    growth = (energy / prev_energy - 1) * 100
    year = int(results.iloc[i]['year'])
    print(f'{year-1}-{year}: {growth:.2f}%')
    prev_energy = energy

print('\n' + '=' * 80)
print('检查结果:')
print('=' * 80)
# 检查2024-2025的过渡
energy_2024 = hist_energy[-1]
energy_2025 = results.iloc[0]['energy_consumption']
transition_growth = (energy_2025 / energy_2024 - 1) * 100

if transition_growth < -10:
    print(f'❌ 失败: 2024-2025能源消费断崖式下降 {transition_growth:.2f}%')
elif transition_growth < 0:
    print(f'⚠️  警告: 2024-2025能源消费下降 {transition_growth:.2f}%')
else:
    print(f'✅ 通过: 2024-2025能源消费增长 {transition_growth:.2f}%')

# 检查能源消费趋势
energy_values = [results.iloc[i]['energy_consumption'] for i in range(min(6, len(results)))]
is_increasing = all(energy_values[i] >= energy_values[i-1] * 0.95 for i in range(1, len(energy_values)))

if is_increasing:
    print('✅ 通过: 能源消费保持增长或平稳趋势')
else:
    print('❌ 失败: 能源消费出现异常波动')
