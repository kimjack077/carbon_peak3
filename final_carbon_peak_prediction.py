"""
最终版碳达峰预测 - 基于真实三年数据
展示不同政策力度下的达峰路径
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from model.data_processor import DataProcessor
from model.kaya_model_fixed import forecast_kaya_fixed, find_peak_year

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def create_peak_scenarios():
    """
    创建展示不同达峰路径的情景
    
    达峰的关键：GDP增长率 ≈ 能效提升率 + 碳因子下降率
    - 初期：减排力度不够，排放上升
    - 中期：减排加强，接近达峰
    - 后期：持续下降
    """
    
    # 情景1：2028年达峰（早期达峰）
    early_peak = {
        "name": "2028年达峰情景",
        "gdp_growth_rate": 0.065,             # GDP年增长6.5%
        "efficiency_improvement_rate": 0.035,  # 能效提升3.5%/年
        "fossil_reduction_rate": 0.025,        # 化石能源占比年降2.5%
        "ren_share_increase": 0.025,
    }
    
    # 情景2：2030年达峰（标准达峰）
    standard_peak = {
        "name": "2030年达峰情景",
        "gdp_growth_rate": 0.07,
        "efficiency_improvement_rate": 0.030,
        "fossil_reduction_rate": 0.020,        # 化石能源占比年降2.0%
        "ren_share_increase": 0.020,
    }
    
    # 情景3：2035年达峰（晚期达峰）
    late_peak = {
        "name": "2035年达峰情景",
        "gdp_growth_rate": 0.075,
        "efficiency_improvement_rate": 0.028,
        "fossil_reduction_rate": 0.018,        # 化石能源占比年降1.8%
        "ren_share_increase": 0.018,
    }
    
    # 情景4：持续下降（无峰值）
    continuous_decline = {
        "name": "持续下降情景",
        "gdp_growth_rate": 0.06,
        "efficiency_improvement_rate": 0.04,
        "fossil_reduction_rate": 0.030,        # 化石能源占比年降3.0%
        "ren_share_increase": 0.030,
    }
    
    # 情景5：持续增长（无峰值）
    continuous_growth = {
        "name": "持续增长情景",
        "gdp_growth_rate": 0.08,
        "efficiency_improvement_rate": 0.025,
        "fossil_reduction_rate": 0.008,        # 化石能源占比年降0.8%
        "ren_share_increase": 0.008,
    }
    
    return {
        "early_peak": early_peak,
        "standard_peak": standard_peak,
        "late_peak": late_peak,
        "continuous_decline": continuous_decline,
        "continuous_growth": continuous_growth
    }


def run_final_prediction():
    """运行最终预测"""
    print("=" * 80)
    print("最终版碳达峰预测 - 基于真实三年数据(2022-2024)")
    print("=" * 80)
    
    # 加载数据
    data_path = 'D:\\software\\carbon_peak3\\backend\\data\\real_data_2022_2024.csv'
    processor = DataProcessor(data_path)
    df = processor.load_data()
    base = processor.prepare_base_dict_for_models()
    
    # 添加能源数据
    real_energy = pd.read_csv(data_path)
    if 'total_energy' in real_energy.columns:
        base['total_energy'] = real_energy['total_energy'].tolist()
    else:
        base['total_energy'] = [980.15, 1098.94, 1081.95]
    
    print(f"\n基年(2024)数据：")
    print(f"  GDP: {base['gdp'][-1]:.2f} 亿元")
    print(f"  CO2排放: {base['co2'][-1]:.2f} 万吨")
    print(f"  能源消费: {base['total_energy'][-1]:.2f} 万吨标煤")
    print(f"  碳强度: {base['co2'][-1]/base['gdp'][-1]:.4f} 万吨CO2/亿元")
    
    # 创建情景
    scenarios = create_peak_scenarios()
    
    # 运行预测
    horizon_year = 2060
    results = {}
    peaks = {}
    
    print("\n" + "=" * 80)
    print("运行预测...")
    print("=" * 80)
    
    for key, scenario in scenarios.items():
        print(f"\n{scenario['name']}...")
        result, peak = forecast_kaya_fixed(base, scenario, horizon_year, P0=1.0)
        results[key] = result
        peaks[key] = peak
        
        if peak:
            peak_data = [r for r in result if r['year'] == peak][0]
            print(f"  ✓ {peak}年达峰，峰值：{peak_data['CO2']:.2f}万吨")
        else:
            last_co2 = result[-1]['CO2']
            first_co2 = result[0]['CO2']
            trend = "持续下降" if last_co2 < first_co2 * 0.9 else "持续增长"
            print(f"  ○ 未出现峰值（{trend}），2060年：{last_co2:.2f}万吨")
    
    # 详细分析
    print("\n" + "=" * 80)
    print("详细分析")
    print("=" * 80)
    
    base_co2 = base['co2'][-1]
    
    for key, scenario in scenarios.items():
        print(f"\n【{scenario['name']}】")
        print("-" * 80)
        
        result = results[key]
        peak = peaks[key]
        
        # 理论分析
        gdp_g = scenario['gdp_growth_rate']
        ei_d = scenario['efficiency_improvement_rate']
        fossil_base = base['mix']['coal'][-1] + base['mix']['oil'][-1] + base['mix']['gas'][-1]
        cf_d = scenario['fossil_reduction_rate'] * fossil_base  # CF下降率估算
        co2_g_theory = gdp_g - ei_d - cf_d
        
        print(f"\n理论分析：")
        print(f"  GDP年增长: {gdp_g*100:.1f}%")
        print(f"  能效年提升: {ei_d*100:.1f}%")
        print(f"  碳因子估算下降: {cf_d*100:.1f}%")
        print(f"  CO2理论年变化: {co2_g_theory*100:+.1f}%")
        
        # 关键年份数据
        print(f"\n关键年份预测：")
        print(f"{'年份':<8} {'CO2(万吨)':<12} {'变化%':<10} {'化石占比%':<12} {'能源(万吨标煤)':<15}")
        print("-" * 80)
        
        for year in [2025, 2028, 2030, 2035, 2040, 2050, 2060]:
            r = [x for x in result if x['year'] == year]
            if r:
                r = r[0]
                change = (r['CO2'] / base_co2 - 1) * 100
                marker = "  " if not peak or r['year'] != peak else "▲"
                print(f"{r['year']:<8} {r['CO2']:<12.2f} {change:+9.1f} {r['fossil_share']*100:<12.1f} {r['Energy']:<15.2f} {marker}")
        
        if peak:
            peak_data = [r for r in result if r['year'] == peak][0]
            print(f"\n达峰特征：")
            print(f"  达峰年份: {peak}年")
            print(f"  峰值排放: {peak_data['CO2']:.2f} 万吨")
            print(f"  相比2024年: {(peak_data['CO2']/base_co2-1)*100:+.1f}%")
            
            # 2060年情况
            data_2060 = [r for r in result if r['year'] == 2060][0]
            print(f"  2060年排放: {data_2060['CO2']:.2f} 万吨")
            if peak_data['CO2'] > 0:
                print(f"  相比峰值: {(data_2060['CO2']/peak_data['CO2']-1)*100:+.1f}%")
    
    # 绘制对比图
    plot_peak_comparison(results, peaks, base, scenarios)
    
    # 政策建议
    print("\n" + "=" * 80)
    print("政策建议")
    print("=" * 80)
    
    print("\n要实现碳达峰，关键是让减排速度超过经济增长速度：")
    print("  ∆CO2% = GDP增长% - 能效提升% - 碳因子下降%")
    print("\n建议的减排组合：")
    print("  1. GDP增长7% + 能效提升3% + 化石降2% → 约2030年达峰")
    print("  2. GDP增长6.5% + 能效提升3.5% + 化石降2.5% → 约2028年达峰")
    print("  3. GDP增长6% + 能效提升4% + 化石降3% → 持续下降，无峰值")
    
    return results, peaks


def plot_peak_comparison(results, peaks, base, scenarios):
    """绘制达峰情景对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('碳达峰情景对比分析 (2024-2060)', fontsize=16, fontweight='bold')
    
    colors = {
        'early_peak': '#2E86AB',
        'standard_peak': '#A23B72',
        'late_peak': '#F18F01',
        'continuous_decline': '#06A77D',
        'continuous_growth': '#C73E1D'
    }
    
    # (1) CO2排放趋势
    ax1 = axes[0, 0]
    ax1.plot(base['years'], base['co2'], 'ko-', linewidth=3, markersize=8, label='历史数据', zorder=10)
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        co2 = [r['CO2'] for r in result]
        label = scenarios[key]['name']
        ax1.plot(years, co2, color=colors[key], linewidth=2.5, label=label, alpha=0.85)
        
        # 标记达峰点
        if peaks[key]:
            peak_data = [r for r in result if r['year'] == peaks[key]][0]
            ax1.plot(peaks[key], peak_data['CO2'], 'D', color=colors[key], 
                    markersize=14, markeredgewidth=2.5, markeredgecolor='black', zorder=5)
            ax1.annotate(f'{peaks[key]}年', 
                        xy=(peaks[key], peak_data['CO2']),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[key], alpha=0.7))
    
    ax1.set_xlabel('年份', fontsize=12, fontweight='bold')
    ax1.set_ylabel('CO2排放量（万吨）', fontsize=12, fontweight='bold')
    ax1.set_title('CO2排放趋势对比', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=9, loc='best', framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.axvline(x=2024, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    
    # (2) 化石能源占比变化
    ax2 = axes[0, 1]
    fossil_hist = [(base['mix']['coal'][i] + base['mix']['oil'][i] + base['mix']['gas'][i])*100 
                   for i in range(len(base['years']))]
    ax2.plot(base['years'], fossil_hist, 'ko-', linewidth=3, markersize=8, label='历史数据', zorder=10)
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        fossil = [r['fossil_share'] * 100 for r in result]
        label = scenarios[key]['name']
        ax2.plot(years, fossil, color=colors[key], linewidth=2.5, label=label, alpha=0.85)
    
    ax2.set_xlabel('年份', fontsize=12, fontweight='bold')
    ax2.set_ylabel('化石能源占比（%）', fontsize=12, fontweight='bold')
    ax2.set_title('化石能源占比变化', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=9, loc='best', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.axvline(x=2024, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    
    # (3) 碳强度变化
    ax3 = axes[1, 0]
    ci_hist = [base['co2'][i] / base['gdp'][i] for i in range(len(base['years']))]
    ax3.plot(base['years'], ci_hist, 'ko-', linewidth=3, markersize=8, label='历史数据', zorder=10)
    
    for key, result in results.items():
        years = [r['year'] for r in result]
        ci = [r['CI'] for r in result]
        label = scenarios[key]['name']
        ax3.plot(years, ci, color=colors[key], linewidth=2.5, label=label, alpha=0.85)
    
    ax3.set_xlabel('年份', fontsize=12, fontweight='bold')
    ax3.set_ylabel('碳强度（万吨CO2/亿元）', fontsize=12, fontweight='bold')
    ax3.set_title('碳强度变化趋势', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=9, loc='best', framealpha=0.9)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.axvline(x=2024, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    
    # (4) 达峰年份和峰值对比
    ax4 = axes[1, 1]
    peak_years = []
    peak_values = []
    peak_labels = []
    peak_colors = []
    
    for key, peak in peaks.items():
        if peak:
            peak_data = [r for r in results[key] if r['year'] == peak][0]
            peak_years.append(peak)
            peak_values.append(peak_data['CO2'])
            peak_labels.append(scenarios[key]['name'].replace('情景', ''))
            peak_colors.append(colors[key])
    
    if peak_years:
        bars = ax4.bar(range(len(peak_years)), peak_values, color=peak_colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax4.set_xticks(range(len(peak_years)))
        ax4.set_xticklabels(peak_labels, rotation=15, ha='right')
        ax4.set_ylabel('峰值排放（万吨CO2）', fontsize=12, fontweight='bold')
        ax4.set_title('不同情景的达峰年份和峰值', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # 在柱子上标注达峰年份
        for i, (year, value) in enumerate(zip(peak_years, peak_values)):
            ax4.text(i, value, f'{year}年\n{value:.0f}万吨', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 添加2024年基准线
        ax4.axhline(y=base['co2'][-1], color='red', linestyle='--', linewidth=2, 
                   label=f'2024年基准({base["co2"][-1]:.0f}万吨)')
        ax4.legend(fontsize=10, loc='best')
    else:
        ax4.text(0.5, 0.5, '没有达峰情景', ha='center', va='center', 
                fontsize=16, transform=ax4.transAxes)
    
    plt.tight_layout()
    
    # 保存图表
    output_path = 'D:\\software\\carbon_peak3\\final_carbon_peak_results.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n\n图表已保存至: {output_path}")


if __name__ == '__main__':
    results, peaks = run_final_prediction()
    print("\n" + "=" * 80)
    print("预测完成！")
    print("=" * 80)
