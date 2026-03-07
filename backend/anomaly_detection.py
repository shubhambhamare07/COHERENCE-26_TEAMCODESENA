"""
ArthRakshak — Anomaly Detection Engine
Detects statistical and pattern-based anomalies in scheme budget data.
"""

import math
import statistics
from datetime import datetime, timedelta
from typing import Optional


ANOMALY_TYPES = {
    "UTILIZATION_SPIKE":    "Sudden utilization spike (>40% in one quarter)",
    "ZERO_UTILIZATION":     "Zero utilization despite disbursement",
    "GHOST_BENEFICIARIES":  "Beneficiary count exceeds demographic baseline",
    "FUND_PARKING":         "Funds parked without disbursement (>90 days)",
    "CIRCULAR_PAYMENT":     "Circular payment pattern detected",
    "DUPLICATE_VENDOR":     "Same vendor across multiple sub-schemes",
    "ROUND_TRIPPING":       "Funds returned and re-released suspiciously",
    "EXCESS_CONTRACTOR":    "Single contractor >60% of scheme contracts",
    "MISREPORT":            "Utilization reported ≠ PFMS records",
    "BUDGET_OVERRUN":       "Expenditure exceeds sanctioned budget",
}

SEVERITY_LEVELS = ["low", "medium", "high", "critical"]


def detect_anomalies(schemes: list, historical: Optional[list] = None) -> list:
    """
    Run anomaly detection on a list of schemes.
    Returns list of anomaly records.
    """
    anomalies = []
    
    # Compute baselines across all schemes
    utils = [s.get("utilization", 0) for s in schemes if s.get("utilization") is not None]
    mean_util = statistics.mean(utils) if utils else 50
    std_util  = statistics.stdev(utils) if len(utils) > 1 else 15

    risks = [s.get("riskScore", 0) for s in schemes]
    mean_risk = statistics.mean(risks) if risks else 40

    for scheme in schemes:
        util    = scheme.get("utilization", 0)
        risk    = scheme.get("riskScore", 0)
        budget  = scheme.get("budget_cr", 100)
        sid     = scheme.get("id", "unknown")
        name    = scheme.get("name", "Unknown")
        sector  = scheme.get("sector", "")
        level   = scheme.get("level", "national")

        # ── Rule 1: Zero / near-zero utilization ─────────────────────
        if util < 5 and budget > 50:
            anomalies.append(_make_anomaly(
                scheme_id=sid, scheme_name=name, sector=sector,
                anomaly_type="ZERO_UTILIZATION",
                severity="high" if budget > 500 else "medium",
                detail=f"Only {util}% utilization despite ₹{budget} Cr disbursed. Funds may be parked.",
                amount_cr=budget * (1 - util/100),
                recommendation="Conduct immediate field verification and PFMS reconciliation.",
            ))

        # ── Rule 2: Statistical outlier utilization ───────────────────
        z = (util - mean_util) / std_util if std_util > 0 else 0
        if z < -2.0 and util < 25:
            anomalies.append(_make_anomaly(
                scheme_id=sid, scheme_name=name, sector=sector,
                anomaly_type="FUND_PARKING",
                severity="medium",
                detail=f"Utilization {util}% is {abs(round(z,1))} std deviations below department average ({round(mean_util)}%). Possible fund parking.",
                amount_cr=round(budget * (mean_util/100 - util/100), 2),
                recommendation="Review fund release timeline. Check for parking in treasury accounts.",
            ))

        # ── Rule 3: High risk + high utilization = potential fraud ────
        if risk >= 65 and util >= 80:
            anomalies.append(_make_anomaly(
                scheme_id=sid, scheme_name=name, sector=sector,
                anomaly_type="GHOST_BENEFICIARIES",
                severity="critical" if risk >= 75 else "high",
                detail=f"Risk score {risk}/100 combined with {util}% utilization is a fraud indicator. High spend + high risk = beneficiary fraud likely.",
                amount_cr=round(budget * util / 100 * 0.15, 2),  # estimate 15% leakage
                recommendation="Cross-verify beneficiary list against Aadhaar/PFMS. Freeze new payments pending audit.",
            ))

        # ── Rule 4: Sector-specific patterns ─────────────────────────
        HIGH_FRAUD_SECTORS = ["Roads", "Infrastructure", "Small Business"]
        if sector in HIGH_FRAUD_SECTORS and risk >= 55 and util < 50:
            anomalies.append(_make_anomaly(
                scheme_id=sid, scheme_name=name, sector=sector,
                anomaly_type="EXCESS_CONTRACTOR",
                severity="high",
                detail=f"Sector '{sector}' with {risk}/100 risk and only {util}% utilization indicates contractor manipulation.",
                amount_cr=round(budget * 0.20, 2),
                recommendation="Audit contractor selection process. Check if single entity dominates contracts.",
            ))

        # ── Rule 5: Budget overrun indicator ─────────────────────────
        if util > 95 and budget < 10:
            anomalies.append(_make_anomaly(
                scheme_id=sid, scheme_name=name, sector=sector,
                anomaly_type="BUDGET_OVERRUN",
                severity="medium",
                detail=f"Small scheme ({util}% utilized) may be padding expenditure to exhaust budget.",
                amount_cr=round(budget * 0.08, 2),
                recommendation="Verify expenditure vouchers and civil work quality reports.",
            ))

    # Sort: critical first
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    anomalies.sort(key=lambda x: (severity_order.get(x["severity"], 4), -x["amount_cr"]))

    return anomalies


def get_anomaly_summary(schemes: list) -> dict:
    """Return aggregate anomaly statistics."""
    anomalies = detect_anomalies(schemes)
    dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_at_risk = 0.0
    for a in anomalies:
        dist[a["severity"]] = dist.get(a["severity"], 0) + 1
        total_at_risk += a.get("amount_cr", 0)

    return {
        "total_anomalies":  len(anomalies),
        "distribution":     dist,
        "total_at_risk_cr": round(total_at_risk, 2),
        "anomalies":        anomalies,
        "scan_time":        datetime.now().isoformat(),
        "schemes_scanned":  len(schemes),
    }


def resolve_anomaly(anomaly_id: str, resolved_by: str, note: str = "") -> dict:
    """Mark an anomaly as resolved (to be persisted by main.py)."""
    return {
        "anomaly_id":    anomaly_id,
        "status":        "resolved",
        "resolved_by":   resolved_by,
        "resolved_at":   datetime.now().isoformat(),
        "resolution_note": note or "Marked resolved after verification.",
    }


# ── Internal helpers ──────────────────────────────────────────────────
_anomaly_counter = 0

def _make_anomaly(scheme_id, scheme_name, sector, anomaly_type,
                  severity, detail, amount_cr=0.0, recommendation="") -> dict:
    global _anomaly_counter
    _anomaly_counter += 1
    return {
        "id":              f"ANO-{scheme_id.upper()}-{_anomaly_counter:03d}",
        "scheme_id":       scheme_id,
        "scheme_name":     scheme_name,
        "sector":          sector,
        "anomaly_type":    anomaly_type,
        "type_label":      ANOMALY_TYPES.get(anomaly_type, anomaly_type),
        "severity":        severity,
        "detail":          detail,
        "amount_cr":       amount_cr,
        "recommendation":  recommendation,
        "status":          "open",
        "detected_at":     datetime.now().isoformat(),
        "flagged_by":      "ArthRakshak AI Engine v2.1",
    }


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_schemes = [
        {"id": "n1",  "name": "PM-KISAN",         "utilization": 91, "sector": "Agriculture",  "budget_cr": 60000, "riskScore": 22, "level": "national"},
        {"id": "n4",  "name": "MGNREGA",           "utilization": 55, "sector": "Employment",   "budget_cr": 60000, "riskScore": 57, "level": "national"},
        {"id": "n5",  "name": "PM Ujjwala Yojana", "utilization": 8,  "sector": "Energy",       "budget_cr": 12000, "riskScore": 38, "level": "national"},
        {"id": "n8",  "name": "Beti Bachao",       "utilization": 25, "sector": "Social Welfare","budget_cr": 2000,  "riskScore": 68, "level": "national"},
        {"id": "d4",  "name": "Katraj Bus Stand",  "utilization": 39, "sector": "Transport",    "budget_cr": 3.8,   "riskScore": 67, "level": "district"},
    ]
    summary = get_anomaly_summary(test_schemes)
    print(f"Anomaly scan: {summary['total_anomalies']} anomalies found in {summary['schemes_scanned']} schemes")
    print(f"Total at risk: ₹{summary['total_at_risk_cr']} Cr")
    print(f"Distribution: {summary['distribution']}")
    for a in summary["anomalies"]:
        print(f"  [{a['severity'].upper():8}] {a['scheme_name'][:30]:30} | {a['anomaly_type']} | ₹{a['amount_cr']} Cr")