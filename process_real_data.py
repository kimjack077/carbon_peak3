"""
真实三年数据处理脚本
基于中国能源统计标准和排放因子
"""
import pandas as pd
import numpy as np

# ============ 中国标准能源转换系数 (转换为万吨标煤) ============
# 参考：《中国能源统计年鉴》和国家发改委相关标准
ENERGY_CONVERSION_FACTORS = {
    "coal": 1.0,                    # 原煤已是标煤单位
    "coke": 0.9714 / 10000,         # 焦炭: 0.9714 kgce/kg
    "electricity_thermal": 0.1229 / 10000,  # 电力(火力发电): 0.1229 kgce/kWh
    "electricity_enduse": 0.3456 / 10000,   # 电力(终端): 0.3456 kgce/kWh
    "crude_oil": 1.4286 / 10000,    # 原油: 1.4286 kgce/kg
    "gasoline": 1.4714 / 10000,     # 汽油: 1.4714 kgce/kg
    "kerosene": 1.4714 / 10000,     # 煤油: 1.4714 kgce/kg
    "diesel": 1.4571 / 10000,       # 柴油: 1.4571 kgce/kg
    "fuel_oil": 1.4286 / 10000,     # 燃料油: 1.4286 kgce/kg
    "natural_gas": 1.33 / 10000,    # 天然气: 1.33 kgce/m³
    "heat": 0.03412 / 1000,         # 热力: 0.03412 kgce/MJ (百万千焦转换)
    "other": 1.0 / 10000            # 其他能源(已是吨标煤)
}

# ============ 中国标准CO2排放因子 (tCO2/tce) ============
# 参考：IPCC指南、国家发改委《中国温室气体清单编制指南》
EMISSION_FACTORS = {
    "coal": 2.66,           # 原煤: 2.66-2.76 tCO2/tce (取保守值)
    "coke": 2.86,           # 焦炭: 2.86 tCO2/tce
    "gasoline": 2.93,       # 汽油: 2.93 tCO2/tce
    "kerosene": 2.99,       # 煤油: 2.99 tCO2/tce
    "diesel": 3.06,         # 柴油: 3.06 tCO2/tce
    "fuel_oil": 3.17,       # 燃料油: 3.17 tCO2/tce
    "natural_gas": 2.16,    # 天然气: 2.16 tCO2/tce
    "electricity": 0.5703,  # 电力: 根据中国电网平均排放因子(约0.57 kgCO2/kWh = 0.5703 tCO2/MWh)
    "heat": 0.11,           # 热力: 0.11 tCO2/GJ (按燃煤供热估算)
    "other": 2.4            # 其他能源: 取化石能源平均值
}


def parse_markdown_data(md_file_path):
    """
    从Markdown文件中解析三年数据
    """
    with open(md_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到数据行（跳过表头和分隔符）
    data_lines = []
    for line in lines:
        # 数据行包含20xx年
        if '20' in line and '年' in line and '----' not in line and '年份' not in line:
            data_lines.append(line)
    
    # 解析每行数据
    records = []
    for line in data_lines:
        # 分割并清理空白项
        parts = [p.strip() for p in line.strip().split('|') if p.strip()]
        
        if len(parts) < 17:
            print(f"   警告：数据行字段不足 ({len(parts)} < 17): {line[:50]}...")
            continue
        
        try:
            # 解析年份，确保是整数
            year_str = parts[0].replace('年', '').replace('.0', '').strip()
            year = int(float(year_str))
            
            record = {
                'year': year,
                'total_energy': float(parts[1]),  # 综合能源消费量
                'coal': float(parts[2]),          # 原煤
                'coke': float(parts[3]),          # 焦炭
                'electricity': float(parts[4]),   # 电力
                'crude_oil': float(parts[5]),     # 原油
                'gasoline': float(parts[6]),      # 汽油
                'kerosene': float(parts[7]),      # 煤油
                'diesel': float(parts[8]),        # 柴油
                'fuel_oil': float(parts[9]),      # 燃料油
                'natural_gas': float(parts[10]),  # 天然气
                'heat': float(parts[11]),         # 热力
                'other_energy': float(parts[12]), # 其他能源
                'energy_conversion_output': float(parts[13]),  # 能源加工转换产出量（负向指标）
                'industrial_output_current': float(parts[14]), # 工业总产值(现价)
                'industrial_output_comparable': float(parts[15]), # 工业总产值(可比价)
                'co2_reported': float(parts[16])  # 二氧化碳排放量
            }
            records.append(record)
        except (ValueError, IndexError) as e:
            print(f"   警告：无法解析数据行: {e}")
            continue
    
    df = pd.DataFrame(records)
    # 按年份排序（升序）
    df = df.sort_values('year')
    return df


def calculate_energy_in_sce(row):
    """
    计算各能源的标煤当量 (万吨标煤)
    注意：能源加工转换产出量是负向指标，需要从总和中扣除
    """
    energy_sce = {
        'coal': row['coal'],  # 已是万吨标煤
        'coke': row['coke'] * ENERGY_CONVERSION_FACTORS['coke'],
        'electricity': row['electricity'] * ENERGY_CONVERSION_FACTORS['electricity_enduse'],  # 使用终端电力系数
        'crude_oil': row['crude_oil'] * ENERGY_CONVERSION_FACTORS['crude_oil'],
        'gasoline': row['gasoline'] * ENERGY_CONVERSION_FACTORS['gasoline'],
        'kerosene': row['kerosene'] * ENERGY_CONVERSION_FACTORS['kerosene'],
        'diesel': row['diesel'] * ENERGY_CONVERSION_FACTORS['diesel'],
        'fuel_oil': row['fuel_oil'] * ENERGY_CONVERSION_FACTORS['fuel_oil'],
        'natural_gas': row['natural_gas'] * ENERGY_CONVERSION_FACTORS['natural_gas'],
        'heat': row['heat'] * ENERGY_CONVERSION_FACTORS['heat'],
        'other': row['other_energy'] * ENERGY_CONVERSION_FACTORS['other']
    }
    
    # 总能耗 = 各项能源之和 - 能源加工转换产出量（负向指标）
    total_calculated = sum(energy_sce.values()) - row['energy_conversion_output']
    
    return energy_sce, total_calculated


def calculate_co2_emissions(energy_sce, row):
    """
    计算CO2排放量 (万吨CO2)
    """
    co2_emissions = {
        'coal': energy_sce['coal'] * EMISSION_FACTORS['coal'],
        'coke': energy_sce['coke'] * EMISSION_FACTORS['coke'],
        'gasoline': energy_sce['gasoline'] * EMISSION_FACTORS['gasoline'],
        'kerosene': energy_sce['kerosene'] * EMISSION_FACTORS['kerosene'],
        'diesel': energy_sce['diesel'] * EMISSION_FACTORS['diesel'],
        'fuel_oil': energy_sce['fuel_oil'] * EMISSION_FACTORS['fuel_oil'],
        'natural_gas': energy_sce['natural_gas'] * EMISSION_FACTORS['natural_gas'],
        'electricity': row['electricity'] / 10000 * EMISSION_FACTORS['electricity'],  # 电力单独计算
        'heat': energy_sce['heat'] * EMISSION_FACTORS['heat'],
        'other': energy_sce['other'] * EMISSION_FACTORS['other']
    }
    
    total_co2 = sum(co2_emissions.values())
    
    return co2_emissions, total_co2


def calculate_energy_mix(energy_sce, total_energy):
    """
    计算能源结构占比
    将能源分类为：煤炭、石油、天然气、可再生能源/其他
    """
    if total_energy <= 0:
        return {'coal': 0.0, 'oil': 0.0, 'gas': 0.0, 'ren': 0.0}
    
    # 煤炭类（原煤 + 焦炭）
    coal_total = energy_sce['coal'] + energy_sce['coke']
    
    # 石油类（原油 + 汽油 + 煤油 + 柴油 + 燃料油）
    oil_total = (energy_sce['crude_oil'] + energy_sce['gasoline'] + 
                 energy_sce['kerosene'] + energy_sce['diesel'] + energy_sce['fuel_oil'])
    
    # 天然气
    gas_total = energy_sce['natural_gas']
    
    # 可再生能源/其他（电力中的可再生部分、热力、其他）
    # 假设其他能源和一部分电力/热力来自可再生能源
    ren_total = energy_sce['other'] + energy_sce['heat'] + energy_sce['electricity'] * 0.3  # 假设30%电力来自可再生
    
    return {
        'coal': coal_total / total_energy,
        'oil': oil_total / total_energy,
        'gas': gas_total / total_energy,
        'ren': ren_total / total_energy
    }


def calculate_power_share(row, total_energy):
    """
    计算电力占总能源消费的比例
    """
    if total_energy <= 0:
        return 0.0
    
    electricity_sce = row['electricity'] * ENERGY_CONVERSION_FACTORS['electricity_enduse']
    return electricity_sce / total_energy


def process_data(md_file_path, output_csv_path):
    """
    处理完整的数据流程
    """
    print("=" * 60)
    print("开始处理真实三年数据")
    print("=" * 60)
    
    # 1. 解析数据
    print("\n1. 解析Markdown数据...")
    df = parse_markdown_data(md_file_path)
    print(f"   解析到 {len(df)} 年的数据: {df['year'].tolist()}")
    
    # 2. 计算能源标煤当量和CO2排放
    print("\n2. 计算能源标煤当量和CO2排放...")
    results = []
    
    for idx, row in df.iterrows():
        year = int(row['year'])
        print(f"\n   处理 {year} 年数据:")
        
        # 计算各能源的标煤当量
        energy_sce, total_calculated = calculate_energy_in_sce(row)
        print(f"   - 计算的综合能耗: {total_calculated:.2f} 万吨标煤")
        print(f"   - 报告的综合能耗: {row['total_energy']:.2f} 万吨标煤")
        print(f"   - 差异: {abs(total_calculated - row['total_energy']):.2f} 万吨标煤 ({abs(total_calculated - row['total_energy']) / row['total_energy'] * 100:.1f}%)")
        
        # 使用报告的总能耗（更准确）
        total_energy = row['total_energy']
        
        # 计算CO2排放
        co2_emissions, total_co2 = calculate_co2_emissions(energy_sce, row)
        print(f"   - 计算的CO2排放: {total_co2:.2f} 万吨")
        print(f"   - 报告的CO2排放: {row['co2_reported']:.2f} 万吨")
        print(f"   - 差异: {abs(total_co2 - row['co2_reported']):.2f} 万吨 ({abs(total_co2 - row['co2_reported']) / row['co2_reported'] * 100:.1f}%)")
        
        # 使用报告的CO2排放（更准确）
        total_co2 = row['co2_reported']
        
        # 计算能源结构
        mix = calculate_energy_mix(energy_sce, total_energy)
        
        # 归一化能源结构（确保总和为1）
        mix_sum = sum(mix.values())
        if mix_sum > 0:
            mix = {k: v / mix_sum for k, v in mix.items()}
        
        print(f"   - 能源结构: 煤炭{mix['coal']*100:.1f}%, 石油{mix['oil']*100:.1f}%, 天然气{mix['gas']*100:.1f}%, 可再生{mix['ren']*100:.1f}%")
        
        # 计算电力占比
        power_share = calculate_power_share(row, total_energy)
        print(f"   - 电力占比: {power_share*100:.1f}%")
        
        # 使用可比价工业总产值作为GDP指标（更适合趋势分析）
        gdp = row['industrial_output_comparable'] / 10000  # 转换为亿元
        
        # 计算碳强度（万吨CO2/亿元GDP）
        carbon_intensity = total_co2 / gdp if gdp > 0 else 0
        print(f"   - GDP(可比价): {gdp:.2f} 亿元")
        print(f"   - 碳强度: {carbon_intensity:.4f} 万吨CO2/亿元")
        
        results.append({
            'year': year,
            'gdp': gdp,
            'co2': total_co2,
            'carbon_intensity': carbon_intensity,
            'mix_coal': mix['coal'],
            'mix_oil': mix['oil'],
            'mix_gas': mix['gas'],
            'mix_ren': mix['ren'],
            'power_share': power_share,
            'total_energy': total_energy
        })
    
    # 3. 创建输出DataFrame
    print("\n3. 创建输出数据...")
    output_df = pd.DataFrame(results)
    
    # 4. 保存到CSV
    print(f"\n4. 保存到 {output_csv_path}")
    output_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    
    # 5. 显示摘要
    print("\n" + "=" * 60)
    print("数据处理完成摘要")
    print("=" * 60)
    print(output_df.to_string(index=False))
    print("\n趋势分析:")
    
    if len(output_df) >= 2:
        # GDP增长率
        gdp_growth = []
        co2_growth = []
        ci_reduction = []
        energy_growth = []
        
        for i in range(1, len(output_df)):
            year_prev = int(output_df.iloc[i-1]['year'])
            year_curr = int(output_df.iloc[i]['year'])
            gdp_g = (output_df.iloc[i]['gdp'] / output_df.iloc[i-1]['gdp'] - 1) * 100
            co2_g = (output_df.iloc[i]['co2'] / output_df.iloc[i-1]['co2'] - 1) * 100
            ci_change = (output_df.iloc[i]['carbon_intensity'] / output_df.iloc[i-1]['carbon_intensity'] - 1) * 100
            energy_g = (output_df.iloc[i]['total_energy'] / output_df.iloc[i-1]['total_energy'] - 1) * 100
            
            print(f"  {year_prev}-{year_curr}:")
            print(f"    GDP增长: {gdp_g:+.2f}%")
            print(f"    CO2排放变化: {co2_g:+.2f}%")
            print(f"    能源消费变化: {energy_g:+.2f}%")
            print(f"    碳强度变化: {ci_change:+.2f}%")
            
            gdp_growth.append(gdp_g)
            co2_growth.append(co2_g)
            ci_reduction.append(ci_change)
            energy_growth.append(energy_g)
        
        print(f"\n  三年平均:")
        print(f"    GDP年均增长: {np.mean(gdp_growth):.2f}%")
        print(f"    CO2年均变化: {np.mean(co2_growth):.2f}%")
        print(f"    能源年均变化: {np.mean(energy_growth):.2f}%")
        print(f"    碳强度年均变化: {np.mean(ci_reduction):.2f}%")
    
    print("=" * 60)
    
    return output_df


if __name__ == '__main__':
    # 输入和输出路径
    input_file = 'D:\\software\\carbon_peak3\\三年的数据.md'
    output_file = 'D:\\software\\carbon_peak3\\backend\\data\\real_data_2022_2024.csv'
    
    # 处理数据
    df = process_data(input_file, output_file)
