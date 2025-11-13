"""
测试修正版Kaya模型
验证算法的正确性
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model.data_processor import DataProcessor
from model.kaya_model_fixed import forecast_kaya_fixed, find_peak_year


def test_simple_scenario():
    """测试简单情景：验证算法逻辑"""
    print("=" * 80)
    print("测试修正版Kaya模型")
    print("=" * 80)
    
    # 加载真实数据
    data_path = 'D:\\software\\carbon_peak3\\backend\\data\\real_data_2022_2024.csv'
    processor = DataProcessor(data_path)
    df = processor.load_data()
    
    # 添加total_energy字段
    # 从真实数据中读取
    real_energy = pd.read_csv(data_path)
    if 'total_energy' in real_energy.columns:
        total_energy_list = real_energy['total_energy'].tolist()
    else:
        # 如果没有，使用处理后的数据估算
        total_energy_list = [980.15, 1098.94, 1081.95]  # 从之前的处理结果
    
    base = processor.prepare_base_dict_for_models()
    base['total_energy'] = total_energy_list
    
    print(f"\n加载数据完成:")
    print(f"  年份: {base['years']}")
    print(f"  GDP: {[f'{x:.2f}' for x in base['gdp']]}")
    print(f"  CO2: {[f'{x:.2f}' for x in base['co2']]}")
    print(f"  能源: {[f'{x:.2f}' for x in base['total_energy']]}")
    
    # 测试情景1：化石能源快速下降
    print("\n" + "=" * 80)
    print("情景1：化石能源每年下降5% (0.05)")
    print("=" * 80)
    
    scenario1 = {
        "name": "快速去化石能源",
        "gdp_growth_rate": 0.06,              # GDP年增长6%
        "efficiency_improvement_rate": 0.04,  # 能效提升4%/年
        "fossil_reduction_rate": 0.05,        # 化石能源占比每年降低5%
        "ren_share_increase": 0.05,           # 可再生能源每年增加5%
    }
    
    result1, peak1 = forecast_kaya_fixed(base, scenario1, 2040, P0=1.0)
    
    print(f"\n预测结果:")
    print(f"{'年份':<8} {'GDP':<10} {'能源':<12} {'CO2':<12} {'化石占比':<10} {'碳因子':<10}")
    print("-" * 80)
    
    for i in range(0, len(result1), 3):  # 每3年显示一次
        r = result1[i]
        print(f"{r['year']:<8} {r['GDP']:<10.2f} {r['Energy']:<12.2f} {r['CO2']:<12.2f} "
              f"{r['fossil_share']*100:<10.1f} {r['CF']:<10.4f}")
    
    if peak1:
        print(f"\n✓ 达峰年份: {peak1}")
    else:
        print(f"\n✗ 未在2040年前达峰")
    
    # 验证：化石能源占比应该在16年后接近0
    base_fossil = base['mix']['coal'][-1] + base['mix']['oil'][-1] + base['mix']['gas'][-1]
    print(f"\n验证化石能源下降速度:")
    print(f"  基年(2024)化石占比: {base_fossil*100:.1f}%")
    print(f"  理论上16年后(2040): {max(0, base_fossil - 0.05*16)*100:.1f}%")
    print(f"  实际预测2040年: {result1[-1]['fossil_share']*100:.1f}%")
    
    # 测试情景2：温和减排
    print("\n" + "=" * 80)
    print("情景2：温和减排（化石能源每年降1%）")
    print("=" * 80)
    
    scenario2 = {
        "name": "温和减排",
        "gdp_growth_rate": 0.07,
        "efficiency_improvement_rate": 0.03,
        "fossil_reduction_rate": 0.01,  # 化石能源占比每年降低1%
        "ren_share_increase": 0.01,
    }
    
    result2, peak2 = forecast_kaya_fixed(base, scenario2, 2060, P0=1.0)
    
    print(f"\n关键年份预测:")
    print(f"{'年份':<8} {'CO2排放':<12} {'能源消费':<12} {'化石占比':<10} {'相比2024':<10}")
    print("-" * 80)
    
    base_co2 = base['co2'][-1]
    for year in [2025, 2030, 2040, 2050, 2060]:
        r = [x for x in result2 if x['year'] == year]
        if r:
            r = r[0]
            change = (r['CO2'] / base_co2 - 1) * 100
            print(f"{r['year']:<8} {r['CO2']:<12.2f} {r['Energy']:<12.2f} "
                  f"{r['fossil_share']*100:<10.1f} {change:+.1f}%")
    
    if peak2:
        print(f"\n✓ 达峰年份: {peak2}")
        peak_data = [r for r in result2 if r['year'] == peak2][0]
        print(f"  峰值排放: {peak_data['CO2']:.2f} 万吨")
    else:
        print(f"\n✗ 未在2060年前达峰")
    
    # 测试情景3：极端情景 - 验证逻辑正确性
    print("\n" + "=" * 80)
    print("情景3：极端减排（化石能源每年降10%，能效提升8%）")
    print("=" * 80)
    
    scenario3 = {
        "name": "极端减排",
        "gdp_growth_rate": 0.05,
        "efficiency_improvement_rate": 0.08,  # 能效大幅提升
        "fossil_reduction_rate": 0.10,        # 化石能源快速下降
        "ren_share_increase": 0.10,
    }
    
    result3, peak3 = forecast_kaya_fixed(base, scenario3, 2040, P0=1.0)
    
    print(f"\n关键指标变化:")
    print(f"  基年(2024):")
    print(f"    CO2: {base['co2'][-1]:.2f} 万吨")
    print(f"    化石占比: {base_fossil*100:.1f}%")
    
    result_2030 = [r for r in result3 if r['year'] == 2030][0]
    result_2040 = [r for r in result3 if r['year'] == 2040][0]
    
    print(f"  2030年:")
    print(f"    CO2: {result_2030['CO2']:.2f} 万吨 ({(result_2030['CO2']/base['co2'][-1]-1)*100:+.1f}%)")
    print(f"    化石占比: {result_2030['fossil_share']*100:.1f}%")
    print(f"  2040年:")
    print(f"    CO2: {result_2040['CO2']:.2f} 万吨 ({(result_2040['CO2']/base['co2'][-1]-1)*100:+.1f}%)")
    print(f"    化石占比: {result_2040['fossil_share']*100:.1f}%")
    
    if peak3:
        print(f"\n✓ 达峰年份: {peak3}")
    else:
        print(f"\n持续下降，未出现峰值")
    
    # 分析结论
    print("\n" + "=" * 80)
    print("算法验证结论")
    print("=" * 80)
    print("1. 化石能源下降速度直接影响碳因子CF的下降")
    print("2. 能效提升速度直接影响能源强度EI的下降")
    print("3. CO2排放取决于：GDP增长 vs (能效提升 + 碳因子下降)")
    print("4. 要达峰需要：能效提升% + 碳因子下降% > GDP增长%")
    
    # 计算达峰条件
    print("\n理论达峰条件:")
    print("  CO2 = GDP × EI × CF")
    print("  CO2增长率 = GDP增长率 - EI下降率 - CF下降率")
    print("  要达峰: GDP增长率 < EI下降率 + CF下降率")
    
    for scenario in [scenario1, scenario2, scenario3]:
        gdp_g = scenario['gdp_growth_rate']
        ei_d = scenario['efficiency_improvement_rate']
        # CF下降率 ≈ 化石能源占比下降率（简化）
        cf_d = scenario['fossil_reduction_rate'] * (base_fossil / 1.0)  # 加权
        co2_g = gdp_g - ei_d - cf_d
        
        print(f"\n  {scenario['name']}:")
        print(f"    GDP增长: {gdp_g*100:.1f}%")
        print(f"    EI下降: {ei_d*100:.1f}%")
        print(f"    CF下降(估算): {cf_d*100:.1f}%")
        print(f"    CO2预期增长: {co2_g*100:+.1f}%")
        if co2_g < 0:
            print(f"    ✓ 应该能达峰并下降")
        else:
            print(f"    ✗ 难以达峰")


if __name__ == '__main__':
    test_simple_scenario()
