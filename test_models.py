#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试LEAP和Kaya模型
演示如何使用新模型进行碳达峰预测
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from model.leap_model import forecast_leap
from model.kaya_model import forecast_kaya
import pandas as pd


def test_leap_model():
    """测试LEAP模型"""
    print("\n" + "="*60)
    print("测试 LEAP 模型")
    print("="*60)
    
    # 准备基础数据（3年历史数据）
    base = {
        "years": [2022, 2023, 2024],
        "gdp": [114.37, 126.06, 134.52],
        "co2": [11200.5, 11450.8, 11580.3],
        "mix": {
            "coal": [0.56, 0.54, 0.52],
            "oil": [0.18, 0.18, 0.18],
            "gas": [0.09, 0.10, 0.11],
            "ren": [0.17, 0.18, 0.19]
        },
        "power_share": [0.27, 0.29, 0.31]
    }
    
    # 情景参数
    scenario = {
        "gdp_growth_rate": 0.05,
        "efficiency_improvement_rate": 0.03,
        "coal_reduction_rate": 0.01,
        "power_share_increase": 0.02,
        "ren_share_increase": 0.015,
        "grid_cf_decline": 0.05,
        "EF_grid": 0.65
    }
    
    # 运行预测
    results, peak_year = forecast_leap(base, scenario, horizon_year=2050)
    
    # 转换为DataFrame
    df = pd.DataFrame(results)
    
    # 显示关键结果
    print("\n关键预测结果：")
    print(f"- 预测年数: {len(results)}")
    print(f"- 预测年份范围: {results[0]['year']} - {results[-1]['year']}")
    print(f"- 达峰年份: {peak_year if peak_year else '未达峰'}")
    
    if peak_year:
        peak_data = df[df['year'] == peak_year].iloc[0]
        print(f"- 峰值碳排放: {peak_data['CO2']:.2f} 万吨CO₂")
        print(f"- 峰值年GDP: {peak_data['GDP']:.2f} 万亿元")
        print(f"- 峰值年碳强度: {peak_data['CI']:.4f}")
    
    # 显示前5年预测
    print("\n前5年预测详情：")
    print(df[['year', 'GDP', 'CO2', 'CI', 'mix_coal', 'mix_ren', 'power_share']].head())
    
    # 显示最后5年预测
    print("\n最后5年预测详情：")
    print(df[['year', 'GDP', 'CO2', 'CI', 'mix_coal', 'mix_ren', 'power_share']].tail())
    
    return df, peak_year


def test_kaya_model():
    """测试Kaya模型"""
    print("\n" + "="*60)
    print("测试 Kaya 模型")
    print("="*60)
    
    # 准备基础数据
    base = {
        "years": [2022, 2023, 2024],
        "gdp": [114.37, 126.06, 134.52],
        "co2": [11200.5, 11450.8, 11580.3],
        "mix": {
            "coal": [0.56, 0.54, 0.52],
            "oil": [0.18, 0.18, 0.18],
            "gas": [0.09, 0.10, 0.11],
            "ren": [0.17, 0.18, 0.19]
        },
        "power_share": [0.27, 0.29, 0.31],
        "population": [141175, 140967, 140821]
    }
    
    # 情景参数
    scenario = {
        "gdp_growth_rate": 0.05,
        "population_growth_rate": -0.005,
        "efficiency_improvement_rate": 0.03,
        "coal_reduction_rate": 0.01,
        "power_share_increase": 0.02,
        "ren_share_increase": 0.015,
        "grid_cf_decline": 0.05,
        "EF_grid": 0.65
    }
    
    # 运行预测
    P0 = base["population"][-1]
    results, peak_year = forecast_kaya(base, scenario, horizon_year=2050, P0=P0)
    
    # 转换为DataFrame
    df = pd.DataFrame(results)
    
    # 显示关键结果
    print("\n关键预测结果：")
    print(f"- 预测年数: {len(results)}")
    print(f"- 预测年份范围: {results[0]['year']} - {results[-1]['year']}")
    print(f"- 达峰年份: {peak_year if peak_year else '未达峰'}")
    
    if peak_year:
        peak_data = df[df['year'] == peak_year].iloc[0]
        print(f"- 峰值碳排放: {peak_data['CO2']:.2f} 万吨CO₂")
        print(f"- 峰值年GDP: {peak_data['GDP']:.2f} 万亿元")
        print(f"- 峰值年人口: {peak_data['Population']:.2f} 万人")
        print(f"- 峰值年人均GDP: {peak_data['GDP_per_capita']:.4f} 万元/人")
    
    # 显示前5年预测
    print("\n前5年预测详情：")
    print(df[['year', 'Population', 'GDP', 'CO2', 'EI', 'CF', 'CI']].head())
    
    # 显示最后5年预测
    print("\n最后5年预测详情：")
    print(df[['year', 'Population', 'GDP', 'CO2', 'EI', 'CF', 'CI']].tail())
    
    return df, peak_year


def compare_models():
    """对比两种模型的预测结果"""
    print("\n" + "="*60)
    print("LEAP vs Kaya 模型对比")
    print("="*60)
    
    # 运行两个模型
    leap_df, leap_peak = test_leap_model()
    kaya_df, kaya_peak = test_kaya_model()
    
    # 对比结果
    print("\n" + "="*60)
    print("模型对比总结")
    print("="*60)
    
    print(f"\nLEAP模型:")
    print(f"  达峰年: {leap_peak if leap_peak else '未达峰'}")
    if leap_peak:
        leap_peak_value = leap_df[leap_df['year'] == leap_peak]['CO2'].iloc[0]
        print(f"  峰值: {leap_peak_value:.2f} 万吨CO₂")
    
    print(f"\nKaya模型:")
    print(f"  达峰年: {kaya_peak if kaya_peak else '未达峰'}")
    if kaya_peak:
        kaya_peak_value = kaya_df[kaya_df['year'] == kaya_peak]['CO2'].iloc[0]
        print(f"  峰值: {kaya_peak_value:.2f} 万吨CO₂")
    
    # 计算差异
    if leap_peak and kaya_peak:
        year_diff = abs(leap_peak - kaya_peak)
        value_diff = abs(leap_peak_value - kaya_peak_value)
        value_diff_pct = (value_diff / leap_peak_value) * 100
        
        print(f"\n差异分析:")
        print(f"  达峰年差异: {year_diff} 年")
        print(f"  峰值差异: {value_diff:.2f} 万吨CO₂ ({value_diff_pct:.2f}%)")
    
    # 2030年和2040年的排放对比
    print("\n特定年份碳排放对比:")
    for year in [2030, 2040, 2050]:
        if year <= leap_df['year'].max() and year <= kaya_df['year'].max():
            leap_co2 = leap_df[leap_df['year'] == year]['CO2'].iloc[0]
            kaya_co2 = kaya_df[kaya_df['year'] == year]['CO2'].iloc[0]
            diff = abs(leap_co2 - kaya_co2)
            diff_pct = (diff / leap_co2) * 100
            print(f"  {year}年: LEAP={leap_co2:.2f}, Kaya={kaya_co2:.2f}, 差异={diff:.2f} ({diff_pct:.2f}%)")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("碳达峰预测系统 - 模型测试")
    print("="*60)
    
    try:
        # 对比两种模型
        compare_models()
        
        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)
        print("\n提示：")
        print("1. 两个模型的预测结果会略有差异，这是正常现象")
        print("2. LEAP侧重能源结构分析，Kaya侧重驱动因素分解")
        print("3. 建议同时使用两个模型，交叉验证预测结果")
        print("4. 可以调整scenario参数来测试不同情景")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
