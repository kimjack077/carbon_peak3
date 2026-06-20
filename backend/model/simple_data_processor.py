"""
Data Processor for Carbon Peak Prediction
Handles CSV data loading and preprocessing
"""

import pandas as pd

from .prediction_utils import clamp, historical_indicators


class SimpleDataProcessor:
    """Process historical data for carbon peak prediction"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        """Load CSV data with validation"""
        self.data = pd.read_csv(self.file_path)

        if "co2_emission" not in self.data.columns and "co2" in self.data.columns:
            self.data["co2_emission"] = self.data["co2"]

        required_cols = ["year", "energy_consumption", "gdp", "co2_emission"]
        missing_cols = [col for col in required_cols if col not in self.data.columns]

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        if "renewable_ratio" not in self.data.columns:
            self.data["renewable_ratio"] = 0.05

        if "coal_ratio" not in self.data.columns:
            self.data["coal_ratio"] = 0.75

        numeric_cols = required_cols + ["renewable_ratio", "coal_ratio"]
        for col in numeric_cols:
            self.data[col] = pd.to_numeric(self.data[col], errors="coerce")

        invalid_cols = [
            col for col in required_cols if self.data[col].isna().any()
        ]
        if invalid_cols:
            raise ValueError(f"Invalid numeric values in columns: {invalid_cols}")

        self.data = self.data.dropna(subset=required_cols)
        if self.data.empty:
            raise ValueError("No valid data rows found")

        if (self.data[["energy_consumption", "gdp", "co2_emission"]] <= 0).any().any():
            raise ValueError("energy_consumption, gdp and co2_emission must be positive")

        self.data["renewable_ratio"] = self.data["renewable_ratio"].fillna(0.05).clip(0, 0.95)
        self.data["coal_ratio"] = self.data["coal_ratio"].fillna(0.75).clip(0.02, 0.98)
        self.data = self.data.sort_values("year").reset_index(drop=True)

        return self.data

    def get_base_year_data(self):
        """Get base year (last year) data for prediction"""
        if self.data is None:
            self.load_data()

        last_row = self.data.iloc[-1]
        base_year = int(last_row["year"])

        return {
            "year": base_year,
            "energy": float(last_row["energy_consumption"]),
            "gdp": float(last_row["gdp"]),
            "co2": float(last_row["co2_emission"]),
            "renewable_ratio": float(last_row.get("renewable_ratio", 0.05)),
            "coal_ratio": float(last_row.get("coal_ratio", 0.75)),
            "energy_intensity": float(last_row["energy_consumption"] / last_row["gdp"]),
            "carbon_intensity": float(
                last_row["co2_emission"] / last_row["energy_consumption"]
            ),
            "co2_intensity": float(last_row["co2_emission"] / last_row["gdp"]),
        }

    def get_historical_data(self):
        """Get all historical data"""
        if self.data is None:
            self.load_data()

        return {
            "years": self.data["year"].tolist(),
            "energy": self.data["energy_consumption"].tolist(),
            "gdp": self.data["gdp"].tolist(),
            "co2": self.data["co2_emission"].tolist(),
            "renewable_ratio": self.data["renewable_ratio"].tolist()
            if "renewable_ratio" in self.data.columns
            else [0.05] * len(self.data),
            "coal_ratio": self.data["coal_ratio"].tolist()
            if "coal_ratio" in self.data.columns
            else [0.75] * len(self.data),
        }

    def get_historical_dataframe(self):
        """Get historical data as DataFrame for model calibration"""
        if self.data is None:
            self.load_data()
        return self.data.copy()

    def calculate_growth_rates(self):
        """Calculate historical growth rates"""
        if self.data is None:
            self.load_data()

        indicators = historical_indicators(self.data, self.get_base_year_data())

        return {
            "gdp_growth_rate": float(indicators["gdp_growth_rate"]),
            "energy_growth_rate": float(indicators["energy_growth_rate"]),
            "co2_growth_rate": float(indicators["co2_growth_rate"]),
        }

    def analyze_trends(self):
        """Analyze historical trends for parameter suggestions"""
        if self.data is None:
            self.load_data()

        growth_rates = self.calculate_growth_rates()
        indicators = historical_indicators(self.data, self.get_base_year_data())

        return {
            "historical_gdp_growth": growth_rates["gdp_growth_rate"],
            "historical_energy_growth": growth_rates["energy_growth_rate"],
            "historical_co2_growth": growth_rates["co2_growth_rate"],
            "suggested_gdp_growth_rate": clamp(
                growth_rates["gdp_growth_rate"] * 0.85, 0.02, 0.08
            ),
            "suggested_efficiency_rate": clamp(
                indicators["energy_intensity_improvement_rate"], 0.02, 0.06
            ),
            "suggested_renewable_increase_rate": clamp(
                indicators["renewable_increase_rate"], 0.005, 0.03
            ),
            "suggested_coal_decrease_rate": clamp(
                indicators["coal_decrease_rate"], 0.005, 0.04
            ),
            "data_years": len(self.data),
            "year_range": [int(self.data["year"].min()), int(self.data["year"].max())],
        }
