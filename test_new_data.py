"""测试新的6年历史数据"""
import sys
import os

# 添加backend目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from model.simple_data_processor import SimpleDataProcessor
from model.simple_scenario_runner import run_simple_scenario

def test_new_data():
    print("=" * 60)
    print("测试新的6年历史数据 (2019-2024)")
    print("=" * 60)
    
    # 加载数据
    data_file = 'backend/data/simple_data.csv'
    processor = SimpleDataProcessor(data_file)
    data = processor.load_data()
    
    print(f"\n✓ 成功加载数据: {len(data)} 年")
    print(f"  年份范围: {int(data['year'].min())} - {int(data['year'].max())}")
    
    # 获取基准年数据
    base_data = processor.get_base_year_data()
    print(f"\n✓ 基准年数据 (2024年):")
    print(f"  GDP: {base_data['gdp']:,.2f} 万元")
    print(f"  能耗: {base_data['energy']:,.2f} 万吨标煤")
    print(f"  碳排放: {base_data['co2']:,.2f} 万吨CO2")
    print(f"  能源强度: {base_data['energy_intensity']:.6f}")
    
    # 计算历史增长率
    growth_rates = processor.calculate_growth_rates()
    print(f"\n✓ 历史增长率 (2019-2024年均):")
    print(f"  GDP增长率: {growth_rates['gdp_growth_rate']:>7.2%}")
    print(f"  能耗增长率: {growth_rates['energy_growth_rate']:>7.2%}")
    print(f"  碳排放增长率: {growth_rates['co2_growth_rate']:>7.2%}")
    
    # 测试三种场景
    print("\n" + "=" * 60)
    print("测试三种预测场景")
    print("=" * 60)
    
    scenarios = [
        {
            'name': '历史趋势场景',
            'model_type': 'leap',
            'gdp_growth_rate': 0.083,  # 历史值
            'efficiency_improvement_rate': 0.05,  # 保守设置
            'renewable_increase_rate': 0.015
        },
        {
            'name': '积极达峰场景',
            'model_type': 'kaya',
            'gdp_growth_rate': 0.06,  # 适度放缓
            'efficiency_improvement_rate': 0.08,  # 加大力度
            'renewable_increase_rate': 0.025  # 加快可再生能源
        },
        {
            'name': '保守场景',
            'model_type': 'leap',
            'gdp_growth_rate': 0.10,  # 高增长
            'efficiency_improvement_rate': 0.03,  # 缓慢改善
            'renewable_increase_rate': 0.010  # 常规发展
        }
    ]
    
    horizon_year = 2024 + 30
    
    print(f"\n{'场景名称':<15} {'模型':<6} {'达峰年份':<10} {'峰值(万吨CO2)':<15} {'达峰时间'}")
    print("-" * 70)
    
    for scenario in scenarios:
        results = run_simple_scenario(base_data, scenario, horizon_year)
        
        # 找到碳达峰
        peak_idx = results['co2_emission'].idxmax()
        peak_year = int(results.loc[peak_idx, 'year'])
        peak_value = float(results.loc[peak_idx, 'co2_emission'])
        years_to_peak = peak_year - 2024
        
        print(f"{scenario['name']:<15} {scenario['model_type'].upper():<6} "
              f"{peak_year:<10} {peak_value:>15,.2f} {years_to_peak:>3}年后")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成！")
    print("=" * 60)
    print("\n说明:")
    print("1. 历史趋势场景：基于2019-2024年实际数据的增长趋势")
    print("2. 积极达峰场景：加大能源效率改善和可再生能源发展力度")
    print("3. 保守场景：维持高经济增长，能源转型相对缓慢")

if __name__ == '__main__':
    test_new_data()
