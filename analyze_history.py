"""分析历史数据计算默认参数"""
import pandas as pd

# 读取数据
df = pd.read_csv('backend/data/simple_data.csv')

print("=" * 60)
print("历史数据分析 (2019-2024)")
print("=" * 60)
print("\n原始数据:")
print(df.to_string(index=False))

# 计算年数
years = len(df) - 1
print(f"\n数据年限: {years} 年 (2019-2024)")

# 计算年均增长率 (CAGR)
gdp_growth = (df['gdp'].iloc[-1] / df['gdp'].iloc[0]) ** (1/years) - 1
energy_growth = (df['energy_consumption'].iloc[-1] / df['energy_consumption'].iloc[0]) ** (1/years) - 1
co2_growth = (df['co2_emission'].iloc[-1] / df['co2_emission'].iloc[0]) ** (1/years) - 1

print("\n" + "=" * 60)
print("历史年均增长率 (CAGR)")
print("=" * 60)
print(f"GDP年均增长率:        {gdp_growth:>8.2%}")
print(f"能耗年均增长率:       {energy_growth:>8.2%}")
print(f"碳排放年均增长率:     {co2_growth:>8.2%}")

# 计算能源强度
ei_2019 = df.iloc[0]['energy_consumption'] / df.iloc[0]['gdp']
ei_2024 = df.iloc[-1]['energy_consumption'] / df.iloc[-1]['gdp']
ei_change_rate = (ei_2024 / ei_2019) ** (1/years) - 1

print("\n" + "=" * 60)
print("能源强度分析 (能耗/GDP)")
print("=" * 60)
print(f"2019年能源强度:       {ei_2019:.6f}")
print(f"2024年能源强度:       {ei_2024:.6f}")
print(f"能源强度年均变化率:   {ei_change_rate:>8.2%}")

# 能源效率改善率 = -能源强度变化率
efficiency_improvement = -ei_change_rate

print("\n" + "=" * 60)
print("推荐的默认场景参数")
print("=" * 60)
print(f"GDP增长率:                    {gdp_growth:.3f}  ({gdp_growth:.1%})")
print(f"能源效率改善率:               {max(0, efficiency_improvement):.3f}  ({max(0, efficiency_improvement):.1%})")
print(f"可再生能源占比提升率:         0.015  (1.5%/年，政策目标)")

print("\n说明:")
if efficiency_improvement < 0:
    print(f"  ⚠️ 历史能源强度上升了{-efficiency_improvement:.2%}/年，说明能源效率在下降！")
    print(f"  建议设置能源效率改善率为正值（如0.02-0.03），以改善未来趋势")
else:
    print(f"  ✓ 历史能源强度下降了{efficiency_improvement:.2%}/年，能源效率持续改善")

print("\n" + "=" * 60)
print("默认场景设置建议")
print("=" * 60)
print("基于历史数据的基准场景:")
print(f"  - GDP增长率: {gdp_growth:.3f}")
print(f"  - 能源效率改善率: {max(0.02, efficiency_improvement):.3f} (取历史值或至少2%)")
print(f"  - 可再生能源占比提升率: 0.015 (政策目标)")
