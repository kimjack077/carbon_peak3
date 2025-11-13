"""
测试 /api/chart-data 端点返回的数据格式
"""
import requests
import json

BASE_URL = "http://localhost:5000"

try:
    print("请求 /api/chart-data...")
    response = requests.get(f"{BASE_URL}/api/chart-data", timeout=10)
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers.get('Content-Type')}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print(f"返回的情景数量: {len(data)}")
        print(f"情景列表: {list(data.keys())}")
        print()
        
        # 检查第一个情景的数据结构
        if data:
            first_scenario = list(data.keys())[0]
            scenario_data = data[first_scenario]
            
            print(f"=== {first_scenario} 的数据结构 ===")
            print(f"数据键: {list(scenario_data.keys())}")
            print()
            
            # 检查每个字段
            for key in ['years', 'emissions', 'peak', 'energy_mix']:
                if key in scenario_data:
                    value = scenario_data[key]
                    if key in ['years', 'emissions']:
                        print(f"{key}: 类型={type(value).__name__}, 长度={len(value) if isinstance(value, list) else 'N/A'}")
                        if isinstance(value, list) and len(value) > 0:
                            print(f"  示例值: {value[:3]}...")
                    elif key == 'peak':
                        print(f"{key}: {value}")
                    elif key == 'energy_mix':
                        print(f"{key}: 类型={type(value).__name__}, 键={list(value.keys()) if isinstance(value, dict) else 'N/A'}")
                else:
                    print(f"{key}: ❌ 缺失")
            
            print()
            print("✅ 数据格式检查完成")
            
            # 保存完整响应到文件
            with open('chart_data_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("完整响应已保存到 chart_data_response.json")
        else:
            print("⚠️  返回的数据为空对象 {}")
    else:
        print(f"❌ 错误: {response.text}")

except requests.ConnectionError:
    print("❌ 无法连接到后端，请确保后端已启动 (python backend/app.py)")
except Exception as e:
    print(f"❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()
