"""Kaya identity model with calibrated intensity decomposition."""

import pandas as pd

from .prediction_utils import (
    carbon_factor_multipliers,
    clamp,
    driver_paths,
    finalize_projection,
    finite_float,
    structure_paths,
)


def _structure_index(renewable_ratio, coal_ratio):
    """Relative CO2/energy pressure from renewable and coal shares."""
    renewable_ratio = clamp(renewable_ratio, 0.0, 0.95)
    coal_ratio = clamp(coal_ratio, 0.02, 0.98)
    return max((1 - renewable_ratio) * (0.58 + 0.42 * coal_ratio), 1e-12)


def run_kaya_model(base_data, params, horizon_year, historical_data=None):
    """
    CO2 = GDP * (Energy/GDP) * (CO2/Energy).

    GDP and energy intensity follow gradual near-to-long-term transitions, while
    carbon intensity is anchored to the base year and adjusted by smooth energy
    structure changes.
    """
    params = params or {}
    base_co2 = max(finite_float(base_data["co2"]), 0.0)
    base_energy = max(finite_float(base_data["energy"]), 1e-12)
    base_renewable = clamp(finite_float(base_data.get("renewable_ratio"), 0.10), 0.0, 0.95)
    base_coal_ratio = clamp(finite_float(base_data.get("coal_ratio"), 0.70), 0.02, 0.98)
    base_carbon_intensity = base_co2 / base_energy

    drivers, indicators = driver_paths(base_data, params, horizon_year, historical_data)
    structures = structure_paths(base_data, params, len(drivers) - 1)
    carbon_multipliers = carbon_factor_multipliers(params, indicators, len(drivers) - 1)

    structure_base = _structure_index(base_renewable, base_coal_ratio)

    rows = []
    for i, driver in drivers.iterrows():
        energy_t = max(float(driver["energy_consumption"]), 0.0)
        renewable_ratio_t = float(structures.loc[i, "renewable_ratio"])
        coal_ratio_t = float(structures.loc[i, "coal_ratio"])
        structure_t = _structure_index(renewable_ratio_t, coal_ratio_t)

        carbon_intensity_t = (
            base_carbon_intensity
            * (structure_t / structure_base)
            * carbon_multipliers[i]
        )

        renewable_energy_t = energy_t * renewable_ratio_t
        nonrenewable_energy_t = energy_t - renewable_energy_t
        coal_energy_t = nonrenewable_energy_t * coal_ratio_t
        other_fossil_energy_t = nonrenewable_energy_t - coal_energy_t

        co2_t = energy_t * carbon_intensity_t
        if i == 0:
            co2_t = base_co2

        rows.append(
            {
                "year": int(driver["year"]),
                "gdp": float(driver["gdp"]),
                "energy_consumption": energy_t,
                "co2_emission": co2_t,
                "renewable_ratio": renewable_ratio_t,
                "renewable_energy": renewable_energy_t,
                "nonrenewable_energy": nonrenewable_energy_t,
                "coal_energy": coal_energy_t,
                "other_fossil_energy": other_fossil_energy_t,
                "coal_ratio": coal_ratio_t,
                "energy_intensity": float(driver["energy_intensity"]),
                "carbon_intensity": carbon_intensity_t,
                "gdp_growth_rate_applied": float(driver["gdp_growth_rate_applied"]),
                "efficiency_improvement_rate_applied": float(
                    driver["efficiency_improvement_rate_applied"]
                ),
                "structure_index": structure_t,
            }
        )

    return finalize_projection(pd.DataFrame(rows), params)
