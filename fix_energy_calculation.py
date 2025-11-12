"""修正能源消费数据计算"""
import pandas as pd

# 加载示例数据
df = pd.read_csv('backend/data/sample_data.csv')

print("原始数据:")
print(df)
print("\n" + "="*60)

# 分析数据单位
print("数据分析:")
print("1. GDP单位: 万亿元")
print("2. CO2单位: 万吨")
print("3. 碳强度应该是: 吨/万元 (而不是万吨/万亿元)")

# 重新计算能源消费
for i in range(len(df)):
    year = df.iloc[i]['year']
    gdp = df.iloc[i]['gdp']  # 万亿元
    co2 = df.iloc[i]['co2']  # 万吨
    ci = df.iloc[i]['carbon_intensity']  # 万吨/万亿元
    
    # 将碳强度转换为 吨/万元
    # 1 万吨/万亿元 = 1 吨/万元
    ci_ton_per_10k = ci  # 直接使用，因为单位转换系数是1
    
    # 计算能源消费
    # 能源消费 = GDP × 能源强度
    # 能源强度 = 碳强度 / 碳因子
    # 碳因子约为 1.5 吨CO2/吨标煤
    
    cf = 1.5  # 吨CO2/吨标煤
    ei = ci_ton_per_10k / cf  # 吨标煤/万元
    energy = gdp * 10000 * ei  # 亿元 × 吨标煤/万元 = 万吨标煤
    
    print(f"{year}年:")
    print(f"  GDP: {gdp} 万亿元")
    print(f"  CO2: {co2} 万吨")
    print(f"  碳强度: {ci} 万吨/万亿元 = {ci_ton_per_10k} 吨/万元")
    print(f"  碳因子: {cf} 吨CO2/吨标煤")
    print(f"  能源强度: {ei} 吨标煤/万元")
    print(f"  能源消费: {energy:.0f} 万吨标煤 ({energy/10000:.2f} 亿吨标煤)")
    
    if i > 0:
        growth = (energy / prev_energy - 1) * 100
        print(f"  增长率: {growth:.2f}%")
    
    prev_energy = energy
    print()

# 与实际数据比较
print("与实际数据比较:")
print("2022年中国实际能源消费: 54.1亿吨标煤")
print("计算结果需要接近这个数值")

# 尝试调整碳因子
print("\n" + "="*60)
print("尝试调整碳因子使计算结果更接近实际:")

# 使用实际能源消费反推碳因子
actual_energy_2022 = 54.1 * 10000  # 万吨标煤
gdp_2022 = df[df['year'] == 2022]['gdp'].iloc[0] * 10000  # 亿元
ci_2022 = df[df['year'] == 2022]['carbon_intensity'].iloc[0]  # 吨/万元

# 从实际能源消费反推碳因子
ei_actual = actual_energy_2022 / gdp_2022  # 吨标煤/亿元
cf_actual = ci_2022 / ei_actual  # 吨CO2/吨标煤

print(f"从2022年实际数据反推的碳因子: {cf_actual:.2f} 吨CO2/吨标煤")

# 使用调整后的碳因子重新计算
print("\n使用调整后的碳因子重新计算:")
cf_adjusted = cf_actual

for i in range(len(df)):
    year = df.iloc[i]['year']
    gdp = df.iloc[i]['gdp']  # 万亿元
    ci = df.iloc[i]['carbon_intensity']  # 吨/万元
    
    ei = ci / cf_adjusted  # 吨标煤/万元
    energy = gdp * 10000 * ei  # 亿元 × 吨标煤/万元 = 万吨标煤
    
    print(f"{year}年: {energy:.0f} 万吨标煤 ({energy/10000:.2f} 亿吨标煤)")
    
    if i > 0:
        growth = (energy / prev_energy - 1) * 100
        print(f"  增长率: {growth:.2f}%")
    
    prev_energy = energy