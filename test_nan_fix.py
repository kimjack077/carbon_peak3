"""
测试 NaN 值是否已修复
"""
import requests
import json
import math

BASE_URL = "http://localhost:5000"

def test_no_nan_values():
    """测试返回的数据中是否还有 NaN 值"""
    print("=" * 80)
    print("测试 NaN 值修复")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/chart-data", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API返回错误: HTTP {response.status_code}")
            return False
        
        data = response.json()
        print(f"✅ 成功获取 {len(data)} 个情景的数据\n")
        
        has_nan = False
        for scenario_name, scenario_data in data.items():
            print(f"检查情景: {scenario_name}")
            
            # 检查 energy_mix 中的 NaN
            if 'energy_mix' in scenario_data:
                for energy_type, values in scenario_data['energy_mix'].items():
                    nan_count = sum(1 for v in values if v is None or (isinstance(v, float) and math.isnan(v)))
                    if nan_count > 0:
                        print(f"  ❌ {energy_type}: 发现 {nan_count} 个 NaN 值")
                        has_nan = True
                    else:
                        print(f"  ✅ {energy_type}: 无 NaN 值 ({len(values)} 个数据点)")
            
            print()
        
        if not has_nan:
            print("=" * 80)
            print("🎉 所有数据都没有 NaN 值！")
            print("=" * 80)
            return True
        else:
            print("=" * 80)
            print("❌ 仍然存在 NaN 值")
            print("=" * 80)
            return False
    
    except requests.ConnectionError:
        print("❌ 无法连接到后端")
        print("请先启动后端: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n提示：请确保后端已重启以应用修复\n")
    input("按 Enter 开始测试...")
    print()
    
    if test_no_nan_values():
        print("\n✅ 测试通过！现在可以刷新前端页面查看效果")
    else:
        print("\n❌ 测试失败，请检查错误信息")
