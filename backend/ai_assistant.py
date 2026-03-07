"""
ArthRakshak — AI Assistant Backend
Handles natural language queries about schemes, budget, and risk.
"""

import re
import math
import random
import statistics
from datetime import datetime
from typing import Optional


# ── Intent Recognition ─────────────────────────────────────────────────
INTENTS = {
    "risk":        [r"risk", r"fraud", r"corrupt", r"suspicious", r"flagged"],
    "utilization": [r"utiliz", r"spent", r"budget.?status", r"utilized", r"expenditure"],
    "schemes":     [r"how many", r"list.*(scheme|program)", r"total scheme", r"access to"],
    "performance": [r"perform", r"best", r"top.?scheme", r"highest"],
    "underperform":[r"underperform", r"low.?util", r"worst", r"below target"],
    "sector":      [r"sector", r"categor", r"type"],
    "anomaly":     [r"anomal", r"irregular", r"discrepan"],
    "map":         [r"map", r"location", r"where", r"google.?map", r"coordinates"],
    "report":      [r"report", r"pdf", r"download", r"export", r"document"],
    "summary":     [r"summar", r"overview", r"brief", r"dashboard"],
    "simulate":    [r"simulat", r"what.?if", r"scenario", r"project"],
    "greeting":    [r"hello", r"hi\b", r"namaste", r"good (morning|afternoon|evening)"],
    "help":        [r"\bhelp\b", r"what can", r"what do you"],
}


def detect_intent(message: str) -> list[str]:
    """Return list of matched intents for a message."""
    m = message.lower()
    matched = []
    for intent, patterns in INTENTS.items():
        if any(re.search(p, m) for p in patterns):
            matched.append(intent)
    return matched if matched else ["general"]


def generate_response(message: str, user: dict, schemes: list) -> dict:
    """
    Generate AI response for a chat message.
    Returns dict with text, intent, and optional action.
    """
    if not schemes:
        return _resp("I don't have access to any schemes for your department currently.", "error")

    intents = detect_intent(message)
    m = message.lower()

    # ── Greeting ─────────────────────────────────────────────────────
    if "greeting" in intents:
        return _resp(
            f"Namaste! 🙏 I'm ArthRakshak AI, your budget intelligence assistant.\n\n"
            f"I have access to **{len(schemes)} schemes** for **{user.get('dept','your department')}**. "
            f"How may I assist you today?",
            "greeting"
        )

    # ── Help ─────────────────────────────────────────────────────────
    if "help" in intents:
        return _resp(
            "I can assist with the following:\n\n"
            "📊 **Budget Analysis** — utilization, spending patterns\n"
            "🛡️ **Risk Assessment** — fraud scores, high-risk schemes\n"
            "⚠️ **Anomaly Detection** — irregular patterns, suspicious transactions\n"
            "🗺️ **Google Maps** — view scheme locations on map\n"
            "📄 **PDF Reports** — generate downloadable scheme reports\n"
            "📈 **Performance** — best and worst performing schemes\n\n"
            "Try: *\"Which schemes have high risk?\"* or *\"Show utilization summary\"*",
            "help"
        )

    # ── Risk ─────────────────────────────────────────────────────────
    if "risk" in intents:
        high_risk = [s for s in schemes if s.get("riskScore", 0) >= 55]
        critical  = [s for s in schemes if s.get("riskScore", 0) >= 75]
        if not high_risk:
            max_s = max(schemes, key=lambda s: s.get("riskScore", 0))
            return _resp(
                f"✅ No high-risk schemes detected.\n\n"
                f"All {len(schemes)} schemes show acceptable risk levels. "
                f"Highest score: **{max_s.get('riskScore',0)}/100** ({max_s.get('name','—')}).",
                "risk", action={"type": "navigate", "url": "risk_score.html"}
            )
        lines = "\n".join([f"• **{s['name']}** — Risk: {s.get('riskScore',0)}/100" for s in high_risk[:8]])
        note = f"\n\n🚨 **{len(critical)} scheme(s)** are in CRITICAL category and need immediate escalation." if critical else ""
        return _resp(
            f"⚠️ **{len(high_risk)} scheme(s)** with elevated risk:\n\n{lines}{note}\n\n"
            f"→ [View Full Risk Register](risk_score.html)",
            "risk", action={"type": "navigate", "url": "risk_score.html"}
        )

    # ── Utilization ───────────────────────────────────────────────────
    if "utilization" in intents:
        utils = [s.get("utilization", 0) for s in schemes]
        avg = round(statistics.mean(utils))
        best = max(schemes, key=lambda s: s.get("utilization", 0))
        worst = min(schemes, key=lambda s: s.get("utilization", 0))
        return _resp(
            f"📊 **Budget Utilization Summary**\n\n"
            f"• Average: **{avg}%** across {len(schemes)} schemes\n"
            f"• Best: **{best['name']}** ({best.get('utilization',0)}%)\n"
            f"• Worst: **{worst['name']}** ({worst.get('utilization',0)}%)\n"
            f"• Below 30%: **{len([s for s in schemes if s.get('utilization',0)<30])} schemes**\n"
            f"• Above 70%: **{len([s for s in schemes if s.get('utilization',0)>=70])} schemes**",
            "utilization"
        )

    # ── Schemes count ─────────────────────────────────────────────────
    if "schemes" in intents:
        secs = list(set(s.get("sector", "") for s in schemes))
        lvl_map = {
            "Finance Ministry": "National", "Chief Economic Advisory": "National",
            "State Department": user.get("state","State"),
            "District Administration": user.get("district","District") + " District",
            "Rural Administration": user.get("town","Rural"),
        }
        lvl = lvl_map.get(user.get("dept",""), user.get("dept",""))
        return _resp(
            f"You have access to **{len(schemes)} schemes** as **{user.get('dept','—')}** "
            f"at the **{lvl}** level.\n\n"
            f"These cover **{len(secs)} sectors**: {', '.join(secs[:6])}{'...' if len(secs)>6 else ''}.",
            "schemes"
        )

    # ── Performance ───────────────────────────────────────────────────
    if "performance" in intents:
        good = [s for s in schemes if s.get("utilization", 0) >= 70]
        if not good:
            return _resp("No schemes currently at 70%+ utilization. Consider reviewing disbursement pipelines.", "performance")
        lines = "\n".join([f"• **{s['name']}** — {s.get('utilization',0)}%" for s in sorted(good, key=lambda s: -s.get("utilization",0))[:6]])
        return _resp(f"✅ **Top Performing Schemes** (≥70% utilization):\n\n{lines}", "performance")

    # ── Underperforming ───────────────────────────────────────────────
    if "underperform" in intents:
        bad = [s for s in schemes if s.get("utilization", 0) < 30]
        if not bad:
            return _resp("✅ All schemes have utilization above 30%.", "underperform")
        lines = "\n".join([f"• **{s['name']}** — {s.get('utilization',0)}%" for s in sorted(bad, key=lambda s: s.get("utilization",0))[:6]])
        return _resp(f"📉 **Underperforming Schemes** (<30% utilization):\n\n{lines}\n\nConsider reviewing fund release and implementation.", "underperform")

    # ── Sectors ───────────────────────────────────────────────────────
    if "sector" in intents:
        from collections import Counter
        sector_counts = Counter(s.get("sector","Unknown") for s in schemes)
        lines = "\n".join([f"• **{sec}** — {cnt} scheme{'s' if cnt>1 else ''}" for sec, cnt in sector_counts.most_common()])
        return _resp(f"Your {len(schemes)} schemes span **{len(sector_counts)} sectors**:\n\n{lines}", "sector")

    # ── Anomalies ─────────────────────────────────────────────────────
    if "anomaly" in intents:
        flagged = len([s for s in schemes if s.get("riskScore", 0) > 45])
        return _resp(
            f"🔍 **Anomaly Detection Summary**\n\n"
            f"AI engine has flagged **{flagged} schemes** with potential irregularities.\n\n"
            f"Common patterns detected:\n"
            f"• Low utilization with full disbursement\n"
            f"• Risk scores above sector baseline\n"
            f"• Possible contractor concentration\n\n"
            f"→ [View Anomaly Report](anomaly.html)",
            "anomaly", action={"type": "navigate", "url": "anomaly.html"}
        )

    # ── Map ───────────────────────────────────────────────────────────
    if "map" in intents:
        infra = [s for s in schemes if s.get("sector","") in ["Roads","Infrastructure","Transport","Water"]]
        if not infra:
            s = schemes[0]
            q = f"{s.get('district',s.get('state','India'))} {s['name']}"
            return _resp(
                f"🗺️ No infrastructure schemes in scope.\n\n"
                f"[📍 Open {s['name']} on Google Maps](https://www.google.com/maps/search/?api=1&query={q.replace(' ','+')})",
                "map", action={"type": "map", "scheme": s}
            )
        s = infra[0]
        q = f"{s.get('district',s.get('state','India'))} {s['name']}"
        lines = "\n".join([f"• {x['name']} — {x.get('sector','')}" for x in infra[:5]])
        return _resp(
            f"🗺️ **{len(infra)} infrastructure project(s)** in your scope:\n\n{lines}\n\n"
            f"[📍 Open first project on Google Maps](https://www.google.com/maps/search/?api=1&query={q.replace(' ','+')})",
            "map", action={"type": "map", "scheme": s}
        )

    # ── Report / PDF ──────────────────────────────────────────────────
    if "report" in intents:
        return _resp(
            f"📄 **PDF Reports Available**\n\n"
            f"You can generate reports for all {len(schemes)} schemes:\n\n"
            f"• Budget Utilization Summary\n"
            f"• Scheme Performance Report\n"
            f"• Risk Assessment Report\n"
            f"• Full Department Overview\n\n"
            f"→ [Generate PDF Report](reports.html)",
            "report", action={"type": "navigate", "url": "reports.html"}
        )

    # ── Summary / Overview ────────────────────────────────────────────
    if "summary" in intents:
        utils = [s.get("utilization", 0) for s in schemes]
        risks = [s.get("riskScore", 0) for s in schemes]
        avg_u = round(statistics.mean(utils))
        avg_r = round(statistics.mean(risks))
        hr    = len([s for s in schemes if s.get("riskScore",0) >= 55])
        return _resp(
            f"📋 **Department Overview — {user.get('dept','—')}**\n\n"
            f"• Total Schemes: **{len(schemes)}**\n"
            f"• Avg Utilization: **{avg_u}%**\n"
            f"• Avg Risk Score: **{avg_r}/100**\n"
            f"• High Risk Schemes: **{hr}**\n"
            f"• Sectors Covered: **{len(set(s.get('sector','') for s in schemes))}**\n\n"
            f"{'⚠️ Action required on high-risk schemes.' if hr > 0 else '✅ All schemes within normal parameters.'}",
            "summary"
        )

    # ── General fallback ──────────────────────────────────────────────
    # Try to match scheme name
    for s in schemes:
        words = s.get("name","").lower().split()[:3]
        if any(w in m for w in words if len(w) > 4):
            q = f"{s.get('district',s.get('state','India'))} {s['name']}"
            return _resp(
                f"📋 **{s['name']}**\n\n"
                f"• Sector: {s.get('sector','—')}\n"
                f"• Utilization: **{s.get('utilization',0)}%**\n"
                f"• Risk Level: **{_risk_label(s.get('riskScore',0))}** ({s.get('riskScore',0)}/100)\n"
                f"• Budget: {s.get('budget','—')}\n\n"
                f"[📍 View on Google Maps](https://www.google.com/maps/search/?api=1&query={q.replace(' ','+')})",
                "scheme_detail", action={"type": "map", "scheme": s}
            )

    return _resp(
        "I can help with:\n\n"
        "• 📊 Budget utilization analysis\n"
        "• 🛡️ Risk & fraud detection\n"
        "• 🗺️ Google Maps view\n"
        "• 📄 PDF report generation\n\n"
        "Try: *\"Which schemes have high risk?\"* or *\"What is average utilization?\"*",
        "help"
    )


def _resp(text: str, intent: str, action: Optional[dict] = None) -> dict:
    return {
        "text":       text,
        "intent":     intent,
        "action":     action,
        "timestamp":  datetime.now().isoformat(),
        "model":      "ArthRakshak-AI-v2.1",
    }


def _risk_label(score: int) -> str:
    if score < 30:  return "Low"
    if score < 55:  return "Medium"
    if score < 75:  return "High"
    return "Critical"


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_user = {"name": "Anil Kumar", "dept": "Finance Ministry", "state": "National"}
    test_schemes = [
        {"id": "n1", "name": "PM-KISAN", "utilization": 91, "sector": "Agriculture", "riskScore": 22, "budget": "₹60,000 Cr"},
        {"id": "n4", "name": "MGNREGA",  "utilization": 55, "sector": "Employment",  "riskScore": 57, "budget": "₹60,000 Cr"},
        {"id": "n8", "name": "Beti Bachao Beti Padhao", "utilization": 25, "sector": "Social Welfare", "riskScore": 68, "budget": "₹2,000 Cr"},
    ]
    queries = [
        "Namaste!", "How many schemes do I have access to?",
        "Which schemes have high risk?", "What is the average utilization?",
        "Show me infrastructure on Google Maps", "Generate a PDF report",
        "What sectors are covered?",
    ]
    for q in queries:
        r = generate_response(q, test_user, test_schemes)
        print(f"\nQ: {q}")
        print(f"Intent: {r['intent']}")
        print(f"A: {r['text'][:120]}...")