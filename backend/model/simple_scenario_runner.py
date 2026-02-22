"""Scenario runner for LEAP/Kaya/STIRPAT unified interface."""

from .simplified_leap import run_leap_model
from .simplified_kaya import run_kaya_model
from .stirpat_model import run_stirpat_model


SUPPORTED_MODELS = {"leap", "kaya", "stirpat"}


def run_simple_scenario(base_data, params, horizon_year, historical_data=None):
    """Run scenario with selected model."""
    model_type = str(params.get("model_type", "leap")).lower()

    if model_type == "leap":
        return run_leap_model(base_data, params, horizon_year)
    if model_type == "kaya":
        return run_kaya_model(base_data, params, horizon_year)
    if model_type == "stirpat":
        return run_stirpat_model(base_data, params, horizon_year, historical_data)

    raise ValueError(
        f"Unknown model type: {model_type}. Must be one of {sorted(SUPPORTED_MODELS)}"
    )


def get_model_description(model_type):
    """Get model description."""
    descriptions = {
        "leap": "LEAP模型：基于活动水平、能效与能源结构分解的长期情景预测。",
        "kaya": "Kaya恒等式：通过GDP、能耗强度和碳强度分解排放驱动因素。",
        "stirpat": "STIRPAT模型：利用弹性系数评估经济、技术和结构变化对排放的影响。",
    }
    return descriptions.get(str(model_type).lower(), "未知模型")
