import pandas as pd

# 读取历史数据
df = pd.read_csv('backend/data/sample_data.csv')

print('=' * 60)
print('历史数据分析')
print('=' * 60)
print(df)

print('\n' + '=' * 60)
print('增长率分析')
print('=' * 60)

# GDP增长率
gdp_growth_22_23 = (df.loc[1, 'gdp'] / df.loc[0, 'gdp'] - 1) * 100
gdp_growth_23_24 = (df.loc[2, 'gdp'] / df.loc[1, 'gdp'] - 1) * 100
print(f'GDP增长率:')
print(f'  2022-2023: {gdp_growth_22_23:.2f}%')
print(f'  2023-2024: {gdp_growth_23_24:.2f}%')
print(f'  平均: {(gdp_growth_22_23 + gdp_growth_23_24) / 2:.2f}%')

# 碳排放增长率
co2_growth_22_23 = (df.loc[1, 'co2'] / df.loc[0, 'co2'] - 1) * 100
co2_growth_23_24 = (df.loc[2, 'co2'] / df.loc[1, 'co2'] - 1) * 100
print(f'\n碳排放增长率:')
print(f'  2022-2023: {co2_growth_22_23:.2f}%')
print(f'  2023-2024: {co2_growth_23_24:.2f}%')
print(f'  平均: {(co2_growth_22_23 + co2_growth_23_24) / 2:.2f}%')

# 碳强度变化
ci_change_22_23 = (df.loc[1, 'carbon_intensity'] / df.loc[0, 'carbon_intensity'] - 1) * 100
ci_change_23_24 = (df.loc[2, 'carbon_intensity'] / df.loc[1, 'carbon_intensity'] - 1) * 100
print(f'\n碳强度变化率:')
print(f'  2022-2023: {ci_change_22_23:.2f}%')
print(f'  2023-2024: {ci_change_23_24:.2f}%')
print(f'  平均: {(ci_change_22_23 + ci_change_23_24) / 2:.2f}%')

# 估算能源消费（简化计算）
print(f'\n能源消费估算（基于碳排放和碳强度）:')
for i in range(len(df)):
    energy_est = df.loc[i, 'co2'] / 2.0  # 假设平均排放因子为2.0
    print(f'  {int(df.loc[i, "year"])}: {energy_est:.2f} 万吨标煤')
    if i > 0:
        growth = (energy_est / (df.loc[i-1, 'co2'] / 2.0) - 1) * 100
        print(f'    增长率: {growth:.2f}%')

print('\n' + '=' * 60)
print('问题诊断')
print('=' * 60)
print('1. GDP持续增长（10.2% -> 6.7%）')
print('2. 碳排放缓慢增长（2.24% -> 1.13%）')
print('3. 碳强度持续下降（-7.25% -> -5.17%）')
print('4. 能源消费应该随GDP增长而增长')
print('5. 预测模型需要确保能源消费的连续性')
