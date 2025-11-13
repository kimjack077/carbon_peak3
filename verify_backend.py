"""
快速验证后端API是否正常工作
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def test_api():
    print("验证后端API...")
    print("=" * 60)
    
    # 等待后端启动
    print("\n1. 检查后端连接...")
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/api/scenarios", timeout=2)
            print(f"   ✓ 后端已连接 (HTTP {response.status_code})")
            break
        except requests.ConnectionError:
            if i < max_retries - 1:
                print(f"   等待后端启动... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"   ✗ 无法连接到后端，请确保后端已启动")
                return False
    
    # 测试获取情景列表
    print("\n2. 获取情景列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/scenarios")
        if response.status_code == 200:
            scenarios = response.json()
            print(f"   ✓ 成功获取 {len(scenarios)} 个情景:")
            for name in scenarios.keys():
                print(f"     - {name}")
        else:
            print(f"   ✗ 获取失败 (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"   ✗ 错误: {str(e)}")
        return False
    
    # 测试加载示例数据
    print("\n3. 加载示例数据...")
    try:
        response = requests.post(f"{BASE_URL}/api/upload/example")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 数据加载成功")
            print(f"     年份: {data.get('years', [])}")
        else:
            print(f"   ✗ 加载失败 (HTTP {response.status_code})")
    except Exception as e:
        print(f"   ✗ 错误: {str(e)}")
    
    # 测试运行预测
    print("\n4. 测试运行预测...")
    try:
        payload = {
            "scenarios": ["基准情景"],
            "forecast_years": 36
        }
        response = requests.post(f"{BASE_URL}/api/predict", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ 预测运行成功")
            print(f"     图表: {result.get('carbon_peak_chart', 'N/A')}")
        else:
            print(f"   ⚠ 预测失败 (HTTP {response.status_code})")
            print(f"     {response.text[:200]}")
    except Exception as e:
        print(f"   ⚠ 错误: {str(e)}")
    
    # 测试获取图表数据
    print("\n5. 测试获取图表数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/chart-data")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 图表数据获取成功")
            print(f"     包含 {len(data)} 个情景的数据")
        else:
            print(f"   ⚠ 获取失败 (HTTP {response.status_code})")
    except Exception as e:
        print(f"   ⚠ 错误: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ 后端API验证完成！")
    print("\n提示：")
    print("  - 后端地址: http://localhost:5000")
    print("  - API文档: 查看 后端更新说明.md")
    print("  - 测试脚本: test_backend_api.py")
    
    return True


if __name__ == '__main__':
    test_api()
