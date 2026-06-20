"""Shared calibration helpers for carbon peak projection models."""

import math

import numpy as np
import pandas as pd


def clamp(value, lower, upper):
    """Clamp numeric values while tolerating malformed input."""
    if lower > upper:
        lower, upper = upper, lower
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = lower
    if not math.isfinite(value):
        value = lower
    return max(lower, min(upper, value))


def safe_pow(base, exp):
    return max(0.0, float(base)) ** max(0, int(exp))


def finite_float(value, default=0.0):
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def normalize_historical_frame(historical_data):
    """Return a normalized historical DataFrame or an empty frame."""
    if historical_data is None:
        return pd.DataFrame()

    if isinstance(historical_data, pd.DataFrame):
        df = historical_data.copy()
    elif isinstance(historical_data, dict):
        df = pd.DataFrame(historical_data)
    else:
        return pd.DataFrame()

    if "co2_emission" not in df.columns and "co2" in df.columns:
        df["co2_emission"] = df["co2"]
    if "energy_consumption" not in df.columns and "energy" in df.columns:
        df["energy_consumption"] = df["energy"]

    needed = ["year", "gdp", "energy_consumption", "co2_emission"]
    existing = [col for col in needed if col in df.columns]
    if len(existing) < 4:
        return pd.DataFrame()

    for col in existing + ["renewable_ratio", "coal_ratio"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=needed).sort_values("year").reset_index(drop=True)
    return df


def _recent_rates(values, mode="growth"):
    arr = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
    rates = []
    for prev, curr in zip(arr.iloc[:-1], arr.iloc[1:]):
        if prev <= 0 or curr <= 0:
            continue
        if mode == "improvement":
            rates.append(1 - curr / prev)
        else:
            rates.append(curr / prev - 1)
    return rates


def robust_recent_rate(values, lower, upper, mode="growth", max_points=5, default=0.0):
    """Weighted, winsorized recent rate for short and noisy history windows."""
    rates = _recent_rates(values, mode=mode)
    if not rates:
        return clamp(default, lower, upper)

    arr = np.asarray(rates[-max_points:], dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return clamp(default, lower, upper)

    if len(arr) >= 4:
        low, high = np.percentile(arr, [20, 80])
        arr = np.clip(arr, low, high)

    weights = np.linspace(1.0, 2.0, len(arr))
    return clamp(float(np.average(arr, weights=weights)), lower, upper)


def robust_recent_diff(values, lower, upper, max_points=5, default=0.0):
    arr = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
    if len(arr) < 2:
        return clamp(default, lower, upper)
    diffs = np.asarray(arr.diff().dropna().iloc[-max_points:], dtype=float)
    diffs = diffs[np.isfinite(diffs)]
    if len(diffs) == 0:
        return clamp(default, lower, upper)
    if len(diffs) >= 4:
        low, high = np.percentile(diffs, [20, 80])
        diffs = np.clip(diffs, low, high)
    weights = np.linspace(1.0, 2.0, len(diffs))
    return clamp(float(np.average(diffs, weights=weights)), lower, upper)


def historical_indicators(historical_data, base_data=None):
    """Calculate stable historical indicators used to calibrate projections."""
    base_data = base_data or {}
    base_gdp = max(finite_float(base_data.get("gdp"), 1.0), 1e-12)
    base_energy = max(finite_float(base_data.get("energy"), 1.0), 1e-12)
    base_co2 = max(finite_float(base_data.get("co2"), 1.0), 1e-12)

    defaults = {
        "gdp_growth_rate": 0.04,
        "energy_growth_rate": 0.02,
        "co2_growth_rate": 0.01,
        "energy_intensity_improvement_rate": 0.025,
        "carbon_intensity_improvement_rate": 0.0,
        "renewable_increase_rate": 0.01,
        "coal_decrease_rate": 0.01,
        "base_energy_intensity": finite_float(
            base_data.get("energy_intensity"), base_energy / base_gdp
        ),
        "base_carbon_intensity": base_co2 / base_energy,
    }

    df = normalize_historical_frame(historical_data)
    if len(df) < 2:
        return defaults

    energy_intensity = (df["energy_consumption"] / df["gdp"]).clip(lower=1e-12)
    carbon_intensity = (df["co2_emission"] / df["energy_consumption"]).clip(lower=1e-12)

    defaults.update(
        {
            "gdp_growth_rate": robust_recent_rate(
                df["gdp"], -0.03, 0.12, default=defaults["gdp_growth_rate"]
            ),
            "energy_growth_rate": robust_recent_rate(
                df["energy_consumption"], -0.08, 0.08, default=defaults["energy_growth_rate"]
            ),
            "co2_growth_rate": robust_recent_rate(
                df["co2_emission"], -0.10, 0.10, default=defaults["co2_growth_rate"]
            ),
            "energy_intensity_improvement_rate": robust_recent_rate(
                energy_intensity,
                -0.02,
                0.08,
                mode="improvement",
                default=defaults["energy_intensity_improvement_rate"],
            ),
            "carbon_intensity_improvement_rate": robust_recent_rate(
                carbon_intensity,
                -0.03,
                0.04,
                mode="improvement",
                default=defaults["carbon_intensity_improvement_rate"],
            ),
            "base_energy_intensity": float(energy_intensity.iloc[-1]),
            "base_carbon_intensity": float(carbon_intensity.iloc[-1]),
        }
    )

    if "renewable_ratio" in df.columns:
        renewable = df["renewable_ratio"].clip(lower=0.0, upper=0.95)
        defaults["renewable_increase_rate"] = robust_recent_diff(
            renewable, 0.0, 0.04, default=defaults["renewable_increase_rate"]
        )
    if "coal_ratio" in df.columns:
        coal = df["coal_ratio"].clip(lower=0.02, upper=0.98)
        defaults["coal_decrease_rate"] = robust_recent_rate(
            coal, 0.0, 0.08, mode="improvement", default=defaults["coal_decrease_rate"]
        )

    return defaults


def smoothstep(progress):
    progress = clamp(progress, 0.0, 1.0)
    return progress * progress * (3 - 2 * progress)


def transition_rate(year_index, near_rate, long_rate, transition_years):
    if transition_years <= 0:
        return long_rate
    progress = smoothstep((year_index - 1) / float(transition_years))
    return near_rate * (1 - progress) + long_rate * progress


def blend_with_history(input_rate, history_rate, lower, upper, history_weight=0.2):
    """Use history as a stabilizer without letting volatile data dominate."""
    if abs(input_rate - history_rate) > 0.06:
        history_weight *= 0.5
    return clamp(
        input_rate * (1 - history_weight) + history_rate * history_weight,
        lower,
        upper,
    )


def default_long_gdp_rate(rate):
    rate = float(rate)
    if rate <= 0:
        return clamp(rate * 0.5, -0.02, 0.0)
    if rate < 0.025:
        return clamp(rate * 0.7, 0.0, rate)
    return clamp(rate * 0.45, 0.012, 0.05)


def default_long_efficiency_rate(rate):
    rate = max(0.0, float(rate))
    if rate < 0.02:
        return rate * 0.8
    return clamp(rate * 0.55, 0.01, 0.05)


def driver_paths(base_data, params, horizon_year, historical_data=None):
    """Project GDP, energy intensity and energy demand with rate transitions."""
    base_year = int(base_data["year"])
    years = max(0, int(horizon_year) - base_year)
    base_gdp = max(finite_float(base_data["gdp"]), 1e-12)
    base_energy = max(finite_float(base_data["energy"]), 1e-12)
    base_energy_intensity = max(
        finite_float(base_data.get("energy_intensity"), base_energy / base_gdp), 1e-12
    )

    indicators = historical_indicators(historical_data, base_data)

    input_gdp_growth = clamp(finite_float(params.get("gdp_growth_rate"), 0.05), -0.05, 0.20)
    input_efficiency = clamp(
        finite_float(params.get("efficiency_improvement_rate"), 0.03), 0.0, 0.15
    )

    near_gdp_growth = blend_with_history(
        input_gdp_growth,
        indicators["gdp_growth_rate"],
        -0.05,
        0.12,
        history_weight=0.2,
    )
    near_efficiency = blend_with_history(
        input_efficiency,
        indicators["energy_intensity_improvement_rate"],
        0.0,
        0.10,
        history_weight=0.2,
    )

    long_gdp_growth = clamp(
        finite_float(
            params.get("long_term_gdp_growth_rate"),
            default_long_gdp_rate(input_gdp_growth),
        ),
        -0.03,
        0.08,
    )
    long_efficiency = clamp(
        finite_float(
            params.get("long_term_efficiency_improvement_rate"),
            default_long_efficiency_rate(input_efficiency),
        ),
        0.0,
        0.08,
    )
    gdp_transition = int(clamp(params.get("gdp_transition_years", 15), 1, 40))
    efficiency_transition = int(clamp(params.get("efficiency_transition_years", 12), 1, 40))

    rows = [
        {
            "year": base_year,
            "gdp": base_gdp,
            "energy_intensity": base_energy_intensity,
            "energy_consumption": base_energy,
            "gdp_growth_rate_applied": 0.0,
            "efficiency_improvement_rate_applied": 0.0,
        }
    ]

    gdp_t = base_gdp
    energy_intensity_t = base_energy_intensity
    for t in range(1, years + 1):
        gdp_rate = transition_rate(t, near_gdp_growth, long_gdp_growth, gdp_transition)
        efficiency_rate = transition_rate(
            t, near_efficiency, long_efficiency, efficiency_transition
        )

        gdp_t = max(0.0, gdp_t * (1 + gdp_rate))
        energy_intensity_t = max(1e-12, energy_intensity_t * (1 - efficiency_rate))
        energy_t = max(0.0, gdp_t * energy_intensity_t)

        rows.append(
            {
                "year": base_year + t,
                "gdp": gdp_t,
                "energy_intensity": energy_intensity_t,
                "energy_consumption": energy_t,
                "gdp_growth_rate_applied": gdp_rate,
                "efficiency_improvement_rate_applied": efficiency_rate,
            }
        )

    return pd.DataFrame(rows), indicators


def saturating_share(base_share, annual_increase, target_share, year_index):
    """Smoothly approach a target share while matching the initial yearly slope."""
    base_share = clamp(base_share, 0.0, 0.95)
    target_share = clamp(target_share, base_share, 0.95)
    annual_increase = max(0.0, float(annual_increase))
    if year_index <= 0 or annual_increase <= 0 or target_share <= base_share:
        return base_share
    distance = max(target_share - base_share, 1e-12)
    return target_share - distance * math.exp(-(annual_increase / distance) * year_index)


def structure_paths(base_data, params, years):
    base_renewable = clamp(finite_float(base_data.get("renewable_ratio"), 0.10), 0.0, 0.95)
    base_coal_ratio = clamp(finite_float(base_data.get("coal_ratio"), 0.70), 0.02, 0.98)

    renewable_increase = clamp(
        finite_float(params.get("renewable_increase_rate"), 0.01), 0.0, 0.08
    )
    coal_decrease = clamp(finite_float(params.get("coal_decrease_rate"), 0.02), 0.0, 0.15)
    renewable_target = clamp(
        finite_float(params.get("renewable_target_ratio"), 0.70), base_renewable, 0.95
    )
    coal_floor = clamp(finite_float(params.get("coal_floor_ratio"), 0.15), 0.02, base_coal_ratio)

    rows = []
    for t in range(years + 1):
        renewable_ratio = saturating_share(
            base_renewable, renewable_increase, renewable_target, t
        )
        if coal_decrease <= 0:
            coal_ratio = base_coal_ratio
        else:
            coal_ratio = coal_floor + (base_coal_ratio - coal_floor) * math.exp(
                -coal_decrease * t
            )
        rows.append(
            {
                "renewable_ratio": clamp(renewable_ratio, 0.0, 0.95),
                "coal_ratio": clamp(coal_ratio, coal_floor, base_coal_ratio),
            }
        )

    return pd.DataFrame(rows)


def carbon_factor_multipliers(params, indicators, years):
    user_rate = params.get("carbon_factor_decline_rate")
    if user_rate is None:
        near_decline = clamp(max(0.0, indicators["carbon_intensity_improvement_rate"]) * 0.3, 0, 0.012)
    else:
        near_decline = clamp(finite_float(user_rate), 0.0, 0.08)

    long_decline = clamp(
        finite_float(
            params.get("long_term_carbon_factor_decline_rate"), near_decline * 0.5
        ),
        0.0,
        0.05,
    )
    transition_years = int(clamp(params.get("carbon_factor_transition_years", 15), 1, 40))

    values = [1.0]
    value = 1.0
    for t in range(1, years + 1):
        decline = transition_rate(t, near_decline, long_decline, transition_years)
        value *= 1 - decline
        values.append(max(value, 0.08))
    return values


def apply_emission_path_constraints(df, params):
    """Limit implausible year-to-year emission jumps in forecast output."""
    if df.empty or params.get("disable_emission_constraints"):
        return df

    max_increase = clamp(params.get("max_annual_emission_increase", 0.08), 0.0, 0.30)
    max_decline = clamp(params.get("max_annual_emission_decline", 0.12), 0.02, 0.50)

    adjusted = []
    for i, value in enumerate(df["co2_emission"].astype(float).tolist()):
        if i == 0:
            adjusted.append(max(value, 0.0))
            continue
        prev = max(adjusted[-1], 1e-12)
        lower = prev * (1 - max_decline)
        upper = prev * (1 + max_increase)
        adjusted.append(clamp(value, lower, upper))

    out = df.copy()
    out["co2_emission"] = adjusted
    if "energy_consumption" in out.columns:
        out["carbon_intensity"] = out["co2_emission"] / out["energy_consumption"].clip(
            lower=1e-12
        )
    return out


def annotate_peak(df, eps=0.005):
    """Mark the maximum in-horizon emission point and attach peak metadata."""
    out = df.copy()
    out["is_peak"] = False
    if out.empty or "co2_emission" not in out.columns:
        out.attrs["peak_year"] = None
        out.attrs["peak_value"] = None
        out.attrs["peak_status"] = "unknown"
        return out

    emissions = out["co2_emission"].astype(float)
    peak_idx = emissions.idxmax()
    peak_pos = list(out.index).index(peak_idx)
    peak_year = int(out.loc[peak_idx, "year"])
    peak_value = float(out.loc[peak_idx, "co2_emission"])

    if peak_pos == len(out) - 1 and len(out) > 1 and emissions.iloc[-1] > emissions.iloc[0] * (1 + eps):
        status = "not_reached"
    elif peak_pos == 0:
        status = "base_year_peak"
    else:
        status = "reached"

    out.loc[peak_idx, "is_peak"] = True
    out.attrs["peak_year"] = peak_year
    out.attrs["peak_value"] = peak_value
    out.attrs["peak_status"] = status
    return out


def finalize_projection(df, params):
    return annotate_peak(apply_emission_path_constraints(df, params))
