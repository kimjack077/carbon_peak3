import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def plot_carbon_peak(results_dict, output_path=None):
    """绘制碳达峰预测图
    
    Args:
        results_dict: 包含不同情景结果的字典
        output_path: 输出图片路径，如果为None则显示图片
    """
    plt.figure(figsize=(14, 9))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4749']
    
    # 绘制每个情景的碳排放曲线
    for idx, (scenario_name, results) in enumerate(results_dict.items()):
        color = colors[idx % len(colors)]
        plt.plot(results['year'], results['CO2'], 
                label=scenario_name, linewidth=2.5, color=color, marker='o', markersize=4)
    
    # 找出每个情景的峰值年份
    for idx, (scenario_name, results) in enumerate(results_dict.items()):
        # 优先使用attrs中的peak_year
        if hasattr(results, 'attrs') and 'peak_year' in results.attrs and results.attrs['peak_year']:
            peak_year = results.attrs['peak_year']
            peak_mask = results['year'] == peak_year
            if peak_mask.any():
                peak_value = results.loc[peak_mask, 'CO2'].iloc[0]
            else:
                continue
        else:
            peak_idx = results['CO2'].idxmax()
            peak_year = results.loc[peak_idx, 'year']
            peak_value = results.loc[peak_idx, 'CO2']
        
        color = colors[idx % len(colors)]
        plt.scatter(peak_year, peak_value, s=150, zorder=5, color=color, edgecolors='black', linewidths=2)
        plt.annotate(f'{scenario_name}\n峰值: {int(peak_year)}年\n{peak_value:.2f}',
                     xy=(peak_year, peak_value), xytext=(15, 15),
                     textcoords='offset points', ha='left', va='bottom',
                     bbox=dict(boxstyle='round,pad=0.6', fc=color, alpha=0.3, edgecolor='black'),
                     arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='black'),
                     fontsize=10, weight='bold')
    
    plt.title('碳排放达峰预测对比', fontsize=18, weight='bold', pad=20)
    plt.xlabel('年份', fontsize=14, weight='bold')
    plt.ylabel('碳排放量 (tCO₂)', fontsize=14, weight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=12, loc='best', framealpha=0.9)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_energy_mix(results, output_path=None):
    """绘制能源结构变化图
    
    Args:
        results: 包含能源结构的DataFrame
        output_path: 输出图片路径，如果为None则显示图片
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    years = results['year']
    
    # 能源结构数据
    coal_share = results['mix_coal'] * 100
    oil_share = results['mix_oil'] * 100
    gas_share = results['mix_gas'] * 100
    ren_share = results['mix_ren'] * 100
    power_share = results['power_share'] * 100
    
    # 绘制直燃能源结构
    ax1.plot(years, coal_share, 'o-', label='煤炭占比', linewidth=2.5, markersize=6, color='#4A4A4A')
    ax1.plot(years, oil_share, 's-', label='石油占比', linewidth=2.5, markersize=6, color='#D4A574')
    ax1.plot(years, gas_share, '^-', label='天然气占比', linewidth=2.5, markersize=6, color='#87CEEB')
    ax1.plot(years, ren_share, 'd-', label='可再生能源占比', linewidth=2.5, markersize=6, color='#6A994E')
    
    ax1.set_title('直燃能源结构变化趋势', fontsize=16, weight='bold', pad=15)
    ax1.set_xlabel('年份', fontsize=12, weight='bold')
    ax1.set_ylabel('占比 (%)', fontsize=12, weight='bold')
    ax1.legend(fontsize=11, loc='best')
    ax1.grid(True, linestyle='--', alpha=0.3)
    
    # 绘制电力占比变化
    ax2.plot(years, power_share, 'o-', label='电力占比', linewidth=3, markersize=7, color='#2E86AB')
    ax2.fill_between(years, 0, power_share, alpha=0.3, color='#2E86AB')
    
    ax2.set_title('电力占比变化趋势', fontsize=16, weight='bold', pad=15)
    ax2.set_xlabel('年份', fontsize=12, weight='bold')
    ax2.set_ylabel('电力占比 (%)', fontsize=12, weight='bold')
    ax2.legend(fontsize=11, loc='best')
    ax2.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
