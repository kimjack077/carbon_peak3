import requests
import json

# 获取API数据
url = "http://localhost:5000/api/chart-data"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    print("===== 能源消费数据验证报告 =====\n")
    
    # 检查每个情景
    for scenario_name, scenario_data in data.items():
        print(f"情景名称: {scenario_name}")
        print(f"模型类型: {scenario_data.get('model_type', 'unknown')}")
        
        # 检查energy_mix字段
        if 'energy_mix' in scenario_data:
            energy_mix = scenario_data['energy_mix']
            coal = energy_mix['coal']
            elec = energy_mix['elec']
            other = energy_mix['other']
            
            # 计算总量
            total_energy = [c + e + o for c, e, o in zip(coal, elec, other)]
            years = scenario_data['years']
            
            # 检查历史数据（前3年）
            print("\n历史数据（前3年）:")
            for i in range(min(3, len(years))):
                year = years[i]
                energy = total_energy[i]
                print(f"  {year}年: {energy:.2f}万吨标煤")
            
            # 检查过渡期（第3-5年）
            if len(years) >= 5:
                print("\n历史与预测过渡期:")
                for i in range(2, min(5, len(years))):
                    year = years[i]
                    energy = total_energy[i]
                    prev_energy = total_energy[i-1]
                    growth_rate = (energy / prev_energy - 1) * 100
                    print(f"  {year}年: {energy:.2f}万吨标煤 (增长率: {growth_rate:.2f}%)")
            
            # 检查异常增长率
            print("\n增长率检查:")
            has_abnormal_growth = False
            for i in range(1, min(10, len(total_energy))):
                prev_energy = total_energy[i-1]
                curr_energy = total_energy[i]
                growth_rate = (curr_energy / prev_energy - 1) * 100
                
                if abs(growth_rate) > 50:  # 增长率超过50%视为异常
                    print(f"  警告: {years[i-1]}年->{years[i]}年增长率异常: {growth_rate:.2f}%")
                    has_abnormal_growth = True
            
            if not has_abnormal_growth:
                print("  无异常增长率")
            
            # 检查数据范围
            min_energy = min(total_energy)
            max_energy = max(total_energy)
            print(f"\n数据范围: {min_energy:.2f} - {max_energy:.2f} 万吨标煤")
            
            if min_energy < 1000:
                print(f"  警告: 最小值过小 ({min_energy:.2f}万吨标煤)")
            if max_energy > 100000:
                print(f"  警告: 最大值过大 ({max_energy:.2f}万吨标煤)")
        
        print("\n" + "="*50 + "\n")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)