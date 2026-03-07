"""
ArthRakshak — Backend API Server
Flask REST API connecting risk scoring, anomaly detection, AI, PDF, and geomap modules.

Run:
    pip install flask flask-cors
    python main.py

Endpoints:
    POST /api/chat                  — AI Assistant
    GET  /api/risk/<dept>           — Risk scores
    GET  /api/anomalies/<dept>      — Anomaly detection
    POST /api/simulate              — Budget simulation
    GET  /api/map/<dept>            — GeoJSON for maps
    GET  /api/scheme/<id>/map       — Single scheme map data
    POST /api/pdf/scheme            — Download scheme PDF
    POST /api/pdf/report            — Download department report PDF
    GET  /api/health                — Health check
"""

import os
import sys
import json
from functools import wraps
from datetime import datetime

# ── Try to import Flask ───────────────────────────────────────────────
try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    FLASK_OK = True
except ImportError:
    FLASK_OK = False
    print("⚠ Flask not installed. Run: pip install flask flask-cors")

# ── Import our modules ────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from risk_score       import compute_risk_score, score_all_schemes, get_risk_summary
from anomaly_detection import detect_anomalies, get_anomaly_summary, resolve_anomaly
from ai_assistant     import generate_response
from geomap           import (get_scheme_map_data, get_schemes_geojson,
                               get_department_map_overview, build_google_maps_url)
from reallocation     import simulate_reallocation, get_reallocation_recommendations
from pdf_generator    import (generate_scheme_pdf, generate_department_report,
                               generate_risk_report, generate_anomaly_report)

import io

# ── Scheme Data (mirrors frontend data.js) ────────────────────────────
NATIONWIDE = [
    {"id":"n1","name":"Ayushman Bharat PM-JAY","utilization":28,"sector":"Healthcare","budget_cr":50000,"budget":"₹50,000 Cr","distributed":"₹14,000 Cr","year":2018,"ministry":"Ministry of Health & Family Welfare","beneficiaries":"10.74 Cr families","riskScore":42,"level":"national","state":"National","desc":"World's largest government health insurance — ₹5 lakh cover per family for secondary & tertiary hospitalization."},
    {"id":"n2","name":"PM Awas Yojana (PMAY)","utilization":73,"sector":"Housing","budget_cr":300000,"budget":"₹3,00,000 Cr","distributed":"₹2,20,000 Cr","year":2015,"ministry":"Ministry of Housing & Urban Affairs","beneficiaries":"2.95 Cr households","riskScore":31,"level":"national","state":"National","desc":"Affordable housing to urban and rural poor. Housing for All Mission by 2024."},
    {"id":"n3","name":"PM-KISAN","utilization":91,"sector":"Agriculture","budget_cr":60000,"budget":"₹60,000 Cr/yr","distributed":"₹80,000 Cr total","year":2019,"ministry":"Ministry of Agriculture & Farmers Welfare","beneficiaries":"11.4 Cr farmers","riskScore":22,"level":"national","state":"National","desc":"Direct income support of ₹6,000/year to all landholding farmer families."},
    {"id":"n4","name":"MGNREGA","utilization":55,"sector":"Employment","budget_cr":60000,"budget":"₹6,000 Cr","distributed":"—","year":2005,"ministry":"Ministry of Rural Development","beneficiaries":"5.5 Cr households","riskScore":57,"level":"national","state":"National","desc":"Guarantees 100 days of wage employment per financial year to rural adult household members."},
    {"id":"n5","name":"PM Ujjwala Yojana","utilization":8,"sector":"Energy/Welfare","budget_cr":12000,"budget":"₹12,000 Cr","distributed":"₹1,000 Cr","year":2016,"ministry":"Ministry of Petroleum & Natural Gas","beneficiaries":"9.59 Cr connections","riskScore":38,"level":"national","state":"National","desc":"Free LPG connections to BPL women households."},
    {"id":"n6","name":"Jan Dhan Yojana","utilization":82,"sector":"Financial Inclusion","budget_cr":20000,"budget":"₹20,000 Cr","distributed":"₹2 Lakh Cr deposits","year":2014,"ministry":"Ministry of Finance","beneficiaries":"51.12 Cr accounts","riskScore":19,"level":"national","state":"National","desc":"National financial inclusion mission."},
    {"id":"n7","name":"PM SVANidhi","utilization":16,"sector":"Small Business","budget_cr":5000,"budget":"₹5,000 Cr","distributed":"₹800 Cr","year":2020,"ministry":"Ministry of Housing & Urban Affairs","beneficiaries":"61.5 Lakh vendors","riskScore":44,"level":"national","state":"National","desc":"Micro-credit for street vendors up to ₹50,000."},
    {"id":"n8","name":"Beti Bachao Beti Padhao","utilization":25,"sector":"Social Welfare","budget_cr":2000,"budget":"₹2,000 Cr","distributed":"₹500 Cr","year":2015,"ministry":"Ministry of Women & Child Development","beneficiaries":"Pan India","riskScore":68,"level":"national","state":"National","desc":"Addresses declining Child Sex Ratio and women empowerment."},
    {"id":"n9","name":"Digital India Mission","utilization":31,"sector":"Technology","budget_cr":130000,"budget":"₹1,30,000 Cr","distributed":"₹40,000 Cr","year":2015,"ministry":"Ministry of Electronics & IT","beneficiaries":"135 Cr citizens","riskScore":26,"level":"national","state":"National","desc":"Transform India into a digitally empowered society."},
    {"id":"n10","name":"PM Surya Ghar Muft Bijli","utilization":79,"sector":"Renewable Energy","budget_cr":75000,"budget":"₹75,000 Cr","distributed":"₹2,75,000 Cr","year":2024,"ministry":"Ministry of New & Renewable Energy","beneficiaries":"1 Cr households (target)","riskScore":35,"level":"national","state":"National","desc":"300 units free electricity/month via rooftop solar."},
]

STATE_SCHEMES = [
    {"id":"s1","name":"Majhi Ladki Bahin Yojana","utilization":51,"sector":"Social Welfare","budget_cr":29570,"budget":"₹29,570 Cr","utilized":"₹15,000 Cr","remaining":"₹14,570 Cr","state":"Maharashtra","purpose":"₹1,500 monthly support to women","riskScore":33,"level":"state"},
    {"id":"s2","name":"Magel Tyala Solar Pump","utilization":48,"sector":"Agriculture","budget_cr":15000,"budget":"₹15,000 Cr","utilized":"₹7,200 Cr","remaining":"₹7,800 Cr","state":"Maharashtra","purpose":"Solar irrigation pumps","riskScore":41,"level":"state"},
    {"id":"s3","name":"Yuva Karya Prashikshan Yojana","utilization":48,"sector":"Employment","budget_cr":6000,"budget":"₹6,000 Cr","utilized":"₹2,900 Cr","remaining":"₹3,100 Cr","state":"Maharashtra","purpose":"Youth internship stipend","riskScore":55,"level":"state"},
    {"id":"s4","name":"Mukhyamantri Annapurna Yojana","utilization":52,"sector":"Welfare","budget_cr":1200,"budget":"₹1,200 Cr","utilized":"₹620 Cr","remaining":"₹580 Cr","state":"Maharashtra","purpose":"Free LPG cylinders","riskScore":30,"level":"state"},
    {"id":"s5","name":"Jal Yukta Shivar Abhiyan","utilization":48,"sector":"Water","budget_cr":650,"budget":"₹650 Cr","utilized":"₹310 Cr","remaining":"₹340 Cr","state":"Maharashtra","purpose":"Water conservation","riskScore":25,"level":"state"},
    {"id":"s6","name":"Gaon Tithe Godown Yojana","utilization":47,"sector":"Agriculture","budget_cr":341,"budget":"₹341 Cr","utilized":"₹160 Cr","remaining":"₹181 Cr","state":"Maharashtra","purpose":"Village crop storage","riskScore":62,"level":"state"},
    {"id":"s7","name":"Solar Rooftop SMART Scheme","utilization":49,"sector":"Energy","budget_cr":655,"budget":"₹655 Cr","utilized":"₹320 Cr","remaining":"₹335 Cr","state":"Maharashtra","purpose":"Rooftop solar for households","riskScore":29,"level":"state"},
    {"id":"s8","name":"Free Higher Education for Girls","utilization":48,"sector":"Education","budget_cr":2000,"budget":"₹2,000 Cr","utilized":"₹950 Cr","remaining":"₹1,050 Cr","state":"Maharashtra","purpose":"Fee reimbursement","riskScore":21,"level":"state"},
    {"id":"s9","name":"Mahatma Phule Jan Arogya Yojana","utilization":50,"sector":"Healthcare","budget_cr":3282,"budget":"₹3,282 Cr","utilized":"₹1,650 Cr","remaining":"₹1,632 Cr","state":"Maharashtra","purpose":"Health insurance ₹5 lakh/family","riskScore":36,"level":"state"},
    {"id":"s10","name":"Maharashtra Irrigation Program","utilization":50,"sector":"Infrastructure","budget_cr":15000,"budget":"₹15,000 Cr","utilized":"₹7,500 Cr","remaining":"₹7,500 Cr","state":"Maharashtra","purpose":"Irrigation canals","riskScore":44,"level":"state"},
]

DISTRICT_SCHEMES = [
    {"id":"d1","name":"NH-60 Highway Widening","utilization":44,"sector":"Roads","budget_cr":95,"budget":"₹95 Cr","utilized":"₹42 Cr","remaining":"₹53 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"4-lane highway widening","riskScore":52,"level":"district"},
    {"id":"d2","name":"Wagholi-Kesnand Rural Road","utilization":43,"sector":"Roads","budget_cr":7.5,"budget":"₹7.5 Cr","utilized":"₹3.2 Cr","remaining":"₹4.3 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Rural road 8 km","riskScore":39,"level":"district"},
    {"id":"d3","name":"Indrayani River Bridge","utilization":53,"sector":"Infrastructure","budget_cr":18,"budget":"₹18 Cr","utilized":"₹9.5 Cr","remaining":"₹8.5 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Bridge construction","riskScore":31,"level":"district"},
    {"id":"d4","name":"Katraj Bus Stand Modernization","utilization":39,"sector":"Transport","budget_cr":3.8,"budget":"₹3.8 Cr","utilized":"₹1.5 Cr","remaining":"₹2.3 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Bus stand development","riskScore":67,"level":"district"},
    {"id":"d5","name":"Pune Junction Improvement","utilization":67,"sector":"Transport","budget_cr":42,"budget":"₹42 Cr","utilized":"₹28 Cr","remaining":"₹14 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Railway station upgrade","riskScore":28,"level":"district"},
    {"id":"d6","name":"Hadapsar Drinking Water Pipeline","utilization":58,"sector":"Water","budget_cr":11,"budget":"₹11 Cr","utilized":"₹6.4 Cr","remaining":"₹4.6 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Drinking water pipeline","riskScore":45,"level":"district"},
    {"id":"d7","name":"Manjari Village Water Tank","utilization":65,"sector":"Water","budget_cr":0.85,"budget":"₹85 L","utilized":"₹55 L","remaining":"₹30 L","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Village water tank","riskScore":22,"level":"district"},
    {"id":"d8","name":"Phursungi Groundwater Recharge","utilization":44,"sector":"Water","budget_cr":0.18,"budget":"₹18 L","utilized":"₹8 L","remaining":"₹10 L","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Borewell recharge","riskScore":18,"level":"district"},
    {"id":"d9","name":"Mulshi Irrigation Canal","utilization":54,"sector":"Agriculture","budget_cr":28,"budget":"₹28 Cr","utilized":"₹15 Cr","remaining":"₹13 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Irrigation canal","riskScore":49,"level":"district"},
    {"id":"d10","name":"Kothrud Rainwater Harvesting","utilization":56,"sector":"Water","budget_cr":1.6,"budget":"₹1.6 Cr","utilized":"₹0.9 Cr","remaining":"₹0.7 Cr","district":"Pune","town":"Shivajinagar","state":"Maharashtra","purpose":"Rainwater harvesting","riskScore":16,"level":"district"},
]

RURAL_SCHEMES = [{**s, "id": s["id"].replace("d","r"), "level":"rural"} for s in DISTRICT_SCHEMES]

ALL_SCHEMES = {
    "Finance Ministry": NATIONWIDE,
    "Chief Economic Advisory": NATIONWIDE,
    "State Department": STATE_SCHEMES,
    "District Administration": DISTRICT_SCHEMES,
    "Rural Administration": RURAL_SCHEMES,
}

def get_schemes_for_user(dept: str) -> list:
    return ALL_SCHEMES.get(dept, NATIONWIDE)


# ── Flask App ─────────────────────────────────────────────────────────
if FLASK_OK:
    app = Flask(__name__)
    CORS(app, origins=["*"])  # Allow all origins for local dev

    def require_dept(f):
        """Decorator: extract dept from query param or JSON body."""
        @wraps(f)
        def decorated(*args, **kwargs):
            dept = request.args.get("dept") or (request.get_json(silent=True) or {}).get("dept", "Finance Ministry")
            return f(dept=dept, *args, **kwargs)
        return decorated

    # ── Health check ─────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "version": "2.1", "time": datetime.now().isoformat()})

    # ── AI Chat ───────────────────────────────────────────────────────
    @app.route("/api/chat", methods=["POST"])
    def chat():
        data    = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        user    = data.get("user", {"name":"User","dept":"Finance Ministry"})
        if not message:
            return jsonify({"error": "message is required"}), 400
        schemes = get_schemes_for_user(user.get("dept","Finance Ministry"))
        response = generate_response(message, user, schemes)
        return jsonify({"success": True, "response": response})

    # ── Risk Scores ───────────────────────────────────────────────────
    @app.route("/api/risk")
    @require_dept
    def risk_scores(dept):
        schemes = get_schemes_for_user(dept)
        summary = get_risk_summary(schemes)
        return jsonify({"success": True, "data": summary})

    @app.route("/api/risk/<scheme_id>")
    def risk_single(scheme_id):
        all_s = NATIONWIDE + STATE_SCHEMES + DISTRICT_SCHEMES + RURAL_SCHEMES
        scheme = next((s for s in all_s if s["id"] == scheme_id), None)
        if not scheme:
            return jsonify({"error": "Scheme not found"}), 404
        result = compute_risk_score(scheme)
        return jsonify({"success": True, "data": result})

    # ── Anomaly Detection ─────────────────────────────────────────────
    @app.route("/api/anomalies")
    @require_dept
    def anomalies(dept):
        schemes = get_schemes_for_user(dept)
        summary = get_anomaly_summary(schemes)
        return jsonify({"success": True, "data": summary})

    @app.route("/api/anomalies/<anomaly_id>/resolve", methods=["POST"])
    def resolve(anomaly_id):
        data = request.get_json(silent=True) or {}
        result = resolve_anomaly(anomaly_id, data.get("resolved_by","Unknown"), data.get("note",""))
        return jsonify({"success": True, "data": result})

    # ── GeoMap ────────────────────────────────────────────────────────
    @app.route("/api/map")
    @require_dept
    def geo_map(dept):
        schemes = get_schemes_for_user(dept)
        overview = get_department_map_overview(schemes, dept)
        return jsonify({"success": True, "data": overview})

    @app.route("/api/map/scheme/<scheme_id>")
    def scheme_map(scheme_id):
        all_s = NATIONWIDE + STATE_SCHEMES + DISTRICT_SCHEMES + RURAL_SCHEMES
        scheme = next((s for s in all_s if s["id"] == scheme_id), None)
        if not scheme:
            return jsonify({"error": "Scheme not found"}), 404
        data = get_scheme_map_data(scheme)
        return jsonify({"success": True, "data": data})

    @app.route("/api/map/geojson")
    @require_dept
    def geojson(dept):
        schemes = get_schemes_for_user(dept)
        return jsonify(get_schemes_geojson(schemes))

    # ── Budget Simulation ─────────────────────────────────────────────
    @app.route("/api/simulate", methods=["POST"])
    def simulate():
        data    = request.get_json(silent=True) or {}
        dept    = data.get("dept", "Finance Ministry")
        schemes = get_schemes_for_user(dept)
        result  = simulate_reallocation(
            schemes,
            increase_pct=float(data.get("budget_increase", 0)),
            efficiency_target=float(data.get("efficiency_target", 0)),
            focus_sectors=data.get("focus_sectors", []),
            risk_reduction_target=float(data.get("risk_reduction", 0)),
        )
        return jsonify({"success": True, "data": result})

    @app.route("/api/recommendations")
    @require_dept
    def recommendations(dept):
        schemes = get_schemes_for_user(dept)
        recs    = get_reallocation_recommendations(schemes)
        return jsonify({"success": True, "data": recs})

    # ── PDF Generation ────────────────────────────────────────────────
    @app.route("/api/pdf/scheme", methods=["POST"])
    def pdf_scheme():
        data      = request.get_json(silent=True) or {}
        scheme_id = data.get("scheme_id")
        user      = data.get("user", {"name":"User","dept":"Finance Ministry"})
        all_s     = NATIONWIDE + STATE_SCHEMES + DISTRICT_SCHEMES + RURAL_SCHEMES
        scheme    = next((s for s in all_s if s["id"] == scheme_id), None)
        if not scheme:
            return jsonify({"error": "Scheme not found"}), 404
        pdf_bytes = generate_scheme_pdf(scheme, user)
        fname     = f"Scheme_{scheme['id']}_{scheme['name'][:20].replace(' ','_')}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes) if isinstance(pdf_bytes, bytes) else io.BytesIO(pdf_bytes.encode()),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=fname,
        )

    @app.route("/api/pdf/report", methods=["POST"])
    def pdf_report():
        data       = request.get_json(silent=True) or {}
        dept       = data.get("dept", "Finance Ministry")
        user       = data.get("user", {"name":"User","dept": dept})
        rtype      = data.get("report_type", "full")
        period     = data.get("period", "FY 2025-26")
        schemes    = get_schemes_for_user(dept)
        if rtype == "risk":
            pdf_bytes = generate_risk_report(schemes, user)
        elif rtype == "anomaly":
            pdf_bytes = generate_anomaly_report(schemes, user)
        else:
            pdf_bytes = generate_department_report(schemes, user, rtype, period)
        fname = f"ArthRakshak_{rtype}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes) if isinstance(pdf_bytes, bytes) else io.BytesIO(pdf_bytes.encode()),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=fname,
        )

    # ── Dashboard Stats ───────────────────────────────────────────────
    @app.route("/api/stats")
    @require_dept
    def stats(dept):
        schemes   = get_schemes_for_user(dept)
        utils     = [s.get("utilization",0) for s in schemes]
        risks     = [s.get("riskScore",0) for s in schemes]
        avg_u     = round(sum(utils)/len(utils)) if utils else 0
        avg_r     = round(sum(risks)/len(risks)) if risks else 0
        sectors   = {}
        for s in schemes:
            sec = s.get("sector","Other")
            sectors[sec] = sectors.get(sec, 0) + 1
        return jsonify({
            "success": True,
            "data": {
                "total_schemes":   len(schemes),
                "avg_utilization": avg_u,
                "avg_risk":        avg_r,
                "high_risk_count": len([s for s in schemes if s.get("riskScore",0)>=55]),
                "low_util_count":  len([s for s in schemes if s.get("utilization",0)<30]),
                "sector_dist":     sectors,
                "dept":            dept,
                "generated_at":    datetime.now().isoformat(),
            }
        })

    # ── Run Server ────────────────────────────────────────────────────
    if __name__ == "__main__":
        print("=" * 60)
        print("  ArthRakshak Backend API Server v2.1")
        print("  http://localhost:5050")
        print("=" * 60)
        print("\n  Endpoints:")
        print("  GET  /api/health")
        print("  POST /api/chat")
        print("  GET  /api/risk?dept=Finance+Ministry")
        print("  GET  /api/anomalies?dept=Finance+Ministry")
        print("  GET  /api/map?dept=Finance+Ministry")
        print("  POST /api/simulate")
        print("  POST /api/pdf/scheme")
        print("  POST /api/pdf/report")
        print("  GET  /api/stats?dept=Finance+Ministry")
        print("\n  Frontend: open frontend/login.html in browser")
        print("=" * 60)
        app.run(debug=True, port=5050, host="0.0.0.0")

else:
    # ── CLI mode if Flask not installed ──────────────────────────────
    if __name__ == "__main__":
        print("ArthRakshak Backend — Running in CLI test mode (Flask not installed)")
        print("Install: pip install flask flask-cors")
        print()

        dept    = "Finance Ministry"
        schemes = NATIONWIDE
        user    = {"name":"Anil Kumar","dept":dept}

        print(f"Testing with dept: {dept} ({len(schemes)} schemes)")

        risk_s = get_risk_summary(schemes)
        print(f"\n✅ Risk Summary: avg={risk_s['average_score']}, high={risk_s['high_count']}, critical={risk_s['critical_count']}")

        anom = get_anomaly_summary(schemes)
        print(f"✅ Anomalies: {anom['total_anomalies']} found, ₹{anom['total_at_risk_cr']} Cr at risk")

        resp = generate_response("Which schemes have high risk?", user, schemes)
        print(f"✅ AI Response ({resp['intent']}): {resp['text'][:100]}...")

        geo = get_scheme_map_data(schemes[0])
        print(f"✅ Map: {schemes[0]['name']} → ({geo['latitude']}, {geo['longitude']})")
        print(f"   Google Maps: {geo['maps_url'][:80]}...")

        sim = simulate_reallocation(schemes[:5], increase_pct=10, efficiency_target=8)
        print(f"✅ Simulation: util gain +{sim['deltas']['utilization_gain']}%, risk reduction -{sim['deltas']['risk_reduction']}")

        pdf = generate_scheme_pdf(schemes[0], user)
        print(f"✅ PDF: {len(pdf)} bytes generated for {schemes[0]['name']}")

        print("\n✅ All backend modules working correctly!")