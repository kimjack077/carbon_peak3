"""简化的LEAP模型 - 只考虑GDP、能源效率、可再生能源占比"""
import numpy as np
import pandas as pd


def run_leap_model(base_data, params, horizon_year):
    """
    运行简化的LEAP模型
    
    参数:
        base_data: 基准年数据字典
            - year: 基准年
            - energy: 能源消费 (万吨标煤)
            - gdp: GDP (万元)
            - co2: 碳排放 (万吨CO2)
            - renewable_ratio: 可再生能源占比
            - energy_intensity: 能源强度
            - carbon_intensity: 碳强度
        params: 情景参数
            - gdp_growth_rate: GDP年增长率
            - efficiency_improvement_rate: 能源效率改善率（能源强度下降率）
            - renewable_increase_rate: 可再生能源占比年提升率
        horizon_year: 预测终止年份
    
    返回:
        DataFrame包含年份、GDP、能源消费、碳排放、可再生能源占比、非可再生能源
    """
    base_year = base_data['year']
    base_gdp = base_data['gdp']
    base_energy = base_data['energy']
    base_co2 = base_data['co2']
    base_renewable = base_data['renewable_ratio']
    base_energy_intensity = base_data['energy_intensity']
    
    # 提取参数
    gdp_growth = params.get('gdp_growth_rate', 0.05)
    efficiency_improvement = params.get('efficiency_improvement_rate', 0.03)
    renewable_increase = params.get('renewable_increase_rate', 0.0)  # 默认不增长
    
    # 计算年数
    years = horizon_year - base_year
    
    # 存储结果
    results = []
    
    for t in range(years + 1):
        year = base_year + t
        
        # GDP增长
        gdp_t = base_gdp * (1 + gdp_growth) ** t
        
        # 能源强度下降（能源效率改善）
        energy_intensity_t = base_energy_intensity * (1 - efficiency_improvement) ** t
        
        # 能源消费 = GDP × 能源强度
        energy_t = gdp_t * energy_intensity_t
        
        # 可再生能源占比提升（线性增长，上限100%）
        renewable_ratio_t = min(base_renewable + renewable_increase * t, 1.0)
        
        # 可再生能源消费（零排放）
        renewable_energy_t = energy_t * renewable_ratio_t
        
        # 非可再生能源消费
        nonrenewable_energy_t = energy_t * (1 - renewable_ratio_t)
        
        # 计算碳排放 = 非可再生能源 × 碳排放系数
        # 碳排放系数 = 基准年碳排放 / 基准年能源消费
        # 调整碳排放系数以保证基年一致性：
        # 令 t=0 时有 nonrenewable_energy_0 * carbon_factor == base_co2
        # 即 carbon_factor = base_co2 / (base_energy * (1 - base_renewable))
        denom = base_energy * max(1e-9, (1.0 - base_renewable))
        carbon_factor = (base_co2 / denom) if base_energy > 0 else 0
        co2_t = nonrenewable_energy_t * carbon_factor
        
        results.append({
            'year': year,
            'gdp': gdp_t,
            'energy_consumption': energy_t,
            'co2_emission': co2_t,
            'renewable_ratio': renewable_ratio_t,
            'renewable_energy': renewable_energy_t,
            'nonrenewable_energy': nonrenewable_energy_t,
        })
    
    return pd.DataFrame(results)
