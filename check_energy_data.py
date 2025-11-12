"""检查能源消费数据计算"""
import pandas as pd
import numpy as np

# 加载示例数据
df = pd.read_csv('backend/data/sample_data.csv')

print("原始数据:")
print(df)
print("\n" + "="*60)

# 排放因子
EMISSION_FACTORS = {
    "coal": 2.5,
    "oil": 2.1,
    "gas": 1.6,
    "ren": 0.0
}
EF_grid = 0.65  # 电网排放因子
kappa = 1.0

# 计算能源消费
energy_list = []
for i in range(len(df)):
    year = df.iloc[i]['year']
    gdp = df.iloc[i]['gdp']
    ci = df.iloc[i]['carbon_intensity']
    
    # 计算综合碳因子
    mix_coal = df.iloc[i]['mix_coal']
    mix_oil = df.iloc[i]['mix_oil']
    mix_gas = df.iloc[i]['mix_gas']
    mix_ren = df.iloc[i]['mix_ren']
    power_share = df.iloc[i]['power_share']
    
    cf_direct = (mix_coal * EMISSION_FACTORS['coal'] + 
                mix_oil * EMISSION_FACTORS['oil'] + 
                mix_gas * EMISSION_FACTORS['gas'] + 
                mix_ren * EMISSION_FACTORS['ren'])
    cf_total = (1 - power_share) * cf_direct + power_share * (EF_grid * kappa)
    
    # 能源强度 = 碳强度 / 碳因子
    ei = ci / max(cf_total, 1e-9)
    
    # 能源消费 = GDP × 能源强度
    energy = gdp * ei
    energy_list.append(energy)
    
    print(f"{year}年:")
    print(f"  GDP: {gdp:.2f} 万亿元")
    print(f"  碳强度: {ci:.4f} 万吨CO2/万亿元")
    print(f"  综合碳因子: {cf_total:.4f} 万吨CO2/万吨标煤")
    print(f"  能源强度: {ei:.4f} 万吨标煤/万亿元")
    print(f"  能源消费: {energy:.2f} 万吨标煤")
    
    if i > 0:
        growth = (energy / energy_list[i-1] - 1) * 100
        print(f"  增长率: {growth:.2f}%")
    print()

# 检查增长率
print("\n增长率分析:")
for i in range(1, len(energy_list)):
    year = df.iloc[i]['year']
    prev_year = df.iloc[i-1]['year']
    growth = (energy_list[i] / energy_list[i-1] - 1) * 100
    print(f"{prev_year}-{year}: {growth:.2f}%")

# 检查数据是否合理
print("\n" + "="*60)
print("数据合理性检查:")
for i, energy in enumerate(energy_list):
    year = df.iloc[i]['year']
    if energy < 1000:  # 能源消费应该大于1000万吨标煤
        print(f"⚠️  警告: {year}年能源消费过低: {energy:.2f}万吨标煤")
    if energy > 50000:  # 能源消费不应该超过50000万吨标煤
        print(f"⚠️  警告: {year}年能源消费过高: {energy:.2f}万吨标煤")

print("\n建议的能源消费数据:")
for i, year in enumerate(df['year']):
    print(f"{year}: {energy_list[i]:.2f}")