"""
LEAP (活动量 × 能效 × 排放因子) 模型实现
基于参考文档的方法A
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


def forecast_leap(base, scenario, horizon_year):
    """
    LEAP模型预测
    
    Args:
        base: dict 包含 years, gdp, co2, mix{coal, oil, gas, ren}, power_share
        scenario: dict 包含情景参数
        horizon_year: 预测截止年份
    
    Returns:
        (out, peak): 预测结果列表和达峰年份
    """
    # 电网排放因子 (tCO2/MWh) - 示意值
    EF_grid = scenario.get('EF_grid', 0.65)
    
    # 1) 从基期数据获取初始值（用最后一年做起点）
    g_last = base["gdp"][-1]
    CO2_base = base["co2"][-1]
    CI_base = CO2_base / g_last  # 基年碳强度
    
    # 获取最后一年的能源结构数据
    mix_last = {f: base["mix"][f][-1] for f in ["coal", "oil", "gas", "ren"]}
    p_last = base["power_share"][-1]
    
    # 从碳强度和能源结构反推能源强度EI
    # CI = EI * CF, 所以 EI = CI / CF
    # 使用平均碳因子0.21（万吨CO2/万吨标煤），基于实际数据反推
    CF = 0.21  # 平均碳因子（万吨CO2/万吨标煤）
    
    EI_last = CI_base / max(CF, 1e-9)
    
    # 计算历史能源消费和增长率（用于确保连续性）
    energy_hist = []
    if len(base["years"]) >= 2:
        # 从历史数据计算能源消费
        for i in range(len(base["years"])):
            ci = base["co2"][i] / base["gdp"][i]  # 碳强度（万吨/万亿元）
            # 使用平均碳因子0.21（万吨CO2/万吨标煤）
            cf = 0.21  # 平均碳因子（万吨CO2/万吨标煤）
            ei = ci / cf  # 能源强度（万吨标煤/万亿元）
            energy_hist.append(base["gdp"][i] * ei)  # 能源消费（万吨标煤）
            mix_i = {f: base["mix"][f][i] for f in ["coal", "oil", "gas", "ren"]}
            p_i = base["power_share"][i]
            cf_dir_i = sum(mix_i[f] * EMISSION_FACTORS[f] for f in mix_i)
            cf_i = (1 - p_i) * cf_dir_i + p_i * (EF_grid * kappa)
            ei_i = ci / max(cf_i, 1e-9)
            energy_hist.append(base["gdp"][i] * ei_i)
        
        # 计算历史能源增长率
        energy_growth_rates = []
        for i in range(1, len(energy_hist)):
            rate = (energy_hist[i] / energy_hist[i-1] - 1)
            energy_growth_rates.append(rate)
        
        # 使用最近一年的增长率作为初始趋势（更准确）
        hist_energy_growth = energy_growth_rates[-1] if energy_growth_rates else 0.04
    else:
        hist_energy_growth = 0.04  # 默认4%增长
        energy_hist = [g_last * EI_last]
    
    # 记录基年值
    EI_base = EI_last
    coal_base = mix_last["coal"]
    ren_base = mix_last["ren"]
    p_base = p_last
    
    y = base["years"][-1]
    out = []
    
    # 2) 逐年预测
    year_count = 0  # 预测年份计数器
    while y < horizon_year:
        y += 1
        year_count += 1
        
        # 经济增长
        gdp_growth = scenario.get("gdp_growth_rate", 0.05)
        g_last *= (1 + gdp_growth)
        
        # 能效改善：采用渐进方式，确保能源消费平滑过渡
        efficiency_rate = scenario.get("efficiency_improvement_rate", 0.02)
        
        # 使用平滑过渡：前10年逐步从历史趋势过渡到目标能效改善
        transition_years = 10
        if year_count <= transition_years:
            # 过渡期：能源增长率从历史趋势逐步降低
            transition_factor = year_count / float(transition_years)
            # 目标能源增长率 = GDP增长率 - 能效改善率
            target_energy_growth = gdp_growth - efficiency_rate
            # 实际能源增长率 = 历史增长率 × (1-过渡因子) + 目标增长率 × 过渡因子
            actual_energy_growth = hist_energy_growth * (1 - transition_factor) + target_energy_growth * transition_factor
            # 更新能源强度：逐年累积变化
            EI_last = EI_last * (1 + actual_energy_growth) / (1 + gdp_growth)
        else:
            # 稳定期：继续按照能效改善率逐年递减
            # 直接在上一年的基础上应用能效改善率
            EI_last = EI_last * (1 - efficiency_rate)
        
        E_t = g_last * EI_last
        
        # 3) 结构更新：采用累积方式
        # 电力占比：从基年开始累积增加
        power_increase = scenario.get("power_share_increase", 0.0)
        p_last = min(1.0, max(0.0, p_base + power_increase * year_count))
        
        # 直燃结构：从基年开始累积变化
        coal_reduction = scenario.get("coal_reduction_rate", 0.01)
        ren_increase = scenario.get("ren_share_increase", 0.0)
        
        coal = max(0.0, coal_base - coal_reduction * year_count)
        ren = min(1.0, ren_base + ren_increase * year_count)
        
        # 油气按比例分配剩余空间
        remain = max(0.0, 1.0 - coal - ren)
        oil0, gas0 = mix_last["oil"], mix_last["gas"]
        s = max(oil0 + gas0, 1e-9)
        oil = remain * oil0 / s
        gas = remain * gas0 / s
        mix_last = {"coal": coal, "oil": oil, "gas": gas, "ren": ren}
        
        # 电网系数可按情景下降
        if "grid_cf_decline" in scenario:
            EF_grid *= (1 - scenario["grid_cf_decline"])
        
        # 4) 排放计算
        E_pow = E_t * p_last
        E_dir = E_t - E_pow
        
        CO2_dir = E_dir * (
            coal * EMISSION_FACTORS["coal"] + 
            oil * EMISSION_FACTORS["oil"] + 
            gas * EMISSION_FACTORS["gas"] + 
            ren * EMISSION_FACTORS["ren"]
        )
        
        # 电力排放（假设E_pow已是MWh口径，若是toe需要转换）
        kappa = scenario.get("kappa", 1.0)  # toe->MWh转换系数，默认1.0
        CO2_pow = (E_pow * kappa) * EF_grid
        
        CO2_t = CO2_dir + CO2_pow
        CI_t = CO2_t / g_last
        
        out.append({
            "year": y,
            "GDP": g_last,
            "Energy": E_t,
            "EI": EI_last,
            "power_share": p_last,
            "mix_coal": coal,
            "mix_oil": oil,
            "mix_gas": gas,
            "mix_ren": ren,
            "CO2": CO2_t,
            "CO2_direct": CO2_dir,
            "CO2_power": CO2_pow,
            "CI": CI_t,
            "EF_grid": EF_grid
        })
    
    # 5) 达峰年判定
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


def validate_base_data(base):
    """
    验证基础数据格式
    
    Args:
        base: 基础数据字典
    
    Raises:
        ValueError: 数据格式错误时抛出
    """
    required_keys = ["years", "gdp", "co2", "mix", "power_share"]
    for key in required_keys:
        if key not in base:
            raise ValueError(f"基础数据缺少必要字段: {key}")
    
    # 检查年份连续性
    years = base["years"]
    if len(years) < 3:
        raise ValueError("至少需要3年的历史数据")
    
    # 检查能源结构份额和为1
    for i in range(len(years)):
        mix_sum = sum(base["mix"][f][i] for f in ["coal", "oil", "gas", "ren"])
        if abs(mix_sum - 1.0) > 0.01:
            raise ValueError(f"第{i+1}年能源结构份额和不为1: {mix_sum}")
    
    # 检查电力占比在0-1之间
    for i, p in enumerate(base["power_share"]):
        if not (0 <= p <= 1):
            raise ValueError(f"第{i+1}年电力占比超出范围[0,1]: {p}")