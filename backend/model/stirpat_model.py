"""STIRPAT model with log-linear calibration from historical data."""

import numpy as np
import pandas as pd


def _clamp(value, lower, upper):
    return max(lower, min(upper, value))


def _safe_pow(base, exp):
    return max(0.0, base) ** max(0, exp)


def calibrate_elasticity(historical_data):
    """Calibrate elasticity coefficients from historical series."""
    if historical_data is None or len(historical_data) < 4:
        return {
            "elasticity_gdp": 0.85,
            "elasticity_energy_intensity": 0.55,
            "elasticity_structure": 0.35,
        }

    df = historical_data.copy()
    if "renewable_ratio" not in df.columns:
        df["renewable_ratio"] = 0.10
    if "energy_consumption" not in df.columns or "gdp" not in df.columns:
        return {
            "elasticity_gdp": 0.85,
            "elasticity_energy_intensity": 0.55,
            "elasticity_structure": 0.35,
        }

    df = df.replace([np.inf, -np.inf], np.nan).dropna(
        subset=["co2_emission", "gdp", "energy_consumption", "renewable_ratio"]
    )
    if len(df) < 4:
        return {
            "elasticity_gdp": 0.85,
            "elasticity_energy_intensity": 0.55,
            "elasticity_structure": 0.35,
        }

    df["energy_intensity"] = (df["energy_consumption"] / df["gdp"]).clip(lower=1e-12)
    df["dirty_share"] = (1 - df["renewable_ratio"]).clip(lower=1e-6, upper=1.0)

    y = np.log(df["co2_emission"].clip(lower=1e-12).values)
    x = np.column_stack(
        [
            np.ones(len(df)),
            np.log(df["gdp"].clip(lower=1e-12).values),
            np.log(df["energy_intensity"].values),
            np.log(df["dirty_share"].values),
        ]
    )

    try:
        coeffs = np.linalg.lstsq(x, y, rcond=None)[0]
        return {
            "elasticity_gdp": _clamp(float(coeffs[1]), 0.2, 1.4),
            "elasticity_energy_intensity": _clamp(float(coeffs[2]), 0.1, 1.4),
            "elasticity_structure": _clamp(float(coeffs[3]), 0.0, 1.4),
        }
    except Exception:
        return {
            "elasticity_gdp": 0.85,
            "elasticity_energy_intensity": 0.55,
            "elasticity_structure": 0.35,
        }


def run_stirpat_model(base_data, params, horizon_year, historical_data=None):
    """Run STIRPAT with calibrated/overridden elasticities."""
    base_year = int(base_data["year"])
    base_gdp = float(base_data["gdp"])
    base_energy = max(float(base_data["energy"]), 1e-12)
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

    calibrated = calibrate_elasticity(historical_data)
    elasticity_gdp = _clamp(
        float(params.get("elasticity_gdp", calibrated["elasticity_gdp"])), 0.2, 1.4
    )
    elasticity_energy = _clamp(
        float(
            params.get(
                "elasticity_energy_intensity", calibrated["elasticity_energy_intensity"]
            )
        ),
        0.1,
        1.4,
    )
    elasticity_structure = _clamp(
        float(params.get("elasticity_structure", calibrated["elasticity_structure"])),
        0.0,
        1.4,
    )

    base_dirty_share = max(1 - base_renewable, 1e-6)
    results = []

    for t in range(years + 1):
        year = base_year + t

        gdp_t = base_gdp * _safe_pow(1 + gdp_growth, t)
        energy_intensity_t = base_energy_intensity * _safe_pow(1 - efficiency_improvement, t)
        energy_t = max(0.0, gdp_t * energy_intensity_t)

        renewable_ratio_t = _clamp(base_renewable + renewable_increase * t, base_renewable, 0.95)
        dirty_share_t = max(1 - renewable_ratio_t, 1e-6)
        coal_ratio_t = _clamp(
            base_coal_ratio * _safe_pow(1 - coal_decrease, t),
            0.05,
            base_coal_ratio,
        )

        scale_effect = _safe_pow(gdp_t / max(base_gdp, 1e-12), elasticity_gdp)
        efficiency_effect = _safe_pow(
            energy_intensity_t / max(base_energy_intensity, 1e-12), elasticity_energy
        )
        structure_effect = _safe_pow(dirty_share_t / base_dirty_share, elasticity_structure)
        co2_t = base_co2 * scale_effect * efficiency_effect * structure_effect

        if t == 0:
            co2_t = base_co2

        renewable_energy_t = energy_t * renewable_ratio_t
        nonrenewable_energy_t = energy_t - renewable_energy_t
        coal_energy_t = nonrenewable_energy_t * coal_ratio_t
        other_fossil_energy_t = nonrenewable_energy_t - coal_energy_t

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
                "scale_effect": scale_effect,
                "efficiency_effect": efficiency_effect,
                "structure_effect": structure_effect,
                "elasticity_gdp": elasticity_gdp,
                "elasticity_energy_intensity": elasticity_energy,
                "elasticity_structure": elasticity_structure,
            }
        )

    return pd.DataFrame(results)
