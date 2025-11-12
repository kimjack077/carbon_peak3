import pandas as pd
import numpy as np

class DataProcessor:
    """数据处理器 - 只支持新格式（3年历史数据）"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = None
        self.years = None
        self.max_year = None
    
    def load_data(self):
        """加载基准年数据（新格式：3年历史数据）"""
        self.data = pd.read_csv(self.data_path)
        
        # 必需字段
        required_cols = ['year', 'gdp', 'co2', 'carbon_intensity', 
                        'mix_coal', 'mix_oil', 'mix_gas', 'mix_ren', 'power_share']
        
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"缺少必要字段: {col}")
        
        # 确保数据类型正确
        self.data['year'] = self.data['year'].astype(int)
        self.data['gdp'] = self.data['gdp'].astype(float)
        self.data['co2'] = self.data['co2'].astype(float)
        self.data['carbon_intensity'] = self.data['carbon_intensity'].astype(float)
        self.data['mix_coal'] = self.data['mix_coal'].astype(float)
        self.data['mix_oil'] = self.data['mix_oil'].astype(float)
        self.data['mix_gas'] = self.data['mix_gas'].astype(float)
        self.data['mix_ren'] = self.data['mix_ren'].astype(float)
        self.data['power_share'] = self.data['power_share'].astype(float)
        
        # 可选字段
        if 'population' in self.data.columns:
            self.data['population'] = self.data['population'].astype(float)
        
        # 提取年份
        self.years = sorted(self.data['year'].unique())
        self.max_year = max(self.years)
        
        # 验证至少有3年数据
        if len(self.years) < 3:
            raise ValueError("至少需要3年的历史数据")
        
        # 验证能源结构份额
        for i in range(len(self.data)):
            mix_sum = (self.data.iloc[i]['mix_coal'] + 
                      self.data.iloc[i]['mix_oil'] + 
                      self.data.iloc[i]['mix_gas'] + 
                      self.data.iloc[i]['mix_ren'])
            if abs(mix_sum - 1.0) > 0.01:
                raise ValueError(f"第{i+1}行能源结构份额和不为1: {mix_sum:.4f}")
        
        return self.data
    
    def prepare_base_dict_for_models(self):
        """准备模型输入格式的基础数据字典"""
        if self.data is None:
            self.load_data()
        
        # 构建base字典
        base = {
            "years": self.data['year'].tolist(),
            "gdp": self.data['gdp'].tolist(),
            "co2": self.data['co2'].tolist(),
            "ci": self.data['carbon_intensity'].tolist(),
            "mix": {
                "coal": self.data['mix_coal'].tolist(),
                "oil": self.data['mix_oil'].tolist(),
                "gas": self.data['mix_gas'].tolist(),
                "ren": self.data['mix_ren'].tolist()
            },
            "power_share": self.data['power_share'].tolist()
        }
        
        # 可选：人口数据
        if 'population' in self.data.columns:
            base["population"] = self.data['population'].tolist()
        
        return base
