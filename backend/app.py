from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import json
import matplotlib
import shutil
matplotlib.use('Agg')  # 非交互式后端

from model.simple_data_processor import SimpleDataProcessor
from model.simple_scenario_runner import run_simple_scenario
from utils.plot_results import plot_carbon_peak, plot_gdp, plot_energy_consumption

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
        processor = SimpleDataProcessor(file_path)
        data = processor.load_data()
        return jsonify({
            'message': 'File uploaded successfully',
            'rows': len(data)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios', methods=['POST'])
def create_scenario():
    """创建预测情景"""
    data = request.json
    
    scenario_name = data.get('name', '默认情景')
    
    # 简化模型参数：只保留2个关键参数
    scenario_params = {
        'model_type': data.get('model_type', 'leap'),  # 'leap' 或 'kaya'
        'gdp_growth_rate': data.get('gdp_growth_rate', 0.083),
        'efficiency_improvement_rate': data.get('efficiency_improvement_rate', 0.05)
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

@app.route('/api/predict/status', methods=['POST', 'GET'])
def predict_status():
    """检查预测状态 - 返回已有预测结果的情景列表"""
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

@app.route('/api/predict', methods=['POST'])
def predict():
    """运行预测"""
    data = request.json
    scenario_names = data.get('scenarios', [])
    forecast_years = data.get('forecast_years', 30)
    
    if not scenario_names:
        return jsonify({'error': 'No scenarios selected'}), 400
    
    # 加载基准年数据（使用简化版）
    data_path = os.path.join(DATA_DIR, 'base_year_data.csv')
    if not os.path.exists(data_path):
        return jsonify({'error': 'No data file found'}), 404
    
    processor = SimpleDataProcessor(data_path)
    processor.load_data()
    base_data = processor.get_base_year_data()
    
    # 加载情景参数
    scenarios_file = os.path.join(DATA_DIR, 'scenarios.json')
    with open(scenarios_file, 'r', encoding='utf-8') as f:
        all_scenarios = json.load(f)
    
    # 运行选定的情景（使用简化模型）
    results_dict = {}
    # 固定预测到2060年
    horizon_year = 2060
    
    for scenario_name in scenario_names:
        if scenario_name in all_scenarios:
            scenario_params = all_scenarios[scenario_name]
            results = run_simple_scenario(base_data, scenario_params, horizon_year)
            results_dict[scenario_name] = results
    
    # 获取历史数据
    historical_data = processor.get_historical_data()
    
    # 生成图表
    carbon_peak_path = os.path.join(OUTPUT_DIR, 'carbon_peak.png')
    gdp_path = os.path.join(OUTPUT_DIR, 'gdp.png')
    energy_path = os.path.join(OUTPUT_DIR, 'energy_consumption.png')
    
    try:
        plot_carbon_peak(results_dict, carbon_peak_path, historical_data)
    except Exception as e:
        print(f"生成碳达峰图表失败: {str(e)}")
    
    try:
        plot_gdp(results_dict, gdp_path, historical_data)
    except Exception as e:
        print(f"生成GDP图表失败: {str(e)}")
    
    try:
        plot_energy_consumption(results_dict, energy_path, historical_data)
    except Exception as e:
        print(f"生成能耗图表失败: {str(e)}")
    
    # 保存结果数据
    for scenario_name, results in results_dict.items():
        results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
        results.to_csv(results_path, index=False, encoding='utf-8')
    
    return jsonify({
        'message': 'Prediction completed',
        'carbon_peak_chart': '/api/charts/carbon_peak',
        'gdp_chart': '/api/charts/gdp',
        'energy_consumption_chart': '/api/charts/energy_consumption',
        'scenarios': list(results_dict.keys())
    })

@app.route('/api/charts/<chart_name>', methods=['GET'])
def get_chart(chart_name):
    """获取生成的图表"""
    chart_files = {
        'carbon_peak': 'carbon_peak.png',
        'gdp': 'gdp.png',
        'energy_consumption': 'energy_consumption.png'
    }
    
    if chart_name in chart_files:
        chart_path = os.path.join(OUTPUT_DIR, chart_files[chart_name])
        if os.path.exists(chart_path):
            return send_file(chart_path, mimetype='image/png')
        else:
            return jsonify({'error': 'Chart file not found'}), 404
    else:
        return jsonify({'error': 'Chart not found'}), 404

@app.route('/api/results/<scenario_name>', methods=['GET'])
def get_results(scenario_name):
    """获取预测结果数据（包括历史数据）"""
    results_path = os.path.join(OUTPUT_DIR, f'{scenario_name}_results.csv')
    
    if not os.path.exists(results_path):
        return jsonify({'error': 'Results not found'}), 404
    
    # 读取预测数据
    forecast_results = pd.read_csv(results_path)
    
    # 读取历史数据
    base_data_path = os.path.join(DATA_DIR, 'base_year_data.csv')
    if os.path.exists(base_data_path):
        historical_data = pd.read_csv(base_data_path)
        
        # 统一列名：co2_emission
        if 'co2_emission' not in historical_data.columns and 'co2' in historical_data.columns:
            historical_data['co2_emission'] = historical_data['co2']
        
        # 只保留需要的列
        common_cols = ['year', 'energy_consumption', 'gdp', 'co2_emission']
        hist_cols = [col for col in common_cols if col in historical_data.columns]
        forecast_cols = [col for col in common_cols if col in forecast_results.columns]
        
        # 子集并标注数据源
        historical_subset = historical_data[hist_cols].copy()
        historical_subset['data_type'] = 'historical'
        forecast_subset = forecast_results[forecast_cols].copy()
        forecast_subset['data_type'] = 'forecast'
        
        # 合并数据（历史优先），按年份去重
        combined = pd.concat([historical_subset, forecast_subset], ignore_index=True)
        combined = combined.sort_values('year')
        combined = combined.groupby('year', as_index=False).first()
        
        return jsonify(combined.to_dict(orient='records'))
    else:
        # 没有历史数据，只返回预测数据
        forecast_cols = [col for col in ['year', 'energy_consumption', 'gdp', 'co2_emission'] if col in forecast_results.columns]
        if forecast_cols:
            forecast_subset = forecast_results[forecast_cols].copy()
        else:
            forecast_subset = forecast_results.copy()
        forecast_subset['data_type'] = 'forecast'
        return jsonify(forecast_subset.to_dict(orient='records'))

@app.route('/api/upload/example', methods=['POST'])
def use_example_data():
    """使用示例数据"""
    # 复制示例数据到工作目录
    sample_path = os.path.join(DATA_DIR, 'sample_data.csv')
    target_path = os.path.join(DATA_DIR, 'base_year_data.csv')
    
    try:
        shutil.copy(sample_path, target_path)
        
        # 加载数据验证
        processor = SimpleDataProcessor(target_path)
        data = processor.load_data()
        
        # 读取数据内容
        df = pd.read_csv(target_path)
        
        return jsonify({
            'message': 'Example data loaded successfully',
            'rows': len(data),
            'years': [int(df['year'].min()), int(df['year'].max())],
            'sectors': ['全部'],
            'data': df.to_dict(orient='records')
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
    """获取所有情景的预测数据（包含历史数据），用于前端绘图"""
    try:
        # 加载历史数据
        base_data_path = os.path.join(DATA_DIR, 'base_year_data.csv')
        historical_years = []
        historical_emissions = []
        historical_gdp = []
        historical_energy = []
        
        if os.path.exists(base_data_path):
            historical_df = pd.read_csv(base_data_path)
            # 兼容列名
            if 'co2_emission' not in historical_df.columns and 'co2' in historical_df.columns:
                historical_df['co2_emission'] = historical_df['co2']
            historical_years = historical_df['year'].tolist()
            if 'co2_emission' in historical_df.columns:
                historical_emissions = historical_df['co2_emission'].tolist()
            if 'gdp' in historical_df.columns:
                historical_gdp = historical_df['gdp'].tolist()
            if 'energy_consumption' in historical_df.columns:
                historical_energy = historical_df['energy_consumption'].tolist()
        
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
            if not os.path.exists(results_path):
                continue
                
            # 读取预测结果
            df = pd.read_csv(results_path)
            
            # 处理NaN - 替换为None便JSON序列化
            df = df.where(pd.notna(df), None)
            
            # 确定排放列名
            emission_col = 'co2_emission' if 'co2_emission' in df.columns else 'total_emission'
            
            # 计算峰值
            emissions_series = df[emission_col].dropna()
            if len(emissions_series) > 0:
                peak_idx = emissions_series.idxmax()
                peak_year = int(df.loc[peak_idx, 'year'])
                peak_value = float(df.loc[peak_idx, emission_col])
            else:
                # 如果没有有效数据，使用第一个值
                peak_year = int(df['year'].iloc[0])
                peak_value = 0.0
            
            # 构建返回数据
            scenario_data = {
                'years': df['year'].tolist(),
                'emissions': df[emission_col].tolist(),
                'gdp': df['gdp'].tolist() if 'gdp' in df.columns else [],
                'historical_years': historical_years,
                'historical_emissions': historical_emissions,
                'historical_gdp': historical_gdp,
                'historical_energy': historical_energy,
                'peak': {
                    'year': peak_year,
                    'value': peak_value
                },
                'model_type': scenarios[scenario_name].get('model_type', 'leap'),
                'energy_mix': {
                    'total': df['energy_consumption'].tolist() if 'energy_consumption' in df.columns else []
                }
            }
            
            # 添加可选的能源细分数据
            if 'renewable_energy' in df.columns:
                scenario_data['energy_mix']['renewable'] = df['renewable_energy'].tolist()
            if 'nonrenewable_energy' in df.columns:
                scenario_data['energy_mix']['nonrenewable'] = df['nonrenewable_energy'].tolist()
            
            chart_data[scenario_name] = scenario_data
        
        if not chart_data:
            return jsonify({'error': 'No prediction results available'}), 404
        
        # 使用json.dumps确保None正确转换为null
        return app.response_class(
            response=json.dumps(chart_data, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    # 从环境变量读取配置，默认开发模式
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
