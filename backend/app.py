from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import json
import matplotlib
import shutil
matplotlib.use('Agg')  # 非交互式后端

from model.data_processor import DataProcessor
from model.scenario_runner import run_scenario
from utils.plot_results import plot_carbon_peak, plot_energy_mix

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置文件路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """上传基准年数据"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 保存上传的文件
    file_path = os.path.join(DATA_DIR, 'base_year_data.csv')
    file.save(file_path)
    
    # 加载数据验证
    try:
        processor = DataProcessor(file_path)
        data = processor.load_data()
        return jsonify({
            'message': 'File uploaded successfully',
            'years': processor.years.tolist(),
            'sectors': processor.sectors.tolist(),
            'rows': len(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios', methods=['POST'])
def create_scenario():
    """创建预测情景"""
    data = request.json
    
    scenario_name = data.get('name', '默认情景')
    
    # 新模型参数
    scenario_params = {
        'model_type': data.get('model_type', 'leap'),  # 'leap' 或 'kaya'
        'gdp_growth_rate': data.get('gdp_growth_rate', 0.05),
        'population_growth_rate': data.get('population_growth_rate', 0.00),
        'efficiency_improvement_rate': data.get('efficiency_improvement_rate', 0.03),
        'coal_reduction_rate': data.get('coal_reduction_rate', 0.01),
        'power_share_increase': data.get('power_share_increase', 0.02),
        'ren_share_increase': data.get('ren_share_increase', 0.015),
        'grid_cf_decline': data.get('grid_cf_decline', 0.05),
        # 兼容旧参数
        'trend_method': data.get('trend_method', 'linear_regression')
    }
    
    # 保存情景参数
    scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')
    
    if os.path.exists(scenarios_file):
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
    else:
        scenarios = {}
    
    scenarios[scenario_name] = scenario_params
    
    with open(scenarios_file, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        'message': 'Scenario created successfully',
        'scenario_name': scenario_name
    })

@app.route('/api/scenarios', methods=['GET'])
def get_scenarios():
    """获取所有预测情景"""
    scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')

    if not os.path.exists(scenarios_file):
        return jsonify([])

    with open(scenarios_file, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    return jsonify(scenarios)

@app.route('/api/scenarios/<scenario_name>', methods=['DELETE'])
def delete_scenario(scenario_name):
    """删除预测情景"""
    scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')

    if not os.path.exists(scenarios_file):
        return jsonify({'error': 'No scenarios file found'}), 404

    try:
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)

        if scenario_name not in scenarios:
            return jsonify({'error': 'Scenario not found'}), 404

        # 删除场景
        del scenarios[scenario_name]

        # 保存更新后的场景文件
        with open(scenarios_file, 'w', encoding='utf-8') as f:
            json.dump(scenarios, f, ensure_ascii=False, indent=2)

        # 删除相关的预测结果文件
        results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
        if os.path.exists(results_path):
            os.remove(results_path)

        return jsonify({
            'message': 'Scenario deleted successfully',
            'scenario_name': scenario_name
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """运行预测"""
    data = request.json
    scenario_names = data.get('scenarios', [])
    forecast_years = data.get('forecast_years', 30)
    
    if not scenario_names:
        return jsonify({'error': 'No scenarios selected'}), 400
    
    # 加载基准年数据
    data_path = os.path.join(DATA_DIR, 'base_year_data.csv')
    processor = DataProcessor(data_path)
    processor.load_data()
    
    # 加载情景参数
    scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')
    with open(scenarios_file, 'r', encoding='utf-8') as f:
        all_scenarios = json.load(f)
    
    # 运行选定的情景
    results_dict = {}
    base = processor.prepare_base_dict_for_models()
    horizon_year = base['years'][-1] + forecast_years
    
    for scenario_name in scenario_names:
        if scenario_name in all_scenarios:
            scenario_params = all_scenarios[scenario_name]
            results = run_scenario(base, scenario_params, horizon_year)
            results_dict[scenario_name] = results
    
    # 生成图表
    carbon_peak_path = os.path.join(OUTPUT_DIR, 'carbon_peak.png')
    try:
        plot_carbon_peak(results_dict, carbon_peak_path)
    except Exception as e:
        print(f"生成碳达峰图表失败: {str(e)}")
    
    # 为第一个情景生成能源结构图
    if results_dict:
        first_scenario = list(results_dict.keys())[0]
        energy_mix_path = os.path.join(OUTPUT_DIR, 'energy_mix.png')
        try:
            plot_energy_mix(results_dict[first_scenario], energy_mix_path)
        except Exception as e:
            print(f"生成能源结构图表失败: {str(e)}")
    
    # 保存结果数据
    for scenario_name, results in results_dict.items():
        results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
        results.to_csv(results_path, index=False, encoding='utf-8')
    
    return jsonify({
        'message': 'Prediction completed',
        'carbon_peak_chart': '/api/charts/carbon_peak',
        'energy_mix_chart': '/api/charts/energy_mix',
        'scenarios': list(results_dict.keys())
    })

@app.route('/api/charts/<chart_name>', methods=['GET'])
def get_chart(chart_name):
    """获取生成的图表"""
    if chart_name == 'carbon_peak':
        return send_file(os.path.join(OUTPUT_DIR, 'carbon_peak.png'), mimetype='image/png')
    elif chart_name == 'energy_mix':
        return send_file(os.path.join(OUTPUT_DIR, 'energy_mix.png'), mimetype='image/png')
    else:
        return jsonify({'error': 'Chart not found'}), 404

@app.route('/api/results/<scenario_name>', methods=['GET'])
def get_results(scenario_name):
    """获取预测结果数据"""
    results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
    
    if not os.path.exists(results_path):
        return jsonify({'error': 'Results not found'}), 404
    
    results = pd.read_csv(results_path)
    return jsonify(results.to_dict(orient='records'))

@app.route('/api/predict/status', methods=['POST'])
def get_prediction_status():
    # 获取所有已运行的预测情景
    scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')
    
    if not os.path.exists(scenarios_file):
        return jsonify({'scenarios': []})
    
    with open(scenarios_file, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    # 检查哪些情景有结果数据
    available_scenarios = []
    for scenario_name in scenarios:
        results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
        if os.path.exists(results_path):
            available_scenarios.append(scenario_name)
    
    return jsonify({'scenarios': available_scenarios})

@app.route('/api/upload/example', methods=['POST'])
def use_example_data():
    """使用示例数据"""
    # 复制示例数据到工作目录
    sample_path = os.path.join(DATA_DIR, 'sample_data.csv')
    target_path = os.path.join(DATA_DIR, 'base_year_data.csv')
    
    try:
        shutil.copy(sample_path, target_path)
        
        # 加载数据验证
        processor = DataProcessor(target_path)
        data = processor.load_data()
        
        return jsonify({
            'message': 'Example data loaded successfully',
            'years': [int(y) for y in processor.years],
            'rows': len(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<scenario_name>/download', methods=['GET'])
def download_results(scenario_name):
    """下载预测结果数据"""
    results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
    
    if not os.path.exists(results_path):
        return jsonify({'error': 'Results not found'}), 404
    
    return send_file(
        results_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{scenario_name}_results.csv'
    )

@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    """获取所有情景的预测数据（包含历史数据），用于前端绘图（支持新旧格式）"""
    try:
        # 加载历史数据
        base_data_path = os.path.join(DATA_DIR, 'base_year_data.csv')
        historical_data = None
        if os.path.exists(base_data_path):
            historical_df = pd.read_csv(base_data_path)
            # 统一列名：co2 -> total_emission
            if 'co2' in historical_df.columns and 'total_emission' not in historical_df.columns:
                historical_df['total_emission'] = historical_df['co2']
            
            # 添加缺失的能源消费列（如果没有）
            if 'energy_consumption' not in historical_df.columns:
                # 使用与模型相同的计算方式
                # 电网排放因子 (tCO2/MWh) - 示意值
                EF_grid = 0.65
                kappa = 1.0  # toe->MWh转换系数，默认1.0
                
                # 排放因子 (tCO2/单位能耗)
                EMISSION_FACTORS = {
                    "coal": 2.5,
                    "oil": 2.1,
                    "gas": 1.6,
                    "ren": 0.0
                }
                
                energy_list = []
                for i in range(len(historical_df)):
                    gdp = historical_df.iloc[i]['gdp']  # 万亿元
                    co2 = historical_df.iloc[i]['co2']  # 万吨CO2
                    
                    # 计算碳强度
                    ci = co2 / gdp  # 万吨CO2/千克 = 万吨CO2
                    
                    # 获取能源结构数据
                    mix_i = {
                        "coal": historical_df.iloc[i]['mix_coal'],
                        "oil": historical_df.iloc[i]['mix_oil'],
                        "gas": historical_df.iloc[i]['mix_gas'],
                        "ren": historical_df.iloc[i]['mix_ren']
                    }
                    p_i = historical_df.iloc[i]['power_share']
                    
                    # 计算直燃碳因子
                    cf_dir_i = sum(mix_i[f] * EMISSION_FACTORS[f] for f in mix_i)
                    
                    # 计算综合碳因子
                    cf_i = (1 - p_i) * cf_dir_i + p_i * (EF_grid * kappa)
                    
                    # 能源强度 = 碳强度 / 碳因子
                    ei_i = ci / max(cf_i, 1e-9)  # 万吨标煤/千克 = 万吨标煤
                    
                    # 能源消费 = GDP × 能源强度
                    energy = gdp * ei_i  # 亿元/千克 = 亿元 × 万吨标煤/千克 = 万吨标煤
                    energy_list.append(energy)
                
                historical_df['energy_consumption'] = energy_list
            
            historical_data = historical_df
        
        # 获取所有可用情景
        scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')
        if not os.path.exists(scenarios_file):
            return jsonify({'error': 'No scenarios available'}), 404
        
        with open(scenarios_file, 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
        
        # 收集所有情景的数据
        chart_data = {}
        for scenario_name in scenarios:
            results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
            if os.path.exists(results_path):
                forecast_df = pd.read_csv(results_path)
                
                # 使用统一的列名
                emission_col = 'total_emission'
                
                # 合并历史数据和预测数据
                if historical_data is not None:
                    # 确保历史数据和预测数据没有重叠的年份
                    hist_years = set(historical_data['year'].tolist())
                    forecast_years = set(forecast_df['year'].tolist())
                    
                    if not hist_years.intersection(forecast_years):
                        # 合并数据
                        combined_df = pd.concat([historical_data, forecast_df], ignore_index=True).sort_values('year')
                    else:
                        # 有重叠，只使用预测数据
                        combined_df = forecast_df
                else:
                    combined_df = forecast_df
                
                # 找出峰值年份和数值（仅在预测数据中）
                peak_idx = forecast_df[emission_col].idxmax()
                peak_year = int(forecast_df.loc[peak_idx, 'year'])
                peak_value = float(forecast_df.loc[peak_idx, emission_col])
                
                # 准备图表数据（包含历史+预测）
                chart_data[scenario_name] = {
                    'years': combined_df['year'].tolist(),
                    'emissions': combined_df[emission_col].tolist(),
                    'peak': {
                        'year': peak_year,
                        'value': peak_value
                    },
                    'model_type': scenarios[scenario_name].get('model_type', 'unknown'),
                    'historical_years': historical_data['year'].tolist() if historical_data is not None else []
                }
                
                # 能源结构数据 - 转换为消费量（从比例计算）
                # 使用能源消费总量 × 各能源占比
                energy_total = combined_df['energy_consumption']
                chart_data[scenario_name]['energy_mix'] = {
                    'coal': (energy_total * combined_df['mix_coal']).tolist(),
                    'elec': (energy_total * combined_df['power_share']).tolist(),
                    'other': (energy_total * (combined_df['mix_oil'] + combined_df['mix_gas'] + combined_df['mix_ren'])).tolist()
                }
        
        if not chart_data:
            return jsonify({'error': 'No prediction results available'}), 404
            
        return jsonify(chart_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    # 从环境变量读取配置，默认开发模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0') 
    # 计算能源消费总量，使用与Kaya模型一致的逻辑
    energy_consumption = []
    
    # 获取情景参数，用于计算碳因子
    model_type = chart_data.get("model_type", "kaya")
    scenario_name = chart_data.get("scenario_name", "")
    
    # 从scenarios.json获取情景参数
    scenarios = {}
    try:
        with open('data/scenarios.json', 'r', encoding='utf-8') as f:
            scenarios = json.load(f)
    except Exception as e:
        print(f"Error loading scenarios: {e}")
    
    scenario_params = scenarios.get(scenario_name, {})
    
    # Kaya模型参数
    EF_grid = scenario_params.get('EF_grid', 0.65)  # 电网排放因子
    kappa = scenario_params.get("kappa", 1.0)  # 转换系数
    
    # 排放因子 (tCO2/单位能耗) - 与Kaya模型保持一致
    EMISSION_FACTORS = {
        "coal": 2.5,
        "oil": 2.1,
        "gas": 1.6,
        "ren": 0.0
    }
    
    # 计算历史能源消费
    for i in range(len(historical_years)):
        year = historical_years[i]
        gdp = historical_data["gdp"][i]
        co2 = historical_data["co2"][i]
        
        # 计算碳强度
        ci = co2 / gdp
        
        # 获取能源结构数据
        coal = historical_data["mix_coal"][i]
        oil = historical_data["mix_oil"][i]
        gas = historical_data["mix_gas"][i]
        ren = historical_data["mix_ren"][i]
        power_share = historical_data["power_share"][i]
        
        # 计算直燃碳因子
        cf_dir = coal * EMISSION_FACTORS["coal"] + oil * EMISSION_FACTORS["oil"] + gas * EMISSION_FACTORS["gas"] + ren * EMISSION_FACTORS["ren"]
        
        # 计算综合碳因子
        cf = (1 - power_share) * cf_dir + power_share * (EF_grid * kappa)
        
        # 计算能源强度 (EI = CI / CF)
        ei = ci / cf
        
        # 计算能源消费总量 (Energy = GDP × EI)
        energy = gdp * ei
        
        energy_consumption.append(energy)
    
    # 合并历史和预测数据
    all_years = historical_years + years
    all_energy_consumption = energy_consumption + forecast_data["energy_consumption"]