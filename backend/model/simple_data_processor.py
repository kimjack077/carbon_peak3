"""简化的数据处理器 - 只处理年份、能耗、GDP、碳排放"""
import pandas as pd
import numpy as np


class SimpleDataProcessor:
    """简化的数据处理器"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
    
    def load_data(self):
        """加载CSV数据"""
        self.data = pd.read_csv(self.file_path)
        
        # 验证必需的列
        required_cols = ['year', 'energy_consumption', 'gdp', 'co2_emission']
        missing_cols = [col for col in required_cols if col not in self.data.columns]
        
        if missing_cols:
            raise ValueError(f"缺少必需的列: {missing_cols}")
        
        # 如果没有可再生能源比例，默认为0
        if 'renewable_ratio' not in self.data.columns:
            self.data['renewable_ratio'] = 0.0
        
        return self.data
    
    def get_base_year_data(self):
        """获取基准年（最后一年）数据"""
        if self.data is None:
            self.load_data()
        
        last_row = self.data.iloc[-1]
        base_year = int(last_row['year'])
        
        return {
            'year': base_year,
            'energy': float(last_row['energy_consumption']),  # 万吨标煤
            'gdp': float(last_row['gdp']),  # 万元
            'co2': float(last_row['co2_emission']),  # 万吨CO2
            'renewable_ratio': float(last_row['renewable_ratio']),  # 可再生能源占比
            'energy_intensity': float(last_row['energy_consumption'] / last_row['gdp']),  # 能源强度
            'carbon_intensity': float(last_row['co2_emission'] / last_row['gdp']),  # 碳强度
        }
    
    def get_historical_data(self):
        """获取历史数据"""
        if self.data is None:
            self.load_data()
        
        return {
            'years': self.data['year'].tolist(),
            'energy': self.data['energy_consumption'].tolist(),
            'gdp': self.data['gdp'].tolist(),
            'co2': self.data['co2_emission'].tolist(),
            'renewable_ratio': self.data['renewable_ratio'].tolist(),
        }
    
    def calculate_growth_rates(self):
        """计算历史增长率"""
        if self.data is None:
            self.load_data()
        
        if len(self.data) < 2:
            return {
                'gdp_growth_rate': 0.0,
                'energy_growth_rate': 0.0,
                'co2_growth_rate': 0.0,
            }
        
        # 计算平均年增长率
        years = len(self.data) - 1
        
        gdp_growth = (self.data['gdp'].iloc[-1] / self.data['gdp'].iloc[0]) ** (1/years) - 1
        energy_growth = (self.data['energy_consumption'].iloc[-1] / self.data['energy_consumption'].iloc[0]) ** (1/years) - 1
        co2_growth = (self.data['co2_emission'].iloc[-1] / self.data['co2_emission'].iloc[0]) ** (1/years) - 1
        
        return {
            'gdp_growth_rate': float(gdp_growth),
            'energy_growth_rate': float(energy_growth),
            'co2_growth_rate': float(co2_growth),
        }
