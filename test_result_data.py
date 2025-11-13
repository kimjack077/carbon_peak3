"""
检查结果文件的数据结构
"""
import pandas as pd
import os

OUTPUT_DIR = 'backend/output'

# 检查几个结果文件
result_files = [
    '基准情景_results.csv',
    '2030年达峰情景_results.csv',
    '持续下降情景_results.csv'
]

print("检查结果文件的数据结构...")
print("=" * 80)

for filename in result_files:
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        print(f"\n文件: {filename}")
        print("-" * 80)
        
        df = pd.read_csv(filepath)
        print(f"行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        
        # 检查关键列是否存在
        required_cols = ['year', 'total_emission', 'energy_consumption', 
                        'mix_coal', 'mix_oil', 'mix_gas', 'mix_ren', 'power_share']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"⚠️  缺失列: {missing_cols}")
        else:
            print("✅ 所有必需列都存在")
        
        # 显示前几行数据
        print("\n前3行数据:")
        print(df.head(3).to_string())
        
        # 检查是否有 NaN 值
        if df.isnull().any().any():
            print("\n⚠️  存在 NaN 值:")
            print(df.isnull().sum()[df.isnull().sum() > 0])
        else:
            print("\n✅ 没有 NaN 值")
    else:
        print(f"\n❌ 文件不存在: {filename}")

print("\n" + "=" * 80)
print("检查完成")
