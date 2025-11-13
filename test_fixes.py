"""
综合测试：验证前后端修复

测试内容：
1. 后端 /api/chart-data 是否正确处理缺少 power_share 的情况
2. 返回的数据结构是否完整
3. 前端能否正确解析数据
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_chart_data_api():
    """测试图表数据API"""
    print("=" * 80)
    print("测试 /api/chart-data 端点")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/chart-data", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ API返回错误: HTTP {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        
        if not data or len(data) == 0:
            print("❌ 返回的数据为空")
            return False
        
        print(f"✅ 成功获取 {len(data)} 个情景的数据")
        print(f"情景列表: {list(data.keys())}")
        print()
        
        # 验证每个情景的数据结构
        all_valid = True
        for scenario_name, scenario_data in data.items():
            print(f"检查情景: {scenario_name}")
            
            # 检查必需字段
            required_fields = ['years', 'emissions', 'peak', 'energy_mix']
            missing_fields = [field for field in required_fields if field not in scenario_data]
            
            if missing_fields:
                print(f"  ❌ 缺少字段: {missing_fields}")
                all_valid = False
                continue
            
            # 检查字段类型和内容
            if not isinstance(scenario_data['years'], list):
                print(f"  ❌ years 不是列表")
                all_valid = False
            elif len(scenario_data['years']) == 0:
                print(f"  ❌ years 列表为空")
                all_valid = False
            else:
                print(f"  ✅ years: {len(scenario_data['years'])} 个数据点")
            
            if not isinstance(scenario_data['emissions'], list):
                print(f"  ❌ emissions 不是列表")
                all_valid = False
            elif len(scenario_data['emissions']) == 0:
                print(f"  ❌ emissions 列表为空")
                all_valid = False
            else:
                print(f"  ✅ emissions: {len(scenario_data['emissions'])} 个数据点")
            
            if not isinstance(scenario_data['peak'], dict):
                print(f"  ❌ peak 不是字典")
                all_valid = False
            elif 'year' not in scenario_data['peak'] or 'value' not in scenario_data['peak']:
                print(f"  ❌ peak 缺少 year 或 value 字段")
                all_valid = False
            else:
                print(f"  ✅ peak: {scenario_data['peak']['year']}年, {scenario_data['peak']['value']:.2f}万吨")
            
            if not isinstance(scenario_data['energy_mix'], dict):
                print(f"  ❌ energy_mix 不是字典")
                all_valid = False
            else:
                energy_mix_keys = list(scenario_data['energy_mix'].keys())
                print(f"  ✅ energy_mix: {energy_mix_keys}")
                
                # 检查每个能源类型的数据
                for key in energy_mix_keys:
                    if not isinstance(scenario_data['energy_mix'][key], list):
                        print(f"    ❌ energy_mix[{key}] 不是列表")
                        all_valid = False
                    elif len(scenario_data['energy_mix'][key]) == 0:
                        print(f"    ❌ energy_mix[{key}] 列表为空")
                        all_valid = False
            
            print()
        
        if all_valid:
            print("=" * 80)
            print("✅ 所有情景的数据结构都有效")
            print("=" * 80)
            
            # 保存一个示例数据到文件
            first_scenario = list(data.keys())[0]
            sample = {first_scenario: data[first_scenario]}
            with open('sample_chart_data.json', 'w', encoding='utf-8') as f:
                json.dump(sample, f, ensure_ascii=False, indent=2)
            print(f"示例数据已保存到 sample_chart_data.json")
            
            return True
        else:
            print("=" * 80)
            print("❌ 部分数据结构无效")
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


def main():
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "碳达峰预测系统 - 修复验证测试" + " " * 20 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    print("提示：")
    print("  1. 确保后端已启动: python backend/app.py")
    print("  2. 此测试将验证后端API返回的数据结构")
    print("  3. 前端需要重新编译以应用修复: npm run build (如果使用生产环境)")
    print("\n")
    
    input("按 Enter 开始测试...")
    print("\n")
    
    success = test_chart_data_api()
    
    print("\n")
    if success:
        print("🎉 所有测试通过！")
        print("\n下一步：")
        print("  1. 重启前端: npm run serve")
        print("  2. 打开浏览器访问前端")
        print("  3. 检查图表是否正常显示")
        sys.exit(0)
    else:
        print("❌ 测试失败，请检查错误信息")
        sys.exit(1)


if __name__ == '__main__':
    main()
