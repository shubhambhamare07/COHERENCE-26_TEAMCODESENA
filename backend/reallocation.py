"""
reallocation_simulator.py
==========================
Simulates moving budget from one city to another WITHOUT permanently
modifying the original dataset.

Expected CSV schema  (backend/data/budget_data.csv)
----------------------------------------------------
city               | str   – city name
allocated_budget   | float – total budget allocated to the city
utilized_budget    | float – amount actually spent / committed
utilization_ratio  | float – derived: utilized_budget / allocated_budget
risk_score         | float – derived: composite risk index (0–100)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

_MODULE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH: Path = _MODULE_DIR / "backend" / "data" / "budget_data.csv"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_dataframe(data_path: str | Path) -> pd.DataFrame:
    """Load the CSV, normalise column names, and return a clean DataFrame."""
    path = Path(data_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Budget data file not found: {path}\n"
            "Pass an explicit `data_path` argument or set the DATA_PATH "
            "environment variable."
        )
    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def _recalculate_utilization_ratio(df: pd.DataFrame) -> pd.DataFrame:
    """
    utilization_ratio = utilized_budget / allocated_budget

    Result is in [0, 1].  Zero-division yields 0.
    """
    mask = df["allocated_budget"] > 0
    df["utilization_ratio"] = 0.0
    df.loc[mask, "utilization_ratio"] = (
        df.loc[mask, "utilized_budget"] / df.loc[mask, "allocated_budget"]
    ).round(6)
    return df


def _recalculate_risk_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Composite risk score  (0–100, integer).

    Formula
    -------
    Two normalised components are blended:

    1. Utilization pressure  (weight 60 %)
       Higher utilization -> less headroom -> higher risk.
       Score = utilization_ratio * 100

    2. Budget adequacy       (weight 40 %)
       A city with a very small allocated_budget relative to the rest of
       the dataset carries higher risk.
       Score = (1 - normalised_budget) * 100
       where normalised_budget = (budget - min) / (max - min)

    Both components are clipped to [0, 100] before blending.
    """
    util_score = (df["utilization_ratio"] * 100).clip(0, 100)

    b_min = df["allocated_budget"].min()
    b_max = df["allocated_budget"].max()
    b_range = b_max - b_min if b_max != b_min else 1.0
    budget_norm = (df["allocated_budget"] - b_min) / b_range
    adequacy_score = ((1 - budget_norm) * 100).clip(0, 100)

    df["risk_score"] = (0.60 * util_score + 0.40 * adequacy_score).round(0).astype(int)
    return df


def _find_city_index(df: pd.DataFrame, city: str) -> int:
    """Return the DataFrame index for *city* (case-insensitive match)."""
    city_col_lower = df["city"].str.strip().str.lower()
    matches = df.index[city_col_lower == city.strip().lower()]
    if matches.empty:
        available = df["city"].tolist()
        raise ValueError(
            f"City '{city}' not found in dataset.\n"
            f"Available cities: {available}"
        )
    return int(matches[0])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def simulate_budget_reallocation(
    from_city: str,
    to_city: str,
    amount: float,
    *,
    data_path: str | Path | None = None,
) -> dict[str, Any]:
    """
    Simulate transferring *amount* of budget from *from_city* to *to_city*.

    The original CSV is **never modified**.  All operations are performed
    on an in-memory deep copy of the loaded DataFrame.

    Parameters
    ----------
    from_city : str
        Name of the city to reduce budget from.
    to_city : str
        Name of the city to increase budget to.
    amount : float
        Monetary amount to transfer (must be > 0).
    data_path : str or Path, optional
        Path to the budget CSV.  Falls back to the DATA_PATH environment
        variable and then to ``backend/data/budget_data.csv`` (relative
        to this module).

    Returns
    -------
    dict
        {
            "from_city":          str,
            "to_city":            str,
            "amount_transferred": float,
            "new_utilization_ratios": {
                "<from_city>": float,
                "<to_city>":   float
            },
            "new_risk_scores": {
                "<from_city>": int,
                "<to_city>":   int
            }
        }

    Raises
    ------
    FileNotFoundError
        If the CSV cannot be found.
    ValueError
        If a city name is missing, amount <= 0, cities are the same, or
        *from_city* would end up with a negative allocated_budget.
    """

    # ------------------------------------------------------------------ #
    # 1. Validate arguments                                                #
    # ------------------------------------------------------------------ #
    if amount <= 0:
        raise ValueError(f"amount must be positive; received {amount}.")

    if from_city.strip().lower() == to_city.strip().lower():
        raise ValueError("from_city and to_city must be different cities.")

    # ------------------------------------------------------------------ #
    # 2. Load data -> deep copy (original file never touched again)       #
    # ------------------------------------------------------------------ #
    resolved_path = (
        Path(data_path)
        if data_path
        else Path(os.environ.get("DATA_PATH", str(DEFAULT_DATA_PATH)))
    )

    original_df = _load_dataframe(resolved_path)
    df = original_df.copy(deep=True)          # simulation sandbox

    # ------------------------------------------------------------------ #
    # 3. Locate city rows                                                  #
    # ------------------------------------------------------------------ #
    from_idx = _find_city_index(df, from_city)
    to_idx   = _find_city_index(df, to_city)

    from_city_label = df.at[from_idx, "city"]
    to_city_label   = df.at[to_idx,   "city"]

    # ------------------------------------------------------------------ #
    # 4. Guard: ensure from_city has enough budget                        #
    # ------------------------------------------------------------------ #
    current_from_budget = df.at[from_idx, "allocated_budget"]
    if current_from_budget - amount < 0:
        raise ValueError(
            f"Insufficient allocated budget in '{from_city_label}': "
            f"available {current_from_budget:,.0f}, "
            f"requested {amount:,.0f}."
        )

    # ------------------------------------------------------------------ #
    # 5. Apply reallocation on the COPY                                   #
    # ------------------------------------------------------------------ #
    df.at[from_idx, "allocated_budget"] -= amount
    df.at[to_idx,   "allocated_budget"] += amount

    # ------------------------------------------------------------------ #
    # 6. Recalculate derived metrics across the full dataset              #
    # ------------------------------------------------------------------ #
    df = _recalculate_utilization_ratio(df)
    df = _recalculate_risk_score(df)

    # ------------------------------------------------------------------ #
    # 7. Build and return result dict                                      #
    # ------------------------------------------------------------------ #
    return {
        "from_city": from_city_label,
        "to_city":   to_city_label,
        "amount_transferred": amount,
        "new_utilization_ratios": {
            from_city_label: round(float(df.at[from_idx, "utilization_ratio"]), 4),
            to_city_label:   round(float(df.at[to_idx,   "utilization_ratio"]), 4),
        },
        "new_risk_scores": {
            from_city_label: int(df.at[from_idx, "risk_score"]),
            to_city_label:   int(df.at[to_idx,   "risk_score"]),
        },
    }


# ---------------------------------------------------------------------------
# CLI entry-point  (quick smoke-test)
# ---------------------------------------------------------------------------
# Usage:
#   python reallocation_simulator.py Mumbai Nagpur 200000000
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 4:
        print(
            "Usage: python reallocation_simulator.py "
            "<from_city> <to_city> <amount>",
            file=sys.stderr,
        )
        sys.exit(1)

    _, _from, _to, _amt = sys.argv

    try:
        result = simulate_budget_reallocation(_from, _to, float(_amt))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)