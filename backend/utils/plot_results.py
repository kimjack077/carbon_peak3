import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def plot_carbon_peak(results_dict, output_path=None, historical_data=None):
    """绘制碳达峰预测图
    
    Args:
        results_dict: 包含不同情景结果的字典
        output_path: 输出图片路径，如果为None则显示图片
        historical_data: 历史数据字典
    """
    plt.figure(figsize=(14, 9))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4749']
    
    # 绘制历史数据（如果有）
    if historical_data:
        plt.plot(historical_data['years'], historical_data['co2'], 
                label='历史数据', linewidth=2.5, color='#333333', 
                marker='s', markersize=5, linestyle='--', alpha=0.7)
    
    # 绘制每个情景的碳排放曲线
    for idx, (scenario_name, results) in enumerate(results_dict.items()):
        color = colors[idx % len(colors)]
        plt.plot(results['year'], results['co2_emission'], 
                label=scenario_name, linewidth=2.5, color=color, marker='o', markersize=4)
    
    # 找出每个情景的峰值年份
    for idx, (scenario_name, results) in enumerate(results_dict.items()):
        # 优先使用attrs中的peak_year
        if hasattr(results, 'attrs') and 'peak_year' in results.attrs and results.attrs['peak_year']:
            peak_year = results.attrs['peak_year']
            peak_mask = results['year'] == peak_year
            if peak_mask.any():
                peak_value = results.loc[peak_mask, 'co2_emission'].iloc[0]
            else:
                continue
        else:
            peak_idx = results['co2_emission'].idxmax()
            peak_year = results.loc[peak_idx, 'year']
            peak_value = results.loc[peak_idx, 'co2_emission']
        
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
    plt.ylabel('碳排放量 (tCO2)', fontsize=14, weight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=12, loc='best', framealpha=0.9)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_gdp(results_dict, output_path=None, historical_data=None):
    """绘制工业生产总值图
    
    Args:
        results_dict: 包含不同情景结果的字典
        output_path: 输出图片路径，如果为None则显示图片
        historical_data: 历史数据字典
    """
    plt.figure(figsize=(14, 9))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4749']
    
    # 绘制历史数据（如果有）
    if historical_data:
        plt.plot(historical_data['years'], historical_data['gdp'], 
                label='历史数据', linewidth=2.5, color='#333333', 
                marker='s', markersize=5, linestyle='--', alpha=0.7)
    
    # 绘制每个情景的GDP曲线
    for idx, (scenario_name, results) in enumerate(results_dict.items()):
        color = colors[idx % len(colors)]
        plt.plot(results['year'], results['gdp'], 
                label=scenario_name, linewidth=2.5, color=color, marker='o', markersize=4)
    
    plt.title('工业生产总值预测', fontsize=18, weight='bold', pad=20)
    plt.xlabel('年份', fontsize=14, weight='bold')
    plt.ylabel('工业总产值 (万元)', fontsize=14, weight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=12, loc='best', framealpha=0.9)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

def plot_energy_consumption(results_dict, output_path=None, historical_data=None):
    """绘制综合能耗图
    
    Args:
        results_dict: 包含不同情景结果的字典
        output_path: 输出图片路径，如果为None则显示图片
        historical_data: 历史数据字典
    """
    plt.figure(figsize=(14, 9))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4749']
    
    # 绘制历史数据（如果有）
    if historical_data:
        plt.plot(historical_data['years'], historical_data['energy'], 
                label='历史数据', linewidth=2.5, color='#333333', 
                marker='s', markersize=5, linestyle='--', alpha=0.7)
    
    # 绘制每个情景的能源消费曲线
    for idx, (scenario_name, results) in enumerate(results_dict.items()):
        color = colors[idx % len(colors)]
        plt.plot(results['year'], results['energy_consumption'], 
                label=scenario_name, linewidth=2.5, color=color, marker='o', markersize=4)
    
    plt.title('综合能源消费量预测', fontsize=18, weight='bold', pad=20)
    plt.xlabel('年份', fontsize=14, weight='bold')
    plt.ylabel('综合能源消费量 (万吨标准煤)', fontsize=14, weight='bold')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.legend(fontsize=12, loc='best', framealpha=0.9)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()
