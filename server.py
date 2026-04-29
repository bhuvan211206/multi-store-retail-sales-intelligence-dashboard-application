"""
NEXUS — Retail Intelligence API Server
========================================
FastAPI backend powering the NEXUS dashboard.

Run:
    python server.py
    # or: python -m uvicorn server:app --reload --port 8000

Endpoints:
    GET  /                          → Health check & API info
    GET  /api/health                → System health + uptime
    GET  /api/data                  → Full enriched dataset (with filters)
    GET  /api/kpis                  → Aggregated KPI metrics
    GET  /api/stores                → Store-level aggregation
    GET  /api/categories            → Category-level aggregation
    GET  /api/trends                → Monthly trend data
    GET  /api/stock/summary         → Inventory health summary
    GET  /api/stock/critical        → Critical restock queue
    GET  /api/stock/velocity        → Stock velocity quadrant data
    GET  /api/correlation           → Metric correlation matrix
    GET  /api/filters               → Available filter options
    POST /api/upload                → Upload new CSV data
"""

import os
import time
import datetime
import numpy as np
import pandas as pd
from io import StringIO
from typing import Optional
from fastapi import FastAPI, Query, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# ══════════════════════════════════════════════════════════════════════════════
# APP INIT
# ══════════════════════════════════════════════════════════════════════════════
app = FastAPI(
    title="NEXUS Retail Intelligence API",
    description="REST API backend for the NEXUS Retail Dashboard — serves enriched sales, "
                "inventory, and performance data with real-time filtering and aggregation.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the Streamlit frontend (and any other origin) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ══════════════════════════════════════════════════════════════════════════════
# STARTUP TIME (for uptime tracking)
# ══════════════════════════════════════════════════════════════════════════════
_SERVER_START = time.time()

# ══════════════════════════════════════════════════════════════════════════════
# DATA ENGINE
# ══════════════════════════════════════════════════════════════════════════════
CSV_PATH = os.path.join(os.path.dirname(__file__), "store_sales_data.csv")

MO_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich raw sales data with derived stock & performance columns."""
    out = df.copy()
    np.random.seed(42)
    n = len(out)

    if "Current_Stock" not in out.columns:
        out["Current_Stock"] = (out["Units_Sold"] * np.random.uniform(0.5, 3.0, size=n)).astype(int)
    if "Reorder_Point" not in out.columns:
        out["Reorder_Point"] = (out["Units_Sold"] * 0.4).astype(int).clip(lower=5)
    if "Unit_Cost_Rs" not in out.columns:
        out["Unit_Cost_Rs"] = (out["Avg_Basket_Size_Rs"] * np.random.uniform(0.4, 0.7, size=n)).round(0)
    if "Product" not in out.columns:
        suffix = np.random.randint(100, 999, size=n).astype(str)
        out["Product"] = out["Category"] + " — SKU" + suffix

    out["Stock_Value_Lakhs"] = (out["Current_Stock"] * out["Unit_Cost_Rs"] / 100_000).round(2)
    out["Stock_Status"] = np.where(
        out["Current_Stock"] <= 0, "Out of Stock",
        np.where(out["Current_Stock"] <= out["Reorder_Point"], "Low Stock", "Healthy"),
    )
    out["Revenue_Per_Footfall"] = (out["Revenue_Lakhs"] / out["Daily_Footfall"].replace(0, np.nan)).round(4)
    out["Margin_Value_Lakhs"] = (out["Revenue_Lakhs"] * out["Gross_Margin_Pct"] / 100).round(2)

    return out


def _load_and_enrich(path: str = CSV_PATH) -> pd.DataFrame:
    """Load CSV from disk and enrich."""
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return _enrich(df)


# In-memory dataframe (reloaded on upload)
_df: pd.DataFrame = pd.DataFrame()

try:
    _df = _load_and_enrich()
except FileNotFoundError:
    print("⚠  store_sales_data.csv not found — start with POST /api/upload")


def _get_df() -> pd.DataFrame:
    """Return current in-memory dataframe or raise 404."""
    if _df.empty:
        raise HTTPException(status_code=404, detail="No data loaded. Upload a CSV via POST /api/upload")
    return _df


def _apply_filters(
    df: pd.DataFrame,
    stores: Optional[list[str]] = None,
    categories: Optional[list[str]] = None,
    months: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Apply optional filter lists to the dataframe."""
    if stores:
        df = df[df["Store"].isin(stores)]
    if categories:
        df = df[df["Category"].isin(categories)]
    if months:
        df = df[df["Month"].isin(months)]
    return df


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
def root():
    return {
        "name": "NEXUS Retail Intelligence API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": [
            "/api/health", "/api/data", "/api/kpis", "/api/stores",
            "/api/categories", "/api/trends", "/api/stock/summary",
            "/api/stock/critical", "/api/stock/velocity",
            "/api/correlation", "/api/filters", "/api/upload",
        ],
    }


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
def health():
    uptime_s = time.time() - _SERVER_START
    h, rem = divmod(int(uptime_s), 3600)
    m, s = divmod(rem, 60)
    return {
        "status": "healthy",
        "uptime": f"{h}h {m}m {s}s",
        "uptime_seconds": round(uptime_s, 1),
        "records_loaded": len(_df),
        "server_time": datetime.datetime.now().isoformat(),
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
    }


# ── Available filter options ──────────────────────────────────────────────────
@app.get("/api/filters", tags=["Filters"])
def filters():
    df = _get_df()
    return {
        "stores": sorted(set(df["Store"].dropna())),
        "categories": sorted(set(df["Category"].dropna())),
        "months": [m for m in MO_ORDER if m in set(df["Month"].dropna())],
        "regions": sorted(set(df["Region"].dropna())) if "Region" in df.columns else [],
        "stock_statuses": sorted(set(df["Stock_Status"].dropna())),
    }


# ── Full data (with optional filters) ────────────────────────────────────────
@app.get("/api/data", tags=["Data"])
def get_data(
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
    month: Optional[list[str]] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    df = _apply_filters(_get_df(), store, category, month)
    total = len(df)
    page = df.iloc[offset: offset + limit]
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "count": len(page),
        "data": page.fillna("").to_dict(orient="records"),
    }


# ── KPI summary ──────────────────────────────────────────────────────────────
@app.get("/api/kpis", tags=["Analytics"])
def kpis(
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
    month: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), store, category, month)
    if df.empty:
        raise HTTPException(400, "Filters returned 0 records")

    total_rev    = round(float(df["Revenue_Lakhs"].sum()), 2)
    total_target = float(df["Annual_Target_Lakhs"].sum())
    attainment   = round(total_rev / total_target * 100, 1) if total_target else 0.0

    return {
        "records": len(df),
        "total_revenue_lakhs": total_rev,
        "total_target_lakhs": round(total_target, 2),
        "target_attainment_pct": attainment,
        "avg_gross_margin_pct": round(float(df["Gross_Margin_Pct"].mean()), 2),
        "avg_conversion_rate_pct": round(float(df["Conversion_Rate_Pct"].mean()), 2),
        "avg_basket_size_rs": round(float(df["Avg_Basket_Size_Rs"].mean()), 0),
        "total_units_sold": int(df["Units_Sold"].sum()),
        "total_footfall": int(df["Daily_Footfall"].sum()),
        "margin_value_lakhs": round(float(df["Margin_Value_Lakhs"].sum()), 2),
        "total_stock_value_lakhs": round(float(df["Stock_Value_Lakhs"].sum()), 2),
        "unique_stores": len(set(df["Store"])),
        "unique_categories": len(set(df["Category"])),
    }


# ── Store-level aggregation ───────────────────────────────────────────────────
@app.get("/api/stores", tags=["Analytics"])
def stores_agg(
    category: Optional[list[str]] = Query(None),
    month: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), categories=category, months=month)
    agg = df.groupby("Store").agg(
        total_revenue=("Revenue_Lakhs", "sum"),
        target=("Annual_Target_Lakhs", "first"),
        avg_margin=("Gross_Margin_Pct", "mean"),
        avg_conversion=("Conversion_Rate_Pct", "mean"),
        avg_basket=("Avg_Basket_Size_Rs", "mean"),
        total_units=("Units_Sold", "sum"),
        total_footfall=("Daily_Footfall", "sum"),
        margin_value=("Margin_Value_Lakhs", "sum"),
    ).reset_index()

    agg["attainment_pct"] = (agg["total_revenue"] / agg["target"].replace(0, np.nan) * 100).round(1).fillna(0)

    # Round floats
    for c in agg.select_dtypes(include="float").columns:
        agg[c] = agg[c].round(2)

    return {"count": len(agg), "stores": agg.to_dict(orient="records")}


# ── Category-level aggregation ────────────────────────────────────────────────
@app.get("/api/categories", tags=["Analytics"])
def categories_agg(
    store: Optional[list[str]] = Query(None),
    month: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), stores=store, months=month)
    agg = df.groupby("Category").agg(
        total_revenue=("Revenue_Lakhs", "sum"),
        avg_margin=("Gross_Margin_Pct", "mean"),
        avg_basket=("Avg_Basket_Size_Rs", "mean"),
        total_units=("Units_Sold", "sum"),
        stock_value=("Stock_Value_Lakhs", "sum"),
    ).reset_index()

    for c in agg.select_dtypes(include="float").columns:
        agg[c] = agg[c].round(2)

    return {"count": len(agg), "categories": agg.to_dict(orient="records")}


# ── Monthly trends ────────────────────────────────────────────────────────────
@app.get("/api/trends", tags=["Analytics"])
def trends(
    metric: str = Query("Revenue_Lakhs"),
    group_by: str = Query("Category"),
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
    month: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), store, category, month)

    valid_metrics = [
        "Revenue_Lakhs", "Gross_Margin_Pct", "Daily_Footfall",
        "Conversion_Rate_Pct", "Avg_Basket_Size_Rs", "Units_Sold",
        "Margin_Value_Lakhs", "Stock_Value_Lakhs",
    ]
    if metric not in valid_metrics:
        raise HTTPException(400, f"metric must be one of {valid_metrics}")
    if group_by not in ("Category", "Store"):
        raise HTTPException(400, "group_by must be 'Category' or 'Store'")

    pivot = df.groupby(["Month", group_by])[metric].mean().unstack().fillna(0)
    # Reorder months
    active = [m for m in MO_ORDER if m in pivot.index]
    pivot = pivot.reindex(active)

    result = []
    for mo in pivot.index:
        row = {"month": mo}
        for col in pivot.columns:
            row[col] = round(float(pivot.loc[mo, col]), 2)
        result.append(row)

    return {
        "metric": metric,
        "group_by": group_by,
        "months": active,
        "groups": list(pivot.columns),
        "data": result,
    }


# ── Stock summary ─────────────────────────────────────────────────────────────
@app.get("/api/stock/summary", tags=["Inventory"])
def stock_summary(
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), store, category)
    return {
        "total_stock_value_lakhs": round(float(df["Stock_Value_Lakhs"].sum()), 2),
        "total_units_on_hand": int(df["Current_Stock"].sum()),
        "total_skus": len(df),
        "healthy": int((df["Stock_Status"] == "Healthy").sum()),
        "low_stock": int((df["Stock_Status"] == "Low Stock").sum()),
        "out_of_stock": int((df["Stock_Status"] == "Out of Stock").sum()),
        "health_rate_pct": round(
            (df["Stock_Status"] == "Healthy").sum() / len(df) * 100, 1
        ) if len(df) else 0,
        "by_category": (
            df.groupby("Category")
            .agg(stock_value=("Stock_Value_Lakhs", "sum"),
                 units=("Current_Stock", "sum"))
            .round(2)
            .reset_index()
            .to_dict(orient="records")
        ),
        "by_store": (
            df.groupby("Store")
            .agg(stock_value=("Stock_Value_Lakhs", "sum"),
                 units=("Current_Stock", "sum"),
                 low=("Stock_Status", lambda x: (x == "Low Stock").sum()),
                 oos=("Stock_Status", lambda x: (x == "Out of Stock").sum()))
            .round(2)
            .reset_index()
            .to_dict(orient="records")
        ),
    }


# ── Critical restock queue ────────────────────────────────────────────────────
@app.get("/api/stock/critical", tags=["Inventory"])
def stock_critical(
    limit: int = Query(25, ge=1, le=100),
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), store, category)
    crit = (
        df[df["Stock_Status"].isin(["Out of Stock", "Low Stock"])]
        .sort_values("Current_Stock")
        .head(limit)
    )
    cols = ["Store", "Category", "Product", "Current_Stock", "Reorder_Point",
            "Units_Sold", "Stock_Value_Lakhs", "Stock_Status"]
    return {
        "count": len(crit),
        "items": crit[cols].to_dict(orient="records"),
    }


# ── Stock velocity quadrant ──────────────────────────────────────────────────
@app.get("/api/stock/velocity", tags=["Inventory"])
def stock_velocity(
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), store, category)
    cols = ["Product", "Store", "Category", "Units_Sold", "Current_Stock",
            "Stock_Value_Lakhs", "Stock_Status"]
    points = df[cols].copy()
    points["median_stock"] = float(df["Current_Stock"].median())
    points["median_sales"] = float(df["Units_Sold"].median())

    for c in points.select_dtypes(include="float").columns:
        points[c] = points[c].round(2)

    return {
        "count": len(points),
        "median_stock": round(float(df["Current_Stock"].median()), 0),
        "median_sales": round(float(df["Units_Sold"].median()), 0),
        "data": points.to_dict(orient="records"),
    }


# ── Correlation matrix ────────────────────────────────────────────────────────
@app.get("/api/correlation", tags=["Analytics"])
def correlation(
    store: Optional[list[str]] = Query(None),
    category: Optional[list[str]] = Query(None),
    month: Optional[list[str]] = Query(None),
):
    df = _apply_filters(_get_df(), store, category, month)
    num_cols = [
        "Revenue_Lakhs", "Gross_Margin_Pct", "Daily_Footfall",
        "Conversion_Rate_Pct", "Avg_Basket_Size_Rs", "Units_Sold",
    ]
    corr = df[num_cols].corr().round(3)
    return {
        "columns": num_cols,
        "matrix": corr.values.tolist(),
    }


# ── Upload new CSV ────────────────────────────────────────────────────────────
@app.post("/api/upload", tags=["Data"])
async def upload_csv(file: UploadFile = File(...)):
    global _df
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only .csv files are accepted")

    content = await file.read()
    try:
        raw = pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(400, f"Failed to parse CSV: {e}")

    required = {"Store", "Month", "Category", "Revenue_Lakhs",
                "Annual_Target_Lakhs", "Gross_Margin_Pct", "Daily_Footfall",
                "Conversion_Rate_Pct", "Avg_Basket_Size_Rs", "Units_Sold"}
    raw.columns = raw.columns.str.strip()
    missing = required - set(raw.columns)
    if missing:
        raise HTTPException(400, f"Missing required columns: {missing}")

    _df = _enrich(raw)

    # Also save to disk so it persists
    raw.to_csv(CSV_PATH, index=False)

    return {
        "status": "success",
        "records": len(_df),
        "columns": list(_df.columns),
        "stores": sorted(set(_df["Store"])),
        "categories": sorted(set(_df["Category"])),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  NEXUS Retail Intelligence API Server")
    print("=" * 60)
    print(f"  Records loaded : {len(_df)}")
    print(f"  Docs           : http://localhost:8000/docs")
    print(f"  Health         : http://localhost:8000/api/health")
    print("=" * 60)
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
