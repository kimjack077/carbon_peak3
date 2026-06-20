"""Simplified LEAP-style model with calibrated fuel-structure dynamics."""

import pandas as pd

from .prediction_utils import (
    carbon_factor_multipliers,
    clamp,
    driver_paths,
    finalize_projection,
    finite_float,
    structure_paths,
)


COAL_EMISSION_FACTOR = 2.66
OIL_EMISSION_FACTOR = 2.12
GAS_EMISSION_FACTOR = 1.51
OTHER_FOSSIL_EMISSION_FACTOR = OIL_EMISSION_FACTOR * 0.6 + GAS_EMISSION_FACTOR * 0.4


def _fuel_factor(renewable_ratio, coal_ratio):
    """Relative emission factor for the projected energy mix."""
    renewable_ratio = clamp(renewable_ratio, 0.0, 0.95)
    coal_ratio = clamp(coal_ratio, 0.02, 0.98)
    fossil_share = max(0.0, 1 - renewable_ratio)
    return fossil_share * (
        coal_ratio * COAL_EMISSION_FACTOR
        + (1 - coal_ratio) * OTHER_FOSSIL_EMISSION_FACTOR
    )


def run_leap_model(base_data, params, horizon_year, historical_data=None):
    """
    LEAP-style projection.

    The absolute fuel factors are treated as relative structure weights and are
    calibrated to the base-year CO2/energy intensity. This keeps the model in
    the uploaded data's unit system and removes the artificial base-year jump.
    """
    params = params or {}
    base_co2 = max(finite_float(base_data["co2"]), 0.0)
    base_energy = max(finite_float(base_data["energy"]), 1e-12)
    base_renewable = clamp(finite_float(base_data.get("renewable_ratio"), 0.10), 0.0, 0.95)
    base_coal_ratio = clamp(finite_float(base_data.get("coal_ratio"), 0.70), 0.02, 0.98)

    drivers, indicators = driver_paths(base_data, params, horizon_year, historical_data)
    structures = structure_paths(base_data, params, len(drivers) - 1)
    carbon_multipliers = carbon_factor_multipliers(params, indicators, len(drivers) - 1)

    base_factor = max(_fuel_factor(base_renewable, base_coal_ratio), 1e-12)
    calibration = (base_co2 / base_energy) / base_factor

    rows = []
    for i, driver in drivers.iterrows():
        energy_t = max(float(driver["energy_consumption"]), 0.0)
        renewable_ratio_t = float(structures.loc[i, "renewable_ratio"])
        coal_ratio_t = float(structures.loc[i, "coal_ratio"])

        renewable_energy_t = energy_t * renewable_ratio_t
        nonrenewable_energy_t = energy_t - renewable_energy_t
        coal_energy_t = nonrenewable_energy_t * coal_ratio_t
        other_fossil_energy_t = nonrenewable_energy_t - coal_energy_t

        co2_t = calibration * carbon_multipliers[i] * (
            coal_energy_t * COAL_EMISSION_FACTOR
            + other_fossil_energy_t * OTHER_FOSSIL_EMISSION_FACTOR
        )
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
                "carbon_intensity": co2_t / max(energy_t, 1e-12),
                "gdp_growth_rate_applied": float(driver["gdp_growth_rate_applied"]),
                "efficiency_improvement_rate_applied": float(
                    driver["efficiency_improvement_rate_applied"]
                ),
                "fuel_factor_index": _fuel_factor(renewable_ratio_t, coal_ratio_t),
            }
        )

    return finalize_projection(pd.DataFrame(rows), params)
