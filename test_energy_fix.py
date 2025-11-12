import requests
import json

# 获取API数据
url = "http://localhost:5000/api/chart-data"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    # 获取第一个情景的数据
    scenario_name = list(data.keys())[0]
    scenario_data = data[scenario_name]
    
    print(f"情景名称: {scenario_name}")
    print(f"情景中的键: {list(scenario_data.keys())}")
    
    # 检查energy_mix字段
    if 'energy_mix' in scenario_data:
        print(f"energy_mix中的键: {list(scenario_data['energy_mix'].keys())}")
        
        # 计算能源消费总量
        energy_mix = scenario_data['energy_mix']
        coal = energy_mix['coal']
        elec = energy_mix['elec']
        other = energy_mix['other']
        
        # 计算总量
        total_energy = [c + e + o for c, e, o in zip(coal, elec, other)]
        print(f"计算的能源消费总量前5个数据: {total_energy[:5]}")
        
        # 检查2022-2024年的数据
        years = scenario_data['years']
        for i, year in enumerate(years[:3]):
            energy = total_energy[i]
            print(f"{year}年: {energy}万吨标煤")
            # 调整阈值，认为低于5000万吨标煤才算过小
            if energy < 5000:
                print(f"  警告: {year}年能源消费数据过小")
        
        # 计算年增长率
        for i in range(1, min(5, len(total_energy))):
            prev_energy = total_energy[i-1]
            curr_energy = total_energy[i]
            growth_rate = (curr_energy / prev_energy - 1) * 100
            print(f"{years[i-1]}年->{years[i]}年: {growth_rate:.2f}%")
            
            # 检查异常增长率
            if growth_rate > 50:
                print(f"  警告: {years[i-1]}年->{years[i]}年增长率异常")
        
        # 检查years字段
        print(f"years字段数量: {len(years)}")
        print(f"years前5个数据: {years[:5]}")
    else:
        print("警告: energy_mix字段不存在")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)