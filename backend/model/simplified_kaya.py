"""简化的Kaya模型 - 基于Kaya恒等式"""
import numpy as np
import pandas as pd


def run_kaya_model(base_data, params, horizon_year):
    """
    运行简化的Kaya模型
    
    Kaya恒等式: CO2 = GDP × (Energy/GDP) × (CO2/Energy)
    其中:
    - GDP: 生产总值
    - Energy/GDP: 能源强度
    - CO2/Energy: 碳强度（碳排放系数）
    
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
    
    # 计算基准年碳排放系数，校准为使 t=0 与历史值一致。
    # 原公式若直接使用 base_co2/base_energy，并再乘以 (1 - renewable_ratio_t)，
    # 会使 t=0 年的排放低于历史值。我们改为：
    # base_carbon_coefficient = base_co2 / (base_energy * (1 - base_renewable))
    denom = base_energy * max(1e-9, (1.0 - base_renewable))
    base_carbon_coefficient = (base_co2 / denom) if base_energy > 0 else 0
    
    # 计算年数
    years = horizon_year - base_year
    
    # 存储结果
    results = []
    
    for t in range(years + 1):
        year = base_year + t
        
        # 1. GDP增长
        gdp_t = base_gdp * (1 + gdp_growth) ** t
        
        # 2. 能源强度下降（能源效率改善）
        energy_intensity_t = base_energy_intensity * (1 - efficiency_improvement) ** t
        
        # 3. 能源消费 = GDP × 能源强度
        energy_t = gdp_t * energy_intensity_t
        
        # 4. 可再生能源占比提升
        renewable_ratio_t = min(base_renewable + renewable_increase * t, 1.0)
        
        # 5. 可再生能源和非可再生能源
        renewable_energy_t = energy_t * renewable_ratio_t
        nonrenewable_energy_t = energy_t * (1 - renewable_ratio_t)
        
        # 6. 碳排放系数随可再生能源占比变化
        # 碳排放系数 = 基准碳排放系数 × (1 - 可再生能源占比)
        carbon_coefficient_t = base_carbon_coefficient * (1 - renewable_ratio_t)
        
        # 7. 根据Kaya恒等式计算碳排放
        # CO2 = GDP × (Energy/GDP) × (CO2/Energy)
        co2_t = gdp_t * energy_intensity_t * carbon_coefficient_t
        
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
