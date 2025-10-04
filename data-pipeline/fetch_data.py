import os, io, json, math
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
import requests
import yaml

ROOT = os.path.dirname(os.path.dirname(__file__))
OUT_PATH = os.path.join(ROOT, "public-data", "indicators.json")

def daterange_years_back(years:int) -> str:
    d = datetime.utcnow() - relativedelta(years=years)
    return d.strftime("%Y-%m-%d")

def fetch_fred_series(series_id: str, api_key: str, start_date: str) -> pd.DataFrame:
    if not api_key:
        raise RuntimeError("Missing FRED_API_KEY")
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    js = r.json()
    rows = []
    for obs in js.get("observations", []):
        v = obs.get("value")
        try:
            val = float(v) if v not in (".", None, "") else math.nan
        except:
            val = math.nan
        rows.append((obs["date"], val))
    df = pd.DataFrame(rows, columns=["date","value"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna().sort_values("date")
    return df

def fetch_csv(url: str, start_date: str, column: str=None) -> pd.DataFrame:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    content = r.content
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception:
        df = pd.read_excel(io.BytesIO(content))
    # Guess date column
    date_col = None
    for cand in ["date","Date","observation_date","t","TIME","Time"]:
        if cand in df.columns:
            date_col = cand
            break
    if date_col is None:
        date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    if column and column in df.columns:
        val_col = column
    else:
        # choose last numeric column
        num_cols = [c for c in df.columns if c != date_col]
        val_col = None
        for c in num_cols[::-1]:
            if pd.api.types.is_numeric_dtype(df[c]):
                val_col = c
                break
        if val_col is None:
            raise ValueError("No numeric column found in external CSV")
    df = df[[date_col, val_col]].rename(columns={date_col:"date", val_col:"value"})
    df = df[df["date"] >= pd.to_datetime(start_date)].sort_values("date")
    return df

def summarize(df: pd.DataFrame):
    if df.empty:
        return {"latest_date": None, "latest_value": None, "yoy_pct": None}
    latest = df.iloc[-1]
    latest_date = latest["date"].date().isoformat()
    latest_value = float(latest["value"])
    # YoY
    one_year_ago = latest["date"] - relativedelta(years=1)
    prior = df.loc[df["date"] <= one_year_ago]
    yoy = None
    if not prior.empty:
        base = float(prior.iloc[-1]["value"])
        if base != 0 and not math.isnan(base):
            yoy = 100 * (latest_value - base) / abs(base)
    return {
        "latest_date": latest_date,
        "latest_value": round(latest_value, 4),
        "yoy_pct": None if yoy is None else round(yoy, 2)
    }

def apply_tripwires(latest_value: float, rules: dict):
    if latest_value is None or math.isnan(latest_value):
        return "unknown"
    # Support warn_lte for inversion-style warnings
    if "severe_lte" in rules and latest_value <= float(rules["severe_lte"]):
        return "severe"
    if "warn_lte" in rules and latest_value <= float(rules["warn_lte"]):
        return "warn"
    sev = rules.get("severe_gte")
    warn = rules.get("warn_gte")
    if sev is not None and latest_value >= float(sev):
        return "severe"
    if warn is not None and latest_value >= float(warn):
        return "warn"
    return "ok"

def fred_series(fred_key: str, series_id: str, start_date: str) -> pd.DataFrame:
    return fetch_fred_series(series_id, fred_key, start_date)

def fred_yoy_pct(fred_key: str, series_id: str, start_date: str) -> pd.DataFrame:
    df = fetch_fred_series(series_id, fred_key, start_date)
    if df.empty:
        return df
    # Resample monthly for a stable YoY
    df = df.set_index("date").asfreq("D").interpolate("time").resample("M").last()
    df["value"] = df["value"].pct_change(12) * 100.0
    df = df.reset_index().dropna().sort_values("date")
    return df

def fred_spread(fred_key: str, a_id: str, b_id: str, start_date: str) -> pd.DataFrame:
    a = fetch_fred_series(a_id, fred_key, start_date)
    b = fetch_fred_series(b_id, fred_key, start_date)
    if a.empty or b.empty:
        return pd.DataFrame(columns=["date","value"])
    m = pd.merge_asof(a.sort_values("date"), b.sort_values("date"), on="date", direction="nearest", tolerance=pd.Timedelta("7D"))
    m["value"] = m["value_x"] - m["value_y"]
    m = m[["date","value"]].dropna().sort_values("date")
    return m

def add_indicator(out, key, label, unit, df, source, rules):
    meta_summary = summarize(df)
    status = apply_tripwires(meta_summary["latest_value"], rules or {})
    out["indicators"][key] = {
        "label": label,
        "unit": unit or "",
        "status": status,
        "series": [{"d": d.date().isoformat(), "v": round(float(v), 6)} for d, v in df[["date","value"]].to_records(index=False)],
        "summary": meta_summary,
        "source": source
    }

def main():
    cfg_path = os.path.join(os.path.dirname(__file__), "indicators.yaml")
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)

    start_date = daterange_years_back(int(cfg.get("start_years_back", 10)))

    out = {
        "generated_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "start_date": start_date,
        "indicators": {}
    }

    fred = cfg.get("fred", {})
    fred_key = os.getenv(fred.get("api_key_env", "FRED_API_KEY"), "")
    series = fred.get("series", {})
    for key, meta in series.items():
        try:
            df = fetch_fred_series(meta["id"], fred_key, start_date)
            add_indicator(out, key, meta["label"], meta.get("unit",""), df, f"FRED {meta['id']}", meta.get("tripwires"))
        except Exception as e:
            out["indicators"][key] = {"error": str(e)}

    # Derived
    derived = fred.get("derived", {})
    for key, meta in derived.items():
        try:
            transform = meta.get("transform")
            if transform == "yoy_pct":
                df = fred_yoy_pct(fred_key, meta["from_id"], start_date)
                src = f"FRED {meta['from_id']} (YoY%)"
            elif transform == "spread":
                df = fred_spread(fred_key, meta["a_id"], meta["b_id"], start_date)
                src = f"FRED {meta['a_id']} - {meta['b_id']}"
            elif transform == "direct":
                df = fetch_fred_series(meta["from_id"], fred_key, start_date)
                src = f"FRED {meta['from_id']}"
            else:
                raise ValueError(f"Unknown transform: {transform}")
            add_indicator(out, key, meta["label"], meta.get("unit",""), df, src, meta.get("tripwires"))
        except Exception as e:
            out["indicators"][key] = {"error": str(e)}

    # Externals
    externals = cfg.get("externals", {})
    for key, meta in externals.items():
        try:
            df = fetch_csv(meta["url"], start_date, meta.get("column"))
            add_indicator(out, key, meta["label"], meta.get("unit",""), df, meta["url"], meta.get("tripwires"))
        except Exception as e:
            out["indicators"][key] = {"error": str(e)}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
