"""
Kaya 扩展模型实现
基于参考文档的方法B
CO2 = P × (GDP/P) × (E/GDP) × (CO2/E)
"""
import pandas as pd
import numpy as np


# 排放因子 (tCO2/单位能耗) - 示意值，可根据实际情况调整
EMISSION_FACTORS = {
    "coal": 2.5,
    "oil": 2.1,
    "gas": 1.6,
    "ren": 0.0
}


def forecast_kaya(base, scenario, horizon_year, P0=1.0):
    """
    Kaya模型预测
    
    Args:
        base: dict 包含 years, gdp, co2, mix{coal, oil, gas, ren}, power_share
        scenario: dict 包含情景参数
        horizon_year: 预测截止年份
        P0: 基期人口或代表性规模量
    
    Returns:
        (out, peak): 预测结果列表和达峰年份
    """
    # 电网排放因子 (tCO2/MWh) - 示意值
    EF_grid = scenario.get('EF_grid', 0.65)
    
    # 基期：用最后一年反演 EI 与 CF 起点
    mix_last = {f: base["mix"][f][-1] for f in ["coal", "oil", "gas", "ren"]}
    
    CI_last = base["co2"][-1] / base["gdp"][-1]
    
    # 计算直燃碳因子
    CF_dir0 = sum(mix_last[f] * EMISSION_FACTORS[f] for f in mix_last)
    
    # 电力对CF的影响取加权：此处用基期电力占比
    p_last = base["power_share"][-1]
    kappa = scenario.get("kappa", 1.0)
    CF_last = (1 - p_last) * CF_dir0 + p_last * (EF_grid * kappa)
    
    # 能源强度 EI = CI / CF
    EI_last = CI_last / max(CF_last, 1e-9)
    
    g_last = base["gdp"][-1]
    y = base["years"][-1]
    P = P0
    
    # 计算历史能源消费和增长率
    energy_hist = []
    if len(base["years"]) >= 2:
        for i in range(len(base["years"])):
            ci = base["co2"][i] / base["gdp"][i]
            mix_i = {f: base["mix"][f][i] for f in ["coal", "oil", "gas", "ren"]}
            p_i = base["power_share"][i]
            cf_dir_i = sum(mix_i[f] * EMISSION_FACTORS[f] for f in mix_i)
            cf_i = (1 - p_i) * cf_dir_i + p_i * (EF_grid * kappa)
            ei_i = ci / max(cf_i, 1e-9)
            energy_hist.append(base["gdp"][i] * ei_i)
        
        energy_growth_rates = []
        for i in range(1, len(energy_hist)):
            rate = (energy_hist[i] / energy_hist[i-1] - 1)
            energy_growth_rates.append(rate)
        
        # 使用最近一年的增长率
        hist_energy_growth = energy_growth_rates[-1] if energy_growth_rates else 0.04
    else:
        hist_energy_growth = 0.04
        energy_hist = [g_last * EI_last]
    
    # 记录基年值
    EI_base = EI_last
    coal_base = mix_last["coal"]
    ren_base = mix_last["ren"]
    p_base = p_last
    
    out = []
    
    # 逐年预测
    year_count = 0  # 预测年份计数器
    while y < horizon_year:
        y += 1
        year_count += 1
        
        # 人口与经济
        P *= (1 + scenario.get("population_growth_rate", 0.0))
        gdp_growth = scenario.get("gdp_growth_rate", 0.05)
        g_last *= (1 + gdp_growth)
        
        # 能源强度：采用平滑过渡方式
        efficiency_rate = scenario.get("efficiency_improvement_rate", 0.02)
        
        transition_years = 10
        if year_count <= transition_years:
            # 过渡期：从历史趋势平滑过渡
            transition_factor = year_count / float(transition_years)
            target_energy_growth = gdp_growth - efficiency_rate
            actual_energy_growth = hist_energy_growth * (1 - transition_factor) + target_energy_growth * transition_factor
            EI_last = EI_last * (1 + actual_energy_growth) / (1 + gdp_growth)
        else:
            # 稳定期：继续按照能效改善率逐年递减
            EI_last = EI_last * (1 - efficiency_rate)
        
        # 电力占比：从基年开始累积增加
        power_increase = scenario.get("power_share_increase", 0.0)
        p_last = min(1.0, max(0.0, p_base + power_increase * year_count))
        
        # 直燃结构更新：从基年开始累积变化
        coal_reduction = scenario.get("coal_reduction_rate", 0.01)
        ren_increase = scenario.get("ren_share_increase", 0.0)
        coal = max(0.0, coal_base - coal_reduction * year_count)
        ren = min(1.0, ren_base + ren_increase * year_count)
        
        remain = max(0.0, 1.0 - coal - ren)
        oil0, gas0 = mix_last["oil"], mix_last["gas"]
        s = max(oil0 + gas0, 1e-9)
        oil = remain * oil0 / s
        gas = remain * gas0 / s
        mix_last = {"coal": coal, "oil": oil, "gas": gas, "ren": ren}
        
        # 电网系数可按情景下降
        if "grid_cf_decline" in scenario:
            EF_grid *= (1 - scenario["grid_cf_decline"])
        
        # 计算综合碳因子CF
        CF_dir = (coal * EMISSION_FACTORS["coal"] + 
                 oil * EMISSION_FACTORS["oil"] + 
                 gas * EMISSION_FACTORS["gas"] + 
                 ren * EMISSION_FACTORS["ren"])
        CF = (1 - p_last) * CF_dir + p_last * (EF_grid * kappa)
        
        # Kaya恒等式: CO2 = GDP × EI × CF
        CI = EI_last * CF
        CO2 = g_last * CI
        
        # 计算总能耗
        E_t = g_last * EI_last
        
        # 人均指标
        gdp_per_capita = g_last / P if P > 0 else 0
        
        out.append({
            "year": y,
            "Population": P,
            "GDP": g_last,
            "GDP_per_capita": gdp_per_capita,
            "EI": EI_last,
            "CF": CF,
            "CF_direct": CF_dir,
            "CI": CI,
            "CO2": CO2,
            "Energy": E_t,
            "power_share": p_last,
            "mix_coal": coal,
            "mix_oil": oil,
            "mix_gas": gas,
            "mix_ren": ren,
            "EF_grid": EF_grid
        })
    
    # 达峰年判定
    peak = find_peak_year(out)
    
    return out, peak


def find_peak_year(results, eps=0.005):
    """
    寻找达峰年份
    
    Args:
        results: 预测结果列表
        eps: 容差（0.5%）
    
    Returns:
        达峰年份，若未达峰返回None
    """
    if len(results) < 3:
        return None
    
    for i in range(1, len(results) - 1):
        if (results[i]["CO2"] >= (1 - eps) * results[i - 1]["CO2"]
            and results[i]["CO2"] > results[i - 1]["CO2"]
            and results[i]["CO2"] >= (1 - eps) * results[i + 1]["CO2"]
            and results[i]["CO2"] > results[i + 1]["CO2"]):
            
            # 检查后续年份不再突破峰值
            peak_value = results[i]["CO2"]
            is_peak = True
            for j in range(i + 1, len(results)):
                if results[j]["CO2"] > peak_value * (1 + eps):
                    is_peak = False
                    break
            
            if is_peak:
                return results[i]["year"]
    
    return None


def decompose_kaya_factors(results):
    """
    Kaya因子分解分析
    
    Args:
        results: 预测结果列表
    
    Returns:
        分解后的DataFrame，包含各因子对排放变化的贡献
    """
    if not results or len(results) < 2:
        return None
    
    decomposition = []
    
    for i in range(1, len(results)):
        prev = results[i - 1]
        curr = results[i]
        
        # 计算各因子的变化贡献
        pop_effect = np.log(curr["Population"] / prev["Population"])
        gdp_per_capita_effect = np.log(curr["GDP_per_capita"] / prev["GDP_per_capita"]) if prev["GDP_per_capita"] > 0 else 0
        ei_effect = np.log(curr["EI"] / prev["EI"]) if prev["EI"] > 0 else 0
        cf_effect = np.log(curr["CF"] / prev["CF"]) if prev["CF"] > 0 else 0
        
        total_change = np.log(curr["CO2"] / prev["CO2"]) if prev["CO2"] > 0 else 0
        
        decomposition.append({
            "year": curr["year"],
            "total_change": total_change,
            "population_effect": pop_effect,
            "gdp_per_capita_effect": gdp_per_capita_effect,
            "energy_intensity_effect": ei_effect,
            "carbon_factor_effect": cf_effect
        })
    
    return pd.DataFrame(decomposition)
