"""
测试图表生成功能
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model.data_processor import DataProcessor
from model.scenario_runner import run_scenario
from utils.plot_results import plot_carbon_peak, plot_energy_mix
import pandas as pd

def test_chart_generation():
    """测试图表生成"""
    print("=" * 80)
    print("测试图表生成功能")
    print("=" * 80)
    
    # 加载数据
    data_path = 'D:\\software\\carbon_peak3\\backend\\data\\base_year_data.csv'
    print(f"\n1. 加载数据...")
    
    processor = DataProcessor(data_path)
    processor.load_data()
    base = processor.prepare_base_dict_for_models()
    
    # 添加total_energy字段
    if 'total_energy' in processor.data.columns:
        base['total_energy'] = processor.data['total_energy'].tolist()
    
    print(f"   ✓ 数据加载完成")
    
    # 运行多个情景
    print(f"\n2. 运行预测情景...")
    
    scenarios = {
        "2030年达峰": {
            "model_type": "kaya",
            "gdp_growth_rate": 0.07,
            "efficiency_improvement_rate": 0.03,
            "fossil_reduction_rate": 0.02,
            "ren_share_increase": 0.02,
            "population_growth_rate": 0.0
        },
        "持续下降": {
            "model_type": "kaya",
            "gdp_growth_rate": 0.06,
            "efficiency_improvement_rate": 0.04,
            "fossil_reduction_rate": 0.03,
            "ren_share_increase": 0.03,
            "population_growth_rate": 0.0
        },
        "基准情景": {
            "model_type": "kaya",
            "gdp_growth_rate": 0.07,
            "efficiency_improvement_rate": 0.03,
            "fossil_reduction_rate": 0.008,
            "ren_share_increase": 0.008,
            "population_growth_rate": 0.0
        }
    }
    
    results_dict = {}
    horizon_year = 2060
    
    for scenario_name, scenario_params in scenarios.items():
        print(f"   运行: {scenario_name}...")
        results = run_scenario(base, scenario_params, horizon_year)
        results_dict[scenario_name] = results
        print(f"   ✓ 完成，生成 {len(results)} 年预测数据")
    
    # 测试碳达峰图表生成
    print(f"\n3. 生成碳达峰对比图...")
    output_dir = 'D:\\software\\carbon_peak3\\backend\\output'
    os.makedirs(output_dir, exist_ok=True)
    
    carbon_peak_path = os.path.join(output_dir, 'carbon_peak.png')
    
    try:
        plot_carbon_peak(results_dict, carbon_peak_path)
        if os.path.exists(carbon_peak_path):
            file_size = os.path.getsize(carbon_peak_path)
            print(f"   ✓ 碳达峰图表生成成功: {carbon_peak_path}")
            print(f"   文件大小: {file_size / 1024:.2f} KB")
        else:
            print(f"   ✗ 图表文件未生成")
    except Exception as e:
        print(f"   ✗ 图表生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 测试能源结构图表生成
    print(f"\n4. 生成能源结构图...")
    energy_mix_path = os.path.join(output_dir, 'energy_mix.png')
    
    try:
        # 使用第一个情景的数据
        first_scenario = list(results_dict.keys())[0]
        plot_energy_mix(results_dict[first_scenario], energy_mix_path)
        if os.path.exists(energy_mix_path):
            file_size = os.path.getsize(energy_mix_path)
            print(f"   ✓ 能源结构图生成成功: {energy_mix_path}")
            print(f"   文件大小: {file_size / 1024:.2f} KB")
        else:
            print(f"   ✗ 图表文件未生成")
    except Exception as e:
        print(f"   ✗ 图表生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 检查输出目录
    print(f"\n5. 检查输出目录...")
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        print(f"   输出目录: {output_dir}")
        print(f"   文件列表:")
        for f in files:
            if f.endswith('.png'):
                file_path = os.path.join(output_dir, f)
                file_size = os.path.getsize(file_path) / 1024
                print(f"     - {f} ({file_size:.2f} KB)")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    
    return results_dict


if __name__ == '__main__':
    results = test_chart_generation()
