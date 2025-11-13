"""
测试后端API是否使用了修正后的模型
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model.data_processor import DataProcessor
from model.scenario_runner import run_scenario
import pandas as pd

def test_backend():
    """测试后端预测功能"""
    print("=" * 80)
    print("测试后端API - 使用修正后的模型")
    print("=" * 80)
    
    # 加载数据
    data_path = 'D:\\software\\carbon_peak3\\backend\\data\\base_year_data.csv'
    print(f"\n1. 加载数据: {data_path}")
    
    processor = DataProcessor(data_path)
    processor.load_data()
    base = processor.prepare_base_dict_for_models()
    
    # 添加total_energy字段
    if 'total_energy' in processor.data.columns:
        base['total_energy'] = processor.data['total_energy'].tolist()
    
    print(f"   基年: {base['years']}")
    print(f"   GDP: {base['gdp']}")
    print(f"   CO2: {base['co2']}")
    if 'total_energy' in base:
        print(f"   能源: {base['total_energy']}")
    
    # 测试场景
    print("\n2. 测试预测情景...")
    
    # 情景1：化石能源快速下降（验证修正是否生效）
    scenario1 = {
        "name": "快速去化石能源（验证测试）",
        "model_type": "kaya",
        "gdp_growth_rate": 0.06,
        "efficiency_improvement_rate": 0.04,
        "fossil_reduction_rate": 0.05,  # 每年降5%
        "ren_share_increase": 0.05,
        "population_growth_rate": 0.0
    }
    
    horizon_year = 2040
    print(f"\n   运行情景: {scenario1['name']}")
    print(f"   化石能源占比年降: {scenario1['fossil_reduction_rate']*100}%")
    
    results_df = run_scenario(base, scenario1, horizon_year)
    
    print(f"\n   预测结果:")
    print(f"   {'年份':<8} {'CO2排放':<12} {'能源消费':<12} {'变化%':<10}")
    print("   " + "-" * 50)
    
    base_co2 = base['co2'][-1]
    for year in [2025, 2030, 2035, 2040]:
        row = results_df[results_df['year'] == year]
        if not row.empty:
            co2 = row['total_emission'].values[0]
            energy = row['energy_consumption'].values[0]
            change = (co2 / base_co2 - 1) * 100
            print(f"   {year:<8} {co2:<12.2f} {energy:<12.2f} {change:+9.1f}%")
    
    # 验证结果
    print("\n3. 验证修正是否生效...")
    result_2040 = results_df[results_df['year'] == 2040]
    if not result_2040.empty:
        co2_2040 = result_2040['total_emission'].values[0]
        reduction = (1 - co2_2040 / base_co2) * 100
        
        print(f"   2024年基准: {base_co2:.2f} 万吨")
        print(f"   2040年预测: {co2_2040:.2f} 万吨")
        print(f"   下降幅度: {reduction:.1f}%")
        
        if reduction > 90:
            print("\n   ✓ 验证通过！化石能源快速下降确实导致CO2大幅下降")
        elif reduction > 50:
            print("\n   ⚠ 部分通过，CO2有显著下降但不如预期")
        else:
            print("\n   ✗ 验证失败！CO2下降不明显，可能仍在使用旧模型")
    
    # 测试2030年达峰情景
    print("\n4. 测试2030年达峰情景...")
    scenario2 = {
        "name": "2030年达峰情景",
        "model_type": "kaya",
        "gdp_growth_rate": 0.07,
        "efficiency_improvement_rate": 0.03,
        "fossil_reduction_rate": 0.02,
        "ren_share_increase": 0.02,
        "population_growth_rate": 0.0
    }
    
    results_df2 = run_scenario(base, scenario2, 2060)
    
    # 寻找达峰年
    peak_year = None
    for i in range(1, len(results_df2) - 1):
        if (results_df2.iloc[i]['total_emission'] > results_df2.iloc[i-1]['total_emission'] and
            results_df2.iloc[i]['total_emission'] > results_df2.iloc[i+1]['total_emission']):
            peak_year = int(results_df2.iloc[i]['year'])
            break
    
    if peak_year:
        print(f"   ✓ 检测到达峰年份: {peak_year}年")
        peak_co2 = results_df2[results_df2['year'] == peak_year]['total_emission'].values[0]
        print(f"   峰值排放: {peak_co2:.2f} 万吨")
    else:
        # 检查是持续增长还是持续下降
        first_co2 = results_df2.iloc[0]['total_emission']
        last_co2 = results_df2.iloc[-1]['total_emission']
        if last_co2 > first_co2 * 1.1:
            print(f"   ○ 持续增长，未达峰")
        else:
            print(f"   ○ 持续下降或平稳，未出现明显峰值")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
    
    return results_df, results_df2


if __name__ == '__main__':
    results1, results2 = test_backend()
