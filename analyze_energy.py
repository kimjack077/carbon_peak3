"""分析能源消费的正确计算方式"""
import pandas as pd

df = pd.read_csv('backend/data/sample_data.csv')

print('=' * 80)
print('数据字段分析')
print('=' * 80)
print(df.columns.tolist())
print('\n数据内容:')
print(df)

print('\n' + '=' * 80)
print('能源消费计算方法分析')
print('=' * 80)

# 方法1: 从碳强度反推
print('\n方法1: 从碳强度反推能源强度')
print('公式: CI = CO2/GDP, EI = E/GDP')
print('假设: CI = EI × CF (碳因子)')

for i in range(len(df)):
    year = df.loc[i, 'year']
    gdp = df.loc[i, 'gdp']
    co2 = df.loc[i, 'co2']
    ci = df.loc[i, 'carbon_intensity']
    
    # 计算综合碳因子（加权平均）
    coal = df.loc[i, 'mix_coal']
    oil = df.loc[i, 'mix_oil']
    gas = df.loc[i, 'mix_gas']
    ren = df.loc[i, 'mix_ren']
    power = df.loc[i, 'power_share']
    
    # 排放因子 (tCO2/tce)
    ef_coal = 2.5
    ef_oil = 2.1
    ef_gas = 1.6
    ef_ren = 0.0
    ef_grid = 0.65  # 电网排放因子
    
    # 直燃部分的碳因子
    cf_direct = coal * ef_coal + oil * ef_oil + gas * ef_gas + ren * ef_ren
    
    # 综合碳因子（考虑电力）
    cf_total = (1 - power) * cf_direct + power * ef_grid
    
    # 能源强度 = 碳强度 / 碳因子
    ei = ci / cf_total
    
    # 能源消费 = GDP × 能源强度
    energy = gdp * ei
    
    print(f'\n{int(year)}年:')
    print(f'  GDP: {gdp:.2f} 万亿元')
    print(f'  CO2: {co2:.2f} 万吨')
    print(f'  碳强度CI: {ci:.4f} 万吨CO2/万亿元')
    print(f'  综合碳因子CF: {cf_total:.4f} 万吨CO2/万吨标煤')
    print(f'  能源强度EI: {ei:.4f} 万吨标煤/万亿元')
    print(f'  能源消费E: {energy:.2f} 万吨标煤')
    
    if i > 0:
        prev_energy = df.loc[i-1, 'gdp'] * (df.loc[i-1, 'carbon_intensity'] / 
                     ((1 - df.loc[i-1, 'power_share']) * 
                      (df.loc[i-1, 'mix_coal'] * ef_coal + df.loc[i-1, 'mix_oil'] * ef_oil + 
                       df.loc[i-1, 'mix_gas'] * ef_gas + df.loc[i-1, 'mix_ren'] * ef_ren) + 
                      df.loc[i-1, 'power_share'] * ef_grid))
        growth = (energy / prev_energy - 1) * 100
        print(f'  能源增长率: {growth:.2f}%')

print('\n' + '=' * 80)
print('结论')
print('=' * 80)
print('1. 能源消费应该从碳强度和碳因子反推')
print('2. 能源消费 = GDP × (碳强度 / 碳因子)')
print('3. 历史能源消费增长率约为 2.23% -> 1.13%')
print('4. 预测时应保持这个趋势，不应出现断崖式变化')
