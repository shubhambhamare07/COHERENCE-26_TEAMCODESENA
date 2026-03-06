"""
ArthRakshak – National Budget Intelligence Platform
====================================================
FastAPI backend entrypoint.

Run with:
    uvicorn main:app --reload

Author: ArthRakshak Dev Team
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
import os

# ── Module imports ────────────────────────────────────────────────────────────
from modules.risk_score import compute_risk_scores
from modules.anomaly_detection import detect_anomalies
from modules.geomap import get_scheme_locations
from modules.reallocation_simulator import simulate_reallocation
from modules.pdf_generator import generate_report
from modules.ai_assistant import answer_query

# ── App initialisation ────────────────────────────────────────────────────────
app = FastAPI(
    title="ArthRakshak – National Budget Intelligence Platform",
    description=(
        "Detect budget anomalies, score corruption risk, visualise schemes on maps, "
        "simulate reallocation, generate government-style PDF reports, and query an "
        "AI assistant – all through a single RESTful API."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow all origins for hackathon frontend) ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Dataset path ──────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "budget_data.csv")


def load_data() -> pd.DataFrame:
    """
    Load the national budget dataset from CSV.

    Returns:
        pd.DataFrame: Parsed budget data.

    Raises:
        HTTPException 500: If the file is missing or unreadable.
    """
    if not os.path.exists(DATA_PATH):
        raise HTTPException(
            status_code=500,
            detail=f"Budget dataset not found at '{DATA_PATH}'. "
                   "Please ensure data/budget_data.csv exists.",
        )
    return pd.read_csv(DATA_PATH)


# ── Request / Response schemas ────────────────────────────────────────────────

class SimulateRequest(BaseModel):
    """Payload for budget reallocation simulation."""
    from_city: str = Field(..., example="Mumbai", description="Source city name")
    to_city: str = Field(..., example="Nagpur", description="Destination city name")
    amount: float = Field(..., gt=0, example=200_000_000, description="Amount in INR to reallocate")


class AssistantRequest(BaseModel):
    """Payload for the AI assistant query."""
    query: str = Field(..., example="Which city has highest corruption risk?",
                       description="Natural-language question about budget data")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get(
    "/",
    tags=["Health"],
    summary="Health Check",
    response_description="Platform status and version",
)
async def health_check():
    """
    **Health Check**

    Returns a simple status message confirming the API is running and
    lists available module endpoints.
    """
    return {
        "status": "ok",
        "platform": "ArthRakshak – National Budget Intelligence Platform",
        "version": "1.0.0",
        "endpoints": [
            "GET  /risk-scores",
            "GET  /anomalies",
            "GET  /schemes/map",
            "POST /simulate",
            "GET  /report",
            "POST /assistant",
        ],
    }


@app.get(
    "/risk-scores",
    tags=["Risk Analysis"],
    summary="Corruption Risk Scores",
    response_description="City-level corruption risk scores and ranking",
)
async def get_risk_scores():
    """
    **Corruption Risk Scores**

    Reads budget data and computes a composite corruption-risk score for
    every city / district using heuristics such as:
    - Budget utilisation rate
    - Discrepancy between allocated and spent amounts
    - Historical anomaly frequency

    Returns a ranked JSON list so the frontend can render league tables
    and choropleth maps.
    """
    df = load_data()
    scores = compute_risk_scores(df)
    return JSONResponse(content={"risk_scores": scores})


@app.get(
    "/anomalies",
    tags=["Anomaly Detection"],
    summary="Detected Budget Anomalies",
    response_description="List of anomalous budget entries with severity flags",
)
async def get_anomalies():
    """
    **Budget Anomaly Detection**

    Runs statistical anomaly detection (Z-score / IQR fence) over the
    budget dataset and returns entries that deviate significantly from
    expected spending patterns.

    Each record includes:
    - `city` / `scheme`
    - `allocated` and `spent` amounts
    - `anomaly_type` (over-spend, under-utilisation, suspicious spike …)
    - `severity` (low / medium / high)
    """
    df = load_data()
    anomalies = detect_anomalies(df)
    return JSONResponse(content={"anomalies": anomalies, "total": len(anomalies)})


@app.get(
    "/schemes/map",
    tags=["Geospatial"],
    summary="Scheme Locations for Map Visualisation",
    response_description="GeoJSON-compatible list of scheme locations with coordinates",
)
async def get_map_data():
    """
    **Scheme Geo-locations**

    Returns latitude/longitude coordinates for each government scheme
    enriched with budget allocation metadata so the frontend can render
    an interactive Leaflet / Mapbox map.

    Each feature includes:
    - `scheme_name`
    - `city` / `state`
    - `lat`, `lng`
    - `allocated_budget` (INR)
    - `risk_level`
    """
    df = load_data()
    locations = get_scheme_locations(df)
    return JSONResponse(content={"type": "FeatureCollection", "features": locations})


@app.post(
    "/simulate",
    tags=["Simulation"],
    summary="Budget Reallocation Simulator",
    response_description="Impact analysis of the proposed budget transfer",
)
async def simulate(request: SimulateRequest):
    """
    **Budget Reallocation Simulation**

    Simulates the fiscal and social impact of moving funds from one city
    to another.

    **Request body:**
    ```json
    {
        "from_city": "Mumbai",
        "to_city":   "Nagpur",
        "amount":    200000000
    }
    ```

    **Returns:**
    - Projected change in risk scores for both cities
    - Estimated beneficiary count
    - Recommended scheme targets in the destination city
    - Warnings if the source city drops below safe-spend thresholds
    """
    df = load_data()
    result = simulate_reallocation(
        df=df,
        from_city=request.from_city,
        to_city=request.to_city,
        amount=request.amount,
    )
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return JSONResponse(content=result)


@app.get(
    "/report",
    tags=["Reporting"],
    summary="Generate Government-Style PDF Report",
    response_description="PDF file download of the budget intelligence report",
)
async def get_report():
    """
    **Government PDF Report**

    Generates a formatted PDF report in the style of official Government
    of India budget documents.  The report includes:

    - Executive Summary
    - City-wise risk score table
    - Top anomalies section
    - Recommendations for reallocation

    The PDF is returned as a file download (`Content-Type: application/pdf`).
    """
    df = load_data()
    pdf_path = generate_report(df)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="PDF generation failed.")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="ArthRakshak_Budget_Report.pdf",
    )


@app.post(
    "/assistant",
    tags=["AI Assistant"],
    summary="AI Budget Intelligence Query",
    response_description="Natural-language answer from the AI assistant",
)
async def assistant(request: AssistantRequest):
    """
    **AI Budget Assistant**

    Accepts a natural-language question about the national budget data and
    returns an intelligent, context-aware answer powered by an LLM.

    **Example queries:**
    - *"Which city has the highest corruption risk?"*
    - *"Show me schemes with under-utilisation above 40 %."*
    - *"What is the total allocated budget for Maharashtra?"*

    **Request body:**
    ```json
    { "query": "Which city has highest corruption risk?" }
    ```

    The assistant is grounded in the live `budget_data.csv` dataset, so
    answers reflect real figures rather than hallucinated values.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    df = load_data()
    response = answer_query(query=request.query, df=df)
    return JSONResponse(content={"query": request.query, "answer": response})