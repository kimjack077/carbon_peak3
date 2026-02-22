from flask import Flask, request, jsonify, send_file
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
            if len(emissions_series) > 0:
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
                "peak": {"year": peak_year, "value": peak_value},
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


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", 5000))
    app.run(debug=debug_mode, port=port, host="0.0.0.0")
