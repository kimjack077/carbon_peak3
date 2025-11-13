"""
简化碳达峰模型使用示例
演示如何使用自定义参数实现碳达峰
"""
import sys
import os

# 添加backend目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from model.simple_model import SimpleCarbonPeakModel, run_simple_analysis


# 您的数据
base_data = {
    'year': [2020, 2021],
    'gdp': [14167844.68, 17243937.42],  # 万元
    'energy': [1120.326643, 1192.619158],  # 万吨标煤
    'co2': [5011.01, 5492.79]  # 万吨CO2
}

print("=" * 80)
print("1. 使用标准情景预测")
print("=" * 80)

model, results, report = run_simple_analysis(base_data, horizon_year=2060)
print(report)


print("\n\n" + "=" * 80)
print("2. 自定义情景：实现碳达峰的必要条件")
print("=" * 80)

# 创建模型实例
model = SimpleCarbonPeakModel(base_data)

# 自定义情景：更激进的减排措施
custom_scenarios = {
    'peak_2028': {
        'name': '2028年达峰情景',
        'description': '通过大幅提升能效和清洁能源占比实现2028年达峰',
        'gdp_growth_rate': 0.03,  # 3% GDP增长
        'energy_intensity_reduction': 0.06,  # 每年能源强度下降6%
        'emission_factor_reduction': 0.05  # 每年排放因子下降5%（清洁能源替代）
    },
    'peak_2030': {
        'name': '2030年达峰情景',
        'description': '通过积极的节能减排措施实现2030年达峰',
        'gdp_growth_rate': 0.04,  # 4% GDP增长
        'energy_intensity_reduction': 0.055,  # 每年能源强度下降5.5%
        'emission_factor_reduction': 0.045  # 每年排放因子下降4.5%
    },
    'peak_2035': {
        'name': '2035年达峰情景',
        'description': '通过适度的节能减排措施实现2035年达峰',
        'gdp_growth_rate': 0.05,  # 5% GDP增长
        'energy_intensity_reduction': 0.05,  # 每年能源强度下降5%
        'emission_factor_reduction': 0.04  # 每年排放因子下降4%
    }
}

print("\n【自定义情景分析】\n")

for scenario_name, scenario_config in custom_scenarios.items():
    df, peak_year = model.predict(scenario_config, horizon_year=2060)
    
    print(f"\n{scenario_config['name']}:")
    print(f"  {scenario_config['description']}")
    print(f"  GDP年增长率: {scenario_config['gdp_growth_rate']*100:.2f}%")
    print(f"  能源强度年下降率: {scenario_config['energy_intensity_reduction']*100:.2f}%")
    print(f"  排放因子年下降率: {scenario_config['emission_factor_reduction']*100:.2f}%")
    
    if peak_year:
        print(f"  [√] 达峰年份: {peak_year}年")
        peak_row = df[df['year'] == peak_year].iloc[0]
        print(f"    峰值排放: {peak_row['CO2']:,.2f} 万吨CO2")
        print(f"    峰值时GDP: {peak_row['GDP']:,.2f} 万元")
        print(f"    相比2021年增长: {((peak_row['CO2'] / base_data['co2'][-1]) - 1) * 100:.1f}%")
    else:
        print(f"  [x] 未能在2060年前达峰")
        last_row = df.iloc[-1]
        print(f"    2060年排放: {last_row['CO2']:,.2f} 万吨CO2")
    
    # 显示关键年份数据
    print("\n  关键年份数据:")
    key_years = [2025, 2030, 2035, 2040, 2050, 2060]
    for year in key_years:
        if year in df['year'].values:
            row = df[df['year'] == year].iloc[0]
            print(f"    {year}年: CO2={row['CO2']:,.0f}万吨, "
                  f"能耗={row['Energy']:,.0f}万吨标煤, "
                  f"GDP={row['GDP']:,.0f}万元")


print("\n\n" + "=" * 80)
print("3. 参数敏感性分析：如何实现碳达峰？")
print("=" * 80)

print("\n根据模型分析，实现碳达峰需要：")
print("\n【关键要素】")
print("1. 能源强度下降率：每年需下降4-6%")
print("   - 通过技术创新提高能源利用效率")
print("   - 产业结构优化，减少高耗能产业比重")
print("")
print("2. 排放因子下降率：每年需下降3-4%")
print("   - 大幅增加清洁能源（风能、太阳能、核能）比重")
print("   - 减少煤炭等高碳能源使用")
print("   - 发展碳捕集与封存技术(CCS)")
print("")
print("3. GDP增长率：控制在4-5%")
print("   - 从高速增长转向高质量发展")
print("   - 避免盲目追求经济总量")
print("")
print("\n【政策建议】")
print("• 短期（2022-2030）：能源强度年降5%，排放因子年降3%")
print("• 中期（2031-2040）：能源强度年降4%，排放因子年降3%")
print("• 长期（2041-2060）：能源强度年降3%，排放因子年降2%")
print("")
print("\n【数据说明】")
print("注意：您的历史数据显示2020-2021年GDP增长率为21.71%")
print("这可能是疫情后恢复性增长，不具有长期可持续性")
print("建议使用5-6%作为长期GDP增长率假设")


print("\n\n" + "=" * 80)
print("4. 导出完整预测数据")
print("=" * 80)

# 导出一个情景的完整数据
scenario = {
    'gdp_growth_rate': 0.05,
    'energy_intensity_reduction': 0.05,
    'emission_factor_reduction': 0.04
}

df, peak_year = model.predict(scenario, horizon_year=2060)

# 保存到CSV
output_dir = os.path.join(os.path.dirname(__file__), 'backend', 'output')
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'simple_prediction.csv')
df.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"\n预测数据已导出到: {output_file}")
if peak_year:
    print(f"该情景事达峰年份: {peak_year}年")

print("\n数据列说明:")
print("  - year: 年份")
print("  - GDP: 总产值（万元）")
print("  - Energy: 综合能耗（万吨标煤）")
print("  - CO2: 碳排放（万吨CO2）")
print("  - EI: 能源强度（万吨标煤/万元）")
print("  - EF: 排放因子（万吨CO2/万吨标煤）")
print("  - CI: 碳强度（万吨CO2/万元）")

print("\n" + "=" * 80)
print("分析完成！")
print("=" * 80)
