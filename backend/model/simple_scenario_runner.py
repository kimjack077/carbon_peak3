"""简化的场景运行器 - 统一调用LEAP和Kaya模型"""
from .simplified_leap import run_leap_model
from .simplified_kaya import run_kaya_model


def run_simple_scenario(base_data, params, horizon_year):
    """
    运行简化的场景预测
    
    参数:
        base_data: 基准年数据字典
        params: 情景参数，必须包含 'model_type' 字段
        horizon_year: 预测终止年份
    
    返回:
        DataFrame包含预测结果
    """
    model_type = params.get('model_type', 'leap').lower()
    
    if model_type == 'leap':
        return run_leap_model(base_data, params, horizon_year)
    elif model_type == 'kaya':
        return run_kaya_model(base_data, params, horizon_year)
    else:
        raise ValueError(f"Unknown model type: {model_type}. Must be 'leap' or 'kaya'")
