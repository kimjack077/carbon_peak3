import pandas as pd
import numpy as np
from .leap_model import forecast_leap, validate_base_data as validate_leap
from .kaya_model import forecast_kaya, decompose_kaya_factors


def run_scenario(base, scenario_params, horizon_year):
    """运行LEAP或Kaya模型的预测
    
    Args:
        base: 基础数据字典 {years, gdp, co2, mix{coal,oil,gas,ren}, power_share, population}
        scenario_params: 情景参数字典 {model_type, gdp_growth_rate, ...}
        horizon_year: 预测截止年份
    
    Returns:
        results_df: 包含预测结果的DataFrame
    """
    # 获取模型类型，默认为LEAP
    model_type = scenario_params.get('model_type', 'leap').lower()
    
    # 验证基础数据
    validate_leap(base)
    
    if model_type == 'leap':
        results, peak_year = forecast_leap(base, scenario_params, horizon_year)
    elif model_type == 'kaya':
        # 获取基期人口
        P0 = base.get('population', [1.0])[-1] if 'population' in base else 1.0
        results, peak_year = forecast_kaya(base, scenario_params, horizon_year, P0)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 统一字段名，确保前后端一致
    # 重命名大写字段为小写
    rename_map = {
        'GDP': 'gdp',
        'Population': 'population',
        'Energy': 'energy_consumption',
        'CO2': 'total_emission',
        'CI': 'carbon_intensity'
    }
    results_df = results_df.rename(columns=rename_map)
    
    # 添加缺失字段
    # 如果LEAP模型没有人口数据，使用基期人口
    if 'population' not in results_df.columns:
        P0 = base.get('population', [1.0])[-1] if 'population' in base else 1.0
        pop_growth = scenario_params.get('population_growth_rate', -0.0099)
        years_count = len(results_df)
        results_df['population'] = [P0 * (1 + pop_growth) ** i for i in range(1, years_count + 1)]
    
    # 计算人均碳排放
    results_df['emission_per_capita'] = results_df['total_emission'] / results_df['population']
    
    # 计算单位GDP碳排放
    results_df['emission_per_gdp'] = results_df['total_emission'] / results_df['gdp']
    
    # 添加达峰年信息
    results_df.attrs['peak_year'] = peak_year
    results_df.attrs['model_type'] = model_type
    
    return results_df
