"""检查能源消费数据单位问题"""
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
print("3. 碳强度 = CO2/GDP = 万吨/万亿元 = 1/万吨")

# 计算2022年的能源消费，考虑单位转换
year = 2022
gdp = df[df['year'] == year]['gdp'].iloc[0]  # 万亿元
co2 = df[df['year'] == year]['co2'].iloc[0]  # 万吨
ci = df[df['year'] == year]['carbon_intensity'].iloc[0]  # 万吨/万亿元

print(f"\n{year}年数据:")
print(f"GDP: {gdp} 万亿元 = {gdp * 10000} 亿元")
print(f"CO2: {co2} 万吨")
print(f"碳强度: {ci} 万吨/万亿元")

# 假设碳强度单位应该是万吨/亿元（而不是万吨/万亿元）
ci_corrected = ci / 10000  # 转换为万吨/亿元
print(f"修正后的碳强度: {ci_corrected} 万吨/亿元")

# 计算能源消费
# 能源消费 = GDP × 能源强度
# 能源强度 = 碳强度 / 碳因子
# 碳因子约为 1.5 万吨CO2/万吨标煤

cf = 1.5  # 万吨CO2/万吨标煤
ei = ci_corrected / cf  # 万吨标煤/亿元
energy = gdp * 10000 * ei  # 亿元 × 万吨标煤/亿元 = 万吨标煤

print(f"能源强度: {ei} 万吨标煤/亿元")
print(f"能源消费: {energy} 万吨标煤")

# 与实际数据比较
print(f"\n实际中国2022年能源消费约为: 54.1亿吨标煤")
print(f"计算结果: {energy/10000:.2f} 亿吨标煤")
print(f"比例: {energy/541000:.2f}")

# 修正计算方法
print("\n" + "="*60)
print("修正计算方法:")
print("假设碳强度单位是万吨/亿元，而不是万吨/万亿元")

for i in range(len(df)):
    year = df.iloc[i]['year']
    gdp = df.iloc[i]['gdp']  # 万亿元
    co2 = df.iloc[i]['co2']  # 万吨
    ci = df.iloc[i]['carbon_intensity']  # 万吨/万亿元
    
    # 修正碳强度单位
    ci_corrected = ci / 10000  # 转换为万吨/亿元
    
    # 计算能源消费
    cf = 1.5  # 万吨CO2/万吨标煤
    ei = ci_corrected / cf  # 万吨标煤/亿元
    energy = gdp * 10000 * ei  # 亿元 × 万吨标煤/亿元 = 万吨标煤
    
    print(f"{year}年: {energy:.0f} 万吨标煤 ({energy/10000:.2f} 亿吨标煤)")
    
    if i > 0:
        growth = (energy / prev_energy - 1) * 100
        print(f"  增长率: {growth:.2f}%")
    
    prev_energy = energy