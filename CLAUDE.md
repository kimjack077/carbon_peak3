# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

碳达峰预测系统 (Carbon Peak Prediction System) - A web application for predicting carbon emission peaks using multiple models (LEAP, Kaya, STIRPAT). Users can create scenarios with different parameters and visualize prediction results.

## Development Commands

### Backend (Flask)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python app.py            # Start development server on port 5000
pytest                   # Run tests
```

### Frontend (Vue.js 2)
```bash
cd frontend
npm install
npm run serve            # Development server on port 8080
npm run build            # Production build to dist/
npm run lint             # ESLint check
npm run test:e2e         # Playwright e2e tests
```

### Full System
- Windows: `start.bat` - launches both backend and frontend
- Linux/Mac: `./start.sh` - launches both with dependency checks

## Architecture

### Backend Structure
- `app.py` - Flask REST API with endpoints for data upload, scenario management, and prediction
- `model/` - Prediction models:
  - `simple_scenario_runner.py` - Unified interface for all models
  - `simplified_leap.py` - LEAP model (energy-demand + fuel-structure dynamics)
  - `simplified_kaya.py` - Kaya identity (GDP × EnergyIntensity × CarbonIntensity)
  - `stirpat_model.py` - STIRPAT with elasticity calibration from historical data
  - `simple_data_processor.py` - CSV data loading and preprocessing
- `utils/plot_results.py` - Matplotlib chart generation
- `data/` - Base year data (CSV) and scenario configurations (JSON)
- `output/` - Generated prediction results and charts

### Frontend Structure
- `src/App.vue` - Main application with three tabs: DataUpload, ScenarioManager, PredictionResults
- `src/components/`:
  - `DataUpload.vue` - CSV upload or use sample data
  - `ScenarioManager.vue` - Create/edit scenarios with model selection and parameters
  - `PredictionResults.vue` - ECharts visualization of carbon peak, GDP, and energy consumption

### API Endpoints
- `POST /api/upload` - Upload CSV data
- `POST /api/upload/example` - Load sample data
- `GET/POST /api/scenarios` - List/create scenarios
- `DELETE /api/scenarios/<name>` - Delete scenario
- `POST /api/predict` - Run prediction for selected scenarios
- `GET /api/chart-data` - Get chart data for frontend
- `GET /api/results/<name>` - Get prediction results

### Required CSV Columns
- `year`, `energy_consumption`, `gdp`, `co2_emission`
- Optional: `renewable_ratio`, `coal_ratio`

### Scenario Parameters
- `model_type`: "leap" | "kaya" | "stirpat"
- `gdp_growth_rate`: GDP annual growth rate (clamped -0.05 to 0.20)
- `efficiency_improvement_rate`: Energy intensity improvement (clamped 0 to 0.15)
- `renewable_increase_rate`: Renewable share increase (clamped 0 to 0.08)
- `coal_decrease_rate`: Coal share decrease (clamped 0 to 0.15)
- STIRPAT-specific: `elasticity_gdp`, `elasticity_energy_intensity`, `elasticity_structure`

### Model Differences
- **LEAP**: Direct activity-based projection with emission factors (coal: 2.66, oil: 2.12, gas: 1.51 tCO2/ton)
- **Kaya**: Decomposes CO2 = GDP × (Energy/GDP) × (CO2/Energy), structure-adjusted carbon intensity
- **STIRPAT**: Log-linear elasticity model, calibrates coefficients from historical data if ≥4 years available

## Key Technical Notes

- Frontend proxy configuration in `vue.config.js` routes `/api` to backend port 5000
- Backend uses matplotlib with 'Agg' backend (non-interactive) for chart generation
- Chinese font support: matplotlib configured with 'SimHei' for Chinese labels
- All numerical parameters are clamped to valid ranges before model execution
- Frontend uses Element UI for components and ECharts for interactive visualizations