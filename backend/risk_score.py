"""
ArthRakshak — Risk Score Engine
Computes AI-based corruption & misutilization risk scores for schemes.
"""

import math
from datetime import datetime


# ── Risk Factor Weights ───────────────────────────────────────────────
WEIGHTS = {
    "utilization_gap":     0.30,   # Low utilization with high disbursement
    "audit_flags":         0.25,   # Known audit/CAG flags
    "disbursement_speed":  0.15,   # Funds disbursed suspiciously fast
    "beneficiary_density": 0.10,   # Unusually high beneficiary count
    "contractor_pattern":  0.10,   # Single contractor dominance
    "reporting_delay":     0.10,   # Late submissions
}

RISK_THRESHOLDS = {
    "low":      (0,  29),
    "medium":   (30, 54),
    "high":     (55, 74),
    "critical": (75, 100),
}


def compute_risk_score(scheme: dict) -> dict:
    """
    Compute risk score for a single scheme.
    Returns dict with score, level, breakdown, and recommendation.
    """
    score = 0.0
    breakdown = {}

    utilization = scheme.get("utilization", 50)
    budget_cr = scheme.get("budget_cr", 100)  # budget in crores

    # 1. Utilization gap risk
    # Low utilization + high disbursement = money possibly siphoned
    if utilization < 20:
        util_risk = 90
    elif utilization < 40:
        util_risk = 65
    elif utilization < 60:
        util_risk = 35
    elif utilization < 80:
        util_risk = 15
    else:
        util_risk = 5
    breakdown["utilization_gap"] = round(util_risk)
    score += util_risk * WEIGHTS["utilization_gap"]

    # 2. Audit flags (based on sector)
    HIGH_RISK_SECTORS = ["Roads", "Infrastructure", "Housing", "Employment", "Small Business"]
    LOW_RISK_SECTORS  = ["Education", "Healthcare", "Financial Inclusion", "Renewable Energy"]
    sector = scheme.get("sector", "")
    if sector in HIGH_RISK_SECTORS:
        audit_risk = 70
    elif sector in LOW_RISK_SECTORS:
        audit_risk = 20
    else:
        audit_risk = 45
    breakdown["audit_flags"] = round(audit_risk)
    score += audit_risk * WEIGHTS["audit_flags"]

    # 3. Disbursement speed risk
    # Large budgets disbursed in short time = suspicious
    if budget_cr > 10000:
        disburse_risk = 60
    elif budget_cr > 1000:
        disburse_risk = 40
    elif budget_cr > 100:
        disburse_risk = 25
    else:
        disburse_risk = 15
    breakdown["disbursement_speed"] = round(disburse_risk)
    score += disburse_risk * WEIGHTS["disbursement_speed"]

    # 4. Beneficiary density risk
    benef = scheme.get("beneficiaries_lakh", 0)
    if benef > 500:     # >5 crore beneficiaries
        benef_risk = 50
    elif benef > 100:
        benef_risk = 30
    else:
        benef_risk = 10
    breakdown["beneficiary_density"] = round(benef_risk)
    score += benef_risk * WEIGHTS["beneficiary_density"]

    # 5. Contractor pattern (rural/district more vulnerable)
    level = scheme.get("level", "national")
    if level == "district" or level == "rural":
        contractor_risk = 65
    elif level == "state":
        contractor_risk = 40
    else:
        contractor_risk = 25
    breakdown["contractor_pattern"] = round(contractor_risk)
    score += contractor_risk * WEIGHTS["contractor_pattern"]

    # 6. Reporting delay
    launch_year = scheme.get("year", datetime.now().year)
    age_years = datetime.now().year - launch_year
    if age_years > 10:
        delay_risk = 55
    elif age_years > 5:
        delay_risk = 35
    else:
        delay_risk = 20
    breakdown["reporting_delay"] = round(delay_risk)
    score += delay_risk * WEIGHTS["reporting_delay"]

    # Normalize to 0-100
    final_score = min(100, max(0, round(score)))

    # Adjust using base_risk from frontend data if provided
    base = scheme.get("riskScore", None)
    if base is not None:
        # Blend computed score with known base (70% computed, 30% base)
        final_score = round(0.7 * final_score + 0.3 * base)

    level_label = _score_to_level(final_score)

    return {
        "scheme_id":       scheme.get("id", "unknown"),
        "scheme_name":     scheme.get("name", "Unknown Scheme"),
        "score":           final_score,
        "level":           level_label,
        "breakdown":       breakdown,
        "recommendation":  _get_recommendation(level_label, breakdown),
        "key_factor":      _get_key_factor(breakdown),
        "computed_at":     datetime.now().isoformat(),
    }


def score_all_schemes(schemes: list) -> list:
    """Score all schemes and return sorted by risk descending."""
    results = [compute_risk_score(s) for s in schemes]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_risk_summary(schemes: list) -> dict:
    """Return aggregate risk statistics for a department's schemes."""
    scored = score_all_schemes(schemes)
    dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for s in scored:
        dist[s["level"]] += 1

    scores = [s["score"] for s in scored]
    avg = round(sum(scores) / len(scores)) if scores else 0

    return {
        "total_schemes":   len(scored),
        "average_score":   avg,
        "distribution":    dist,
        "highest_risk":    scored[0] if scored else None,
        "lowest_risk":     scored[-1] if scored else None,
        "critical_count":  dist["critical"],
        "high_count":      dist["high"],
        "schemes":         scored,
    }


def _score_to_level(score: int) -> str:
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "critical"


def _get_recommendation(level: str, breakdown: dict) -> str:
    RECS = {
        "low":      "✅ Routine monitoring sufficient. Maintain quarterly reports.",
        "medium":   "📋 Enhanced monitoring recommended. Schedule quarterly audit.",
        "high":     "🔍 Immediate investigation required. Freeze new disbursements.",
        "critical": "🚨 Escalate to CAG/CBI. Suspend disbursements pending review.",
    }
    return RECS.get(level, "Monitor closely.")


def _get_key_factor(breakdown: dict) -> str:
    """Return the single highest-contributing risk factor."""
    if not breakdown:
        return "Unknown"
    key = max(breakdown, key=breakdown.get)
    LABELS = {
        "utilization_gap":     "Low utilization with high disbursement",
        "audit_flags":         "Sector historically prone to audit findings",
        "disbursement_speed":  "Unusually rapid fund disbursement",
        "beneficiary_density": "Large beneficiary pool — verification risk",
        "contractor_pattern":  "Local contractor concentration risk",
        "reporting_delay":     "Historical reporting delays detected",
    }
    return LABELS.get(key, key)


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_schemes = [
        {"id": "n1", "name": "PM-KISAN", "utilization": 91, "sector": "Agriculture", "budget_cr": 60000, "year": 2019, "level": "national", "riskScore": 22},
        {"id": "n4", "name": "MGNREGA", "utilization": 55, "sector": "Employment", "budget_cr": 60000, "year": 2005, "level": "national", "riskScore": 57},
        {"id": "n8", "name": "Beti Bachao Beti Padhao", "utilization": 25, "sector": "Social Welfare", "budget_cr": 2000, "year": 2015, "level": "national", "riskScore": 68},
        {"id": "d4", "name": "Katraj Bus Stand", "utilization": 39, "sector": "Transport", "budget_cr": 3.8, "year": 2022, "level": "district", "riskScore": 67},
    ]
    summary = get_risk_summary(test_schemes)
    print(f"Risk Summary: {summary['total_schemes']} schemes, avg score: {summary['average_score']}")
    print(f"Distribution: {summary['distribution']}")
    for s in summary["schemes"]:
        print(f"  [{s['level'].upper():8}] {s['scheme_name'][:35]:35} Score: {s['score']:3} | {s['key_factor']}")