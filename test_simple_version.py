"""测试简化版碳达峰预测系统"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from backend.model.simple_data_processor import SimpleDataProcessor
from backend.model.simple_scenario_runner import run_simple_scenario

def test_data_processor():
    """测试数据处理器"""
    print("=" * 60)
    print("测试1: 数据处理器")
    print("=" * 60)
    
    data_file = os.path.join('backend', 'data', 'simple_data.csv')
    processor = SimpleDataProcessor(data_file)
    
    # 加载数据
    data = processor.load_data()
    print(f"✓ 成功加载数据: {len(data)} 行")
    print(f"  列名: {list(data.columns)}")
    
    # 获取基准年数据
    base_data = processor.get_base_year_data()
    print(f"\n✓ 基准年数据:")
    print(f"  年份: {base_data['year']}")
    print(f"  GDP: {base_data['gdp']:,.2f} 万元")
    print(f"  能耗: {base_data['energy']:,.2f} 万吨标煤")
    print(f"  碳排放: {base_data['co2']:,.2f} 万吨CO2")
    print(f"  能源强度: {base_data['energy_intensity']:.6f}")
    print(f"  碳强度: {base_data['carbon_intensity']:.6f}")
    
    # 计算增长率
    growth_rates = processor.calculate_growth_rates()
    print(f"\n✓ 历史增长率:")
    print(f"  GDP增长率: {growth_rates['gdp_growth_rate']:.2%}")
    print(f"  能耗增长率: {growth_rates['energy_growth_rate']:.2%}")
    print(f"  碳排放增长率: {growth_rates['co2_growth_rate']:.2%}")
    
    return base_data

def test_leap_model(base_data):
    """测试LEAP模型"""
    print("\n" + "=" * 60)
    print("测试2: LEAP模型")
    print("=" * 60)
    
    params = {
        'model_type': 'leap',
        'gdp_growth_rate': 0.05,
        'efficiency_improvement_rate': 0.03,
        'renewable_increase_rate': 0.015,
    }
    
    print(f"场景参数:")
    print(f"  模型类型: LEAP")
    print(f"  GDP增长率: {params['gdp_growth_rate']:.1%}")
    print(f"  能源效率改善率: {params['efficiency_improvement_rate']:.1%}")
    print(f"  可再生能源占比提升率: {params['renewable_increase_rate']:.1%}")
    
    horizon_year = base_data['year'] + 30
    results = run_simple_scenario(base_data, params, horizon_year)
    
    print(f"\n✓ 预测结果 (前5年):")
    print(results.head())
    
    # 找到碳达峰
    peak_idx = results['co2_emission'].idxmax()
    peak_year = int(results.loc[peak_idx, 'year'])
    peak_value = float(results.loc[peak_idx, 'co2_emission'])
    
    print(f"\n✓ 碳达峰信息:")
    print(f"  达峰年份: {peak_year}")
    print(f"  峰值: {peak_value:,.2f} 万吨CO2")
    
    return results

def test_kaya_model(base_data):
    """测试Kaya模型"""
    print("\n" + "=" * 60)
    print("测试3: Kaya模型")
    print("=" * 60)
    
    params = {
        'model_type': 'kaya',
        'gdp_growth_rate': 0.05,
        'efficiency_improvement_rate': 0.03,
        'renewable_increase_rate': 0.015,
    }
    
    print(f"场景参数:")
    print(f"  模型类型: Kaya")
    print(f"  GDP增长率: {params['gdp_growth_rate']:.1%}")
    print(f"  能源效率改善率: {params['efficiency_improvement_rate']:.1%}")
    print(f"  可再生能源占比提升率: {params['renewable_increase_rate']:.1%}")
    
    horizon_year = base_data['year'] + 30
    results = run_simple_scenario(base_data, params, horizon_year)
    
    print(f"\n✓ 预测结果 (前5年):")
    print(results.head())
    
    # 找到碳达峰
    peak_idx = results['co2_emission'].idxmax()
    peak_year = int(results.loc[peak_idx, 'year'])
    peak_value = float(results.loc[peak_idx, 'co2_emission'])
    
    print(f"\n✓ 碳达峰信息:")
    print(f"  达峰年份: {peak_year}")
    print(f"  峰值: {peak_value:,.2f} 万吨CO2")
    
    return results

def test_scenario_comparison(base_data):
    """测试不同场景对比"""
    print("\n" + "=" * 60)
    print("测试4: 多场景对比")
    print("=" * 60)
    
    scenarios = [
        {
            'name': '积极达峰',
            'model_type': 'leap',
            'gdp_growth_rate': 0.03,
            'efficiency_improvement_rate': 0.05,
            'renewable_increase_rate': 0.02,
        },
        {
            'name': '基准达峰',
            'model_type': 'kaya',
            'gdp_growth_rate': 0.05,
            'efficiency_improvement_rate': 0.03,
            'renewable_increase_rate': 0.015,
        },
        {
            'name': '保守场景',
            'model_type': 'leap',
            'gdp_growth_rate': 0.06,
            'efficiency_improvement_rate': 0.02,
            'renewable_increase_rate': 0.01,
        }
    ]
    
    horizon_year = base_data['year'] + 30
    
    print(f"\n场景对比结果:\n")
    print(f"{'场景名称':<12} {'模型':<6} {'达峰年份':<10} {'峰值(万吨CO2)':<15}")
    print("-" * 60)
    
    for scenario in scenarios:
        results = run_simple_scenario(base_data, scenario, horizon_year)
        peak_idx = results['co2_emission'].idxmax()
        peak_year = int(results.loc[peak_idx, 'year'])
        peak_value = float(results.loc[peak_idx, 'co2_emission'])
        
        print(f"{scenario['name']:<12} {scenario['model_type'].upper():<6} {peak_year:<10} {peak_value:>15,.2f}")

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("简化版碳达峰预测系统 - 测试套件")
    print("=" * 60)
    
    try:
        # 测试1: 数据处理
        base_data = test_data_processor()
        
        # 测试2: LEAP模型
        test_leap_model(base_data)
        
        # 测试3: Kaya模型
        test_kaya_model(base_data)
        
        # 测试4: 场景对比
        test_scenario_comparison(base_data)
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n系统已准备就绪，可以运行:")
        print("  python simple_app.py")
        print("\n然后访问前端查看可视化结果")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
