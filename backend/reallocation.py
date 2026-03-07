"""
ArthRakshak — Budget Reallocation Engine
Simulates budget reallocation scenarios and projects outcomes.
"""

import math
import statistics
from datetime import datetime
from typing import Optional


# ── Simulation Config ─────────────────────────────────────────────────
SECTOR_MULTIPLIERS = {
    # sector -> (utilization_efficiency, risk_reduction_factor)
    "Healthcare":         (1.25, 0.90),
    "Education":          (1.20, 0.85),
    "Agriculture":        (1.15, 0.80),
    "Water":              (1.18, 0.82),
    "Renewable Energy":   (1.22, 0.88),
    "Financial Inclusion":(1.30, 0.75),
    "Employment":         (1.10, 0.95),
    "Roads":              (0.95, 1.05),  # higher corruption risk
    "Infrastructure":     (0.90, 1.10),
    "Housing":            (1.05, 0.92),
    "Social Welfare":     (1.15, 0.88),
    "Technology":         (1.35, 0.70),
    "Small Business":     (1.12, 0.95),
    "Energy":             (1.20, 0.85),
    "Transport":          (0.95, 1.08),
}


def simulate_reallocation(
    schemes: list,
    increase_pct: float = 0.0,       # % increase in total budget
    efficiency_target: float = 0.0,  # target utilization increase %
    focus_sectors: list = None,       # sectors to prioritize
    risk_reduction_target: float = 0.0,  # desired risk score reduction
) -> dict:
    """
    Run a budget reallocation simulation.
    Returns projected outcomes vs current baseline.
    """
    if not schemes:
        return {"error": "No schemes to simulate"}

    focus_sectors = focus_sectors or []
    current_utils   = [s.get("utilization", 50) for s in schemes]
    current_risks   = [s.get("riskScore", 40) for s in schemes]
    current_avg_u   = round(statistics.mean(current_utils), 1)
    current_avg_r   = round(statistics.mean(current_risks), 1)

    # Simulate per-scheme outcomes
    projected = []
    for s in schemes:
        sector = s.get("sector", "")
        curr_u = s.get("utilization", 50)
        curr_r = s.get("riskScore", 40)
        eff_mult, risk_mult = SECTOR_MULTIPLIERS.get(sector, (1.0, 1.0))

        # Utilization improvement
        base_improvement = efficiency_target * eff_mult
        if focus_sectors and sector in focus_sectors:
            base_improvement *= 1.4  # focused sectors improve more
        budget_boost = increase_pct * 0.3  # more budget → some utilization improvement
        new_u = min(99, round(curr_u + base_improvement + budget_boost, 1))

        # Risk improvement (risk reduces with better monitoring)
        risk_improvement = risk_reduction_target * (2 - risk_mult)  # high-risk sectors harder
        new_r = max(5, round(curr_r - risk_improvement, 1))

        projected.append({
            "id":            s.get("id"),
            "name":          s.get("name"),
            "sector":        sector,
            "current_util":  curr_u,
            "projected_util": new_u,
            "util_delta":    round(new_u - curr_u, 1),
            "current_risk":  curr_r,
            "projected_risk": new_r,
            "risk_delta":    round(new_r - curr_r, 1),
            "focused":       sector in focus_sectors,
        })

    proj_utils = [p["projected_util"] for p in projected]
    proj_risks  = [p["projected_risk"] for p in projected]
    proj_avg_u  = round(statistics.mean(proj_utils), 1)
    proj_avg_r  = round(statistics.mean(proj_risks), 1)
    high_risk_before = len([s for s in schemes if s.get("riskScore", 0) >= 55])
    high_risk_after  = len([p for p in projected if p["projected_risk"] >= 55])

    # Estimate additional beneficiaries reached
    benef_increase = 0
    if increase_pct > 0:
        benef_increase = round(increase_pct * 0.8 * 1000)  # rough proxy

    return {
        "simulation_id":    f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "inputs": {
            "schemes_count":         len(schemes),
            "budget_increase_pct":   increase_pct,
            "efficiency_target":     efficiency_target,
            "focus_sectors":         focus_sectors,
            "risk_reduction_target": risk_reduction_target,
        },
        "baseline": {
            "avg_utilization":  current_avg_u,
            "avg_risk_score":   current_avg_r,
            "high_risk_count":  high_risk_before,
        },
        "projected": {
            "avg_utilization":        proj_avg_u,
            "avg_risk_score":         proj_avg_r,
            "high_risk_count":        high_risk_after,
            "additional_beneficiaries": benef_increase,
        },
        "deltas": {
            "utilization_gain":  round(proj_avg_u - current_avg_u, 1),
            "risk_reduction":    round(current_avg_r - proj_avg_r, 1),
            "high_risk_reduced": high_risk_before - high_risk_after,
        },
        "scheme_projections": projected,
        "chart_data":         _build_chart_data(projected),
        "insights":           _generate_insights(projected, increase_pct, proj_avg_u, current_avg_u),
        "simulated_at":       datetime.now().isoformat(),
    }


def get_reallocation_recommendations(schemes: list) -> list:
    """
    AI-based recommendations for fund reallocation.
    Returns list of recommendation objects.
    """
    recommendations = []
    sectors = {}
    for s in schemes:
        sec = s.get("sector","")
        if sec not in sectors:
            sectors[sec] = []
        sectors[sec].append(s)

    for sec, sec_schemes in sectors.items():
        avg_u = statistics.mean(s.get("utilization",0) for s in sec_schemes)
        avg_r = statistics.mean(s.get("riskScore",0) for s in sec_schemes)
        eff_mult, _ = SECTOR_MULTIPLIERS.get(sec, (1.0, 1.0))

        if avg_u < 35 and avg_r > 50:
            rec_type = "critical"
            action = "Consider reallocating underutilized funds to performing sectors"
        elif avg_u < 50:
            rec_type = "warning"
            action = "Review disbursement pipeline and remove bottlenecks"
        elif avg_u > 75 and eff_mult > 1.1:
            rec_type = "opportunity"
            action = "Sector performing well — consider increased allocation"
        else:
            continue

        recommendations.append({
            "sector":           sec,
            "type":             rec_type,
            "avg_utilization":  round(avg_u, 1),
            "avg_risk":         round(avg_r, 1),
            "scheme_count":     len(sec_schemes),
            "action":           action,
            "priority":         "HIGH" if rec_type == "critical" else "MEDIUM",
        })

    recommendations.sort(key=lambda r: {"critical":0,"warning":1,"opportunity":2}.get(r["type"],3))
    return recommendations


def _build_chart_data(projections: list) -> dict:
    """Build chart.js compatible data from projections."""
    labels = [p["name"][:20] + ("…" if len(p["name"]) > 20 else "") for p in projections[:10]]
    return {
        "utilization": {
            "labels":  labels,
            "current": [p["current_util"] for p in projections[:10]],
            "projected": [p["projected_util"] for p in projections[:10]],
        },
        "risk": {
            "labels":  labels,
            "current": [p["current_risk"] for p in projections[:10]],
            "projected": [p["projected_risk"] for p in projections[:10]],
        }
    }


def _generate_insights(projections: list, budget_increase: float,
                        proj_avg: float, base_avg: float) -> list:
    insights = []
    gain = proj_avg - base_avg
    if gain > 10:
        insights.append(f"📈 Significant utilization improvement of {round(gain,1)}% projected across all schemes.")
    elif gain > 5:
        insights.append(f"📊 Moderate utilization gain of {round(gain,1)}% projected.")
    elif gain > 0:
        insights.append(f"📊 Marginal utilization improvement of {round(gain,1)}% projected.")

    if budget_increase > 10:
        insights.append(f"💰 Budget increase of {round(budget_increase,1)}% will reach an estimated {round(budget_increase * 0.8 * 1000):,} additional beneficiaries.")

    improved = [p for p in projections if p["util_delta"] > 5]
    if improved:
        top = sorted(improved, key=lambda p: -p["util_delta"])[:3]
        insights.append(f"🏆 Top gainers: {', '.join(p['name'][:20] for p in top)}.")

    declined = [p for p in projections if p["util_delta"] < 0]
    if declined:
        insights.append(f"⚠️ {len(declined)} scheme(s) show projected utilization decline — review funding adequacy.")

    return insights


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_schemes = [
        {"id":"n1","name":"PM-KISAN","utilization":91,"sector":"Agriculture","riskScore":22},
        {"id":"n4","name":"MGNREGA","utilization":55,"sector":"Employment","riskScore":57},
        {"id":"n5","name":"PM Ujjwala","utilization":8,"sector":"Energy","riskScore":38},
        {"id":"n8","name":"Beti Bachao","utilization":25,"sector":"Social Welfare","riskScore":68},
        {"id":"n9","name":"Digital India","utilization":31,"sector":"Technology","riskScore":26},
    ]
    result = simulate_reallocation(
        test_schemes,
        increase_pct=10,
        efficiency_target=8,
        focus_sectors=["Education","Healthcare","Technology"],
        risk_reduction_target=10
    )
    print("Simulation Results:")
    print(f"  Baseline util: {result['baseline']['avg_utilization']}%  →  Projected: {result['projected']['avg_utilization']}%")
    print(f"  Baseline risk: {result['baseline']['avg_risk_score']}   →  Projected: {result['projected']['avg_risk_score']}")
    print(f"  Utilization gain: +{result['deltas']['utilization_gain']}%")
    print(f"  High-risk reduced: {result['deltas']['high_risk_reduced']} schemes")
    print("\nInsights:")
    for i in result["insights"]: print(f"  {i}")
    print("\nRecommendations:")
    for r in get_reallocation_recommendations(test_schemes):
        print(f"  [{r['priority']}] {r['sector']}: {r['action']}")