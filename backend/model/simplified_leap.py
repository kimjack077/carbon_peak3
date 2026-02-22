"""Simplified LEAP-style model with energy-demand and fuel-structure dynamics."""

import pandas as pd


COAL_EMISSION_FACTOR = 2.66
OIL_EMISSION_FACTOR = 2.12
GAS_EMISSION_FACTOR = 1.51
OTHER_FOSSIL_EMISSION_FACTOR = OIL_EMISSION_FACTOR * 0.6 + GAS_EMISSION_FACTOR * 0.4


def _clamp(value, lower, upper):
    return max(lower, min(upper, value))


def _safe_pow(base, exp):
    return max(0.0, base) ** max(0, exp)


def run_leap_model(base_data, params, horizon_year):
    """
    LEAP-style projection:
    1) GDP growth drives activity;
    2) Energy intensity decline captures efficiency improvement;
    3) Energy structure transition determines carbon factors.
    """
    base_year = int(base_data["year"])
    base_gdp = float(base_data["gdp"])
    base_energy = float(base_data["energy"])
    base_co2 = float(base_data["co2"])
    base_renewable = _clamp(float(base_data.get("renewable_ratio", 0.10)), 0.0, 0.95)
    base_coal_ratio = _clamp(float(base_data.get("coal_ratio", 0.70)), 0.05, 0.95)
    base_energy_intensity = max(float(base_data["energy_intensity"]), 1e-12)
    years = max(0, int(horizon_year) - base_year)

    gdp_growth = _clamp(float(params.get("gdp_growth_rate", 0.05)), -0.05, 0.20)
    efficiency_improvement = _clamp(
        float(params.get("efficiency_improvement_rate", 0.03)), 0.0, 0.15
    )
    renewable_increase = _clamp(float(params.get("renewable_increase_rate", 0.01)), 0.0, 0.08)
    coal_decrease = _clamp(float(params.get("coal_decrease_rate", 0.02)), 0.0, 0.15)

    results = []
    for t in range(years + 1):
        year = base_year + t
        gdp_t = base_gdp * _safe_pow(1 + gdp_growth, t)
        energy_intensity_t = base_energy_intensity * _safe_pow(1 - efficiency_improvement, t)
        energy_t = max(0.0, gdp_t * energy_intensity_t)

        renewable_ratio_t = _clamp(base_renewable + renewable_increase * t, base_renewable, 0.95)
        coal_ratio_t = _clamp(
            base_coal_ratio * _safe_pow(1 - coal_decrease, t),
            0.05,
            base_coal_ratio,
        )

        renewable_energy_t = energy_t * renewable_ratio_t
        nonrenewable_energy_t = energy_t - renewable_energy_t
        coal_energy_t = nonrenewable_energy_t * coal_ratio_t
        other_fossil_energy_t = nonrenewable_energy_t - coal_energy_t

        co2_t = (
            coal_energy_t * COAL_EMISSION_FACTOR
            + other_fossil_energy_t * OTHER_FOSSIL_EMISSION_FACTOR
        )
        if t == 0:
            co2_t = base_co2

        results.append(
            {
                "year": year,
                "gdp": gdp_t,
                "energy_consumption": energy_t,
                "co2_emission": co2_t,
                "renewable_ratio": renewable_ratio_t,
                "renewable_energy": renewable_energy_t,
                "nonrenewable_energy": nonrenewable_energy_t,
                "coal_energy": coal_energy_t,
                "other_fossil_energy": other_fossil_energy_t,
                "coal_ratio": coal_ratio_t,
                "energy_intensity": energy_intensity_t,
                "carbon_intensity": co2_t / max(energy_t, 1e-12),
            }
        )

    df = pd.DataFrame(results)
    return df
