from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import pandas as pd
import os
import json
import matplotlib
import shutil

matplotlib.use("Agg")

from model.simple_data_processor import SimpleDataProcessor
from model.simple_scenario_runner import run_simple_scenario, get_model_description
from utils.plot_results import plot_carbon_peak, plot_gdp, plot_energy_consumption
from utils.export_utils import generate_excel_report, generate_summary_text

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def _clamp(value, lower, upper):
    return max(lower, min(upper, value))


@app.route("/api/upload", methods=["POST"])
def upload_data():
    """Upload base year data"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(DATA_DIR, "base_year_data.csv")
    file.save(file_path)

    try:
        processor = SimpleDataProcessor(file_path)
        data = processor.load_data()
        return jsonify({"message": "File uploaded successfully", "rows": len(data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scenarios", methods=["POST"])
def create_scenario():
    """Create prediction scenario with all parameters"""
    data = request.json

    scenario_name = data.get("name", "默认情景")

    scenario_params = {
        "model_type": str(data.get("model_type", "leap")).lower(),
        "gdp_growth_rate": _clamp(float(data.get("gdp_growth_rate", 0.05)), -0.05, 0.20),
        "efficiency_improvement_rate": _clamp(
            float(data.get("efficiency_improvement_rate", 0.03)), 0.0, 0.15
        ),
        "renewable_increase_rate": _clamp(
            float(data.get("renewable_increase_rate", 0.01)), 0.0, 0.08
        ),
        "coal_decrease_rate": _clamp(float(data.get("coal_decrease_rate", 0.02)), 0.0, 0.15),
    }

    if scenario_params["model_type"] == "stirpat":
        if "elasticity_gdp" in data:
            scenario_params["elasticity_gdp"] = _clamp(float(data["elasticity_gdp"]), 0.2, 1.4)
        if "elasticity_energy_intensity" in data:
            scenario_params["elasticity_energy_intensity"] = _clamp(
                float(data["elasticity_energy_intensity"]), 0.1, 1.4
            )
        if "elasticity_structure" in data:
            scenario_params["elasticity_structure"] = _clamp(
                float(data["elasticity_structure"]), 0.0, 1.4
            )

    scenarios_file = os.path.join(DATA_DIR, "scenarios.json")

    if os.path.exists(scenarios_file):
        with open(scenarios_file, "r", encoding="utf-8") as f:
            scenarios = json.load(f)
    else:
        scenarios = {}

    scenarios[scenario_name] = scenario_params

    with open(scenarios_file, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    return jsonify(
        {
            "message": "Scenario created successfully",
            "scenario_name": scenario_name,
            "params": scenario_params,
        }
    )


@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    """Get all scenarios"""
    scenarios_file = os.path.join(DATA_DIR, "scenarios.json")

    if not os.path.exists(scenarios_file):
        return jsonify([])

    with open(scenarios_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    return jsonify(scenarios)


@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available prediction models"""
    models = [
        {
            "id": "leap",
            "name": "LEAP模型",
            "description": get_model_description("leap"),
            "best_for": "能源结构分析、政策评估",
        },
        {
            "id": "kaya",
            "name": "Kaya恒等式",
            "description": get_model_description("kaya"),
            "best_for": "碳排放驱动因素分析",
        },
        {
            "id": "stirpat",
            "name": "STIRPAT模型",
            "description": get_model_description("stirpat"),
            "best_for": "弹性分析、情景预测",
        },
    ]
    return jsonify(models)


@app.route("/api/scenarios/<scenario_name>", methods=["DELETE"])
def delete_scenario(scenario_name):
    """Delete scenario"""
    scenarios_file = os.path.join(DATA_DIR, "scenarios.json")

    if not os.path.exists(scenarios_file):
        return jsonify({"error": "No scenarios file found"}), 404

    try:
        with open(scenarios_file, "r", encoding="utf-8") as f:
            scenarios = json.load(f)

        if scenario_name not in scenarios:
            return jsonify({"error": "Scenario not found"}), 404

        del scenarios[scenario_name]

        with open(scenarios_file, "w", encoding="utf-8") as f:
            json.dump(scenarios, f, ensure_ascii=False, indent=2)

        results_path = os.path.join(OUTPUT_DIR, f"{scenario_name}_results.csv")
        if os.path.exists(results_path):
            os.remove(results_path)

        return jsonify(
            {"message": "Scenario deleted successfully", "scenario_name": scenario_name}
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict/status", methods=["POST", "GET"])
def predict_status():
    """Check prediction status"""
    scenarios_file = os.path.join(DATA_DIR, "scenarios.json")

    if not os.path.exists(scenarios_file):
        return jsonify({"scenarios": []})

    with open(scenarios_file, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    available_scenarios = []
    for scenario_name in scenarios:
        results_path = os.path.join(OUTPUT_DIR, f"{scenario_name}_results.csv")
        if os.path.exists(results_path):
            available_scenarios.append(scenario_name)

    return jsonify({"scenarios": available_scenarios})


@app.route("/api/predict", methods=["POST"])
def predict():
    """Run prediction for selected scenarios"""
    data = request.json
    scenario_names = data.get("scenarios", [])
    forecast_years = int(data.get("forecast_years", 30))
    forecast_years = int(_clamp(forecast_years, 1, 100))

    if not scenario_names:
        return jsonify({"error": "No scenarios selected"}), 400

    data_path = os.path.join(DATA_DIR, "base_year_data.csv")
    if not os.path.exists(data_path):
        return jsonify({"error": "No data file found"}), 404

    processor = SimpleDataProcessor(data_path)
    processor.load_data()
    base_data = processor.get_base_year_data()
    historical_df = processor.get_historical_dataframe()

    scenarios_file = os.path.join(DATA_DIR, "scenarios.json")
    with open(scenarios_file, "r", encoding="utf-8") as f:
        all_scenarios = json.load(f)

    results_dict = {}
    horizon_year = int(base_data["year"]) + forecast_years

    for scenario_name in scenario_names:
        if scenario_name in all_scenarios:
            scenario_params = all_scenarios[scenario_name]
            results = run_simple_scenario(
                base_data,
                scenario_params,
                horizon_year,
                historical_df,
            )
            results_dict[scenario_name] = results

    historical_data = processor.get_historical_data()

    carbon_peak_path = os.path.join(OUTPUT_DIR, "carbon_peak.png")
    gdp_path = os.path.join(OUTPUT_DIR, "gdp.png")
    energy_path = os.path.join(OUTPUT_DIR, "energy_consumption.png")

    try:
        plot_carbon_peak(results_dict, carbon_peak_path, historical_data)
    except Exception as e:
        print(f"Failed to generate carbon peak chart: {str(e)}")

    try:
        plot_gdp(results_dict, gdp_path, historical_data)
    except Exception as e:
        print(f"Failed to generate GDP chart: {str(e)}")

    try:
        plot_energy_consumption(results_dict, energy_path, historical_data)
    except Exception as e:
        print(f"Failed to generate energy chart: {str(e)}")

    for scenario_name, results in results_dict.items():
        results_path = os.path.join(OUTPUT_DIR, f"{scenario_name}_results.csv")
        results.to_csv(results_path, index=False, encoding="utf-8")

    return jsonify(
        {
            "message": "Prediction completed",
            "carbon_peak_chart": "/api/charts/carbon_peak",
            "gdp_chart": "/api/charts/gdp",
            "energy_consumption_chart": "/api/charts/energy_consumption",
            "scenarios": list(results_dict.keys()),
        }
    )


@app.route("/api/charts/<chart_name>", methods=["GET"])
def get_chart(chart_name):
    """Get generated chart"""
    chart_files = {
        "carbon_peak": "carbon_peak.png",
        "gdp": "gdp.png",
        "energy_consumption": "energy_consumption.png",
    }

    if chart_name in chart_files:
        chart_path = os.path.join(OUTPUT_DIR, chart_files[chart_name])
        if os.path.exists(chart_path):
            return send_file(chart_path, mimetype="image/png")
        else:
            return jsonify({"error": "Chart file not found"}), 404
    else:
        return jsonify({"error": "Chart not found"}), 404


@app.route("/api/results/<scenario_name>", methods=["GET"])
def get_results(scenario_name):
    """Get prediction results"""
    results_path = os.path.join(OUTPUT_DIR, f"{scenario_name}_results.csv")

    if not os.path.exists(results_path):
        return jsonify({"error": "Results not found"}), 404

    forecast_results = pd.read_csv(results_path)

    base_data_path = os.path.join(DATA_DIR, "base_year_data.csv")
    if os.path.exists(base_data_path):
        historical_data = pd.read_csv(base_data_path)

        if (
            "co2_emission" not in historical_data.columns
            and "co2" in historical_data.columns
        ):
            historical_data["co2_emission"] = historical_data["co2"]

        common_cols = ["year", "energy_consumption", "gdp", "co2_emission"]
        hist_cols = [col for col in common_cols if col in historical_data.columns]
        forecast_cols = [col for col in common_cols if col in forecast_results.columns]

        historical_subset = historical_data[hist_cols].copy()
        historical_subset["data_type"] = "historical"
        forecast_subset = forecast_results[forecast_cols].copy()
        forecast_subset["data_type"] = "forecast"

        combined = pd.concat([historical_subset, forecast_subset], ignore_index=True)
        combined = combined.sort_values("year")
        combined = combined.groupby("year", as_index=False).first()

        return jsonify(combined.to_dict(orient="records"))
    else:
        forecast_cols = [
            col
            for col in ["year", "energy_consumption", "gdp", "co2_emission"]
            if col in forecast_results.columns
        ]
        if forecast_cols:
            forecast_subset = forecast_results[forecast_cols].copy()
        else:
            forecast_subset = forecast_results.copy()
        forecast_subset["data_type"] = "forecast"
        return jsonify(forecast_subset.to_dict(orient="records"))


@app.route("/api/upload/example", methods=["POST"])
def use_example_data():
    """Use example data"""
    sample_path = os.path.join(DATA_DIR, "sample_data.csv")
    target_path = os.path.join(DATA_DIR, "base_year_data.csv")

    try:
        shutil.copy(sample_path, target_path)

        processor = SimpleDataProcessor(target_path)
        data = processor.load_data()

        df = pd.read_csv(target_path)

        return jsonify(
            {
                "message": "Example data loaded successfully",
                "rows": len(data),
                "years": [int(df["year"].min()), int(df["year"].max())],
                "sectors": ["全部"],
                "data": df.to_dict(orient="records"),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/results/<scenario_name>/download", methods=["GET"])
def download_results(scenario_name):
    """Download prediction results"""
    results_path = os.path.join(OUTPUT_DIR, f"{scenario_name}_results.csv")

    if not os.path.exists(results_path):
        return jsonify({"error": "Results not found"}), 404

    return send_file(
        results_path,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{scenario_name}_results.csv",
    )


@app.route("/api/chart-data", methods=["GET"])
def get_chart_data():
    """Get chart data for frontend rendering"""
    try:
        base_data_path = os.path.join(DATA_DIR, "base_year_data.csv")
        historical_years = []
        historical_emissions = []
        historical_gdp = []
        historical_energy = []

        if os.path.exists(base_data_path):
            historical_df = pd.read_csv(base_data_path)
            if (
                "co2_emission" not in historical_df.columns
                and "co2" in historical_df.columns
            ):
                historical_df["co2_emission"] = historical_df["co2"]
            historical_years = historical_df["year"].tolist()
            if "co2_emission" in historical_df.columns:
                historical_emissions = historical_df["co2_emission"].tolist()
            if "gdp" in historical_df.columns:
                historical_gdp = historical_df["gdp"].tolist()
            if "energy_consumption" in historical_df.columns:
                historical_energy = historical_df["energy_consumption"].tolist()

        scenarios_file = os.path.join(DATA_DIR, "scenarios.json")
        if not os.path.exists(scenarios_file):
            return jsonify({"error": "No scenarios available"}), 404

        with open(scenarios_file, "r", encoding="utf-8") as f:
            scenarios = json.load(f)

        chart_data = {}

        for scenario_name in scenarios:
            results_path = os.path.join(OUTPUT_DIR, f"{scenario_name}_results.csv")
            if not os.path.exists(results_path):
                continue

            df = pd.read_csv(results_path)

            df = df.where(pd.notna(df), None)

            emission_col = (
                "co2_emission" if "co2_emission" in df.columns else "total_emission"
            )

            emissions_series = df[emission_col].dropna()
            peak_status = "unknown"
            if "is_peak" in df.columns and df["is_peak"].fillna(False).astype(bool).any():
                peak_idx = df.index[df["is_peak"].fillna(False).astype(bool)][0]
                peak_year = int(df.loc[peak_idx, "year"])
                peak_value = float(df.loc[peak_idx, emission_col])
                peak_status = "model_marked"
            elif len(emissions_series) > 0:
                peak_idx = emissions_series.idxmax()
                peak_year = int(df.loc[peak_idx, "year"])
                peak_value = float(df.loc[peak_idx, emission_col])
            else:
                peak_year = int(df["year"].iloc[0])
                peak_value = 0.0

            scenario_data = {
                "years": df["year"].tolist(),
                "emissions": df[emission_col].tolist(),
                "gdp": df["gdp"].tolist() if "gdp" in df.columns else [],
                "historical_years": historical_years,
                "historical_emissions": historical_emissions,
                "historical_gdp": historical_gdp,
                "historical_energy": historical_energy,
                "peak": {"year": peak_year, "value": peak_value, "status": peak_status},
                "model_type": scenarios[scenario_name].get("model_type", "leap"),
                "energy_mix": {
                    "total": df["energy_consumption"].tolist()
                    if "energy_consumption" in df.columns
                    else []
                },
            }

            if "renewable_energy" in df.columns:
                scenario_data["energy_mix"]["renewable"] = df[
                    "renewable_energy"
                ].tolist()
            if "nonrenewable_energy" in df.columns:
                scenario_data["energy_mix"]["nonrenewable"] = df[
                    "nonrenewable_energy"
                ].tolist()
            if "coal_energy" in df.columns:
                scenario_data["energy_mix"]["coal"] = df["coal_energy"].tolist()
            if "other_fossil_energy" in df.columns:
                scenario_data["energy_mix"]["other_fossil"] = df[
                    "other_fossil_energy"
                ].tolist()

            chart_data[scenario_name] = scenario_data

        if not chart_data:
            return jsonify({"error": "No prediction results available"}), 404

        return app.response_class(
            response=json.dumps(chart_data, ensure_ascii=False),
            status=200,
            mimetype="application/json",
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/trends", methods=["GET"])
def get_trends():
    """Get historical data analysis and suggested parameters"""
    try:
        data_path = os.path.join(DATA_DIR, "base_year_data.csv")
        if not os.path.exists(data_path):
            return jsonify({"error": "No data available"}), 404

        processor = SimpleDataProcessor(data_path)
        processor.load_data()
        trends = processor.analyze_trends()

        return jsonify(trends)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload/custom", methods=["POST"])
def upload_custom_data():
    """Upload custom data (supports CSV and Excel)"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = file.filename.lower()
    data_path = os.path.join(DATA_DIR, "base_year_data.csv")

    try:
        # 根据文件类型读取数据
        if filename.endswith(('.xlsx', '.xls')):
            # Excel文件先转为CSV保存
            df = pd.read_excel(file)
            df.to_csv(data_path, index=False)
        elif filename.endswith('.csv'):
            file.save(data_path)
            df = pd.read_csv(data_path)
        else:
            return jsonify({"error": "不支持的文件格式，请上传CSV或Excel文件"}), 400

        # 标准化列名
        df.columns = [col.strip().lower() for col in df.columns]

        # 列名映射
        col_mapping = {
            '年份': 'year', '年': 'year',
            'gdp': 'gdp', '生产总值': 'gdp', '国内生产总值': 'gdp',
            '能源消费': 'energy_consumption', '能耗': 'energy_consumption', '能源消耗': 'energy_consumption',
            'co2排放': 'co2_emission', '碳排放': 'co2_emission', 'co2': 'co2_emission', '二氧化碳': 'co2_emission',
            '可再生能源占比': 'renewable_ratio', '可再生能源': 'renewable_ratio', '新能源占比': 'renewable_ratio'
        }

        df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
        df.to_csv(data_path, index=False)

        processor = SimpleDataProcessor(data_path)
        data = processor.load_data()

        # 获取部门信息
        sectors = []
        if "sector" in df.columns:
            sectors = df["sector"].unique().tolist()[:10]

        return jsonify({
            "message": "数据上传成功",
            "rows": len(data),
            "years": [int(df["year"].min()), int(df["year"].max())],
            "sectors": sectors,
            "data": df.head(10).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/current", methods=["GET"])
def get_current_data():
    """获取当前加载的数据"""
    data_path = os.path.join(DATA_DIR, "base_year_data.csv")
    if not os.path.exists(data_path):
        return jsonify({"rows": 0, "data": []})

    try:
        df = pd.read_csv(data_path)
        # 获取部门信息（如果有sector列）
        sectors = []
        if "sector" in df.columns:
            sectors = df["sector"].unique().tolist()[:10]

        return jsonify({
            "rows": len(df),
            "years": [int(df["year"].min()), int(df["year"].max())],
            "sectors": sectors,
            "data": df.head(10).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/sample", methods=["GET"])
def download_sample():
    """下载样例数据文件"""
    sample_data = {
        "year": [2018, 2019, 2020, 2021, 2022, 2023],
        "gdp": [50000, 54000, 52000, 57000, 61000, 65000],
        "energy_consumption": [3200, 3350, 3280, 3450, 3580, 3700],
        "co2_emission": [5200, 5400, 5100, 5500, 5700, 5850],
        "renewable_ratio": [0.08, 0.10, 0.12, 0.14, 0.16, 0.18]
    }
    df = pd.DataFrame(sample_data)

    # 保存为Excel
    output_path = os.path.join(DATA_DIR, "sample_data.xlsx")
    df.to_excel(output_path, index=False, sheet_name="基础数据")

    return send_file(
        output_path,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="碳达峰预测_样例数据.xlsx"
    )


@app.route("/api/data/validate", methods=["POST"])
def validate_data():
    """Validate uploaded data structure"""
    try:
        data = request.json
        required_cols = ["year", "gdp", "energy_consumption", "co2_emission"]

        if not data or "columns" not in data:
            return jsonify({"valid": False, "error": "No column data provided"}), 400

        columns = [col.lower() for col in data.get("columns", [])]
        missing = [col for col in required_cols if col not in columns]

        if missing:
            return jsonify({
                "valid": False,
                "error": f"Missing required columns: {missing}"
            })

        return jsonify({"valid": True, "message": "Data structure is valid"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/excel/<name>", methods=["GET"])
def export_excel(name):
    """Export Excel format prediction results"""
    try:
        results_path = os.path.join(OUTPUT_DIR, f"{name}_results.csv")
        if not os.path.exists(results_path):
            return jsonify({"error": "Results not found"}), 404

        results_df = pd.read_csv(results_path)
        results = results_df.to_dict(orient="records")
        excel_data = generate_excel_report(results, name)

        response = make_response(excel_data)
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers["Content-Disposition"] = f"attachment; filename={name}_预测结果.xlsx"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/export/pdf/<name>", methods=["GET"])
def export_pdf(name):
    """Export PDF format prediction report"""
    try:
        results_path = os.path.join(OUTPUT_DIR, f"{name}_results.csv")
        if not os.path.exists(results_path):
            return jsonify({"error": "Results not found"}), 404

        results_df = pd.read_csv(results_path)
        results = results_df.to_dict(orient="records")

        # 简化版：返回JSON让前端生成PDF
        summary = generate_summary_text(results, {})

        return jsonify({
            "summary": summary,
            "scenario": name,
            "data": results[:10]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/recommend/parameters", methods=["GET"])
def recommend_parameters():
    """智能参数推荐"""
    try:
        data_path = os.path.join(DATA_DIR, "base_year_data.csv")
        if not os.path.exists(data_path):
            return jsonify({
                "gdp_growth_rate": 0.05,
                "efficiency_improvement_rate": 0.03,
                "renewable_increase_rate": 0.01,
                "coal_decrease_rate": 0.02,
                "gdp_reason": "数据不足，采用默认推荐值",
                "efficiency_reason": "数据不足，采用默认推荐值",
                "sensitivity": [0.05, 0.03, 0.01, 0.02]
            })

        df = pd.read_csv(data_path)

        if len(df) >= 4:
            years = df["year"].tolist()
            gdps = df["gdp"].tolist()
            energies = df["energy_consumption"].tolist()

            # 计算GDP平均增长率
            gdp_growth = sum((gdps[i+1]/gdps[i] - 1) for i in range(len(gdps)-1)) / (len(gdps)-1)

            # 计算效率改善率
            intensities = [e/g for e, g in zip(energies, gdps)]
            efficiency_improve = sum((intensities[i] - intensities[i+1])/intensities[i]
                                    for i in range(len(intensities)-1)) / (len(intensities)-1)

            recommendations = {
                "gdp_growth_rate": round(gdp_growth * 0.9, 4),
                "efficiency_improvement_rate": round(max(efficiency_improve, 0.02), 4),
                "renewable_increase_rate": 0.015,
                "coal_decrease_rate": 0.02,
                "gdp_reason": f"基于历史{len(years)}年数据趋势，建议采用略保守的增长率",
                "efficiency_reason": "历史能效改善趋势良好，建议维持或加强",
                "sensitivity": [gdp_growth, efficiency_improve, 0.015, 0.02]
            }
        else:
            recommendations = {
                "gdp_growth_rate": 0.05,
                "efficiency_improvement_rate": 0.03,
                "renewable_increase_rate": 0.01,
                "coal_decrease_rate": 0.02,
                "gdp_reason": "数据不足，采用默认推荐值",
                "efficiency_reason": "数据不足，采用默认推荐值",
                "sensitivity": [0.05, 0.03, 0.01, 0.02]
            }

        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scenarios/compare", methods=["POST"])
def compare_scenarios():
    """情景对比分析"""
    try:
        data = request.json
        scenario_names = data.get("scenarios", [])

        if len(scenario_names) < 2:
            return jsonify({"error": "至少需要选择2个情景进行对比"}), 400

        comparison_data = {
            "peak_years": [],
            "paths": [],
            "indicators": [],
            "years": [],
            "report": {
                "summary": f"对比分析了 {len(scenario_names)} 个情景的碳排放路径差异",
                "details": []
            }
        }

        all_years = set()

        for name in scenario_names:
            results_path = os.path.join(OUTPUT_DIR, f"{name}_results.csv")
            if not os.path.exists(results_path):
                continue

            results_df = pd.read_csv(results_path)
            results = results_df.to_dict(orient="records")

            # 找峰值年份
            emission_col = "co2_emission" if "co2_emission" in results_df.columns else "total_emission"
            emissions = results_df[emission_col].tolist()

            if emissions:
                peak_idx = emissions.index(max(emissions))
                peak_year = int(results_df.loc[peak_idx, "year"])
                peak_value = emissions[peak_idx]

                comparison_data["peak_years"].append(peak_year)
                comparison_data["paths"].append(emissions)
                comparison_data["report"]["details"].append({
                    "scenario": name,
                    "peak_year": peak_year,
                    "peak_value": f"{peak_value:.2f}",
                    "reduction_rate": f"{((emissions[0] - emissions[-1])/emissions[0]*100):.1f}%"
                })

                # 关键指标评分
                comparison_data["indicators"].append([
                    100 - peak_year + 2020,
                    80,
                    70,
                    75
                ])

            for r in results:
                all_years.add(int(r["year"]))

        comparison_data["years"] = sorted(list(all_years))

        return jsonify(comparison_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scenarios/copy", methods=["POST"])
def copy_scenario():
    """复制情景"""
    try:
        data = request.json
        source_name = data.get("source")
        new_name = data.get("name")

        if not source_name or not new_name:
            return jsonify({"error": "需要提供源情景名和新情景名"}), 400

        scenarios_file = os.path.join(DATA_DIR, "scenarios.json")
        if not os.path.exists(scenarios_file):
            return jsonify({"error": "情景文件不存在"}), 404

        with open(scenarios_file, "r", encoding="utf-8") as f:
            scenarios = json.load(f)

        if source_name not in scenarios:
            return jsonify({"error": "源情景不存在"}), 404

        scenarios[new_name] = {**scenarios[source_name]}
        save_scenarios(scenarios)

        return jsonify({"success": True, "name": new_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def save_scenarios(scenarios):
    """保存情景到文件"""
    scenarios_file = os.path.join(DATA_DIR, "scenarios.json")
    with open(scenarios_file, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)


def get_scenario_results(name):
    """获取情景预测结果"""
    results_path = os.path.join(OUTPUT_DIR, f"{name}_results.csv")
    if not os.path.exists(results_path):
        return []

    df = pd.read_csv(results_path)
    return df.to_dict(orient="records")


def load_current_data():
    """加载当前数据"""
    data_path = os.path.join(DATA_DIR, "base_year_data.csv")
    if not os.path.exists(data_path):
        return []

    df = pd.read_csv(data_path)
    return df.to_dict(orient="records")


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(debug=debug_mode, port=port, host="0.0.0.0")
