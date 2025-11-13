"""
基于真实三年数据的碳达峰预测测试
使用2022-2024年的实际数据进行预测
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import sys
import os

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model.data_processor import DataProcessor
from model.kaya_model_fixed import forecast_kaya_fixed, find_peak_year

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def create_realistic_scenarios():
    """
    根据历史数据趋势创建符合实际的预测情景
    
    历史趋势分析（2022-2024）:
    - GDP年均增长: 10.54%
    - CO2年均变化: +4.80%
    - 能源年均变化: +5.29%
    - 碳强度年均下降: -5.27%
    - 能源结构: 煤炭占比83%，石油0.1%，天然气0.02%，可再生16.8%
    """
    
    # 基准情景：延续当前趋势
    baseline = {
        "name": "基准情景（延续当前趋势）",
        "gdp_growth_rate": 0.07,              # GDP年增閿7%
        "efficiency_improvement_rate": 0.03,  # 能效提升33%/年
        "fossil_reduction_rate": 0.008,       # 化石能源占比年陥0.8%
        "ren_share_increase": 0.008,          # 可再生能源年增0.8%
    }
    
    # 强化政策情景：积极减排
    enhanced_policy = {
        "name": "强化政策情景（积极减排）",
        "gdp_growth_rate": 0.065,             # GDP年增閿6.5%
        "efficiency_improvement_rate": 0.04,  # 能效提升44%/年
        "fossil_reduction_rate": 0.030,       # 化石能源占比年陥3.0%（积极去化石化）
        "ren_share_increase": 0.030,          # 可再生能源年增3.0%
    }
    
    # 低碳转型情景：加速脱碳
    low_carbon = {
        "name": "低碳转型情景（加速脱碳）",
        "gdp_growth_rate": 0.06,              # GDP年增閿6%
        "efficiency_improvement_rate": 0.05,  # 能效提升55%/年
        "fossil_reduction_rate": 0.050,       # 化石能源占比年陥5.0%（大力去化石化）
        "ren_share_increase": 0.050,          # 可再生能源年增5.0%
    }
    
    # 延续高排放情景：弱减排（对比参照）
    high_emission = {
        "name": "延续高排放情景（弱减排）",
        "gdp_growth_rate": 0.075,             # GDP年增閿7.5%
        "efficiency_improvement_rate": 0.02,  # 能效提升22%/年
        "fossil_reduction_rate": 0.005,       # 化石能源占比年陥0.5%
        "ren_share_increase": 0.005,          # 可再生能源年增0.5%
    }
    
    return {
        "baseline": baseline,
        "enhanced_policy": enhanced_policy,
        "low_carbon": low_carbon,
        "high_emission": high_emission
    }


def run_predictions():
    """运行预测并分析结果"""
    print("=" * 70)
    print("基于真实三年数据的碳达峰预测")
    print("数据来源：2022-2024年实际能源消耗和排放数据")
    print("=" * 70)
    
    # 1. 加载真实数据
    print("\n1. 加载数据...")
    data_path = 'D:\\software\\carbon_peak3\\backend\\data\\real_data_2022_2024.csv'
    processor = DataProcessor(data_path)
    df = processor.load_data()
    base = processor.prepare_base_dict_for_models()
    
    # 添加total_energy字段
    real_energy = pd.read_csv(data_path)
    if 'total_energy' in real_energy.columns:
        base['total_energy'] = real_energy['total_energy'].tolist()
    else:
        base['total_energy'] = [980.15, 1098.94, 1081.95]
    
    print(f"   历史数据年份: {base['years']}")
    print(f"   基年GDP: {base['gdp'][-1]:.2f} 亿元")
    print(f"   基年CO2排放: {base['co2'][-1]:.2f} 万吨")
    print(f"   基年碳强度: {base['ci'][-1]:.4f} 万吨CO2/亿元")
    
    # 2. 创建情景
    print("\n2. 创建预测情景...")
    scenarios = create_realistic_scenarios()
    for key, scenario in scenarios.items():
        print(f"   - {scenario['name']}")
    
    # 3. 运行预测
    print("\n3. 运行预测模型...")
    horizon_year = 2060
    results = {}
    peaks = {}
    
    for key, scenario in scenarios.items():
        print(f"\n   运行情景: {scenario['name']}")
        result, peak = forecast_kaya_fixed(base, scenario, horizon_year, P0=1.0)
        results[key] = result
        peaks[key] = peak
        
        if peak:
            print(f"   → 达峰年份: {peak}")
            peak_data = [r for r in result if r['year'] == peak][0]
            print(f"   → 峰值排放: {peak_data['CO2']:.2f} 万吨")
            print(f"   → 峰值相比2024年: {(peak_data['CO2'] / base['co2'][-1] - 1) * 100:+.1f}%")
        else:
            print(f"   → 未在{horizon_year}年前达峰")
            last_co2 = result[-1]['CO2']
            print(f"   → {horizon_year}年排放: {last_co2:.2f} 万吨")
    
    # 4. 生成详细报告
    print("\n" + "=" * 70)
    print("预测结果详细分析")
    print("=" * 70)
    
    for key, scenario in scenarios.items():
        print(f"\n【{scenario['name']}】")
        print("-" * 70)
        
        result = results[key]
        peak = peaks[key]
        
        # 关键年份数据
        years_of_interest = [2025, 2030, 2040, 2050, 2060]
        print("\n关键年份预测:")
        print(f"{'年份':<8} {'GDP(亿元)':<12} {'CO2(万吨)':<12} {'碳强度':<10} {'能源(万吨标煤)':<15}")
        print("-" * 70)
        
        for year in years_of_interest:
            data = [r for r in result if r['year'] == year]
            if data:
                d = data[0]
                print(f"{d['year']:<8} {d['GDP']:<12.2f} {d['CO2']:<12.2f} {d['CI']:<10.4f} {d['Energy']:<15.2f}")
        
        # 达峰分析
        if peak:
            print(f"\n✓ 达峰年份: {peak}年")
            peak_data = [r for r in result if r['year'] == peak][0]
            print(f"  - 峰值排放: {peak_data['CO2']:.2f} 万吨CO2")
            print(f"  - 相比2024年: {(peak_data['CO2'] / base['co2'][-1] - 1) * 100:+.1f}%")
            
            # 2060年情况
            data_2060 = [r for r in result if r['year'] == 2060][0]
            reduction_from_peak = (1 - data_2060['CO2'] / peak_data['CO2']) * 100
            print(f"  - 2060年排放: {data_2060['CO2']:.2f} 万吨CO2")
            print(f"  - 相比峰值下降: {reduction_from_peak:.1f}%")
        else:
            print(f"\n✗ 未在2060年前达峰")
        
        # 能源结构演变
        print("\n能源结构演变:")
        data_2024 = {'year': 2024, 'mix_coal': base['mix']['coal'][-1], 
                     'mix_oil': base['mix']['oil'][-1], 'mix_gas': base['mix']['gas'][-1],
                     'mix_ren': base['mix']['ren'][-1]}
        data_2030 = [r for r in result if r['year'] == 2030][0]
        data_2060 = [r for r in result if r['year'] == 2060][0]
        
        print(f"  2024年: 煤{data_2024['mix_coal']*100:.1f}% 油{data_2024['mix_oil']*100:.1f}% "
              f"气{data_2024['mix_gas']*100:.1f}% 可再生{data_2024['mix_ren']*100:.1f}%")
        print(f"  2030年: 煤{data_2030['mix_coal']*100:.1f}% 油{data_2030['mix_oil']*100:.1f}% "
              f"气{data_2030['mix_gas']*100:.1f}% 可再生{data_2030['mix_ren']*100:.1f}%")
        print(f"  2060年: 煤{data_2060['mix_coal']*100:.1f}% 油{data_2060['mix_oil']*100:.1f}% "
              f"气{data_2060['mix_gas']*100:.1f}% 可再生{data_2060['mix_ren']*100:.1f}%")
    
    # 5. 绘制对比图
    print("\n5. 生成可视化图表...")
    plot_comparison(results, peaks, base, scenarios)
    
    return results, peaks


def plot_comparison(results, peaks, base, scenarios):
    """绘制情景对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('基于真实数据的碳达峰预测情景对比 (2022-2060)', fontsize=16, fontweight='bold')
    
    colors = {
        'baseline': '#2E86AB',
        'enhanced_policy': '#A23B72',
        'low_carbon': '#F18F01',
        'high_emission': '#C73E1D'
    }
    
    # (1) CO2排放趋势
    ax1 = axes[0, 0]
    # 绘制历史数据
    ax1.plot(base['years'], base['co2'], 'ko-', linewidth=2, markersize=8, label='历史数据', zorder=10)
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        co2 = [r['CO2'] for r in result]
        label = scenarios[key]['name']
        ax1.plot(years, co2, color=colors[key], linewidth=2, label=label, alpha=0.8)
        
        # 标记达峰点
        if peaks[key]:
            peak_data = [r for r in result if r['year'] == peaks[key]][0]
            ax1.plot(peaks[key], peak_data['CO2'], 'o', color=colors[key], 
                    markersize=12, markeredgewidth=2, markeredgecolor='black', zorder=5)
            ax1.text(peaks[key], peak_data['CO2'], f'{peaks[key]}年', 
                    fontsize=9, ha='center', va='bottom')
    
    ax1.set_xlabel('年份', fontsize=12)
    ax1.set_ylabel('CO2排放量（万吨）', fontsize=12)
    ax1.set_title('CO2排放趋势对比', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=2024, color='gray', linestyle='--', alpha=0.5, label='基年')
    
    # (2) 碳强度变化
    ax2 = axes[0, 1]
    ax2.plot(base['years'], base['ci'], 'ko-', linewidth=2, markersize=8, label='历史数据', zorder=10)
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        ci = [r['CI'] for r in result]
        label = scenarios[key]['name']
        ax2.plot(years, ci, color=colors[key], linewidth=2, label=label, alpha=0.8)
    
    ax2.set_xlabel('年份', fontsize=12)
    ax2.set_ylabel('碳强度（万吨CO2/亿元GDP）', fontsize=12)
    ax2.set_title('碳强度变化趋势', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.axvline(x=2024, color='gray', linestyle='--', alpha=0.5)
    
    # (3) 能源消费总量
    ax3 = axes[1, 0]
    # 历史能源消费（从total_energy反算）
    hist_energy = []
    for i in range(len(base['years'])):
        ci = base['ci'][i]
        gdp = base['gdp'][i]
        # 从历史数据文件读取
        hist_energy.append(None)  # 暂不绘制，避免误差
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        energy = [r['Energy'] for r in result]
        label = scenarios[key]['name']
        ax3.plot(years, energy, color=colors[key], linewidth=2, label=label, alpha=0.8)
    
    ax3.set_xlabel('年份', fontsize=12)
    ax3.set_ylabel('能源消费总量（万吨标煤）', fontsize=12)
    ax3.set_title('能源消费总量趋势', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9, loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.axvline(x=2024, color='gray', linestyle='--', alpha=0.5)
    
    # (4) 可再生能源占比
    ax4 = axes[1, 1]
    hist_ren = [base['mix']['ren'][i] * 100 for i in range(len(base['years']))]
    ax4.plot(base['years'], hist_ren, 'ko-', linewidth=2, markersize=8, label='历史数据', zorder=10)
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        ren = [r['mix_ren'] * 100 for r in result]
        label = scenarios[key]['name']
        ax4.plot(years, ren, color=colors[key], linewidth=2, label=label, alpha=0.8)
    
    ax4.set_xlabel('年份', fontsize=12)
    ax4.set_ylabel('可再生能源占比（%）', fontsize=12)
    ax4.set_title('可再生能源占比趋势', fontsize=13, fontweight='bold')
    ax4.legend(fontsize=9, loc='best')
    ax4.grid(True, alpha=0.3)
    ax4.axvline(x=2024, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    # 保存图表
    output_path = 'D:\\software\\carbon_peak3\\real_data_prediction_results.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   图表已保存至: {output_path}")
    
    # plt.show()  # 取消注释以显示图表


if __name__ == '__main__':
    results, peaks = run_predictions()
    print("\n" + "=" * 70)
    print("预测完成！")
    print("=" * 70)
