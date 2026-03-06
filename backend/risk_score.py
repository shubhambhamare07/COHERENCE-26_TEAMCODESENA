"""
risk_score.py — ArthRakshak Platform
-------------------------------------
Calculates corruption risk scores for cities based on budget
allocation vs. expenditure data.

Risk Score Formula:
    risk_score = (1 - utilization_ratio) * 50
               + anomaly_factor * 30
               + allocation_weight * 20

Higher unused budget → higher corruption risk.
"""

import pandas as pd
import numpy as np
from pathlib import Path


# --------------------------------------------------------------------------- #
#  Constants
# --------------------------------------------------------------------------- #

DATA_PATH = Path("backend/data/budget_data.csv")

# Weights used in the risk formula (must sum to 100)
W_UTILIZATION  = 50   # Penalises low spend vs allocation
W_ANOMALY      = 30   # Penalises statistical outliers within a city
W_ALLOCATION   = 20   # Penalises cities with disproportionately large budgets


# --------------------------------------------------------------------------- #
#  Internal helpers
# --------------------------------------------------------------------------- #

def _load_data(path: Path) -> pd.DataFrame:
    """
    Load and validate the budget CSV file.

    Expected columns: city, scheme, allocated, spent, latitude, longitude
    Rows with missing or zero 'allocated' values are dropped to avoid
    division-by-zero errors.
    """
    df = pd.read_csv(path)

    required_cols = {"city", "scheme", "allocated", "spent", "latitude", "longitude"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    # Drop rows where allocation is null or zero (cannot compute a ratio)
    df = df[df["allocated"].notna() & (df["allocated"] > 0)].copy()

    # Ensure 'spent' is never negative or NaN
    df["spent"] = df["spent"].fillna(0).clip(lower=0)

    return df


def _compute_utilization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a per-row utilization_ratio column.

    utilization_ratio = spent / allocated
    Capped at 1.0 — overspending does not reduce risk score.
    """
    df["utilization_ratio"] = (df["spent"] / df["allocated"]).clip(upper=1.0)
    return df


def _compute_anomaly_factor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute an anomaly_factor for each row using z-score normalisation
    applied within each city group.

    A scheme whose utilization_ratio is unusually low compared to other
    schemes in the same city is flagged as anomalous (score closer to 1).
    Normalised to [0, 1].
    """
    def city_anomaly(group: pd.DataFrame) -> pd.Series:
        ratio = group["utilization_ratio"]
        std   = ratio.std(ddof=0)

        if std == 0 or len(group) < 2:
            # All schemes behave identically — no detectable anomaly
            return pd.Series(0.0, index=group.index)

        # z-score of *inverse* utilization so low spend = high anomaly
        inv_ratio  = 1 - ratio
        z_scores   = (inv_ratio - inv_ratio.mean()) / std

        # Normalise z-scores to [0, 1] using min-max within the city
        z_min, z_max = z_scores.min(), z_scores.max()
        if z_max == z_min:
            return pd.Series(0.0, index=group.index)

        return (z_scores - z_min) / (z_max - z_min)

    df["anomaly_factor"] = (
        df.groupby("city", group_keys=False)
          .apply(city_anomaly)
    )
    return df


def _compute_allocation_weight(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute an allocation_weight that reflects how large a city's total
    budget is relative to all other cities.

    Cities receiving disproportionately large allocations are weighted
    higher, reflecting greater corruption opportunity.
    Normalised to [0, 1].
    """
    city_totals = df.groupby("city")["allocated"].sum()
    total_min, total_max = city_totals.min(), city_totals.max()

    if total_max == total_min:
        # All cities have the same total allocation
        city_weight = pd.Series(0.5, index=city_totals.index)
    else:
        city_weight = (city_totals - total_min) / (total_max - total_min)

    # Map city-level weight back to individual rows
    df["allocation_weight"] = df["city"].map(city_weight)
    return df


def _aggregate_to_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate scheme-level metrics to city level by taking weighted means
    (weighted by allocated budget within the city).
    """
    def weighted_mean(group: pd.DataFrame, col: str) -> float:
        weights = group["allocated"]
        return np.average(group[col], weights=weights)

    records = []
    for city, group in df.groupby("city"):
        records.append({
            "city":               city,
            "utilization_ratio":  weighted_mean(group, "utilization_ratio"),
            "anomaly_factor":     weighted_mean(group, "anomaly_factor"),
            "allocation_weight":  group["allocation_weight"].iloc[0],  # city-level constant
            "latitude":           group["latitude"].iloc[0],
            "longitude":          group["longitude"].iloc[0],
            "total_allocated":    group["allocated"].sum(),
            "total_spent":        group["spent"].sum(),
            "scheme_count":       len(group),
        })

    return pd.DataFrame(records)


def _apply_risk_formula(city_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the ArthRakshak risk score formula to city-level aggregates.

    risk_score = (1 - utilization_ratio) * 50
               + anomaly_factor          * 30
               + allocation_weight       * 20

    Result is rounded to 2 decimal places.
    """
    city_df["risk_score"] = (
        (1 - city_df["utilization_ratio"]) * W_UTILIZATION
        + city_df["anomaly_factor"]         * W_ANOMALY
        + city_df["allocation_weight"]      * W_ALLOCATION
    ).round(2)

    return city_df


# --------------------------------------------------------------------------- #
#  Public API
# --------------------------------------------------------------------------- #

def calculate_risk_scores(data_path: str | Path = DATA_PATH) -> list[dict]:
    """
    Calculate corruption risk scores for every city in the dataset.

    Parameters
    ----------
    data_path : str or Path
        Path to the budget CSV file.
        Defaults to ``backend/data/budget_data.csv``.

    Returns
    -------
    list[dict]
        List of city risk records sorted by risk_score descending.
        Each record contains:
          - city              : str
          - risk_score        : float  (0–100)
          - utilization_ratio : float  (0–1)
          - anomaly_factor    : float  (0–1)
          - allocation_weight : float  (0–1)
          - total_allocated   : float
          - total_spent       : float
          - scheme_count      : int
          - latitude          : float
          - longitude         : float

    Example
    -------
    >>> results = calculate_risk_scores()
    >>> results[0]
    {
        'city': 'Delhi',
        'risk_score': 72.45,
        'utilization_ratio': 0.45,
        ...
    }
    """
    # Step 1: Load & validate raw data
    df = _load_data(Path(data_path))

    # Step 2: Compute per-scheme metrics
    df = _compute_utilization(df)
    df = _compute_anomaly_factor(df)
    df = _compute_allocation_weight(df)

    # Step 3: Roll up to city level
    city_df = _aggregate_to_city(df)

    # Step 4: Apply risk formula
    city_df = _apply_risk_formula(city_df)

    # Step 5: Sort by highest risk first
    city_df = city_df.sort_values("risk_score", ascending=False).reset_index(drop=True)

    # Step 6: Serialise to plain Python dicts (JSON-friendly)
    results = city_df.to_dict(orient="records")

    return results


# --------------------------------------------------------------------------- #
#  CLI / quick test
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import json

    scores = calculate_risk_scores()

    # Pretty-print top results
    print(json.dumps(scores, indent=2))

    print(f"\n{'─'*40}")
    print(f"Cities analysed : {len(scores)}")
    if scores:
        top = scores[0]
        print(f"Highest risk    : {top['city']}  →  {top['risk_score']}")
        bot = scores[-1]
        print(f"Lowest risk     : {bot['city']}  →  {bot['risk_score']}")