"""
Data Processor for Carbon Peak Prediction
Handles CSV data loading and preprocessing
"""

import pandas as pd
import numpy as np


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
            "carbon_intensity": float(last_row["co2_emission"] / last_row["gdp"]),
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

        if len(self.data) < 2:
            return {
                "gdp_growth_rate": 0.0,
                "energy_growth_rate": 0.0,
                "co2_growth_rate": 0.0,
            }

        years = len(self.data) - 1

        gdp_growth = (self.data["gdp"].iloc[-1] / self.data["gdp"].iloc[0]) ** (
            1 / years
        ) - 1
        energy_growth = (
            self.data["energy_consumption"].iloc[-1]
            / self.data["energy_consumption"].iloc[0]
        ) ** (1 / years) - 1
        co2_growth = (
            self.data["co2_emission"].iloc[-1] / self.data["co2_emission"].iloc[0]
        ) ** (1 / years) - 1

        return {
            "gdp_growth_rate": float(gdp_growth),
            "energy_growth_rate": float(energy_growth),
            "co2_growth_rate": float(co2_growth),
        }

    def analyze_trends(self):
        """Analyze historical trends for parameter suggestions"""
        if self.data is None:
            self.load_data()

        growth_rates = self.calculate_growth_rates()

        return {
            "historical_gdp_growth": growth_rates["gdp_growth_rate"],
            "historical_energy_growth": growth_rates["energy_growth_rate"],
            "historical_co2_growth": growth_rates["co2_growth_rate"],
            "suggested_efficiency_rate": max(
                0.02,
                min(
                    0.08,
                    growth_rates["gdp_growth_rate"]
                    - growth_rates["energy_growth_rate"],
                ),
            ),
            "data_years": len(self.data),
            "year_range": [int(self.data["year"].min()), int(self.data["year"].max())],
        }
