"""
ArthRakshak — GeoMap Engine
Generates Google Maps URLs, coordinates, and location data for schemes.
"""

from urllib.parse import quote_plus
from typing import Optional


# ── Known location coordinates ────────────────────────────────────────
LOCATION_DB = {
    # States
    "Maharashtra":     (19.7515, 75.7139),
    "Delhi":           (28.6139, 77.2090),
    "Gujarat":         (22.2587, 71.1924),
    "Karnataka":       (15.3173, 75.7139),
    "Tamil Nadu":      (11.1271, 78.6569),
    "Rajasthan":       (27.0238, 74.2179),
    "Uttar Pradesh":   (26.8467, 80.9462),
    "West Bengal":     (22.9868, 87.8550),
    "Madhya Pradesh":  (22.9734, 78.6569),
    "Andhra Pradesh":  (15.9129, 79.7400),
    "National":        (20.5937, 78.9629),  # India center
    # Cities / Districts
    "Pune":            (18.5204, 73.8567),
    "Mumbai":          (19.0760, 72.8777),
    "Nagpur":          (21.1458, 79.0882),
    "Nashik":          (19.9975, 73.7898),
    "Aurangabad":      (19.8762, 75.3433),
    "Shivajinagar":    (18.5314, 73.8446),
    "New Delhi":       (28.6139, 77.2090),
    "Bengaluru":       (12.9716, 77.5946),
    "Chennai":         (13.0827, 80.2707),
    "Hyderabad":       (17.3850, 78.4867),
    "Kolkata":         (22.5726, 88.3639),
    "Ahmedabad":       (23.0225, 72.5714),
    "Jaipur":          (26.9124, 75.7873),
    "Lucknow":         (26.8467, 80.9462),
}

# Sector → map layer icon
SECTOR_ICONS = {
    "Roads":             "🛣️",
    "Infrastructure":    "🏗️",
    "Transport":         "🚌",
    "Water":             "💧",
    "Healthcare":        "🏥",
    "Education":         "🎓",
    "Agriculture":       "🌾",
    "Housing":           "🏘️",
    "Employment":        "👷",
    "Energy":            "⚡",
    "Renewable Energy":  "☀️",
    "Social Welfare":    "🤝",
    "Financial Inclusion":"🏦",
    "Technology":        "💻",
    "Small Business":    "🏪",
}


def get_scheme_coordinates(scheme: dict) -> tuple[float, float]:
    """Return (lat, lng) for a scheme based on its location fields."""
    # Try district first, then state, then national
    for field in ["town", "district", "state"]:
        val = scheme.get(field)
        if val and val != "National":
            coords = LOCATION_DB.get(val)
            if coords:
                return coords

    # Fallback to India center
    return LOCATION_DB["National"]


def build_google_maps_url(scheme: dict, mode: str = "search") -> str:
    """
    Build a Google Maps URL for a scheme.
    mode: 'search' | 'directions' | 'embed'
    """
    lat, lng = get_scheme_coordinates(scheme)
    name = scheme.get("name", "Government Scheme")
    loc_parts = []
    for field in ["town", "district", "state"]:
        val = scheme.get(field)
        if val and val != "National":
            loc_parts.append(val)
    location = ", ".join(loc_parts) if loc_parts else "India"
    query = quote_plus(f"{name}, {location}")

    if mode == "search":
        return f"https://www.google.com/maps/search/?api=1&query={query}"
    elif mode == "directions":
        return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
    elif mode == "embed":
        return f"https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q={query}&center={lat},{lng}&zoom=12"
    else:
        return f"https://www.google.com/maps/search/?api=1&query={query}"


def build_maps_url_by_location(location: str, query: str = "") -> str:
    """Build Google Maps URL for a named location."""
    full_query = f"{query} {location}".strip() if query else location
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(full_query)}"


def get_schemes_geojson(schemes: list) -> dict:
    """
    Return GeoJSON FeatureCollection for all schemes.
    Can be rendered on a Leaflet/Mapbox map.
    """
    features = []
    for scheme in schemes:
        lat, lng = get_scheme_coordinates(scheme)
        risk = scheme.get("riskScore", 0)
        util = scheme.get("utilization", 0)
        sector = scheme.get("sector", "General")
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "id":           scheme.get("id", ""),
                "name":         scheme.get("name", ""),
                "sector":       sector,
                "icon":         SECTOR_ICONS.get(sector, "📍"),
                "utilization":  util,
                "risk_score":   risk,
                "risk_level":   _risk_level(risk),
                "risk_color":   _risk_color(risk),
                "budget":       scheme.get("budget", "—"),
                "maps_url":     build_google_maps_url(scheme),
                "popup_html":   _build_popup(scheme),
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features,
        "meta": {
            "total":        len(features),
            "generated_at": __import__("datetime").datetime.now().isoformat(),
        }
    }


def get_scheme_map_data(scheme: dict) -> dict:
    """Return all map-related data for a single scheme."""
    lat, lng = get_scheme_coordinates(scheme)
    return {
        "scheme_id":    scheme.get("id"),
        "scheme_name":  scheme.get("name"),
        "latitude":     lat,
        "longitude":    lng,
        "maps_url":     build_google_maps_url(scheme, "search"),
        "directions_url": build_google_maps_url(scheme, "directions"),
        "embed_url":    build_google_maps_url(scheme, "embed"),
        "location":     _get_location_label(scheme),
        "sector_icon":  SECTOR_ICONS.get(scheme.get("sector",""), "📍"),
    }


def get_department_map_overview(schemes: list, dept: str) -> dict:
    """Return map overview for a department — cluster of scheme pins."""
    geo = get_schemes_geojson(schemes)
    lats = [f["geometry"]["coordinates"][1] for f in geo["features"]]
    lngs = [f["geometry"]["coordinates"][0] for f in geo["features"]]
    center_lat = sum(lats)/len(lats) if lats else 20.5937
    center_lng = sum(lngs)/len(lngs) if lngs else 78.9629
    overview_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(dept + ' India')}"
    return {
        "dept":        dept,
        "center":      {"lat": round(center_lat, 4), "lng": round(center_lng, 4)},
        "overview_url": overview_url,
        "geojson":     geo,
        "scheme_count": len(schemes),
    }


# ── Internal helpers ──────────────────────────────────────────────────
def _risk_level(score: int) -> str:
    if score < 30: return "low"
    if score < 55: return "medium"
    if score < 75: return "high"
    return "critical"

def _risk_color(score: int) -> str:
    if score < 30: return "#1a7a4a"
    if score < 55: return "#f59e0b"
    if score < 75: return "#c0392b"
    return "#5b21b6"

def _get_location_label(scheme: dict) -> str:
    parts = []
    for f in ["town", "district", "state"]:
        v = scheme.get(f)
        if v and v != "National":
            parts.append(v)
    return ", ".join(parts) if parts else "Pan India"

def _build_popup(scheme: dict) -> str:
    risk = scheme.get("riskScore", 0)
    util = scheme.get("utilization", 0)
    color = _risk_color(risk)
    maps_url = build_google_maps_url(scheme)
    return (
        f'<div style="font-family:sans-serif;min-width:200px">'
        f'<strong style="color:#002147">{scheme.get("name","")}</strong><br>'
        f'<span style="font-size:11px;color:#64748b">{scheme.get("sector","")}</span><br><br>'
        f'Utilization: <strong>{util}%</strong><br>'
        f'Risk: <strong style="color:{color}">{risk}/100</strong><br><br>'
        f'<a href="{maps_url}" target="_blank" style="color:#002147;font-weight:700">📍 Open in Google Maps</a>'
        f'</div>'
    )


# ── Standalone test ───────────────────────────────────────────────────
if __name__ == "__main__":
    test_schemes = [
        {"id":"d1","name":"NH-60 Highway Widening","sector":"Roads","district":"Pune","state":"Maharashtra","utilization":44,"riskScore":52,"budget":"₹95 Cr"},
        {"id":"d3","name":"Indrayani River Bridge","sector":"Infrastructure","district":"Pune","state":"Maharashtra","utilization":53,"riskScore":31,"budget":"₹18 Cr"},
        {"id":"n1","name":"PM-KISAN","sector":"Agriculture","state":"National","utilization":91,"riskScore":22,"budget":"₹60,000 Cr"},
    ]
    for s in test_schemes:
        data = get_scheme_map_data(s)
        print(f"📍 {s['name']}")
        print(f"   Coords: ({data['latitude']}, {data['longitude']})")
        print(f"   Maps: {data['maps_url'][:80]}...")
        print()
    
    overview = get_department_map_overview(test_schemes[:2], "District Administration")
    print(f"Dept Overview: center=({overview['center']['lat']}, {overview['center']['lng']})")
    print(f"GeoJSON features: {len(overview['geojson']['features'])}")