"""简化版碳达峰预测系统后端API"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json

from backend.model.simple_data_processor import SimpleDataProcessor
from backend.model.simple_scenario_runner import run_simple_scenario

app = Flask(__name__)
CORS(app)

# 路径配置
DATA_DIR = os.path.join(os.path.dirname(__file__), 'backend', 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'backend', 'output')
SCENARIOS_FILE = os.path.join(DATA_DIR, 'simple_scenarios.json')
DATA_FILE = os.path.join(DATA_DIR, 'simple_data.csv')

os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route('/api/simple/scenarios', methods=['GET'])
def get_scenarios():
    """获取所有场景"""
    if not os.path.exists(SCENARIOS_FILE):
        return jsonify([])
    
    with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    return jsonify(scenarios)


@app.route('/api/simple/scenarios', methods=['POST'])
def create_scenario():
    """创建新场景"""
    data = request.json
    
    scenario = {
        'name': data.get('name', '未命名场景'),
        'model_type': data.get('model_type', 'leap'),
        'gdp_growth_rate': data.get('gdp_growth_rate', 0.05),
        'efficiency_improvement_rate': data.get('efficiency_improvement_rate', 0.03),
        'renewable_increase_rate': data.get('renewable_increase_rate', 0.015),
    }
    
    # 加载现有场景
    if os.path.exists(SCENARIOS_FILE):
        with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
    else:
        scenarios = []
    
    # 添加新场景
    scenarios.append(scenario)
    
    # 保存
    with open(SCENARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)
    
    return jsonify({'message': 'Scenario created', 'scenario': scenario})


@app.route('/api/simple/scenarios/<int:index>', methods=['DELETE'])
def delete_scenario(index):
    """删除场景"""
    if not os.path.exists(SCENARIOS_FILE):
        return jsonify({'error': 'No scenarios found'}), 404
    
    with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    if index < 0 or index >= len(scenarios):
        return jsonify({'error': 'Invalid scenario index'}), 400
    
    scenarios.pop(index)
    
    with open(SCENARIOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)
    
    return jsonify({'message': 'Scenario deleted'})


@app.route('/api/simple/predict', methods=['POST'])
def predict():
    """运行预测"""
    data = request.json
    forecast_years = data.get('forecast_years', 30)
    
    # 加载基准数据
    if not os.path.exists(DATA_FILE):
        return jsonify({'error': 'Data file not found'}), 404
    
    processor = SimpleDataProcessor(DATA_FILE)
    processor.load_data()
    base_data = processor.get_base_year_data()
    historical_data = processor.get_historical_data()
    
    # 加载场景
    if not os.path.exists(SCENARIOS_FILE):
        return jsonify({'error': 'No scenarios found'}), 404
    
    with open(SCENARIOS_FILE, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    if not scenarios:
        return jsonify({'error': 'No scenarios available'}), 400
    
    # 预测终止年份
    horizon_year = base_data['year'] + forecast_years
    
    # 运行所有场景
    results = []
    for i, scenario in enumerate(scenarios):
        try:
            forecast_df = run_simple_scenario(base_data, scenario, horizon_year)
            
            # 找到碳达峰年份和峰值
            peak_idx = forecast_df['co2_emission'].idxmax()
            peak_year = int(forecast_df.loc[peak_idx, 'year'])
            peak_value = float(forecast_df.loc[peak_idx, 'co2_emission'])
            
            # 合并历史数据和预测数据
            scenario_result = {
                'name': scenario['name'],
                'model_type': scenario['model_type'],
                'peak_year': peak_year,
                'peak_value': peak_value,
                'historical': {
                    'years': historical_data['years'],
                    'gdp': historical_data['gdp'],
                    'energy': historical_data['energy'],
                    'co2': historical_data['co2'],
                },
                'forecast': {
                    'years': forecast_df['year'].tolist(),
                    'gdp': forecast_df['gdp'].tolist(),
                    'energy': forecast_df['energy_consumption'].tolist(),
                    'co2': forecast_df['co2_emission'].tolist(),
                    'renewable_energy': forecast_df['renewable_energy'].tolist(),
                    'nonrenewable_energy': forecast_df['nonrenewable_energy'].tolist(),
                }
            }
            
            results.append(scenario_result)
            
        except Exception as e:
            results.append({
                'name': scenario['name'],
                'error': str(e)
            })
    
    return jsonify(results)


@app.route('/api/simple/historical', methods=['GET'])
def get_historical():
    """获取历史数据"""
    if not os.path.exists(DATA_FILE):
        return jsonify({'error': 'Data file not found'}), 404
    
    processor = SimpleDataProcessor(DATA_FILE)
    processor.load_data()
    historical_data = processor.get_historical_data()
    
    return jsonify(historical_data)


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5001))
    app.run(debug=True, port=port, host='0.0.0.0')
